"""Financial Intelligence System — multi-agent CLI."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


def _print_banner() -> None:
    coach_on = os.getenv("COACH_MODE", "off").strip().lower() == "on"
    mode_note = " [bold yellow]🎓 Coach Mode ON[/bold yellow]" if coach_on else ""
    console.print(Panel(
        f"[bold blue]Financial Intelligence System[/bold blue]{mode_note}\n"
        "[dim]RAG · Analysis · Market · Email · Paper Trading — powered by Claude + MCP[/dim]",
        border_style="blue",
    ))


def _manage_documents_menu() -> list[str]:
    """Let user pick documents to index at startup. Returns list of paths."""
    console.print("\n[bold]Financial documents to index[/bold]")
    docs_dir = Path("data/raw")
    docs_dir.mkdir(parents=True, exist_ok=True)

    existing = list(docs_dir.glob("*.pdf")) + list(docs_dir.glob("*.xlsx")) + list(docs_dir.glob("*.xls"))
    to_index: list[str] = []

    if existing:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#")
        table.add_column("File")
        table.add_column("Size")
        for i, f in enumerate(existing, 1):
            size_kb = f.stat().st_size // 1024
            table.add_row(str(i), f.name, f"{size_kb} KB")
        console.print(table)

        choice = Prompt.ask(
            "  Index (numbers separated by commas, 'all', or Enter to skip)",
            default="",
        )
        if choice.strip().lower() == "all":
            to_index = [str(f) for f in existing]
        elif choice.strip():
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                to_index = [str(existing[i]) for i in indices if 0 <= i < len(existing)]
            except (ValueError, IndexError):
                console.print("  [red]Invalid selection, skipped.[/red]")
    else:
        console.print(f"  [dim]No files in {docs_dir}. Copy your PDFs/Excel files there.[/dim]")

    custom = Prompt.ask("  Path to an additional file (Enter to skip)", default="")
    if custom.strip() and Path(custom.strip()).exists():
        to_index.append(custom.strip())

    return to_index


def _settings_menu() -> None:
    from src.setup_wizard import run_partial_setup

    options = {
        "1": ("Anthropic API Key", "api"),
        "2": ("Email Configuration (SMTP)", "email"),
        "3": ("Email Groups", "groups"),
        "4": ("Favorite Tickers", "tickers"),
        "5": ("News API", "news"),
        "6": ("Coach Mode (beginner-friendly tone)", "coach"),
        "7": ("Alpaca Paper Trading", "alpaca"),
    }
    console.print("\n[bold]Settings[/bold]")
    for k, (label, _) in options.items():
        console.print(f"  {k}. {label}")
    console.print("  0. Back")

    choice = Prompt.ask("  Choice", default="0")
    if choice in options:
        run_partial_setup(options[choice][1])


def _quick_market_overview() -> None:
    """Show a quick market snapshot for tracked tickers (no agents needed)."""
    tickers_raw = os.getenv("TRACKED_TICKERS", "")
    if not tickers_raw:
        console.print("  [dim]No tickers configured. Go to Settings → Favorite Tickers.[/dim]")
        return

    try:
        import yfinance as yf
        tickers = [t.strip() for t in tickers_raw.split(",") if t.strip()]
        console.print(f"\n[bold]Live Market — {', '.join(tickers)}[/bold]")
        for ticker in tickers:
            try:
                info = yf.Ticker(ticker).info
                price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
                change = info.get("regularMarketChangePercent", 0) or 0
                color = "green" if change >= 0 else "red"
                sign = "+" if change >= 0 else ""
                arrow = "↑" if change >= 0 else "↓"
                console.print(
                    f"  [cyan]{ticker:6}[/cyan]  ${price:<10}  [{color}]{arrow} {sign}{change:.2f}%[/{color}]"
                )
            except Exception:
                console.print(f"  [red]{ticker}: error[/red]")
    except ImportError:
        console.print("  [red]yfinance not installed. Run: pip install yfinance[/red]")


def _paper_portfolio_menu() -> None:
    """Display the paper trading portfolio directly via Alpaca (no agent needed)."""
    api_key = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_SECRET_KEY", "")

    if not api_key or not secret_key:
        console.print("\n  [yellow]Alpaca Paper Trading is not configured yet.[/yellow]")
        console.print("  Go to Settings → Alpaca Paper Trading to set it up.")
        console.print("  [dim](It's free and uses only fake money — no risk!)[/dim]")
        return

    try:
        from alpaca.trading.client import TradingClient
    except ImportError:
        console.print("\n  [red]alpaca-py not installed. Run: pip install alpaca-py[/red]")
        return

    try:
        client = TradingClient(api_key, secret_key, paper=True)
        acct = client.get_account()

        equity = float(acct.equity)
        cash = float(acct.cash)
        last_equity = float(acct.last_equity)
        day_pl = equity - last_equity
        day_pl_pct = (day_pl / last_equity * 100) if last_equity else 0.0
        arrow = "↑" if day_pl >= 0 else "↓"
        color = "green" if day_pl >= 0 else "red"

        console.print("\n[bold]My Paper Portfolio[/bold] [dim](simulated — no real money)[/dim]")
        console.print(f"  Portfolio Value:  [bold]${float(acct.portfolio_value):,.2f}[/bold]")
        console.print(f"  Cash Available:   ${cash:,.2f}")
        console.print(f"  Day P&L:          [{color}]{arrow} ${day_pl:+,.2f} ({day_pl_pct:+.2f}%)[/{color}]")
        console.print(f"  Buying Power:     ${float(acct.buying_power):,.2f}")

        positions = client.get_all_positions()
        if positions:
            console.print("\n  [bold]Open Positions:[/bold]")
            table = Table(show_header=True, header_style="bold cyan", padding=(0, 1))
            table.add_column("Symbol")
            table.add_column("Qty", justify="right")
            table.add_column("Avg Cost", justify="right")
            table.add_column("Current", justify="right")
            table.add_column("P&L", justify="right")
            table.add_column("P&L%", justify="right")

            for pos in positions:
                pl = float(pos.unrealized_pl)
                pl_pct = float(pos.unrealized_plpc) * 100
                pl_arrow = "↑" if pl >= 0 else "↓"
                pl_color = "green" if pl >= 0 else "red"
                signal = "✅" if pl >= 0 else "❌"
                table.add_row(
                    pos.symbol,
                    f"{float(pos.qty):.2f}",
                    f"${float(pos.avg_entry_price):,.2f}",
                    f"${float(pos.current_price):,.2f}",
                    f"[{pl_color}]{signal}{pl_arrow}${pl:+,.2f}[/{pl_color}]",
                    f"[{pl_color}]{pl_pct:+.2f}%[/{pl_color}]",
                )
            console.print(table)
        else:
            console.print("\n  [dim]No open positions yet. Analyze a report and simulate your first trade![/dim]")

        console.print("\n  [dim]To simulate a trade, start an analysis session and ask the coach for a recommendation.[/dim]")

    except Exception as exc:
        console.print(f"\n  [red]Error connecting to Alpaca: {exc}[/red]")
        console.print("  Check your API keys in Settings → Alpaca Paper Trading.")


def _learn_finance_menu() -> None:
    from src.education import run_education_menu
    run_education_menu()


async def _run_agent_session(pre_index: list[str]) -> None:
    from src.agents.orchestrator import run_session
    await run_session(pre_index=pre_index)


async def _run_weekly_report() -> None:
    from src.agents.orchestrator import run_weekly_report_session
    await run_weekly_report_session()


def main() -> None:
    _print_banner()

    from src.setup_wizard import is_configured, is_onboarding_done, run_full_setup, run_onboarding

    if not is_configured():
        console.print("\n[yellow]First launch detected. Starting configuration...[/yellow]")
        run_full_setup()
        load_dotenv(override=True)
        if is_configured() and not is_onboarding_done():
            run_onboarding()
        return

    if not is_onboarding_done():
        console.print(Panel(
            "[bold blue]Welcome! 👋[/bold blue]\n"
            "It looks like you haven't taken the quick tour yet.",
            border_style="blue",
        ))
        if Confirm.ask("  Take a 2-minute guided tour?", default=True):
            run_onboarding()

    while True:
        load_dotenv(override=True)
        _print_banner()
        console.print("\n[bold]Main Menu[/bold]")
        console.print("  1. Start an analysis session (AI agents)")
        console.print("  2. Quick market overview (favorite tickers)")
        console.print("  3. My Paper Portfolio")
        console.print("  4. Learn Finance (mini-lessons)")
        console.print("  5. Send Weekly Coach Report")
        console.print("  6. Settings")
        console.print("  0. Quit")

        choice = Prompt.ask("\n  Choice", default="1")

        if choice == "0":
            console.print("[dim]Goodbye.[/dim]")
            break

        elif choice == "1":
            pre_index = _manage_documents_menu()
            console.print("\n[yellow]Starting MCP agents...[/yellow]")
            asyncio.run(_run_agent_session(pre_index))

        elif choice == "2":
            _quick_market_overview()

        elif choice == "3":
            _paper_portfolio_menu()

        elif choice == "4":
            _learn_finance_menu()

        elif choice == "5":
            console.print(
                "\n[bold]Send Weekly Coach Report[/bold]\n"
                "  This will generate a personalized weekly update and email it\n"
                "  to everyone in your 'weekly' group.\n"
            )
            if Confirm.ask("  Send now?", default=True):
                asyncio.run(_run_weekly_report())

        elif choice == "6":
            _settings_menu()


if __name__ == "__main__":
    main()
