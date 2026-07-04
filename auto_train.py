import argparse
import copy
import gc
import json
import math
import sys
import time
from pathlib import Path

if sys.version_info < (3, 10):
    raise RuntimeError(
        "auto_train.py requires Python 3.10 or newer. Run with `python3` or `py -3` instead of `python`."
    )

import torch
import torch.nn as nn
import torch.optim as optim

import config
from dataset import CodeDataset, ReplayTrainer
from model_v3 import HybridCodeGenerator
from utils import torch_load

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def resize_model_vocab(model, new_vocab_size, old_vocab_size):
    old_emb = model.embedding.weight.data
    new_emb = torch.zeros(new_vocab_size, old_emb.size(1))
    copy_size = min(new_vocab_size, old_vocab_size)
    new_emb[:copy_size] = old_emb[:copy_size]
    model.embedding = nn.Embedding(new_vocab_size, old_emb.size(1))
    model.embedding.weight.data.copy_(new_emb)

    old_out_weight = model.output_fc.weight.data
    old_out_bias = model.output_fc.bias.data
    new_out_weight = torch.zeros(new_vocab_size, old_out_weight.size(1))
    new_out_bias = torch.zeros(new_vocab_size)
    new_out_weight[:copy_size] = old_out_weight[:copy_size]
    new_out_bias[:copy_size] = old_out_bias[:copy_size]
    model.output_fc = nn.Linear(old_out_weight.size(1), new_vocab_size)
    model.output_fc.weight.data.copy_(new_out_weight)
    model.output_fc.bias.data.copy_(new_out_bias)
    return model


def load_state():
    if config.STATE_FILE.exists():
        with open(config.STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"max_vocab_size": 0, "trained_files": []}


def save_state(state):
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def save_vocab(all_files):
    all_text = ""
    for filename in all_files:
        filepath = config.DATA_DIR / filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                all_text += f.read()
        except OSError:
            pass

    chars = sorted(set(all_text))
    vocab = {
        "stoi": {ch: i for i, ch in enumerate(chars)},
        "itos": {str(i): ch for i, ch in enumerate(chars)},
        "vocab_size": len(chars),
    }
    if config.FORCE_VOCAB_SIZE is not None:
        if config.FORCE_VOCAB_SIZE < len(chars):
            raise ValueError(
                f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= actual vocab size ({len(chars)})"
            )
        vocab["vocab_size"] = config.FORCE_VOCAB_SIZE
        print(f"Using forced vocab size {config.FORCE_VOCAB_SIZE} (actual chars = {len(chars)})")
    with open(config.VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)
    print(f"Vocabulary saved to {config.VOCAB_FILE} ({vocab['vocab_size']} chars)")
    return vocab


