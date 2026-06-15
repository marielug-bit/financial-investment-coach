"""Vector store management and semantic retrieval."""

import os
from typing import List

import chromadb
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma


PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/vector_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "financial_reports")
TOP_K = int(os.getenv("TOP_K_RESULTS", 5))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def _embeddings():
    return SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_embeddings(),
        persist_directory=PERSIST_DIR,
    )


def add_documents(documents: List[Document]) -> None:
    store = get_vector_store()
    store.add_documents(documents)


def retrieve(query: str, k: int = TOP_K) -> List[Document]:
    store = get_vector_store()
    return store.similarity_search(query, k=k)
