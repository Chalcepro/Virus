#!/usr/bin/env python3
import subprocess
import sys
from scrape_wikipedia import fetch_random_wikipedia_article, save_to_data   # adjust to your scrape function

def main():
    print("Scraping new data...")
    content, title = fetch_random_wikipedia_article()
    filepath = save_to_data(content, title)

    print("Training on new data...")
    cmd = [sys.executable, "auto_train.py", "--lr", "0.0001"]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Training failed")
        sys.exit(1)

    print("\nStarting interactive correction session...")
    subprocess.run([sys.executable, "interactive_correction.py"])

    print("\nPushing updates to GitHub...")
    subprocess.run(["git", "add", "data/", "model_v3.pt", "auto_train_state.json"])
    subprocess.run(["git", "commit", "-m", "Auto-learn: new data and user corrections"])
    subprocess.run(["git", "push"])

    print("Continuous learning cycle completed.")

if __name__ == "__main__":
    main()