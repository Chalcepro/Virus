import requests
import time
import random
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; AutoLearningBot/1.0; +https://github.com/yourusername/yourrepo)"
HEADERS = {"User-Agent": USER_AGENT}

def fetch_random_wikipedia_article(retries=3):
    """Get a random Wikipedia article summary with retries."""
    for attempt in range(retries):
        try:
            # Use the REST API endpoint for random summary
            url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            title = data["title"]
            extract = data["extract"]
            content = f"# Article: {title}\n# Source: Wikipedia\n\n{extract}\n"
            return content, title
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # exponential backoff
    raise RuntimeError("Failed to fetch Wikipedia article after retries")

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
