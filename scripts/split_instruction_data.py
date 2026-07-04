from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

INPUT_RE = re.compile(r"### INPUT:\s*\n(.*?)(?=\n### OUTPUT:|\Z)", re.DOTALL)
OUTPUT_RE = re.compile(r"### OUTPUT:\s*\n(.*?)(?=\n### INPUT:|\Z)", re.DOTALL)


def parse_pairs(text):
    inputs = [m.group(1).strip() for m in INPUT_RE.finditer(text) if m.group(1).strip()]
    outputs = [m.group(1).strip() for m in OUTPUT_RE.finditer(text) if m.group(1).strip()]
    return list(zip(inputs, outputs))


def normalize_blocks(blocks):
    return [block.strip() for block in blocks if block.strip()]


def paragraph_blocks(text):
    groups = [grp.strip() for grp in re.split(r"\n\s*\n+", text.strip()) if grp.strip()]
    if groups:
        return groups
    return [text.strip()]


def split_text(text):
    text = text.strip()
    if not text:
        return ("", "")
    words = text.split()
    if len(words) >= 2:
        half = len(words) // 2
        return (" ".join(words[:half]).strip(), " ".join(words[half:]).strip())
    mid = len(text) // 2
    return (text[:mid].strip(), text[mid:].strip())


def build_pairs_from_blocks(blocks):
    blocks = normalize_blocks(blocks)
    pairs = []
    for i in range(0, len(blocks) - 1, 2):
        pairs.append((blocks[i], blocks[i + 1]))
    if len(blocks) % 2 == 1:
        last = blocks[-1]
        if pairs:
            question, answer = pairs[-1]
            pairs[-1] = (question, f"{answer}\n\n{last}")
        else:
            pairs.append(split_text(last))
    return pairs


def split_file(source_path):
    text = source_path.read_text(encoding="utf-8")
    pairs = parse_pairs(text)
    fallback = False
    if not pairs:
        blocks = paragraph_blocks(text)
        pairs = build_pairs_from_blocks(blocks)
        fallback = True

    if not pairs:
        return False

    name = source_path.name
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_path = INPUT_DIR / name
    output_path = OUTPUT_DIR / name

    input_blocks = [inp for inp, _ in pairs]
    output_blocks = [out for _, out in pairs]

    input_path.write_text("\n\n".join(normalize_blocks(input_blocks)) + "\n", encoding="utf-8")
    output_path.write_text("\n\n".join(normalize_blocks(output_blocks)) + "\n", encoding="utf-8")
    return True


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    txt_files = [p for p in DATA_DIR.glob("*.txt") if p.is_file()]
    if not txt_files:
        print("No root-level .txt files found to split.")
        return

    split_count = 0
    for txt in txt_files:
        if split_file(txt):
            split_count += 1
            print(f"Split {txt.name} -> data/input/{txt.name}, data/output/{txt.name}")
        else:
            print(f"Skipped {txt.name}: no ### INPUT:/### OUTPUT: pairs found")

    if split_count:
        print(f"\nWrote {split_count} split file(s).")
    else:
        print("No files were split.")


if __name__ == "__main__":
    main()
