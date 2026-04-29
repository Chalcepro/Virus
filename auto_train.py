import torch
import torch.nn as nn
import torch.optim as optim
import os
import sys
import json
import gc
import time
from pathlib import Path
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator
import argparse


# ---- Configuration ----
BLOCK_SIZE = 64
BATCH_SIZE = 16
EPOCHS = 100
LEARNING_RATE = 0.001
GRAD_CLIP = 1.0
MODEL_PATH = "model_v3.pt"
DATA_DIR = "data"
STATE_FILE = "auto_train_state.json"
VOCAB_FILE = "vocab.json"  # Save character vocabulary for inference

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Parse command line for learning rate override
parser = argparse.ArgumentParser()
parser.add_argument("--lr", type=float, default=LEARNING_RATE)
parser.add_argument("--files", nargs="+", help="Only train on specific file names (from data/)")
args, unknown = parser.parse_known_args()
LEARNING_RATE = args.lr
TARGET_FILES = args.files  # None means train on all new files

# ---- Vocab resize (fix mismatch) ----
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

# ---- State management ----
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"max_vocab_size": 0, "trained_files": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def save_vocab(all_files):
    """Build and save character vocabulary from all data files."""
    all_text = ""
    for filename in all_files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                all_text += f.read()
        except:
            pass
    
    chars = sorted(list(set(all_text)))
    vocab = {
        "stoi": {ch: i for i, ch in enumerate(chars)},
        "itos": {str(i): ch for i, ch in enumerate(chars)},
        "vocab_size": len(chars)
    }
    
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Vocabulary saved to {VOCAB_FILE} ({len(chars)} chars)")
    return vocab

def load_or_create_vocab(all_files):
    """Load existing vocab or create new one from all files."""
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        print(f"✓ Loaded existing vocabulary ({vocab['vocab_size']} chars)")
        return vocab
    else:
        print("Creating vocabulary from all files...")
        return save_vocab(all_files)

# ---- Load model (existing or new) ----
def load_model(vocab_size):
    """Create a fresh model with given vocab size."""
    # IMPORTANT: adjust embed_size / state_size to match your architecture.
    # These values are taken from your checkpoint shape: embedding (96,64), state_size (128).
    model = HybridCodeGenerator(
        vocab_size=vocab_size,
        embed_size=64,
        state_size=128
    )
    model.to(device)
    return model

# ---- Scan all data files for max vocab ----
def get_data_files():
    data_path = Path(DATA_DIR)
    if not data_path.exists():
        print(f"Error: {DATA_DIR} directory not found!")
        sys.exit(1)
    return sorted([f.name for f in data_path.glob("*.txt")])

def get_max_vocab_size():
    files = get_data_files()
    max_vocab = 0
    print("Scanning vocab sizes across all files...")
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            dataset = CodeDataset(filepath, block_size=BLOCK_SIZE)
            max_vocab = max(max_vocab, dataset.vocab_size)
            print(f"  {filename}: {dataset.vocab_size} chars")
        except Exception as e:
            print(f"  {filename}: error reading")
    print(f"\nMax vocab size across all files: {max_vocab}\n")
    return max_vocab

# ---- Training one file ----
def train_on_file(model, filepath, epochs=EPOCHS, vocab_mapping=None):
    try:
        print(f"\n  Loading dataset: {filepath}")
        dataset = CodeDataset(filepath, block_size=BLOCK_SIZE)
        
        # If vocab_mapping provided, adjust dataset to use consistent indices
        if vocab_mapping:
            dataset.stoi = vocab_mapping["stoi"]
            dataset.itos = vocab_mapping["itos"]
            # Re-encode data with the fixed vocabulary
            dataset.data = torch.tensor(
                [dataset.stoi.get(ch, 0) for ch in dataset.text], 
                dtype=torch.long
            )
            print(f"  Using fixed vocabulary ({vocab_mapping['vocab_size']} chars)")
        else:
            print(f"  Vocabulary size: {dataset.vocab_size}")

        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)
        loss_fn = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            model.train()
            total_loss = 0
            steps = 100
            epoch_start = time.time()

            for step_idx in range(steps):
                x, y = dataset.get_batch(BATCH_SIZE)
                x, y = x.to(device), y.to(device)

                logits, _ = model(x)
                vocab_size = model.embedding.num_embeddings
                loss = loss_fn(logits.reshape(-1, vocab_size), y.reshape(-1))

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                optimizer.step()

                total_loss += loss.detach().item()
                del x, y, logits, loss

                if (step_idx + 1) % 20 == 0:
                    gc.collect()
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

            scheduler.step()
            gc.collect()
            if device.type == "cuda":
                torch.cuda.empty_cache()

            avg_loss = total_loss / steps
            epoch_time = time.time() - epoch_start
            print(f"  Epoch {epoch+1:3d}/{epochs} | loss = {avg_loss:.4f}")

        print(f"  ✓ Training complete for {filepath}")
        return True
    except KeyboardInterrupt:
        print("\n  ⚠ Training interrupted by user")
        return False
    except Exception as e:
        print(f"  ✗ Error training on {filepath}: {e}")
        return False

