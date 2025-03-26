from dataclasses import dataclass

@dataclass
class Posting:
    """
    Represents an occurrence of a term in a document.

    Attributes:
        doc_id (int): The ID of the document where the term appears.
        term_freq (int): The frequency of the term in the document.
        important (bool): Indicates if the term is considered important (e.g., based on weight or relevance).
    """
    doc_id: int
    term_freq: int
    important: bool
