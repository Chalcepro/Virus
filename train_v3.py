import torch
import torch.nn as nn
import torch.optim as optim
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator

# ---- Configuration ----
BLOCK_SIZE = 64
BATCH_SIZE = 16
EPOCHS = 50
LEARNING_RATE = 0.001
GRAD_CLIP = 1.0

# ---- Dataset ----
dataset = CodeDataset("data/python.txt", block_size=BLOCK_SIZE)
print(f"Vocabulary size: {dataset.vocab_size}")

# ---- Model ----
model = HybridCodeGenerator(
    vocab_size=dataset.vocab_size,
    state_size=128,
    embed_size=64,
    window_size=BLOCK_SIZE
)

# ---- Optimizer & Loss ----
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.9)
loss_fn = nn.CrossEntropyLoss()

# ---- Training Loop ----
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    steps = 100  # number of batches per epoch

    for _ in range(steps):
        x, y = dataset.get_batch(BATCH_SIZE)   # (B, T)

        # Forward pass – state starts as zeros (no state passed)
        logits, _ = model(x)

        # Reshape for loss: (B*T, vocab_size) vs (B*T)
        loss = loss_fn(logits.reshape(-1, dataset.vocab_size), y.reshape(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()

        total_loss += loss.item()

    scheduler.step()
    print(f"Epoch {epoch:3d} | loss = {total_loss/steps:.4f}")

# ---- Save ----
torch.save(model.state_dict(), "model_v3.pt")
print("Training complete. Model saved to model_v3.pt")