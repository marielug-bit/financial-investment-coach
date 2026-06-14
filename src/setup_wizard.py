"""Interactive setup wizard — runs on first launch or when user chooses 'Settings'."""

import os
import yaml
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

_ENV_FILE = Path(".env")
_CONFIG_FILE = Path("config") / "email_groups.yaml"
_ONBOARDING_MARKER = Path(".onboarding_done")


def _set_env(key: str, value: str) -> None:
    """Write or update a key=value in .env"""
    lines: list[str] = []
    updated = False
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            if line.startswith(f"{key}="):
                lines.append(f"{key}={value}")
                updated = True
            else:
                lines.append(line)
    if not updated:
        lines.append(f"{key}={value}")
    _ENV_FILE.write_text("\n".join(lines) + "\n")


def _load_config() -> dict:
    if _CONFIG_FILE.exists():
        return yaml.safe_load(_CONFIG_FILE.read_text()) or {"groups": {}}
    return {"groups": {}}


def _save_config(config: dict) -> None:
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True))


def setup_api_key() -> None:
    console.print("\n[bold]1. Anthropic API Key[/bold]")
    current = os.getenv("ANTHROPIC_API_KEY", "")
    if current and current != "your_anthropic_api_key_here":
        console.print(f"  Current key: [green]***{current[-6:]}[/green]")
        if not Confirm.ask("  Update?", default=False):
            return
    key = Prompt.ask("  ANTHROPIC_API_KEY", password=True)
    if key:
        _set_env("ANTHROPIC_API_KEY", key)
        console.print("  [green]✓ Key saved[/green]")


def setup_smtp() -> None:
    console.print("\n[bold]2. Email Configuration (SMTP)[/bold]")
    console.print("  [dim]For Gmail: create an App Password at myaccount.google.com/security[/dim]")

    host = Prompt.ask("  SMTP Host", default=os.getenv("SMTP_HOST", "smtp.gmail.com"))
    port = Prompt.ask("  SMTP Port", default=os.getenv("SMTP_PORT", "587"))
    user = Prompt.ask("  Sender email", default=os.getenv("SMTP_USER", ""))
    password = Prompt.ask("  Password / App Password", password=True, default="")

    _set_env("SMTP_HOST", host)
    _set_env("SMTP_PORT", port)
    if user:
        _set_env("SMTP_USER", user)
    if password:
        _set_env("SMTP_PASSWORD", password)
    console.print("  [green]✓ Email configured[/green]")


def setup_email_groups() -> None:
    console.print("\n[bold]3. Email Groups[/bold]")
    config = _load_config()
    groups = config.get("groups", {})

    while True:
        if groups:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Group")
            table.add_column("Members")
            for name, members in groups.items():
                table.add_row(name, ", ".join(members or []))
            console.print(table)
        else:
            console.print("  [dim]No groups configured.[/dim]")

        action = Prompt.ask(
            "  Action",
            choices=["add", "remove", "done"],
            default="done",
        )
        if action == "done":
            break
        elif action == "add":
            name = Prompt.ask("  Group name (e.g., management, analysts)")
            emails_raw = Prompt.ask("  Emails (comma-separated)")
            emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
            if name and emails:
                groups[name] = emails
                console.print(f"  [green]✓ Group '{name}' added ({len(emails)} members)[/green]")
        elif action == "remove":
            name = Prompt.ask("  Group name to remove")
            if name in groups:
                del groups[name]
                console.print(f"  [green]✓ Group '{name}' removed[/green]")
            else:
                console.print(f"  [red]Group '{name}' not found[/red]")

    config["groups"] = groups
    _save_config(config)
    console.print("  [green]✓ Groups saved[/green]")


def setup_tracked_tickers() -> None:
    console.print("\n[bold]4. Favorite Stock Tickers[/bold]")
    current = os.getenv("TRACKED_TICKERS", "")
    if current:
        console.print(f"  Current: [cyan]{current}[/cyan]")
    tickers_raw = Prompt.ask(
        "  Tickers (comma-separated, e.g., AAPL,MSFT,NVDA)",
        default=current,
    )
    tickers = ",".join(t.strip().upper() for t in tickers_raw.split(",") if t.strip())
    _set_env("TRACKED_TICKERS", tickers)
    console.print(f"  [green]✓ Tickers saved: {tickers}[/green]")


def setup_news_api() -> None:
    console.print("\n[bold]5. News API (optional)[/bold]")
    console.print("  [dim]Free key at newsapi.org — improves news results[/dim]")
    current = os.getenv("NEWS_API_KEY", "")
    if current:
        console.print(f"  Current key: [green]***{current[-4:]}[/green]")
        if not Confirm.ask("  Update?", default=False):
            return
    key = Prompt.ask("  NEWS_API_KEY (Enter to skip)", default="")
    if key:
        _set_env("NEWS_API_KEY", key)
        console.print("  [green]✓ News API configured[/green]")


def setup_coach_mode() -> None:
    console.print("\n[bold]6. Coach Mode[/bold]")
    console.print("  [dim]ON  → plain English, every term explained, encouraging tone[/dim]")
    console.print("  [dim]OFF → advanced mode with full financial detail[/dim]")
    current = os.getenv("COACH_MODE", "off").strip().lower()
    console.print(f"  Current: [cyan]{'ON' if current == 'on' else 'OFF'}[/cyan]")
    enable = Confirm.ask("  Enable Coach Mode?", default=(current == "on"))
    _set_env("COACH_MODE", "on" if enable else "off")
    console.print(f"  [green]✓ Coach Mode {'enabled' if enable else 'disabled'}[/green]")


