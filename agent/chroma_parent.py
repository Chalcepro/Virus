#!/usr/bin/env python3
"""Minecraft parent brain: WebSocket server + ChromaDB memory + model inference."""
import asyncio
import hashlib
import json
import logging
import os
import random
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import chromadb
import config
import torch
import websockets
from sentence_transformers import SentenceTransformer
from utils import get_device, torch_load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Chroma")


def load_model_and_vocab(model_path=None, vocab_path=None):
    from model_v3 import HybridCodeGenerator

    if model_path is None:
        model_path = config.MODEL_PATH
    if vocab_path is None:
        vocab_path = config.VOCAB_FILE

    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    if config.FORCE_VOCAB_SIZE is not None:
        if config.FORCE_VOCAB_SIZE < vocab["vocab_size"]:
            raise ValueError(
                f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= saved vocab size ({vocab['vocab_size']})"
            )
        vocab["vocab_size"] = config.FORCE_VOCAB_SIZE
    stoi = vocab["stoi"]
    itos = vocab["itos"]
    vocab_size = vocab["vocab_size"]
    device = get_device()
    model = HybridCodeGenerator(vocab_size=vocab_size, embed_size=64, state_size=128)
    checkpoint = torch_load(str(model_path), map_location=device)
    model.load_state_dict_adaptive(checkpoint)
    model.to(device)
    model.eval()
    logger.info("Loaded model (vocab %d) on %s", vocab_size, device)
    return model, stoi, itos, device


def generate_action_token(model, stoi, itos, device, prompt, temperature=0.7):
    input_ids = [stoi.get(ch, 0) for ch in prompt]
    input_tensor = torch.tensor([input_ids], device=device)
    with torch.no_grad():
        logits, _ = model(input_tensor)
        next_token_logits = logits[0, -1, :] / temperature
        probs = torch.softmax(next_token_logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1).item()
    return itos.get(str(next_token), "?")


class CausalityBuffer:
    def __init__(self, maxlen=5):
        self.buffer = deque(maxlen=maxlen)

    def add(self, state, action):
        self.buffer.append(
            {
                "state": state.copy() if isinstance(state, dict) else state,
                "action": action,
                "time": time.time(),
            }
        )

    def detect_change(self, new_state):
        if len(self.buffer) < 1:
            return None
        prev = self.buffer[-1]
        if prev["action"] is None:
            return None

        changes = []
        if "health" in prev["state"] and "health" in new_state:
            delta = new_state["health"] - prev["state"]["health"]
            if abs(delta) > 0.1:
                changes.append(f"health {delta:+0.1f}")

        if "position" in prev["state"] and "position" in new_state:
            p1 = prev["state"]["position"]
            p2 = new_state["position"]
            dist = ((p2["x"] - p1["x"]) ** 2 + (p2["z"] - p1["z"]) ** 2) ** 0.5
            if dist > 0.5:
                changes.append(f"moved {dist:.1f}")

        if changes:
            return {"action": prev["action"], "changes": changes}
        return None


class ChromaParent:
    def __init__(self, chroma_path="chroma_memory"):
        logger.info("Initializing parent brain...")
        self.model, self.stoi, self.itos, self.device = load_model_and_vocab()
        self.client = chromadb.PersistentClient(path=str(ROOT / chroma_path))
        self.collection = self.client.get_or_create_collection("experiences")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.buffer = CausalityBuffer()
        self.last_state = None
        self.last_action = None
        self.experience_count = 0
        self.action_names = ["forward", "back", "left", "right", "jump", "attack", "use"]
        self.last_inference_time = 0.0
        self.inference_cooldown = 2.0
        self.last_embed_time = 0.0
        self.embed_cooldown = 1.0
        logger.info("Ready.")

    def retrieve_similar_experiences(self, query_text, n_results=3):
        try:
            count = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, count),
            )
            return results.get("documents", [[]])[0] or []
        except Exception as exc:
            logger.warning("Memory retrieval failed: %s", exc)
            return []

    def store_experience(self, before, action, after, outcome):
        now = time.time()
        if now - self.last_embed_time < self.embed_cooldown:
            return
        self.last_embed_time = now

        text = f"{before} -> {action} -> {after} : {outcome}"
        emb = self.embedder.encode(text).tolist()
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[emb],
            metadatas=[{"action": action, "outcome": outcome}],
            documents=[text],
        )
        self.experience_count += 1
        logger.info("Stored experience #%d: %s", self.experience_count, action)

    async def decide_action(self, state):
        now = time.time()
        if now - self.last_inference_time < self.inference_cooldown:
            return {"action": random.choice(self.action_names)}
        self.last_inference_time = now

        health = state.get("health", 20)
        if health < 8:
            return {"action": "jump"}

        pos = state.get("position", {})
        state_desc = f"x={pos.get('x', 0):.1f} z={pos.get('z', 0):.1f} hp={health}"
        memories = self.retrieve_similar_experiences(state_desc)
        memory_block = ""
        if memories:
            memory_block = "\nRelevant past experiences:\n" + "\n".join(
                f"- {m}" for m in memories[:3]
            )

        prompt = (
            f"Bot state: {state_desc}\n"
            f"Choose action (0-6):\n"
            f"0 forward 1 back 2 left 3 right 4 jump 5 attack 6 use\n"
            f"{memory_block}\n"
            f"Number:"
        )

        try:
            out = generate_action_token(
                self.model, self.stoi, self.itos, self.device, prompt, temperature=0.8
            )
            if out.isdigit() and 0 <= int(out) <= 6:
                act = self.action_names[int(out)]
                logger.info("Model chose: %s", act)
                return {"action": act}
        except Exception as exc:
            logger.error("Model error: %s", exc)

        act = random.choice(self.action_names)
        logger.info("Fallback action: %s", act)
        return {"action": act}

    def process_state(self, state):
        if self.last_state and self.last_action:
            change = self.buffer.detect_change(state)
            if change:
                self.store_experience(
                    self.last_state,
                    self.last_action,
                    state,
                    "; ".join(change["changes"]),
                )
        self.last_state = state
        return True


async def handle_bot(websocket):
    parent = ChromaParent()
    logger.info("Bot connected")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "state_update":
                    parent.process_state(data)
                    cmd = await parent.decide_action(data)
                    parent.last_action = cmd["action"]
                    parent.buffer.add(data, parent.last_action)
                    await websocket.send(json.dumps(cmd))

                elif msg_type == "request_action":
                    if parent.last_state:
                        cmd = await parent.decide_action(parent.last_state)
                        parent.last_action = cmd["action"]
                        parent.buffer.add(parent.last_state, parent.last_action)
                        await websocket.send(json.dumps(cmd))

                elif msg_type == "chat":
                    logger.info("Chat from %s: %s", data.get("from"), data.get("msg"))

                elif msg_type == "player_event":
                    logger.info("Player event: %s", data.get("event"))
                    parent.store_experience(
                        "player", "demo", data.get("event"), "human teaching"
                    )

            except Exception as exc:
                logger.error("Message error: %s", exc)

    except websockets.exceptions.ConnectionClosed:
        logger.info("Bot disconnected")


async def main():
    async with websockets.serve(handle_bot, "localhost", 8765):
        logger.info("Listening on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
