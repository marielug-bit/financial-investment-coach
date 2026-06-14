"""Share — send analysis via MCP email agent."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.theme import inject_css, section
from utils.market import get_ticker_info, format_price, format_mktcap, compute_health_score, resolve_ticker

st.set_page_config(page_title="Share · Financial Intelligence",
                   page_icon="📧", layout="wide")
inject_css()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h3>📊 Financial Intelligence</h3></div>',
                unsafe_allow_html=True)
    st.page_link("streamlit_app.py",     label="🏠 Home")
    st.page_link("pages/1_Discover.py",  label="🔍 Discover")
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio")
    st.page_link("pages/3_Share.py",     label="📧 Share", disabled=True)
    st.page_link("pages/4_Learn.py",     label="🎓 Learn")
    st.page_link("pages/5_Settings.py",  label="⚙️ Settings")

st.markdown("""
<h1 style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px">📧 Share Analysis</h1>
<p style="color:#8892a4;font-size:.88rem;margin:0 0 20px">
  Send investment insights to your contacts
</p>
""", unsafe_allow_html=True)

# ── Load email groups ─────────────────────────────────────────────────────────
import yaml, os

def _load_groups() -> dict[str, list[str]]:
    cfg_path = Path(__file__).parent.parent / "config" / "email_groups.yaml"
    try:
        with open(cfg_path) as f:
            return yaml.safe_load(f).get("groups", {})
    except Exception:
        return {}

groups = _load_groups()

# ── Pre-fill from Discover page ───────────────────────────────────────────────
prefill = st.session_state.pop("share_prefill", "")

# ── Compose form ──────────────────────────────────────────────────────────────
section("✉️ Compose Your Message")

col_form, col_preview = st.columns([1, 1], gap="large")

with col_form:
    ticker_input = st.text_input(
        "Company or ticker to share",
        value=prefill,
        placeholder="Apple, NVDA, TSLA…",
    )

    group_names = list(groups.keys())
    if not group_names:
        st.warning("No email groups found. Create them in **Settings → Email Groups**.")
        chosen_group = None
    else:
        chosen_group = st.selectbox(
            "Send to group",
            options=group_names,
            format_func=lambda g: f"📬 {g}  ({', '.join(groups[g][:2])}{'…' if len(groups[g])>2 else ''})",
        )
        if chosen_group:
            recipients = groups[chosen_group]
            st.markdown(f"""
            <div style="background:#131720;border:1px solid #1e2d40;border-radius:8px;
                padding:10px 14px;font-size:.82rem;color:#8892a4;margin:4px 0 12px">
              Recipients: <b style="color:#fff">{', '.join(recipients)}</b>
            </div>
            """, unsafe_allow_html=True)

    message_type = st.radio(
        "What to send",
        ["📊 Full Analysis",
         "💡 Quick Insight (1 paragraph)",
         "🚦 Just the Verdict (INVEST/WAIT/AVOID)"],
        label_visibility="visible",
    )

    custom_note = st.text_area(
        "Add a personal note (optional)",
        placeholder="I think this could be interesting because…",
        height=80,
    )

with col_preview:
    if ticker_input:
        t = resolve_ticker(ticker_input)
        info = get_ticker_info(t)
        score, green, red = compute_health_score(info)

        if score >= 7:
            verdict, v_color = "INVEST", "#00d4aa"
        elif score >= 4:
            verdict, v_color = "WAIT", "#ffc107"
        else:
            verdict, v_color = "AVOID", "#ff4757"

        pct    = info.get("change_pct", 0)
        pct_c  = "#00d4aa" if pct >= 0 else "#ff4757"
        arrow  = "▲" if pct >= 0 else "▼"

        st.markdown(f"""
        <div style="background:#131720;border:1px solid #1e2d40;border-radius:14px;padding:20px;margin-top:8px">
          <div style="font-size:.72rem;color:#8892a4;text-transform:uppercase;letter-spacing:.08em">Preview</div>
          <div style="margin-top:10px">
            <span style="color:#fff;font-size:1.1rem;font-weight:700">{info['name']}</span>
            <span style="color:#8892a4"> · {t}</span>
          </div>
          <div style="margin:8px 0">
            <span style="color:#fff;font-size:1.3rem;font-weight:800">{format_price(info['price'])}</span>
            <span style="color:{pct_c};margin-left:8px">{arrow} {pct:+.2f}%</span>
          </div>
          <div style="display:flex;gap:12px;margin:12px 0">
            <div style="background:#0e1117;padding:8px 14px;border-radius:8px;text-align:center">
              <div style="color:#8892a4;font-size:.72rem">Health Score</div>
              <div style="color:#fff;font-weight:700;font-size:1.1rem">{score}/10</div>
            </div>
            <div style="background:{v_color}18;border:1px solid {v_color};
                padding:8px 20px;border-radius:8px;text-align:center">
              <div style="color:#8892a4;font-size:.72rem">Verdict</div>
              <div style="color:{v_color};font-weight:800">{verdict}</div>
            </div>
          </div>
          <div style="margin-top:12px">
            {"".join([f'<div style="color:#00d4aa;font-size:.8rem;margin:3px 0">✅ {f}</div>' for f in green[:2]])}
            {"".join([f'<div style="color:#ff4757;font-size:.8rem;margin:3px 0">⚠️ {f}</div>' for f in red[:2]])}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#131720;border:1px dashed #1e2d40;border-radius:14px;
            padding:40px;text-align:center;color:#8892a4;margin-top:8px">
          Enter a ticker above to see the preview
        </div>
        """, unsafe_allow_html=True)

# ── Send ──────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

can_send = bool(ticker_input) and bool(chosen_group)

if st.button("📤 Send via Email", type="primary", use_container_width=True, disabled=not can_send):
    if not can_send:
        st.warning("Please enter a ticker and select a group.")
    else:
        t = resolve_ticker(ticker_input)
        info = get_ticker_info(t)
        score, green, red = compute_health_score(info)

        if score >= 7:
            verdict = "INVEST ✅"
        elif score >= 4:
            verdict = "WAIT ⏳"
        else:
            verdict = "AVOID ❌"

        if "Verdict" in message_type:
            body = (
                f"Quick update on {info['name']} ({t}):\n\n"
                f"Verdict: {verdict}\n"
                f"Current price: {format_price(info['price'])} ({info['change_pct']:+.2f}% today)\n"
                f"Health score: {score}/10\n"
            )
            if custom_note:
                body += f"\n{custom_note}"
        elif "Insight" in message_type:
            positives = "; ".join(green) if green else "no major strengths"
            concerns  = "; ".join(red) if red else "no major concerns"
            body = (
                f"Here's a quick look at {info['name']} ({t}):\n\n"
                f"Price: {format_price(info['price'])} ({info['change_pct']:+.2f}% today)\n"
                f"Health score: {score}/10 — Verdict: {verdict}\n\n"
                f"Strengths: {positives}\n"
                f"Concerns: {concerns}\n"
                f"Market cap: {format_mktcap(info['market_cap'])}"
            )
            if custom_note:
                body += f"\n\n{custom_note}"
        else:
            # Full analysis — use MCP agent
            body = None

        if body:
            # Send directly via MCP email tool
            with st.spinner("Sending via MCP email agent…"):
                try:
                    from utils.mcp_session import start_mcp
                    mcp = start_mcp()
                    if mcp.error:
                        raise RuntimeError(mcp.error)
                    prompt = (
                        f"Send this email to the '{chosen_group}' email group:\n\n"
                        f"Subject: {info['name']} ({t}) — {verdict}\n\n"
                        f"{body}\n\n"
                        f"Use the send_email MCP tool."
                    )
                    result = mcp.ask(prompt, timeout=60)
                    st.success(f"✅ Sent to **{chosen_group}** ({len(groups[chosen_group])} recipient(s))!")
                    st.caption(f"Agent response: {result[:200]}")
                except Exception as e:
                    # Fallback: show what would be sent
                    st.warning(f"MCP email agent unavailable ({e}). Here's what would be sent:")
                    st.code(body)
        else:
            # Full analysis via MCP
            with st.spinner("Generating full analysis (30–60 s)…"):
                try:
                    from utils.mcp_session import start_mcp
                    mcp = start_mcp()
                    if mcp.error:
                        raise RuntimeError(mcp.error)
                    prompt = (
                        f"Write a full investment analysis of {t} ({info['name']}) for a beginner investor, "
                        f"then send it to the '{chosen_group}' email group. "
                        f"Include: current price, health score reasoning, key strengths/risks, and a clear verdict. "
                        f"Write in plain English, no jargon. Keep it under 400 words. "
                        + (f"Add this note at the end: {custom_note}" if custom_note else "")
                    )
                    result = mcp.ask(prompt, timeout=120)
                    st.success(f"✅ Full analysis sent to **{chosen_group}**!")
                    st.caption(f"Agent: {result[:200]}")
                except Exception as e:
                    st.error(f"Could not send full analysis: {e}")

# ── Weekly Report ─────────────────────────────────────────────────────────────
section("📅 Weekly Coach Report")
st.markdown("""
<div style="background:#131720;border:1px solid #1e2d40;border-radius:14px;padding:20px;margin-bottom:16px">
  <div style="color:#fff;font-weight:700;margin-bottom:8px">📬 Auto Weekly Summary</div>
  <div style="color:#8892a4;font-size:.86rem">
    Sends a full portfolio summary, top opportunities, and market insights
    to your <code style="color:#00d4aa">weekly</code> email group every Monday.
  </div>
</div>
""", unsafe_allow_html=True)

if "weekly_sent" not in st.session_state:
    st.session_state.weekly_sent = False

col_w1, col_w2 = st.columns([2, 1])
with col_w1:
    if st.button("🚀 Send Weekly Report Now", use_container_width=True):
        with st.spinner("Generating weekly report (up to 2 min)…"):
            try:
                from utils.mcp_session import start_mcp
                mcp = start_mcp()
                if mcp.error:
                    raise RuntimeError(mcp.error)
                result = mcp.run_weekly_report(timeout=180)
                st.session_state.weekly_sent = True
                st.success("✅ Weekly report sent!")
                with st.expander("See report summary"):
                    st.write(result)
            except Exception as e:
                st.error(f"Could not send weekly report: {e}")
