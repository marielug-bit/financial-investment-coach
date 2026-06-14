# Financial Intelligence System — Personal Financial Coach

A multi-agent RAG application that analyzes financial reports, tracks markets, and coaches beginner investors — all powered by Claude + MCP.

## Features

### Core (original)
- Ingest PDF and Excel financial reports into a vector store (ChromaDB)
- Natural language Q&A over indexed reports
- Live stock prices, financial statements, and news via yfinance and NewsAPI
- Email reports and alerts to configured groups via SMTP

### New — Financial Coach
- **Coach Mode**: toggle beginner-friendly language — every term explained with everyday analogies
- **Coach Report**: after every document analysis, get a plain-English summary with financial health score 1-10, 3 green flags, 3 red flags, invest/wait/avoid verdict, and an ASCII dashboard
- **5-Agent Pipeline**: Document Analyst → Market Analyst → Coach → Reporter → Trader
- **Paper Trading**: simulate buying stocks on Alpaca with fake money — no real money ever involved
- **Learn Finance**: 6 interactive mini-lessons covering the basics of investing
- **Weekly Coach Report**: generated on-demand (or via cron), emailed to your `weekly` group
- **Beginner Onboarding**: guided first-launch tutorial

---

## Project Structure

```
financial_analyzer/
├── src/
│   ├── agents/
│   │   └── orchestrator.py      # 6-server LangGraph agent, Coach/Advanced modes
│   ├── mcp_servers/
│   │   ├── rag_server.py        # Agent 1 — Document Analyst
│   │   ├── market_server.py     # Agent 2 — Market Analyst
│   │   ├── coach_server.py      # Agent 3 — Coach (plain English translations)
│   │   ├── email_server.py      # Agent 4 — Reporter (email groups)
│   │   ├── analysis_server.py   # Deep analysis + coach report generator
│   │   └── trading_server.py    # Agent 5 — Trader (Alpaca paper trading)
│   ├── education.py             # 6 finance mini-lessons
│   ├── ingestion.py             # PDF/Excel loading and chunking
│   ├── retrieval.py             # ChromaDB vector store
│   ├── setup_wizard.py          # First-run and settings configuration
│   └── agent.py                 # Original RAG agent (kept for compatibility)
├── config/
│   └── email_groups.yaml        # me / alerts / weekly / management / ...
├── data/
│   ├── raw/                     # Drop your PDF/Excel files here
│   ├── processed/               # Intermediate artifacts
│   └── vector_store/            # ChromaDB persistence
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `ANTHROPIC_API_KEY` — get one at console.anthropic.com
- `SMTP_USER` / `SMTP_PASSWORD` — for email reports
- `TRACKED_TICKERS` — stocks to monitor (e.g., `AAPL,MSFT,NVDA`)
- `NEWS_API_KEY` — optional, free at newsapi.org
- `COACH_MODE` — `on` for beginner-friendly mode, `off` for advanced

### 3. Run the app

```bash
python main.py
```

On first launch, the setup wizard runs automatically, followed by an optional guided tour.

---

## Alpaca Paper Trading Setup

Paper trading lets you practice buying and selling stocks with **fake money**. Nothing is real — it's a safe sandbox.

**Step 1:** Go to [alpaca.markets](https://alpaca.markets) and create a free account.

**Step 2:** In the Alpaca dashboard, switch to **Paper Trading** mode (toggle in the top navigation).

**Step 3:** Go to **API Keys** → generate a new key pair under Paper Trading.

**Step 4:** Add them to your `.env` file:
```
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret_key
```

**Step 5:** In the app, go to **Settings → Alpaca Paper Trading** to verify the connection, or use **My Paper Portfolio** from the main menu.

> ⚠️ These are PAPER trading keys only. Real-money trading is never used by this app.

---

## Email Groups

Configured in `config/email_groups.yaml`:

| Group | Purpose |
|---|---|
| `me` | Personal reports and trade confirmations |
| `alerts` | Urgent signals — big price drops, strong buy opportunities |
| `weekly` | Weekly coach report (every Monday, or trigger manually) |
| `management` | Existing group |

Manage groups from **Settings → Email Groups** or edit the YAML directly.

---

## Weekly Coach Report (automated)

To send the weekly report manually: choose **Send Weekly Coach Report** from the main menu.

To automate it every Monday at 8am, add a cron job:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path to your project):
0 8 * * 1 cd /path/to/financial_analyzer && .venv/bin/python -c "
import asyncio
from src.agents.orchestrator import run_weekly_report_session
asyncio.run(run_weekly_report_session())
"
```

---

## Coach Mode

Toggle in **Settings → Coach Mode** or set `COACH_MODE=on` in `.env`.

| Mode | Behavior |
|---|---|
| **ON** | Plain English, every term explained with an analogy, encouraging tone |
| **OFF** | Full advanced analysis, technical language, original mode |

Coach Mode affects both the agent's responses and which system prompt is used.

---

## Learn Finance — Mini Lessons

Access from **Learn Finance** in the main menu:

1. What is a Balance Sheet?
2. How to Read an Income Statement
3. What Makes a Good Investment?
4. The 5 Key Numbers to Always Check
5. What is a Stock and How Does Buying One Work?
6. How to Read Market News Without Panicking

---

## Running Tests

```bash
pytest tests/
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Claude (Anthropic) via `langchain-anthropic` |
| Agent framework | LangGraph `create_react_agent` |
| Inter-agent communication | MCP (FastMCP) + `langchain-mcp-adapters` |
| Vector store | ChromaDB + SentenceTransformers |
| Document processing | pdfplumber, openpyxl |
| Market data | yfinance |
| News | newsapi-python |
| Paper trading | alpaca-py |
| Email | SMTP (smtplib) |
| CLI | rich |
