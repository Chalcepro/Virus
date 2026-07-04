"""Legacy single-file trainer (superseded by auto_train.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch
import torch.nn as nn
import torch.optim as optim
import config
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator

BLOCK_SIZE = 128
BATCH_SIZE = 512
EPOCHS = 50
LEARNING_RATE = 0.001
GRAD_CLIP = 1.0

dataset = CodeDataset(str(ROOT / "data" / "python.txt"), block_size=BLOCK_SIZE)
print(f"Vocabulary size: {dataset.vocab_size}")

model = HybridCodeGenerator(
    vocab_size=dataset.vocab_size,
    state_size=128,
    embed_size=64,
    window_size=BLOCK_SIZE,
)

optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for _ in range(100):
        x, y = dataset.get_batch(BATCH_SIZE)
        logits, _ = model(x)
        loss = loss_fn(logits.reshape(-1, dataset.vocab_size), y.reshape(-1))
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()
        total_loss += loss.item()
    scheduler.step()
    print(f"Epoch {epoch:3d} | loss = {total_loss / 100:.4f}")

torch.save(model.state_dict(), str(config.MODEL_PATH))
print("Training complete.")
