"""Load and merge the three layers of parameters: defaults <- enclosure <- per-instance."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "config" / "defaults.yaml"
COMPONENTS = ROOT / "components"
ENCLOSURES = ROOT / "enclosures"
SCAD_LIB = ROOT / "scad" / "enclosure.scad"


class ConfigError(Exception):
    pass


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"missing file: {path.relative_to(ROOT)}")
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path.relative_to(ROOT)} must contain a mapping")
    return data


def deep_merge(base: dict, over: dict) -> dict:
    """Mappings merge key by key; lists and scalars in `over` replace `base`."""
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_component(kind: str, part: str, override: dict | None = None) -> dict:
    comp = load_yaml(COMPONENTS / kind / f"{part}.yaml")
    if comp.get("kind") != kind:
        raise ConfigError(f"components/{kind}/{part}.yaml has kind {comp.get('kind')!r}, expected {kind!r}")
    comp["part"] = part
    return deep_merge(comp, override or {})


def enclosure_dir(name: str) -> Path:
    return ENCLOSURES / name


def list_enclosures() -> list[str]:
    return sorted(p.parent.name for p in ENCLOSURES.glob("*/enclosure.yaml"))


def load_enclosure_yaml(name: str, seen: tuple = ()) -> dict:
    """An enclosure's own YAML, with `extends: <other>` resolved: the other
    enclosure's YAML is merged underneath (recursively)."""
    if name in seen:
        raise ConfigError(f"extends loop: {' -> '.join(seen + (name,))}")
    data = load_yaml(enclosure_dir(name) / "enclosure.yaml")
    parent = data.pop("extends", None)
    if parent:
        data = deep_merge(load_enclosure_yaml(parent, seen + (name,)), data)
    return data


def load_enclosure(name: str) -> dict:
    """Return the fully merged parameter tree for one enclosure.

    Components named by `part:` are loaded from components/<kind>/<part>.yaml
    and the instance's own `override:` mapping is merged over them, so an
    enclosure can correct one dimension without forking the library file.
    """
    cfg = deep_merge(load_yaml(DEFAULTS), load_enclosure_yaml(name))
    if cfg.get("name") != name:
        raise ConfigError(f"enclosures/{name}/enclosure.yaml: name must be {name!r}")

    if cfg.get("psu"):
        inst = cfg["psu"]
        inst["spec"] = load_component("psu", inst["part"], inst.get("override"))
    else:
        raise ConfigError("every enclosure houses a power supply: `psu:` is required")

    for inst in cfg.get("perfboards") or []:
        inst["spec"] = load_component("perfboard", inst["part"], inst.get("override"))
    for inst in cfg.get("panel_parts") or []:
        inst["spec"] = load_component("panel", inst["part"], inst.get("override"))
    for inst in cfg.get("wire_holes") or []:
        if inst.get("part"):
            inst["spec"] = load_component("passthrough", inst["part"], inst.get("override"))

    cfg.setdefault("perfboards", [])
    cfg.setdefault("panel_parts", [])
    cfg.setdefault("wire_holes", [])
    cfg.setdefault("vents", {})
    return cfg
