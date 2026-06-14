"""MCP server for Alpaca paper trading — Agent 5 (Trader)."""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("trading-agent")


def _get_client():
    try:
        from alpaca.trading.client import TradingClient
    except ImportError:
        raise RuntimeError("alpaca-py not installed. Run: pip install alpaca-py")

    api_key = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_SECRET_KEY", "")
    if not api_key or not secret_key:
        raise RuntimeError(
            "ALPACA_API_KEY and ALPACA_SECRET_KEY must be set in .env.\n"
            "Sign up free at alpaca.markets → Paper Trading → Generate API Keys."
        )
    return TradingClient(api_key, secret_key, paper=True)


@mcp.tool()
def get_portfolio() -> str:
    """Get current paper trading portfolio value, cash balance, and day P&L."""
    try:
        client = _get_client()
        acct = client.get_account()

        equity = float(acct.equity)
        cash = float(acct.cash)
        portfolio_value = float(acct.portfolio_value)
        last_equity = float(acct.last_equity)
        day_pl = equity - last_equity
        day_pl_pct = (day_pl / last_equity * 100) if last_equity else 0.0

        arrow = "↑" if day_pl >= 0 else "↓"
        signal = "✅" if day_pl >= 0 else "⚠️"

        return (
            "=== Paper Portfolio ===\n"
            f"  Portfolio Value:  ${portfolio_value:,.2f}\n"
            f"  Cash Available:   ${cash:,.2f}\n"
            f"  Equity:           ${equity:,.2f}\n"
            f"  Day P&L:          {signal} {arrow} ${day_pl:+,.2f} ({day_pl_pct:+.2f}%)\n"
            f"  Buying Power:     ${float(acct.buying_power):,.2f}\n"
            "\n[PAPER TRADING — No real money involved]"
        )
    except RuntimeError as exc:
        return f"Configuration error: {exc}"
    except Exception as exc:
        return f"Error fetching portfolio: {exc}"


@mcp.tool()
def get_positions() -> str:
    """List all current paper trading positions with unrealized P&L."""
    try:
        client = _get_client()
        positions = client.get_all_positions()

        if not positions:
            return "No open positions in your paper portfolio."

        header = f"{'Symbol':<8} {'Qty':>6} {'Avg Cost':>10} {'Current':>10} {'P&L':>12} {'P&L%':>8}"
        divider = "-" * 58
        lines = ["=== Open Positions ===", header, divider]

        for pos in positions:
            pl = float(pos.unrealized_pl)
            pl_pct = float(pos.unrealized_plpc) * 100
            arrow = "↑" if pl >= 0 else "↓"
            signal = "✅" if pl >= 0 else "❌"
            lines.append(
                f"{pos.symbol:<8} {float(pos.qty):>6.2f}"
                f" ${float(pos.avg_entry_price):>9.2f}"
                f" ${float(pos.current_price):>9.2f}"
                f" {signal}{arrow}${pl:>+9.2f} {pl_pct:>+7.2f}%"
            )

        lines.append("\n[PAPER TRADING — No real money involved]")
        return "\n".join(lines)
    except RuntimeError as exc:
        return f"Configuration error: {exc}"
    except Exception as exc:
        return f"Error fetching positions: {exc}"


@mcp.tool()
def preview_order(ticker: str, qty: float, side: str = "buy") -> str:
    """
    Preview a paper order — shows price, estimated cost, and confirmation prompt.
    Call place_paper_order to execute after showing this preview to the user.
    side: 'buy' or 'sell'
    """
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        total = price * qty
        side_label = side.upper()
        icon = "🟢" if side.lower() == "buy" else "🔴"

        return (
            f"=== Order Preview ===\n"
            f"  {icon} {side_label}  {qty} share(s) of {ticker.upper()}\n"
            f"  Current Price:    ${price:,.2f}\n"
            f"  Estimated Total:  ${total:,.2f}\n"
            f"\n⚠️  PAPER TRADING ONLY — No real money will be used.\n"
            f"To confirm and simulate this order, call place_paper_order."
        )
    except Exception as exc:
        return f"Error previewing order: {exc}"


@mcp.tool()
def place_paper_order(ticker: str, qty: float, side: str = "buy") -> str:
    """
    Place a simulated paper trading order on Alpaca.
    IMPORTANT: Always call preview_order first and show it to the user before calling this.
    side: 'buy' or 'sell'
    This is PAPER TRADING only — no real money involved.
    """
    try:
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
    except ImportError:
        return "alpaca-py not installed. Run: pip install alpaca-py"

    try:
        client = _get_client()
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        request = MarketOrderRequest(
            symbol=ticker.upper(),
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY,
        )
        order = client.submit_order(request)

        return (
            f"=== Simulated Order Submitted ✅ ===\n"
            f"  Order ID:  {order.id}\n"
            f"  Symbol:    {order.symbol}\n"
            f"  Side:      {order.side}\n"
            f"  Qty:       {order.qty}\n"
            f"  Status:    {order.status}\n"
            f"\n[PAPER TRADING — No real money involved]"
        )
    except RuntimeError as exc:
        return f"Configuration error: {exc}"
    except Exception as exc:
        return f"Error placing order: {exc}"


if __name__ == "__main__":
    mcp.run()
