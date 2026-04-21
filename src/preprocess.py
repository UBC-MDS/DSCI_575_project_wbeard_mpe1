import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# required to run on posit connect cloud
nltk.download('stopwords')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

def preprocess(text):
    """Preprocess search text: lowercase, alpha-numeric only, word-tokenize, remove stopwords"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = word_tokenize(text)
    return [t for t in tokens if t not in stop_words and len(t) > 2]

def preprocess_without_using_stopwords(text):
    """Preprocess search text: lowercase, alpha-numeric only, word-tokenize"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = word_tokenize(text)
    return tokens
