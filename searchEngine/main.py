from inverted_index import InvertedIndex
from search import Search
import os, time


def create_inverted_index(flag=False):
    indexExists = os.path.exists("../index")
    if not indexExists or flag:
        ii = InvertedIndex("../documents/test", 10)
        ii.init_index_dir()
        ii.build_index()
    else:
        print("Index already exists.")


if __name__ == "__main__":
    create_inverted_index()

    queries = ["cristina lopes", "machine learning", "ACM"]
    s = Search()
    
    for query in queries:
        print(f"Running Query - {query}")
        s.search(query)
        s.printResults()
    