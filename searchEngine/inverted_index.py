import os
import json
import shutil
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict
import string


class InvertedIndex:
    def __init__(self, docs_dir, block_size=1000):
        self.docs_dir = docs_dir      # directory where documents are stored
        self.block_size = block_size  # block size to write to disk
        self.doc_id = 0               # will be used to give unique id to each document
        self.doc_url = dict()         # map doc_id to the url
        self.inverted_index = defaultdict(list)  # map term to its posting
        self.term_pos = dict()        # map term to position in disk

    def init_index_dir(self) -> None:
        # clear/create directory to store partial + combined inverted index
        shutil.rmtree("../index", ignore_errors=True)
        if not os.path.exists("../index"):
            os.makedirs("../index")

    def build_index(self) -> None:
        print(f"Building Index...")
        total_docs = 0
        for root, dirs, files in os.walk(self.docs_dir):
            print(f"current root: {root}")
            for file in files:
                total_docs += 1
                if file.endswith(".json"):
                    # Read the JSON file
                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)

                    # Associate url with corresponding doc_id
                    self.doc_id += 1
                    self.doc_url[self.doc_id] = data['url']

                    # Analyze the file's data
                    self.analyze_file(data)

                # If block size is reached, write inverted index to disk
                if self.doc_id % self.block_size == 0:
                    filepath = f"../index/index_block_{self.doc_id//self.block_size}.txt"
                    self.store_in_disk(filepath, self.inverted_index)
                    self.inverted_index.clear()

        # Write remaining inverted index to disk
        if len(self.inverted_index) > 0:
            filepath = f"../index/index_block_{self.doc_id//self.block_size+1}.txt"
            self.store_in_disk(filepath, self.inverted_index)
            self.inverted_index.clear()

        # Perform multi-way merge of index blocks
        self.merge_index_blocks()
        print("Finished Building Index.")

        # Store important attributes in a file
        with open(f"../index/inverted_index_variables.txt", 'w') as f:
            f.write(str(self.doc_url) + "\n")
            f.write(str(self.term_pos) + "\n")
            f.write(str(total_docs) + "\n")
    
    def analyze_file(self, data) -> None:
        # Extract the content
        html_raw_content = data['content']
        soup = BeautifulSoup(html_raw_content, 'html.parser')

        # Find the "important" words in document
        important_words = set()
        important_elements = soup.find_all(
            ['h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'])
        for element in important_elements:
            for word in element.text.split():
                stemmed_word = self.stem(word)
                if len(stemmed_word) >= 2:
                    important_words.add(stemmed_word)

        # Find (and keep count) of the words in document
        word_count = defaultdict(int)
        for str in soup.stripped_strings:
            for word in str.split():
                stemmed_word = self.stem(word)
                if len(stemmed_word) >= 2:
                    new_stemmed_word = stemmed_word.replace('"', "'")
                    word_count[new_stemmed_word] += 1

        # Update the inverted index by adding postings
        for word in word_count.keys():
            posting = {
                'doc_id': self.doc_id,
                'tf': word_count[word],
                'important': word in important_words,
            }
            self.inverted_index[word].append(posting)

    def merge_index_blocks(self) -> None:
        # Open all partial index files and maintain a read buffer for each one
        read_buffer = []
        for file in os.listdir("../index"):
            if file.startswith("index_block_"):
                read_buffer.append(open(f"../index/{file}", 'r'))

        # Maintain a write buffer for the output files
        write_buffer = defaultdict(list)

        # Posting buffer stores the current postings we're reading for each file
        postings_buffer = []
        for f in read_buffer:
            line = f.readline().rstrip('\n')
            postings_buffer.append(eval(line))

        # Variable to keep track of where the term will be located on file
        position = 0

        while len(read_buffer) > 0:
            # Get smallest term from the posting buffer
            term_list = [list(posting.keys())[0]
                         for posting in postings_buffer]
            smallest_term = min(term_list)

            # Values will be used to store all postings for the smallest term
            values = []

            # If term in multiple files, combine postings; append term + posting to file
            for i, posting in enumerate(postings_buffer):
                k, v = list(posting.items())[0]
                if k == smallest_term:
                    values.extend(v)
                    line = read_buffer[i].readline().rstrip('\n')
                    if line == "":
                        del read_buffer[i]
                        del postings_buffer[i]
                    else:
                        postings_buffer[i] = eval(line)

            # sort the postings by doc_id and then put in the write_buffer
            values = sorted(values, key=lambda x: x["doc_id"])
            write_buffer[smallest_term] = values

            # Keep track of where the term is in the file
            self.term_pos[smallest_term] = position
            position += 8 + len(smallest_term) + len(str(values))

            # Write output buffer to disk if it reaches block size
            if len(write_buffer) >= self.block_size:
                filepath = "../index/inverted_index.txt"
                self.store_in_disk(filepath, write_buffer)
                write_buffer.clear()

        # Write any remaining output buffer to disk
        if len(write_buffer) > 0:
            filepath = "../index/inverted_index.txt"
            self.store_in_disk(filepath, write_buffer)
            write_buffer.clear()

    @staticmethod
    def store_in_disk(filepath, info) -> None:
        # Sort posting/info by doc_id and add to file
        with open(filepath, 'a') as f:
            for k, v in sorted(info.items()):
                f.write("{" + f'"{k}": {v}' + "}\n")

    @staticmethod
    def stem(word) -> str:
        strip_word = word.strip(string.punctuation +
                                string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip(
            string.punctuation + string.whitespace + "‘’“”")

        return strip_stem_word
