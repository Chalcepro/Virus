#!/usr/bin/env python3
"""
Demo script to show Words Generator integration in action.
Shows generated data samples and verifies integration.
"""

import sys
from pathlib import Path

# Import modules
current_dir = Path(__file__).parent
import importlib.util

spec_dict = importlib.util.spec_from_file_location(
    "word_dictionary", 
    current_dir / "words generator" / "deepseek_python_20260615_a821e8.py"
)
word_dictionary = importlib.util.module_from_spec(spec_dict)
sys.modules['word_dictionary'] = word_dictionary
spec_dict.loader.exec_module(word_dictionary)

spec_sg = importlib.util.spec_from_file_location(
    "sentence_generator",
    current_dir / "words generator" / "deepseek_python_20260615_c8f549.py"
)
sentence_generator = importlib.util.module_from_spec(spec_sg)
sys.modules['sentence_generator'] = sentence_generator
spec_sg.loader.exec_module(sentence_generator)

from sentence_generator import SentenceGenerator

def demo():
    """Show the Words Generator in action"""
    
    print("\n" + "="*70)
    print("WORDS GENERATOR - LIVE DEMO")
    print("="*70)
    
    sg = SentenceGenerator()
    
    # Demo 1: Word Lists
    print("\n📚 AVAILABLE WORDS")
    print("-" * 70)
    print(f"Nouns:       {', '.join(sg.nouns[:6])} ... ({len(sg.nouns)} total)")
    print(f"Verbs:       {', '.join(sg.verbs[:6])} ... ({len(sg.verbs)} total)")
    print(f"Adjectives:  {', '.join(sg.adjectives[:6])} ... ({len(sg.adjectives)} total)")
    print(f"Adverbs:     {', '.join(sg.adverbs[:6])} ... ({len(sg.adverbs)} total)")
    print(f"Pronouns:    {', '.join(sg.pronouns_subj)} (subject)")
    
    # Demo 2: Sentence Patterns
    print("\n" + "="*70)
    print("📝 SENTENCE PATTERN EXAMPLES")
    print("="*70)
    
    patterns = [
        ("SVO (Subject-Verb-Object)", sg.pattern_svo, "present"),
        ("SVC (Subject-Verb-Complement)", sg.pattern_svc, "present"),
        ("SV (Subject-Verb)", sg.pattern_sv, "present"),
        ("SV+Adverb", sg.pattern_sv_adv, None),
        ("Interrogative (Yes/No)", sg.pattern_interrogative_sv, None),
        ("Interrogative (Wh-)", sg.pattern_interrogative_wh, None),
        ("Imperative", sg.pattern_imperative, None),
    ]
    
    for name, pattern, tense in patterns:
        try:
            if tense:
                sentence = pattern(tense)
            else:
                sentence = pattern()
            print(f"\n{name:30} → {sentence}")
        except Exception as e:
            print(f"\n{name:30} → [Error: {type(e).__name__}]")
    
    # Demo 3: Generated Content Samples
    print("\n" + "="*70)
    print("🎯 GENERATED CONTENT SAMPLES")
    print("="*70)
    
    # Sample conversations
    print("\n💬 CONVERSATION SAMPLE:")
    print("-" * 70)
    for i in range(3):
        if i % 2 == 0:
            print(f"ME: {sg.pattern_interrogative_wh()}")
        else:
            print(f"YOU: {sg.pattern_svo('present')}")
    
    # Sample knowledge
    print("\n\n💡 KNOWLEDGE Q&A SAMPLE:")
    print("-" * 70)
    for i in range(2):
        noun = sg.nouns[i % len(sg.nouns)]
        print(f"\n### INPUT:")
        print(f"What is a {noun}?")
        print(f"### OUTPUT:")
        print(f"A {sg.get_article(noun)} {noun} is {sg.pattern_svc('present').lower()}")
    
    # Demo 4: File Summary
    print("\n" + "="*70)
    print("📊 GENERATED FILES STATUS")
    print("="*70)
    
    import config
    base_data_dirs = [
        ("Conversations", config.DATA_DIR / 'base-data-conversations'),
        ("Knowledge", config.DATA_DIR / 'base-data-knowledge'),
        ("Sentences", config.DATA_DIR / 'base-data-sentences'),
    ]
    
    total_files = 0
    total_size = 0
    
    for name, dir_path in base_data_dirs:
        if dir_path.exists():
            files = list(dir_path.glob("*.txt"))
            if files:
                size_kb = sum(f.stat().st_size for f in files) / 1024
                lines = sum(len(open(f).readlines()) for f in files)
                total_files += len(files)
                total_size += size_kb
                print(f"\n{name:15} ✓ {len(files)} files, {size_kb:6.1f} KB, {lines:,} lines")
            else:
                print(f"\n{name:15} ✗ No files (run generator first)")
        else:
            print(f"\n{name:15} ✗ Directory doesn't exist")
    
    if total_files > 0:
        print(f"\n{'Total':15} {total_files} files, {total_size:.1f} KB")
        print(f"\n✅ Ready to train with: py -3 auto_train.py --base-data")
    else:
        print(f"\n⚠️  Generate data first: py -3 \"words generator\\main_generator.py\"")
    
    # Demo 5: Usage Examples
    print("\n" + "="*70)
    print("📋 USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        ("Generate data", 'py -3 "words generator\\main_generator.py"'),
        ("Custom generation", 'py -3 "words generator\\main_generator.py" --conversations 500 --sentences 3000'),
        ("Train with base-data", 'py -3 auto_train.py --base-data'),
        ("Full workflow", 'py -3 workflow.py --full'),
        ("Quick test", 'py -3 workflow.py --quick'),
    ]
    
    for desc, cmd in examples:
        print(f"\n{desc}:")
        print(f"  {cmd}")
    
    print("\n" + "="*70)
    print("✨ For more information, see WORDS_GENERATOR_GUIDE.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo()
