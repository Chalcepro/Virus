# Words Generator Integration Guide

## Overview

The **Words Generator** system creates synthetic training data from rule-based sentence generation. It generates conversations, knowledge Q&A pairs, and standalone sentences that are organized in dedicated `base-data-*` folders to distinguish them from user data.

### What Was Added

1. **Main Generator Script** (`words generator/main_generator.py`)
   - Master script that orchestrates all generation
   - Creates conversations, knowledge entries, and sentences
   - Organizes output into category folders

2. **Enhanced auto_train.py**
   - Added `--base-data` flag to include generated data
   - Modified `get_data_files()` to support base-data folders
   - Base-data is kept separate for easy distinction from manual/scraped data

3. **Generated Data Folders**
   ```
   data/
   ├── base-data-conversations/   (ME: / YOU: dialogue format)
   ├── base-data-knowledge/       (### INPUT: / ### OUTPUT: Q&A format)
   ├── base-data-sentences/       (### INPUT: / ### OUTPUT: sentence pairs)
   └── [existing data files]
   ```

---

## Quick Start

### 1. Generate Training Data

```bash
# Generate default amounts (200 conversations, 200 knowledge, 500 sentences)
py -3 "words generator\main_generator.py"

# Custom amounts
py -3 "words generator\main_generator.py" --conversations 500 --knowledge 300 --sentences 2000

# Options
py -3 "words generator\main_generator.py" --help
```

**Output:**
- `data/base-data-conversations/conversations.txt` - Multi-turn conversations
- `data/base-data-knowledge/knowledge_qa.txt` - Q&A pairs
- `data/base-data-sentences/sentences.txt` - Single sentence pairs

### 2. Train with Base Data

```bash
# Include base-data in training
py -3 auto_train.py --base-data

# Train only with base-data (use --reset first to clear normal training state)
py -3 auto_train.py --base-data --retrain

# Customize training parameters
py -3 auto_train.py --base-data --epochs 30 --lr 0.0005

# Combine with split-data mode
py -3 auto_train.py --base-data --split-data --retrain
```

### 3. Use Trained Model

```bash
# Chat with the model (after training with base-data)
py -3 text_model.py

# Generate text
py -3 main.py "hello" 100
```

---

## Data Formats

### Conversations (`base-data-conversations/conversations.txt`)

```
ME: what is a cat?
YOU: i am a big cat.
ME: why is the cat big?
YOU: a cat is big.

ME: where do you live?
YOU: i live on the table.
...
```

- Multi-turn alternating format (ME: / YOU:)
- Configurable dialogue length (2-6 turns by default)
- Diverse question patterns and responses

### Knowledge Q&A (`base-data-knowledge/knowledge_qa.txt`)

```
### INPUT:
What is a dog?
### OUTPUT:
A dog is beautiful.

### INPUT:
Tell me about a house.
### OUTPUT:
A house is important.
...
```

- Question templates with random word substitution
- Answers generated from sentence patterns
- Compatible with existing ### INPUT/OUTPUT format

### Sentences (`base-data-sentences/sentences.txt`)

```
### INPUT:
she runs quickly.
### OUTPUT:
she runs quickly.

### INPUT:
i am big.
### OUTPUT:
i am big.
...
```

- Single sentence pairs (input = output)
- Diverse grammatical structures
- SVO, SVC, SV+adv, imperative, etc.

---

## Configuration

### Generator Parameters

Edit `words generator/main_generator.py` or pass command-line arguments:

```python
# Default amounts
num_conversations = 500  # Multi-turn dialogues
num_knowledge = 500      # Q&A pairs
num_sentences = 2000     # Single sentences
```

### Training Parameters

Use with `auto_train.py`:

```bash
py -3 auto_train.py --base-data \
  --epochs 30 \
  --lr 0.0005 \
  --replay-ratio 0.35 \
  --anchor-lambda 0.01
```

See `config.py` for defaults or `auto_train.py --help` for full options.

---

## Workflow Examples

### Example 1: Initial Training with Base Data

```bash
# Generate synthetic data
py -3 "words generator\main_generator.py" --conversations 300 --knowledge 300 --sentences 1000

# Train model with both regular and generated data
py -3 auto_train.py --base-data --epochs 25

# Chat to test
py -3 text_model.py
```

### Example 2: Base Data Only

```bash
# Reset previous training state
py -3 auto_train.py --reset

# Train only on generated data
py -3 auto_train.py --base-data --retrain --epochs 20
```

### Example 3: Expanding Training Data

