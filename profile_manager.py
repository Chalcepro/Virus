"""Profile-aware helpers for Virus model artifacts."""

from pathlib import Path

import torch

import config
from model_v3 import HybridCodeGenerator
from utils import get_device


def ensure_profile_dirs(profile_name=None):
    profile, _ = config.resolve_profile(profile_name)
    config.apply_profile(profile)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return profile


def create_profile_model(profile_name=None, vocab_size=None):
    profile = ensure_profile_dirs(profile_name)
    device = get_device()

    if vocab_size is None:
        if config.VOCAB_FILE.exists():
            import json

            with open(config.VOCAB_FILE, "r", encoding="utf-8") as f:
                vocab_size = json.load(f).get("vocab_size", 106)
        else:
            vocab_size = config.FORCE_VOCAB_SIZE or 106

    model = HybridCodeGenerator(
        vocab_size=vocab_size,
        embed_size=config.EMBED_SIZE,
        state_size=config.STATE_SIZE,
        window_size=config.WINDOW_SIZE,
    ).to(device)

    config.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), config.MODEL_PATH)
    return profile, config.MODEL_PATH


def list_profiles():
    rows = []
    for name, paths in config.PROFILE_CONFIGS.items():
        rows.append(
            {
                "profile": name,
                "model": str(paths["model_path"]),
                "vocab": str(paths["vocab_file"]),
                "data_dir": str(paths["data_dir"]),
                "model_exists": Path(paths["model_path"]).exists(),
            }
        )
    return rows
