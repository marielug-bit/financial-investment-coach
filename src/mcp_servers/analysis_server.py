"""MCP server for deep financial analysis — Claude acts as a specialist sub-agent."""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

import anthropic
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("analysis-agent")
_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def _ask_analyst(prompt: str, system: str, max_tokens: int = 2048) -> str:
    resp = _get_client().messages.create(
        model=os.getenv("MODEL_ID", "claude-sonnet-4-6"),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


@mcp.tool()
def analyze_financials(extracted_text: str, analysis_type: str = "comprehensive") -> str:
    """
    Deep financial analysis by a specialist sub-agent (Claude).
    analysis_type: 'comprehensive' | 'risk' | 'growth' | 'profitability' | 'liquidity'
    """
    focus = {
        "comprehensive": "profitability, liquidity, solvency, growth, and key risks",
        "risk": "market risk, credit risk, liquidity risk, operational risk, and regulatory risk",
        "growth": "revenue growth drivers, market expansion, R&D investment, and forward outlook",
        "profitability": "gross/net/operating margins, ROE, ROA, EBITDA, and earnings quality",
        "liquidity": "cash position, working capital, debt maturity profile, and cash conversion cycle",
    }.get(analysis_type, "all financial dimensions")

    return _ask_analyst(
        f"Analyse the following financial data focusing on {focus}. "
        f"Structure your answer with clear sections and bullet points.\n\n{extracted_text}",
        system="You are a senior financial analyst at a top-tier investment bank. "
               "Provide rigorous, structured, data-driven analysis. Cite figures precisely.",
    )


@mcp.tool()
def calculate_financial_ratios(
    revenue: float,
    net_income: float,
    total_assets: float,
    total_equity: float,
    current_assets: float = 0.0,
    current_liabilities: float = 0.0,
    total_debt: float = 0.0,
    ebitda: float = 0.0,
) -> str:
    """Calculate key financial ratios from raw figures (all values in same currency unit)."""
    ratios: dict[str, str] = {}

    if revenue > 0:
        ratios["Net Profit Margin"] = f"{net_income / revenue * 100:.2f}%"
    if total_assets > 0:
        ratios["Return on Assets (ROA)"] = f"{net_income / total_assets * 100:.2f}%"
        ratios["Asset Turnover"] = f"{revenue / total_assets:.2f}x"
    if total_equity > 0:
        ratios["Return on Equity (ROE)"] = f"{net_income / total_equity * 100:.2f}%"
    if current_liabilities > 0 and current_assets > 0:
        ratios["Current Ratio"] = f"{current_assets / current_liabilities:.2f}x"
    if total_equity > 0 and total_debt > 0:
        ratios["Debt-to-Equity"] = f"{total_debt / total_equity:.2f}x"
    if ebitda > 0 and total_debt > 0:
        ratios["Debt/EBITDA"] = f"{total_debt / ebitda:.2f}x"
    if total_assets > 0 and total_equity > 0:
        ratios["Equity Multiplier"] = f"{total_assets / total_equity:.2f}x"

    lines = ["=== Financial Ratios ==="]
    lines.extend(f"  {k}: {v}" for k, v in ratios.items())
    return "\n".join(lines)


@mcp.tool()
def compare_periods(period1_label: str, period1_data: str, period2_label: str, period2_data: str) -> str:
    """Compare financial performance between two periods and identify key changes."""
    return _ask_analyst(
        f"Compare these two financial periods. Highlight key changes, trends, and what drove them.\n\n"
        f"**{period1_label}:**\n{period1_data}\n\n**{period2_label}:**\n{period2_data}",
        system="You are a financial analyst. Be concise, quantitative, and flag surprises.",
        max_tokens=1024,
    )


@mcp.tool()
def generate_executive_summary(full_analysis: str) -> str:
    """Generate a 3-5 bullet executive summary for non-technical stakeholders."""
    return _ask_analyst(
        f"Write a 3-5 bullet executive summary for non-technical stakeholders. "
        f"Respond in English.\n\n{full_analysis}",
        system="You write clear, impactful executive summaries. No jargon.",
        max_tokens=512,
    )


@mcp.tool()
def generate_coach_report(extracted_text: str, company_name: str = "the company") -> str:
    """
    Generate a beginner-friendly investment report from financial document text.
    Returns plain-English summary, health score 1-10, green/red flags,
    invest/wait/avoid recommendation, and ASCII dashboard with arrows and indicators.
    """
    return _ask_analyst(
        f"Analyze the following financial text about {company_name} and produce "
        f"a beginner-friendly report in this EXACT format (fill in all placeholders with real data):\n\n"
        f"## WHAT THIS COMPANY DOES\n"
        f"• [plain-English bullet 1]\n"
        f"• [plain-English bullet 2]\n"
        f"• [plain-English bullet 3]\n"
        f"• [plain-English bullet 4]\n"
        f"• [plain-English bullet 5]\n\n"
        f"## FINANCIAL HEALTH SCORE: [X]/10\n"
        f"[1-2 sentence simple explanation of the score]\n\n"
        f"## GREEN FLAGS ✅\n"
        f"• [positive thing 1]\n"
        f"• [positive thing 2]\n"
        f"• [positive thing 3]\n\n"
        f"## RED FLAGS ❌\n"
        f"• [risk or concern 1]\n"
        f"• [risk or concern 2]\n"
        f"• [risk or concern 3]\n\n"
        f"## RECOMMENDATION: [INVEST / WAIT / AVOID]\n"
        f"[2-3 sentence plain-English justification a beginner can act on]\n\n"
        f"## DASHBOARD\n"
        f"+---------------------------+----------+--------+\n"
        f"| Metric                    | Trend    | Signal |\n"
        f"+---------------------------+----------+--------+\n"
        f"| Revenue Growth            | [↑/↓/→ + label] | [✅/⚠️/❌] |\n"
        f"| Profit Margins            | [↑/↓/→ + label] | [✅/⚠️/❌] |\n"
        f"| Debt Level                | [↑/↓/→ + label] | [✅/⚠️/❌] |\n"
        f"| Cash Flow                 | [↑/↓/→ + label] | [✅/⚠️/❌] |\n"
        f"| Valuation vs Market       | [↑/↓/→ + label] | [✅/⚠️/❌] |\n"
        f"+---------------------------+----------+--------+\n\n"
        f"Use plain English throughout. No jargon. Be honest about both opportunities and risks.\n\n"
        f"Financial data:\n{extracted_text}",
        system=(
            "You are a financial coach writing for complete beginners. "
            "Use simple everyday language. Explain numbers in plain terms. "
            "Be encouraging but honest. Fill in the exact template provided."
        ),
        max_tokens=2048,
    )


if __name__ == "__main__":
    mcp.run()
