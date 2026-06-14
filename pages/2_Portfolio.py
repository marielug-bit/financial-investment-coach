"""Portfolio — Alpaca paper trading tracker with buy flow."""
import asyncio
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.theme import inject_css, section, kpi
from utils.market import get_history, get_ticker_info, format_price, resolve_ticker

st.set_page_config(page_title="Portfolio · Financial Intelligence",
                   page_icon="💼", layout="wide")
inject_css()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h3>📊 Financial Intelligence</h3></div>',
                unsafe_allow_html=True)
    st.page_link("streamlit_app.py",     label="🏠 Home")
    st.page_link("pages/1_Discover.py",  label="🔍 Discover")
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio", disabled=True)
    st.page_link("pages/3_Share.py",     label="📧 Share")
    st.page_link("pages/4_Learn.py",     label="🎓 Learn")
    st.page_link("pages/5_Settings.py",  label="⚙️ Settings")

st.markdown("""
<h1 style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px">💼 My Paper Portfolio</h1>
<p style="color:#8892a4;font-size:.88rem;margin:0 0 20px">
  Simulated trades — no real money involved
</p>
""", unsafe_allow_html=True)

# ── Alpaca connection ─────────────────────────────────────────────────────────
api_key = os.getenv("ALPACA_API_KEY","")
secret  = os.getenv("ALPACA_SECRET_KEY","")

