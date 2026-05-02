#!/usr/bin/env python3
import subprocess
import sys
import argparse
from scrape_wikipedia import fetch_multiple_wikipedia_articles, save_multiple_articles

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Continuous learning: scrape wiki + train + correct")
    parser.add_argument("--num-articles", type=int, default=1, help="Number of Wikipedia articles to fetch (default: 1)")
    args = parser.parse_args()
    num_articles = args.num_articles
    
    print(f"📖 Scraping {num_articles} Wikipedia article(s)...")
    articles = fetch_multiple_wikipedia_articles(num_articles=num_articles)
    filepaths = save_multiple_articles(articles)
    print(f"✓ Saved {len(filepaths)} article(s)")

    print("🧠 Training on new data...")
    cmd = [sys.executable, "auto_train.py", "--lr", "0.0001"]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Training failed")
        sys.exit(1)

    print("\n🔧 Starting interactive correction session...")
    subprocess.run([sys.executable, "interactive_correction.py"])

    print("\n📤 Pushing updates to GitHub...")
    subprocess.run(["git", "add", "data/", "model_v3.pt", "auto_train_state.json"])
    subprocess.run(["git", "commit", "-m", f"Auto-learn: {len(filepaths)} new wiki article(s) and user corrections"])
    subprocess.run(["git", "push"])

    print("✅ Continuous learning cycle completed.")

if __name__ == "__main__":
    main()