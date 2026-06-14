"""MCP server for live market data, stock prices, financial statements, and news."""

import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("market-agent")


@mcp.tool()
def get_stock_info(ticker: str) -> str:
    """Get current stock price, market cap, P/E, 52-week range, and key metrics."""
    try:
        info = yf.Ticker(ticker).info
        hist = yf.Ticker(ticker).history(period="5d")

        name = info.get("longName", ticker.upper())
        price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        mcap = info.get("marketCap", 0)
        mcap_str = f"${mcap / 1e9:.2f}B" if mcap else "N/A"

        lines = [f"=== {name} ({ticker.upper()}) ===",
                 f"Price:          ${price}",
                 f"Market Cap:     {mcap_str}",
                 f"P/E (trailing): {info.get('trailingPE', 'N/A')}",
                 f"P/E (forward):  {info.get('forwardPE', 'N/A')}",
                 f"52W High:       ${info.get('fiftyTwoWeekHigh', 'N/A')}",
                 f"52W Low:        ${info.get('fiftyTwoWeekLow', 'N/A')}",
                 f"Dividend Yield: {(info.get('dividendYield') or 0) * 100:.2f}%",
                 f"Beta:           {info.get('beta', 'N/A')}",
                 f"Sector:         {info.get('sector', 'N/A')}",
                 f"Industry:       {info.get('industry', 'N/A')}"]

        if not hist.empty:
            chg = (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100
            lines.append(f"5-Day Change:   {chg:+.2f}%")

        return "\n".join(lines)
    except Exception as exc:
        return f"Error fetching data for {ticker}: {exc}"


@mcp.tool()
def get_financial_statements(ticker: str, statement: str = "income") -> str:
    """
    Fetch annual financial statements for a public company.
    statement: 'income' | 'balance' | 'cashflow'
    """
    try:
        stock = yf.Ticker(ticker)
        df_map = {"income": stock.financials, "balance": stock.balance_sheet, "cashflow": stock.cashflow}
        df = df_map.get(statement)
        if df is None:
            return f"Unknown statement type '{statement}'. Use: income, balance, cashflow."
        if df.empty:
            return f"No {statement} statement data available for {ticker.upper()}."

        lines = [f"=== {ticker.upper()} {statement.title()} Statement (Annual, last 4 years) ==="]
        for idx in df.index[:12]:
            row = df.loc[idx].dropna()
            if row.empty:
                continue
            values = "  |  ".join(f"{col.year}: {val:,.0f}" for col, val in row.items())
            lines.append(f"  {idx}: {values}")
        return "\n".join(lines)
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def compare_stocks(tickers: list[str]) -> str:
    """Compare key valuation and performance metrics across multiple stocks side by side."""
    rows = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
            mcap = info.get("marketCap", 0)
            rows.append({
                "Ticker": t.upper(),
                "Price": f"${price}",
                "Mkt Cap": f"${mcap / 1e9:.1f}B" if mcap else "N/A",
                "P/E": str(round(info.get("trailingPE", 0) or 0, 1) or "N/A"),
                "Fwd P/E": str(round(info.get("forwardPE", 0) or 0, 1) or "N/A"),
                "52W Hi": f"${info.get('fiftyTwoWeekHigh', 'N/A')}",
                "52W Lo": f"${info.get('fiftyTwoWeekLow', 'N/A')}",
                "Beta": str(info.get("beta", "N/A")),
                "Div%": f"{(info.get('dividendYield') or 0) * 100:.1f}%",
            })
        except Exception as exc:
            rows.append({"Ticker": t.upper(), "Price": f"Error: {exc}"})

    if not rows:
        return "No data retrieved."

    headers = list(rows[0].keys())
    widths = [max(len(h), max(len(r.get(h, "")) for r in rows)) for h in headers]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "|" + "|".join(f" {h:<{w}} " for h, w in zip(headers, widths)) + "|"

    lines = [sep, header_row, sep]
    for r in rows:
        lines.append("|" + "|".join(f" {r.get(h, ''):<{w}} " for h, w in zip(headers, widths)) + "|")
    lines.append(sep)
    return "\n".join(lines)


@mcp.tool()
def get_financial_news(query: str, max_articles: int = 5) -> str:
    """Get recent financial news for a company or topic. Falls back to yfinance if no API key."""
    news_api_key = os.getenv("NEWS_API_KEY")

    if news_api_key:
        try:
            from newsapi import NewsApiClient
            client = NewsApiClient(api_key=news_api_key)
            result = client.get_everything(q=query, language="en", sort_by="publishedAt", page_size=max_articles)
            articles = result.get("articles", [])
            if articles:
                lines = [f"=== News: {query} ==="]
                for a in articles:
                    lines.append(f"• [{a['publishedAt'][:10]}] {a['title']} — {a['source']['name']}")
                    if a.get("description"):
                        lines.append(f"  {a['description'][:160]}")
                return "\n".join(lines)
        except Exception:
            pass

    # Fallback: yfinance news for first word (ticker guess)
    try:
        ticker_guess = query.split()[0]
        news = yf.Ticker(ticker_guess).news[:max_articles]
        if news:
            lines = [f"=== News: {query} (via yfinance) ==="]
            for art in news:
                lines.append(f"• {art.get('title', 'N/A')} — {art.get('publisher', 'N/A')}")
            return "\n".join(lines)
    except Exception:
        pass

    return f"No news found for '{query}'. Set NEWS_API_KEY in .env for full news access."


if __name__ == "__main__":
    mcp.run()
