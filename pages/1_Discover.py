"""Discover — Search & analyze any company."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.theme import inject_css, section, kpi, verdict_badge
from utils.market import (
    resolve_ticker, get_ticker_info, get_history, get_news,
    compute_health_score, format_price, format_mktcap, one_line_description,
)

st.set_page_config(page_title="Discover · Financial Intelligence",
                   page_icon="🔍", layout="wide")
inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h3>📊 Financial Intelligence</h3></div>',
                unsafe_allow_html=True)
    st.page_link("streamlit_app.py",  label="🏠 Home")
    st.page_link("pages/1_Discover.py",  label="🔍 Discover", disabled=True)
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio")
    st.page_link("pages/3_Share.py",     label="📧 Share")
    st.page_link("pages/4_Learn.py",     label="🎓 Learn")
    st.page_link("pages/5_Settings.py",  label="⚙️ Settings")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px">
  🔍 Discover Any Company
</h1>
<p style="color:#8892a4;font-size:.88rem;margin:0 0 20px">
  Type a company name or ticker — get instant AI-powered analysis
</p>
""", unsafe_allow_html=True)

# ── Search bar ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("discover_prefill", "")
col_s, col_b = st.columns([5, 1])
with col_s:
    query = st.text_input("", placeholder="Apple, NVDA, Tesla, Microsoft…",
                          value=prefill, label_visibility="collapsed")
with col_b:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("Analyze →", type="primary", use_container_width=True)

compare_mode = st.checkbox("📊 Compare with another company")
query2 = ""
if compare_mode:
    query2 = st.text_input("", placeholder="Second company…",
                            label_visibility="collapsed", key="q2")

if not query and not search:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#8892a4;">
      <div style="font-size:3rem">🔍</div>
      <div style="margin-top:12px;font-size:1rem">Search for any company above to get started</div>
      <div style="font-size:.82rem;margin-top:6px">Examples: Apple · NVDA · Tesla · Microsoft</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

ticker = resolve_ticker(query)

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner(f"Loading {ticker}…"):
    info = get_ticker_info(ticker)
    hist = get_history(ticker, "1y")

if not info.get("price"):
    st.error(f"Could not find data for **{ticker}**. Try the ticker symbol directly (e.g. AAPL).")
    st.stop()

score, green_flags, red_flags = compute_health_score(info)
pct = info["change_pct"]
pct_color = "#00d4aa" if pct >= 0 else "#ff4757"
arrow = "▲" if pct >= 0 else "▼"

