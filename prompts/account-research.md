# Account / deal research

Goal: turn a target company name into a **decision-ready briefing**, what they do, the signal that says "now", the people to reach, how your product maps to their pain, and an honest **fit / priority score**. This is the "deal analysis" skill: useful before an outbound push, before a first call, or to score a list of accounts.

Use your built-in **web search + fetch**. Public sources only, be polite. No paid API needed for one account; for doing this across hundreds, see the stack note at the end.

> **Before you start**, you need the operator's product context: what it is, who it's for, the painful problem it solves, and the realistic next step (pilot, POC, intro call). Without it you can't judge fit.

## The steps

1. **Identify the company.** Official website + LinkedIn company page + domain. Confirm you have the right entity (watch for same-name companies, the wrong country, parent vs subsidiary).
2. **Firmographics.** What they do in one line, product/category, customer type (who *they* sell to), employee size band, HQ + key geos, funding stage / ownership, and rough maturity.
3. **Signals, the "why now".** Hunt for a trigger in the last ~6 months. Check each quickly and note the source + date:
   | Signal | Where to look |
   |---|---|
   | New funding / round | news, Crunchbase, "we raised" posts |
   | Hiring for a relevant role | careers page, LinkedIn Jobs |
   | Leadership change / new exec | LinkedIn, press |
   | Product launch / expansion / new market | their blog, socials, news |
   | Tech they use (or a gap) | their site, job posts, BuiltWith |
   | Public complaint / review theme | G2, Trustpilot, socials |
4. **Map to your product.** Given their context, what is their likely pain, and where does your product fit? Be specific and honest, name the one use case that matters most to *this* account.
5. **People to reach.** The likely economic buyer, the champion, and the day-to-day user/owner of the problem. Give role + name where public + LinkedIn URL where public. Note who to open with and why.
6. **Score the fit (1–5) and say why.** 5 = textbook ICP with a live trigger; 1 = poor fit / disqualified. State the reasoning in one or two lines and list any **disqualifiers** (too big/small, wrong geo, no budget, competitor-locked).
7. **Recommend the next action** + draft one **personalized opener** (follow `prompts/copy.md`: scenario-first, one soft CTA, no em-dashes, no fake stats).

## Output (write to `output/account-<slug>.md`)

```markdown
# <Company> — account briefing
Fit score: <1-5> · Priority: <high/med/low> · Researched: <date>

## What they do
<one or two lines: product, who they sell to, size, geo, stage>

## Why now (signals)
- <signal> — <source/date>
- <signal> — <source/date>

## Where we fit
<the one use case + the likely pain, in their terms>

## Who to reach
- <Name>, <Role> — <linkedin_url> — open with this person because <reason>
- <Name>, <Role> — <linkedin_url>

## Fit + disqualifiers
<why this score; what would kill the deal>

## Next action + opener
<recommended next step>

> <2-3 line personalized opener, ready to adapt>
```

Keep it tight, a briefing someone can act on in two minutes. Every claim should have a source or be marked as an assumption. If you can't find a real trigger, say so and score the fit lower; don't invent one.

## Doing this at scale
For one account, this prompt + web search is enough. To research and **score a whole list** automatically (the "signaling tool" pattern, ICP rating + news scrape per company), the workhorses are **Clay** (enrichment + AI columns + scoring) and **Trigify** (social/buying signals). Ask "what should I use to score accounts at scale?" and the agent will surface them from `RECOMMENDED-STACK.md`.
