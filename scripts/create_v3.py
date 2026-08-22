import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config
from profile_manager import create_profile_model


def parse_args():
    parser = argparse.ArgumentParser(description="Create a fresh Virus model checkpoint")
    parser.add_argument(
        "--profile",
        choices=sorted(config.PROFILE_CONFIGS.keys()),
        default=config.DEFAULT_PROFILE,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    profile, model_path = create_profile_model(args.profile)
    print(f"Created profile model: {profile}")
    print(f"Checkpoint: {model_path}")

    print("\nGenerating sample...")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "generate_v3.py"),
            "--profile",
            profile,
            "--prompt",
            "### INPUT: action narration\n### OUTPUT:",
            "--max-tokens",
            "120",
        ],
        check=True,
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
