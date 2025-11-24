import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt')

FILLER_WORDS = ["um", "uh", "like", "you know", "so", "actually", "basically",
                "right", "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah"]

def clean_text(text):
    return text.lower().strip()

def get_word_count(text):
    words = word_tokenize(text)
    return len(words), words

def get_sentence_count(text):
    return len(sent_tokenize(text))

def count_filler_words(words):
    count = sum(1 for w in words if w in FILLER_WORDS)
    return count
