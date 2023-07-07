
class Posting:
    def __init__(self, doc_id, count, important):
        self.doc_id = doc_id
        self.count = count
        self.important = important

    def __lt__(self, other):
        return self.doc_id < other.doc_id