def setup_alpaca() -> None:
    console.print("\n[bold]7. Alpaca Paper Trading[/bold]")
    console.print("  [dim]Practice investing with simulated money — no real money involved.[/dim]")
    console.print("  [dim]Setup steps:[/dim]")
    console.print("  [dim]  1. Go to alpaca.markets and create a free account[/dim]")
    console.print("  [dim]  2. Switch to Paper Trading mode in the dashboard[/dim]")
    console.print("  [dim]  3. Generate API keys under Paper Trading[/dim]")
    console.print("  [dim]  4. Enter them below[/dim]")

    current_key = os.getenv("ALPACA_API_KEY", "")
    if current_key:
        console.print(f"\n  Current API key: [green]***{current_key[-6:]}[/green]")
        if not Confirm.ask("  Update?", default=False):
            return

    api_key = Prompt.ask("  ALPACA_API_KEY (Enter to skip)", default="")
    if not api_key:
        console.print("  [dim]Skipped. You can configure this later in Settings.[/dim]")
        return

    secret_key = Prompt.ask("  ALPACA_SECRET_KEY", password=True)
    if api_key:
        _set_env("ALPACA_API_KEY", api_key)
    if secret_key:
        _set_env("ALPACA_SECRET_KEY", secret_key)
    console.print("  [green]✓ Alpaca Paper Trading configured[/green]")


def is_configured() -> bool:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    return bool(key and key != "your_anthropic_api_key_here")


def is_onboarding_done() -> bool:
    return _ONBOARDING_MARKER.exists()


def _mark_onboarding_done() -> None:
    _ONBOARDING_MARKER.write_text("done")


def run_onboarding() -> None:
    """Guided first-time tutorial for new users."""
    console.print(Panel(
        "[bold blue]Welcome to Your Personal Financial Coach! 🎓[/bold blue]\n\n"
        "I'm here to help you understand financial reports, track the market,\n"
        "and practice investing — all in plain English, no experience needed.\n\n"
        "Let me give you a quick tour so you know exactly what to do.",
        border_style="blue",
        padding=(1, 2),
    ))

    console.print("\n[bold]Here's what you can do:[/bold]")
    console.print("  📄  Upload a company report (PDF) and I'll explain it in plain English")
    console.print("  📈  Track stock prices for companies you're interested in")
    console.print("  🎓  Take finance mini-lessons from the 'Learn Finance' menu")
    console.print("  💼  Simulate buying stocks with paper money (no real money!)")
    console.print("  📧  Get weekly reports delivered to your email")

    Prompt.ask("\n  Press Enter to continue", default="")

    console.print("\n[bold]Step 1 — Turn on Coach Mode[/bold]")
    console.print("  Coach Mode makes everything beginner-friendly: simple words, analogies, and encouragement.")
    enable_coach = Confirm.ask("  Would you like to enable Coach Mode?", default=True)
    _set_env("COACH_MODE", "on" if enable_coach else "off")
    console.print(f"  [green]✓ Coach Mode {'enabled' if enable_coach else 'disabled'}[/green]")

    console.print("\n[bold]Step 2 — Your first financial report[/bold]")
    console.print("  Copy any PDF financial report into the [cyan]data/raw/[/cyan] folder.")
    console.print("  Then choose 'Start an analysis session' from the main menu.")
    console.print("  The app will index it and you can ask questions like:")
    console.print("  [dim]  'Is this company profitable?'[/dim]")
    console.print("  [dim]  'Should I invest in this company?'[/dim]")
    console.print("  [dim]  'Explain the balance sheet in simple terms'[/dim]")

    Prompt.ask("\n  Press Enter to continue", default="")

    console.print("\n[bold]Step 3 — Set up Paper Trading (optional)[/bold]")
    console.print("  Paper trading lets you practice buying stocks with fake money.")
    console.print("  It's completely safe — you can't lose real money.")
    if Confirm.ask("  Would you like to set up Alpaca Paper Trading now?", default=False):
        setup_alpaca()
    else:
        console.print("  [dim]No problem! You can set it up anytime in Settings → Alpaca Paper Trading.[/dim]")

    _mark_onboarding_done()
    console.print(Panel(
        "[bold green]You're all set! 🎉[/bold green]\n\n"
        "Head back to the main menu to start your first analysis.\n"
        "Remember: there are no silly questions here. I'm here to help!",
        border_style="green",
        padding=(1, 2),
    ))
    Prompt.ask("\n  Press Enter to go to the main menu", default="")


def run_full_setup() -> None:
    console.print(Panel.fit(
        "[bold blue]Financial Intelligence System — Setup[/bold blue]\n"
        "[dim]Press Enter to keep the current value[/dim]",
        border_style="blue",
    ))
    setup_api_key()
    setup_smtp()
    setup_email_groups()
    setup_tracked_tickers()
    setup_news_api()
    setup_coach_mode()
    setup_alpaca()
    console.print(Panel("[bold green]✓ Setup complete — restart the app[/bold green]", border_style="green"))


def run_partial_setup(section: str) -> None:
    """Run a specific section of the setup (called from the main menu)."""
    sections = {
        "api": setup_api_key,
        "email": setup_smtp,
        "groups": setup_email_groups,
        "tickers": setup_tracked_tickers,
        "news": setup_news_api,
        "coach": setup_coach_mode,
        "alpaca": setup_alpaca,
    }
    fn = sections.get(section)
    if fn:
        fn()
    else:
        run_full_setup()
