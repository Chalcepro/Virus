import torch

class CodeDataset:
    def __init__(self, filepath, block_size=64):
        # Read entire file as raw characters
        with open(filepath, encoding='utf-8') as f:
            self.text = f.read()

        # Build vocabulary (all unique chars, including spaces/newlines)
        chars = sorted(list(set(self.text)))
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for ch, i in self.stoi.items()}
        self.vocab_size = len(chars)
        self.block_size = block_size

        # Convert whole text to tensor of indices
        self.data = torch.tensor([self.stoi[ch] for ch in self.text], dtype=torch.long)

    def get_batch(self, batch_size):
        """Randomly sample (x, y) pairs of length block_size."""
        max_start = len(self.data) - self.block_size - 1
        ix = torch.randint(0, max_start, (batch_size,))
        x = torch.stack([self.data[i:i+self.block_size] for i in ix])
        y = torch.stack([self.data[i+1:i+self.block_size+1] for i in ix])
        return x, y

    def encode(self, text):
        return torch.tensor([self.stoi[ch] for ch in text if ch in self.stoi], dtype=torch.long)

    def decode(self, ids):
        return ''.join([self.itos.get(i.item(), '') for i in ids])