# ── Company Header ────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    sector_txt = f" · {info['sector']}" if info.get("sector") else ""
    st.markdown(f"""
    <div class="company-header">
      <div class="co-name">{info['name']}</div>
      <div class="co-sector">{ticker}{sector_txt}</div>
      <div class="co-price">
        {format_price(info['price'])}
        &nbsp;<span style="color:{pct_color};font-size:1rem">
          {arrow} {pct:+.2f}% today
        </span>
      </div>
      <div class="co-desc">{one_line_description(info) or "No description available."}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI row
    mc  = format_mktcap(info.get("market_cap", 0))
    pe  = f"{info['pe']:.1f}x" if info.get("pe") else "N/A"
    div = f"{info['dividend']:.2f}%" if info.get("dividend") else "None"
    emp = f"{info.get('employees',0):,}" if info.get("employees") else "N/A"
    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Market Cap", mc, "Total company value")
    with k2: kpi("P/E Ratio", pe, "Price ÷ earnings per share")
    with k3: kpi("Dividend", div, "Annual cash paid per share")
    with k4: kpi("Employees", emp, "Full-time staff worldwide")

with right:
    # Health Score Gauge
    import plotly.graph_objects as go
    score_color = "#00d4aa" if score >= 7 else ("#ffc107" if score >= 4 else "#ff4757")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 40, "color": "#fff"}},
        domain={"x": [0,1], "y": [0,1]},
        gauge={
            "axis": {"range": [0,10], "tickfont": {"color": "#8892a4"}, "tickwidth": 1},
            "bar": {"color": score_color, "thickness": 0.3},
            "bgcolor": "#1e2d40",
            "borderwidth": 0,
            "steps": [
                {"range": [0,3],  "color": "rgba(255,71,87,.12)"},
                {"range": [3,6],  "color": "rgba(255,193,7,.12)"},
                {"range": [6,10], "color": "rgba(0,212,170,.12)"},
            ],
        },
        title={"text": "Financial Health", "font": {"color": "#8892a4", "size": 13}},
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#131720", height=200,
        margin=dict(l=16, r=16, t=40, b=8),
        font={"family": "sans-serif"},
    )
    st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # Flags
    for g in green_flags:
        st.markdown(f'<div class="flag-row" style="display:flex;gap:6px;margin:4px 0;font-size:.82rem;color:#c5cdd8">✅ {g}</div>', unsafe_allow_html=True)
    for r in red_flags:
        st.markdown(f'<div class="flag-row" style="display:flex;gap:6px;margin:4px 0;font-size:.82rem;color:#c5cdd8">❌ {r}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Verdict
    if score >= 7:
        v, expl = "INVEST", "Strong fundamentals. Worth a closer look."
    elif score >= 4:
        v, expl = "WAIT", "Mixed signals. Monitor before committing."
    else:
        v, expl = "AVOID", "Weak fundamentals right now. Proceed with caution."
    verdict_badge(v)
    st.markdown(f'<p style="color:#8892a4;font-size:.8rem;margin:8px 0 0">{expl}</p>',
                unsafe_allow_html=True)

# ── Price Chart ───────────────────────────────────────────────────────────────
section("📈 Price History")
period_map = {"1 Week":"1wk","1 Month":"1mo","3 Months":"3mo","6 Months":"6mo","1 Year":"1y","5 Years":"5y"}
p_label = st.select_slider("", list(period_map.keys()), value="1 Year",
                            label_visibility="collapsed")
period = period_map[p_label]

hist = get_history(ticker, period)
ticker2 = resolve_ticker(query2) if compare_mode and query2 else None
hist2 = get_history(ticker2, period) if ticker2 else None

if not hist.empty:
    fig = go.Figure()
    is_up = hist["Close"].iloc[-1] >= hist["Close"].iloc[0]
    clr = "#00d4aa" if is_up else "#ff4757"
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["Close"], name=ticker,
        line=dict(color=clr, width=2),
        fill="tozeroy", fillcolor=f"rgba({'0,212,170' if is_up else '255,71,87'},.07)",
        hovertemplate="%{x|%b %d, %Y}<br><b>$%{y:,.2f}</b><extra></extra>",
    ))
    if hist2 is not None and not hist2.empty:
        fig.add_trace(go.Scatter(
            x=hist2.index, y=hist2["Close"], name=ticker2,
            line=dict(color="#ffc107", width=2, dash="dot"),
            hovertemplate="%{x|%b %d}<br><b>$%{y:,.2f}</b><extra></extra>",
        ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#131720", plot_bgcolor="#131720",
        margin=dict(l=8,r=8,t=8,b=8), height=300,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1e2d40", tickformat="$,.0f"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("No price history available.")

# ── Extra Insights ────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2, gap="large")

with col_a:
    section("📰 Recent News")
    articles = get_news(ticker, limit=5)
    if articles:
        for a in articles:
            title = a.get("title",""); url = a.get("url","#"); src = a.get("source","")
            if title:
                st.markdown(f"""
                <div class="news-item">
                  <div class="news-title">
                    <a href="{url}" target="_blank" style="color:#fff;text-decoration:none">{title}</a>
                  </div>
                  <div class="news-meta">{src}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("No recent news found.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💡 Why did it move today?", use_container_width=True):
        with st.spinner("Checking the news…"):
            news_summary = "; ".join(a.get("title","") for a in articles[:3] if a.get("title"))
            prompt = (f"In 2 plain English sentences, why might {info['name']} ({ticker}) "
                      f"stock have moved today? Recent headlines: {news_summary}. "
                      "If no clear reason, say so simply.")
            try:
                from src.agent import FinancialAnalyzerAgent
                if "_rag_agent" not in st.session_state:
                    st.session_state._rag_agent = FinancialAnalyzerAgent()
                agent = st.session_state._rag_agent
                ans = agent.ask(prompt)
                st.info(ans)
            except Exception as e:
                st.error(f"Agent error: {e}")

with col_b:
    section("🔔 Price Alert")
    h52  = info.get("52w_high", 0); l52 = info.get("52w_low", 0)
    cur  = info.get("price", 0)
    if h52 and l52:
        st.markdown(f"""
        <div style="display:flex;gap:24px;margin-bottom:16px">
          <div><span style="color:#8892a4;font-size:.72rem">52W HIGH</span><br>
               <span style="color:#00d4aa;font-weight:700">{format_price(h52)}</span></div>
          <div><span style="color:#8892a4;font-size:.72rem">52W LOW</span><br>
               <span style="color:#ff4757;font-weight:700">{format_price(l52)}</span></div>
          <div><span style="color:#8892a4;font-size:.72rem">CURRENT</span><br>
               <span style="color:#fff;font-weight:700">{format_price(cur)}</span></div>
        </div>
        """, unsafe_allow_html=True)

    alert_price = st.number_input(
        f"Alert me by email when {ticker} drops below ($)",
        min_value=0.0, value=round(cur * 0.9, 2) if cur else 0.0, step=1.0,
    )
    alert_email = st.text_input("Your email", placeholder="you@email.com",
                                value=os.getenv("SMTP_USER",""))
    if st.button("🔔 Set Alert", type="primary", use_container_width=True):
        if cur and alert_price >= cur:
            st.warning("Alert price must be BELOW the current price.")
        else:
            st.session_state.setdefault("price_alerts", []).append(
                {"ticker": ticker, "price": alert_price, "email": alert_email}
            )
            st.success(f"✅ Alert set! You'll be emailed if {ticker} drops below {format_price(alert_price)}.")
            st.caption("Note: alerts are checked each time the Home page loads while the app is running.")

# ── Deepen with PDF ───────────────────────────────────────────────────────────
section("📄 Deepen Analysis — Upload a Financial Report")
uploaded = st.file_uploader("Drop a PDF or Excel report here",
                             type=["pdf","xlsx","xls"],
                             label_visibility="collapsed")
if uploaded:
    from pathlib import Path as P
    raw = P("data/raw"); raw.mkdir(parents=True, exist_ok=True)
    dest = raw / uploaded.name
    dest.write_bytes(uploaded.read())
    with st.spinner(f"Indexing {uploaded.name}…"):
        try:
            from src.agent import FinancialAnalyzerAgent
            if "_rag_agent" not in st.session_state:
                st.session_state._rag_agent = FinancialAnalyzerAgent()
            ag = st.session_state._rag_agent
            chunks = ag.index_report(str(dest))
            if str(dest) not in st.session_state.get("indexed_files", []):
                st.session_state.setdefault("indexed_files", []).append(str(dest))
            st.success(f"✅ {uploaded.name} indexed — {chunks} chunks ready for questions.")
        except Exception as e:
            st.error(f"Indexing error: {e}")

# ── Chat ──────────────────────────────────────────────────────────────────────
section("💬 Ask Anything About This Company")

if "discover_messages" not in st.session_state:
    st.session_state.discover_messages = []

for msg in st.session_state.discover_messages:
    css = "chat-u" if msg["role"] == "user" else "chat-a"
    icon = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>',
                unsafe_allow_html=True)

