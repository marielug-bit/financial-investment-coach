"""Settings — API keys, tickers, email groups, Coach Mode."""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv, set_key
load_dotenv()

from utils.theme import inject_css, section

st.set_page_config(page_title="Settings · Financial Intelligence",
                   page_icon="⚙️", layout="wide")
inject_css()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h3>📊 Financial Intelligence</h3></div>',
                unsafe_allow_html=True)
    st.page_link("streamlit_app.py",     label="🏠 Home")
    st.page_link("pages/1_Discover.py",  label="🔍 Discover")
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio")
    st.page_link("pages/3_Share.py",     label="📧 Share")
    st.page_link("pages/4_Learn.py",     label="🎓 Learn")
    st.page_link("pages/5_Settings.py",  label="⚙️ Settings", disabled=True)

st.markdown("""
<h1 style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px">⚙️ Settings</h1>
<p style="color:#8892a4;font-size:.88rem;margin:0 0 20px">Configure your Financial Intelligence app</p>
""", unsafe_allow_html=True)

ENV_PATH = Path(__file__).parent.parent / ".env"
YAML_PATH = Path(__file__).parent.parent / "config" / "email_groups.yaml"

def _save_env(key: str, value: str):
    set_key(str(ENV_PATH), key, value)
    os.environ[key] = value

def _mask(val: str) -> str:
    if not val: return "❌ Not set"
    return f"✅ `{'*' * 8}{val[-4:]}`"

# ── Coach Mode ────────────────────────────────────────────────────────────────
section("🤖 AI Coach Mode")
st.markdown("""
<div style="background:#131720;border:1px solid #1e2d40;border-radius:14px;padding:20px;margin-bottom:16px">
  <div style="color:#fff;font-weight:700;margin-bottom:6px">🎓 Coach Mode</div>
  <div style="color:#8892a4;font-size:.86rem">
    When on, the AI explains every answer in plain English for beginners.
    When off, responses are more concise and data-focused.
  </div>
</div>
""", unsafe_allow_html=True)

current_coach = os.getenv("COACH_MODE", "true").lower() == "true"
new_coach = st.toggle("Enable Coach Mode", value=current_coach)
if new_coach != current_coach:
    _save_env("COACH_MODE", "true" if new_coach else "false")
    st.success("Coach Mode " + ("enabled ✅" if new_coach else "disabled"))

# ── Tracked Tickers ───────────────────────────────────────────────────────────
section("📈 Tracked Tickers")
st.markdown("""
<div style="color:#8892a4;font-size:.85rem;margin-bottom:12px">
  These appear on the Home page ticker bar and investment opportunities.
  Enter comma-separated ticker symbols.
</div>
""", unsafe_allow_html=True)

current_tickers = os.getenv("TRACKED_TICKERS", "AAPL,NVDA,TSLA,MSFT,GOOGL")
new_tickers_str = st.text_input(
    "Tickers (comma-separated)",
    value=current_tickers,
    help="Example: AAPL,NVDA,TSLA,MSFT",
    key="tickers_input",
)

# Show parsed tickers
parsed = [t.strip().upper() for t in new_tickers_str.split(",") if t.strip()]
if parsed:
    chip_html = " ".join([
        f'<span style="background:#00d4aa22;color:#00d4aa;padding:3px 10px;'
        f'border-radius:99px;font-size:.8rem;font-weight:600">{t}</span>'
        for t in parsed
    ])
    st.markdown(f'<div style="margin:8px 0">{chip_html}</div>', unsafe_allow_html=True)

col_t1, col_t2 = st.columns(2)
with col_t1:
    if st.button("💾 Save Tickers", use_container_width=True, type="primary",
                 disabled=(new_tickers_str == current_tickers)):
        _save_env("TRACKED_TICKERS", new_tickers_str)
        st.success(f"Saved {len(parsed)} tickers.")
        st.rerun()
with col_t2:
    if st.button("↺ Reset to Default", use_container_width=True):
        _save_env("TRACKED_TICKERS", "AAPL,NVDA,TSLA,MSFT,GOOGL")
        st.rerun()

# ── Email Groups ──────────────────────────────────────────────────────────────
section("📬 Email Groups")
import yaml

def _load_yaml() -> dict:
    try:
        with open(YAML_PATH) as f:
            return yaml.safe_load(f) or {"groups": {}}
    except Exception:
        return {"groups": {}}

def _save_yaml(data: dict):
    YAML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

email_data = _load_yaml()
groups: dict[str, list] = email_data.get("groups", {})

st.markdown("""
<div style="color:#8892a4;font-size:.85rem;margin-bottom:12px">
  Manage who receives your investment analysis emails.
</div>
""", unsafe_allow_html=True)

# Display existing groups
changed = False
groups_to_delete = []
for gname, emails in list(groups.items()):
    with st.expander(f"📬 {gname}  ({len(emails)} recipient(s))", expanded=False):
        emails_str = st.text_area(
            "Recipients (one per line)",
            value="\n".join(emails),
            key=f"group_{gname}",
            height=90,
        )
        c_save, c_del = st.columns([3, 1])
        with c_save:
            if st.button(f"Save {gname}", key=f"save_g_{gname}", use_container_width=True):
                new_list = [e.strip() for e in emails_str.splitlines() if e.strip()]
                groups[gname] = new_list
                changed = True
                st.success(f"Saved {gname} with {len(new_list)} recipient(s).")
        with c_del:
            if st.button("🗑 Delete", key=f"del_g_{gname}", use_container_width=True):
                groups_to_delete.append(gname)
                changed = True

for g in groups_to_delete:
    del groups[g]