```bash
# Generate large dataset
py -3 "words generator\main_generator.py" \
  --conversations 1000 \
  --knowledge 1000 \
  --sentences 5000

# Retrain with expanded base-data
py -3 auto_train.py --base-data --retrain --epochs 30
```

---

## File Organization

### Before Integration
```
data/
├── advanced_python.txt
├── algorithms.txt
├── conversation_1.0.txt
├── greetings.txt
├── ... (48 existing files)
└── [input/ and output/ if using --split-data]
```

### After Integration
```
data/
├── base-data-conversations/
│   └── conversations.txt (generated)
├── base-data-knowledge/
│   └── knowledge_qa.txt (generated)
├── base-data-sentences/
│   └── sentences.txt (generated)
├── advanced_python.txt (existing)
├── algorithms.txt (existing)
└── ... (all existing files)
```

**Key**: Base-data files have `base-data-` prefix to distinguish from manual/scraped data.

---

## Troubleshooting

### "No base-data files found"
```bash
# Verify files exist
dir data\base-data-*

# Regenerate if missing
py -3 "words generator\main_generator.py"
```

### "TypeError: SentenceGenerator.pattern_*() takes X positional arguments"
- Ensure you're running with Python 3 (`py -3`)
- The sentence_generator.py module has specific method signatures

### Training is slow with base-data
- Reduce `--epochs` on first run
- Use `--replay-ratio` to balance between new and old data
- Base-data is text-light but adds vocabulary diversity

### Want to clear base-data from training state
```bash
# Reset training tracking
py -3 auto_train.py --reset

# Now train without base-data
py -3 auto_train.py  # (no --base-data flag)
```

---

## Advanced Usage

### Regenerate With Different Parameters

```bash
# Increase diversity with more data
py -3 "words generator\main_generator.py" \
  --conversations 1000 \
  --knowledge 1000 \
  --sentences 10000 \
  --output data
```

### Inspect Generated Data Quality

```bash
# View sample conversations
type data\base-data-conversations\conversations.txt | more

# View sample knowledge pairs
type data\base-data-knowledge\knowledge_qa.txt | more

# Count lines per file
(gc data\base-data-conversations\conversations.txt | Measure-Object -Line).Lines
```

### Custom Training Schedule

```bash
# Train first on base-data only
py -3 auto_train.py --base-data --reset --epochs 20 --retrain

# Then continue training with regular data
py -3 auto_train.py --epochs 15
```

---

## Implementation Details

### How --base-data Works

1. **Modified `get_data_files()` function** in `auto_train.py`:
   - Checks for files in `data/base-data-conversations/`, etc.
   - Includes them in training file list when `--base-data` flag is set
   - Files are treated like regular data files (same training logic)

2. **Vocabulary Integration**:
   - Base-data vocabulary is merged with existing vocabulary
   - Model size automatically adjusted if needed
   - No separate vocab tracking

3. **Training**:
   - Base-data files are included in balanced sampling
   - Replayed according to `--replay-ratio`
   - Perplexity metrics reported per file

### Word Generator Architecture

```
word_dictionary.py (626 lines)
├── WORD_DICT with categories: nouns, verbs, adjectives, etc.
├── Helper functions: is_vowel(), starts_with_vowel(), etc.
└── Linguistic properties: consonant/vowel patterns, syllables

sentence_generator.py (420 lines)
├── SentenceGenerator class
│   ├── _init_word_lists() - Flatten dictionaries for quick access
│   ├── Pattern methods: pattern_svo(), pattern_svc(), etc.
│   └── Complex sentence generation
├── InstructionGenerator class
│   └── ### INPUT: / ### OUTPUT: format generation
└── Word-level linguistic awareness

main_generator.py (220 lines)
├── TrainingDataGenerator class
│   ├── generate_conversations() - Multi-turn dialogues
│   ├── generate_knowledge() - Q&A pairs
│   └── generate_sentences() - Single sentence pairs
└── Argument parsing and file organization
```

---

## Tips for Best Results

1. **Start Small**: Generate 200-300 examples of each type first, check quality
2. **Vary Data**: Use multiple generation runs to add diversity
3. **Balance Training**: Use `--replay-ratio` (default 0.35) to prevent forgetting
4. **Monitor Perplexity**: Check domain scores after training (`auto_train.py` prints these)
5. **Combine Strategically**: Base-data works best mixed with your domain-specific data

---

## Next Steps

- Generate large base-data sets for pre-training
- Fine-tune with domain-specific data afterward
- Use `--base-data --retrain` periodically to refresh model
- Combine with corrections and learning from `continuous_learner.py`

For questions about the training system, see [ARCHITECTURE.md](../ARCHITECTURE.md).
