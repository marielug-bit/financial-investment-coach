"""Learn — 6 finance lessons with quizzes and glossary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.theme import inject_css, section
from utils.market import GLOSSARY

st.set_page_config(page_title="Learn · Financial Intelligence",
                   page_icon="🎓", layout="wide")
inject_css()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h3>📊 Financial Intelligence</h3></div>',
                unsafe_allow_html=True)
    st.page_link("streamlit_app.py",     label="🏠 Home")
    st.page_link("pages/1_Discover.py",  label="🔍 Discover")
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio")
    st.page_link("pages/3_Share.py",     label="📧 Share")
    st.page_link("pages/4_Learn.py",     label="🎓 Learn", disabled=True)
    st.page_link("pages/5_Settings.py",  label="⚙️ Settings")

st.markdown("""
<h1 style="font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 4px">🎓 Finance School</h1>
<p style="color:#8892a4;font-size:.88rem;margin:0 0 20px">
  Six lessons that turn beginner confusion into investor confidence
</p>
""", unsafe_allow_html=True)

# ── Lessons data ──────────────────────────────────────────────────────────────
LESSONS = {
    "1": {
        "title": "What is a Balance Sheet?",
        "emoji": "📊",
        "summary": "Understand what a company owns, owes, and is worth",
        "content": """\
## What is a Balance Sheet?

Think of a balance sheet like a **snapshot photo of a company's finances** taken on one specific day.

It answers: *What does the company own, what does it owe, and what's left over?*

### The Three Parts

**Assets — What the company OWNS**
Cash in the bank, buildings, equipment, and money that customers still owe them.

**Liabilities — What the company OWES**
Loans, credit cards, unpaid bills, mortgages.

**Equity — What's LEFT OVER**
Equity = Assets − Liabilities. The company's real "net worth."

### The Golden Rule
> **Assets = Liabilities + Equity**

### Why Should You Care?
- High debt vs equity → **risky** (like someone drowning in credit card debt)
- More assets than debts → **financially stable** (like someone with a paid-off house)

**Beginner tip:** If a company's debt is more than 2× its equity, that's a yellow flag.
""",
        "quiz": [
            {
                "q": "Assets = Liabilities + ___?",
                "options": ["Revenue", "Equity", "Net Income", "Cash Flow"],
                "answer": "Equity",
                "explanation": "The balance sheet must always balance: Assets = Liabilities + Equity.",
            },
            {
                "q": "If a company has $100M in assets and $60M in liabilities, its equity is:",
                "options": ["$160M", "$60M", "$40M", "$100M"],
                "answer": "$40M",
                "explanation": "Equity = Assets − Liabilities = $100M − $60M = $40M.",
            },
            {
                "q": "Which is a sign of financial stability?",
                "options": [
                    "Debt is 3× equity",
                    "More assets than debts",
                    "Negative equity",
                    "No cash reserves",
                ],
                "answer": "More assets than debts",
                "explanation": "A company with more assets than debts has a healthy financial cushion.",
            },
        ],
    },
    "2": {
        "title": "How to Read an Income Statement",
        "emoji": "💰",
        "summary": "Follow the money from sales to final profit",
        "content": """\
## How to Read an Income Statement

If the balance sheet is a photo, the income statement is a **movie** — it shows what happened over time.

It answers: *Did the company make or lose money?*

### The Journey from Sales to Profit

```
Revenue (all money coming in)
  − Cost of Goods Sold
  = Gross Profit

  − Operating Expenses (salaries, rent, marketing)
  = Operating Income

  − Interest & Taxes
  = Net Income ← "the bottom line"
```

### Key Terms

**Revenue** — Total money from selling products or services.

**Gross Profit** — Revenue minus the cost to make the product.

**Net Income** — Final profit after *everything* is paid.

**EPS (Earnings Per Share)** — Net income ÷ shares outstanding.

