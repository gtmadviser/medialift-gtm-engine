# medialift-gtm-engine

A **GTM workspace** you drive with **Claude Code or Codex**, or with copy-paste prompts in ChatGPT. Built for the **Media Lift × GTM Adviser workshop** (nextMedia.Hamburg, Batch 8, 10 November 2026).

Strategy first, then tactics. Point an agent at this repo and it helps you count your market, sharpen your ICP, write your positioning, design an offer that turns conversations into deals, and then do the repetitive work: account research, lead lists, message variants and a paused campaign.

> Everything is real and yours to keep. Nothing sends unless you launch it.

---

## What you can do here

**Strategy (no keys needed)**

1. **Map your market** (`prompts/market-map.md`): count the organizations that could buy and list them by name. → `output/market-map.md` + `output/accounts.csv`
2. **Sharpen your ICP** (`prompts/icp.md`): best-fit vs worst-fit, buyer vs user vs blocker, the trigger. → `output/icp.md` + `output/icp.json`
3. **Write your positioning** (`prompts/positioning.md`): against the real alternative, in one sentence. → `output/positioning.md`
4. **Design the first yes** (`prompts/offer-pricing.md`): a small, paid next step, a pilot with a success metric, and a price test. → `output/offer.md`
5. **Find partners** (`prompts/partner-research.md`): for B2B2C and B2C, the organizations that already own your customer relationship. → `output/partners.md`

**Tactics**

6. **Research an account** (`prompts/account-research.md`): signals, trigger, people, fit score. → `output/account-<name>.md`
7. **Write messages + an A/B test** (`prompts/messaging-ab.md`, `prompts/copy.md`): two variants that differ in one thing. → `output/campaign.md`
8. **Source a list and stage a campaign** (`prompts/sourcing.md`, `prompts/lemlist.md`): real decision-makers via the Blitz API, a paused campaign in lemlist. Needs your own keys. → `output/leads.csv`
9. **Plan your next experiment** (`prompts/experiment.md`): one hypothesis, one metric, an end date. → `output/experiment.md`

It also knows the **stack**: ask "what should I use for X?" and it points you to the tool Emanuel actually runs (`RECOMMENDED-STACK.md`).

---

## Setup (a few minutes)

1. **An agent.** [Claude Code](https://www.anthropic.com/claude-code) (`npm install -g @anthropic-ai/claude-code`, then `claude`) **or** [Codex](https://openai.com/codex).
   No coding agent? Open `chatgpt/prompts.md` and paste the prompts into ChatGPT or Claude in the browser.
2. **Get the repo.**
   ```bash
   git clone https://github.com/gtmadviser/medialift-gtm-engine && cd medialift-gtm-engine
   ```
3. **Keys, only for outbound.** The strategy skills need none. For lead lists and campaigns:
   ```bash
   cp .env.example .env
   ```
   Paste your own **BLITZAPI_API_KEY** (https://app.blitz-api.ai) and **LEMLIST_API_KEY** (lemlist → Settings → Integrations → API). `.env` is gitignored, never commit it.

No pip installs, standard library only.

---

## Run it

```bash
claude        # or: codex
```

Then, for example:

> "Read CLAUDE.md. Our product is ___ and it helps ___. Start with a market map, then sharpen our ICP."

> "Read CLAUDE.md. We have conversations but they don't close. Help us design a small, paid first step and a price test."

> "Read CLAUDE.md. Research **<target account>** as a potential customer and write two message variants for an A/B test."

---

## Definition of done (after the workshop)

- [ ] `market-map.md`: how many accounts can buy, and the motion that fits that number
- [ ] `icp.md`: one card with best/worst fit, buyer vs user, trigger
- [ ] `positioning.md`: one sentence you would say to a buyer
- [ ] `offer.md`: the small, paid first yes and the price you will test
- [ ] `experiment.md`: one experiment until 26 November, with a metric close to money

See `examples/` for what "done" looks like.

---

## Repo map

```
README.md                    you are here
CLAUDE.md                    the brain: skills, workflow, guardrails the agent follows
AGENTS.md                    Codex entry point (points at CLAUDE.md)
DEMO.md                      the live walkthrough from the workshop
RECOMMENDED-STACK.md         tools, with referral links
chatgpt/prompts.md           copy-paste prompts for ChatGPT / Claude in the browser
prompts/market-map.md        count and list your market
prompts/icp.md               ICP, buyer vs user, trigger
prompts/positioning.md       positioning against the real alternative
prompts/offer-pricing.md     the first yes, pilots, price tests
prompts/partner-research.md  partners who own your customer (B2B2C, B2C)
prompts/account-research.md  research one account, score the fit
prompts/messaging-ab.md      message variants and a clean A/B test
prompts/copy.md              copy rules learned from real campaigns
prompts/experiment.md        one experiment, one metric, an end date
prompts/sourcing.md          real lists via the Blitz API (free fallback)
prompts/blitzapi.md          Blitz API contract
prompts/lemlist.md           lemlist API contract
scripts/                     source_leads.py, push_to_lemlist.py, scrape_example.py
data/                        icp.example.json, leads_template.csv
examples/                    worked examples
output/                      your work lands here (gitignored)
```

## Go deeper

- Slides, agenda and the full stack: **medialift.gtmadviser.com**
- Want this built and run *for* you? That is what [GTM Adviser](https://gtmadviser.com) does. Book a call: https://cal.com/emanuel-morhard/30min
