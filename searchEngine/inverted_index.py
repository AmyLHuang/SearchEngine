import os
import json
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string as string


class InvertedIndex:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir

    def build_index(self):
        print(f"Building Index...")
        for root, dirs, files in os.walk(self.docs_dir):
            print(f"current root: {root}")
            for file in files:
                if file.endswith(".json"):
                    self.analyze_file(root, file)
                break
        print("Finished Building Index.")

    def analyze_file(self, root, file):
        # Read the JSON file
        with open(os.path.join(root, file), 'r') as f:
            data = json.load(f)

        # Extract the content
        html_raw_content = data['content']
        soup = BeautifulSoup(html_raw_content, 'html.parser')
        ps = PorterStemmer()

        # Find the "important" words
        important_words = set()
        important_words_found = soup.find_all(
            ['h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'])
        for words in important_words_found:
            words_list = word_tokenize(words.text)
            for word in words_list:
                stemmed_word = ps.stem(word.strip(string.punctuation))
                if len(stemmed_word) >= 2:
                    important_words.add(stemmed_word)
        print(important_words)

        # Find all the words in document
        for str in soup.stripped_strings:
            words = word_tokenize(str)
            for word in words:
                # print(ps.stem(word).strip(string.punctuation+string.whitespace))
                pass
            # stemmed_sentence = reduce(
            #     lambda x, y: x + " " + ps.stem(y), words, "")
            # print(stemmed_sentence)
            # # print(repr(string))
