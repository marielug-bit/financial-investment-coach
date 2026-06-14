"""MCP server for the Coach agent — Agent 3, translates analysis into beginner insights."""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

import anthropic
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("coach-agent")
_client: anthropic.Anthropic | None = None

_COACH_SYSTEM = (
    "You are a friendly personal financial coach helping complete beginners. "
    "Use plain, everyday English. For every financial term, immediately explain it with a simple analogy "
    "(e.g., 'Revenue is like the total cash in your tip jar before paying any bills'). "
    "Be warm, encouraging, and honest. Never assume prior financial knowledge. "
    "Use short sentences. If you must use a technical term, always define it right after."
)


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def _ask_coach(prompt: str, max_tokens: int = 1024) -> str:
    resp = _get_client().messages.create(
        model=os.getenv("MODEL_ID", "claude-sonnet-4-6"),
        max_tokens=max_tokens,
        system=_COACH_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


@mcp.tool()
def explain_term(term: str) -> str:
    """Explain a financial term in plain English with an everyday analogy."""
    return _ask_coach(
        f"Explain the financial term '{term}' in 2-3 sentences. "
        f"Use simple language and one everyday analogy. Be friendly.",
        max_tokens=250,
    )


@mcp.tool()
def simplify_analysis(analysis_text: str) -> str:
    """Rewrite a technical financial analysis in plain, beginner-friendly English."""
    return _ask_coach(
        f"Rewrite this financial analysis so a complete beginner can understand it. "
        f"Keep all the important facts but remove jargon. Use bullet points.\n\n{analysis_text}",
        max_tokens=800,
    )


@mcp.tool()
def generate_investment_tip(context: str = "") -> str:
    """Generate a practical, beginner-friendly investing tip relevant to the current context."""
    base = "Give one practical investing tip for a beginner. 2-3 sentences, actionable, encouraging."
    prompt = f"{base} Context: {context}" if context else base
    return _ask_coach(prompt, max_tokens=200)


@mcp.tool()
def coach_weekly_narrative(
    docs_summary: str,
    market_summary: str,
    portfolio_summary: str,
    opportunities: str,
) -> str:
    """
    Write the narrative sections of a weekly coach report in plain English.
    Returns formatted text ready to include in the weekly email.
    """
    return _ask_coach(
        f"Write a friendly weekly financial update for a beginner investor. "
        f"Use simple language, be encouraging, and explain any numbers in plain terms. "
        f"Structure it with these sections:\n"
        f"1. THIS WEEK IN REVIEW (based on: {docs_summary})\n"
        f"2. MARKET UPDATE (based on: {market_summary})\n"
        f"3. YOUR PORTFOLIO (based on: {portfolio_summary})\n"
        f"4. OPPORTUNITIES TO WATCH (based on: {opportunities})\n"
        f"5. YOUR LEARNING TIP OF THE WEEK\n"
        f"Keep it warm, under 400 words total.",
        max_tokens=600,
    )


if __name__ == "__main__":
    mcp.run()
