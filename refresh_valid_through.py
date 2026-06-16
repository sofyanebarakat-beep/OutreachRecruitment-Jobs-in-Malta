#!/usr/bin/env python3
"""
Quarterly validThrough refresh.
Sets validThrough on all job pages to today + 180 days.
Run this every ~3 months to keep listings fresh in Google Jobs.

Usage: python3 refresh_valid_through.py
"""
import os, re
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS = os.path.join(BASE, "jobs")
NEW_DATE = (date.today() + timedelta(days=180)).isoformat()

updated = 0
for fname in os.listdir(JOBS):
    if fname.endswith(".html") and fname != "index.html":
        path = os.path.join(JOBS, fname)
        with open(path, encoding="utf-8") as f:
            c = f.read()
        new_c = re.sub(r'"validThrough":\s*"[^"]+"', f'"validThrough": "{NEW_DATE}"', c)
        if new_c != c:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_c)
            updated += 1

for d in os.scandir(JOBS):
    if d.is_dir():
        idx = os.path.join(d.path, "index.html")
        if os.path.exists(idx):
            with open(idx, encoding="utf-8") as f:
                c = f.read()
            new_c = re.sub(r'"validThrough":\s*"[^"]+"', f'"validThrough": "{NEW_DATE}"', c)
            if new_c != c:
                with open(idx, "w", encoding="utf-8") as f:
                    f.write(new_c)
                updated += 1

print(f"Updated {updated} files → validThrough: {NEW_DATE}")
