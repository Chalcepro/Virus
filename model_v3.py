import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class GatedMemoryCell(nn.Module):
    """Gated state-space memory cell (Mamba-style)."""
    def __init__(self, state_size=128):
        super().__init__()
        self.forget_gate = nn.Linear(state_size, state_size)
        self.input_gate = nn.Linear(state_size, state_size)
        self.output_proj = nn.Linear(state_size, state_size)
        # Initialize forget bias high (remember by default)
        self.forget_gate.bias.data.fill_(1.0)
        self.input_gate.bias.data.fill_(0.1)

    def forward(self, state, x):
        forget = torch.sigmoid(self.forget_gate(x))
        inp = torch.sigmoid(self.input_gate(x))
        new_state = forget * state + inp * x
        output = torch.tanh(self.output_proj(new_state))
        return new_state, output


class HybridCodeGenerator(nn.Module):
    def __init__(self, vocab_size, state_size=128, embed_size=128, window_size=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.window_size = window_size
        self.state_size = state_size

        # Project embedding to a common dimension for attention & memory
        self.input_proj = nn.Linear(embed_size, state_size)

        # Lightweight local attention (single head)
        self.q_proj = nn.Linear(state_size, state_size, bias=False)
        self.k_proj = nn.Linear(state_size, state_size, bias=False)
        self.v_proj = nn.Linear(state_size, state_size, bias=False)

        # Gated memory module
        self.memory = GatedMemoryCell(state_size)

        # Learnable fusion weight (alpha)
        self.alpha = nn.Parameter(torch.tensor(0.5))

        # Final output projection
        self.output_fc = nn.Linear(state_size, vocab_size)

    def forward(self, x, state=None):
        """
        x: (B, T) token indices
        state: optional (B, state_size) memory state
        returns: logits (B, T, vocab_size), final_state (B, state_size)
        """
        B, T = x.shape
        if state is None:
            state = torch.zeros(B, self.state_size, device=x.device)

        # Embed and project to state_size
        emb = self.embedding(x)                     # (B, T, embed_size)
        proj = self.input_proj(emb)                 # (B, T, state_size)

        # ----- Memory block (recurrent) -----
        memory_outputs = []
        new_state = state
        for t in range(T):
            new_state, mem_out = self.memory(new_state, proj[:, t, :])  # (B, state_size)
            memory_outputs.append(mem_out)
        memory_out = torch.stack(memory_outputs, dim=1)  # (B, T, state_size)

        # ----- Local attention block (causal) -----
        q = self.q_proj(proj)                       # (B, T, state_size)
        k = self.k_proj(proj)
        v = self.v_proj(proj)

        # Scaled dot-product attention
        scale = math.sqrt(self.state_size)
        attn_weights = torch.bmm(q, k.transpose(1, 2)) / scale  # (B, T, T)

        # Causal mask
        causal_mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        attn_weights = attn_weights.masked_fill(causal_mask, float('-inf'))

        attn_probs = F.softmax(attn_weights, dim=-1)

        attn_out = torch.bmm(attn_probs, v)          # (B, T, state_size)

        # ----- Fusion -----
        alpha = torch.sigmoid(self.alpha)            # scalar
        fused = alpha * attn_out + (1 - alpha) * memory_out

        # ----- Output logits -----
        logits = self.output_fc(fused)               # (B, T, vocab_size)

        return logits, new_state

    @torch.no_grad()
    def generate(self, prompt_ids, max_new_tokens=200, temperature=1.0, top_k=0):
        """Autoregressive generation with state maintenance and attention windowing."""
        self.eval()
        device = next(self.parameters()).device
        input_ids = prompt_ids.clone()  # (T)
        state = torch.zeros(1, self.state_size, device=device)

        for _ in range(max_new_tokens):
            # Use last window_size tokens for attention (keeps CPU usage low)
            if input_ids.size(0) > self.window_size:
                window = input_ids[-self.window_size:].unsqueeze(0)  # (1, window)
            else:
                window = input_ids.unsqueeze(0)

            logits, state = self.forward(window, state)
            next_logits = logits[0, -1, :] / temperature

            if top_k > 0:
                v, _ = torch.topk(next_logits, min(top_k, next_logits.size(-1)))
                next_logits[next_logits < v[-1]] = float('-inf')

            probs = F.softmax(next_logits, dim=-1)
            next_id = torch.multinomial(probs, 1)
            input_ids = torch.cat([input_ids, next_id])

        return input_ids

    def _adapt_state_dict_vocab(self, state_dict, target_vocab_size):
        """Resize checkpoint embeddings and output projection to match current vocab."""
        if not isinstance(state_dict, dict):
            raise TypeError("Expected state_dict to be a dict")

        state_dict = dict(state_dict)

        if "embedding.weight" in state_dict:
            old_emb = state_dict["embedding.weight"]
            old_vocab_size, old_emb_dim = old_emb.size()
            target_emb_dim = self.embedding.embedding_dim
            if old_vocab_size != target_vocab_size or old_emb_dim != target_emb_dim:
                new_emb = torch.zeros(target_vocab_size, target_emb_dim, device=old_emb.device)
                copy_vocab = min(old_vocab_size, target_vocab_size)
                copy_dim = min(old_emb_dim, target_emb_dim)
                new_emb[:copy_vocab, :copy_dim] = old_emb[:copy_vocab, :copy_dim]
                state_dict["embedding.weight"] = new_emb

        if "output_fc.weight" in state_dict:
            old_out = state_dict["output_fc.weight"]
            old_vocab_size, old_out_dim = old_out.size()
            target_out_dim = self.output_fc.in_features
            if old_vocab_size != target_vocab_size or old_out_dim != target_out_dim:
                new_out = torch.zeros(target_vocab_size, target_out_dim, device=old_out.device)
                copy_vocab = min(old_vocab_size, target_vocab_size)
                copy_dim = min(old_out_dim, target_out_dim)
                new_out[:copy_vocab, :copy_dim] = old_out[:copy_vocab, :copy_dim]
                state_dict["output_fc.weight"] = new_out

        if "output_fc.bias" in state_dict:
            old_bias = state_dict["output_fc.bias"]
            old_vocab_size = old_bias.size(0)
            if old_vocab_size != target_vocab_size:
                new_bias = torch.zeros(target_vocab_size, device=old_bias.device)
                copy_size = min(old_vocab_size, target_vocab_size)
                new_bias[:copy_size] = old_bias[:copy_size]
                state_dict["output_fc.bias"] = new_bias

        return state_dict

    def load_state_dict_adaptive(self, state_dict, strict=True):
        state_dict = self._adapt_state_dict_vocab(state_dict, self.embedding.num_embeddings)
        result = super().load_state_dict(state_dict, strict=False)
        if strict and (result.missing_keys or result.unexpected_keys):
            raise RuntimeError(
                f"Adaptive state_dict load failed. Missing keys: {result.missing_keys}, "
                f"Unexpected keys: {result.unexpected_keys}"
            )
        return result

    def resize_vocab(self, new_vocab_size):
        """Resize embedding and output projection to a new vocabulary size."""
        old_vocab_size = self.embedding.num_embeddings
        if new_vocab_size == old_vocab_size:
            return

        emb_dim = self.embedding.embedding_dim
        old_emb = self.embedding.weight.data
        new_emb = torch.zeros(new_vocab_size, emb_dim, device=old_emb.device)
        copy_size = min(old_vocab_size, new_vocab_size)
        new_emb[:copy_size] = old_emb[:copy_size]
        self.embedding = nn.Embedding(new_vocab_size, emb_dim)
        self.embedding.weight.data.copy_(new_emb)

        old_out = self.output_fc.weight.data
        old_bias = self.output_fc.bias.data
        new_out = torch.zeros(new_vocab_size, old_out.size(1), device=old_out.device)
        new_bias = torch.zeros(new_vocab_size, device=old_bias.device)
        new_out[:copy_size] = old_out[:copy_size]
        new_bias[:copy_size] = old_bias[:copy_size]
        self.output_fc = nn.Linear(old_out.size(1), new_vocab_size)
        self.output_fc.weight.data.copy_(new_out)
        self.output_fc.bias.data.copy_(new_bias)
