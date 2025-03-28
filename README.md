# Project Title: SearchEngine

## Team Members & Contributions

- Amy Huang (Inverted Index + Search Function + App)
- Wafa Afridi (App)
- Vinh Nguyen (Inverted Index, analyzing file portion)

## Dependencies (pip install)

- Flask
- NLTK
- BeautifulSoup

## Simple/Example Usage

```
git clone https://github.com/AmyLHuang/SearchEngine.git
cd SearchEngine/searchEngine
python3 main.py
python3 app.py
```

## Detailed Usage

To create the inverted index, create an instance of InvertedIndex and call the build_index method. To start the search interface, run app.py.

**Important**: You have to create the inverted index before the search engine can run and make sure you are in the searchEngine directory when making the inverted index and running the search engine!

### Creating the Inverted Index

Before running the search engine, you will need to build the inverted index which maps terms to their postings, enabling efficient full-text search.

When building the inverted index, it will make a new directory called "index" in the parent of your current file location. When the process is finished, the index folder will contain index_blocks, the inverted index, and the metadata. The index blocks make the building process more efficient storage wise since it makes sure the whole index will not be cached. Instead, when the index reaches a certain block size, which you can specify, it will store the data in a txt file and clear itself. When building the final index, it only reads one line at a time per file, and writing to the final index immediately.

#### To construct the inverted index from a collection of documents, specify the directory containing the text files and call:

```
index.build_index("path/to/documents")
```

Replace "path/to/documents" with the actual path to your document collection.

#### Optional Debug Mode

If you want to enable debugging to see detailed processing steps, use:

```
index.build_index("path/to/documents", debug=True)
```

#### For example:

```
from inverted_index import InvertedIndex
ii = InvertedIndex(block_size=10) ii.build_index(parent_dir="../documents/analyst", debug=True)
```

### Running the Search Engine

1. Make sure you are in the searchEngine path
2. Run `python3 app.py`
3. Once you've started the search interface, you can enter search queries in the search box and click "Search". The search engine will return a list of documents that match your query, ranked by relevance.
