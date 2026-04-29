import subprocess
import sys

print("Training V3 model...")
subprocess.run([sys.executable, "train_v3.py"], check=True)

print("\nGenerating sample code...")
subprocess.run([sys.executable, "generate_v3.py"], check=True)