import os, json, shutil, string, re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict
from posting import Posting

class InvertedIndex:
    def __init__(self, block_size=1000):
        self.block_size = block_size
        self.inverted_index = defaultdict(list)
        self.total_docs = 0
        self.term_pos = dict()
        self.map_doc_id_to_url = dict()

    def init_index_dir(self) -> None:
        """Initialize or reset the index directory."""
        shutil.rmtree("../index", ignore_errors=True)
        os.makedirs("../index", exist_ok=True)

    def build_index(self, parent_directory, debug=False) -> None:
        """Builds the inverted index from documents."""
        doc_id = 0
        for root, _, files in os.walk(parent_directory):
            if debug:
                print(f"Processing {root}")
            for file in files:
                if not file.endswith(".json"):
                    continue
                self.total_docs += 1
                with open(os.path.join(root, file), 'r') as f:
                    jsonData = json.load(f)
                    
                # map doc id to url and analyze the file
                doc_id += 1
                self.map_doc_id_to_url[doc_id] = jsonData["url"]
                self._analyze_file(jsonData["content"], doc_id)
                
                # If block size is reached, write inverted index to disk
                if doc_id % self.block_size == 0:
                    filepath = f"../index/index_block_{doc_id//self.block_size}.txt"
                    self._store_in_disk(filepath, self.inverted_index)
                    self.inverted_index.clear()
                
        # Write remaining inverted index to disk
        if len(self.inverted_index) > 0:
            filepath = f"../index/index_block_{doc_id//self.block_size+1}.txt"
            self._store_in_disk(filepath, self.inverted_index)
            self.inverted_index.clear()

        # Perform multi-way merge of index blocks
        self._merge_index_blocks()
        self._store_metadata()

        if debug:
            print("Finished Building Index.")
    
    def _analyze_file(self, raw_content, doc_id) -> None:
        soup = BeautifulSoup(raw_content, 'html.parser')

        # Find the "important" words in document
        important_words = set()
        important_elements = soup.find_all(
            ['h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'])
        for element in important_elements:
            for word in re.split(r'[ (){};,\s-]+', element.text):
                stemmed_word = self.stem(word)
                if len(stemmed_word) >= 2:
                    important_words.add(stemmed_word)

        # Find (and keep count) of the words in document
        word_count = defaultdict(int)
        for str in soup.stripped_strings:
            for word in re.split(r'[ (){};,\s-]+', str):
                stemmed_word = self.stem(word)
                if len(stemmed_word) >= 2:
                    new_stemmed_word = stemmed_word.replace('"', "'")
                    word_count[new_stemmed_word] += 1

        # Update the inverted index by adding postings
        for word in word_count.keys():
            post = Posting(doc_id=doc_id, term_freq=word_count[word], important=word in important_words)
            self.inverted_index[word].append(post)

    def _merge_index_blocks(self) -> None:
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
            term_list = [list(posting.keys())[0] for posting in postings_buffer]
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
            values = sorted(values, key=lambda x: x.doc_id)
            write_buffer[smallest_term] = values

            # Keep track of where the term is in the file
            self.term_pos[smallest_term] = position
            position += 8 + len(smallest_term) + len(str(values))

            # Write output buffer to disk if it reaches block size
            if len(write_buffer) >= self.block_size:
                filepath = "../index/inverted_index.txt"
                self._store_in_disk(filepath, write_buffer)
                write_buffer.clear()

        # Write any remaining output buffer to disk
        if len(write_buffer) > 0:
            filepath = "../index/inverted_index.txt"
            self._store_in_disk(filepath, write_buffer)
            write_buffer.clear()

    def _store_in_disk(self, filepath, content) -> None:
        # Sort posting/info by doc_id and add to file
        with open(filepath, 'a') as f:
            for k, v in sorted(content.items()):
                f.write("{" + f'"{k}": {v}' + "}\n")

    def _store_metadata(self):
        '''Store important attributes in a metadata.json file'''
        with open(f"../index/metadata.json", 'w') as json_file:
            json.dump({
                "doc_id_to_url": self.map_doc_id_to_url,
                "term_pos": self.term_pos,
                "total_docs": self.total_docs
            }, json_file, indent=4)
    
    @staticmethod
    def stem(word) -> str:
        strip_word = word.strip(string.punctuation + string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip( string.punctuation + string.whitespace + "‘’“”")
        return strip_stem_word