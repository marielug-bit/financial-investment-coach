"""Document loading, parsing, and chunking for financial reports."""

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader, UnstructuredExcelLoader


CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))


def load_document(file_path: str | Path) -> List[Document]:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        loader = PDFPlumberLoader(str(path))
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        loader = UnstructuredExcelLoader(str(path))
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return loader.load()


def chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest(file_path: str | Path) -> List[Document]:
    docs = load_document(file_path)
    return chunk_documents(docs)