user_q = st.chat_input(f"Ask anything about {info['name']}…")
if user_q:
    full_q = f"About {info['name']} ({ticker}): {user_q}"
    st.session_state.discover_messages.append({"role":"user","content":user_q})
    st.markdown(f'<div class="chat-u">🧑 {user_q}</div>', unsafe_allow_html=True)
    with st.spinner("AI is thinking…"):
        try:
            from src.agent import FinancialAnalyzerAgent
            if "_rag_agent" not in st.session_state:
                st.session_state._rag_agent = FinancialAnalyzerAgent()
            ans = st.session_state._rag_agent.ask(full_q)
        except Exception as e:
            ans = f"Error: {e}"
    st.session_state.discover_messages.append({"role":"assistant","content":ans})
    st.markdown(f'<div class="chat-a">🤖 {ans}</div>', unsafe_allow_html=True)

# ── Share Button ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("📧 Share This Analysis →", type="secondary", use_container_width=True):
    st.session_state["share_prefill"] = {
        "company": info["name"],
        "ticker": ticker,
        "verdict": v if "v" in dir() else "WAIT",
        "score": score,
        "analysis": f"{info['name']} ({ticker}) — Health Score {score}/10 — Verdict: {v if 'v' in dir() else 'WAIT'}.\n"
                    + "\n".join([f"✅ {g}" for g in green_flags] + [f"❌ {r}" for r in red_flags]),
    }
    st.switch_page("pages/3_Share.py")
