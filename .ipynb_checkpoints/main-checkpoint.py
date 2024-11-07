# .\.venv\Scripts\activate for activating the venv

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

text = "NLTK is a powerful library for natural language proccessing"

pos_tags = pos_tag(words)

print("Original text:")
print(text)

print("\nPos Tagging Result:")
for word, pos_tag in pos_tags:
    print(f"{word}: {pos_tag}")