def load_or_create_vocab(all_files):
    if config.VOCAB_FILE.exists():
        with open(config.VOCAB_FILE, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        if config.FORCE_VOCAB_SIZE is not None:
            if config.FORCE_VOCAB_SIZE < vocab["vocab_size"]:
                raise ValueError(
                    f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= saved vocab size ({vocab['vocab_size']})"
                )
            print(f"Loaded vocabulary ({vocab['vocab_size']} chars), overriding to {config.FORCE_VOCAB_SIZE}")
            vocab["vocab_size"] = config.FORCE_VOCAB_SIZE
        else:
            print(f"Loaded vocabulary ({vocab['vocab_size']} chars)")
        return vocab
    print("Creating vocabulary from all files...")
    return save_vocab(all_files)


def load_model(vocab_size):
    model = HybridCodeGenerator(
        vocab_size=vocab_size,
        embed_size=config.EMBED_SIZE,
        state_size=config.STATE_SIZE,
    )
    model.to(device)
    return model


def load_checkpoint_into_model(model, vocab_size):
    if not config.MODEL_PATH.exists():
        print("Starting fresh model")
        return None

    checkpoint = torch_load(config.MODEL_PATH, map_location=device)
    if checkpoint["embedding.weight"].size(0) != vocab_size:
        print(f"Resizing vocab from {checkpoint['embedding.weight'].size(0)} to {vocab_size}")

    model.load_state_dict_adaptive(checkpoint, strict=False)
    print("Loaded existing checkpoint")
    return copy.deepcopy(model.state_dict())


def get_data_files(split_data=False, include_base_data=False):
    if not config.DATA_DIR.exists():
        print(f"Error: {config.DATA_DIR} directory not found")
        sys.exit(1)

    files = []
    
    # Get regular data files
    if split_data:
        input_paths = sorted(config.DATA_DIR.glob("input/*.txt"))
        output_paths = sorted(config.DATA_DIR.glob("output/*.txt"))
        files.extend([filepath.relative_to(config.DATA_DIR).as_posix() for filepath in input_paths + output_paths])
    else:
        files.extend([f.relative_to(config.DATA_DIR).as_posix() for f in sorted(config.DATA_DIR.glob("*.txt"))])
    
    # Get base-data files if requested
    if include_base_data:
        base_data_dirs = [
            config.DATA_DIR / 'base-data-conversations',
            config.DATA_DIR / 'base-data-knowledge',
            config.DATA_DIR / 'base-data-sentences',
            config.DATA_DIR / 'base-data-generated',
        ]
        for base_dir in base_data_dirs:
            if base_dir.exists():
                base_files = sorted(base_dir.glob("*.txt"))
                files.extend([filepath.relative_to(config.DATA_DIR).as_posix() for filepath in base_files])
    
    return sorted(files)


def filter_recent_wiki_files(all_files, num_wiki_files):
    wiki_files = sorted(
        [f for f in all_files if Path(f).name.startswith("wiki_")],
        key=lambda f: Path(f).name.split("_")[-1],
        reverse=True,
    )
    recent_wiki = set(wiki_files[:num_wiki_files])
    non_wiki = {f for f in all_files if not Path(f).name.startswith("wiki_")}
    return sorted(recent_wiki | non_wiki)


def anchor_loss(model, anchor_state, anchor_lambda):
    if anchor_state is None or anchor_lambda <= 0:
        return torch.tensor(0.0, device=device)
    penalty = torch.tensor(0.0, device=device)
    for name, param in model.named_parameters():
        if name in anchor_state:
            penalty = penalty + torch.sum((param - anchor_state[name]) ** 2)
    return anchor_lambda * penalty


def train_mixed(model, trainer, epochs, learning_rate, anchor_state=None, anchor_lambda=0.0):
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)
    loss_fn = nn.CrossEntropyLoss()
    vocab_size = model.embedding.num_embeddings

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        epoch_start = time.time()

        for _ in range(config.STEPS_PER_EPOCH):
            x, y = trainer.get_batch(config.BATCH_SIZE, replay_ratio=config.REPLAY_RATIO)
            x, y = x.to(device), y.to(device)

            logits, _ = model(x)
            ce_loss = loss_fn(logits.reshape(-1, vocab_size), y.reshape(-1))
            loss = ce_loss + anchor_loss(model, anchor_state, anchor_lambda)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP)
            optimizer.step()
            total_loss += ce_loss.detach().item()

        scheduler.step()
        avg_loss = total_loss / config.STEPS_PER_EPOCH
        print(f"  Epoch {epoch + 1:3d}/{epochs} | loss = {avg_loss:.4f} | {time.time() - epoch_start:.1f}s")

    return True


