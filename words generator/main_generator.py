#!/usr/bin/env python3
"""
Master script to generate training data from word-based templates.
Generates conversations, knowledge entries, and standalone sentences.
Organizes output into category-based folders with --base-data prefix.
"""

import sys
import os
from pathlib import Path

# Import from words_generator modules
# Rename files to proper module names on import
current_dir = Path(__file__).parent

# Dynamically load the modules
import importlib.util

# Load word_dictionary (from deepseek_python_20260615_a821e8.py)
spec_dict = importlib.util.spec_from_file_location(
    "word_dictionary", 
    current_dir / "deepseek_python_20260615_a821e8.py"
)
word_dictionary = importlib.util.module_from_spec(spec_dict)
sys.modules['word_dictionary'] = word_dictionary
spec_dict.loader.exec_module(word_dictionary)

# Load sentence_generator (from deepseek_python_20260615_c8f549.py)
spec_sg = importlib.util.spec_from_file_location(
    "sentence_generator",
    current_dir / "deepseek_python_20260615_c8f549.py"
)
sentence_generator = importlib.util.module_from_spec(spec_sg)
sys.modules['sentence_generator'] = sentence_generator
spec_sg.loader.exec_module(sentence_generator)

import random
from sentence_generator import SentenceGenerator, InstructionGenerator


