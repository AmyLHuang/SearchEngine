from inverted_index import InvertedIndex
from search import Search
import os


def create_inverted_index(replace=False):
    indexExists = os.path.exists("../index")
    if not indexExists or replace:
        ii = InvertedIndex(block_size=10)
        ii.build_index(parent_dir="../documents/analyst", debug=True)
    else:
        print("Index already exists.")


if __name__ == "__main__":
    create_inverted_index()

    queries = ["cristina lopes", "machine learning", "ACM" ,"master of software engineering"]
    s = Search()
    
    for query in queries:
        print(f"Running Query - {query}")
        s.search(query)
        s.printResults()
    