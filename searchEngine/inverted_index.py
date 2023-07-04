import os
import json
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from posting import Posting
from collections import defaultdict
import string as string


class InvertedIndex:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.doc_id = 0
        self.invertedIndex = defaultdict(list)

    def build_index(self):
        print(f"Building Index...")
        for root, dirs, files in os.walk(self.docs_dir):
            print(f"current root: {root}")
            for file in files:
                if file.endswith(".json"):
                    self.doc_id += 1

                    # Read the JSON file
                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)

                    # Analyze the file's data
                    self.analyze_file(data)
        
        print(self.invertedIndex.keys())


        print("Finished Building Index.")

    def analyze_file(self, data):
        # Extract the content
        html_raw_content = data['content']
        soup = BeautifulSoup(html_raw_content, 'html.parser')

        # Find the "important" words in document
        important_words = set()
        important_words_found = soup.find_all(
            ['h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'])
        for words in important_words_found:
            for word in words.text.split():
                stemmed_word = InvertedIndex.stem(word)
                if len(stemmed_word) >= 2:
                    important_words.add(stemmed_word)

        # Find all the words in document
        words_in_document = []
        for str in soup.stripped_strings:
            for word in str.split():
                stemmed_word = InvertedIndex.stem(word)
                if len(stemmed_word) >= 2:
                    words_in_document.append(stemmed_word)

        # Update the inverted index by adding postings
        for word in set(words_in_document):
            stemmed_word = InvertedIndex.stem(word)
            posting = Posting(self.doc_id, words_in_document.count(
                stemmed_word), stemmed_word in important_words)
            self.invertedIndex[stemmed_word].append(posting)

    @staticmethod
    def stem(word):
        strip_word = word.strip(string.punctuation +
                                string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip(
            string.punctuation + string.whitespace + "‘’“”")

        return strip_stem_word
