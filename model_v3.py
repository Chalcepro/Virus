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
