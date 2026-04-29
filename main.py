import sys
from generate_v3 import generate

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "def "
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    temperature = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9
    top_k = int(sys.argv[4]) if len(sys.argv) > 4 else 40

    generate(prompt, max_tokens, temperature, top_k)