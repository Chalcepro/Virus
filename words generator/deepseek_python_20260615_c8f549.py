# sentence_generator.py

import random
import itertools
from word_dictionary import WORD_DICT, is_vowel, starts_with_vowel

class SentenceGenerator:
    """Generates infinite variations of English sentences"""
    
    def __init__(self):
        self.word_dict = WORD_DICT
        self._init_word_lists()
    
    def _init_word_lists(self):
        """Create flattened lists for quick access"""
        self.nouns = list(self.word_dict["nouns"]["common"].keys())
        self.nouns_plural = list(self.word_dict["nouns"]["plural"].keys())
        self.verbs = list(self.word_dict["verbs"]["base"].keys())
        self.verbs_past = list(self.word_dict["verbs"]["past_tense"].keys())
        self.verbs_ing = list(self.word_dict["verbs"]["present_participle"].keys())
        self.verbs_3sg = list(self.word_dict["verbs"]["3sg_present"].keys())
        self.adjectives = list(self.word_dict["adjectives"]["positive"].keys())
        self.adverbs = []
        for cat in self.word_dict["adverbs"]:
            self.adverbs.extend(self.word_dict["adverbs"][cat].keys())
        self.prepositions = []
        for cat in self.word_dict["prepositions"]:
            self.prepositions.extend(self.word_dict["prepositions"][cat].keys())
        self.pronouns_subj = list(self.word_dict["pronouns"]["personal_subject"].keys())
        self.pronouns_obj = list(self.word_dict["pronouns"]["personal_object"].keys())
        self.determiners = list(self.word_dict["determiners"]["articles"].keys())
        self.demonstratives = list(self.word_dict["determiners"]["demonstrative"].keys())
        self.quantifiers = list(self.word_dict["determiners"]["quantifiers"].keys())
        self.conj_coord = list(self.word_dict["conjunctions"]["coordinating"].keys())
        self.conj_subord = list(self.word_dict["conjunctions"]["subordinating"].keys())
    
    def get_article(self, noun):
        """Return 'a' or 'an' based on noun's starting sound"""
        return "an" if starts_with_vowel(noun) else "a"
    
    def random_word(self, word_list):
        return random.choice(word_list) if word_list else ""
    
    # ========== CLAUSE PATTERNS ==========
    
    def pattern_sv(self, tense="present"):
        """Subject + Verb (intransitive)"""
        subject = self.random_word(self.pronouns_subj)
        if subject in ["he", "she", "it"] and tense == "present":
            verb = self.random_word(self.verbs_3sg)
        elif tense == "past":
            verb = self.random_word(self.verbs_past)
        else:
            verb = self.random_word(self.verbs)
        return f"{subject} {verb}."
    
    def pattern_svo(self, tense="present"):
        """Subject + Verb + Object (transitive)"""
        subject = self.random_word(self.pronouns_subj)
        if subject in ["he", "she", "it"] and tense == "present":
            verb = self.random_word(self.verbs_3sg)
        elif tense == "past":
            verb = self.random_word(self.verbs_past)
        else:
            verb = self.random_word(self.verbs)
        # Add article to object
        obj = self.random_word(self.nouns)
        article = self.get_article(obj)
        return f"{subject} {verb} {article} {obj}."
    
    def pattern_svc(self, tense="present"):
        """Subject + Verb + Complement (adjective)"""
        subject = self.random_word(self.pronouns_subj)
        be_verb = {"present": "is", "past": "was"}.get(tense, "is")
        if subject in ["i"]:
            be_verb = "am" if tense == "present" else "was"
        elif subject in ["you", "we", "they"]:
            be_verb = "are" if tense == "present" else "were"
        
        adjective = self.random_word(self.adjectives)
        return f"{subject} {be_verb} {adjective}."
    
    def pattern_svoo(self):
        """Subject + Verb + Indirect Object + Direct Object"""
        subject = self.random_word(self.pronouns_subj)
        verb = self.random_word(["give", "show", "tell", "send", "offer"])
        if subject in ["he", "she", "it"]:
            verb = verb + "s" if verb not in ["give", "show", "tell"] else {"give": "gives", "show": "shows", "tell": "tells", "send": "sends", "offer": "offers"}.get(verb, verb)
        
        io = self.random_word(self.pronouns_obj)
        do = self.random_word(self.nouns)
        do_article = self.get_article(do)
        return f"{subject} {verb} {io} {do_article} {do}."
    
    def pattern_sv_adv(self):
        """Subject + Verb + Adverb"""
        subject = self.random_word(self.pronouns_subj)
        verb = self.random_word(self.verbs)
        if subject in ["he", "she", "it"]:
            verb = verb + "s"
        adverb = self.random_word(self.adverbs)
        return f"{subject} {verb} {adverb}."
    
    def pattern_there_be(self, tense="present"):
        """There + be + Noun (existential)"""
        be = "is" if tense == "present" else "was"
        be = f"are" if random.random() > 0.5 else be
        noun = self.random_word(self.nouns_plural if be == "are" else self.nouns)
        article = self.get_article(noun) if be != "are" else ""
        location = self.random_word(self.prepositions) + " the " + self.random_word(self.nouns) if random.random() > 0.5 else ""
        return f"There {be} {article} {noun} {location}.".strip()
    
    def pattern_imperative(self):
        """Command sentence"""
        verb = self.random_word(self.verbs)
        obj = self.random_word(self.nouns)
        article = self.get_article(obj)
        adverb = self.random_word(self.adverbs) if random.random() > 0.7 else ""
        return f"{verb} {article} {obj} {adverb}!".strip()
    
    def pattern_interrogative_sv(self):
        """Yes/No question"""
        subject = self.random_word(self.pronouns_subj)
        verb = self.random_word(self.verbs)
        if subject in ["he", "she", "it"]:
            verb = verb + "s"
        # Add do/does/do support
        auxiliary = ""
        if random.random() > 0.5:
            auxiliary = "do" if subject in ["i", "you", "we", "they"] else "does"
            return f"{auxiliary} {subject} {verb}?"
        else:
            return f"{verb} {subject}?"
    
    def pattern_interrogative_wh(self):
        """Wh- question"""
        wh_words = ["what", "where", "when", "why", "who", "how"]
        wh = self.random_word(wh_words)
        subject = self.random_word(self.pronouns_subj)
        verb = self.random_word(self.verbs)
        return f"{wh} {verb} {subject}?"
    
    # ========== COMPOUND SENTENCES ==========
    
    def compound_sentence(self):
        """Two independent clauses joined by coordinating conjunction"""
        pattern_choices = [self.pattern_svo, self.pattern_svc, self.pattern_sv]
        clause1 = random.choice(pattern_choices)("present")
        clause2 = random.choice(pattern_choices)("present")
        conj = self.random_word(self.conj_coord)
        return f"{clause1} {conj} {clause2}"
    
    def complex_sentence(self):
        """Independent + subordinate clause"""
        main = self.pattern_svo("present")
        sub_conj = self.random_word(self.conj_subord)
        sub_clause = self.pattern_sv("present")
        # Remove period from main
        main = main.rstrip('.')
        return f"{main} {sub_conj} {sub_clause}"
    
    # ========== EXPANDED SENTENCES (with modifiers) ==========
    
    def pattern_svo_expanded(self):
        """SVO with adjectives, adverbs, prepositional phrases"""
        # Subject with adjectives
        subject = self.random_word(self.pronouns_subj)
        adj1 = self.random_word(self.adjectives) if random.random() > 0.6 else ""
        adj2 = self.random_word(self.adjectives) if random.random() > 0.7 else ""
        subject_prefix = f"{adj1} {adj2} ".strip() if adj1 else ""
        
        # Verb with adverb
        verb = self.random_word(self.verbs)
        if subject in ["he", "she", "it"]:
            verb = verb + "s"
        adverb = self.random_word(self.adverbs) if random.random() > 0.6 else ""
        
        # Object with adjectives
        obj = self.random_word(self.nouns)
        obj_adj1 = self.random_word(self.adjectives) if random.random() > 0.6 else ""
        obj_adj2 = self.random_word(self.adjectives) if random.random() > 0.7 else ""
        obj_prefix = f"{obj_adj1} {obj_adj2} ".strip() if obj_adj1 else ""
        article = self.get_article(obj)
        
        # Prepositional phrase
        prep_phrase = ""
        if random.random() > 0.5:
            prep = self.random_word(self.prepositions)
            prep_obj = self.random_word(self.nouns)
            prep_article = self.get_article(prep_obj)
            prep_phrase = f"{prep} {prep_article} {prep_obj}"
        
        parts = [f"{subject_prefix}{subject}".strip(), adverb, f"{verb}", f"{article} {obj_prefix}{obj}".strip(), prep_phrase]
        sentence = " ".join(p for p in parts if p)
        return sentence.capitalize() + "."
    
    # ========== PROGRESSIVE TENSES ==========
    
    def pattern_progressive(self, tense="present"):
        """Subject + be + V-ing"""
        subject = self.random_word(self.pronouns_subj)
        
        # Choose correct be form
        be_map = {
            ("i", "present"): "am",
            ("he", "present"): "is",
            ("she", "present"): "is",
            ("it", "present"): "is",
            ("you", "present"): "are",
            ("we", "present"): "are",
            ("they", "present"): "are",
            ("i", "past"): "was",
            ("he", "past"): "was",
            ("she", "past"): "was",
            ("it", "past"): "was",
            ("you", "past"): "were",
            ("we", "past"): "were",
            ("they", "past"): "were",
        }
        be = be_map.get((subject, tense), "is")
        
        verb_ing = self.random_word(self.verbs_ing)
        # Optional object
        obj = ""
        if random.random() > 0.5:
            obj_noun = self.random_word(self.nouns)
            obj_article = self.get_article(obj_noun)
            obj = f"{obj_article} {obj_noun}"
        
        return f"{subject} {be} {verb_ing} {obj}".strip() + "."
    
    # ========== PERFECT TENSES ==========
    
    def pattern_perfect(self, tense="present"):
        """Subject + have/has + past participle"""
        subject = self.random_word(self.pronouns_subj)
        
        have = "have"
        if subject in ["he", "she", "it"]:
            have = "has"
        if tense == "past":
            have = "had"
        
        pp = self.random_word(list(self.word_dict["verbs"]["past_participle"].keys()))
        
        obj = ""
        if random.random() > 0.5:
            obj_noun = self.random_word(self.nouns)
            obj_article = self.get_article(obj_noun)
            obj = f"{obj_article} {obj_noun}"
        
        return f"{subject} {have} {pp} {obj}".strip() + "."
    
    # ========== PASSIVE VOICE ==========
    
    def pattern_passive(self, tense="present"):
        """Object + be + past participle + (by subject)"""
        obj_noun = self.random_word(self.nouns)
        obj_article = self.get_article(obj_noun)
        obj = f"{obj_article} {obj_noun}"
        
        be = {"present": "is", "past": "was"}.get(tense, "is")
        pp = self.random_word(list(self.word_dict["verbs"]["past_participle"].keys()))
        
        # Optional agent
        agent = ""
        if random.random() > 0.5:
            agent_subj = self.random_word(self.pronouns_obj)
            agent = f"by {agent_subj}"
        
        return f"{obj} {be} {pp} {agent}".strip() + "."
    
    # ========== NEGATION ==========
    
    def pattern_negation(self, pattern_type="svo"):
        """Negative sentence"""
        pattern = getattr(self, f"pattern_{pattern_type}")
        positive = pattern("present")
        # Simple negation for be verbs
        if " is " in positive or " are " in positive or " am " in positive:
            return positive.replace(" is ", " is not ").replace(" are ", " are not ").replace(" am ", " am not ")
        # Add do/does/did not
        words = positive.split()
        if words and words[0] in self.pronouns_subj:
            subj = words[0]
            aux = "do not" if subj in ["i", "you", "we", "they"] else "does not"
            # Remove existing verb's s/es
            if len(words) > 1:
                verb = words[1]
                if verb.endswith('s') and subj in ["he", "she", "it"]:
                    verb = verb[:-1]
                return f"{subj} {aux} {verb} " + " ".join(words[2:])
        return "not " + positive
    
    # ========== COMPARATIVES ==========
    
    def pattern_comparative(self):
        """Comparative sentence (X is ADJ-er than Y)"""
        subject = self.random_word(self.nouns)
        subj_article = self.get_article(subject)
        adj = self.random_word([a for a in self.adjectives if len(a) <= 5 and a not in ["good", "bad", "beautiful", "interesting"]])
        # Get comparative form
        if adj.endswith('y'):
            comp = adj[:-1] + "ier"
        elif len(adj) <= 4:
            comp = adj + "er"
        else:
            comp = "more " + adj
        obj = self.random_word(self.nouns)
        obj_article = self.get_article(obj)
        return f"{subj_article} {subject} is {comp} than {obj_article} {obj}."
    
    # ========== GENERATE BATCH OF SENTENCES ==========
    
    def generate_batch(self, count=1000, output_file=None):
        """Generate large number of varied sentences"""
        patterns = [
            self.pattern_sv, self.pattern_svo, self.pattern_svc, self.pattern_svoo,
            self.pattern_sv_adv, self.pattern_there_be, self.pattern_imperative,
            self.pattern_interrogative_sv, self.pattern_interrogative_wh,
            self.compound_sentence, self.complex_sentence, self.pattern_svo_expanded,
            self.pattern_progressive, self.pattern_perfect, self.pattern_passive,
            self.pattern_negation, self.pattern_comparative
        ]
        
        tenses = ["present", "past"]
        sentences = []
        
        for i in range(count):
            pattern = random.choice(patterns)
            if pattern in [self.pattern_sv, self.pattern_svo, self.pattern_svc, self.pattern_there_be]:
                tense = random.choice(tenses)
                sentence = pattern(tense)
            elif pattern in [self.pattern_progressive, self.pattern_perfect, self.pattern_passive]:
                tense = random.choice(tenses)
                sentence = pattern(tense)
            else:
                sentence = pattern()
            
            # Ensure proper capitalization and period
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            sentences.append(sentence)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for s in sentences:
                    f.write(s + '\n')
            print(f"Generated {count} sentences to {output_file}")
        
        return sentences


