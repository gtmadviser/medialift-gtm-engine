#!/usr/bin/env python3
"""
Verify and enrich the people on your network shortlist.

The LinkedIn export only knows what your contact typed into LinkedIn at some
point. Before you write to someone, check their current role. This script
looks up each profile by its LinkedIn URL and stores current title, company,
headline and location. Pick the provider you have a key for:

    --provider blitz    Blitz API     BLITZAPI_API_KEY   fast, misses are free
    --provider harvest  HarvestAPI    HARVEST_API_KEY    live profile scrape, freshest
    --provider aiark    AI Ark        AI_ARK_API_KEY     profile plus verified email

Usage:
    python3 scripts/network_enrich.py --top 40                 # top 40 of the shortlist, Blitz
    python3 scripts/network_enrich.py --top 40 --provider harvest
    python3 scripts/network_enrich.py --top 20 --emails        # Blitz: also find work emails
    python3 scripts/network_enrich.py --all-network --top 300  # enrich output/network.csv instead

Results are cached in output/network_enrichment.json, so a rerun never pays
twice for the same person. Afterwards run network_filter.py again: it picks
up the fresh data. Standard library only.
"""

import argparse
import datetime
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from netlib import (ENRICH_CACHE, NETWORK_CSV, SHORTLIST_CSV, load_env_key,  # noqa: E402
                    load_json, read_csv, save_json)

socket.setdefaulttimeout(40)
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


class Miss(Exception):
    """Provider answered, but does not know this person."""


