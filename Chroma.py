#!/usr/bin/env python3
"""Launcher for agent/chroma_parent.py (run from project root)."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).parent / "agent" / "chroma_parent.py"), run_name="__main__")
