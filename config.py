"""Shared training and inference configuration."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Paths
DATA_DIR = ROOT / "data"
DEFAULT_MODEL_FILE = "model_v3.pt"
MODEL_PATH = Path(os.getenv("TRAINING_MODEL_PATH", str(ROOT / DEFAULT_MODEL_FILE)))
VOCAB_FILE = ROOT / "vocab.json"
STATE_FILE = ROOT / "auto_train_state.json"

# Model
EMBED_SIZE = 256
STATE_SIZE = 512
WINDOW_SIZE = 64
BLOCK_SIZE = 256
FORCE_VOCAB_SIZE = 106  # set to an int >= actual vocab size to force a larger model vocab

# Training defaults
BATCH_SIZE = 32
EPOCHS = 30
STEPS_PER_EPOCH = 120
LEARNING_RATE = 5e-4
GRAD_CLIP = 1.0

# Anti-forgetting
REPLAY_RATIO = 0.05
ANCHOR_LAMBDA = 0.5
BALANCED_SAMPLING = True
INSTRUCTION_SAMPLE_RATIO = 0.4

# Validation
VAL_BATCHES_PER_FILE = 20

# Legacy sequential mode (per-file overwrite)
SEQUENTIAL_EPOCHS = 30

