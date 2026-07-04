# format_training_data.py

import random
from sentence_generator import SentenceGenerator, InstructionGenerator

class TrainingDataFormatter:
    """Formats generated data into your existing training format"""
    
    def __init__(self):
        self.sg = SentenceGenerator()
        self.ig = InstructionGenerator(self.sg)
    
    def generate_conversation(self, turns=4):
        """Generate a full conversation"""
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
                ai_line = r_pattern("present")
                conversation.append(f"YOU: {ai_line}")
        
        return "\n".join(conversation) + "\n"
    
    def generate_knowledge_entry(self):
        """Generate a knowledge Q&A entry"""
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
            answer = f"A {self.sg.get_article(noun)} {noun} is " + self.sg.pattern_svc("present").lower()
        elif "{adj}" in template:
            adj = random.choice(self.sg.adjectives)
            question = template.format(adj=adj)
            answer = f"Because {adj} things are " + self.sg.pattern_svc("present").lower()
        else:
            verb = random.choice(self.sg.verbs)
            question = template.format(verb=verb)
            answer = f"To {verb} means " + self.sg.pattern_sv_adv().lower()
        
        return f"### INPUT:\n{question}\n### OUTPUT:\n{answer}\n"
    
    def generate_full_training_file(self, output_path, num_conversations=200, num_knowledge=300, num_sentences=1000):
        """Generate a complete training file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write conversations
            for i in range(num_conversations):
                f.write(self.generate_conversation())
                f.write("\n")
            
            # Write knowledge entries
            for i in range(num_knowledge):
                f.write(self.generate_knowledge_entry())
                f.write("\n")
            
            # Write standalone sentences
            sentences = self.sg.generate_batch(num_sentences)
            for s in sentences:
                f.write(f"### INPUT:\n{s}\n### OUTPUT:\n{s}\n\n")
        
        print(f"Training data written to {output_path}")


if __name__ == "__main__":
    formatter = TrainingDataFormatter()
    formatter.generate_full_training_file("data/training_data_2024.txt")