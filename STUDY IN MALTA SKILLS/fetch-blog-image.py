#!/usr/bin/env python3
"""
fetch-blog-image.py — Outreach Recruitment Blog Image Fetcher
=============================================================
Automatically fetches a real photograph from Unsplash or Pexels,
resizes it to 1200×630 (feature image) and 800×450 (in-article),
converts to WebP, and saves to /images/{slug}.webp

Usage:
    python3 fetch-blog-image.py

You will be asked for:
  1. Search query   — e.g. "students studying Malta university"
  2. Article slug   — e.g. "study-in-malta-complete-guide"

Config:
    Set your API keys in SKILL-TEMPLATE-CONFIG.json (same folder as this script)
    or paste them directly into UNSPLASH_KEY and PEXELS_KEY below.
"""

import os, sys, json, requests, io
from PIL import Image
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────────────
# Option A: put keys directly here
UNSPLASH_KEY = ""   # get free key at unsplash.com/developers
PEXELS_KEY   = ""   # get free key at pexels.com/api

# Option B: keys are loaded from config file (takes priority if present)
SCRIPT_DIR   = Path(__file__).parent
CONFIG_FILE  = SCRIPT_DIR / "image-api-keys.json"
PROJECT_ROOT = SCRIPT_DIR.parent
IMAGES_DIR   = PROJECT_ROOT / "images"

# Output sizes
FEATURE_SIZE  = (1200, 630)   # OG / feature image
ARTICLE_SIZE  = (800,  450)   # in-article image
THUMBNAIL_SIZE= (400,  210)   # blog card thumbnail

# ── LOAD CONFIG ─────────────────────────────────────────────────────────────
def load_keys():
    global UNSPLASH_KEY, PEXELS_KEY
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        UNSPLASH_KEY = cfg.get("unsplash_key", UNSPLASH_KEY)
        PEXELS_KEY   = cfg.get("pexels_key",   PEXELS_KEY)

# ── UNSPLASH SEARCH ──────────────────────────────────────────────────────────
def search_unsplash(query: str, count: int = 10) -> list[dict]:
    """Search Unsplash and return list of photo dicts."""
    if not UNSPLASH_KEY:
        return []
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": count,
        "order_by": "relevant",
        "client_id": UNSPLASH_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = []
        for p in data.get("results", []):
            results.append({
                "source":      "Unsplash",
                "id":          p["id"],
                "thumb":       p["urls"]["small"],
                "download":    p["urls"]["full"],
                "description": p.get("alt_description") or p.get("description") or query,
                "photographer":p["user"]["name"],
                "profile_url": p["user"]["links"]["html"],
                "photo_url":   p["links"]["html"],
                "download_url":p["links"]["download_location"],  # must trigger for Unsplash guidelines
            })
        return results
    except Exception as e:
        print(f"  Unsplash error: {e}")
        return []

# ── PEXELS SEARCH ────────────────────────────────────────────────────────────
def search_pexels(query: str, count: int = 10) -> list[dict]:
    """Search Pexels and return list of photo dicts."""
    if not PEXELS_KEY:
        return []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_KEY}
    params  = {"query": query, "orientation": "landscape", "per_page": count}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        results = []
        for p in data.get("photos", []):
            results.append({
                "source":      "Pexels",
                "id":          str(p["id"]),
                "thumb":       p["src"]["medium"],
                "download":    p["src"]["original"],
                "description": p.get("alt") or query,
                "photographer":p["photographer"],
                "profile_url": p["photographer_url"],
                "photo_url":   p["url"],
                "download_url":p["src"]["original"],
            })
        return results
    except Exception as e:
        print(f"  Pexels error: {e}")
        return []

# ── TRIGGER UNSPLASH DOWNLOAD (required by API guidelines) ──────────────────
def trigger_unsplash_download(photo: dict):
    try:
        dl_url = photo.get("download_url", "")
        if dl_url and "unsplash" in dl_url:
            requests.get(dl_url + f"&client_id={UNSPLASH_KEY}", timeout=5)
    except Exception:
        pass

# ── DISPLAY RESULTS ──────────────────────────────────────────────────────────
def display_results(results: list[dict]):
    print()
    print("─" * 60)
    print(f"  Found {len(results)} photos:")
    print("─" * 60)
    for i, p in enumerate(results, 1):
        desc = p["description"][:55] if p["description"] else "no description"
        print(f"  [{i:2d}] {p['source']:8s} │ {p['photographer'][:20]:20s} │ {desc}")
    print("─" * 60)

