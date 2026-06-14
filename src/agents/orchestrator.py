"""Multi-agent orchestrator: LangGraph agent connecting to 6 MCP specialist servers."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

_PROJECT_ROOT = str(Path(__file__).parent.parent.parent.resolve())

_ADVANCED_SYSTEM_PROMPT = """You are a financial intelligence system coordinating five specialist agents:

- **Agent 1 — Document Analyst** (rag-agent): reads, indexes, and extracts data from financial reports
- **Agent 2 — Market Analyst** (market-agent): watches live tickers, fetches financial statements and news
- **Agent 3 — Coach** (coach-agent): translates technical findings into beginner-friendly insights
- **Agent 4 — Reporter** (email-agent): formats and sends reports and alerts to configured email groups
- **Agent 5 — Trader** (trading-agent): handles Alpaca paper trading orders (simulated, no real money)

## Workflow:
1. For any company question → Agent 1 searches documents first, Agent 2 enriches with live data
2. After complete analysis → Agent 3 generates a beginner-friendly coach report (generate_coach_report)
3. If recommendation is "INVEST" → offer: "Want to simulate buying this stock?" via Agent 5
4. After any simulated trade → Agent 5 places the order, Agent 4 sends trade confirmation to 'me' group
5. After any full analysis → offer to send a report via Agent 4
6. For market alerts (big price drops, strong signals) → Agent 4 sends to 'alerts' group
7. Always cite sources: document name + page number
8. Always fetch live market data — never guess prices

Respond in English."""

_COACH_SYSTEM_PROMPT = """You are a friendly personal financial coach helping a complete beginner understand their investments.

You coordinate five specialist helpers behind the scenes:
- **Document Reader**: finds information in uploaded financial reports
- **Market Watcher**: checks live stock prices and recent news
- **Coach** (that's you): explains everything in plain, friendly English
- **Email Sender**: sends you reports and trade confirmations
- **Paper Trader**: simulates buying stocks with fake money so you can practice safely

## How you work:
1. When the user asks about a company → search documents first, then check live market data
2. Always generate a beginner-friendly coach report (generate_coach_report) after analyzing a document
3. Explain every financial term you mention with a simple everyday analogy
4. If the analysis says "INVEST" → ask: "Would you like to practice buying this stock with paper money? (It's completely simulated — no real money!)"
5. Before any simulated order → always show a preview with: "You are about to simulate buying X shares of Y at $Z — sound good?"
6. After any simulated trade → send a confirmation email to the 'me' group
7. Be encouraging, warm, and patient. Never assume prior knowledge.
8. Use bullet points and short sentences.

Remember: your job is to make finance feel approachable and understandable, not intimidating.

Respond in English."""


def _coach_mode_on() -> bool:
    return os.getenv("COACH_MODE", "off").strip().lower() == "on"


def _get_system_prompt() -> str:
    return _COACH_SYSTEM_PROMPT if _coach_mode_on() else _ADVANCED_SYSTEM_PROMPT


def _server_config() -> dict:
    env = {**os.environ, "PYTHONPATH": _PROJECT_ROOT}
    python = sys.executable
    base = {
        "command": python,
        "transport": "stdio",
        "env": env,
        "cwd": _PROJECT_ROOT,
    }
    return {
        "rag": {**base, "args": ["-m", "src.mcp_servers.rag_server"]},
        "analysis": {**base, "args": ["-m", "src.mcp_servers.analysis_server"]},
        "market": {**base, "args": ["-m", "src.mcp_servers.market_server"]},
        "email": {**base, "args": ["-m", "src.mcp_servers.email_server"]},
        "coach": {**base, "args": ["-m", "src.mcp_servers.coach_server"]},
        "trading": {**base, "args": ["-m", "src.mcp_servers.trading_server"]},
    }


def _get_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model=os.getenv("MODEL_ID", "claude-sonnet-4-6"),
        max_tokens=int(os.getenv("MAX_TOKENS", 4096)),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )


def _extract_answer(result: dict) -> str:
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content:
            return msg.content
    return str(result)


async def run_query(question: str) -> str:
    """Run a single query through the full multi-agent pipeline."""
    async with MultiServerMCPClient(_server_config()) as client:
        tools = client.get_tools()
        agent = create_agent(_get_llm(), tools, system_prompt=_get_system_prompt())
        result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
        return _extract_answer(result)


async def run_session(pre_index: list[str] | None = None) -> None:
    """Start an interactive session, keeping all MCP servers alive throughout."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    coach_on = _coach_mode_on()

    async with MultiServerMCPClient(_server_config()) as client:
        tools = client.get_tools()
        tool_names = [t.name for t in tools]
        agent = create_agent(_get_llm(), tools, system_prompt=_get_system_prompt())

        mode_label = "[bold yellow]Coach Mode ON[/bold yellow] 🎓" if coach_on else "[bold cyan]Advanced Mode[/bold cyan]"
        console.print(Panel(
            f"[bold green]MCP Agents connected[/bold green] ({len(tool_names)} tools) — {mode_label}\n" +
            "\n".join(f"  ✓ [cyan]{n}[/cyan]" for n in tool_names),
            title="[bold]Financial Intelligence System[/bold]",
            border_style="blue",
        ))

        if pre_index:
            for doc_path in pre_index:
                console.print(f"\n[yellow]Indexing {os.path.basename(doc_path)}...[/yellow]")
                res = await agent.ainvoke(
                    {"messages": [HumanMessage(content=f"Index the document at: {doc_path}")]}
                )
                console.print(f"[green]{_extract_answer(res)}[/green]")

        if coach_on:
            console.print("\n[dim]Hi! I'm your financial coach. Ask me anything about investing. Type 'quit' to exit.[/dim]\n")
        else:
            console.print("\n[dim]Type your question (or 'quit' to exit)[/dim]\n")

        while True:
            try:
                question = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye.[/dim]")
                break

            if not question:
                continue
            if question.lower() in {"quit", "exit", "q"}:
                console.print("[dim]Goodbye.[/dim]")
                break

            if coach_on:
                console.print("\n[yellow]Your coach is thinking...[/yellow]\n")
            else:
                console.print("\n[yellow]Agents working...[/yellow]\n")

            try:
                result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
                answer = _extract_answer(result)
                console.print(Markdown(answer))
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
            console.print()


async def run_weekly_report_session() -> None:
    """Run a dedicated agent session to generate and send the weekly coach report."""
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()

    prompt = (
        "Generate and send the weekly coach report. Do the following:\n"
        "1. Search documents indexed this week for key findings\n"
        "2. Get current prices for all tracked tickers\n"
        "3. Get the paper portfolio summary\n"
        "4. Identify 3 investment opportunities based on recent analysis\n"
        "5. Send the weekly coach report to the 'weekly' email group using send_weekly_coach_report\n"
        "Write everything in plain English suitable for a beginner investor."
    )

    console.print("\n[yellow]Generating weekly coach report...[/yellow]\n")
    async with MultiServerMCPClient(_server_config()) as client:
        tools = client.get_tools()
        agent = create_agent(_get_llm(), tools, system_prompt=_get_system_prompt())
        result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
        answer = _extract_answer(result)
        console.print(Markdown(answer))
