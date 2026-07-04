#!/usr/bin/env python3
import argparse
import subprocess
import sys

import config
from scrape_wikipedia import fetch_multiple_wikipedia_articles, save_multiple_articles


def main():
    parser = argparse.ArgumentParser(description="Scrape Wikipedia, train, and push to GitHub")
    parser.add_argument("--num-articles", type=int, default=1)
    args = parser.parse_args()

    print(f"Scraping {args.num_articles} Wikipedia article(s)...")
    articles = fetch_multiple_wikipedia_articles(num_articles=args.num_articles)
    filepaths = save_multiple_articles(articles)
    print(f"Saved {len(filepaths)} article(s)")

    print("Training on new data (mixed + replay, low LR)...")
    result = subprocess.run(
        [sys.executable, "auto_train.py", "--lr", "0.0001", "--epochs", "30"],
        check=False,
    )
    if result.returncode != 0:
        print("Training failed")
        sys.exit(1)

    print("Pushing updates to GitHub...")
    subprocess.run(["git", "add", "data/", str(config.MODEL_PATH), "auto_train_state.json", "vocab.json"])
    subprocess.run(
        ["git", "commit", "-m", f"Auto-learn: {len(filepaths)} new wiki article(s)"],
        check=False,
    )
    subprocess.run(["git", "push"])
    print("Continuous learning cycle completed.")


if __name__ == "__main__":
    main()
