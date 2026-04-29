import torch
import os
import sys
import json
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator

# === Settings ===
MODEL_PATH = "./model_v3.pt"                     # your trained weights
DATA_FILE = "data/python.txt"                  # file to generate from
VOCAB_FILE = "./vocab.json"                    # vocabulary from training
MAX_NEW_TOKENS = 200                           # how many characters to generate
TEMPERATURE = 0.8                              # randomness (higher = more creative)
TOP_K = 40                                     # nucleus sampling top‑k

# === Load dataset and model ===
device = torch.device("cpu")

# Load checkpoint to get its vocab size
checkpoint = torch.load(MODEL_PATH, map_location=device)
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
stoi = full_stoi
itos = full_itos
vocab_size_to_use = vocab_data["vocab_size"]

print(f"Loaded vocabulary: {vocab_size_to_use} characters")
print(f"Checkpoint was trained with: {checkpoint_vocab_size} vocabulary size")

# Load the specific file for generation prompts
dataset = CodeDataset(DATA_FILE, block_size=64)

# Create model with the correct vocab size
model = HybridCodeGenerator(
    vocab_size=checkpoint_vocab_size,
    state_size=128,
    embed_size=64,
    window_size=64
)

# Load weights
model.load_state_dict(checkpoint)
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