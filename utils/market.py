"""yfinance helpers, health score, risk classification — all cached."""
import datetime
import os
import streamlit as st

# ── Company name → ticker lookup ─────────────────────────────────────────────
NAME_TO_TICKER: dict[str, str] = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
    "alphabet": "GOOGL", "amazon": "AMZN", "nvidia": "NVDA",
    "tesla": "TSLA", "meta": "META", "facebook": "META",
    "netflix": "NFLX", "spotify": "SPOT", "uber": "UBER",
    "airbnb": "ABNB", "paypal": "PYPL", "visa": "V",
    "mastercard": "MA", "jpmorgan": "JPM", "jp morgan": "JPM",
    "goldman sachs": "GS", "disney": "DIS", "coca cola": "KO",
    "cocacola": "KO", "pepsi": "PEP", "pepsico": "PEP",
    "walmart": "WMT", "target": "TGT", "nike": "NKE",
    "boeing": "BA", "ford": "F", "general motors": "GM", "gm": "GM",
    "intel": "INTC", "amd": "AMD", "qualcomm": "QCOM",
    "salesforce": "CRM", "oracle": "ORCL", "ibm": "IBM",
    "palantir": "PLTR", "snowflake": "SNOW", "coinbase": "COIN",
    "shopify": "SHOP", "square": "SQ", "block": "SQ",
    "twitter": "X", "x": "X", "teva": "TEVA", "nice": "NICE",
    "johnson": "JNJ", "pfizer": "PFE", "moderna": "MRNA",
    "exxon": "XOM", "chevron": "CVX", "shell": "SHEL",
    "berkshire": "BRK-B", "warren buffett": "BRK-B",
}

GLOSSARY: dict[str, str] = {
    "Asset": "Anything a company owns that has value — cash, buildings, equipment",
    "Liability": "Money a company owes — loans, credit cards, unpaid bills",
    "Equity": "What's left after paying all debts — the company's true net worth",
    "Revenue": "Total money coming in from selling products or services",
    "Net Income": "Final profit after ALL expenses, taxes, and interest are paid",
    "EPS": "Earnings Per Share — total profit divided by number of shares",
    "P/E Ratio": "Price ÷ Earnings — how much you pay for every $1 of profit",
    "Dividend": "Regular cash payment from a company to its shareholders",
    "Bull Market": "When stock prices rise overall — investors are optimistic",
    "Bear Market": "When stock prices fall overall — investors are pessimistic",
    "Portfolio": "The total collection of all your investments",
    "Diversification": "Owning many different investments to reduce risk",
    "IPO": "First time a company sells shares to the public",
    "Market Cap": "Total value of all shares — a measure of company size",
    "Beta": "How volatile a stock is vs the market (above 1 = more swings)",
    "Free Cash Flow": "Real cash left after running the business and growing it",
    "Moat": "A competitive advantage protecting the business from rivals",
    "Ticker": "Stock's short code — AAPL for Apple, MSFT for Microsoft",
    "P&L": "Profit and Loss — how much you've gained or lost",
    "Paper Trading": "Practice investing with fake money — zero real risk",
}


OPPORTUNITY_UNIVERSE: dict[str, list[str]] = {
    "high": [
        "NVDA", "TSLA", "COIN", "PLTR", "MRNA", "SNOW", "SPOT",
        "UBER", "ABNB", "AMD", "SHOP", "RBLX", "HOOD", "SOFI",
    ],
    "moderate": [
        "AAPL", "MSFT", "GOOGL", "META", "AMZN", "NFLX", "CRM",
        "ORCL", "ADBE", "INTC", "QCOM", "PYPL", "DIS", "SBUX",
    ],
    "low": [
        "JNJ", "KO", "PEP", "WMT", "XOM", "CVX", "V",
        "MA", "PFE", "MCD", "PG", "T", "VZ", "IBM",
    ],
}


def daily_opportunities() -> dict[str, str]:
    """Return one ticker per risk category, rotating daily."""
    ordinal = datetime.date.today().toordinal()
    return {
        cat: tickers[ordinal % len(tickers)]
        for cat, tickers in OPPORTUNITY_UNIVERSE.items()
    }


def resolve_ticker(query: str) -> str:
    """Convert company name or ticker to a valid ticker symbol."""
    q = query.strip().lower()
    if q in NAME_TO_TICKER:
        return NAME_TO_TICKER[q]
    return query.strip().upper()


def tracked_tickers() -> list[str]:
    raw = os.getenv("TRACKED_TICKERS", "")
    return [t.strip() for t in raw.split(",") if t.strip()]


