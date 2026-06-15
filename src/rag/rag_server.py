"""MCP server exposing RAG document retrieval tools."""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
from src.rag.retrieval import retrieve, add_documents
from src.rag.ingestion import ingest

mcp = FastMCP("rag-agent")


@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> str:
    """Search indexed financial reports for information. Always call this before answering."""
    docs = retrieve(query, k=top_k)
    if not docs:
        return "No relevant documents found for this query."
    return "\n\n---\n\n".join(
        f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    )


@mcp.tool()
def search_multiple_queries(queries: list[str]) -> str:
    """Search with several queries in parallel to answer complex multi-part questions."""
    all_docs = []
    for q in queries:
        all_docs.extend(retrieve(q, k=3))
    seen: set[str] = set()
    unique = [d for d in all_docs if d.page_content not in seen and not seen.add(d.page_content)]  # type: ignore[func-returns-value]
    if not unique:
        return "No relevant documents found."
    return "\n\n---\n\n".join(
        f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in unique
    )


@mcp.tool()
def index_document(file_path: str) -> str:
    """Index a financial document (PDF or Excel) into the vector store."""
    chunks = ingest(file_path)
    add_documents(chunks)
    return f"Successfully indexed {len(chunks)} chunks from '{os.path.basename(file_path)}'"


if __name__ == "__main__":
    mcp.run()