if changed:
    email_data["groups"] = groups
    _save_yaml(email_data)
    st.rerun()

# Add new group
st.markdown("**Add a new group**")
col_gn, col_ge = st.columns([1, 2])
with col_gn:
    new_gname = st.text_input("Group name", placeholder="team, family…", key="new_gname")
with col_ge:
    new_gemails = st.text_input("Email(s) — comma separated", placeholder="a@b.com, c@d.com", key="new_gemails")
if st.button("➕ Add Group", type="primary", disabled=not (new_gname and new_gemails)):
    grp_emails = [e.strip() for e in new_gemails.split(",") if e.strip()]
    groups[new_gname.strip()] = grp_emails
    email_data["groups"] = groups
    _save_yaml(email_data)
    st.success(f"Group '{new_gname}' added with {len(grp_emails)} recipient(s).")
    st.rerun()

# ── Alpaca ────────────────────────────────────────────────────────────────────
section("📊 Alpaca Paper Trading")
st.markdown("""
<div style="color:#8892a4;font-size:.85rem;margin-bottom:12px">
  Connect your free Alpaca paper trading account to track simulated investments.
  <a href="https://alpaca.markets" target="_blank" style="color:#00d4aa">Get free API keys →</a>
</div>
""", unsafe_allow_html=True)

cur_key = os.getenv("ALPACA_API_KEY", "")
cur_sec = os.getenv("ALPACA_SECRET_KEY", "")

c_ak, c_as = st.columns(2)
with c_ak:
    st.markdown(f"**API Key** — {_mask(cur_key)}")
    new_ak = st.text_input("New API Key", type="password", key="alp_key",
                            placeholder="Leave blank to keep current")
with c_as:
    st.markdown(f"**Secret Key** — {_mask(cur_sec)}")
    new_sk = st.text_input("New Secret Key", type="password", key="alp_sec",
                            placeholder="Leave blank to keep current")

col_alp1, col_alp2 = st.columns(2)
with col_alp1:
    if st.button("💾 Save Alpaca Keys", type="primary", use_container_width=True,
                 disabled=not (new_ak or new_sk)):
        if new_ak: _save_env("ALPACA_API_KEY", new_ak)
        if new_sk: _save_env("ALPACA_SECRET_KEY", new_sk)
        st.success("Alpaca keys saved.")
        st.rerun()
with col_alp2:
    if st.button("🔌 Test Connection", use_container_width=True):
        key = new_ak or cur_key
        sec = new_sk or cur_sec
        if not key or not sec:
            st.warning("Enter API keys first.")
        else:
            with st.spinner("Testing connection…"):
                try:
                    from alpaca.trading.client import TradingClient
                    acct = TradingClient(key, sec, paper=True).get_account()
                    st.success(f"✅ Connected! Portfolio value: ${float(acct.portfolio_value):,.2f}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

# ── Anthropic & other API keys ───────────────────────────────────────────────
section("🔑 API Keys")

API_FIELDS = [
    ("ANTHROPIC_API_KEY",   "Anthropic (Claude AI)",  "sk-ant-…"),
    ("EMAIL_SMTP_PASSWORD", "Email SMTP Password",    "App password from Gmail"),
    ("EMAIL_FROM",          "From Email Address",     "you@gmail.com"),
]

for env_key, label, placeholder in API_FIELDS:
    cur = os.getenv(env_key, "")
    with st.expander(f"{label} — {_mask(cur)}", expanded=False):
        new_val = st.text_input(
            f"New {label}",
            type="password" if "KEY" in env_key or "PASSWORD" in env_key else "default",
            placeholder=placeholder,
            key=f"key_{env_key}",
        )
        if st.button(f"Save {label}", key=f"save_{env_key}",
                     disabled=not new_val):
            _save_env(env_key, new_val)
            st.success(f"✅ {label} saved.")

# ── MCP status ────────────────────────────────────────────────────────────────
section("🤖 MCP Agent Status")
mcp = st.session_state.get("_mcp")
if mcp is None:
    st.markdown("""
    <div style="background:#ffc10711;border:1px solid #ffc107;border-radius:10px;
        padding:12px 16px;color:#ffc107;font-size:.86rem">
      ⏸ MCP agents not started — they start automatically when you ask a question.
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Start MCP Agents", type="primary"):
        with st.spinner("Connecting to MCP servers (~15 s first time)…"):
            from utils.mcp_session import start_mcp
            m = start_mcp()
            if m.error:
                st.error(f"Failed: {m.error}")
            else:
                st.success(f"✅ Connected! {len(m.tool_names)} tools available: {', '.join(m.tool_names[:5])}…")
                st.rerun()
elif mcp.error:
    st.error(f"MCP error: {mcp.error}")
    if st.button("♻️ Restart MCP"):
        del st.session_state["_mcp"]
        st.rerun()
else:
    tools_list = ", ".join(mcp.tool_names[:8])
    if len(mcp.tool_names) > 8:
        tools_list += f" …+{len(mcp.tool_names)-8} more"
    st.markdown(f"""
    <div style="background:#00d4aa11;border:1px solid #00d4aa44;border-radius:10px;
        padding:12px 16px;font-size:.86rem">
      <span style="color:#00d4aa;font-weight:700">✅ MCP Online</span>
      <span style="color:#8892a4;margin-left:12px">{len(mcp.tool_names)} tools active</span><br>
      <span style="color:#8892a4;font-size:.78rem">{tools_list}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("♻️ Restart MCP Agents"):
        mcp.cleanup()
        del st.session_state["_mcp"]
        st.rerun()
