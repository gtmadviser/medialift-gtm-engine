"""Shared helpers for the network scripts. Standard library only."""

import csv
import json
import os
import re
import sys

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(REPO_ROOT, "output")
NETWORK_CSV = os.path.join(OUTPUT_DIR, "network.csv")
SHORTLIST_CSV = os.path.join(OUTPUT_DIR, "network_shortlist.csv")
ENRICH_CACHE = os.path.join(OUTPUT_DIR, "network_enrichment.json")
ICP_JSON = os.path.join(OUTPUT_DIR, "icp.json")

NETWORK_FIELDS = ["full_name", "first_name", "last_name", "position", "company",
                  "linkedin_url", "email", "connected_on"]


def load_env_key(name, hint):
    """Read one key from the environment or from .env in the repo root."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    env_path = os.path.join(REPO_ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(name + "="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        return value
    sys.exit("ERROR: %s is not set. Copy .env.example to .env and paste your key. %s"
             % (name, hint))


def normalize_linkedin_url(url):
    """Return https://www.linkedin.com/in/<slug> or '' if it is not a profile URL."""
    url = (url or "").strip()
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", url, re.I)
    if not m:
        return ""
    return "https://www.linkedin.com/in/" + m.group(1).strip("/")


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
