import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.ingestion import chunk_documents
from langchain_core.documents import Document


def test_chunk_documents_splits_long_text():
    long_text = "Revenue increased significantly. " * 100
    docs = [Document(page_content=long_text, metadata={"source": "test.pdf"})]
    chunks = chunk_documents(docs)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 1200


def test_chunk_documents_preserves_metadata():
    docs = [Document(page_content="Net income was $1.2B.", metadata={"source": "annual_report.pdf", "page": 5})]
    chunks = chunk_documents(docs)
    assert all(c.metadata["source"] == "annual_report.pdf" for c in chunks)


def test_ingest_unsupported_format():
    from src.ingestion import ingest
    with pytest.raises(ValueError, match="Unsupported file type"):
        ingest("report.docx")
