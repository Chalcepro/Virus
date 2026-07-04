import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

print("Training V3 model (legacy)...")
subprocess.run([sys.executable, str(ROOT / "scripts" / "train_v3.py")], check=True, cwd=ROOT)

print("\nGenerating sample...")
subprocess.run([sys.executable, str(ROOT / "generate_v3.py")], check=True, cwd=ROOT)