**Beginner tip:** A profit margin > 15% means the company keeps at least $0.15 from every $1 of sales. That's healthy.
""",
        "quiz": [
            {
                "q": "Revenue minus Cost of Goods Sold equals:",
                "options": ["Net Income", "Gross Profit", "EPS", "Operating Cash Flow"],
                "answer": "Gross Profit",
                "explanation": "Gross Profit is the first step: Revenue − COGS.",
            },
            {
                "q": "EPS stands for:",
                "options": [
                    "Equity Per Share",
                    "Earnings Per Share",
                    "Expense Per Statement",
                    "Equity Profit Summary",
                ],
                "answer": "Earnings Per Share",
                "explanation": "EPS = Net Income ÷ number of shares — tells you profit per share.",
            },
            {
                "q": "A 20% profit margin means the company keeps:",
                "options": ["$0.02 per $1 sales", "$0.20 per $1 sales", "$2.00 per $1 sales", "$20 per $1 sales"],
                "answer": "$0.20 per $1 sales",
                "explanation": "20% margin means $0.20 profit from every $1 of revenue.",
            },
        ],
    },
    "3": {
        "title": "What Makes a Good Investment?",
        "emoji": "🎯",
        "summary": "The 4 factors every investor should check",
        "content": """\
## What Makes a Good Investment?

Not every cheap stock is a bargain — and not every expensive one is overpriced. Here's what actually matters.

### The 4 Factors

**1. Competitive Moat**
Does the company have something hard to copy? (Brand loyalty, patents, network effects, switching costs)
→ Apple's ecosystem = huge moat. A generic restaurant = no moat.

**2. Growth Potential**
Is revenue growing? Are they entering new markets? Is the industry expanding?
→ Revenue growing > 10%/year is strong.

**3. Management Quality**
Do leaders have a track record of making good decisions? Do they own shares themselves?
→ Insider ownership > 5% aligns management with shareholders.

**4. Fair Valuation**
Are you paying a fair price for what you're getting?
→ P/E < 20 is usually reasonable. P/E > 50 needs spectacular growth to justify.

### The Quick Mental Check
Before buying, ask: *"Would I buy this company if the stock market was closed for 10 years?"*
If yes, you're investing. If no, you're gambling.
""",
        "quiz": [
            {
                "q": "A 'moat' in investing refers to:",
                "options": [
                    "A company's cash reserves",
                    "A competitive advantage that's hard to copy",
                    "High debt levels",
                    "International headquarters",
                ],
                "answer": "A competitive advantage that's hard to copy",
                "explanation": "A moat protects a company from competitors — like Apple's ecosystem or Coca-Cola's brand.",
            },
            {
                "q": "Revenue growing 15% year-over-year is generally considered:",
                "options": ["Concerning", "Average", "Strong", "Negative"],
                "answer": "Strong",
                "explanation": "15% revenue growth is above the typical 10% threshold for strong expansion.",
            },
            {
                "q": "A P/E ratio of 60 suggests the stock might be:",
                "options": [
                    "Undervalued",
                    "Fairly priced",
                    "Expensive — needs strong future growth",
                    "Ready to buy immediately",
                ],
                "answer": "Expensive — needs strong future growth",
                "explanation": "P/E > 50 means you're paying a lot for current earnings — only justified by exceptional expected growth.",
            },
        ],
    },
    "4": {
        "title": "The 5 Key Numbers to Always Check",
        "emoji": "🔢",
        "summary": "Five metrics that reveal a company's financial health",
        "content": """\
## The 5 Key Numbers to Always Check

Before investing in any company, look at these five numbers. No finance degree needed.

### 1. P/E Ratio (Price-to-Earnings)
**What it is:** How much you pay for every $1 of profit.
**Rule of thumb:** < 15 = cheap · 15–25 = fair · > 50 = expensive

### 2. Profit Margin
**What it is:** How much of each sale becomes profit.
**Rule of thumb:** > 15% = strong · 5–15% = average · < 5% = thin

### 3. Debt-to-Equity Ratio
**What it is:** How much debt vs owner value.
**Rule of thumb:** < 50 = safe · 50–150 = moderate · > 200 = risky