# ── DOWNLOAD & PROCESS ───────────────────────────────────────────────────────
def download_and_process(photo: dict, slug: str) -> dict:
    """Download photo, crop/resize to all sizes, save WebP files."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n  Downloading from {photo['source']}...")
    r = requests.get(photo["download"], timeout=30, stream=True)
    r.raise_for_status()

    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    print(f"  Original size: {img.width}×{img.height}")

    # Trigger Unsplash download endpoint (API requirement)
    if photo["source"] == "Unsplash":
        trigger_unsplash_download(photo)

    outputs = {}
    sizes = {
        "feature":   (FEATURE_SIZE,   f"{slug}.webp"),
        "article":   (ARTICLE_SIZE,   f"{slug}-article.webp"),
        "thumbnail": (THUMBNAIL_SIZE, f"{slug}-thumb.webp"),
    }

    for name, (size, filename) in sizes.items():
        out_path = IMAGES_DIR / filename
        cropped  = smart_crop(img.copy(), size)
        cropped.save(str(out_path), "WEBP", quality=85, method=6)
        file_kb  = out_path.stat().st_size // 1024
        print(f"  Saved {name:10s}: images/{filename} ({size[0]}×{size[1]}, {file_kb} KB)")
        outputs[name] = f"/images/{filename}"

    return outputs

def smart_crop(img: Image.Image, target: tuple) -> Image.Image:
    """Resize then centre-crop to target (w, h)."""
    tw, th = target
    iw, ih = img.size

    # Scale so the shorter dimension matches target
    scale = max(tw / iw, th / ih)
    new_w = int(iw * scale)
    new_h = int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Centre crop
    left = (new_w - tw) // 2
    top  = (new_h - th) // 2
    return img.crop((left, top, left + tw, top + th))

# ── ATTRIBUTION HTML ─────────────────────────────────────────────────────────
def attribution_html(photo: dict) -> str:
    return (
        f'<!-- Photo by <a href="{photo["profile_url"]}?utm_source=outreach_recruitment&utm_medium=referral">'
        f'{photo["photographer"]}</a> on '
        f'<a href="{photo["photo_url"]}?utm_source=outreach_recruitment&utm_medium=referral">'
        f'{photo["source"]}</a> -->'
    )

def img_tag(outputs: dict, slug: str, alt_text: str, photo: dict) -> str:
    return f'''<!-- Feature image (1200×630) -->
{attribution_html(photo)}
<img src="{outputs["feature"]}"
     alt="{alt_text}"
     width="1200" height="630"
     loading="eager" fetchpriority="high" />

<!-- In-article image (800×450) -->
<img src="{outputs["article"]}"
     alt="{alt_text}"
     width="800" height="450"
     loading="lazy" />

<!-- Blog card thumbnail (400×210) -->
<img src="{outputs["thumbnail"]}"
     alt="{alt_text}"
     width="400" height="210"
     loading="lazy" />'''

# ── SAVE TO LOG ──────────────────────────────────────────────────────────────
def save_log(slug: str, query: str, photo: dict, outputs: dict):
    log_file = IMAGES_DIR / "image-log.json"
    log = []
    if log_file.exists():
        with open(log_file) as f:
            try: log = json.load(f)
            except: log = []
    log.append({
        "slug":         slug,
        "query":        query,
        "source":       photo["source"],
        "photographer": photo["photographer"],
        "photo_url":    photo["photo_url"],
        "description":  photo["description"],
        "files":        outputs,
    })
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print()
    print("━" * 60)
    print("  Outreach Recruitment — Blog Image Fetcher")
    print("━" * 60)

    load_keys()

    if not UNSPLASH_KEY and not PEXELS_KEY:
        print("""
  ⚠  No API keys configured.

  To set up your free keys:
  1. Unsplash (free):  unsplash.com/developers → New Application
  2. Pexels   (free):  pexels.com/api → Get Started

  Then save them in:
    STUDY IN MALTA SKILLS/image-api-keys.json

  File format:
  {
    "unsplash_key": "YOUR_UNSPLASH_ACCESS_KEY",
    "pexels_key":   "YOUR_PEXELS_API_KEY"
  }
""")
        sys.exit(1)

    # ── Input ──────────────────────────────────────────────────────────────
    print()
    query_input = input("  Search query (e.g. 'students studying Malta university'):\n  > ").strip()
    if not query_input:
        print("  No query entered. Exiting.")
        sys.exit(0)

    slug_input = input("\n  Article slug (e.g. 'study-in-malta-complete-guide'):\n  > ").strip()
    if not slug_input:
        slug_input = query_input.lower().replace(" ", "-")[:50]

    alt_input = input(f"\n  Alt text for img tag (press Enter to use query):\n  > ").strip()
    if not alt_input:
        alt_input = query_input

    # ── Search ────────────────────────────────────────────────────────────
    print(f"\n  Searching for: '{query_input}'...")

    results = []
    if UNSPLASH_KEY:
        print("  → Unsplash...")
        results += search_unsplash(query_input, 8)
    if PEXELS_KEY:
        print("  → Pexels...")
        results += search_pexels(query_input, 8)

    if not results:
        # Fallback: broaden the query
        broad = query_input.split()[0] + " Malta"
        print(f"  No results. Trying broader query: '{broad}'...")
        if UNSPLASH_KEY: results += search_unsplash(broad, 8)
        if PEXELS_KEY:   results += search_pexels(broad, 8)

    if not results:
        print("  No photos found. Try a different search query.")
        sys.exit(0)

    display_results(results)

    # ── Pick ──────────────────────────────────────────────────────────────
    while True:
        choice = input(f"\n  Pick a photo number [1–{len(results)}], or 0 to cancel:\n  > ").strip()
        if choice == "0":
            print("  Cancelled.")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(results):
            selected = results[int(choice) - 1]
            break
        print(f"  Please enter a number between 1 and {len(results)}.")

    # ── Download & process ────────────────────────────────────────────────
    outputs = download_and_process(selected, slug_input)

    # ── Output ────────────────────────────────────────────────────────────
    save_log(slug_input, query_input, selected, outputs)

    print()
    print("─" * 60)
    print("  IMG TAG (copy into article HTML):")
    print("─" * 60)
    print(img_tag(outputs, slug_input, alt_input, selected))
    print("─" * 60)
    print()
    print(f"  Attribution: Photo by {selected['photographer']} on {selected['source']}")
    print(f"  Photo page:  {selected['photo_url']}")
    print()
    print("  Done. Images saved to /images/")
    print()


if __name__ == "__main__":
    main()
