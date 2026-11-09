# Your network first: find buyers, partners and intros among your LinkedIn connections

Most early customers come through network and intros. Before any cold outreach, look at who you already know. A founder with 1,000 connections usually has 20 to 60 people in there who are a buyer, work at a possible partner, or can open a door. This skill finds them.

Nothing here sends anything, and the connection data never leaves the machine: `data/private/` and `output/` are gitignored.

## Step 1: export your connections (start this first, it takes about 10 minutes to arrive)

Tell the founder exactly this:

1. LinkedIn → click your photo (**Me**) → **Settings & Privacy**
2. **Data privacy** → **Get a copy of your data**
3. Choose **"Want something in particular?"**, tick **Connections** only → **Request archive**
4. LinkedIn emails a download link after roughly 10 minutes. Download, unzip, and put `Connections.csv` into `data/private/` in this repo.

Every co-founder can do this. Several files are merged automatically.

While they wait, do Step 2.

## Step 2: make sure the ICP is in the repo

If `output/brief.md` does not exist, run `prompts/start-here.md` first. Then check that `output/icp.json` has a `network` block (shape in `data/icp.example.json`). If not, write it together with the founder. Ask these four things, give examples from their brief, and turn the answers into lowercase keywords:

1. **Buyers.** Which kinds of organisations buy, and which roles sign? → `buyer_company_keywords`, `buyer_titles`
2. **Partners.** Which organisations already have your end customer's trust or attention? Which roles own partnerships there? → `partner_company_keywords`, `partner_titles`
3. **Connectors.** Who knows many of your buyers: investors, advisors, consultants, journalists, association people, alumni of a target company? → `connector_keywords`
4. **Exclude.** Own company, competitors, existing customers, students, recruiters. → `exclude_companies`, `exclude_keywords`

Keyword rules:
- Short and general beats long and exact: `rundfunk` finds "Norddeutscher Rundfunk" and "Bayerischer Rundfunk". `verlag` finds every publisher.
- Add German and English forms: `chefredakt` (matches Chefredakteur and Chefredakteurin), `editor-in-chief`.
- Add the names of the accounts from `output/accounts.csv` and the partners from `output/partners.md` as company keywords. That is how the market map and the network connect.
- Per archetype (from the brief):
  - **Small B2B market:** company keywords are the account names themselves, plus the category word. Anyone at a target account is interesting, even a non-buyer, because they can tell you who decides.
  - **B2B2C:** the partner block matters most. The partner is the customer you sell to first.
  - **B2C premium:** look for people at organisations that already serve your audience, and for connectors with reach into it. Do not try to find end customers by job title.
  - **Larger B2B market:** titles matter more than company names. Keep company keywords to the industry word.

## Step 3: import and filter (free, no keys)

```bash
python3 scripts/network_import.py     # reads data/private/Connections*.csv -> output/network.csv
python3 scripts/network_filter.py     # -> output/network_shortlist.csv
```

Read the import summary with the founder first: the companies where they know the most people are often a surprise, and a signal.

The filter labels each match `buyer`, `partner` or `connector`, with a score and a plain reason in the `why` column. It is a keyword screen. It finds candidates, it does not decide.

**Now use judgment.** Read the top 30 to 50 rows and:
- remove false positives (a keyword matched but the person is clearly not relevant), and say which keyword caused it
- if good people are missing, loosen the keywords in `icp.json` and run the filter again. Two or three rounds are normal.
- update `output/brief.md` if this changes what the founder believes about the ICP or the partners (see "Keep it current" in `prompts/start-here.md`)

## Step 4 (optional, needs one key): verify before you write

The export only shows the company and position a contact entered at some point. People change jobs. Verify the top of the shortlist before writing to anyone:

```bash
python3 scripts/network_enrich.py --top 40                     # Blitz API (BLITZAPI_API_KEY)
python3 scripts/network_enrich.py --top 40 --provider harvest  # HarvestAPI (HARVEST_API_KEY), live scrape
python3 scripts/network_enrich.py --top 40 --provider aiark    # AI Ark (AI_ARK_API_KEY), profile + email
python3 scripts/network_filter.py                              # run again, it uses the fresh data
```

- Which provider? Use the one the founder has a key for. Blitz is fast and does not charge for misses. HarvestAPI scrapes the live profile, so it is the freshest and finds people Blitz does not know. AI Ark returns a verified email with the profile and only answers when it has one.
- Results are cached in `output/network_enrichment.json`, so nobody is looked up twice.
- Enrich the shortlist, not the whole network. 40 people cost cents. Thousands cost money and add nothing.
- Lines marked `<- changed job` are worth a look: a contact who just moved into a buyer role at a target account is the best trigger there is.
- For first-degree connections you rarely need an email. You can message them on LinkedIn directly. Add `--emails` (Blitz) only if the founder wants an email channel too.

## Step 5: turn the shortlist into action

Write `output/network-plan.md`:

1. **Top 10 to write to this week**, each with: who, why them, the ask, and the first message.
2. **Intro paths:** for each Tier 1 account in `output/accounts.csv` with no direct contact, the connection who is closest to it and what to ask them for.
3. **Partners:** the contacts at partner organisations, with the partner pitch from `prompts/partner-research.md`.

Message rules for people you already know (on top of `prompts/copy.md`):
- It is a warm message, so write like one. Reference how you know each other in the first line. No pitch deck tone.
- One ask, and make it easy to say yes to. Three asks that work:
  - **Advice ask** (to a buyer-type contact): "You have run a newsroom for years. Could I show you what we are building for 15 minutes and hear where you would poke holes?"
  - **Intro ask** (to a connector): name the exact person or role and offer two forwardable sentences they can paste.
  - **Partner ask** (to a partner contact): their members' situation, what the members get, a small pilot.
- Never ask a connector to "spread the word". Ask for one named intro.
- 40 to 60 words. German *Du* or *Sie* as the founder would actually address this person.

Then offer the tracker: `python3 scripts/sheet_export.py` and `prompts/gsheet.md`.

## Guardrails

- The connection export is personal data of other people. It stays in `data/private/` and `output/`, both gitignored. Never commit it, never paste the full list into a chat or a public tool.
- No automated messages to the network. The founder sends every warm message by hand. A burned warm contact does not come back.
- Do not present a keyword match as a fact about a person. Say "looks like", then verify.
