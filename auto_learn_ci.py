#!/usr/bin/env python3
import argparse
import subprocess
import sys

from scrape_wikipedia import fetch_multiple_wikipedia_articles, save_multiple_articles


def main():
    parser = argparse.ArgumentParser(description="CI: scrape Wikipedia and train incrementally")
    parser.add_argument("--num-articles", type=int, default=1)
    args = parser.parse_args()

    print(f"Scraping {args.num_articles} Wikipedia article(s)...")
    articles = fetch_multiple_wikipedia_articles(num_articles=args.num_articles)
    filepaths = save_multiple_articles(articles)
    print(f"Saved {len(filepaths)} article(s)")

    print("Training on new data only (mixed + replay, low LR)...")
    result = subprocess.run(
        [sys.executable, "auto_train.py", "--lr", "0.0003", "--epochs", "30"],
        check=False,
    )
    if result.returncode != 0:
        print("Training failed")
        sys.exit(1)

    print(f"Automated learning completed ({len(filepaths)} new file(s)).")


if __name__ == "__main__":
    main()