def train_on_file(model, filepath, epochs, vocab_mapping, learning_rate):
    dataset = CodeDataset(filepath, block_size=config.BLOCK_SIZE)
    dataset.stoi = vocab_mapping["stoi"]
    dataset.itos = {int(k): v for k, v in vocab_mapping["itos"].items()}
    dataset.data = torch.tensor(
        [dataset.stoi.get(ch, 0) for ch in dataset.text],
        dtype=torch.long,
    )

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)
    loss_fn = nn.CrossEntropyLoss()
    vocab_size = model.embedding.num_embeddings

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for _ in range(config.STEPS_PER_EPOCH):
            x, y = dataset.get_batch(config.BATCH_SIZE)
            x, y = x.to(device), y.to(device)
            logits, _ = model(x)
            loss = loss_fn(logits.reshape(-1, vocab_size), y.reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP)
            optimizer.step()
            total_loss += loss.detach().item()
        scheduler.step()
        print(f"  Epoch {epoch + 1:3d}/{epochs} | loss = {total_loss / config.STEPS_PER_EPOCH:.4f}")

    return True


@torch.no_grad()
def evaluate_per_domain(model, filepaths, vocab, batches=None):
    """Per-file perplexity to detect domain forgetting."""
    batches = batches or config.VAL_BATCHES_PER_FILE
    model.eval()
    loss_fn = nn.CrossEntropyLoss()
    vocab_size = model.embedding.num_embeddings
    stoi = vocab["stoi"]
    results = {}

    for filepath in filepaths:
        name = filepath.name if hasattr(filepath, "name") else str(filepath)
        try:
            with open(filepath, encoding="utf-8") as f:
                text = f.read()
            data = torch.tensor([stoi.get(ch, 0) for ch in text], dtype=torch.long)
            if len(data) <= config.BLOCK_SIZE + 1:
                continue

            total_loss = 0.0
            max_start = len(data) - config.BLOCK_SIZE - 1
            for _ in range(batches):
                i = torch.randint(0, max_start, (1,)).item()
                x = data[i : i + config.BLOCK_SIZE].unsqueeze(0).to(device)
                y = data[i + 1 : i + config.BLOCK_SIZE + 1].unsqueeze(0).to(device)
                logits, _ = model(x)
                total_loss += loss_fn(
                    logits.reshape(-1, vocab_size), y.reshape(-1)
                ).item()

            results[name] = math.exp(total_loss / batches)
        except OSError:
            continue

    return results


