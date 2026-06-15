"""RAG agent for financial report analysis using the Anthropic SDK."""

import os
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

from .ingestion import ingest
from .retrieval import add_documents, retrieve

load_dotenv()

MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-6")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))

SYSTEM_PROMPT = """You are a financial analyst agent.
You have access to tools to search financial reports.
Always use search_documents before answering.
Cite sources and page numbers in your answers.
If information is not found, say so clearly."""

TOOLS = [
    {
        "name": "search_documents",
        "description": "Search indexed financial reports for relevant information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Number of results"}
            },
            "required": ["query"]
        }
    },
{
        "name": "search_multiple_queries",
        "description": "Search with multiple queries for complex questions",
        "input_schema": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of search queries"
                }
            },
            "required": ["queries"]
        }
    }
]


class FinancialAnalyzerAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def index_report(self, file_path: str | Path) -> int:
        chunks = ingest(file_path)
        add_documents(chunks)
        return len(chunks)
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
         if tool_name == "search_documents":
            query = tool_input["query"]
            k     = tool_input.get("top_k", 5)
            docs  = retrieve(query, k=k)
            return "\n\n---\n\n".join(
                f"[Source: {d.metadata.get('source','?')}, page {d.metadata.get('page','?')}]\n{d.page_content}"
                for d in docs
            )
         elif tool_name == "search_multiple_queries":
            all_results = []
            for query in tool_input["queries"]:
                docs = retrieve(query, k=3)
                all_results.extend(docs)
            seen = set()
            unique = [d for d in all_results if d.page_content not in seen and not seen.add(d.page_content)]
            return "\n\n---\n\n".join( f"[{d.metadata.get('source', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}" for d in unique)
         return "Tool not found"

    def ask(self, question: str) -> str:
        messages = [{"role": "user", "content": question}]
        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages
            )
            if response.stop_reason == "end_turn":
                return response.content[0].text
            
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    print(f"  → Agent uses: {block.name}({block.input})")
                    result = self._execute_tool(block.name, block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result
                    })
                messages += [
                    {"role": "assistant", "content": response.content},
                    {"role": "user",      "content": tool_results}
                ]


        context = "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source', 'unknown')}, "
            f"page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in context_docs
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context from financial reports:\n\n{context}\n\nQuestion: {question}",
                }
            ],
        )
        return response.content[0].text
