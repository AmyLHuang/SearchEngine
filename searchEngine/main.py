from inverted_index import InvertedIndex
from search import Search
import os


def search_query(query):
    s = Search(query)


def create_inverted_index(flag=False):
    indexExists = os.path.exists("../index")
    if not indexExists or flag:
        ii = InvertedIndex("../documents/test", 10)
        ii.init_index_dir()
        ii.build_index()
    else:
        print("Index already exists.")


if __name__ == "__main__":
    # if inverted index does not exist or flag is True, build ii
    create_inverted_index()

    # queries
    queries = ["cristina lopes", "machine learning", "ACM"]
    for query in queries:
        search_query(query)
