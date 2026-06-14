"""Home — landing page with ticker bar, nav, opportunities, concept of day, news."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.theme import inject_css, section
from utils.market import (
    tracked_tickers, get_ticker_info, get_news,
    concept_of_day, risk_category, format_price, one_line_description,
)

st.set_page_config(
    page_title="Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()

# ── Additional home-page CSS ──────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="collapsedControl"] { display: none; }
.stApp > header { display: none; }
</style>""", unsafe_allow_html=True)


# ── Live Ticker Bar ───────────────────────────────────────────────────────────
@st.fragment(run_every=60)
def _ticker_bar():
    tickers = tracked_tickers()
    if not tickers:
        return
    pills = []
    for t in tickers:
        info = get_ticker_info(t)
        p = info["price"]; pct = info["change_pct"]
        cls = "t-up" if pct >= 0 else "t-dn"
        arrow = "▲" if pct >= 0 else "▼"
        sign  = "+" if pct >= 0 else ""
        pills.append(f"""
        <span class="ticker-pill">
          <span class="t-sym">{t}</span>
          <span class="t-price">{format_price(p)}</span>
          <span class="{cls}">{arrow}{sign}{pct:.2f}%</span>
        </span>""")
    live = '<span style="color:#8892a4;font-size:.72rem;letter-spacing:.06em;font-weight:700">LIVE&nbsp;</span>'
    st.markdown(f'<div class="ticker-bar">{live}{"".join(pills)}</div>', unsafe_allow_html=True)


_ticker_bar()

# ── App title ─────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-size:1.8rem;font-weight:800;color:#fff;margin:0 0 4px">
  📊 Financial Intelligence
</h1>
<p style="color:#8892a4;font-size:.9rem;margin:0 0 8px">
  Your personal investment coach — powered by Claude AI
</p>
""", unsafe_allow_html=True)

# ── Navigation Cards ──────────────────────────────────────────────────────────
# Style nav buttons to look like big emoji cards
st.markdown("""<style>
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"] .stButton > button {
    background: linear-gradient(145deg,#131720,#1a2035) !important;
    border: 2px solid #1e2d40 !important;
    border-radius: 20px !important;
    height: 110px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    font-size: .82rem !important;
    font-weight: 800 !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    color: #fff !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
    white-space: pre-line !important;
    line-height: 1.2 !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"] .stButton > button:hover {
    border-color: #00d4aa !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 32px rgba(0,212,170,.18) !important;
    color: #00d4aa !important;
}
</style>""", unsafe_allow_html=True)

nav_items = [
    ("🔍", "Discover",   "pages/1_Discover.py"),
    ("💼", "Portfolio",  "pages/2_Portfolio.py"),
    ("📧", "Share",      "pages/3_Share.py"),
    ("🎓", "Learn",      "pages/4_Learn.py"),
    ("⚙️", "Settings",  "pages/5_Settings.py"),
]

cols = st.columns(5, gap="small")
for col, (emoji, label, path) in zip(cols, nav_items):
    with col:
        if st.button(f"{emoji}\n{label}", key=f"nav_{label}",
                     use_container_width=True, help=f"Go to {label}"):
            st.switch_page(path)

# ── Investment Opportunities ──────────────────────────────────────────────────
section("💡 Investment Opportunities Today")

tickers = tracked_tickers()
if not tickers:
    st.info("Add tickers in **Settings → Tracked Tickers** to see opportunities.")
else:
    # Bucket tickers by risk category
    all_infos = [get_ticker_info(t) for t in tickers]
    buckets: dict[str, list] = {"high": [], "moderate": [], "low": []}
    for info in all_infos:
        buckets[risk_category(info)].append(info)

    # Fallback: if a bucket is empty, fill it with the closest match
    if not buckets["low"] and all_infos:
        buckets["low"] = [min(all_infos, key=lambda x: x.get("beta") or 1.0)]
    if not buckets["high"] and all_infos:
        buckets["high"] = [max(all_infos, key=lambda x: x.get("beta") or 1.0)]
    if not buckets["moderate"] and all_infos:
        used = {buckets["low"][0]["ticker"], buckets["high"][0]["ticker"]}
        rest = [i for i in all_infos if i["ticker"] not in used]
        if rest:
            buckets["moderate"] = [rest[0]]

    risk_cfg = {
        "high":     ("🔴", "High Risk · High Reward", "#ff4757",
                     "More volatile — bigger swings up AND down."),
        "moderate": ("🟡", "Moderate Risk",            "#ffc107",
                     "Balanced option — not too wild, not too boring."),
        "low":      ("🟢", "Low Risk · Stable",        "#00d4aa",
                     "Steady performer — lower reward but fewer surprises."),
    }

    opp_cols = st.columns(3, gap="small")
    for col, (cat, (icon, label, color, default_why)) in zip(opp_cols, risk_cfg.items()):
        with col:
            pool = buckets[cat]
            if pool:
                info = pool[0]
                pct   = info["change_pct"]
                arrow = "▲" if pct >= 0 else "▼"
                pct_c = "#00d4aa" if pct >= 0 else "#ff4757"
                why   = one_line_description(info) or default_why
                if len(why) > 110: why = why[:107] + "…"
                st.markdown(f"""
                <div class="opp-card">
                  <div class="opp-bar" style="background:{color}"></div>
                  <div class="risk-lbl" style="color:{color}">{icon} {label}</div>
                  <div class="opp-name">{info['name']}</div>
                  <div class="opp-price">
                    {format_price(info['price'])}
                    &nbsp;<span style="color:{pct_c}">{arrow} {pct:+.2f}%</span>
                  </div>
                  <div class="opp-why">{why}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Analyze {info['ticker']} →", key=f"opp_{cat}",
                             use_container_width=True):
                    st.session_state["discover_prefill"] = info["ticker"]
                    st.switch_page("pages/1_Discover.py")
            else:
                st.markdown(f"""
                <div class="opp-card">
                  <div class="opp-bar" style="background:{color}"></div>
                  <div class="risk-lbl" style="color:{color}">{icon} {label}</div>
                  <div class="opp-why" style="margin-top:16px">
                    Add more tickers in Settings to see {label.lower()} picks.
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ── Concept of the Day ────────────────────────────────────────────────────────
section("🧠 Concept of the Day")
term, definition = concept_of_day()
st.markdown(f"""
<div class="concept">
  <div class="concept-term">💡 {term}</div>
  <div class="concept-def">{definition}</div>
</div>
""", unsafe_allow_html=True)

# ── News Feed ─────────────────────────────────────────────────────────────────
if tickers:
    section("📰 Latest News")
    news_cols = st.columns(min(len(tickers), 3), gap="small")
    for col, t in zip(news_cols, tickers[:3]):
        with col:
            st.markdown(f"**{t}**")
            articles = get_news(t, limit=3)
            if articles:
                for a in articles:
                    title = a.get("title") or ""
                    url   = a.get("url") or "#"
                    src   = a.get("source") or ""
                    if title:
                        st.markdown(f"""
                        <div class="news-item">
                          <div class="news-title">
                            <a href="{url}" target="_blank"
                               style="color:#fff;text-decoration:none">{title}</a>
                          </div>
                          <div class="news-meta">{src}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.caption("No recent news found.")
