#!/usr/bin/env python3
import subprocess
import sys
from scrape_wikipedia import fetch_random_wikipedia_article, save_to_data

def main():
    print("🌐 Scraping new data...")
    content, title = fetch_random_wikipedia_article()
    filepath = save_to_data(content, title)

    print("🧠 Training on new data (low LR)...")
    cmd = [sys.executable, "auto_train.py", "--lr", "0.0001"]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Training failed")
        sys.exit(1)

    print("✅ Automated learning completed. No interactive session on CI.")
    # No git push here – let the GitHub Action handle pushing after this script

if __name__ == "__main__":
    main()
