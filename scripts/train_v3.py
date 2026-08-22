"""Legacy trainer wrapper (superseded by auto_train.py)."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config


def parse_args():
    parser = argparse.ArgumentParser(description="Train Virus model via auto_train")
    parser.add_argument(
        "--profile",
        choices=sorted(config.PROFILE_CONFIGS.keys()),
        default=config.DEFAULT_PROFILE,
    )
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--lr", type=float, default=config.LEARNING_RATE)
    return parser.parse_args()


def main():
    args = parse_args()
    cmd = [
        sys.executable,
        str(ROOT / "auto_train.py"),
        "--profile",
        args.profile,
        "--epochs",
        str(args.epochs),
        "--lr",
        str(args.lr),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
