
class Search:
    def __init__(self, query):
        self.query = query
        self.inverted_index_file = open("../index/inverted_index.txt")

        with open("../index/inverted_index_variables.txt") as f:
            self.doc_url = eval(f.readline())
            self.term_pos = eval(f.readline())

        print(self.doc_url)
        print(self.term_pos)
        print(len(self.doc_url))