### 4. Revenue Growth
**What it is:** Sales increase year-over-year.
**Rule of thumb:** > 10% = expanding fast · 0–10% = steady · < 0 = shrinking

### 5. Current Ratio
**What it is:** Can the company pay its short-term bills?
**Rule of thumb:** > 1.5 = comfortable · 1–1.5 = OK · < 1 = watch out

### Quick Reference
| Metric | Good | Caution | Danger |
|---|---|---|---|
| P/E | < 20 | 20–50 | > 50 |
| Profit Margin | > 15% | 5–15% | < 0% |
| Debt/Equity | < 50 | 50–200 | > 200 |
| Revenue Growth | > 10% | 0–10% | < 0% |
| Current Ratio | > 1.5 | 1–1.5 | < 1 |
""",
        "quiz": [
            {
                "q": "A P/E ratio of 12 suggests the stock is:",
                "options": ["Expensive", "About average", "Cheap/fairly valued", "Overpriced"],
                "answer": "Cheap/fairly valued",
                "explanation": "P/E below 15 is generally considered cheap or fair relative to earnings.",
            },
            {
                "q": "A current ratio of 0.7 means:",
                "options": [
                    "The company has lots of cash",
                    "The company may struggle to pay short-term debts",
                    "The company is growing fast",
                    "The stock is undervalued",
                ],
                "answer": "The company may struggle to pay short-term debts",
                "explanation": "Current ratio < 1 means current liabilities exceed current assets — a short-term liquidity risk.",
            },
            {
                "q": "Which profit margin is the healthiest?",
                "options": ["2%", "8%", "18%", "-5%"],
                "answer": "18%",
                "explanation": "Profit margin > 15% is strong. -5% means the company is losing money.",
            },
        ],
    },
    "5": {
        "title": "What is a Stock and How Does Buying One Work?",
        "emoji": "📈",
        "summary": "Ownership, dividends, and why prices move",
        "content": """\
## What is a Stock?

When you buy a share of Apple, you literally own a tiny piece of Apple. You're a shareholder — a part-owner of the business.

### How It Works

**Going Public (IPO)**
When a private company wants to raise money, it sells shares to the public for the first time. This is called an IPO.

**Stock Exchanges**
Shares are bought and sold on exchanges like NYSE or NASDAQ — like a marketplace but for company ownership.

**Why Prices Move**
Stock prices move based on supply and demand. If more people want to buy than sell → price goes up. Driven by:
- Earnings reports
- Industry news
- Economic data
- Investor sentiment

**Dividends**
Some companies share profits with shareholders regularly (quarterly). This is passive income from your investment.

### Paper Trading First
Always practice with simulated money before using real money. Our Portfolio page uses Alpaca's free paper trading — real market data, fake money.

### Key Terms
- **Market Order** — Buy/sell at whatever the current price is (right now)
- **Limit Order** — Only buy/sell at a specific price you set
- **Long** — You own the stock and profit if it rises
""",
        "quiz": [
            {
                "q": "When you buy a stock, you become:",
                "options": [
                    "A creditor of the company",
                    "A part-owner (shareholder) of the company",
                    "An employee of the company",
                    "A bond holder",
                ],
                "answer": "A part-owner (shareholder) of the company",
                "explanation": "A share of stock represents fractional ownership of the company.",
            },
            {
                "q": "IPO stands for:",
                "options": [
                    "International Price Offering",
                    "Initial Public Offering",
                    "Investor Profit Opportunity",
                    "Index Position Order",
                ],
                "answer": "Initial Public Offering",
                "explanation": "An IPO is when a private company first sells shares to the public.",
            },
            {
                "q": "Paper trading is useful because:",
                "options": [
                    "You make real profits",
                    "It's faster than real trading",
                    "You can practice with no real money at risk",
                    "It guarantees you'll win when trading for real",
                ],
                "answer": "You can practice with no real money at risk",
                "explanation": "Paper trading lets you learn with simulated money — zero financial risk.",
            },
        ],
    },
    "6": {
        "title": "How to Read Market News Without Panicking",
        "emoji": "📰",
        "summary": "Stay calm and make rational decisions when markets move",
        "content": """\