# ========== INSTRUCTION FORMAT GENERATOR ==========

class InstructionGenerator:
    """Generates instruction-response pairs in the ### INPUT: / ### OUTPUT: format"""
    
    def __init__(self, sentence_gen):
        self.sg = sentence_gen
    
    def generate_instruction_pair(self):
        """Generate one instruction-response pair"""
        instruction_templates = [
            "what is {noun}",
            "tell me about {noun}",
            "how do you {verb}",
            "why is {adj}",
            "explain {noun}",
            "what does {verb} mean",
            "describe {noun}",
            "give me an example of {noun}",
            "how can I {verb}",
            "when should I {verb}",
            "where can I find {noun}",
            "who is {proper_noun}",
        ]
        
        template = random.choice(instruction_templates)
        
        # Fill template with random words
        instruction = template.format(
            noun=random.choice(self.sg.nouns),
            verb=random.choice(self.sg.verbs),
            adj=random.choice(self.sg.adjectives),
            proper_noun=random.choice(["John", "Mary", "London", "Paris"])
        )
        
        # Generate a response using sentence patterns
        response_pattern = random.choice([
            self.sg.pattern_svo,
            self.sg.pattern_svc,
            self.sg.pattern_sv_adv
        ])
        response = response_pattern("present")
        
        return f"### INPUT:\n{instruction}\n### OUTPUT:\n{response}\n"
    
    def generate_batch(self, count=500, output_file=None):
        """Generate many instruction-response pairs"""
        pairs = []
        for _ in range(count):
            pairs.append(self.generate_instruction_pair())
        
        text = "\n".join(pairs)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Generated {count} instruction pairs to {output_file}")
        
        return text


# ========== MAIN EXECUTION ==========

if __name__ == "__main__":
    sg = SentenceGenerator()
    ig = InstructionGenerator(sg)
    
    # Generate training data in your format
    print("Generating sentences...")
    sg.generate_batch(5000, "data/generated_sentences.txt")
    
    print("Generating instruction pairs...")
    ig.generate_batch(2000, "data/generated_instructions.txt")
    
    print("Done! Training data ready.")