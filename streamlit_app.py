"""Streamlit web interface for the Financial Intelligence System."""

import asyncio
import os
import sys
import threading
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

.page-header {
    background: linear-gradient(135deg, #1a2035 0%, #252d40 100%);
    border-left: 4px solid #4299e1;
    border-radius: 0 10px 10px 0;
    padding: 16px 24px;
    margin-bottom: 24px;
}
.page-header h2 { margin: 0; font-size: 1.4rem; color: #fafafa; }
.page-header p  { margin: 4px 0 0; color: #90a0b7; font-size: 0.9rem; }

.kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.kpi-label { color: #90a0b7; font-size: 0.78rem; text-transform: uppercase;
             letter-spacing: 0.06em; margin-bottom: 6px; }
.kpi-value { font-size: 1.7rem; font-weight: 700; color: #fafafa; }
.kpi-delta { font-size: 0.85rem; margin-top: 4px; }
.pos { color: #48bb78; }
.neg { color: #fc8181; }

.ticker-chip {
    display: inline-block;
    background: #1a2035;
    border: 1px solid #2d3748;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    color: #90a0b7;
    margin: 3px;
}
.ticker-chip b { color: #fafafa; }

.tool-badge {
    display: inline-block;
    background: #1c3a2a;
    border: 1px solid #2f6b48;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.78rem;
    color: #48bb78;
    margin: 2px;
}

.chat-bubble-user {
    background: #2a3550;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 6px 0 6px 15%;
    color: #fafafa;
    font-size: 0.93rem;
}
.chat-bubble-ai {
    background: #1a2035;
    border-left: 3px solid #4299e1;
    border-radius: 0 18px 18px 18px;
    padding: 12px 16px;
    margin: 6px 15% 6px 0;
    color: #fafafa;
    font-size: 0.93rem;
}

.indexed-badge {
    background: #1c3a2a;
    border: 1px solid #2f6b48;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.82rem;
    color: #48bb78;
    margin: 4px 0;
}

.lesson-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}

.upload-hint {
    color: #90a0b7;
    font-size: 0.85rem;
    text-align: center;
    margin-top: 8px;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.sidebar-logo {
    text-align: center;
    padding: 12px 0 20px;
}
.sidebar-logo h3 { color: #4299e1; margin: 0; font-size: 1.1rem; }
.sidebar-logo p  { color: #90a0b7; font-size: 0.78rem; margin: 2px 0 0; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []
if "_agent" not in st.session_state:
    st.session_state._agent = None
if "_mcp" not in st.session_state:
    st.session_state._mcp = None
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "quick"


# ── MCP persistent session ────────────────────────────────────────────────────

class _MCPSession:
    """Keeps all 6 MCP servers alive in a background thread across Streamlit reruns."""

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._agent = None
        self._cm = None
        self.tool_names: list[str] = []
        self._ready = threading.Event()
        self.error: str | None = None

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self._init(), self._loop)

        if not self._ready.wait(timeout=45):
            self.error = self.error or "MCP servers did not respond within 45 s"

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _init(self):
        from src.agents.orchestrator import _server_config, _get_llm, _get_system_prompt
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain.agents import create_agent
        try:
            self._cm = MultiServerMCPClient(_server_config())
            client = await self._cm.__aenter__()
            tools = client.get_tools()
            self.tool_names = [t.name for t in tools]
            self._agent = create_agent(
                _get_llm(), tools, system_prompt=_get_system_prompt()
            )
        except Exception as e:
            self.error = str(e)
        finally:
            self._ready.set()

    def ask(self, question: str, timeout: int = 120) -> str:
        from src.agents.orchestrator import _extract_answer
        from langchain_core.messages import HumanMessage

        async def _run():
            return _extract_answer(
                await self._agent.ainvoke({"messages": [HumanMessage(content=question)]})
            )

        future = asyncio.run_coroutine_threadsafe(_run(), self._loop)
        return future.result(timeout=timeout)

    def run_weekly_report(self, timeout: int = 180) -> str:
        from src.agents.orchestrator import _extract_answer
        from langchain_core.messages import HumanMessage

        prompt = (
            "Generate and send the weekly coach report. Do the following:\n"
            "1. Search documents indexed this week for key findings\n"
            "2. Get current prices for all tracked tickers\n"
            "3. Get the paper portfolio summary\n"
            "4. Identify 3 investment opportunities based on recent analysis\n"
            "5. Send the weekly coach report to the 'weekly' email group "
            "using send_weekly_coach_report\n"
            "Write everything in plain English suitable for a beginner investor."
        )

        async def _run():
            return _extract_answer(
                await self._agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
            )

        future = asyncio.run_coroutine_threadsafe(_run(), self._loop)
        return future.result(timeout=timeout)

    def cleanup(self):
        async def _stop():
            if self._cm:
                await self._cm.__aexit__(None, None, None)
        asyncio.run_coroutine_threadsafe(_stop(), self._loop).result(timeout=10)
        self._loop.call_soon_threadsafe(self._loop.stop)


def _get_mcp() -> _MCPSession | None:
    return st.session_state._mcp


def _start_mcp() -> _MCPSession:
    if st.session_state._mcp is not None:
        return st.session_state._mcp
    session = _MCPSession()
    st.session_state._mcp = session
    return session


# ── Quick RAG agent ───────────────────────────────────────────────────────────

def _agent():
    if st.session_state._agent is None:
        from src.agent import FinancialAnalyzerAgent
        st.session_state._agent = FinancialAnalyzerAgent()
    return st.session_state._agent


# ── Market helpers ────────────────────────────────────────────────────────────

def _tracked_tickers() -> list[str]:
    raw = os.getenv("TRACKED_TICKERS", "")
    return [t.strip() for t in raw.split(",") if t.strip()]


def _fetch_ticker_info(ticker: str) -> dict:
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("regularMarketPrice", 0) or 0
        change_pct = info.get("regularMarketChangePercent", 0) or 0
        name = info.get("shortName") or ticker
        return {"ticker": ticker, "name": name, "price": price, "change_pct": change_pct}
    except Exception:
        return {"ticker": ticker, "name": ticker, "price": 0, "change_pct": 0}


@st.cache_data(ttl=300)
def _fetch_history(ticker: str, period: str = "1mo"):
    import yfinance as yf
    hist = yf.Ticker(ticker).history(period=period)
    hist.index = hist.index.tz_localize(None)
    return hist


@st.cache_data(ttl=60)
def _fetch_portfolio():
    api_key = os.getenv("ALPACA_API_KEY", "")
    secret = os.getenv("ALPACA_SECRET_KEY", "")
    if not api_key or not secret:
        return None, None
    try:
        from alpaca.trading.client import TradingClient
        client = TradingClient(api_key, secret, paper=True)
        return client.get_account(), client.get_all_positions()
    except Exception as e:
        return None, str(e)


# ── Chart builders ────────────────────────────────────────────────────────────

def _make_line_chart(ticker: str, period: str):
    import plotly.graph_objects as go
    hist = _fetch_history(ticker, period)
    if hist.empty:
        return go.Figure()
    is_up = hist["Close"].iloc[-1] >= hist["Close"].iloc[0]
    color = "#48bb78" if is_up else "#fc8181"
    fill = "rgba(72,187,120,0.08)" if is_up else "rgba(252,129,129,0.08)"
    fig = go.Figure(go.Scatter(
        x=hist.index, y=hist["Close"], mode="lines",
        line=dict(color=color, width=2), fill="tozeroy", fillcolor=fill,
        hovertemplate="%{x|%b %d}<br>$%{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", plot_bgcolor="#1a2035", paper_bgcolor="#1a2035",
        margin=dict(l=8, r=8, t=8, b=8), height=180,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, tickformat="$,.0f", tickfont=dict(size=10)),
        showlegend=False,
    )
    return fig


def _make_portfolio_pie(positions):
    import plotly.graph_objects as go
    if not positions:
        return go.Figure()
    fig = go.Figure(go.Pie(
        labels=[p.symbol for p in positions],
        values=[abs(float(p.market_value)) for p in positions],
        hole=0.55,
        textinfo="label+percent",
        textfont=dict(size=12, color="#fafafa"),
        marker=dict(
            colors=["#4299e1","#48bb78","#ed8936","#9f7aea",
                    "#fc8181","#38b2ac","#f6e05e","#76e4f7"],
            line=dict(color="#0e1117", width=2),
        ),
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#1a2035", plot_bgcolor="#1a2035",
        margin=dict(l=0, r=0, t=0, b=0), height=280, showlegend=False,
    )
    return fig


def _make_pl_bar(positions):
    import plotly.graph_objects as go
    if not positions:
        return go.Figure()
    pls = [float(p.unrealized_pl) for p in positions]
    fig = go.Figure(go.Bar(
        x=[p.symbol for p in positions], y=pls,
        marker_color=["#48bb78" if v >= 0 else "#fc8181" for v in pls],
        text=[f"${v:+,.0f}" for v in pls], textposition="outside",
        textfont=dict(color="#fafafa", size=11),
        hovertemplate="%{x}<br>P&L: $%{y:+,.2f}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#1a2035", plot_bgcolor="#1a2035",
        margin=dict(l=8, r=8, t=8, b=8), height=240,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#2d3748", zeroline=True,
                   zerolinecolor="#4a5568", tickformat="$,.0f"),
        showlegend=False,
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <h3>📊 Financial Intelligence</h3>
      <p>RAG · Market · Trading · AI</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["🏠  Dashboard", "📄  Upload & Analyze", "💬  Chat with Reports",
         "📚  Learn Finance", "💼  Portfolio", "⚙️  Settings"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    tickers = _tracked_tickers()
    if tickers:
        st.markdown("**Tracked Tickers**")
        chips = "".join(f'<span class="ticker-chip"><b>{t}</b></span>' for t in tickers)
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.caption("No tickers configured yet.")

    st.markdown("---")

    indexed = st.session_state.indexed_files
    if indexed:
        st.markdown(f"**Indexed Documents** ({len(indexed)})")
        for f in indexed[-5:]:
            st.markdown(
                f'<div class="indexed-badge">✅ {Path(f).name}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No documents indexed yet.")

    mcp = _get_mcp()
    if mcp and not mcp.error:
        st.markdown("---")
        st.markdown(f"**MCP Agents** ({len(mcp.tool_names)} tools)")
        badges = "".join(
            f'<span class="tool-badge">{n}</span>' for n in mcp.tool_names
        )
        st.markdown(badges, unsafe_allow_html=True)

    if os.getenv("COACH_MODE", "off").strip().lower() == "on":
        st.markdown("---")
        st.markdown("🎓 **Coach Mode ON**")


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
    <div class="page-header">
      <h2>🏠 Market Dashboard</h2>
      <p>Live prices and performance for your tracked tickers</p>
    </div>
    """, unsafe_allow_html=True)

    tickers = _tracked_tickers()
    if not tickers:
        st.info("No tickers configured. Go to **Settings** to add your favorite stocks.")
        return

    period_choice = st.selectbox(
        "Chart period", ["1wk", "1mo", "3mo", "6mo", "1y"], index=1,
        label_visibility="collapsed",
    )

    with st.spinner("Fetching market data..."):
        infos = [_fetch_ticker_info(t) for t in tickers]

    cols = st.columns(min(len(tickers), 4))
    for i, info in enumerate(infos):
        with cols[i % len(cols)]:
            pct = info["change_pct"]
            sign = "+" if pct >= 0 else ""
            cls = "pos" if pct >= 0 else "neg"
            arrow = "▲" if pct >= 0 else "▼"
            price_str = f"${info['price']:,.2f}" if info["price"] else "N/A"
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">{info['ticker']} · {info['name'][:22]}</div>
              <div class="kpi-value">{price_str}</div>
              <div class="kpi-delta {cls}">{arrow} {sign}{pct:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for row_start in range(0, len(tickers), 2):
        chunk = tickers[row_start:row_start + 2]
        cols = st.columns(len(chunk))
        for col, ticker in zip(cols, chunk):
            with col:
                st.markdown(f"**{ticker}** — {period_choice} price history")
                try:
                    st.plotly_chart(
                        _make_line_chart(ticker, period_choice),
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )
                except Exception as e:
                    st.error(f"Could not load chart: {e}")


def page_upload():
    st.markdown("""
    <div class="page-header">
      <h2>📄 Upload & Analyze</h2>
      <p>Drag and drop financial reports to index them for AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop PDF or Excel files here",
        type=["pdf", "xlsx", "xls"],
        accept_multiple_files=True,
        help="Supports PDF and Excel financial reports",
    )
    st.markdown(
        '<p class="upload-hint">Supported: PDF, XLSX, XLS · Files are saved to data/raw/</p>',
        unsafe_allow_html=True,
    )

    if uploaded:
        if st.button("📥 Index Selected Files", type="primary"):
            raw_dir = Path("data/raw")
            raw_dir.mkdir(parents=True, exist_ok=True)
            progress = st.progress(0, text="Starting...")
            status = st.empty()
            agent = _agent()

            for i, f in enumerate(uploaded):
                dest = raw_dir / f.name
                dest.write_bytes(f.read())
                status.markdown(f"**Indexing** `{f.name}`...")
                try:
                    chunks = agent.index_report(str(dest))
                    if str(dest) not in st.session_state.indexed_files:
                        st.session_state.indexed_files.append(str(dest))
                    st.success(f"✅ {f.name} — {chunks} chunks indexed")
                except Exception as e:
                    st.error(f"❌ {f.name}: {e}")
                progress.progress((i + 1) / len(uploaded), text=f"{i+1}/{len(uploaded)} files done")

            status.empty()
            progress.empty()
            st.balloons()

    raw_dir = Path("data/raw")
    if raw_dir.exists():
        existing = sorted(raw_dir.glob("*.pdf")) + sorted(raw_dir.glob("*.xls*"))
        if existing:
            st.markdown("---")
            st.markdown("### Documents in data/raw/")
            for f in existing:
                size_kb = f.stat().st_size // 1024
                indexed = str(f) in st.session_state.indexed_files
                col1, col2, col3 = st.columns([5, 2, 2])
                col1.markdown(f"**{f.name}**")
                col2.markdown(f"`{size_kb} KB`")
                col3.markdown("✅ Indexed" if indexed else "⬜ Not indexed")
                if not indexed:
                    if st.button(f"Index {f.name}", key=f"idx_{f.name}"):
                        with st.spinner(f"Indexing {f.name}..."):
                            try:
                                chunks = _agent().index_report(str(f))
                                st.session_state.indexed_files.append(str(f))
                                st.success(f"{chunks} chunks indexed")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))


def page_chat():
    st.markdown("""
    <div class="page-header">
      <h2>💬 Chat with Your Reports</h2>
      <p>Ask questions — or let the full agent team search, trade, email and coach you</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode selector ────────────────────────────────────────────────────────
    col_mode, col_clear = st.columns([5, 1])
    with col_mode:
        mode = st.radio(
            "Agent mode",
            ["⚡ Quick (RAG only)", "🤖 Full MCP Agents (email · trading · market · coach)"],
            horizontal=True,
            key="mode_radio",
        )
    with col_clear:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    use_mcp = "MCP" in mode

    # ── MCP connection ───────────────────────────────────────────────────────
    mcp = None
    if use_mcp:
        mcp = _get_mcp()
        if mcp is None:
            st.info("Connecting to MCP agents... (first time takes ~15 s)")
            with st.spinner("Starting 6 MCP servers..."):
                try:
                    mcp = _start_mcp()
                except Exception as e:
                    st.error(f"MCP failed to start: {e}")
                    mcp = None

        if mcp and mcp.error:
            st.error(f"MCP error: {mcp.error}")
            mcp = None

        if mcp:
            badges = " ".join(
                f'<span class="tool-badge">{n}</span>' for n in mcp.tool_names
            )
            st.markdown(
                f"✅ **{len(mcp.tool_names)} tools active** — {badges}",
                unsafe_allow_html=True,
            )
            st.markdown("")

    if not st.session_state.indexed_files and not use_mcp:
        st.warning("No documents indexed yet. Go to **Upload & Analyze** to index some reports first.")

    # ── Render history ───────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input ────────────────────────────────────────────────────────────────
    placeholder = (
        "Ask anything — the agents will search reports, check live prices, simulate trades..."
        if use_mcp else "Ask about your indexed financial reports..."
    )
    user_input = st.chat_input(placeholder)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(
            f'<div class="chat-bubble-user">🧑 {user_input}</div>',
            unsafe_allow_html=True,
        )
        label = "Full agent team working..." if use_mcp else "Searching reports..."
        with st.spinner(label):
            try:
                if use_mcp and mcp:
                    answer = mcp.ask(user_input)
                else:
                    answer = _agent().ask(user_input)
            except Exception as e:
                answer = f"⚠️ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.markdown(
            f'<div class="chat-bubble-ai">🤖 {answer}</div>',
            unsafe_allow_html=True,
        )

    # ── Weekly report (MCP only) ─────────────────────────────────────────────
    if use_mcp and mcp:
        st.markdown("---")
        col_btn, col_info = st.columns([2, 5])
        with col_btn:
            send = st.button("📧 Send Weekly Coach Report", type="secondary")
        with col_info:
            st.caption(
                "Generates a personalised summary and emails it to everyone "
                "in your 'weekly' group. Requires email to be configured."
            )
        if send:
            with st.spinner("Generating and sending weekly report..."):
                try:
                    result = mcp.run_weekly_report()
                    st.success("Report sent!")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Suggested questions (empty state) ────────────────────────────────────
    if not st.session_state.messages:
        st.markdown("---")
        st.markdown("**Try asking:**")
        if use_mcp:
            suggestions = [
                "What is the current price of AAPL?",
                "Analyze apple_2025.pdf and give me a coach summary",
                "What are the latest news for NVDA?",
                "Simulate buying 5 shares of AAPL",
                "What is the revenue for the latest fiscal year?",
                "Send an alert email about today's market movement",
            ]
        else:
            suggestions = [
                "What is the revenue for the latest fiscal year?",
                "What are the key risk factors mentioned?",
                "Summarize the company's competitive position.",
                "What is the debt-to-equity ratio?",
                "What does management say about future growth?",
            ]
        cols = st.columns(2)
        for i, q in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(q, key=f"sugg_{i}"):
                    st.session_state.messages.append({"role": "user", "content": q})
                    with st.spinner("Thinking..."):
                        try:
                            answer = mcp.ask(q) if (use_mcp and mcp) else _agent().ask(q)
                        except Exception as e:
                            answer = f"⚠️ Error: {e}"
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()


def page_learn():
    from src.education import LESSONS

    st.markdown("""
    <div class="page-header">
      <h2>📚 Learn Finance</h2>
      <p>Six beginner-friendly lessons — read at your own pace</p>
    </div>
    """, unsafe_allow_html=True)

    lesson_titles = [f"{k}. {v['title']}" for k, v in LESSONS.items()]
    choice = st.selectbox("Choose a lesson", lesson_titles, label_visibility="collapsed")
    key = choice.split(".")[0].strip()
    lesson = LESSONS[key]

    st.markdown(f"""
    <div class="lesson-card">
      <h3 style="color:#4299e1; margin-top:0;">{lesson['title']}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(lesson["content"])

    st.markdown("---")
    st.markdown("**All lessons**")
    tabs = st.tabs([v["title"] for v in LESSONS.values()])
    for tab, (_, lesson_data) in zip(tabs, LESSONS.items()):
        with tab:
            st.markdown(lesson_data["content"])


def page_portfolio():
    st.markdown("""
    <div class="page-header">
      <h2>💼 Paper Portfolio</h2>
      <p>Alpaca paper trading — simulated positions with no real money</p>
    </div>
    """, unsafe_allow_html=True)

    if not os.getenv("ALPACA_API_KEY", ""):
        st.info(
            "Alpaca Paper Trading is not configured yet.\n\n"
            "Run `python main.py` → **Settings → Alpaca Paper Trading** to set up your free account."
        )
        return

    with st.spinner("Fetching portfolio..."):
        acct, positions = _fetch_portfolio()

    if isinstance(positions, str):
        st.error(f"Could not connect to Alpaca: {positions}")
        return

    if acct is None:
        st.error("Failed to load portfolio. Check your Alpaca API keys.")
        return

    equity = float(acct.equity)
    cash = float(acct.cash)
    last_equity = float(acct.last_equity)
    day_pl = equity - last_equity
    day_pl_pct = (day_pl / last_equity * 100) if last_equity else 0.0
    pl_class = "pos" if day_pl >= 0 else "neg"
    pl_arrow = "▲" if day_pl >= 0 else "▼"

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, delta, delta_cls in [
        (c1, "Portfolio Value", f"${float(acct.portfolio_value):,.2f}", "Total equity", ""),
        (c2, "Day P&L", f"${day_pl:+,.2f}", f"{pl_arrow} {day_pl_pct:+.2f}% today", pl_class),
        (c3, "Cash Available", f"${cash:,.2f}", "Uninvested", ""),
        (c4, "Buying Power", f"${float(acct.buying_power):,.2f}", "Available to trade", ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{val}</div>
              <div class="kpi-delta {delta_cls}" style="color:{'inherit' if not delta_cls else ''}">
                {delta}
              </div>
            </div>
            """, unsafe_allow_html=True)

    if not positions:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("No open positions yet. Use **Chat → Full MCP Agents** to simulate your first trade.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    col_pie, col_bar = st.columns(2)
    with col_pie:
        st.markdown("**Portfolio Allocation**")
        st.plotly_chart(_make_portfolio_pie(positions), use_container_width=True,
                        config={"displayModeBar": False})
    with col_bar:
        st.markdown("**Unrealized P&L by Position**")
        st.plotly_chart(_make_pl_bar(positions), use_container_width=True,
                        config={"displayModeBar": False})

    st.markdown("### Open Positions")
    for pos in positions:
        pl = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc) * 100
        pl_class = "pos" if pl >= 0 else "neg"
        pl_arrow = "▲" if pl >= 0 else "▼"
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 3])
        with c1:
            st.markdown(f"**{pos.symbol}**")
            st.caption(f"{float(pos.qty):g} shares")
        with c2:
            st.markdown(f"${float(pos.current_price):,.2f}")
            st.caption(f"avg ${float(pos.avg_entry_price):,.2f}")
        with c3:
            st.markdown(f"${float(pos.market_value):,.2f}")
            st.caption("market value")
        with c4:
            st.markdown(
                f'<span class="{pl_class}">{pl_arrow} ${pl:+,.2f}</span>',
                unsafe_allow_html=True,
            )
            st.caption(f"{pl_pct:+.2f}% return")
        with c5:
            try:
                hist = _fetch_history(pos.symbol, "1wk")
                if not hist.empty:
                    import plotly.graph_objects as go
                    fig = go.Figure(go.Scatter(
                        x=hist.index, y=hist["Close"], mode="lines",
                        line=dict(color="#48bb78" if pl >= 0 else "#fc8181", width=1.5),
                    ))
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0, r=0, t=0, b=0), height=50,
                        xaxis=dict(visible=False), yaxis=dict(visible=False),
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception:
                pass
        st.divider()

    if st.button("🔄 Refresh Portfolio"):
        _fetch_portfolio.clear()
        st.rerun()


def page_settings():
    st.markdown("""
    <div class="page-header">
      <h2>⚙️ Settings</h2>
      <p>Current configuration — edit via .env file or run the terminal app</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "To change settings, edit your `.env` file or run `python main.py` "
        "and go to **Settings** from the terminal menu."
    )

    def _mask(val: str) -> str:
        if not val:
            return "❌ Not set"
        return f"✅ `{'*' * 8}{val[-4:]}`"

    configs = {
        "Core": {
            "ANTHROPIC_API_KEY": _mask(os.getenv("ANTHROPIC_API_KEY", "")),
            "MODEL_ID": os.getenv("MODEL_ID", "claude-sonnet-4-6 (default)"),
            "COACH_MODE": os.getenv("COACH_MODE", "off"),
        },
        "Market Data": {
            "TRACKED_TICKERS": os.getenv("TRACKED_TICKERS", "Not set"),
            "NEWS_API_KEY": _mask(os.getenv("NEWS_API_KEY", "")),
        },
        "Alpaca Paper Trading": {
            "ALPACA_API_KEY": _mask(os.getenv("ALPACA_API_KEY", "")),
            "ALPACA_SECRET_KEY": _mask(os.getenv("ALPACA_SECRET_KEY", "")),
        },
        "Email (SMTP)": {
            "SMTP_HOST": os.getenv("SMTP_HOST", "Not set"),
            "SMTP_PORT": os.getenv("SMTP_PORT", "Not set"),
            "EMAIL_SENDER": os.getenv("EMAIL_SENDER", "Not set"),
        },
        "RAG / Vector Store": {
            "CHROMA_PERSIST_DIR": os.getenv("CHROMA_PERSIST_DIR", "data/vector_store"),
            "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            "CHUNK_SIZE": os.getenv("CHUNK_SIZE", "1000"),
            "TOP_K_RESULTS": os.getenv("TOP_K_RESULTS", "5"),
        },
    }

    for section, items in configs.items():
        st.markdown(f"### {section}")
        for key, val in items.items():
            col1, col2 = st.columns([3, 4])
            col1.markdown(f"`{key}`")
            col2.markdown(str(val))
        st.markdown("---")

    st.markdown("### Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Terminal app:** `python main.py`")
        st.markdown("**Run Streamlit:** `streamlit run streamlit_app.py`")
    with col2:
        st.markdown("**Config file:** `.env`")
        st.markdown("**Email groups:** `config/email_groups.yaml`")


# ── Router ────────────────────────────────────────────────────────────────────
if "Dashboard" in page:
    page_dashboard()
elif "Upload" in page:
    page_upload()
elif "Chat" in page:
    page_chat()
elif "Learn" in page:
    page_learn()
elif "Portfolio" in page:
    page_portfolio()
elif "Settings" in page:
    page_settings()
