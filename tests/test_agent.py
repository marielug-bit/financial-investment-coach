import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document


@patch("src.agent.retrieve")
@patch("src.agent.anthropic.Anthropic")
def test_ask_returns_text(mock_anthropic_cls, mock_retrieve):
    mock_retrieve.return_value = [
        Document(page_content="Revenue was $5B in Q4.", metadata={"source": "q4.pdf", "page": 1})
    ]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        stop_reason="end_turn",
        content=[MagicMock(text="Revenue was $5B in Q4 2024.")],
    )
    mock_anthropic_cls.return_value = mock_client

    from src.agent import FinancialAnalyzerAgent
    agent = FinancialAnalyzerAgent()
    answer = agent.ask("What was the Q4 revenue?")

    assert "5B" in answer
    # retrieve is now called via tool execution (when Claude requests search_documents),
    # not directly — so we only assert the LLM was invoked
    mock_client.messages.create.assert_called_once()


@patch("src.agent.add_documents")
@patch("src.agent.ingest")
@patch("src.agent.anthropic.Anthropic")
def test_index_report_returns_chunk_count(mock_anthropic_cls, mock_ingest, mock_add):
    mock_ingest.return_value = [MagicMock()] * 12
    mock_anthropic_cls.return_value = MagicMock()

    from src.agent import FinancialAnalyzerAgent
    agent = FinancialAnalyzerAgent()
    count = agent.index_report("annual_report.pdf")

    assert count == 12
    mock_add.assert_called_once()
