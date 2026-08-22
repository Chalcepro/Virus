# Virus

A continuously learning character-level language model with optional Minecraft embodiment.

## What this is

Virus trains a small hybrid LM (gated memory + attention) on text files you provide — conversations, code, Wikipedia articles, corrections — and can run as a chat interface or control a Minecraft bot.

This is a **prototype-scale** system. A 64-dim char-LM trained on dozens of small files will not match commercial models. It **will** learn patterns in your data, improve with corrections, and accumulate Wikipedia knowledge incrementally.

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design docs and honest limitations.

## Setup

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-train.txt
npm install mineflayer ws
```

For the Minecraft agent, install the full environment:

```bash
python3 -m pip install -r requirements.txt
```

## Profile-based models

Virus now supports two training/inference profiles:

| Profile | Data dir | Model | Vocab | State |
|---------|----------|-------|-------|-------|
| `general` | `data/` | `model_v3.pt` | `vocab.json` | `auto_train_state.json` |
| `ats` | `data_ats/` | `model_ats_v3.pt` | `vocab_ats.json` | `auto_train_state_ats.json` |

```bash
# General profile (default)
python3 auto_train.py --profile general

# ATS-specialized profile
python3 auto_train.py --profile ats --epochs 30 --lr 0.0001

# Generate with profile
python3 generate_v3.py --profile ats --prompt "### INPUT: action narration\n### OUTPUT:"
python3 text_model.py --profile ats
```

Create a fresh profile checkpoint:

```bash
python3 scripts/create_v3.py --profile ats
```


```bash
# Train on new data files (balanced sampling + replay)
python3 auto_train.py

# Retrain all domains together after major changes
python3 auto_train.py --retrain

# Chat
python3 text_model.py

# One-shot generation
python3 main.py "hello" 100
```

After training, check the **domain perplexity** table printed at the end. Lower = better retention for that file.

## Minecraft bot

```bash
# Terminal 1 — start server in server/ first
python Chroma.py

# Terminal 2
node M_bot.js
```

Implementation lives in `agent/`. Root launchers (`Chroma.py`, `M_bot.js`) forward to those files.

## Project structure

| Path | Role |
|------|------|
| `model_v3.py` | Model architecture |
| `auto_train.py` | Main trainer |
| `config.py` | Hyperparameters |
| `dataset.py` | Mixed/replay/instruction sampling |
| `data/` | Training text |
| `agent/` | Minecraft parent + bot |
| `scripts/` | Legacy trainers and utilities |

## Training tips

- Add conversation data as `### INPUT:` / `### OUTPUT:` pairs in `data/`
- Or split paired files into `data/input/*.txt` and `data/output/*.txt` using `python scripts/split_instruction_data.py`
- Use `python interactive_correction.py` to fix bad replies (saves to `data/corrections.txt`)
- For wiki updates: `python auto_train.py --lr 0.0001 --epochs 30`
- Avoid `--sequential` unless debugging — it causes forgetting

## Split-data training workflows

### Train only split A/B files

```bash
python3 auto_train.py --split-data
```

### Train only normal root-level data files

```bash
python3 auto_train.py
```

### Train split A/B first, then root-level info files

```bash
python3 auto_train.py --split-data
python3 auto_train.py --retrain
```

### Train a specific split file by name

```bash
python3 auto_train.py --split-data --files input/english.txt
```

### Train only selected root-level files

```bash
python3 auto_train.py --files python.txt data_structures.txt
```

## Continuous learning

```bash
python continuous_learner.py          # local: scrape + train + push
python scrape_wikipedia.py            # fetch articles only
```
