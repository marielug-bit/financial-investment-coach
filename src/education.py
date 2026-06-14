"""Finance mini-lessons for the Learn Finance module."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

LESSONS: dict[str, dict] = {
    "1": {
        "title": "What is a Balance Sheet?",
        "content": """\
## What is a Balance Sheet?

Think of a balance sheet like a **snapshot photo of a company's finances** taken on one specific day.

It answers one simple question: *What does the company own, what does it owe, and what's left over?*

---

### The Three Parts

**Assets — What the company OWNS**
This includes cash in the bank, buildings, equipment, and money that customers still owe them.
Think of it like listing everything in your apartment: your laptop, furniture, and savings.

**Liabilities — What the company OWES**
These are the bills and debts the company needs to pay — loans from the bank, unpaid invoices, mortgages.
Like your credit card balance and rent you owe.

**Equity — What's LEFT OVER**
Equity = Assets − Liabilities. It's what the company is really "worth" to its owners.
If you sold everything and paid all debts, equity is what remains.

---

### The Golden Rule
A balance sheet must always balance:
> **Assets = Liabilities + Equity**

---

### Why Should You Care?
- A company with lots of debt compared to equity is **risky** — like someone drowning in credit card debt.
- A company with more assets than debts is **financially stable** — like someone with a paid-off house and savings.

---

### Key Numbers to Look At
| Number | What It Tells You |
|---|---|
| Total Debt | How much the company borrowed |
| Cash & Equivalents | Can they pay bills tomorrow? |
| Total Equity | The company's "net worth" |

**Beginner tip:** If a company's debt is more than 2× its equity, that's a yellow flag worth investigating.
""",
    },
    "2": {
        "title": "How to Read an Income Statement",
        "content": """\
## How to Read an Income Statement

If the balance sheet is a photo, the income statement is a **movie** — it shows everything that happened over a period of time (usually 3 months or 1 year).

It answers: *Did the company make or lose money?*

---

### The Journey from Sales to Profit

```
Revenue (all money coming in)
  − Cost of Goods Sold (cost to make the product)
  = Gross Profit

  − Operating Expenses (salaries, rent, marketing)
  = Operating Income (EBIT)

  − Interest on Debt
  − Taxes
  = Net Income ← This is the "bottom line"
```

---

### Key Terms Explained

**Revenue (aka Sales or Turnover)**
The total money customers paid the company. Like the total on a restaurant's till at end of day — before paying the chef, electricity, and rent.

**Gross Profit**
Revenue minus what it actually costs to make the product. A restaurant's gross profit = sales minus ingredient costs.

**Net Income**
The final profit after everything — salaries, taxes, interest on loans. This is what's left to grow the business or pay shareholders.

**EPS (Earnings Per Share)**
Net income divided by number of shares. Tells you how much profit each share of stock "earned."

---

### What to Look For

✅ **Revenue growing year over year** — the business is expanding
✅ **Net profit margin above 10%** — the company keeps a good chunk of every dollar earned
⚠️ **Revenue growing but net income shrinking** — costs are rising faster than sales
❌ **Negative net income** — the company is losing money

---

**Beginner tip:** A company can have growing revenue but still lose money. Always check net income, not just sales.
""",
    },
    "3": {
        "title": "What Makes a Good Investment?",
        "content": """\
## What Makes a Good Investment?

Investing is putting money to work so it can grow. But not every stock is worth buying. Here's how to think about it like a pro.

---

### The 4 Questions Every Investor Asks

**1. Does the business make sense?**
Can you explain what the company does in one sentence? If not, that's a red flag.
Good example: "Apple sells iPhones, Macs, and services to hundreds of millions of loyal customers."

**2. Is the company actually profitable?**
Look at net income. Is it positive? Is it growing? A company that never makes money is like a store that's always running a sale at a loss.

**3. Is the price reasonable?**
Even a great company can be a bad investment if you pay too much. The **P/E ratio** (Price-to-Earnings) is the main tool here.
- P/E of 15 = you pay $15 for every $1 of earnings. That's usually reasonable.
- P/E of 50 = very expensive. The company needs to grow a lot to justify it.

**4. Does it have a moat?**
A "moat" is something that protects the business from competition — like a castle moat. Examples:
- Brand loyalty (people pay a premium for Apple, Nike)
- Patents (pharmaceutical companies)
- Network effects (more users = more valuable, like Instagram)
- Low-cost advantage (Walmart)