if not api_key or not secret:
    st.markdown("""
    <div style="text-align:center;padding:60px 0">
      <div style="font-size:3rem">📭</div>
      <h3 style="color:#fff;margin:16px 0 8px">Alpaca not connected</h3>
      <p style="color:#8892a4">Set up your free paper trading account to track simulated investments.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚙️ Go to Settings →", type="primary"):
        st.switch_page("pages/5_Settings.py")
    st.stop()

@st.cache_data(ttl=60)
def _load_alpaca():
    try:
        from alpaca.trading.client import TradingClient
        client = TradingClient(api_key, secret, paper=True)
        return client.get_account(), list(client.get_all_positions()), client, None
    except Exception as e:
        return None, None, None, str(e)

with st.spinner("Loading portfolio…"):
    acct, positions, _client, err = _load_alpaca()

if err or acct is None:
    st.error(f"Could not connect to Alpaca: {err}")
    st.stop()

equity      = float(acct.equity)
cash        = float(acct.cash)
last_equity = float(acct.last_equity)
pv          = float(acct.portfolio_value)
day_pl      = equity - last_equity
day_pl_pct  = (day_pl / last_equity * 100) if last_equity else 0
bp          = float(acct.buying_power)

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4, gap="small")
with c1: kpi("Portfolio Value", format_price(pv), "Total simulated equity")
with c2: kpi("Day P&L", f"${day_pl:+,.2f}",
             f"{'▲' if day_pl>=0 else '▼'} {day_pl_pct:+.2f}% today", day_pl>=0)
with c3: kpi("Cash Available", format_price(cash), "Uninvested cash")
with c4: kpi("Buying Power", format_price(bp), "Max you can spend now")

# ── Portfolio vs S&P 500 chart ────────────────────────────────────────────────
section("📈 Performance vs S&P 500")
import plotly.graph_objects as go

spy = get_history("SPY", "1mo")
port_hist = None
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetPortfolioHistoryRequest
    import pandas as pd
    c2_tmp = TradingClient(api_key, secret, paper=True)
    h = c2_tmp.get_portfolio_history(GetPortfolioHistoryRequest(period="1M", timeframe="1D"))
    if h.equity and any(v for v in h.equity if v):
        port_hist = pd.DataFrame({"date": pd.to_datetime(h.timestamp, unit="s"), "equity": h.equity})
        port_hist = port_hist[port_hist["equity"] > 0]
except Exception:
    pass

fig_perf = go.Figure()
if port_hist is not None and not port_hist.empty:
    base = port_hist["equity"].iloc[0]
    fig_perf.add_trace(go.Scatter(
        x=port_hist["date"], y=(port_hist["equity"]/base - 1)*100,
        name="My Portfolio", line=dict(color="#00d4aa", width=2),
        hovertemplate="%{x|%b %d}<br>%{y:+.2f}%<extra>Portfolio</extra>",
    ))
if not spy.empty:
    spy_base = spy["Close"].iloc[0]
    fig_perf.add_trace(go.Scatter(
        x=spy.index, y=(spy["Close"]/spy_base - 1)*100,
        name="S&P 500", line=dict(color="#8892a4", width=1.5, dash="dot"),
        hovertemplate="%{x|%b %d}<br>%{y:+.2f}%<extra>S&P 500</extra>",
    ))
if not fig_perf.data:
    fig_perf.add_annotation(text="No history available yet",
                             xref="paper", yref="paper", x=0.5, y=0.5,
                             font=dict(color="#8892a4"))
fig_perf.update_layout(
    template="plotly_dark", paper_bgcolor="#131720", plot_bgcolor="#131720",
    margin=dict(l=8,r=8,t=8,b=8), height=260,
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#1e2d40", ticksuffix="%"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified",
)
st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar":False})

# ── Positions ─────────────────────────────────────────────────────────────────
section("📋 Open Positions")
if not positions:
    st.markdown("""
    <div style="text-align:center;padding:40px 0;color:#8892a4">
      <div style="font-size:2rem">📭</div>
      <div style="margin-top:10px">No positions yet — buy your first stock below!</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Allocation pie
    pie_col, bar_col = st.columns(2, gap="large")
    with pie_col:
        fig_pie = go.Figure(go.Pie(
            labels=[p.symbol for p in positions],
            values=[abs(float(p.market_value)) for p in positions],
            hole=0.55, textinfo="label+percent",
            textfont=dict(size=11, color="#fff"),
            marker=dict(colors=["#00d4aa","#4299e1","#ffc107","#ff4757",
                                 "#9f7aea","#38b2ac","#f6e05e","#76e4f7"],
                        line=dict(color="#0e1117", width=2)),
        ))
        fig_pie.update_layout(paper_bgcolor="#131720", plot_bgcolor="#131720",
                               margin=dict(l=0,r=0,t=0,b=0), height=240, showlegend=False)
        st.markdown("**Allocation**")
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar":False})

    with bar_col:
        pls = [float(p.unrealized_pl) for p in positions]
        fig_bar = go.Figure(go.Bar(
            x=[p.symbol for p in positions], y=pls,
            marker_color=["#00d4aa" if v>=0 else "#ff4757" for v in pls],
            text=[f"${v:+,.0f}" for v in pls], textposition="outside",
            textfont=dict(color="#fff", size=11),
        ))
        fig_bar.update_layout(
            template="plotly_dark", paper_bgcolor="#131720", plot_bgcolor="#131720",
            margin=dict(l=8,r=8,t=8,b=8), height=240,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1e2d40", tickformat="$,.0f"),
            showlegend=False,
        )
        st.markdown("**Unrealized P&L**")
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

    # Position rows
    for pos in positions:
        pl     = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc)*100
        cur    = float(pos.current_price)
        avg    = float(pos.avg_entry_price)
        mv     = float(pos.market_value)
        qty    = float(pos.qty)
        pl_c   = "#00d4aa" if pl>=0 else "#ff4757"
        arrow  = "▲" if pl>=0 else "▼"

        c_sym, c_qty, c_avg, c_cur, c_mv, c_pl, c_spark = st.columns([2,1,1.5,1.5,1.5,2,2])
        c_sym.markdown(f"**{pos.symbol}**")
        c_qty.markdown(f"{qty:g}")
        c_qty.caption("shares")
        c_avg.markdown(f"${avg:,.2f}")
        c_avg.caption("avg cost")
        c_cur.markdown(f"${cur:,.2f}")
        c_cur.caption("current")
        c_mv.markdown(f"${mv:,.2f}")
        c_mv.caption("value")
        c_pl.markdown(f'<span style="color:{pl_c}">{arrow} ${pl:+,.2f}<br>{pl_pct:+.2f}%</span>',
                      unsafe_allow_html=True)
        with c_spark:
            try:
                h = get_history(pos.symbol, "1wk")
                if not h.empty:
                    fig_sp = go.Figure(go.Scatter(
                        x=h.index, y=h["Close"], mode="lines",
                        line=dict(color=pl_c, width=1.5),
                    ))
                    fig_sp.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0,r=0,t=0,b=0), height=44,
                        xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False,
                    )
                    st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar":False})
            except Exception:
                pass
        st.divider()