## How to Read Market News Without Panicking

The media is designed to get your attention — not to help you invest well. Here's how to filter the noise.

### The Media Trap

Headlines like "MARKET CRASHES 3%!" or "STOCKS SURGE TO ALL-TIME HIGH!" are designed to trigger emotion — fear or greed. Neither emotion makes for good investing.

### What "Market Down 3%" Actually Means

A 3% drop in the S&P 500 is completely normal. It happens multiple times per year. The S&P 500 has averaged +10%/year for 100 years, including all crashes.

### The Zoom-Out Rule
When scary news hits, zoom out your chart. A 20% drop over 6 months looks terrible. The same chart over 10 years looks like a small blip before a continued rise.

### Types of Market News

**Earnings Reports** — Actual company performance. These matter most.

**Fed Interest Rate Decisions** — Changes the cost of borrowing for everyone.

**Macroeconomic Data** — GDP, unemployment, inflation. Background signals.

**Analyst Ratings** — "Buy/Sell" recommendations. Often wrong; use as one signal only.

### The Only Question That Matters
*"Has anything changed about the company's ability to generate profits long-term?"*

If no → ignore the noise.
If yes → reassess your thesis.

### Beginner Rule
Don't check your portfolio every day. Weekly at most. Daily watching turns investors into nervous gamblers.
""",
        "quiz": [
            {
                "q": "A 3% single-day market drop is:",
                "options": [
                    "A market crash — sell everything",
                    "Normal — it happens multiple times per year",
                    "Extremely rare",
                    "Always a sign of economic recession",
                ],
                "answer": "Normal — it happens multiple times per year",
                "explanation": "Single-digit percentage drops are routine in markets. They've happened throughout history without lasting damage.",
            },
            {
                "q": "When scary market news hits, the best investor response is usually to:",
                "options": [
                    "Sell immediately",
                    "Buy more of everything",
                    "Check if the company's fundamentals changed",
                    "Refresh your portfolio every 5 minutes",
                ],
                "answer": "Check if the company's fundamentals changed",
                "explanation": "Rational investors ask: 'Did anything change about this company's ability to make money?' If not, stay the course.",
            },
            {
                "q": "Which source of market news matters MOST for long-term investors?",
                "options": [
                    "Twitter/social media stock tips",
                    "Earnings reports from the company",
                    "Daily price movement headlines",
                    "Analyst buy/sell ratings",
                ],
                "answer": "Earnings reports from the company",
                "explanation": "Actual earnings (revenue, profit, guidance) are the most reliable signals about a company's health.",
            },
        ],
    },
}

# ── Progress state ────────────────────────────────────────────────────────────
if "lessons_done" not in st.session_state:
    st.session_state.lessons_done = set()
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = {}

done_count = len(st.session_state.lessons_done)
total      = len(LESSONS)

# ── Progress bar ──────────────────────────────────────────────────────────────
pct = int(done_count / total * 100)
st.markdown(f"""
<div style="margin-bottom:20px">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px">
    <span style="color:#fff;font-weight:600">{done_count}/{total} lessons completed</span>
    <span style="color:#00d4aa;font-weight:700">{pct}%</span>
  </div>
  <div style="background:#1e2d40;border-radius:99px;height:8px">
    <div style="background:linear-gradient(90deg,#00d4aa,#4299e1);
        width:{pct}%;height:8px;border-radius:99px;transition:width .4s"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Lesson cards ──────────────────────────────────────────────────────────────
