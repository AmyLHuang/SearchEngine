from inverted_index import InvertedIndex
from search import Search
import os, time, math


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
    create_inverted_index()

    queries = ["cristina lopes", "machine learning", "ACM"]
    # start_time = time.time()
    
    for query in queries:
        print(f"Running Query - {query}")
        search_query(query)

    # end_time = time.time()
    # print(f"Finished. Total Querying Time is {end_time - start_time} seconds.")
