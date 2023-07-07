import os
import json
import shutil
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from posting import Posting
from collections import defaultdict
import string


class InvertedIndex:
    def __init__(self, docs_dir, block_size=10):
        self.docs_dir = docs_dir      # directory where documents are stored
        self.block_size = block_size  # block size to write to disk
        self.doc_id = 0               # will be used to give unique id to each document
        self.doc_url = dict()         # map doc_id to the url
        self.inverted_index = defaultdict(list)  # map term to its posting

    def init_index_dir(self):
        # clear/create directory to store partial + combined inverted index
        shutil.rmtree("../index", ignore_errors=True)
        os.makedirs("../index")

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

                    # Associate url with corresponding doc_id
                    self.doc_url[self.doc_id] = data['url']

                    # Analyze the file's data
                    self.analyze_file(data)

                # If block size is reached, write inverted index to disk
                if self.doc_id % self.block_size == 0:
                    filepath = f"../index/index_block_{self.doc_id//self.block_size}.txt"
                    self.store_in_disk(filepath, self.inverted_index)
                    self.inverted_index.clear()

        print("Finished Building Index.")
        print("last index length = ", len(self.inverted_index))
        print("last doc id = ", self.doc_id)

    def analyze_file(self, data):
        # Extract the content
        html_raw_content = data['content']
        soup = BeautifulSoup(html_raw_content, 'html.parser')

        # Find the "important" words in document
        important_words = set()
        important_elements = soup.find_all(
            ['h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'])
        for element in important_elements:
            for word in element.text.split():
                stemmed_word = InvertedIndex.stem(word)
                if len(stemmed_word) >= 2:
                    important_words.add(stemmed_word)

        # Find (and keep count) of the words in document
        word_count = defaultdict(int)
        for str in soup.stripped_strings:
            for word in str.split():
                stemmed_word = InvertedIndex.stem(word)
                if len(stemmed_word) >= 2:
                    word_count[stemmed_word] += 1

        # Update the inverted index by adding postings
        for word in word_count.keys():
            posting = Posting(
                self.doc_id, word_count[word], word in important_words)
            self.inverted_index[word].append(posting)

    @staticmethod
    def store_in_disk(filepath, info):
        # print("inside write_to_disk function, info: ")
        # i = 0
        # for k, v in info.items():
        #     i += 1
        #     print(k, v)
        #     if (i == 20):
        #         break
        with open(filepath, 'a') as f:
            # sort the dict by terms and write to file
            for k, v in sorted(info.items()):
                print(k, sorted(v))

    @staticmethod
    def stem(word):
        strip_word = word.strip(string.punctuation +
                                string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip(
            string.punctuation + string.whitespace + "‘’“”")

        return strip_stem_word
