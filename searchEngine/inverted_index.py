import os, json, shutil, string, re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict

class InvertedIndex:
    """
    An Inverted Index maps terms to their postings, enabling efficient full-text search.

    Attributes:
        - block_size (int): The number of documents to process before writing to disk.
        - index (defaultdict): A dictionary mapping terms to lists of Posting objects.
        - term_positions (dict): A mapping of terms to their byte positions in the final index file.
        - map_doc_id_to_url (dict): A mapping of document IDs to their corresponding URLs.

    Methods:
        - build_index(parent_dir, debug=False): Constructs the inverted index from documents.
    """
    def __init__(self, block_size=1000):
        self.block_size = block_size
        self.index = defaultdict(list)
        self.term_positions = dict()
        self.map_doc_id_to_url = dict()

        # Initialize or reset the index directory
        shutil.rmtree("../index", ignore_errors=True)
        os.makedirs("../index", exist_ok=True)

    def build_index(self, parent_dir, debug=False) -> None:
        """Builds the inverted index from documents."""
        total_docs, doc_id = 0, 0
        for root, _, files in os.walk(parent_dir):
            if debug:
                print(f"Processing {root}")
            for file in files:
                if not file.endswith(".json"):
                    continue

                # update counters and open/load the file
                total_docs += 1
                doc_id += 1
                with open(os.path.join(root, file), 'r') as f:
                    jsonData = json.load(f)
                    
                # map doc id to url and analyze the file
                self.map_doc_id_to_url[doc_id] = jsonData["url"]
                self._analyze_file(jsonData["content"], doc_id)
                
                # If block size is reached, write inverted index to disk
                if doc_id % self.block_size == 0:
                    self._store_in_disk(f"../index/index_block_{doc_id//self.block_size}.txt")
                    self.index.clear()
                
        # Write remaining inverted index to disk
        if len(self.index) > 0:
            self._store_in_disk(f"../index/index_block_{doc_id//self.block_size+1}.txt")
            self.index.clear()

        # Perform multi-way merge of index blocks
        self._merge_index_blocks()
        self._store_metadata(total_docs)

        if debug:
            print("Finished Building Index.")
    
    def _analyze_file(self, file_content, doc_id) -> None:
        soup = BeautifulSoup(file_content, 'html.parser')

        important_words = set()
        word_count = defaultdict(int)

        # Find and process all text elements in the document
        for element in soup.find_all(text=True):
            words = re.split(r'[ (){};,\s-]+', element.strip())  # Tokenize words
            
            for word in words:
                stemmed_word = self._stem(word).replace('"', "'")
                word_count[stemmed_word] += 1
                
                # Mark as important if it's inside important tags
                if element.parent.name in {'h1', 'h2', 'h3', 'b', 'strong', 'i', 'em', 'mark', 'title', 'a'}:
                    important_words.add(stemmed_word)

        for word, freq in word_count.items():
            posting = {
                "doc_id": doc_id,
                "term_freq": freq,
                "important": word in important_words
            }
            self.index[word].append(posting)

    def _merge_index_blocks(self) -> None:
        # Open all partial index files and maintain a read buffer for each one
        read_buffer = []
        for file in os.listdir("../index"):
            if file.startswith("index_block_"):
                read_buffer.append(open(f"../index/{file}", 'r'))

        # Posting buffer stores the postings for each file in the read buffer
        postings_buffer = []
        for f in read_buffer:
            line = f.readline().rstrip('\n')
            entry = json.loads(line)
            postings_buffer.append(entry)
        
        while len(read_buffer) > 0:
            # Get smallest term from the posting buffer
            term_list = [next(iter(posting)) for posting in postings_buffer]
            smallest_term = min(term_list)

            # Add the posting(s) of the smallest term into values
            values = []
            for i, posting in enumerate(postings_buffer):
                k, v = next(iter(posting.items()))
                if k == smallest_term:
                    values.extend(v)
                    line = read_buffer[i].readline().rstrip('\n')
                    if line == "":
                        del read_buffer[i]
                        del postings_buffer[i]
                    else:
                        entry = json.loads(line)
                        postings_buffer[i] = entry

            # sort the postings in values by doc_id and then put into index
            values = sorted(values, key=lambda x: x["doc_id"])
            self.index[smallest_term] = values

            # Write output buffer to disk if it reaches block size
            if len(self.index) >= self.block_size:
                self._store_in_disk("../index/inverted_index.txt", True)
                self.index.clear()

        # Write any remaining output buffer to disk
        if len(self.index) > 0:
            self._store_in_disk("../index/inverted_index.txt", True)
            self.index.clear()

    def _store_in_disk(self, filepath, track_position=False) -> None:
        '''Store the index into filepath.'''
        with open(filepath, 'a') as f:
            for key, value in sorted(self.index.items()):
                if track_position:
                    pos = f.tell()
                    self.term_positions[key] = pos
                f.write(json.dumps({key: value}) + "\n")

    def _store_metadata(self, total_docs):
        '''Store important attributes in a metadata.json file'''
        with open(f"../index/metadata.json", 'w') as json_file:
            json.dump({
                "doc_id_to_url": self.map_doc_id_to_url,
                "term_positions": self.term_positions,
                "total_docs": total_docs
            }, json_file, indent=4)
    
    @staticmethod
    def _stem(word) -> str:
        '''Stems a given word by removing punctuation, whitespace, and quote characters, and then applying the Porter Stemming algorithm.'''
        strip_word = word.strip(string.punctuation + string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip( string.punctuation + string.whitespace + "‘’“”")
        return strip_stem_word.lstrip("0")
