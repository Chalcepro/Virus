import torch
import os
import sys
import json
import config
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator
from utils import torch_load

# === Settings ===
MODEL_PATH = config.MODEL_PATH                   # your trained weights
DATA_FILE = config.DATA_DIR / "python.txt"      # file to generate from
VOCAB_FILE = config.VOCAB_FILE                 # vocabulary from training
MAX_NEW_TOKENS = 200                           # how many characters to generate
TEMPERATURE = 0.8                              # randomness (higher = more creative)
TOP_K = 40                                     # nucleus sampling top‑k

# === Load dataset and model ===
print(f"Using model checkpoint: {MODEL_PATH}")
device = torch.device("cpu")

# Load checkpoint to get its vocab size
checkpoint = torch_load(MODEL_PATH, map_location=device)
checkpoint_vocab_size = checkpoint['embedding.weight'].size(0)

# Load the vocabulary file
if not os.path.exists(VOCAB_FILE):
    print(f"ERROR: {VOCAB_FILE} not found!")
    print("Make sure you've run 'python auto_train.py' first to create the vocabulary.")
    sys.exit(1)

with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
    vocab_data = json.load(f)
    full_stoi = vocab_data["stoi"]
    full_itos = {int(k): v for k, v in vocab_data["itos"].items()}

# Use the full vocabulary (model should be trained with this)
if config.FORCE_VOCAB_SIZE is not None:
    if config.FORCE_VOCAB_SIZE < vocab_data["vocab_size"]:
        raise ValueError(
            f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= saved vocab size ({vocab_data['vocab_size']})"
        )
    vocab_data["vocab_size"] = config.FORCE_VOCAB_SIZE
    print(f"Overriding vocab size to {config.FORCE_VOCAB_SIZE} for generation")

stoi = full_stoi
itos = full_itos
vocab_size_to_use = vocab_data["vocab_size"]

print(f"Loaded vocabulary: {vocab_size_to_use} characters")
print(f"Checkpoint was trained with: {checkpoint_vocab_size} vocabulary size")

# Load the specific file for generation prompts
dataset = CodeDataset(str(DATA_FILE), block_size=config.BLOCK_SIZE)

# Create model with the full vocab size and adapt the checkpoint if needed
# Use sizes from config so they match training/checkpoint settings
model = HybridCodeGenerator(
    vocab_size=vocab_size_to_use,
    state_size=config.STATE_SIZE,
    embed_size=config.EMBED_SIZE,
    window_size=config.WINDOW_SIZE
)

# Load weights, resizing embeddings and output projection if the checkpoint was trained with a different vocab
model.load_state_dict_adaptive(checkpoint)
model.to(device)
model.eval()

print("Model loaded. Type your prompt (or 'exit').\n")

# === Interactive loop ===
while True:
    prompt = input("You: ").strip()
    if prompt.lower() == "exit":
        break
    if not prompt:
        continue

    # Encode prompt into tensor using the full vocab
    input_ids = torch.tensor([stoi[ch] for ch in prompt if ch in stoi], dtype=torch.long)
    if len(input_ids) == 0:
        input_ids = torch.tensor([0], device=device)
    input_ids = input_ids.to(device)

    # Generate
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_k=TOP_K
        )

    # Decode and print using full vocab
    generated = ''.join([itos.get(i.item(), '') for i in output_ids])
    print(f"Model: {generated[len(prompt):]}\n")   # only show the new part