import torch
from dataset import CodeDataset
from model_v3 import HybridCodeGenerator

def generate(prompt="def ", max_tokens=200, temperature=0.8, top_k=40):
    device = torch.device("cpu")
    dataset = CodeDataset("data/code.txt", block_size=64)
    model = HybridCodeGenerator(
        vocab_size=dataset.vocab_size,
        state_size=128,
        embed_size=64,
        window_size=64
    )
    try:
        model.load_state_dict(torch.load("model_v3.pt", map_location=device))
    except FileNotFoundError:
        print("Error: model_v3.pt not found. Train first with: python train_v3.py")
        return

    model.to(device)
    model.eval()

    input_ids = dataset.encode(prompt).to(device)
    if len(input_ids) == 0:
        input_ids = torch.tensor([0], device=device)

    output_ids = model.generate(input_ids, max_tokens, temperature, top_k)
    print(dataset.decode(output_ids))

if __name__ == "__main__":
    generate(prompt="def ", max_tokens=300, temperature=0.9, top_k=40)