def http_json(method, url, headers, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if e.code == 429 and attempt < 3:
                time.sleep(int(e.headers.get("Retry-After") or 5))
                continue
            if e.code in (401, 403):
                sys.exit("ERROR: the provider rejected your key or plan (HTTP %d): %s"
                         % (e.code, body[:200]))
            try:
                return e.code, json.loads(body or "{}")
            except ValueError:
                return e.code, {"raw": body[:200]}
        except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
            if attempt == 3:
                raise Miss("network error: %s" % e)
            time.sleep(2)
    raise Miss("gave up after retries")


# ---- providers: each returns {title, company, headline, location, email, company_linkedin_url}

def blitz_lookup(key, url, want_email):
    headers = {"x-api-key": key, "Content-Type": "application/json"}
    status, body = http_json("POST", "https://api.blitz-api.ai/v2/enrichment/person",
                             headers, {"person_linkedin_url": url})
    if status != 200 or not body.get("found"):
        raise Miss(body.get("message") or "not found")
    person = body.get("person") or {}
    current = next((e for e in person.get("experiences") or [] if e.get("job_is_current")), {})
    loc = person.get("location") or {}
    out = {
        "title": current.get("job_title") or "",
        "company": current.get("company_name") or "",
        "company_linkedin_url": current.get("company_linkedin_url") or "",
        "headline": person.get("headline") or "",
        "location": ", ".join(x for x in [loc.get("city"), loc.get("country_code")] if x),
        "email": "",
    }
    if want_email:
        time.sleep(0.25)
        status, mail = http_json("POST", "https://api.blitz-api.ai/v2/enrichment/email",
                                 headers, {"person_linkedin_url": url})
        if status == 200 and mail.get("found"):
            out["email"] = mail.get("email") or ""
    return out


def harvest_lookup(key, url, want_email):
    query = urllib.parse.urlencode({"url": url, "main": "true"})
    status, body = http_json("GET", "https://api.harvest-api.com/linkedin/profile?" + query,
                             {"X-API-Key": key, "User-Agent": BROWSER_UA})
    el = body.get("element") or {}
    if status != 200 or not el:
        raise Miss(str(body.get("error") or "not found")[:120])
    positions = el.get("currentPosition") or []
    if not positions:  # can be empty even when the person is employed
        first = (el.get("experience") or [{}])[0]
        if ((first.get("endDate") or {}).get("text") or "") == "Present":
            positions = [first]
    current = positions[0] if positions else {}
    loc = el.get("location") or {}
    return {
        "title": current.get("position") or "",
        "company": current.get("companyName") or "",
        "company_linkedin_url": current.get("companyLinkedinUrl") or "",
        "headline": el.get("headline") or "",
        "location": (loc.get("parsed") or {}).get("text") or loc.get("linkedinText") or "",
        "email": "",
    }


def aiark_lookup(key, url, want_email):
    # AI Ark's single export returns profile + verified email and answers 404
    # (no charge) when it finds no valid email for the person.
    status, body = http_json(
        "POST", "https://api.ai-ark.com/api/developer-portal/v1/people/export/single",
        {"X-TOKEN": key, "Content-Type": "application/json"}, {"url": url})
    if status != 200:
        raise Miss("no verified email on file (HTTP %d)" % status)
    profile = body.get("profile") or {}
    company = body.get("company") or {}
    email = body.get("email")
    if isinstance(email, dict):
        email = email.get("email") or email.get("address") or email.get("value") or ""
    return {
        "title": profile.get("title") or "",
        "company": (company.get("summary") or {}).get("name") or "",
        "company_linkedin_url": (company.get("link") or {}).get("linkedin") or "",
        "headline": profile.get("headline") or "",
        "location": (body.get("location") or {}).get("default") or "",
        "email": email or "",
    }


PROVIDERS = {
    "blitz": ("BLITZAPI_API_KEY", "Get one at https://app.blitz-api.ai", blitz_lookup, 0.25),
    "harvest": ("HARVEST_API_KEY", "Get one at https://harvest-api.com", harvest_lookup, 0.1),
    "aiark": ("AI_ARK_API_KEY", "Get one in your AI Ark account (API needs a paid plan)",
              aiark_lookup, 0.3),
}


def main():
    ap = argparse.ArgumentParser(description="Verify and enrich your network shortlist.")
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default="blitz")
    ap.add_argument("--top", type=int, default=40, help="how many people to look up (default 40)")
    ap.add_argument("--emails", action="store_true", help="Blitz only: also find verified work emails")
    ap.add_argument("--all-network", action="store_true",
                    help="enrich output/network.csv instead of the shortlist")
    ap.add_argument("--refresh", action="store_true", help="look up again even if cached")
    args = ap.parse_args()

    source = NETWORK_CSV if args.all_network else SHORTLIST_CSV
    if not os.path.exists(source):
        sys.exit("ERROR: %s not found. Run network_import.py and network_filter.py first."
                 % os.path.relpath(source))
    env_name, hint, lookup, pause = PROVIDERS[args.provider]
    key = load_env_key(env_name, hint)

    rows = [r for r in read_csv(source) if r.get("linkedin_url")][:args.top]
    cache = load_json(ENRICH_CACHE, {}) or {}
    todo = [r for r in rows if args.refresh or r["linkedin_url"].lower() not in cache]
    print("%d people selected, %d already cached, %d to look up via %s"
          % (len(rows), len(rows) - len(todo), len(todo), args.provider))

    found = missed = changed = 0
    for i, row in enumerate(todo, 1):
        url = row["linkedin_url"]
        entry = {"provider": args.provider, "found": False,
                 "fetched_at": datetime.date.today().isoformat()}
        try:
            entry.update(lookup(key, url, args.emails))
            entry["found"] = True
            found += 1
            old = (row.get("company") or "").casefold().strip()
            new = (entry.get("company") or "").casefold().strip()
            moved = bool(old and new and old not in new and new not in old)
            changed += moved
            print("  %3d/%d  %s: %s @ %s%s" % (
                i, len(todo), row.get("full_name") or url, entry.get("title") or "?",
                entry.get("company") or "?", "   <- changed job" if moved else ""))
        except Miss as e:
            missed += 1
            entry["note"] = str(e)[:120]
            print("  %3d/%d  %s: not found (%s)" % (i, len(todo), row.get("full_name") or url, e))
        cache[url.lower()] = entry
        if i % 10 == 0:
            save_json(ENRICH_CACHE, cache)
        time.sleep(pause)
    save_json(ENRICH_CACHE, cache)

    print("\nDone. %d found, %d not found, %d have changed company since the export."
          % (found, missed, changed))
    print("Cached in output/network_enrichment.json. Now run again:\n"
          "  python3 scripts/network_filter.py")


if __name__ == "__main__":
    main()