# ---- Main ----
def main():
    # Check for command-line arguments
    allow_retrain = "--retrain" in sys.argv
    reset_state = "--reset" in sys.argv
    
    print("=" * 60)
    print("AUTO TRAIN - Sequential Multi-File Training")
    print("=" * 60)
    if allow_retrain:
        print("MODE: RETRAIN (will train all files again)")
    else:
        print("MODE: NORMAL (skip already-trained files)")
    if reset_state:
        print("ACTION: Clearing training state")
    print("Press Ctrl+C to stop (model will be saved safely)\n")

    state = load_state()
    
    # Reset state if requested
    if reset_state:
        state = {"max_vocab_size": state.get("max_vocab_size", 0), "trained_files": []}
        save_state(state)
        print("✓ Training state cleared\n")
    
    all_files = get_data_files()

    # Load or create vocabulary (use consistent vocab for all files)
    vocab = load_or_create_vocab(all_files)
    vocab_size_fixed = vocab["vocab_size"]

    print(f"Found {len(all_files)} data files:")
    for f in all_files:
        status = "✓ TRAINED" if f in state["trained_files"] else "⊙ PENDING"
        print(f"  {status:12} {f}")

    # ---- Model loading with vocab mismatch handling ----
    print(f"\nInitializing model...")
    model = load_model(vocab_size=vocab_size_fixed)

    if os.path.exists(MODEL_PATH):
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        checkpoint_vocab = checkpoint['embedding.weight'].size(0)
        if checkpoint_vocab != vocab_size_fixed:
            print(f"Resizing vocab from {checkpoint_vocab} to {vocab_size_fixed}")
            # Resize checkpoint weights before loading
            old_emb = checkpoint['embedding.weight']
            new_emb = torch.zeros(vocab_size_fixed, old_emb.size(1))
            copy_size = min(vocab_size_fixed, checkpoint_vocab)
            new_emb[:copy_size] = old_emb[:copy_size]
            checkpoint['embedding.weight'] = new_emb
            
            old_out_weight = checkpoint['output_fc.weight']
            new_out_weight = torch.zeros(vocab_size_fixed, old_out_weight.size(1))
            new_out_weight[:copy_size] = old_out_weight[:copy_size]
            checkpoint['output_fc.weight'] = new_out_weight
            
            old_out_bias = checkpoint['output_fc.bias']
            new_out_bias = torch.zeros(vocab_size_fixed)
            new_out_bias[:copy_size] = old_out_bias[:copy_size]
            checkpoint['output_fc.bias'] = new_out_bias
        
        model.load_state_dict(checkpoint, strict=False)
        print("✓ Loaded existing model with vocab fix")
    else:
        print("✓ Starting fresh model")

    print(f"\nStarting training on {len(all_files)} files...\n")
    files_trained = 0

    try:
        for i, filename in enumerate(all_files, 1):
            # Skip files not in TARGET_FILES list if specified
            if TARGET_FILES is not None and filename not in TARGET_FILES:
                print(f"\n[{i}/{len(all_files)}] Skipping {filename} (not in --files list)")
                continue
            
            # Skip already trained files UNLESS --retrain is enabled
            if filename in state["trained_files"] and not allow_retrain:
                print(f"\n[{i}/{len(all_files)}] Skipping {filename} (already trained)")
                print("  TIP: Use 'python auto_train.py --retrain' to train all files again")
                continue

            filepath = os.path.join(DATA_DIR, filename)
            
            is_retrain = filename in state["trained_files"] and allow_retrain
            if is_retrain:
                print(f"\n[{i}/{len(all_files)}] RE-TRAINING {filename}")
            else:
                print(f"\n[{i}/{len(all_files)}] Training on {filename}")
            print("-" * 60)

            file_start = time.time()
            success = train_on_file(model, filepath, epochs=EPOCHS, vocab_mapping=vocab)
            file_time = time.time() - file_start

            if success:
                torch.save(model.state_dict(), MODEL_PATH)
                print(f"  💾 Model saved to {MODEL_PATH}")

                if filename not in state["trained_files"]:
                    state["trained_files"].append(filename)
                save_state(state)
                print(f"  📝 Progress saved to {STATE_FILE}")
                files_trained += 1

                gc.collect()
                if device.type == "cuda":
                    torch.cuda.empty_cache()
            else:
                print(f"  ✗ Skipping {filename} due to error")
                torch.save(model.state_dict(), MODEL_PATH)
                gc.collect()
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("⚠ TRAINING INTERRUPTED")
        print("=" * 60)
        print("TIP: Run again without --reset to continue from where you left off")
        print("     Or use --retrain to train on files multiple times")
        print("     Or use --lr to avoid forgetting old knowledge.")
        torch.save(model.state_dict(), MODEL_PATH)
        save_state(state)
        sys.exit(0)

    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  python auto_train.py            - Continue training (skip already-trained)")
    print("  python auto_train.py --retrain  - Re-train all files from scratch")
    print("  python auto_train.py --reset    - Clear progress and start over")

if __name__ == "__main__":
    main()