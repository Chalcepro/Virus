import requests
import random
import time
from pathlib import Path

def fetch_random_wikipedia_article():
    """Get a random Wikipedia article in plain text."""
    # 1. Get a random article title
    rand_url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    resp = requests.get(rand_url)
    data = resp.json()
    title = data["title"]
    extract = data["extract"]   # plain text summary

    # 2. Add some metadata as a header
    content = f"# Article: {title}\n# Source: Wikipedia\n\n{extract}\n"
    return content, title

def save_to_data(text, title, data_dir="data"):
    Path(data_dir).mkdir(exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in " ._-")[:50]
    filename = f"wiki_{safe_title}_{int(time.time())}.txt"
    filepath = Path(data_dir) / filename
    filepath.write_text(text, encoding="utf-8")
    print(f"Saved: {filepath}")
    return filepath

if __name__ == "__main__":
    content, title = fetch_random_wikipedia_article()
    save_to_data(content, title)