def print_domain_scores(scores):
    if not scores:
        return
    print("\nDomain perplexity (lower = better retention):")
    for name in sorted(scores, key=scores.get):
        print(f"  {name:40s}  ppl={scores[name]:.1f}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train HybridCodeGenerator on data/*.txt")
    parser.add_argument("--lr", type=float, default=config.LEARNING_RATE)
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--files", nargs="+", help="Only train on specific file names")
    parser.add_argument("--wiki-files", type=int, help="Keep only N most recent wiki_*.txt files")
    parser.add_argument("--retrain", action="store_true", help="Include already-trained files")
    parser.add_argument("--reset", action="store_true", help="Clear trained_files progress")
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Legacy per-file training (prone to forgetting)",
    )
    parser.add_argument(
        "--split-data",
        action="store_true",
        help="Use data/input + data/output split layout for training",
    )
    parser.add_argument(
        "--base-data",
        action="store_true",
        help="Include base-data files (conversations, knowledge, sentences) generated by words generator",
    )
    parser.add_argument("--replay-ratio", type=float, default=config.REPLAY_RATIO)
    parser.add_argument("--anchor-lambda", type=float, default=config.ANCHOR_LAMBDA)
    parser.add_argument(
        "--model",
        default=str(config.MODEL_PATH),
        help="Path to the weights/checkpoint file to train and save",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config.REPLAY_RATIO = args.replay_ratio
    config.MODEL_PATH = Path(args.model).expanduser()

    print("=" * 60)
    print("AUTO TRAIN")
    print("=" * 60)
    mode = "sequential (legacy)" if args.sequential else "mixed + replay (default)"
    split_text = "split-mode" if args.split_data else "mixed root + split"
    base_data_text = "+ base-data" if args.base_data else ""
    print(f"Mode: {mode} | data layout: {split_text} {base_data_text}")
    print(f"Device: {device}")
    print("Press Ctrl+C to stop safely\n")

    state = load_state()
    if args.reset:
        state = {"max_vocab_size": state.get("max_vocab_size", 0), "trained_files": []}
        save_state(state)
        print("Training state cleared\n")

    all_files = get_data_files(split_data=args.split_data, include_base_data=args.base_data)
    if args.wiki_files is not None:
        all_files = filter_recent_wiki_files(all_files, args.wiki_files)

    vocab = load_or_create_vocab(all_files)
    vocab_size = vocab["vocab_size"]
    model = load_model(vocab_size)
    anchor_state = load_checkpoint_into_model(model, vocab_size)

    def resolve_selected_files(selected_names, available_files):
        selected = []
        basenames = {Path(name).name for name in selected_names}

        for name in available_files:
            if name in selected_names:
                selected.append(name)
                continue
            if Path(name).name in basenames:
                selected.append(name)

        return selected

    if args.files:
        candidate_files = resolve_selected_files(args.files, all_files)
    elif args.retrain:
        candidate_files = all_files
    else:
        candidate_files = [f for f in all_files if f not in state["trained_files"]]

    if args.split_data and args.retrain:
        print("Warning: --split-data and --retrain together will retrain all split data files.")

    if not candidate_files:
        print("No files to train. Use --retrain or add new data/*.txt files.")
        return

    print(f"Files scheduled ({len(candidate_files)}):")
    for name in candidate_files:
        print(f"  - {name}")

    try:
        if args.sequential:
            for i, filename in enumerate(candidate_files, 1):
                print(f"\n[{i}/{len(candidate_files)}] Training {filename}")
                filepath = config.DATA_DIR / filename
                train_on_file(model, filepath, args.epochs, vocab, args.lr)
                torch.save(model.state_dict(), config.MODEL_PATH)
                if filename not in state["trained_files"]:
                    state["trained_files"].append(filename)
                save_state(state)
        else:
            new_paths = [config.DATA_DIR / f for f in candidate_files]
            if args.retrain:
                replay_paths = []
                print("\nRetrain: sampling from all selected files each batch")
            else:
                replay_names = [f for f in state["trained_files"] if f in all_files]
                replay_paths = [config.DATA_DIR / f for f in replay_names]
                if replay_paths:
                    print(f"\nReplay enabled from {len(replay_paths)} prior file(s) "
                          f"({args.replay_ratio:.0%} of batches)")

            trainer = ReplayTrainer(
                new_paths,
                replay_paths,
                vocab,
                block_size=config.BLOCK_SIZE,
                balanced=config.BALANCED_SAMPLING,
                instruction_ratio=config.INSTRUCTION_SAMPLE_RATIO,
            )
            print(f"\nTraining for {args.epochs} epochs "
                  f"({config.STEPS_PER_EPOCH} steps/epoch, lr={args.lr})")
            train_mixed(
                model,
                trainer,
                epochs=args.epochs,
                learning_rate=args.lr,
                anchor_state=anchor_state,
                anchor_lambda=args.anchor_lambda,
            )
            torch.save(model.state_dict(), config.MODEL_PATH)
            for filename in candidate_files:
                if filename not in state["trained_files"]:
                    state["trained_files"].append(filename)
            save_state(state)

        gc.collect()
        if device.type == "cuda":
            torch.cuda.empty_cache()

    except KeyboardInterrupt:
        print("\nTraining interrupted. Saving checkpoint...")
        torch.save(model.state_dict(), config.MODEL_PATH)
        save_state(state)
        sys.exit(0)

    all_paths = [config.DATA_DIR / f for f in all_files]
    scores = evaluate_per_domain(model, all_paths, vocab)
    print_domain_scores(scores)

    print("\nTraining complete.")
    print(f"Model: {config.MODEL_PATH}")
    print(f"State: {config.STATE_FILE}")


if __name__ == "__main__":
    main()
