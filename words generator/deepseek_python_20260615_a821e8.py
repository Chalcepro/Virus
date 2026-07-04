# word_dictionary.py

WORD_DICT = {
    # ========== NOUNS ==========
    "nouns": {
        "common": {
            # [word, consonant_start, consonant_end, vowel_count, syllable_count]
            "cat": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "animal"},
            "dog": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "animal"},
            "bird": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "animal"},
            "fish": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "animal"},
            "house": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 1, "class": "place"},
            "car": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "object"},
            "book": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "object"},
            "pen": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "object"},
            "table": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 2, "class": "object"},
            "chair": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "object"},
            "door": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "object"},
            "window": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 2, "class": "object"},
            "person": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 2, "class": "person"},
            "man": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "person"},
            "woman": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 2, "class": "person"},
            "child": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "person"},
            "day": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 1, "class": "time"},
            "night": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "time"},
            "year": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "time"},
            "water": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 2, "class": "substance"},
            "food": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "substance"},
            "air": {"pos": "n", "c_start": False, "c_end": True, "vowels": 2, "syllables": 1, "class": "substance"},
            "fire": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 2, "class": "element"},
            "earth": {"pos": "n", "c_start": False, "c_end": True, "vowels": 2, "syllables": 1, "class": "element"},
            "sun": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "celestial"},
            "moon": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "celestial"},
            "star": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "celestial"},
            "tree": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 1, "class": "plant"},
            "flower": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 2, "class": "plant"},
            "grass": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "plant"},
            "rock": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "object"},
            "stone": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 1, "class": "object"},
            "road": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "place"},
            "city": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 2, "class": "place"},
            "town": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "place"},
            "country": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 2, "class": "place"},
            "world": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "place"},
            "family": {"pos": "n", "c_start": True, "c_end": False, "vowels": 2, "syllables": 3, "class": "group"},
            "group": {"pos": "n", "c_start": True, "c_end": True, "vowels": 1, "syllables": 1, "class": "group"},
            "team": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "group"},
            "friend": {"pos": "n", "c_start": True, "c_end": True, "vowels": 2, "syllables": 1, "class": "person"},
        },
        
        # Proper nouns (with capital flag)
        "proper": {
            "john": {"pos": "np", "capital": True, "gender": "male"},
            "mary": {"pos": "np", "capital": True, "gender": "female"},
            "london": {"pos": "np", "capital": True, "type": "city"},
            "paris": {"pos": "np", "capital": True, "type": "city"},
            "monday": {"pos": "np", "capital": True, "type": "day"},
            "tuesday": {"pos": "np", "capital": True, "type": "day"},
            "january": {"pos": "np", "capital": True, "type": "month"},
        },
        
        # Plural forms
        "plural": {
            "cats": {"singular": "cat"},
            "dogs": {"singular": "dog"},
            "birds": {"singular": "bird"},
            "fish": {"singular": "fish", "irregular": True},
            "houses": {"singular": "house"},
            "cars": {"singular": "car"},
            "books": {"singular": "book"},
            "pens": {"singular": "pen"},
            "tables": {"singular": "table"},
            "chairs": {"singular": "chair"},
            "people": {"singular": "person", "irregular": True},
            "men": {"singular": "man", "irregular": True},
            "women": {"singular": "woman", "irregular": True},
            "children": {"singular": "child", "irregular": True},
            "days": {"singular": "day"},
            "years": {"singular": "year"},
            "trees": {"singular": "tree"},
            "flowers": {"singular": "flower"},
            "rocks": {"singular": "rock"},
            "cities": {"singular": "city"},
            "towns": {"singular": "town"},
            "families": {"singular": "family"},
            "groups": {"singular": "group"},
            "teams": {"singular": "team"},
            "friends": {"singular": "friend"},
        }
    },
    
    # ========== VERBS ==========
    "verbs": {
        "base": {
            # [base, conjugation_pattern, transitivity, vowel_start, consonant_end]
            "run": {"pos": "v", "pattern": "run_ran_run", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "walk": {"pos": "v", "pattern": "regular", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "jump": {"pos": "v", "pattern": "regular", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "sit": {"pos": "v", "pattern": "sit_sat_sat", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "stand": {"pos": "v", "pattern": "stand_stood_stood", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "eat": {"pos": "v", "pattern": "eat_ate_eaten", "transitive": True, "v_start": False, "c_end": True, "vowels": 2},
            "drink": {"pos": "v", "pattern": "drink_drank_drunk", "transitive": True, "v_start": False, "c_end": True, "vowels": 1},
            "see": {"pos": "v", "pattern": "see_saw_seen", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "look": {"pos": "v", "pattern": "regular", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "hear": {"pos": "v", "pattern": "hear_heard_heard", "transitive": True, "v_start": False, "c_end": True, "vowels": 2},
            "speak": {"pos": "v", "pattern": "speak_spoke_spoken", "transitive": True, "v_start": False, "c_end": True, "vowels": 2},
            "talk": {"pos": "v", "pattern": "regular", "transitive": False, "v_start": False, "c_end": True, "vowels": 1},
            "say": {"pos": "v", "pattern": "say_said_said", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "tell": {"pos": "v", "pattern": "tell_told_told", "transitive": True, "v_start": False, "c_end": True, "vowels": 1},
            "make": {"pos": "v", "pattern": "make_made_made", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "do": {"pos": "v", "pattern": "do_did_done", "transitive": True, "v_start": False, "c_end": False, "vowels": 1},
            "go": {"pos": "v", "pattern": "go_went_gone", "transitive": False, "v_start": False, "c_end": False, "vowels": 1},
            "come": {"pos": "v", "pattern": "come_came_come", "transitive": False, "v_start": False, "c_end": False, "vowels": 2},
            "give": {"pos": "v", "pattern": "give_gave_given", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "take": {"pos": "v", "pattern": "take_took_taken", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "have": {"pos": "v", "pattern": "have_had_had", "transitive": True, "v_start": False, "c_end": False, "vowels": 2},
            "be": {"pos": "v", "pattern": "be_was_been", "transitive": False, "v_start": False, "c_end": False, "vowels": 1, "auxiliary": True},
            "is": {"pos": "v", "tense": "present", "person": "3sg", "parent": "be"},
            "am": {"pos": "v", "tense": "present", "person": "1sg", "parent": "be"},
            "are": {"pos": "v", "tense": "present", "person": "plural", "parent": "be"},
            "was": {"pos": "v", "tense": "past", "person": "1/3sg", "parent": "be"},
            "were": {"pos": "v", "tense": "past", "person": "plural", "parent": "be"},
            "been": {"pos": "v", "form": "past_participle", "parent": "be"},
            "being": {"pos": "v", "form": "present_participle", "parent": "be"},
        },
        
        "past_tense": {
            "ran": {"base": "run"},
            "walked": {"base": "walk"},
            "jumped": {"base": "jump"},
            "ate": {"base": "eat"},
            "drank": {"base": "drink"},
            "saw": {"base": "see"},
            "looked": {"base": "look"},
            "heard": {"base": "hear"},
            "spoke": {"base": "speak"},
            "talked": {"base": "talk"},
            "said": {"base": "say"},
            "told": {"base": "tell"},
            "made": {"base": "make"},
            "did": {"base": "do"},
            "went": {"base": "go"},
            "came": {"base": "come"},
            "gave": {"base": "give"},
            "took": {"base": "take"},
            "had": {"base": "have"},
        },
        
        "past_participle": {
            "run": {"base": "run"},  # identical to base
            "walked": {"base": "walk"},
            "jumped": {"base": "jump"},
            "eaten": {"base": "eat"},
            "drunk": {"base": "drink"},
            "seen": {"base": "see"},
            "looked": {"base": "look"},
            "heard": {"base": "hear"},
            "spoken": {"base": "speak"},
            "talked": {"base": "talk"},
            "said": {"base": "say"},
            "told": {"base": "tell"},
            "made": {"base": "make"},
            "done": {"base": "do"},
            "gone": {"base": "go"},
            "come": {"base": "come"},
            "given": {"base": "give"},
            "taken": {"base": "take"},
            "had": {"base": "have"},
        },
        
        "present_participle": {
            "running": {"base": "run", "double_consonant": True},
            "walking": {"base": "walk"},
            "jumping": {"base": "jump"},
            "eating": {"base": "eat"},
            "drinking": {"base": "drink"},
            "seeing": {"base": "see"},
            "looking": {"base": "look"},
            "hearing": {"base": "hear"},
            "speaking": {"base": "speak"},
            "talking": {"base": "talk"},
            "saying": {"base": "say"},
            "telling": {"base": "tell"},
            "making": {"base": "make"},
            "doing": {"base": "do"},
            "going": {"base": "go"},
            "coming": {"base": "come"},
            "giving": {"base": "give"},
            "taking": {"base": "take"},
            "having": {"base": "have"},
        },
        
        "3sg_present": {
            "runs": {"base": "run"},
            "walks": {"base": "walk"},
            "jumps": {"base": "jump"},
            "eats": {"base": "eat"},
            "drinks": {"base": "drink"},
            "sees": {"base": "see"},
            "looks": {"base": "look"},
            "hears": {"base": "hear"},
            "speaks": {"base": "speak"},
            "talks": {"base": "talk"},
            "says": {"base": "say"},
            "tells": {"base": "tell"},
            "makes": {"base": "make"},
            "does": {"base": "do"},
            "goes": {"base": "go"},
            "comes": {"base": "come"},
            "gives": {"base": "give"},
            "takes": {"base": "take"},
            "has": {"base": "have"},
        }
    },
    
    # ========== ADJECTIVES ==========
    "adjectives": {
        "positive": {
            "big": {"pos": "adj", "comparative": "bigger", "superlative": "biggest", "syllables": 1, "gradable": True},
            "small": {"pos": "adj", "comparative": "smaller", "superlative": "smallest", "syllables": 1, "gradable": True},
            "fast": {"pos": "adj", "comparative": "faster", "superlative": "fastest", "syllables": 1, "gradable": True},
            "slow": {"pos": "adj", "comparative": "slower", "superlative": "slowest", "syllables": 1, "gradable": True},
            "good": {"pos": "adj", "comparative": "better", "superlative": "best", "irregular": True},
            "bad": {"pos": "adj", "comparative": "worse", "superlative": "worst", "irregular": True},
            "happy": {"pos": "adj", "comparative": "happier", "superlative": "happiest", "syllables": 2, "y_to_ier": True},
            "sad": {"pos": "adj", "comparative": "sadder", "superlative": "saddest", "syllables": 1},
            "beautiful": {"pos": "adj", "comparative": "more beautiful", "superlative": "most beautiful", "syllables": 3},
            "interesting": {"pos": "adj", "comparative": "more interesting", "superlative": "most interesting", "syllables": 4},
            "red": {"pos": "adj", "type": "color"},
            "blue": {"pos": "adj", "type": "color"},
            "green": {"pos": "adj", "type": "color"},
            "yellow": {"pos": "adj", "type": "color"},
            "black": {"pos": "adj", "type": "color"},
            "white": {"pos": "adj", "type": "color"},
            "hot": {"pos": "adj", "type": "temperature"},
            "cold": {"pos": "adj", "type": "temperature"},
            "warm": {"pos": "adj", "type": "temperature"},
            "cool": {"pos": "adj", "type": "temperature"},
            "new": {"pos": "adj", "type": "age"},
            "old": {"pos": "adj", "type": "age"},
            "young": {"pos": "adj", "type": "age"},
            "high": {"pos": "adj", "type": "measurement"},
            "low": {"pos": "adj", "type": "measurement"},
            "long": {"pos": "adj", "type": "measurement"},
            "short": {"pos": "adj", "type": "measurement"},
            "wide": {"pos": "adj", "type": "measurement"},
            "narrow": {"pos": "adj", "type": "measurement"},
            "strong": {"pos": "adj", "type": "quality"},
            "weak": {"pos": "adj", "type": "quality"},
            "hard": {"pos": "adj", "type": "quality"},
            "soft": {"pos": "adj", "type": "quality"},
            "bright": {"pos": "adj", "type": "quality"},
            "dark": {"pos": "adj", "type": "quality"},
            "light": {"pos": "adj", "type": "weight"},
            "heavy": {"pos": "adj", "type": "weight"},
            "rich": {"pos": "adj", "type": "wealth"},
            "poor": {"pos": "adj", "type": "wealth"},
            "clean": {"pos": "adj", "type": "condition"},
            "dirty": {"pos": "adj", "type": "condition"},
            "full": {"pos": "adj", "type": "state"},
            "empty": {"pos": "adj", "type": "state"},
            "open": {"pos": "adj", "type": "state"},
            "closed": {"pos": "adj", "type": "state"},
            "alive": {"pos": "adj", "type": "state"},
            "dead": {"pos": "adj", "type": "state"},
        },
        "comparative": {
            "bigger": {"positive": "big"},
            "smaller": {"positive": "small"},
            "faster": {"positive": "fast"},
            "slower": {"positive": "slow"},
            "better": {"positive": "good"},
            "worse": {"positive": "bad"},
            "happier": {"positive": "happy"},
            "sadder": {"positive": "sad"},
        },
        "superlative": {
            "biggest": {"positive": "big"},
            "smallest": {"positive": "small"},
            "fastest": {"positive": "fast"},
            "slowest": {"positive": "slow"},
            "best": {"positive": "good"},
            "worst": {"positive": "bad"},
            "happiest": {"positive": "happy"},
            "saddest": {"positive": "sad"},
        }
    },
    
    # ========== ADVERBS ==========
    "adverbs": {
        "manner": {
            "quickly": {"pos": "adv", "type": "manner", "adjective": "quick"},
            "slowly": {"pos": "adv", "type": "manner", "adjective": "slow"},
            "happily": {"pos": "adv", "type": "manner", "adjective": "happy"},
            "sadly": {"pos": "adv", "type": "manner", "adjective": "sad"},
            "easily": {"pos": "adv", "type": "manner", "adjective": "easy"},
            "hard": {"pos": "adv", "type": "manner"},
            "fast": {"pos": "adv", "type": "manner"},
            "well": {"pos": "adv", "type": "manner", "adjective": "good"},
            "badly": {"pos": "adv", "type": "manner", "adjective": "bad"},
        },
        "time": {
            "now": {"pos": "adv", "type": "time"},
            "then": {"pos": "adv", "type": "time"},
            "today": {"pos": "adv", "type": "time"},
            "tomorrow": {"pos": "adv", "type": "time"},
            "yesterday": {"pos": "adv", "type": "time"},
            "soon": {"pos": "adv", "type": "time"},
            "late": {"pos": "adv", "type": "time"},
            "early": {"pos": "adv", "type": "time"},
            "always": {"pos": "adv", "type": "frequency"},
            "never": {"pos": "adv", "type": "frequency"},
            "often": {"pos": "adv", "type": "frequency"},
            "sometimes": {"pos": "adv", "type": "frequency"},
            "usually": {"pos": "adv", "type": "frequency"},
            "rarely": {"pos": "adv", "type": "frequency"},
        },
        "place": {
            "here": {"pos": "adv", "type": "place"},
            "there": {"pos": "adv", "type": "place"},
            "everywhere": {"pos": "adv", "type": "place"},
            "nowhere": {"pos": "adv", "type": "place"},
            "inside": {"pos": "adv", "type": "place"},
            "outside": {"pos": "adv", "type": "place"},
            "up": {"pos": "adv", "type": "direction"},
            "down": {"pos": "adv", "type": "direction"},
            "in": {"pos": "adv", "type": "direction"},
            "out": {"pos": "adv", "type": "direction"},
            "away": {"pos": "adv", "type": "direction"},
            "back": {"pos": "adv", "type": "direction"},
        },
        "degree": {
            "very": {"pos": "adv", "type": "degree"},
            "quite": {"pos": "adv", "type": "degree"},
            "rather": {"pos": "adv", "type": "degree"},
            "almost": {"pos": "adv", "type": "degree"},
            "nearly": {"pos": "adv", "type": "degree"},
            "too": {"pos": "adv", "type": "degree"},
            "enough": {"pos": "adv", "type": "degree"},
            "so": {"pos": "adv", "type": "degree"},
            "such": {"pos": "adv", "type": "degree"},
        }
    },
    
    # ========== PRONOUNS ==========
    "pronouns": {
        "personal_subject": {
            "i": {"person": 1, "number": "singular", "case": "subjective"},
            "you": {"person": 2, "number": "singular/plural", "case": "subjective"},
            "he": {"person": 3, "number": "singular", "gender": "male", "case": "subjective"},
            "she": {"person": 3, "number": "singular", "gender": "female", "case": "subjective"},
            "it": {"person": 3, "number": "singular", "gender": "neuter", "case": "subjective"},
            "we": {"person": 1, "number": "plural", "case": "subjective"},
            "they": {"person": 3, "number": "plural", "case": "subjective"},
        },
        "personal_object": {
            "me": {"person": 1, "number": "singular", "case": "objective"},
            "you": {"person": 2, "number": "singular/plural", "case": "objective"},
            "him": {"person": 3, "number": "singular", "gender": "male", "case": "objective"},
            "her": {"person": 3, "number": "singular", "gender": "female", "case": "objective"},
            "it": {"person": 3, "number": "singular", "gender": "neuter", "case": "objective"},
            "us": {"person": 1, "number": "plural", "case": "objective"},
            "them": {"person": 3, "number": "plural", "case": "objective"},
        },
        "possessive_adjective": {
            "my": {"person": 1, "number": "singular"},
            "your": {"person": 2, "number": "singular/plural"},
            "his": {"person": 3, "number": "singular", "gender": "male"},
            "her": {"person": 3, "number": "singular", "gender": "female"},
            "its": {"person": 3, "number": "singular", "gender": "neuter"},
            "our": {"person": 1, "number": "plural"},
            "their": {"person": 3, "number": "plural"},
        },
        "possessive_pronoun": {
            "mine": {"person": 1, "number": "singular"},
            "yours": {"person": 2, "number": "singular/plural"},
            "his": {"person": 3, "number": "singular", "gender": "male"},
            "hers": {"person": 3, "number": "singular", "gender": "female"},
            "its": {"person": 3, "number": "singular", "gender": "neuter"},
            "ours": {"person": 1, "number": "plural"},
            "theirs": {"person": 3, "number": "plural"},
        },
        "reflexive": {
            "myself": {"person": 1, "number": "singular"},
            "yourself": {"person": 2, "number": "singular"},
            "himself": {"person": 3, "number": "singular", "gender": "male"},
            "herself": {"person": 3, "number": "singular", "gender": "female"},
            "itself": {"person": 3, "number": "singular", "gender": "neuter"},
            "ourselves": {"person": 1, "number": "plural"},
            "yourselves": {"person": 2, "number": "plural"},
            "themselves": {"person": 3, "number": "plural"},
        },
        "demonstrative": {
            "this": {"number": "singular", "distance": "near"},
            "that": {"number": "singular", "distance": "far"},
            "these": {"number": "plural", "distance": "near"},
            "those": {"number": "plural", "distance": "far"},
        },
        "interrogative": {
            "who": {"case": "subjective", "reference": "person"},
            "whom": {"case": "objective", "reference": "person"},
            "whose": {"case": "possessive", "reference": "person"},
            "which": {"reference": "thing"},
            "what": {"reference": "thing"},
        },
        "indefinite": {
            "someone": {"reference": "person", "specificity": "specific"},
            "somebody": {"reference": "person", "specificity": "specific"},
            "something": {"reference": "thing", "specificity": "specific"},
            "anyone": {"reference": "person", "specificity": "non-specific"},
            "anybody": {"reference": "person", "specificity": "non-specific"},
            "anything": {"reference": "thing", "specificity": "non-specific"},
            "no one": {"reference": "person", "specificity": "negative"},
            "nobody": {"reference": "person", "specificity": "negative"},
            "nothing": {"reference": "thing", "specificity": "negative"},
            "everyone": {"reference": "person", "specificity": "universal"},
            "everybody": {"reference": "person", "specificity": "universal"},
            "everything": {"reference": "thing", "specificity": "universal"},
            "each": {"reference": "individual"},
            "every": {"reference": "universal"},
            "all": {"reference": "universal"},
            "some": {"reference": "partial"},
            "any": {"reference": "non-specific"},
            "none": {"reference": "negative"},
        }
    },
    
    # ========== PREPOSITIONS ==========
    "prepositions": {
        "time": {
            "at": {"usage": "specific time"},
            "on": {"usage": "day/date"},
            "in": {"usage": "month/year/season"},
            "during": {"usage": "period"},
            "before": {"usage": "earlier than"},
            "after": {"usage": "later than"},
            "since": {"usage": "from past point"},
            "until": {"usage": "up to point"},
            "by": {"usage": "deadline"},
            "for": {"usage": "duration"},
        },
        "place": {
            "at": {"usage": "specific point"},
            "on": {"usage": "surface"},
            "in": {"usage": "enclosed space"},
            "inside": {"usage": "interior"},
            "outside": {"usage": "exterior"},
            "above": {"usage": "higher than"},
            "below": {"usage": "lower than"},
            "under": {"usage": "directly below"},
            "over": {"usage": "directly above"},
            "between": {"usage": "among two"},
            "among": {"usage": "among many"},
            "near": {"usage": "close to"},
            "far": {"usage": "distant from"},
            "behind": {"usage": "at back of"},
            "in front of": {"usage": "ahead of"},
            "next to": {"usage": "adjacent"},
            "beside": {"usage": "at side of"},
        },
        "direction": {
            "to": {"usage": "towards"},
            "from": {"usage": "away from"},
            "into": {"usage": "enter"},
            "out of": {"usage": "exit"},
            "onto": {"usage": "move to surface"},
            "off": {"usage": "away from surface"},
            "up": {"usage": "upwards"},
            "down": {"usage": "downwards"},
            "across": {"usage": "from one side to other"},
            "through": {"usage": "pass inside"},
            "along": {"usage": "following line"},
            "around": {"usage": "surrounding"},
            "past": {"usage": "beyond"},
        },
        "other": {
            "of": {"usage": "possession/relation"},
            "with": {"usage": "accompaniment"},
            "without": {"usage": "lack"},
            "like": {"usage": "similarity"},
            "as": {"usage": "function"},
            "about": {"usage": "concerning"},
            "against": {"usage": "opposition"},
            "for": {"usage": "purpose"},
            "by": {"usage": "agent"},
            "via": {"usage": "through"},
            "per": {"usage": "each"},
            "despite": {"usage": "contrast"},
            "except": {"usage": "exclusion"},
        }
    },
    
    # ========== CONJUNCTIONS ==========
    "conjunctions": {
        "coordinating": {
            "and": {"function": "addition"},
            "or": {"function": "alternative"},
            "but": {"function": "contrast"},
            "so": {"function": "result"},
            "for": {"function": "reason"},
            "nor": {"function": "negative addition"},
            "yet": {"function": "contrast"},
        },
        "subordinating": {
            "because": {"function": "reason"},
            "since": {"function": "reason/time"},
            "if": {"function": "condition"},
            "unless": {"function": "negative condition"},
            "although": {"function": "concession"},
            "though": {"function": "concession"},
            "whereas": {"function": "contrast"},
            "while": {"function": "time/contrast"},
            "when": {"function": "time"},
            "whenever": {"function": "any time"},
            "where": {"function": "place"},
            "wherever": {"function": "any place"},
            "as": {"function": "manner/time/reason"},
            "so that": {"function": "purpose"},
            "in order that": {"function": "purpose"},
            "so ... that": {"function": "result"},
            "such ... that": {"function": "result"},
        },
        "correlative": {
            "both...and": {},
            "either...or": {},
            "neither...nor": {},
            "not only...but also": {},
            "whether...or": {},
        }
    },
    
    # ========== DETERMINERS ==========
    "determiners": {
        "articles": {
            "a": {"type": "indefinite", "before_consonant": True},
            "an": {"type": "indefinite", "before_vowel": True},
            "the": {"type": "definite"},
        },
        "demonstrative": {
            "this": {"number": "singular", "distance": "near"},
            "that": {"number": "singular", "distance": "far"},
            "these": {"number": "plural", "distance": "near"},
            "those": {"number": "plural", "distance": "far"},
        },
        "quantifiers": {
            "some": {"type": "positive indefinite"},
            "any": {"type": "negative/indefinite"},
            "no": {"type": "negative"},
            "every": {"type": "universal"},
            "each": {"type": "distributive"},
            "either": {"type": "choice between two"},
            "neither": {"type": "negative choice"},
            "much": {"type": "uncountable"},
            "many": {"type": "countable plural"},
            "few": {"type": "small number"},
            "little": {"type": "small amount"},
            "several": {"type": "more than few"},
            "enough": {"type": "sufficient"},
        },
        "numbers": {
            "one": {"value": 1, "type": "cardinal"},
            "two": {"value": 2, "type": "cardinal"},
            "three": {"value": 3, "type": "cardinal"},
            "four": {"value": 4, "type": "cardinal"},
            "five": {"value": 5, "type": "cardinal"},
            "first": {"value": 1, "type": "ordinal"},
            "second": {"value": 2, "type": "ordinal"},
            "third": {"value": 3, "type": "ordinal"},
            "fourth": {"value": 4, "type": "ordinal"},
            "fifth": {"value": 5, "type": "ordinal"},
        }
    },
    
    # ========== INTERJECTIONS ==========
    "interjections": {
        "greeting": ["hello", "hi", "hey", "goodbye", "bye"],
        "agreement": ["yes", "yeah", "okay", "alright", "sure", "indeed"],
        "negation": ["no", "nope", "never"],
        "surprise": ["wow", "oh", "ah", "gosh", "my"],
        "pain": ["ouch", "ow", "ah"],
        "thinking": ["um", "uh", "well", "hmm", "er"],
        "attention": ["hey", "look", "listen", "psst"],
        "emotion": ["yay", "whoa", "aw", "phew", "alas"],
    }
}


# ========== VOWEL/CONSONANT CLASSIFICATION ==========
LETTERS = {
    "vowels": ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"],
    "consonants": ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z",
                   "B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "X", "Y", "Z"],
    "syllabic_consonants": ["l", "m", "n", "r"],  # can form syllable nucleus
}

def is_vowel(letter):
    return letter in LETTERS["vowels"]

def is_consonant(letter):
    return letter in LETTERS["consonants"]

def vowel_count(word):
    return sum(1 for c in word if is_vowel(c))

def consonant_count(word):
    return sum(1 for c in word if is_consonant(c))

def starts_with_vowel(word):
    return word and is_vowel(word[0])

def starts_with_consonant(word):
    return word and is_consonant(word[0])

def ends_with_vowel(word):
    return word and is_vowel(word[-1])

def ends_with_consonant(word):
    return word and is_consonant(word[-1])


# ========== SYLLABLE DIVISION ==========
def count_syllables(word):
    """Approximate syllable count for English words"""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    prev_is_vowel = False
    
    for i, char in enumerate(word):
        is_vowel_char = char in vowels
        if is_vowel_char and not prev_is_vowel:
            count += 1
        # Handle silent e at end
        if char == 'e' and i == len(word) - 1 and count > 1:
            count -= 1
        prev_is_vowel = is_vowel_char
    
    # Minimum one syllable
    return max(1, count)