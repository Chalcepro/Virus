#!/usr/bin/env python3
"""Start the project's virtual environment in a new terminal."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_venv_dir(root: Path) -> Path:
    for candidate in (root / ".venv", root / "venv", root / "env"):
        if candidate.exists():
            return candidate
    return root / ".venv"


def ensure_venv(venv_dir: Path) -> Path:
    if not venv_dir.exists():
        print(f"Creating virtual environment at {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, cwd=str(ROOT))
    return venv_dir


def main() -> None:
    venv_dir = ensure_venv(find_venv_dir(ROOT))

    if os.name == "nt":
        if (venv_dir / "Scripts" / "Activate.ps1").exists():
            activate_script = venv_dir / "Scripts" / "Activate.ps1"
            cmd = [
                "powershell",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"& '{activate_script}'; Set-Location '{ROOT}'",
            ]
        else:
            activate_script = venv_dir / "Scripts" / "activate.bat"
            cmd = ["cmd", "/k", str(activate_script), "&&", f"cd /d {ROOT}"]

        print(f"Launching terminal with virtual environment: {venv_dir}")
        subprocess.Popen(cmd, cwd=str(ROOT))
    else:
        activate_script = venv_dir / "bin" / "activate"
        print(f"Virtual environment ready at {venv_dir}")
        print("Run this in your shell:")
        print(f"source {activate_script}")


if __name__ == "__main__":
    main()
