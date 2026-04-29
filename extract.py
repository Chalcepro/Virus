import re

with open('all.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the Python block (starts with the shebang line)
py_start = text.find('#!/usr/bin/env python3')
if py_start == -1:
    raise ValueError('Could not find Python block in all.txt')

python_code = text[py_start:]

# Extract function and class definitions (including docstrings/decorators)
# This regex captures a block that starts with 'def ' or 'class ' and continues
# until the next def/class at the same indentation level.
pattern = r'(?:^|\n)(@\w+[^\n]*\n)*(def |class )\w+[^:]*:.*?(?=\n(?:def |class |\Z))'
matches = re.finditer(pattern, python_code, re.DOTALL)

instructions = []
for match in matches:
    block = match.group(0).strip()
    if not block:
        continue
    # Use the first line as a simple description
    first_line = block.split('\n')[0].strip()
    instruction = f'Write the following Python code:\n{first_line}'
    pair = f'### Instruction:\n{instruction}\n\n### Response:\n{block}'
    instructions.append(pair)

# Add special end-of-text token after each response
data = '\n<|endoftext|>\n'.join(instructions)

with open('python_instructions.txt', 'w', encoding='utf-8') as f:
    f.write(data)

print(f'Extracted {len(instructions)} Python instruction–response pairs.')