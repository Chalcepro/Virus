import random
import re
import torch

import config

INPUT_RE = re.compile(
    r"### INPUT:\s*\n(.*?)(?=\n### OUTPUT:|\Z)",
    re.DOTALL,
)

INSTRUCTION_OUTPUT_RE = re.compile(
    r"### OUTPUT:\s*\n(.*?)(?=\n### INPUT:|\Z)",
    re.DOTALL,
)


def parse_instruction_inputs(text):
    return [m.group(1).strip() for m in INPUT_RE.finditer(text) if len(m.group(1).strip()) > 0]


def parse_instruction_outputs(text):
    return [m.group(1).strip() for m in INSTRUCTION_OUTPUT_RE.finditer(text) if len(m.group(1).strip()) > 0]


def parse_instruction_pairs(text):
    inputs = parse_instruction_inputs(text)
    outputs = parse_instruction_outputs(text)
    return [(inp, out) for inp, out in zip(inputs, outputs) if inp and out]


def parse_lines(text):
    groups = re.split(r"\n\s*\n+", text.strip())
    return [group.strip() for group in groups if group.strip()]


class CodeDataset:
    def __init__(self, filepath, block_size=64):
        with open(filepath, encoding="utf-8") as f:
            self.text = f.read()

        chars = sorted(list(set(self.text)))
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for ch, i in self.stoi.items()}
        actual_vocab_size = len(chars)
        if config.FORCE_VOCAB_SIZE is not None:
            if config.FORCE_VOCAB_SIZE < actual_vocab_size:
                raise ValueError(
                    f"FORCE_VOCAB_SIZE ({config.FORCE_VOCAB_SIZE}) must be >= actual vocab size ({actual_vocab_size})"
                )
            self.vocab_size = config.FORCE_VOCAB_SIZE
        else:
            self.vocab_size = actual_vocab_size
        self.block_size = block_size
        self.data = torch.tensor([self.stoi[ch] for ch in self.text], dtype=torch.long)

    def get_batch(self, batch_size):
        max_start = len(self.data) - self.block_size - 1
        ix = torch.randint(0, max_start, (batch_size,))
        x = torch.stack([self.data[i : i + self.block_size] for i in ix])
        y = torch.stack([self.data[i + 1 : i + self.block_size + 1] for i in ix])
        return x, y

    def encode(self, text):
        return torch.tensor([self.stoi[ch] for ch in text if ch in self.stoi], dtype=torch.long)

    def decode(self, ids):
        return "".join([self.itos.get(i.item(), "") for i in ids])


class MixedDataset:
    """Sample batches across files with balanced domain weighting and instruction focus."""

    def __init__(
        self,
        filepaths,
        vocab_mapping,
        block_size=128,
        balanced=True,
        instruction_ratio=0.4,
    ):
        self.block_size = block_size
        self.stoi = vocab_mapping["stoi"]
        itos_raw = vocab_mapping.get("itos", {})
        self.itos = {int(k): v for k, v in itos_raw.items()}
        self.instruction_ratio = instruction_ratio
        self.sources = []
        self.instruction_sources = []

        input_files = {}
        output_files = {}
        regular_files = []

        for filepath in filepaths:
            if filepath.parent.name == "input":
                input_files[filepath.name] = filepath
                continue
            if filepath.parent.name == "output":
                output_files[filepath.name] = filepath
                continue
            regular_files.append(filepath)

        def add_source(name, text):
            data = torch.tensor([self.stoi.get(ch, 0) for ch in text], dtype=torch.long)
            if len(data) > block_size + 1:
                self.sources.append((name, data))

        def add_instruction_source(text):
            data = torch.tensor([self.stoi.get(ch, 0) for ch in text], dtype=torch.long)
            if len(data) > block_size + 1:
                self.instruction_sources.append(data)

        for filepath in regular_files:
            with open(filepath, encoding="utf-8") as f:
                text = f.read()

            add_source(str(filepath), text)

            outputs = parse_instruction_outputs(text)
            if outputs:
                combined_outputs = "\n\n".join(outputs).strip() + "\n"
                add_instruction_source(combined_outputs)

        for name, input_path in input_files.items():
            output_path = output_files.get(name)
            input_text = input_path.read_text(encoding="utf-8")
            inputs = parse_lines(input_text)

            if output_path is not None:
                output_text = output_path.read_text(encoding="utf-8")
                outputs = parse_lines(output_text)

                paired_text = "\n\n".join(
                    f"### INPUT:\n{inp}\n### OUTPUT:\n{out}" for inp, out in zip(inputs, outputs)
                ).strip() + "\n"
                add_source(f"{name}-pairs", paired_text)

                combined_outputs = "\n\n".join(outputs).strip() + "\n"
                add_instruction_source(combined_outputs)
            else:
                combined_inputs = "\n".join(inputs).strip() + "\n"
                add_source(f"{name}-prompts", combined_inputs)

        for name, output_path in output_files.items():
            if name in input_files:
                continue
            output_text = output_path.read_text(encoding="utf-8")
            outputs = parse_lines(output_text)
            combined_outputs = "\n\n".join(outputs).strip() + "\n"
            add_instruction_source(combined_outputs)

        # Fallback for files without explicit instruction markers
        if not self.instruction_sources and self.sources:
            for _, data in self.sources:
                if len(data) > block_size + 1:
                    self.instruction_sources.append(data)

        if not self.sources:
            raise ValueError("No usable training data in provided files")

        if balanced:
            self.weights = [1.0 / len(self.sources)] * len(self.sources)
        else:
            lengths = [len(data) for _, data in self.sources]
            total = sum(lengths)
            self.weights = [length / total for length in lengths]

    def _batch_from_tensor(self, data, batch_size):
        max_start = len(data) - self.block_size - 1
        ix = torch.randint(0, max_start, (batch_size,))
        x = torch.stack([data[i : i + self.block_size] for i in ix])
        y = torch.stack([data[i + 1 : i + self.block_size + 1] for i in ix])
        return x, y

    def get_batch(self, batch_size):
        if self.instruction_sources and random.random() < self.instruction_ratio:
            data = random.choice(self.instruction_sources)
            return self._batch_from_tensor(data, batch_size)

        _, data = random.choices(self.sources, weights=self.weights, k=1)[0]
        return self._batch_from_tensor(data, batch_size)


class ReplayTrainer:
    """Mix new-file batches with replay batches from previously trained files."""

    def __init__(self, new_files, replay_files, vocab_mapping, block_size=128, balanced=True, instruction_ratio=0.4):
        self.new_dataset = (
            MixedDataset(new_files, vocab_mapping, block_size, balanced, instruction_ratio)
            if new_files
            else None
        )
        self.replay_dataset = (
            MixedDataset(replay_files, vocab_mapping, block_size, balanced, instruction_ratio)
            if replay_files
            else None
        )

    def get_batch(self, batch_size, replay_ratio=0.35):
        use_replay = (
            self.replay_dataset is not None
            and self.new_dataset is not None
            and random.random() < replay_ratio
        )
        if use_replay:
            return self.replay_dataset.get_batch(batch_size)
        if self.new_dataset is not None:
            return self.new_dataset.get_batch(batch_size)
        if self.replay_dataset is not None:
            return self.replay_dataset.get_batch(batch_size)
        raise ValueError("ReplayTrainer has no data sources")
