"""Add "Customer Service Jobs" to the sitewide Resources nav (header dropdown + footer),
right after "Hospitality Jobs". Idempotent: safe to re-run."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOSP = '<a class="nav-item" href="/hospitality-jobs-in-malta">Hospitality Jobs</a>'
CS = '<a class="nav-item" href="/customer-service-jobs-in-malta">Customer Service Jobs</a>'

changed = 0
for p in ROOT.rglob("*.html"):
    if {"node_modules", ".git"} & set(p.parts):
        continue
    s = p.read_text(encoding="utf-8", errors="surrogateescape")
    if HOSP not in s:
        continue
    new = s.replace(HOSP + CS, HOSP).replace(HOSP, HOSP + CS)
    if new != s:
        p.write_text(new, encoding="utf-8", errors="surrogateescape")
        changed += 1
print(f"Customer Service Jobs nav link present on all nav pages ({changed} file(s) updated)")
