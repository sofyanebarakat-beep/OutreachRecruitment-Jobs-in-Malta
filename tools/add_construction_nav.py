"""Add "Construction Jobs" to the sitewide Resources nav (header dropdown + footer),
right after "Manufacturing Jobs". Idempotent: safe to re-run."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MFG = '<a class="nav-item" href="https://outreachrecruitment.net/manufacturing-jobs-in-malta">Manufacturing Jobs</a>'
CON = '<a class="nav-item" href="https://outreachrecruitment.net/construction-jobs-in-malta">Construction Jobs</a>'

changed = 0
for p in ROOT.rglob("*.html"):
    if {"node_modules", ".git"} & set(p.parts):
        continue
    s = p.read_text(encoding="utf-8", errors="surrogateescape")
    if MFG not in s:
        continue
    new = s.replace(MFG + CON, MFG).replace(MFG, MFG + CON)
    if new != s:
        p.write_text(new, encoding="utf-8", errors="surrogateescape")
        changed += 1
print(f"Construction Jobs nav link present on all nav pages ({changed} file(s) updated)")