---

### The Risk Spectrum

```
Lower Risk ←─────────────────────────────→ Higher Risk
Government   Blue-chip    Growth    Small-cap   Crypto
  Bonds       Stocks      Stocks     Stocks
```

As a beginner: **start in the middle**. Blue-chip stocks (Apple, Microsoft, Johnson & Johnson) are large, stable companies.

---

### Diversification — Your Best Friend
Never put all your money in one stock. Spread across different companies and industries.
Think of it like not putting all your eggs in one basket.

---

**Beginner tip:** Warren Buffett's rule: "Never invest in a business you cannot understand."
""",
    },
    "4": {
        "title": "The 5 Key Numbers to Always Check",
        "content": """\
## The 5 Key Numbers to Always Check

Before investing in any company, always look at these 5 numbers. They give you a fast health check.

---

### Number 1: Revenue Growth Rate
**What it is:** How fast is the company's sales growing year over year?
**Formula:** (This year's revenue − Last year's revenue) ÷ Last year's revenue × 100
**What's good:** 10%+ per year is solid. 20%+ is impressive for a large company.
**Red flag:** Revenue shrinking for 2+ years in a row.

---

### Number 2: Net Profit Margin
**What it is:** Out of every $1 in sales, how many cents does the company actually keep as profit?
**Formula:** Net Income ÷ Revenue × 100
**What's good:** Above 10% is healthy. Tech companies often hit 20-30%.
**Red flag:** Below 5% or getting smaller each year.

---

### Number 3: Debt-to-Equity Ratio
**What it is:** How much debt does the company carry compared to what it actually owns?
**Formula:** Total Debt ÷ Total Equity
**What's good:** Below 1.0 means more equity than debt — financially healthy.
**Red flag:** Above 2.0 means the company is heavily leveraged (risky if things go wrong).

---

### Number 4: P/E Ratio (Price-to-Earnings)
**What it is:** How much are investors paying for each dollar of profit?
**Formula:** Stock Price ÷ Earnings Per Share (EPS)
**What's good:** Compare to industry average. 15-25 is typical for stable companies.
**Red flag:** P/E above 50 means the stock is expensive — it needs strong future growth to justify the price.

---

### Number 5: Free Cash Flow
**What it is:** Cash left over after paying for operations and investments. This is the real money the company generates.
**Why it matters:** A company can show accounting profits but still be cash-poor. Free cash flow doesn't lie.
**What's good:** Positive and growing.
**Red flag:** Negative free cash flow for several years (unless the company is intentionally investing heavily in growth).

---

### Quick Reference Card

| # | Metric | Healthy Range | Red Flag |
|---|---|---|---|
| 1 | Revenue Growth | >10%/yr | Declining |
| 2 | Net Profit Margin | >10% | <5% |
| 3 | Debt/Equity | <1.0 | >2.0 |
| 4 | P/E Ratio | 15–25 | >50 |
| 5 | Free Cash Flow | Positive | Negative |

**Beginner tip:** You don't need to memorize formulas. Your financial coach will calculate these for you from any report you upload.
""",
    },
    "5": {
        "title": "What is a Stock and How Does Buying One Work?",
        "content": """\
## What is a Stock and How Does Buying One Work?

### What is a Stock?
A stock (also called a "share") is a tiny piece of ownership in a company.

When Apple has 15 billion shares outstanding and you buy 1 share, you own 1/15,000,000,000th of Apple. That makes you an actual part-owner of the company — you get to vote on some decisions and receive a portion of profits (called dividends) if the company pays them.

---

### Why Do Companies Sell Shares?
Companies sell shares to raise money without borrowing. Instead of going to a bank for a loan, they say: "We'll sell pieces of the company to the public." This is called an IPO (Initial Public Offering) — the first time shares become available to the public.

---

### How Do You Make Money From a Stock?

**Way 1: Price Appreciation**
You buy 1 share at $100. A year later it's worth $150. You sell it and pocket $50 profit.
This is called a **capital gain**.

**Way 2: Dividends**
Some companies pay shareholders a regular cash payment (quarterly or annually) just for holding the stock. Think of it like rent income if you owned an apartment building.

---

