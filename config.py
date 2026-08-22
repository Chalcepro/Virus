"""Shared training and inference configuration."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Profile system (general text + ATS-specialized)
DEFAULT_PROFILE = os.getenv("VIRUS_PROFILE", "general")
PROFILE_CONFIGS = {
    "general": {
        "data_dir": ROOT / "data",
        "model_path": ROOT / "model_v3.pt",
        "vocab_file": ROOT / "vocab.json",
        "state_file": ROOT / "auto_train_state.json",
    },
    "ats": {
        "data_dir": ROOT / "data_ats",
        "model_path": ROOT / "model_ats_v3.pt",
        "vocab_file": ROOT / "vocab_ats.json",
        "state_file": ROOT / "auto_train_state_ats.json",
    },
}


def resolve_profile(profile_name=None):
    profile = profile_name or DEFAULT_PROFILE
    if profile not in PROFILE_CONFIGS:
        valid = ", ".join(sorted(PROFILE_CONFIGS.keys()))
        raise ValueError(f"Unknown profile '{profile}'. Valid profiles: {valid}")
    return profile, PROFILE_CONFIGS[profile]


def apply_profile(profile_name=None):
    """Update path globals based on selected profile."""
    profile, selected = resolve_profile(profile_name)
    global ACTIVE_PROFILE, DATA_DIR, MODEL_PATH, VOCAB_FILE, STATE_FILE
    ACTIVE_PROFILE = profile
    DATA_DIR = selected["data_dir"]
    MODEL_PATH = Path(
        os.getenv(
            "TRAINING_MODEL_PATH",
            str(selected["model_path"]),
        )
    )
    VOCAB_FILE = selected["vocab_file"]
    STATE_FILE = selected["state_file"]
    return profile


# Paths (active profile defaults)
ACTIVE_PROFILE = None
DATA_DIR = ROOT / "data"
MODEL_PATH = ROOT / "model_v3.pt"
VOCAB_FILE = ROOT / "vocab.json"
STATE_FILE = ROOT / "auto_train_state.json"
apply_profile(DEFAULT_PROFILE)

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