@st.cache_data(ttl=60)
def get_ticker_info(ticker: str) -> dict:
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "price": info.get("currentPrice") or info.get("regularMarketPrice") or 0,
            "change_pct": info.get("regularMarketChangePercent") or 0,
            "market_cap": info.get("marketCap") or 0,
            "pe": info.get("trailingPE") or 0,
            "beta": info.get("beta") or 1.0,
            "dividend": (info.get("dividendYield") or 0) * 100,
            "profit_margin": (info.get("profitMargins") or 0) * 100,
            "debt_to_equity": info.get("debtToEquity") or 0,
            "revenue_growth": (info.get("revenueGrowth") or 0) * 100,
            "current_ratio": info.get("currentRatio") or 0,
            "description": info.get("longBusinessSummary") or "",
            "website": info.get("website") or "",
            "employees": info.get("fullTimeEmployees") or 0,
            "next_earnings": info.get("earningsDate") or None,
            "52w_high": info.get("fiftyTwoWeekHigh") or 0,
            "52w_low": info.get("fiftyTwoWeekLow") or 0,
        }
    except Exception:
        return {"ticker": ticker, "name": ticker, "price": 0, "change_pct": 0,
                "beta": 1.0, "dividend": 0, "profit_margin": 0, "sector": ""}


@st.cache_data(ttl=300)
def get_history(ticker: str, period: str = "1mo"):
    import yfinance as yf
    hist = yf.Ticker(ticker).history(period=period)
    if not hist.empty:
        hist.index = hist.index.tz_localize(None)
    return hist


@st.cache_data(ttl=300)
def get_news(ticker: str, limit: int = 5) -> list[dict]:
    try:
        import yfinance as yf
        items = yf.Ticker(ticker).news or []
        out = []
        for n in items[:limit]:
            content = n.get("content") or {}
            out.append({
                "title": content.get("title") or n.get("title", ""),
                "url": content.get("canonicalUrl", {}).get("url") or n.get("link") or n.get("url", ""),
                "source": (content.get("provider") or {}).get("displayName") or n.get("publisher", ""),
                "time": content.get("pubDate") or "",
            })
        return out
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_portfolio_history():
    """Fetch Alpaca portfolio equity history (30 days)."""
    try:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import GetPortfolioHistoryRequest
        import pandas as pd, os
        client = TradingClient(os.getenv("ALPACA_API_KEY",""), os.getenv("ALPACA_SECRET_KEY",""), paper=True)
        hist = client.get_portfolio_history(GetPortfolioHistoryRequest(period="1M", timeframe="1D"))
        df = pd.DataFrame({"timestamp": hist.timestamp, "equity": hist.equity})
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        return df
    except Exception:
        return None


def compute_health_score(info: dict) -> tuple[int, list[str], list[str]]:
    """Return (score 1-10, green_flags, red_flags)."""
    score = 5
    green, red = [], []

    pe = info.get("pe") or 0
    if 0 < pe < 20:
        score += 1; green.append(f"P/E of {pe:.0f} — fairly priced for what you get")
    elif pe > 50:
        score -= 1; red.append(f"P/E of {pe:.0f} — expensive, needs strong future growth")

    margin = info.get("profit_margin") or 0
    if margin > 15:
        score += 1; green.append(f"Keeps {margin:.0f}¢ profit from every $1 in sales")
    elif margin < 0:
        score -= 1; red.append("Company is losing money — expenses exceed revenue")

    de = info.get("debt_to_equity") or 0
    if de < 50:
        score += 1; green.append("Low debt — financially stable, not over-borrowed")
    elif de > 200:
        score -= 1; red.append("High debt — owes a lot, risky if business slows down")

    rg = info.get("revenue_growth") or 0
    if rg > 10:
        score += 1; green.append(f"Sales growing at {rg:.0f}% — business is expanding")
    elif rg < 0:
        score -= 1; red.append("Revenue shrinking — fewer sales than last year")

    cr = info.get("current_ratio") or 0
    if cr > 1.5:
        score += 1; green.append("Strong cash cushion — can pay near-term bills easily")
    elif 0 < cr < 1:
        score -= 1; red.append("Cash tight — may struggle to pay short-term debts")

    score = max(1, min(10, score))
    return score, green[:3], red[:3]


def risk_category(info: dict) -> str:
    """Return 'high', 'moderate', or 'low' based on beta."""
    beta = info.get("beta") or 1.0
    mkt_cap = info.get("market_cap") or 0
    if beta > 1.3 or mkt_cap < 5e9:
        return "high"
    if beta < 0.95:
        return "low"
    return "moderate"


def one_line_description(info: dict) -> str:
    """Return a 1-2 sentence plain English description (truncated)."""
    desc = info.get("description") or ""
    sentences = [s.strip() for s in desc.split(".") if len(s.strip()) > 20]
    return ". ".join(sentences[:2]) + "." if sentences else ""


def concept_of_day() -> tuple[str, str]:
    """Return (term, definition) based on today's date."""
    terms = list(GLOSSARY.keys())
    idx = datetime.date.today().toordinal() % len(terms)
    term = terms[idx]
    return term, GLOSSARY[term]


def format_price(v: float) -> str:
    return f"${v:,.2f}" if v else "N/A"


def format_mktcap(v: float) -> str:
    if v >= 1e12: return f"${v/1e12:.1f}T"
    if v >= 1e9:  return f"${v/1e9:.1f}B"
    if v >= 1e6:  return f"${v/1e6:.1f}M"
    return f"${v:,.0f}" if v else "N/A"
