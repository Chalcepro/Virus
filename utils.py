import inspect
import torch

def torch_load(path, map_location=None, **kwargs):
    if "weights_only" in inspect.signature(torch.load).parameters and "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return torch.load(path, map_location=map_location, **kwargs)


def build_vocab(text):
    chars = sorted(list(set(text)))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for ch, i in stoi.items()}
    return stoi, itos

def encode(text, stoi):
    return [stoi.get(c, 0) for c in text]

def decode(tokens, itos):
    return ''.join([itos.get(t, '') for t in tokens])