class TrainingDataGenerator:
    """Generates and organizes training data into categories."""
    
    def __init__(self, output_base_dir="data"):
        self.output_base = Path(output_base_dir)
        self.sg = SentenceGenerator()
        self.ig = InstructionGenerator(self.sg)
        
        # Create output directories
        self.dirs = {
            'conversations': self.output_base / 'base-data-conversations',
            'knowledge': self.output_base / 'base-data-knowledge',
            'sentences': self.output_base / 'base-data-sentences',
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_conversation(self, turns=4):
        """Generate a full conversation."""
        conversation = []
        for i in range(turns):
            if i % 2 == 0:
                # User turn - generate a question or statement
                q_pattern = random.choice([self.sg.pattern_interrogative_sv, self.sg.pattern_interrogative_wh])
                user_line = q_pattern()
                if not user_line.endswith('?'):
                    user_line += '?'
                conversation.append(f"ME: {user_line}")
            else:
                # AI turn - generate a response
                r_pattern = random.choice([self.sg.pattern_svo, self.sg.pattern_svc, self.sg.pattern_sv_adv])
                try:
                    ai_line = r_pattern("present")
                except TypeError:
                    # Some patterns don't take tense argument
                    ai_line = r_pattern()
                conversation.append(f"YOU: {ai_line}")
        
        return "\n".join(conversation) + "\n"
    
    def generate_knowledge_entry(self):
        """Generate a knowledge Q&A entry."""
        question_templates = [
            "What is {noun}?",
            "Why is {adj}?",
            "How does {noun} work?",
            "What does {verb} mean?",
            "Tell me about {noun}.",
        ]
        
        template = random.choice(question_templates)
        if "{noun}" in template:
            noun = random.choice(self.sg.nouns)
            question = template.format(noun=noun)
            # Generate a factual-sounding answer
            try:
                answer = f"A {self.sg.get_article(noun)} {noun} is " + self.sg.pattern_svc("present").lower()
            except:
                answer = f"A {self.sg.get_article(noun)} {noun} is important."
        elif "{adj}" in template:
            adj = random.choice(self.sg.adjectives)
            question = template.format(adj=adj)
            try:
                answer = f"Because {adj} things are " + self.sg.pattern_svc("present").lower()
            except:
                answer = f"Because {adj} is a significant property."
        else:
            verb = random.choice(self.sg.verbs)
            question = template.format(verb=verb)
            try:
                answer = f"To {verb} means " + self.sg.pattern_sv_adv().lower()
            except:
                answer = f"To {verb} means to perform an action."
        
        return f"### INPUT:\n{question}\n### OUTPUT:\n{answer}\n"
    
    def generate_sentence(self):
        """Generate a standalone sentence."""
        pattern = random.choice([
            self.sg.pattern_svo,
            self.sg.pattern_svc,
            self.sg.pattern_sv_adv,
            self.sg.pattern_sv,
            self.sg.pattern_svoo,
        ])
        tense = random.choice(["present", "past"])
        try:
            sentence = pattern(tense)
        except TypeError:
            # Some patterns don't take tense argument
            sentence = pattern()
        
        return sentence.strip()
    
    def generate_conversations(self, num_conversations=500):
        """Generate conversations file."""
        output_file = self.dirs['conversations'] / 'conversations.txt'
        
        print(f"Generating {num_conversations} conversations...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(num_conversations):
                conversation = self.generate_conversation(turns=random.randint(2, 6))
                f.write(conversation)
                f.write("\n")
                
                if (i + 1) % 100 == 0:
                    print(f"  Generated {i + 1}/{num_conversations} conversations")
        
        print(f"✓ Conversations saved to {output_file}")
        return output_file
    
    def generate_knowledge(self, num_knowledge=500):
        """Generate knowledge Q&A file."""
        output_file = self.dirs['knowledge'] / 'knowledge_qa.txt'
        
        print(f"Generating {num_knowledge} knowledge entries...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(num_knowledge):
                entry = self.generate_knowledge_entry()
                f.write(entry)
                f.write("\n")
                
                if (i + 1) % 100 == 0:
                    print(f"  Generated {i + 1}/{num_knowledge} knowledge entries")
        
        print(f"✓ Knowledge saved to {output_file}")
        return output_file
    
    def generate_sentences(self, num_sentences=2000):
        """Generate standalone sentences file."""
        output_file = self.dirs['sentences'] / 'sentences.txt'
        
        print(f"Generating {num_sentences} sentences...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(num_sentences):
                sentence = self.generate_sentence()
                # Format as INPUT/OUTPUT pair
                f.write(f"### INPUT:\n{sentence}\n### OUTPUT:\n{sentence}\n\n")
                
                if (i + 1) % 500 == 0:
                    print(f"  Generated {i + 1}/{num_sentences} sentences")
        
        print(f"✓ Sentences saved to {output_file}")
        return output_file
    
    def generate_all(self, num_conversations=500, num_knowledge=500, num_sentences=2000):
        """Generate all training data."""
        print("\n" + "="*60)
        print("TRAINING DATA GENERATION")
        print("="*60 + "\n")
        
        files = {}
        files['conversations'] = self.generate_conversations(num_conversations)
        files['knowledge'] = self.generate_knowledge(num_knowledge)
        files['sentences'] = self.generate_sentences(num_sentences)
        
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"\nGenerated files:")
        for category, filepath in files.items():
            size = filepath.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  • {category:15} → {filepath.name:30} ({size:.2f} MB)")
        
        print(f"\nAll files organized in 'data/' with '--base-data' prefix:")
        print(f"  • data/base-data-conversations/")
        print(f"  • data/base-data-knowledge/")
        print(f"  • data/base-data-sentences/")
        
        print("\nTo train with this base data, use:")
        print("  python3 auto_train.py --base-data")
        
        return files


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate training data from word templates')
    parser.add_argument('--conversations', type=int, default=500, help='Number of conversations to generate')
    parser.add_argument('--knowledge', type=int, default=500, help='Number of knowledge entries to generate')
    parser.add_argument('--sentences', type=int, default=2000, help='Number of sentences to generate')
    parser.add_argument('--output', type=str, default='data', help='Output base directory')
    
    args = parser.parse_args()
    
    generator = TrainingDataGenerator(output_base_dir=args.output)
    generator.generate_all(
        num_conversations=args.conversations,
        num_knowledge=args.knowledge,
        num_sentences=args.sentences
    )


if __name__ == "__main__":
    main()
