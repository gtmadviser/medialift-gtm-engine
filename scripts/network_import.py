#!/usr/bin/env python3
"""
Import your LinkedIn connections export into this repo.

LinkedIn: Settings & Privacy -> Data privacy -> Get a copy of your data ->
tick "Connections" -> Request archive. The email with the download arrives
after roughly 10 minutes. Unzip it and put Connections.csv into data/private/.

Usage:
    python3 scripts/network_import.py                         # finds data/private/Connections*.csv
    python3 scripts/network_import.py ~/Downloads/Connections.csv
    python3 scripts/network_import.py a.csv b.csv             # merge several founders

Writes output/network.csv (gitignored, it never leaves your machine) and
prints a short summary. No API key and no pip installs needed.
"""

import csv
import glob
import io
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from netlib import (NETWORK_CSV, NETWORK_FIELDS, REPO_ROOT,  # noqa: E402
                    normalize_linkedin_url, write_csv)

# LinkedIn's export header. Kept flexible in case LinkedIn renames a column.
COLUMN_ALIASES = {
    "first_name": ["first name", "vorname"],
    "last_name": ["last name", "nachname"],
    "linkedin_url": ["url", "profile url", "linkedin url"],
    "email": ["email address", "e-mail-adresse", "email"],
    "company": ["company", "unternehmen"],
    "position": ["position"],
    "connected_on": ["connected on", "verbunden am"],
}


def find_default_inputs():
    patterns = ["data/private/Connections*.csv", "data/private/connections*.csv",
                "data/Connections*.csv", "Connections*.csv"]
    found = []
    for pattern in patterns:
        found.extend(sorted(glob.glob(os.path.join(REPO_ROOT, pattern))))
    return found


def read_export(path):
    """LinkedIn puts a few 'Notes:' lines above the real header. Skip them."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.read().splitlines()
    header_index = None
    for i, line in enumerate(lines[:20]):
        low = line.lower()
        if ("first name" in low or "vorname" in low) and ("url" in low):
            header_index = i
            break
    if header_index is None:
        sys.exit("ERROR: %s does not look like a LinkedIn Connections export "
                 "(no header row with 'First Name' and 'URL')." % path)
    reader = csv.DictReader(io.StringIO("\n".join(lines[header_index:])))
    lookup = {}
    for field, aliases in COLUMN_ALIASES.items():
        for name in reader.fieldnames or []:
            if name and name.strip().lower() in aliases:
                lookup[field] = name
                break
    rows = []
    for raw in reader:
        row = {field: (raw.get(col) or "").strip() for field, col in lookup.items()}
        row["linkedin_url"] = normalize_linkedin_url(row.get("linkedin_url", ""))
        row["full_name"] = (row.get("first_name", "") + " " + row.get("last_name", "")).strip()
        if not row["full_name"] and not row["linkedin_url"]:
            continue  # connections who hide their data come through as empty rows
        rows.append(row)
    return rows


def main():
    paths = sys.argv[1:] or find_default_inputs()
    if not paths:
        sys.exit("No Connections.csv found. Put your LinkedIn export in data/private/ "
                 "or pass the path:\n  python3 scripts/network_import.py ~/Downloads/Connections.csv")
    merged, seen = [], set()
    for path in paths:
        path = os.path.expanduser(path)
        rows = read_export(path)
        added = 0
        for row in rows:
            key = row["linkedin_url"].lower() or row["full_name"].lower() + "|" + row.get("company", "").lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
            added += 1
        print("Read %d connections from %s (%d new)" % (len(rows), os.path.basename(path), added))

    write_csv(NETWORK_CSV, merged, NETWORK_FIELDS)

    with_company = [r for r in merged if r.get("company")]
    companies = Counter(r["company"] for r in with_company)
    print("\n%d connections saved to output/network.csv" % len(merged))
    print("  with a company: %d, with an email: %d" % (
        len(with_company), sum(1 for r in merged if r.get("email"))))
    print("\nCompanies you know the most people at:")
    for name, count in companies.most_common(12):
        print("  %3d  %s" % (count, name))
    print("\nNext: python3 scripts/network_filter.py   (needs output/icp.json, see prompts/network.md)")


if __name__ == "__main__":
    main()
