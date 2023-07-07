from inverted_index import InvertedIndex
import os


def initialize_index(flag=False):
    indexExists = os.path.exists("../index")
    if not indexExists or flag:
        print("Create index")
        ii = InvertedIndex("../documents/test")
        ii.init_index_dir()
        ii.build_index()
    else:
        print("Index already exists.")


if __name__ == "__main__":
    # if inverted index does not exist, build it
    initialize_index()

    # queries
