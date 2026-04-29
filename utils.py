import torch

def build_vocab(text):
    chars = sorted(list(set(text)))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for ch, i in stoi.items()}
    return stoi, itos

def encode(text, stoi):
    return [stoi.get(c, 0) for c in text]

def decode(tokens, itos):
    return ''.join([itos.get(t, '') for t in tokens])