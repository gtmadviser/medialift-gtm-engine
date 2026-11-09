# Start here: the founder brief

Goal: capture once, in the repo, what every other skill needs to know. After this the founder never has to explain the company again, and every artifact is written for *their* case.

Run this the first time a founder opens the repo, and whenever `output/brief.md` is missing.

## How to run the interview

- Ask in **three short rounds**, not one long form. Wait for the answers after each round.
- Take answers in German or English, in any shape (bullets, a pasted pitch deck text, a website URL you then read).
- If something is on their website, read it instead of asking.
- Never fill a gap with a guess. Write `OPEN:` next to what is unknown, and ask again later when it matters.
- Reflect back in two sentences after each round so the founder can correct you early.

**Round 1: product and stage**
1. What is the product, in one sentence a customer would use?
2. Who is it for, and what painful problem does it solve for them?
3. Where are you today: paying customers, pilots, pre-orders, conversations? Rough numbers.

**Round 2: who buys**
4. Who pays? Directly (B2B or B2C), or through a partner who owns the customer (B2B2C)?
5. Your 3 best-fit customers or conversations, and 3 that looked right but went nowhere. What was different?
6. In a typical deal: who uses it, who signs, who can block it?

**Round 3: where it is stuck**
7. Where do conversations stall: no reply, no next step, price, the wrong person, timing?
8. What would a customer do if you did not exist (the real alternative)?
9. What is the smallest step you could ask a prospect to pay for or commit to?
10. How do customers find you today, and which channel do you want to make work next?

## Pick the archetype

From the answers, name the one that fits and tell the founder what it means for them. It decides which skills matter most.

| Archetype | Typical for | What to do first |
|---|---|---|
| **Small B2B market** (under a few hundred accounts) | tools for newsrooms, broadcasters, production companies, publishers | `market-map` (list accounts by name), then `network` to find warm paths into each account |
| **Larger B2B market** | tools for marketing, community or HR teams in many companies | `icp` with a hard trigger, then segment tests of 25 to 50 |
| **B2B2C** (a partner owns the end customer) | health, care, education, anything sold through an institution | `partner-research`, then `network` filtered for partner organisations |
| **B2C premium** (few, high-value customers) | services for affluent or niche audiences | `partner-research` (who already has their trust), `offer-pricing` with a deposit or pre-order |

## Write the files (this is the point of the skill)

1. **`output/brief.md`** from `data/brief.template.md`. Keep the founder's own words for pain and alternative.
2. **`output/icp.md`**: the one-paragraph ICP card (format in `prompts/icp.md`). If the founder gave several different ICPs, say so and make them pick one to work on first. List the others under "Later".
3. **`output/icp.json`**: the machine-readable version (shape in `data/icp.example.json`), including the `network` block the network filter uses.

Then show the founder the three files in a short summary and ask: "What is wrong or missing?" Fix it right away.

## Keep it current (applies to every skill)

`output/brief.md` is the single source of truth about the company. Whenever the founder tells you something that changes it (a new ICP, a price, a lost deal and why, a new partner), update the brief, `icp.md` and `icp.json` in the same turn and add one line to the "Change log" at the bottom of the brief with the date and what changed. Do not let the files drift apart. Every other skill reads the brief first and does not ask again for what is already in it.

## Then move

End with one recommendation, not a menu: the next skill for their archetype and why. For most founders in this programme, whose customers come through network and intros, that is `prompts/network.md`.
