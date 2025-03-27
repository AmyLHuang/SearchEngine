from nltk.stem import PorterStemmer
import math, json, string, re

class Search:
    """
    A Search class that performs full-text search using an inverted index.

    Attributes:
        - sorted_results (list): Stores ranked search results.
        - doc_id_to_url (dict): Maps document IDs to their URLs.
        - term_positions (dict): Byte positions of terms in the index file.
        - total_docs (int): Total number of documents indexed.
        
    Methods:
        - search(query): Processes a query, retrieves relevant documents, and ranks them.
        - print_results(): Prints the URLs of ranked documents.
        - get_results(): Returns the ranked document IDs.
        - get_docid_url(): Returns the document ID-to-URL mapping.
    """
    def __init__(self):
        self.sorted_results = set()
        with open("../index/metadata.json") as f:
            jsonData = json.load(f)
        self.doc_id_to_url = jsonData["doc_id_to_url"]
        self.term_positions = jsonData["term_positions"]
        self.total_docs = jsonData["total_docs"]
        
    def search(self, query):
        """Search for documents matching the given query and rank results."""
        results = set()
        query_words = re.split(r'[ (){};,\s-]+', query.lower())
        scores = [[0]*len(query_words) for _ in range(self.total_docs)]
        weights = [1]*len(query_words)
        inverted_index_file = open("../index/inverted_index.txt")

        for i, term in enumerate(query_words):
            stemmed_term = self._stem(term)
            if stemmed_term not in self.term_positions:
                continue

            if query.count(term) > 0:
                weights[i] += math.log(query.count(term), 10)

            # Retrieve postings list from the index file
            inverted_index_file.seek(self.term_positions[stemmed_term])
            line = inverted_index_file.readline()
            entry = json.loads(line)
            idf = math.log(self.total_docs/len(entry.values()), 10)
            
            doc_ids = set()
            for postings in entry.values():
                for posting in postings:
                    tf_idf = (1+math.log(posting["term_freq"], 10)) * idf
                    scores[posting["doc_id"] - 1][i] = tf_idf

                    #if the term is important in this doc, inc its score
                    if posting["important"] == True:
                        scores[posting["doc_id"] - 1][i] *= 2
                    
                    doc_ids.add(posting["doc_id"])
            
            # If result is not empty, take the intersection between results and doc_ids to find set of docs that contain all the terms in the query
            if results:
                results = results.intersection(doc_ids)
            else:
                results = doc_ids
        
        inverted_index_file.close()
        
        #length normalization on all the scores
        for i, score in enumerate(scores):
            length = math.sqrt(sum([s ** 2 for s in score]))
            if length != 0:
                for j in range(len(score)):
                    scores[i][j] /= length

        # Length normalization on weights:
        length = math.sqrt(sum(weights))
        if length != 0:
            weights = [w/length for w in weights]

        # get cosine score for document query pair
        for doc, score in enumerate(scores):
            temp = 0
            for s, w in zip(score, weights):
                temp += (w * s)
            scores[doc] = temp

        # for the doc_ids, sort by cosine score
        self.sorted_results = sorted(results, key=lambda x: scores[x-1], reverse=True)

    def printResults(self):
        """Prints the URLs of ranked search results."""
        for r in self.sorted_results:
            print(self.doc_id_to_url[str(r)])

    def getResults(self):
        """Returns the ranked document IDs."""
        return self.sorted_results

    def getDocIdToUrl(self):
        """Returns the document ID-to-URL mapping."""
        return self.doc_id_to_url

    @staticmethod
    def _stem(word) -> str:
        strip_word = word.strip(string.punctuation + string.whitespace + "‘’“”")
        stem_word = PorterStemmer().stem(strip_word)
        strip_stem_word = stem_word.strip( string.punctuation + string.whitespace + "‘’“”")
        return strip_stem_word
