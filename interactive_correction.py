#!/usr/bin/env python3
import torch
import subprocess
import sys
from pathlib import Path
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator

MODEL_PATH = "model_v3.pt"
DATA_DIR = "data"
CORRECTIONS_FILE = "corrections.txt"
CORRECTIONS_PATH = Path(DATA_DIR) / CORRECTIONS_FILE
DEVICE = torch.device("cpu")

def ensure_corrections_file():
    CORRECTIONS_PATH.parent.mkdir(exist_ok=True)
    if not CORRECTIONS_PATH.exists():
        CORRECTIONS_PATH.write_text("", encoding="utf-8")

def append_correction(prompt: str, correct_output: str):
    entry = f"\n### INPUT:\n{prompt}\n### OUTPUT:\n{correct_output}\n"
    with open(CORRECTIONS_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Correction saved to {CORRECTIONS_PATH}")

def fine_tune_on_corrections(lr=0.0001):
    print("\n🔄 Fine‑tuning model on your correction...")
    cmd = [sys.executable, "auto_train.py", "--lr", str(lr), "--files", CORRECTIONS_FILE]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("⚠ Fine‑tuning failed.")
    else:
        print("✓ Model updated with your correction.\n")

def load_model_and_dataset():
    # Load checkpoint to get the exact vocab size used during training
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    checkpoint_vocab = checkpoint['embedding.weight'].size(0)
    
    # Choose a dataset file that contains a rich character set (matching the training data)
    # Priority: data/python.txt , data/code.txt , all.txt , or any .txt in data/
    possible_files = [
        Path(DATA_DIR) / "python.txt",
        Path(DATA_DIR) / "code.txt",
        Path("all.txt"),
    ]
    data_file = None
    for f in possible_files:
        if f.exists():
            data_file = f
            break
    if data_file is None:
        data_files = list(Path(DATA_DIR).glob("*.txt"))
        if not data_files:
            raise FileNotFoundError("No .txt files found in data/ or root")
        data_file = data_files[0]
    
    dataset = CodeDataset(str(data_file), block_size=64)
    print(f"Using dataset: {data_file} (vocab size = {dataset.vocab_size})")
    
    # Create model with the checkpoint's vocabulary size (no resizing needed)
    model = HybridCodeGenerator(
        vocab_size=checkpoint_vocab,
        state_size=128,
        embed_size=64,
        window_size=64
    )
    model.load_state_dict(checkpoint, strict=True)   # exact match now
    model.to(DEVICE)
    model.eval()
    return model, dataset

def generate_response(model, dataset, prompt, max_tokens=200, temperature=0.8, top_k=40):
    input_ids = dataset.encode(prompt).to(DEVICE)
    if len(input_ids) == 0:
        input_ids = torch.tensor([0], device=DEVICE)
    with torch.no_grad():
        output_ids = model.generate(input_ids, max_tokens, temperature, top_k)
    full_response = dataset.decode(output_ids)
    if full_response.startswith(prompt):
        return full_response[len(prompt):].lstrip()
    return full_response

def main():
    ensure_corrections_file()
    print("Loading model...")
    model, dataset = load_model_and_dataset()
    print("\n🤖 Interactive Correction Mode")
    print("   Model says: Hello! Test me with any prompt.")
    print("   Type 'exit' to quit, 'skip' to skip correction.\n")

    while True:
        user_prompt = input("You: ").strip()
        if user_prompt.lower() == "exit":
            break
        if not user_prompt:
            continue

        generated = generate_response(model, dataset, user_prompt)
        print(f"\n🤖 Model: {generated}\n")

        correct = input("Was this correct? (y/n/skip): ").strip().lower()
        if correct == "y":
            print("✅ Great! Moving on.\n")
            continue
        elif correct == "skip":
            print("⏭ Skipping correction.\n")
            continue
        elif correct == "n":
            correct_output = input("Please type the correct output: ").strip()
            if correct_output:
                append_correction(user_prompt, correct_output)
                fine_tune_on_corrections()
                model, dataset = load_model_and_dataset()  # reload after fine‑tune
                print("Model reloaded with your correction.\n")
            else:
                print("No correction provided. Skipping.\n")
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()