#!/usr/bin/env python3
"""Build enclosures: `python build.py [name ...] [--check] [--no-preview]`. See README.md."""
import sys

from enclosure_builder.cli import main

sys.exit(main())
