#!/usr/bin/env python3
"""
Turn any list in output/ into a Google Sheets ready tracker.

Adds the columns a founder needs to actually work the list (status, owner,
next step, last contact, notes) and writes a CSV that Google Sheets imports
cleanly, umlauts included.

Usage:
    python3 scripts/sheet_export.py                              # output/network_shortlist.csv
    python3 scripts/sheet_export.py output/leads.csv
    python3 scripts/sheet_export.py output/accounts.csv --owner Anna

Writes output/sheets/<name>_tracker.csv. Then, in the browser:
    1. open https://sheets.new
    2. File -> Import -> Upload -> pick the file
    3. "Replace spreadsheet", separator "Detect automatically"

If your agent has a Google Drive or Google Sheets connector, ask it to create
the sheet directly instead (see prompts/gsheet.md). Standard library only.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from netlib import OUTPUT_DIR, SHORTLIST_CSV, read_csv  # noqa: E402

TRACKER_FIELDS = ["status", "owner", "next_step", "last_contact", "notes"]
STATUS_HINT = "to contact"   # then: contacted / replied / meeting / pilot / won / not now


def main():
    ap = argparse.ArgumentParser(description="Export a list as a Google Sheets ready tracker.")
    ap.add_argument("input", nargs="?", default=SHORTLIST_CSV, help="CSV in output/ to export")
    ap.add_argument("--owner", default="", help="name to pre-fill in the owner column")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.exit("ERROR: %s not found." % args.input)
    rows = read_csv(args.input)
    if not rows:
        sys.exit("ERROR: %s is empty." % args.input)

    source_fields = [f for f in rows[0].keys() if f and f not in TRACKER_FIELDS]
    fields = ["status", "owner"] + source_fields + ["next_step", "last_contact", "notes"]
    for row in rows:
        row.setdefault("status", STATUS_HINT)
        row["status"] = row["status"] or STATUS_HINT
        row["owner"] = row.get("owner") or args.owner

    out_dir = os.path.join(OUTPUT_DIR, "sheets")
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(args.input))[0] + "_tracker.csv"
    out_path = os.path.join(out_dir, name)
    import csv
    # utf-8-sig: Google Sheets and Excel then read umlauts correctly.
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print("%d rows -> %s" % (len(rows), os.path.relpath(out_path)))
    print("Import it: open https://sheets.new, then File -> Import -> Upload -> this file.")
    print("Status values to use: to contact, contacted, replied, meeting, pilot, won, not now.")


if __name__ == "__main__":
    main()
