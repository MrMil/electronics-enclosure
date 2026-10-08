"""Run OpenSCAD on the generated wrapper files."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

CANDIDATES = ["openscad", "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"]


def find_openscad() -> str:
    for c in CANDIDATES:
        p = shutil.which(c) or (c if Path(c).exists() else None)
        if p:
            return p
    raise SystemExit("OpenSCAD not found. Install a 2024+ snapshot (manifold backend): "
                     "brew install --cask openscad@snapshot")


def run(args: list[str]) -> None:
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0 or "ERROR" in res.stderr:
        raise SystemExit(f"OpenSCAD failed:\n{' '.join(args)}\n{res.stderr}")
    for line in res.stderr.splitlines():
        if "WARNING" in line:
            print("  openscad:", line)


def render_stl(scad: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run([find_openscad(), "--backend=manifold", "-o", str(out), str(scad)])


def render_png(scad: Path, out: Path, camera: str | None = None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    args = [find_openscad(), "--backend=manifold", "-o", str(out), "--imgsize=1600,1200",
            "--render", "--viewall", "--autocenter", "--colorscheme=Tomorrow", "--projection=p"]
    if camera:
        args.append(f"--camera={camera}")
    run(args + [str(scad)])
