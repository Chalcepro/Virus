import requests
import time
import random
import sys
import argparse
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; AutoBot/1.0)"
HEADERS = {"User-Agent": USER_AGENT}

def fetch_random_wikipedia_article(retries=3):
    """Get a random Wikipedia article summary with retries."""
    for attempt in range(retries):
        try:
            # Use the REST API endpoint for random summary
            url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            if not resp.text:
                raise ValueError(f"Empty response body from {url} (status {resp.status_code})")
            try:
                data = resp.json()
            except ValueError as e:
                raise ValueError(f"Invalid JSON response from {url}: {e}; response text: {resp.text!r}") from e
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

def fetch_multiple_wikipedia_articles(num_articles=1, retries=3):
    """Fetch multiple Wikipedia articles and return list of (content, title) tuples."""
    articles = []
    for i in range(num_articles):
        try:
            print(f"Fetching article {i+1}/{num_articles}...")
            content, title = fetch_random_wikipedia_article(retries=retries)
            articles.append((content, title))
            # Add delay between requests to be respectful to Wikipedia
            if i < num_articles - 1:
                time.sleep(1)
        except Exception as e:
            print(f"Failed to fetch article {i+1}: {e}")
            continue
    
    if not articles:
        raise RuntimeError("Failed to fetch any Wikipedia articles")
    
    return articles

def save_to_data(text, title, data_dir="data"):
    Path(data_dir).mkdir(exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in " ._-")[:50]
    filename = f"wiki_{safe_title}_{int(time.time())}.txt"
    filepath = Path(data_dir) / filename
    filepath.write_text(text, encoding="utf-8")
    print(f"Saved: {filepath}")
    return filepath

def save_multiple_articles(articles, data_dir="data"):
    """Save multiple articles and return list of file paths."""
    filepaths = []
    for content, title in articles:
        filepath = save_to_data(content, title, data_dir)
        filepaths.append(filepath)
    return filepaths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Wikipedia articles")
    parser.add_argument("--num-articles", type=int, default=1, help="Number of Wikipedia articles to fetch (default: 1)")
    args = parser.parse_args()
    
    print(f"Fetching {args.num_articles} Wikipedia article(s)...")
    articles = fetch_multiple_wikipedia_articles(num_articles=args.num_articles)
    filepaths = save_multiple_articles(articles)
    print(f"\nSuccessfully saved {len(filepaths)} article(s)!")
