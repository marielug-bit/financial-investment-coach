# Financial Investment Coach

A multi-agent investment companion for beginner investors — powered by Claude AI + MCP.
Analyzes stocks, tracks your portfolio, explains financial concepts in plain English, and sends personalized reports by email.

---

## What it does

- **Smart daily picks** — scores 120 stocks every morning on health + momentum, shows the 3 best opportunities
- **Stock analysis** — type any company name or ticker, get an instant AI-powered health score (1–10), price chart, flags, and a verdict (INVEST / WAIT / AVOID)
- **RAG chat** — upload a company PDF report and ask questions in plain English
- **Paper portfolio** — practice buying stocks with fake money via Alpaca (no real money ever)
- **Email sharing** — send analysis summaries or a full weekly coach report to your contacts
- **Finance lessons** — 6 interactive lessons with quizzes, glossary, and progress tracking
- **Coach Mode** — toggle beginner-friendly explanations for every AI response

---

## Project Structure

```
financial-investment-coach/
│
├── streamlit_app.py          # Home page — smart picks, news, concept of the day
│
├── pages/
│   ├── 1_Discover.py         # Stock analysis + RAG chat
│   ├── 2_Portfolio.py        # Alpaca paper trading dashboard
│   ├── 3_Share.py            # Send analysis by email
│   ├── 4_Learn.py            # Finance lessons + quiz
│   └── 5_Settings.py         # API keys, tickers, email groups, Coach Mode
│
├── utils/
│   ├── theme.py              # Global CSS and UI components
│   ├── market.py             # Market data, health score, smart opportunity picker
│   └── mcp_session.py        # Keeps MCP agents alive across Streamlit reruns
│
├── src/
│   ├── rag/
│   │   ├── ingestion.py      # PDF → chunks
│   │   ├── retrieval.py      # ChromaDB vector search
│   │   ├── agent.py          # Direct RAG agent (Discover chat)
│   │   └── rag_server.py     # RAG exposed as MCP tool
│   │
│   └── agents/
│       ├── orchestrator.py   # LangGraph orchestrator — connects all agents
│       ├── analysis_server.py
│       ├── coach_server.py
│       ├── email_server.py
│       ├── market_server.py
│       └── trading_server.py
│
├── config/
│   └── email_groups.yaml     # Email recipient groups
│
├── data/
│   ├── raw/                  # Drop PDF reports here
│   └── vector_store/         # ChromaDB database
│
├── .env                      # API keys (never committed)
└── .streamlit/
    └── config.toml           # App theme and colors
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

Create a `.env` file at the project root with:

```
ANTHROPIC_API_KEY=your_key_here
MODEL_ID=claude-sonnet-4-6

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password

TRACKED_TICKERS=AAPL,NVDA,MSFT,TSLA
COACH_MODE=on

ALPACA_API_KEY=your_paper_key
ALPACA_SECRET_KEY=your_paper_secret

CHROMA_PERSIST_DIR=data/vector_store
COLLECTION_NAME=financial_reports
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### 3. Run

```bash
streamlit run streamlit_app.py
```

---

## Alpaca Paper Trading

Practice investing with **fake money** — completely safe, nothing real.

1. Create a free account at [alpaca.markets](https://alpaca.markets)
2. Switch to **Paper Trading** mode in the dashboard
3. Generate API keys under Paper Trading
4. Add them to `.env` as `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`
5. Test the connection in **Settings → Alpaca Paper Trading**

---

## Email Groups

Configured in `config/email_groups.yaml` and manageable from **Settings → Email Groups**.

| Group | Purpose |
|---|---|
| `me` | Personal reports and trade confirmations |
| `weekly` | Weekly coach report |
| `management` | Team or family group |

---

## Coach Mode

Toggle in **Settings → Coach Mode** or set `COACH_MODE=on` in `.env`.

| Mode | Behavior |
|---|---|
| **ON** | Plain English, every term explained with analogies, encouraging tone |
| **OFF** | Concise, data-focused responses |

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Claude (Anthropic) |
| Agent framework | LangGraph + `langchain-mcp-adapters` |
| Inter-agent protocol | MCP (FastMCP) |
| Vector store | ChromaDB + SentenceTransformers |
| Document processing | pdfplumber |
| Market data | yfinance |
| Paper trading | alpaca-py |
| Email | smtplib (SMTP) |
| Frontend | Streamlit 1.58+ |
| Charts | Plotly |
