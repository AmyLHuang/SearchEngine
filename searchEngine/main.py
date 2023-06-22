from inverted_index import InvertedIndex
import os.path


def initialize_index():
    indexExists = os.path.exists("index")
    if indexExists == False:
        ii = InvertedIndex("../documents/analyst/ANALYST")
        ii.build_index()


if __name__ == "__main__":
    # if inverted index does not exist, build it
    initialize_index()

    # queries
