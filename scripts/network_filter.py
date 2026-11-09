#!/usr/bin/env python3
"""
Filter your LinkedIn network against your ICP: who is a buyer, who is a
partner, who can introduce you.

Reads output/network.csv (from network_import.py) and the "network" block in
output/icp.json (the agent writes it with you, see prompts/network.md).
If output/network_enrichment.json exists (from network_enrich.py), the fresher
title, company, headline and location from there are used as well.

Usage:
    python3 scripts/network_filter.py              # writes output/network_shortlist.csv
    python3 scripts/network_filter.py --top 100    # keep the best 100 (default 150)
    python3 scripts/network_filter.py --min-score 3

This is a keyword screen, on purpose: it is free, fast and explainable. It
finds candidates. You and the agent then read the top rows and decide.
No API key and no pip installs needed.
"""

import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from netlib import (ENRICH_CACHE, ICP_JSON, NETWORK_CSV, SHORTLIST_CSV,  # noqa: E402
                    load_json, read_csv, write_csv)

SHORTLIST_FIELDS = ["segment", "score", "full_name", "position", "company", "headline",
                    "location", "linkedin_url", "email", "connected_on", "why", "data_source"]

SENIOR = ["founder", "gründer", "co-founder", "ceo", "cto", "coo", "cmo", "cfo", "chief",
          "geschäftsführer", "geschäftsführerin", "managing director", "owner", "inhaber",
          "partner", "head of", "leiter", "leiterin", "leitung", "director", "direktor",
          "vp", "vice president", "chefredakteur", "chefredakteurin", "editor-in-chief",
          "vorstand", "president"]

# Used only when icp.json has no "network" block yet, so the script never ends at zero.
EMPTY_NETWORK = {
    "buyer_company_keywords": [], "buyer_titles": [],
    "partner_company_keywords": [], "partner_titles": [],
    "connector_keywords": [], "exclude_keywords": [], "exclude_companies": [],
}


def norm(text):
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def hits(keywords, text):
    """Keywords found in text. Short keywords (<= 3 chars) must match a whole word."""
    found = []
    for kw in keywords or []:
        k = norm(kw)
        if not k:
            continue
        if len(k) <= 3:
            if re.search(r"(?<![a-z0-9äöüß])" + re.escape(k) + r"(?![a-z0-9äöüß])", text):
                found.append(kw)
        elif k in text:
            found.append(kw)
    return found


def score_row(row, net):
    company = norm(row.get("company"))
    title = norm(row.get("position")) + " " + norm(row.get("headline"))
    everything = company + " " + title

    if company and any(norm(c) and norm(c) in company for c in net.get("exclude_companies", [])):
        return None
    if hits(net.get("exclude_keywords"), everything):
        return None

    senior = bool(hits(SENIOR, title))
    candidates = []

    b_company = hits(net.get("buyer_company_keywords"), company)
    b_title = hits(net.get("buyer_titles"), title)
    if b_company or b_title:
        s = 3 * bool(b_company) + 2 * bool(b_title) + (1 if senior else 0)
        why = []
        if b_company:
            why.append("works at a target organisation (%s)" % ", ".join(b_company[:3]))
        if b_title:
            why.append("buyer-type role (%s)" % ", ".join(b_title[:3]))
        candidates.append((s, "buyer", why))

    p_company = hits(net.get("partner_company_keywords"), company)
    p_title = hits(net.get("partner_titles"), title)
    if p_company:
        s = 3 + 2 * bool(p_title) + (1 if senior else 0)
        why = ["works at a possible partner (%s)" % ", ".join(p_company[:3])]
        if p_title:
            why.append("partnership-type role (%s)" % ", ".join(p_title[:3]))
        candidates.append((s, "partner", why))

    c_hits = hits(net.get("connector_keywords"), everything)
    if c_hits:
        s = 2 + (1 if senior else 0)
        candidates.append((s, "connector", ["can open doors (%s)" % ", ".join(c_hits[:3])]))

    if not candidates:
        return None
    candidates.sort(key=lambda c: -c[0])
    s, segment, why = candidates[0]
    if senior:
        why.append("senior")
    return s, segment, "; ".join(why)


def main():
    ap = argparse.ArgumentParser(description="Filter your LinkedIn network against your ICP.")
    ap.add_argument("--top", type=int, default=150, help="how many rows to keep (default 150)")
    ap.add_argument("--min-score", type=int, default=2, help="drop rows below this score (default 2)")
    ap.add_argument("--config", default=ICP_JSON, help="path to icp.json")
    args = ap.parse_args()

    if not os.path.exists(NETWORK_CSV):
        sys.exit("ERROR: output/network.csv not found. Run python3 scripts/network_import.py first.")
    icp = load_json(args.config, {}) or {}
    net = dict(EMPTY_NETWORK)
    net.update(icp.get("network") or {})
    if not any(net.get(k) for k in ("buyer_company_keywords", "buyer_titles",
                                    "partner_company_keywords", "connector_keywords")):
        sys.exit('ERROR: no "network" block with keywords in %s.\n'
                 'Ask the agent: "read prompts/network.md and set up my network filter", '
                 'or copy the block from data/icp.example.json.' % os.path.relpath(args.config))

    rows = read_csv(NETWORK_CSV)
    cache = load_json(ENRICH_CACHE, {}) or {}
    shortlist = []
    for row in rows:
        fresh = cache.get((row.get("linkedin_url") or "").lower()) or {}
        if fresh.get("found"):
            row = dict(row)
            row["position"] = fresh.get("title") or row.get("position", "")
            row["company"] = fresh.get("company") or row.get("company", "")
            row["headline"] = fresh.get("headline", "")
            row["location"] = fresh.get("location", "")
            row["email"] = fresh.get("email") or row.get("email", "")
            row["data_source"] = "enriched via " + fresh.get("provider", "?")
        else:
            row = dict(row, data_source="linkedin export")
        result = score_row(row, net)
        if not result:
            continue
        score, segment, why = result
        if score < args.min_score:
            continue
        row.update(score=score, segment=segment, why=why)
        shortlist.append(row)

    order = {"buyer": 0, "partner": 1, "connector": 2}
    shortlist.sort(key=lambda r: (-r["score"], order[r["segment"]], r.get("company", "")))
    shortlist = shortlist[:args.top]
    write_csv(SHORTLIST_CSV, shortlist, SHORTLIST_FIELDS)

    counts = Counter(r["segment"] for r in shortlist)
    print("%d of %d connections match your ICP -> output/network_shortlist.csv" % (len(shortlist), len(rows)))
    print("  buyers: %d   partners: %d   connectors: %d" % (
        counts["buyer"], counts["partner"], counts["connector"]))
    print("\nTop 15:")
    for r in shortlist[:15]:
        print("  [%s %d] %s, %s @ %s" % (r["segment"], r["score"], r["full_name"],
                                         r.get("position") or "?", r.get("company") or "?"))
    if not shortlist:
        print("\nNothing matched. Loosen the keywords in the network block of icp.json "
              "(shorter, more general words) and run again.")
    else:
        print("\nNext: read the top rows with the agent, then optionally verify them:\n"
              "  python3 scripts/network_enrich.py --top 40\n"
              "  python3 scripts/sheet_export.py")


if __name__ == "__main__":
    main()