section("📚 Lessons")
card_cols = st.columns(3, gap="small")
for idx, (lid, lesson) in enumerate(LESSONS.items()):
    is_done = lid in st.session_state.lessons_done
    qs      = st.session_state.quiz_scores.get(lid)
    badge   = ""
    if is_done:
        badge = f'<span style="background:#00d4aa22;color:#00d4aa;padding:2px 8px;border-radius:99px;font-size:.7rem">✓ Done</span>'
        if qs is not None:
            badge += f' <span style="color:#8892a4;font-size:.7rem">{qs}/3 quiz</span>'

    with card_cols[idx % 3]:
        st.markdown(f"""
        <div class="lesson-card" style="{'border-color:#00d4aa22' if is_done else ''}">
          <div class="lesson-emoji">{lesson['emoji']}</div>
          <div class="lesson-title">{lesson['title']}</div>
          <div class="lesson-desc">{lesson['summary']}</div>
          <div style="margin-top:8px">{badge}</div>
        </div>
        """, unsafe_allow_html=True)
        btn_label = "Review →" if is_done else "Start →"
        if st.button(btn_label, key=f"lesson_btn_{lid}", use_container_width=True):
            st.session_state["active_lesson"] = lid
            st.rerun()

# ── Active lesson view ────────────────────────────────────────────────────────
active = st.session_state.get("active_lesson")
if active and active in LESSONS:
    lesson = LESSONS[active]
    st.divider()
    section(f"{lesson['emoji']} {lesson['title']}")

    # Content
    with st.expander("📖 Read the lesson", expanded=True):
        st.markdown(lesson["content"])
        if st.button("✅ Mark as Read", key=f"read_{active}", type="primary"):
            st.session_state.lessons_done.add(active)
            st.success("Lesson marked as complete!")

    # Quiz
    st.markdown("### 🧠 Quick Quiz")
    quiz = lesson["quiz"]
    answers = {}
    all_answered = True
    for i, q in enumerate(quiz):
        choice = st.radio(
            f"**Q{i+1}.** {q['q']}",
            options=q["options"],
            key=f"quiz_{active}_{i}",
            index=None,
        )
        answers[i] = choice
        if choice is None:
            all_answered = False

    if st.button("Submit Quiz", key=f"submit_{active}", type="primary",
                 disabled=not all_answered):
        score = sum(1 for i, q in enumerate(quiz) if answers[i] == q["answer"])
        st.session_state.quiz_scores[active] = score
        st.session_state.lessons_done.add(active)

        if score == 3:
            st.balloons()
            st.success(f"🏆 Perfect score! {score}/3 — You've got this!")
        elif score >= 2:
            st.success(f"✅ Good job! {score}/3 correct")
        else:
            st.warning(f"📚 {score}/3 — Review the lesson and try again.")

        for i, q in enumerate(quiz):
            is_correct = answers[i] == q["answer"]
            icon = "✅" if is_correct else "❌"
            st.markdown(f"""
            <div style="background:{'#00d4aa11' if is_correct else '#ff475711'};
                border:1px solid {'#00d4aa44' if is_correct else '#ff475744'};
                border-radius:8px;padding:10px 14px;margin:6px 0;font-size:.86rem">
              {icon} <b>Q{i+1}:</b> {q['q']}<br>
              <span style="color:{'#00d4aa' if is_correct else '#ff4757'}">
                Your answer: {answers[i]}
              </span>
              {'<br><span style="color:#8892a4">ℹ️ ' + q['explanation'] + '</span>' if not is_correct else ''}
            </div>
            """, unsafe_allow_html=True)

    if st.button("← Back to all lessons", key=f"back_{active}"):
        del st.session_state["active_lesson"]
        st.rerun()

# ── Glossary ─────────────────────────────────────────────────────────────────
section("📖 Glossary")
search = st.text_input("Search a term…", placeholder="P/E, dividend, beta…", key="gloss_search")
terms = {k: v for k, v in GLOSSARY.items()
         if not search or search.lower() in k.lower() or search.lower() in v.lower()}

gcols = st.columns(2, gap="small")
for i, (term, defn) in enumerate(terms.items()):
    with gcols[i % 2]:
        st.markdown(f"""
        <div style="background:#131720;border:1px solid #1e2d40;border-radius:10px;
            padding:12px 16px;margin-bottom:10px">
          <div style="color:#00d4aa;font-weight:700;margin-bottom:4px">{term}</div>
          <div style="color:#8892a4;font-size:.84rem">{defn}</div>
        </div>
        """, unsafe_allow_html=True)

if not terms:
    st.caption("No matching terms found.")
