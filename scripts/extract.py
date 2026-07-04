"""One-off utility: extract Python defs from all.txt into instruction pairs."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
text = (ROOT / "all.txt").read_text(encoding="utf-8")

py_start = text.find("#!/usr/bin/env python3")
if py_start == -1:
    raise ValueError("Could not find Python block in all.txt")

python_code = text[py_start:]
pattern = r"(?:^|\n)(@\w+[^\n]*\n)*(def |class )\w+[^:]*:.*?(?=\n(?:def |class |\Z))"
instructions = []
for match in re.finditer(pattern, python_code, re.DOTALL):
    block = match.group(0).strip()
    if not block:
        continue
    first_line = block.split("\n")[0].strip()
    instruction = f"Write the following Python code:\n{first_line}"
    pair = f"### Instruction:\n{instruction}\n\n### Response:\n{block}"
    instructions.append(pair)

data = "\n<|endoftext|>\n".join(instructions)
(ROOT / "python_instructions.txt").write_text(data, encoding="utf-8")
print(f"Extracted {len(instructions)} Python instruction-response pairs.")
