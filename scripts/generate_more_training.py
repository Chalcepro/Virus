from pathlib import Path
import random
root = Path('data')
root.mkdir(exist_ok=True)

def write_file(path, pairs):
    path.write_text('\n\n'.join(pairs) + '\n', encoding='utf-8')
    print(f'Wrote {path} ({len(pairs)} pairs)')

# Pools for inputs and responses
casual = ['hey', 'hi', 'hello', 'yo', 'sup', 'what\'s up', 'hey there', 'hiya', 'howdy']
time_based = ['good morning', 'good afternoon', 'good evening', 'good night', 'morning', 'evening']
slang = ['wassup', 'whats poppin', 'yoo', 'yo yo', 'sup bro', 'sup fam']
naija = ['how you dey', 'how far', 'una dey', 'how body', 'how far na', 'i dey here']
multilingual = ['hola', 'bonjour', 'ciao', 'konnichiwa', 'namaste', 'salaam', 'shalom', 'ola']
are_you_there = ['are you there', 'you there', 'are you awake', 'still there', 'anyone there', 'hello?']
reentry = ["I\'m back", 'back', 'just got back', 'back online', 'i\'m here again']
name_based = ['hey bro', 'hey fam', 'hey sis', 'hey mate', 'hey friend', 'hey boss']
closing = ['bye', 'see you', 'later', 'catch you later', 'talk soon', 'peace']

# generate greeting inputs
greeting_inputs = []
for pool in (casual, time_based, slang, naija, multilingual, are_you_there, reentry, name_based, closing):
    for phrase in pool:
        greeting_inputs.append(phrase)
# add variations with punctuation and short questions
extras = [p + '?' for p in greeting_inputs[:40]] + [p + '!!!' for p in greeting_inputs[40:80]]
greeting_inputs.extend(extras)

# responses for greetings
greeting_responses = [
    'hey, how\'s it going?', 'hi, good to see you', 'hello, what\'s up?', 'yo, all good here', 'not much, you?',
    'good morning, hope you slept well', 'good afternoon, how\'s your day?', 'good evening, how was your day?', 'night, sleep tight',
    'hiya, what\'s new?', 'i\'m here, tell me', 'yup, i\'m around', 'welcome back!', 'glad you\'re back', 'catch you later, take care',
]
# expand responses
while len(greeting_responses) < 200:
    greeting_responses += [r + (' now' if i%2==0 else '') for i,r in enumerate(greeting_responses)]
    greeting_responses = greeting_responses[:300]

# Everyday conversation pools
everyday_inputs = [
    'how are you feeling', 'are you tired', 'did you sleep well', 'what did you eat', 'are you hungry', 'how was work', 'how was school',
    'how\'s the weather', 'is it raining', 'are you busy', 'got any plans', 'what\'s for dinner', 'did you exercise', 'are you okay',
]
# expand everyday inputs with slight variants
for i in range(200):
    everyday_inputs.append(random.choice(['how are you', 'how\'s it going', 'you good', 'what\'s up']) + (' bro' if i%5==0 else ''))

everyday_responses = [
    'i\'m okay, you?', 'i\'m a bit tired but fine', 'slept okay, thanks', 'just had something to eat', 'i\'m full', 'work was busy', 'school was fine',
    'it\'s sunny here', 'a bit rainy, bring an umbrella', 'i\'m free later', 'no big plans', 'dinner sounds good', 'i\'m exercising later', 'i\'m alright',
]
# Knowledge and problem solving pools
knowledge_inputs = [
    'what is ai', 'how to fix a bug', 'why is the sky blue', 'how do i train a model', 'what is a neural network', 'how to make a website',
    'what is cloud computing', 'why does code crash', 'how do i learn python', 'what is nlp', 'how do i pick a font', 'why do we sleep',
]
knowledge_responses = [
    'ai is tech that mimics human tasks', 'try isolating the issue and testing small parts', 'light scatters in the atmosphere causing blue',
    'train with many examples and check validation', 'a neural network is layered math functions', 'start with html and css',
    'cloud uses remote servers to run services', 'check error logs and reproduce the bug', 'practice and build small projects', 'nlp helps machines understand language', 'pick readable fonts', 'sleep restores the brain',
]

# Create pairs
pairs_greetings = []
for i in range(160):
    inp = greeting_inputs[i % len(greeting_inputs)]
    out = greeting_responses[i % len(greeting_responses)]
    pairs_greetings.append(f"### INPUT:\n{inp}\n### OUTPUT:\n{out}")

pairs_everyday = []
for i in range(120):
    inp = everyday_inputs[i % len(everyday_inputs)]
    out = everyday_responses[i % len(everyday_responses)]
    pairs_everyday.append(f"### INPUT:\n{inp}\n### OUTPUT:\n{out}")

pairs_knowledge = []
for i in range(100):
    inp = knowledge_inputs[i % len(knowledge_inputs)]
    out = knowledge_responses[i % len(knowledge_responses)]
    pairs_knowledge.append(f"### INPUT:\n{inp}\n### OUTPUT:\n{out}")

# Write files
write_file(root / 'extended_greetings_160.txt', pairs_greetings)
write_file(root / 'extended_everyday_120.txt', pairs_everyday)
write_file(root / 'extended_knowledge_100.txt', pairs_knowledge)
print('Total pairs:', len(pairs_greetings)+len(pairs_everyday)+len(pairs_knowledge))