### What Makes a Stock Price Go Up or Down?
- Company earns more profit than expected → price usually goes up
- Company earns less than expected → price usually goes down
- Overall economy improves → many stocks go up
- Recession or bad news → many stocks go down
- Investor sentiment and emotions → prices can swing even without news

---

### The Buying Process (Simplified)
1. Open a brokerage account (Alpaca, Robinhood, Fidelity, etc.)
2. Deposit money
3. Search for the company by ticker symbol (AAPL for Apple, MSFT for Microsoft)
4. Place an order — specify how many shares
5. The order executes and you own the shares

**With this app:** You can practice with Alpaca's paper trading. Same process, but with fake money. No risk!

---

### Important Vocabulary

| Term | Meaning |
|---|---|
| Ticker | Short code for a stock (e.g., AAPL, TSLA) |
| Bull Market | Prices going up overall (optimism) |
| Bear Market | Prices going down overall (pessimism) |
| Portfolio | All the stocks you own combined |
| Dividend | Cash payment from company to shareholders |
| Broker | Platform where you buy/sell stocks |

**Beginner tip:** Never invest money you can't afford to lose. Start with paper trading (fake money) until you feel confident.
""",
    },
    "6": {
        "title": "How to Read Market News Without Panicking",
        "content": """\
## How to Read Market News Without Panicking

Financial news is designed to grab your attention — which means it's often scary or overly exciting. Here's how to read it calmly and rationally.

---

### The Most Important Rule
**Short-term noise ≠ long-term trend.**

Headlines like "Markets crash 3%!" sound terrifying. But if you zoom out to a 10-year chart, that 3% drop is barely visible. The stock market has recovered from every single crash in history — including the 2008 financial crisis and the 2020 pandemic.

---

### How to Read a News Article About a Stock

**Step 1: Who wrote it and why?**
Financial media makes money from clicks. Scary and exciting headlines get clicks. Always ask: is this analysis or is this designed to make me feel something?

**Step 2: Is this about the company's fundamentals or just sentiment?**
- Fundamentals = actual business results (revenue, profit, new products)
- Sentiment = people's feelings and expectations
Fundamentals matter more in the long run. Sentiment drives short-term swings.

**Step 3: What's the time frame?**
"Stock drops 5% today" is very different from "Stock drops 5% over 5 years." Always look at the time frame mentioned.

**Step 4: What's the source?**
- Company press releases: official but can be optimistic
- Analyst reports: professional opinions, but analysts are often wrong
- News articles: summarizing info, quality varies enormously

---

### Common Headlines Decoded

| Headline | What It Actually Means |
|---|---|
| "Markets in freefall!" | A normal correction — happens multiple times per year |
| "Stock soars after earnings beat" | Company did better than analysts guessed |
| "Investor sentiment turns bearish" | People are feeling pessimistic right now |
| "Fed raises rates — markets tumble" | Higher interest rates make bonds more attractive vs stocks |
| "Recession fears grip Wall Street" | Analysts worry the economy might slow down |

---

### The 3-Step Panic Check
When scary news makes you want to sell everything, ask:
1. **Has the actual business changed?** (Not the stock price — the business)
2. **Is this temporary or permanent?** (Pandemic = temporary; industry dying = permanent)
3. **Would I be happy buying this stock at this lower price?** (If yes, stay calm or even buy more)

---

### What Long-Term Investors Actually Do
- They read news to stay informed, not to react
- They don't check their portfolio every day
- They know that time in the market beats timing the market

---

**Beginner tip:** Set a rule for yourself — you won't make any buy or sell decision within 24 hours of reading scary news. Sleep on it first.
""",
    },
}


def run_education_menu() -> None:
    """Display the Learn Finance menu and let user pick a lesson."""
    while True:
        console.print("\n[bold]Learn Finance[/bold]")
        console.print("  Choose a lesson:\n")
        for key, lesson in LESSONS.items():
            console.print(f"  {key}. {lesson['title']}")
        console.print("  0. Back to main menu")

        choice = Prompt.ask("\n  Your choice", default="0")

        if choice == "0":
            break

        if choice in LESSONS:
            lesson = LESSONS[choice]
            console.print(Panel(
                Markdown(lesson["content"]),
                title=f"[bold blue]{lesson['title']}[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            ))
            Prompt.ask("\n  Press Enter to continue", default="")
        else:
            console.print("  [red]Invalid choice.[/red]")
