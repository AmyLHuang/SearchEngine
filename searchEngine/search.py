from nltk.stem import PorterStemmer
import math
from inverted_index import Posting

class Search:
    def __init__(self):
        self.sorted_results = set()
        
        with open("../index/inverted_index_variables.txt") as f:
            self.docid_url = eval(f.readline())
            self.term_pos = eval(f.readline())
            self.total_docs = int(f.readline())
        
    def search(self, query):
        results = set()
        scores = [[0]*len(query.split()) for _ in range(self.total_docs)]
        weights = []
        inverted_index_file = open("../index/inverted_index.txt")

        for i, term in enumerate(query.lower().split()):
            doc_ids = set()
            if query.count(term) == 0:
                weights.append(1)
            else:
                weights.append(1 + math.log(query.count(term), 10))

            stemmed_term = PorterStemmer().stem(term).strip(".,;:?-!()/\"[]{}\n ")
            if stemmed_term not in self.term_pos:
                continue

            # Retrieve term and its posting list from index file
            inverted_index_file.seek(self.term_pos[stemmed_term])

            line = inverted_index_file.readline()
            if line.split(":")[0][2:-1] != term:
                line = inverted_index_file.readline()
            
            d = eval(line)
            print(d)
            df = len(d.values())
            idf = math.log(self.total_docs/df, 10)

            for postings in d.values():
                for posting in postings:
                    print(posting)
                    # Calculate tf_idf for each doc: tf x idf
                    tf_idf = (1+math.log(posting.term_freq, 10)) * idf

                    #set the score of the doc for this term
                    scores[posting.doc_id - 1][i] = tf_idf

                    #if the term is important in this doc, inc its score
                    if posting.important == True:
                        scores[posting.doc_id - 1][i] *= 2
                    
                    doc_ids.add(posting.doc_id)
            
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

        # for the docids, sort by cosine score
        self.sorted_results = sorted(results, key=lambda x: scores[x-1], reverse=True)


    def printResults(self):
        for r in self.sorted_results:
            print(self.docid_url[r])

    def getResults(self):
        return self.sorted_results

    def getDocidUrl(self):
        return self.docid_url
