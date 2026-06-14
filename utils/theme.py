"""Global CSS, design tokens, and shared UI helpers."""
import streamlit as st

TEAL   = "#00d4aa"
RED    = "#ff4757"
YELLOW = "#ffc107"
BG     = "#0e1117"
CARD   = "#131720"
BORDER = "#1e2d40"
TEXT   = "#ffffff"
MUTED  = "#8892a4"

CSS = """
/* ── Reset ─────────────────────────────────────────────────── */
#MainMenu, footer { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding: 1.2rem 1.5rem 3rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: #0c0f1a !important; border-right: 1px solid #1e2d40; }

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    background: #1a2035; border: 1px solid #1e2d40; color: #fff;
    border-radius: 10px; font-weight: 600;
    transition: all .2s ease; min-height: 44px;
}
.stButton > button:hover { border-color: #00d4aa; color: #00d4aa; }
[data-testid="baseButton-primary"] {
    background: #00d4aa !important; border-color: #00d4aa !important;
    color: #0e1117 !important; font-weight: 700 !important;
}
[data-testid="baseButton-primary"]:hover { background: #00bfa0 !important; }
[data-testid="baseButton-secondary"] {
    background: transparent !important; border: 1px solid #00d4aa !important;
    color: #00d4aa !important;
}

/* ── Nav Cards ───────────────────────────────────────────────── */
.nav-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin: 24px 0; }
.nav-card {
    background: linear-gradient(145deg,#131720,#1a2035);
    border: 2px solid #1e2d40; border-radius: 20px;
    padding: 32px 12px; text-align: center; cursor: pointer;
    transition: all .25s cubic-bezier(.4,0,.2,1);
    text-decoration: none; display: block;
}
.nav-card:hover {
    border-color: #00d4aa; transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,212,170,.18);
}
.nav-emoji { font-size: 2.4rem; line-height: 1; display: block; }
.nav-label {
    color: #fff; font-size: .82rem; font-weight: 800;
    letter-spacing: .08em; text-transform: uppercase;
    margin-top: 10px; display: block;
}
@media (max-width: 640px) {
    .nav-grid { grid-template-columns: repeat(3,1fr); }
}

/* ── Ticker Bar ──────────────────────────────────────────────── */
.ticker-bar {
    background: #0c0f1a; border: 1px solid #1e2d40; border-radius: 12px;
    padding: 10px 16px; display: flex; flex-wrap: wrap; gap: 8px;
    align-items: center; margin-bottom: 20px;
}
.ticker-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #131720; border: 1px solid #1e2d40;
    border-radius: 999px; padding: 4px 14px; font-size: .84rem;
}
.t-sym { color: #fff; font-weight: 700; }
.t-price { color: #8892a4; }
.t-up { color: #00d4aa; }
.t-dn { color: #ff4757; }

/* ── Section Header ──────────────────────────────────────────── */
.section-hdr {
    color: #8892a4; font-size: .7rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: .1em;
    margin: 28px 0 14px; padding-bottom: 8px;
    border-bottom: 1px solid #1e2d40;
}

/* ── KPI Card ────────────────────────────────────────────────── */
.kpi {
    background: #131720; border: 1px solid #1e2d40; border-radius: 16px;
    padding: 18px 20px; text-align: center;
}
.kpi-lbl { color: #8892a4; font-size: .7rem; text-transform: uppercase; letter-spacing: .07em; }
.kpi-val { color: #fff; font-size: 1.7rem; font-weight: 800; margin: 4px 0; }
.kpi-d   { font-size: .84rem; }
.pos { color: #00d4aa; }
.neg { color: #ff4757; }
.neu { color: #8892a4; }

/* ── Opportunity Card ────────────────────────────────────────── */
.opp-card {
    background: #131720; border: 1px solid #1e2d40; border-radius: 16px;
    padding: 20px; position: relative; overflow: hidden; height: 100%;
}
.opp-bar { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.opp-name { color: #fff; font-size: 1rem; font-weight: 700; margin: 8px 0 2px; }
.opp-price { color: #8892a4; font-size: .85rem; }
.opp-why { color: #c5cdd8; font-size: .82rem; line-height: 1.5; margin: 10px 0; }
.risk-lbl { font-size: .7rem; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }

/* ── Concept of Day ──────────────────────────────────────────── */
.concept {
    background: linear-gradient(135deg,#0d2e26,#132e28);
    border: 1px solid #1a4d40; border-radius: 16px; padding: 20px 24px;
}
.concept-term { color: #00d4aa; font-size: 1.1rem; font-weight: 800; }
.concept-def { color: #c5cdd8; font-size: .88rem; margin-top: 8px; line-height: 1.6; }

/* ── News ────────────────────────────────────────────────────── */
.news-item { border-bottom: 1px solid #1e2d40; padding: 12px 0; }
.news-title { color: #fff; font-size: .88rem; font-weight: 600; }
.news-meta { color: #8892a4; font-size: .73rem; margin-top: 3px; }

/* ── Company Card ────────────────────────────────────────────── */
.company-header {
    background: linear-gradient(135deg,#131720,#1a2035);
    border: 1px solid #1e2d40; border-radius: 16px; padding: 24px;
}
.co-name { color: #fff; font-size: 1.4rem; font-weight: 800; }
.co-sector { color: #8892a4; font-size: .82rem; margin: 2px 0 12px; }
.co-price { color: #fff; font-size: 2rem; font-weight: 800; }
.co-desc { color: #c5cdd8; font-size: .88rem; line-height: 1.6; margin-top: 12px; }

/* ── Verdict ─────────────────────────────────────────────────── */
.verdict {
    display: inline-block; border-radius: 999px;
    padding: 8px 32px; font-size: 1rem; font-weight: 800;
    letter-spacing: .06em; text-align: center;
}
.v-invest { background: rgba(0,212,170,.12); color: #00d4aa; border: 2px solid #00d4aa; }
.v-wait   { background: rgba(255,193,7,.12);  color: #ffc107; border: 2px solid #ffc107; }
.v-avoid  { background: rgba(255,71,87,.12);  color: #ff4757; border: 2px solid #ff4757; }

/* ── Chat ────────────────────────────────────────────────────── */
.chat-u {
    background: #1e2d40; border-radius: 18px 18px 4px 18px;
    padding: 12px 16px; margin: 8px 0 8px 20%;
    color: #fff; font-size: .9rem;
}
.chat-a {
    background: #131720; border-left: 3px solid #00d4aa;
    border-radius: 0 18px 18px 18px;
    padding: 12px 16px; margin: 8px 20% 8px 0;
    color: #c5cdd8; font-size: .9rem;
}

/* ── Lesson Card ─────────────────────────────────────────────── */
.lesson-card {
    background: #131720; border: 1px solid #1e2d40; border-radius: 16px;
    padding: 20px; transition: all .2s ease;
}
.lesson-card.done { border-color: #00d4aa; }
.lesson-title { color: #fff; font-size: .95rem; font-weight: 700; }
.lesson-desc  { color: #8892a4; font-size: .8rem; margin-top: 6px; line-height: 1.4; }
.lesson-emoji { font-size: 2rem; margin-bottom: 8px; }
.lesson-meta  { color: #8892a4; font-size: .75rem; margin-top: 4px; }

/* ── Quiz ────────────────────────────────────────────────────── */
.quiz-correct { color: #00d4aa; font-weight: 700; }
.quiz-wrong   { color: #ff4757; font-weight: 700; }

/* ── Glossary ────────────────────────────────────────────────── */
.gloss-term { color: #00d4aa; font-weight: 700; font-size: .9rem; }
.gloss-def  { color: #c5cdd8; font-size: .85rem; }

/* ── Settings ────────────────────────────────────────────────── */
.setting-row {
    background: #131720; border: 1px solid #1e2d40; border-radius: 12px;
    padding: 14px 18px; margin: 8px 0;
    display: flex; align-items: center; justify-content: space-between;
}
.setting-key { color: #8892a4; font-size: .8rem; font-family: monospace; }
.setting-val { color: #fff; font-size: .9rem; }
.status-ok  { color: #00d4aa; font-weight: 700; }
.status-err { color: #ff4757; font-weight: 700; }

/* ── Progress Override ───────────────────────────────────────── */
.stProgress > div > div { background: #00d4aa !important; }

/* ── Inputs ──────────────────────────────────────────────────── */
.stTextInput > div > input, .stTextArea textarea {
    background: #131720 !important; border: 1px solid #1e2d40 !important;
    color: #fff !important; border-radius: 10px !important;
}
.stTextInput > div > input:focus { border-color: #00d4aa !important; }

/* ── Tabs ────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] { gap: 6px; background: transparent; }
[data-baseweb="tab"] {
    background: #131720 !important; border: 1px solid #1e2d40 !important;
    border-radius: 8px !important; color: #8892a4 !important; padding: 8px 18px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(0,212,170,.12) !important; border-color: #00d4aa !important;
    color: #00d4aa !important;
}

/* ── Expander ────────────────────────────────────────────────── */
.streamlit-expanderHeader { color: #8892a4 !important; font-size: .8rem !important; }
.streamlit-expanderHeader:hover { color: #00d4aa !important; }

/* ── Alerts ──────────────────────────────────────────────────── */
[data-testid="stNotification"] { border-radius: 12px; }

/* ── Divider ─────────────────────────────────────────────────── */
hr { border-color: #1e2d40 !important; margin: 20px 0 !important; }

/* ── Sidebar logo ────────────────────────────────────────────── */
.sidebar-logo { text-align: center; padding: 16px 0 20px; }
.sidebar-logo h3 { color: #00d4aa; margin: 0; font-size: 1rem; }
.sidebar-logo p  { color: #8892a4; font-size: .75rem; margin: 2px 0 0; }
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def sidebar_logo():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
          <h3>📊 Financial Intelligence</h3>
          <p>RAG · Market · Trading · AI</p>
        </div>
        """, unsafe_allow_html=True)


def section(title: str):
    st.markdown(f'<div class="section-hdr">{title}</div>', unsafe_allow_html=True)


def kpi(label: str, value: str, delta: str = "", positive: bool | None = None):
    cls = ""
    if positive is True:  cls = "pos"
    elif positive is False: cls = "neg"
    else:                   cls = "neu"
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      {'<div class="kpi-d ' + cls + '">' + delta + '</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def verdict_badge(v: str):
    v_up = v.upper()
    css = {"INVEST": "v-invest", "WAIT": "v-wait", "AVOID": "v-avoid"}.get(v_up, "v-wait")
    icons = {"INVEST": "✅", "WAIT": "⏳", "AVOID": "🚫"}
    st.markdown(f'<div class="verdict {css}">{icons.get(v_up,"")} {v_up}</div>', unsafe_allow_html=True)