# ── Buy a Stock ───────────────────────────────────────────────────────────────
section("🛒 Buy a Stock (Simulated)")

if "buy_success" not in st.session_state:
    st.session_state.buy_success = None

with st.expander("▶ Open Buy Flow", expanded=st.session_state.get("buy_open", False)):
    b_query = st.text_input("Search company or ticker", placeholder="Apple, NVDA…", key="buy_q")
    if b_query:
        b_ticker = resolve_ticker(b_query)
        b_info   = get_ticker_info(b_ticker)
        b_price  = b_info.get("price", 0)
        if b_price:
            st.markdown(f"""
            <div style="background:#131720;border:1px solid #1e2d40;border-radius:12px;padding:16px;margin:12px 0">
              <span style="color:#fff;font-weight:700">{b_info['name']}</span>
              <span style="color:#8892a4"> · {b_ticker}</span><br>
              <span style="color:#00d4aa;font-size:1.3rem;font-weight:800">{format_price(b_price)}</span>
            </div>
            """, unsafe_allow_html=True)
            qty_buy = st.number_input("Number of shares", min_value=1, value=1, step=1)
            total   = b_price * qty_buy
            st.markdown(f'<p style="color:#8892a4">Total cost: <b style="color:#fff">{format_price(total)}</b> '
                        f'· Cash available: <b style="color:#fff">{format_price(cash)}</b></p>',
                        unsafe_allow_html=True)

            if total > cash:
                st.warning("Not enough cash. Reduce shares or add more buying power.")
            else:
                st.markdown("""
                <div style="background:rgba(255,193,7,.08);border:1px solid #ffc107;
                    border-radius:10px;padding:12px;font-size:.82rem;color:#ffc107;margin:8px 0">
                  ⚠️ <b>Simulated money only — no real money involved.</b>
                  Orders execute at the next market open.
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🚀 Buy {qty_buy} share(s) of {b_ticker}", type="primary",
                             use_container_width=True, key="exec_buy"):
                    with st.spinner(f"Placing order for {b_ticker}…"):
                        try:
                            from alpaca.trading.client import TradingClient
                            from alpaca.trading.requests import MarketOrderRequest
                            from alpaca.trading.enums import OrderSide, TimeInForce
                            tc = TradingClient(api_key, secret, paper=True)
                            order = tc.submit_order(MarketOrderRequest(
                                symbol=b_ticker,
                                qty=qty_buy,
                                side=OrderSide.BUY,
                                time_in_force=TimeInForce.GTC,  # Good Till Cancelled — works outside market hours
                            ))
                            _load_alpaca.clear()
                            st.session_state.buy_success = f"{qty_buy} × {b_ticker} | order #{str(order.id)[:8]}…"
                            st.session_state.buy_open = False
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Order failed: {e}")
        else:
            st.warning(f"Could not find '{b_ticker}'. Try the ticker symbol directly (e.g. AAPL).")

if st.session_state.buy_success:
    st.success(f"✅ Order submitted: {st.session_state.buy_success} — will appear in Positions once the market opens (Mon 9:30 ET)")
    st.session_state.buy_success = None

if st.button("🔄 Refresh Portfolio", use_container_width=True):
    _load_alpaca.clear()
    st.rerun()
