import json
import argparse
import sys

import torch

import config
from model_v3 import HybridCodeGenerator
from utils import get_device, torch_load


def load_vocab():
    with open(config.VOCAB_FILE, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    if config.FORCE_VOCAB_SIZE is not None:
        if config.FORCE_VOCAB_SIZE < vocab["vocab_size"]:
            raise ValueError(
                f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= saved vocab size ({vocab['vocab_size']})"
            )
        vocab["vocab_size"] = config.FORCE_VOCAB_SIZE
    stoi = vocab["stoi"]
    itos = {int(k): v for k, v in vocab["itos"].items()}
    return stoi, itos, vocab["vocab_size"]


def generate(prompt="def ", max_tokens=200, temperature=0.8, top_k=40, profile=None):
    if profile:
        config.apply_profile(profile)
    device = get_device()
    stoi, itos, vocab_size = load_vocab()

    model = HybridCodeGenerator(
        vocab_size=vocab_size,
        state_size=config.STATE_SIZE,
        embed_size=config.EMBED_SIZE,
        window_size=config.WINDOW_SIZE,
    )
    try:
        checkpoint = torch_load(config.MODEL_PATH, map_location=device)
    except FileNotFoundError:
        print(f"Error: {config.MODEL_PATH} not found. Train first with: python auto_train.py")
        sys.exit(1)

    try:
        model.load_state_dict_adaptive(checkpoint)
    except RuntimeError as exc:
        print("Error loading checkpoint:", exc)
        sys.exit(1)

    model.to(device)
    model.eval()

    input_ids = torch.tensor([stoi.get(ch, 0) for ch in prompt if ch in stoi], dtype=torch.long)
    if len(input_ids) == 0:
        input_ids = torch.tensor([0], device=device)
    else:
        input_ids = input_ids.to(device)

    output_ids = model.generate(input_ids, max_tokens, temperature, top_k)
    generated = "".join(itos.get(i.item(), "") for i in output_ids)
    print(generated)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate text from Virus model")
    parser.add_argument(
        "--profile",
        choices=sorted(config.PROFILE_CONFIGS.keys()),
        default=config.DEFAULT_PROFILE,
        help="Model profile to load",
    )
    parser.add_argument("--prompt", default="def ")
    parser.add_argument("--max-tokens", type=int, default=300)
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--top-k", type=int, default=40)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate(
        prompt=args.prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        profile=args.profile,
    )
