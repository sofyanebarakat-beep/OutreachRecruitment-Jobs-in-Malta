#!/usr/bin/env python3
"""
generate-article-images.py — Outreach Recruitment Auto Image System
=====================================================================
Fetches 7 real photographs from Unsplash / Pexels, resizes + converts
to WebP, and outputs production-ready HTML for every image in the article.

Images generated per article:
  0  Hero         1200 x 630  (OG + page header)          fetchpriority="high"
  1  Section 1    1200 x 628  (first H2 body section)     loading="lazy"
  2  Section 2    800  x 500  (visa / requirements)       loading="lazy"
  3  Section 3    800  x 500  (cost / fees)               loading="lazy"
  4  Section 4    800  x 500  (accommodation / housing)   loading="lazy"
  5  Section 5    800  x 500  (work / career)             loading="lazy"
  6  Section 6    800  x 500  (student life / location)   loading="lazy"

Usage:
  python3 generate-article-images.py              (interactive)
  python3 generate-article-images.py --auto       (auto-pick best results, no prompts)

  or import and call fetch_images_for_article() from your article build script.
"""

import os, sys, json, time, re, io, textwrap, argparse
import requests
from PIL import Image
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
CONFIG_FILE  = SCRIPT_DIR / "image-api-keys.json"
PROJECT_ROOT = SCRIPT_DIR.parent
IMAGES_ROOT  = PROJECT_ROOT / "images"

# ── API keys ───────────────────────────────────────────────────────────────
UNSPLASH_KEY = ""
PEXELS_KEY   = ""

# ── Image slot definitions ─────────────────────────────────────────────────
# Each slot: (name, size_wh, position_label, loading)
SLOTS = [
    ("hero",      (1200, 630),  "Page hero / OG image",         "eager"),
    ("section-1", (1200, 628),  "Section 1 — overview",         "lazy"),
    ("section-2", (800,  500),  "Section 2 — visa/requirements","lazy"),
    ("section-3", (800,  500),  "Section 3 — costs/fees",       "lazy"),
    ("section-4", (800,  500),  "Section 4 — accommodation",    "lazy"),
    ("section-5", (800,  500),  "Section 5 — work/career",      "lazy"),
    ("section-6", (800,  500),  "Section 6 — student life",     "lazy"),
]

# ── Per-article query templates ────────────────────────────────────────────
# Keys are generic topic categories. Map your article topic to one below.
# You can override individual slot queries when calling fetch_images_for_article().
QUERY_SETS = {
    "study-in-malta": [
        "international students studying Malta university campus",
        "diverse students university lecture hall",
        "passport visa documents application desk",
        "students budget planning laptop coffee",
        "modern student apartment bedroom Mediterranean",
        "young professional working part time cafe",
        "Valletta Malta aerial view sea",
    ],
    "student-visa": [
        "passport visa documents application desk",
        "student university campus",
        "visa application form documents",
        "immigration office documents",
        "student planning abroad",
        "travel documents stamps",
        "Malta Valletta Government buildings",
    ],
    "cost-of-living": [
        "student budget planning expenses Malta",
        "students grocery shopping supermarket",
        "student apartment kitchen affordable",
        "public transport bus students",
        "student cooking home budget",
        "part time work student cafe",
        "Mediterranean city street market",
    ],
    "accommodation": [
        "student accommodation apartment bedroom Malta",
        "students moving into apartment",
        "cozy student room desk laptop",
        "apartment building Mediterranean city",
        "students housemates living room",
        "modern student residence hall",
        "Malta harbour apartment buildings",
    ],
    "english-courses": [
        "English language school students classroom Malta",
        "students English conversation class",
        "language school teacher students",
        "IELTS exam preparation study",
        "international students library studying",
        "English learning books laptop desk",
        "sunny Malta street outdoor study",
    ],
    "working-while-studying": [
        "student working part time job Malta",
        "young professional office laptop",
        "student barista cafe part time",
        "work life balance student professional",
        "students networking event",
        "modern office Malta business",
        "Mediterranean city career opportunities",
    ],
    "scholarships": [
        "students scholarship award ceremony",
        "student application scholarship letter",
        "diverse students university success",
        "graduate student diploma ceremony",
        "student research library books",
        "international student smiling campus",
        "Malta university campus sunny",
    ],
    "default": [
        "international students Malta Mediterranean",
        "diverse university students campus",
        "student studying laptop library",
        "Malta Valletta scenic view",
        "student apartment accommodation",
        "young professionals working together",
        "Europe education career opportunities",
    ],
}


# ── Key loading ────────────────────────────────────────────────────────────
def load_keys():
    global UNSPLASH_KEY, PEXELS_KEY
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        UNSPLASH_KEY = cfg.get("unsplash_key", "")
        PEXELS_KEY   = cfg.get("pexels_key", "")


# ── Unsplash search ────────────────────────────────────────────────────────
def search_unsplash(query: str, count: int = 5) -> list:
    if not UNSPLASH_KEY:
        return []
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "orientation": "landscape",
                    "per_page": count, "order_by": "relevant",
                    "client_id": UNSPLASH_KEY},
            timeout=10,
        )
        r.raise_for_status()
        results = []
        for p in r.json().get("results", []):
            results.append({
                "source":       "Unsplash",
                "id":           p["id"],
                "thumb":        p["urls"]["small"],
                "download":     p["urls"]["full"],
                "description":  (p.get("alt_description") or p.get("description") or query).strip(),
                "photographer": p["user"]["name"],
                "profile_url":  p["user"]["links"]["html"],
                "photo_url":    p["links"]["html"],
                "dl_trigger":   p["links"]["download_location"],
            })
        return results
    except Exception as e:
        print(f"    Unsplash error: {e}")
        return []


# ── Pexels search ──────────────────────────────────────────────────────────
def search_pexels(query: str, count: int = 5) -> list:
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "orientation": "landscape", "per_page": count},
            timeout=10,
        )
        r.raise_for_status()
        results = []
        for p in r.json().get("photos", []):
            results.append({
                "source":       "Pexels",
                "id":           str(p["id"]),
                "thumb":        p["src"]["medium"],
                "download":     p["src"]["original"],
                "description":  (p.get("alt") or query).strip(),
                "photographer": p["photographer"],
                "profile_url":  p["photographer_url"],
                "photo_url":    p["url"],
                "dl_trigger":   None,
            })
        return results
    except Exception as e:
        print(f"    Pexels error: {e}")
        return []


def search(query: str, count: int = 5) -> list:
    results = search_unsplash(query, count)
    if not results:
        results = search_pexels(query, count)
    if not results and " " in query:
        # Try shorter fallback query
        short = " ".join(query.split()[:3])
        results = search_unsplash(short, count) or search_pexels(short, count)
    return results


def trigger_unsplash_dl(photo: dict):
    if photo.get("dl_trigger") and UNSPLASH_KEY:
        try:
            requests.get(photo["dl_trigger"] + f"&client_id={UNSPLASH_KEY}", timeout=5)
        except Exception:
            pass


# ── Smart crop + resize ────────────────────────────────────────────────────
def smart_crop(img: Image.Image, target: tuple) -> Image.Image:
    tw, th = target
    iw, ih = img.size
    scale  = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img    = img.resize((nw, nh), Image.LANCZOS)
    left   = (nw - tw) // 2
    top    = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


# ── Download + process ─────────────────────────────────────────────────────
def download_photo(photo: dict, out_path: Path, size: tuple) -> bool:
    try:
        r = requests.get(photo["download"], timeout=30, stream=True)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        cropped = smart_crop(img, size)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(str(out_path), "WEBP", quality=85, method=6)
        if photo["source"] == "Unsplash":
            trigger_unsplash_dl(photo)
        kb = out_path.stat().st_size // 1024
        print(f"    Saved {out_path.name} ({size[0]}×{size[1]}, {kb} KB)")
        return True
    except Exception as e:
        print(f"    Download failed: {e}")
        return False


# ── SEO alt-text builder ───────────────────────────────────────────────────
def build_alt(description: str, topic: str, slot_label: str) -> str:
    """Create a clean, descriptive alt text (max 120 chars)."""
    base = description.strip().rstrip(".")
    # Avoid pure keyword stuffing — use the photo description if it's meaningful
    if len(base) > 15 and base.lower() != topic.lower():
        alt = base[:115].rsplit(" ", 1)[0] + " — Outreach Recruitment"
    else:
        alt = f"{slot_label} — {topic} | Outreach Recruitment"
    return alt[:120]


def build_caption(description: str, photographer: str, source: str) -> str:
    desc = description.strip().rstrip(".").capitalize()
    return f"{desc}. Photo: {photographer} / {source}."


def attribution_comment(photo: dict) -> str:
    return (
        f'<!-- Photo: {photo["photographer"]} on {photo["source"]} '
        f'— {photo["photo_url"]} -->'
    )


# ── HTML image tag builder ─────────────────────────────────────────────────
def build_img_html(
    web_path: str,
    alt: str,
    width: int,
    height: int,
    loading: str,
    caption: str,
    photo: dict,
    slot_name: str,
) -> str:
    fetch_attr = ' fetchpriority="high"' if loading == "eager" else ""
    load_attr  = '' if loading == "eager" else ' loading="lazy"'
    srcset = (
        f'{web_path.replace(".webp", "-800w.webp")} 800w, {web_path} {width}w'
        if width > 800 else ""
    )
    srcset_attr = f'\n     srcset="{srcset}"' if srcset else ""
    return (
        f"{attribution_comment(photo)}\n"
        f"<figure>\n"
        f'  <img src="{web_path}"\n'
        f'       alt="{alt}"\n'
        f'       width="{width}" height="{height}"{load_attr}{fetch_attr}{srcset_attr} />\n'
        f"  <figcaption>{caption}</figcaption>\n"
        f"</figure>"
    )


# ── Log ───────────────────────────────────────────────────────────────────
def save_log(slug: str, manifest: list):
    log_path = IMAGES_ROOT / slug / "image-manifest.json"
    with open(log_path, "w") as f:
        json.dump(manifest, f, indent=2)


# ── Main fetch function (importable) ──────────────────────────────────────
def fetch_images_for_article(
    slug: str,
    topic: str,
    queries: list = None,
    auto: bool = False,
) -> dict:
    """
    Fetch 7 images for an article.

    Args:
        slug:    article slug, e.g. "study-in-malta-complete-guide"
        topic:   human-readable topic, e.g. "Study in Malta 2026"
        queries: list of 7 search query strings (overrides defaults)
        auto:    if True, auto-pick first result without prompting

    Returns:
        dict keyed by slot name: {"hero": {"web_path": ..., "html": ..., ...}, ...}
    """
    load_keys()

    if not UNSPLASH_KEY and not PEXELS_KEY:
        print("  ERROR: No API keys. Set up image-api-keys.json first.")
        return {}

    # Resolve query set
    query_key = "default"
    for k in QUERY_SETS:
        if k in slug:
            query_key = k
            break
    default_queries = QUERY_SETS[query_key]

    if queries is None:
        queries = default_queries
    # Pad or trim to exactly 7
    while len(queries) < 7:
        queries.append(default_queries[len(queries) % len(default_queries)])
    queries = queries[:7]

    out_dir  = IMAGES_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    results  = {}

    print(f"\n  Fetching 7 images for: {slug}")
    print(f"  Saving to: images/{slug}/\n")

    for i, (slot_name, size, label, loading) in enumerate(SLOTS):
        query   = queries[i]
        w, h    = size
        file    = f"{slug}-{slot_name}.webp"
        out_path = out_dir / file
        web_path = f"/images/{slug}/{file}"

        print(f"  [{i+1}/7] {slot_name:10s} — searching: \"{query}\"")

        photos = search(query, count=5)
        if not photos:
            print(f"    No results — skipping {slot_name}")
            continue

        if auto:
            chosen = photos[0]
        else:
            print()
            for j, p in enumerate(photos, 1):
                desc = p["description"][:55] if p["description"] else "no description"
                print(f"    [{j}] {p['source']:8s} | {p['photographer'][:18]:18s} | {desc}")
            while True:
                choice = input(f"\n    Pick 1–{len(photos)} (Enter = auto-pick 1): ").strip()
                if choice == "":
                    chosen = photos[0]; break
                if choice.isdigit() and 1 <= int(choice) <= len(photos):
                    chosen = photos[int(choice)-1]; break
            print()

        if not download_photo(chosen, out_path, size):
            continue

        alt     = build_alt(chosen["description"], topic, label)
        caption = build_caption(chosen["description"], chosen["photographer"], chosen["source"])
        html    = build_img_html(web_path, alt, w, h, loading, caption, chosen, slot_name)

        # Also generate 800w srcset variant for hero
        if slot_name == "hero" and w > 800:
            small_path = out_dir / file.replace(".webp", "-800w.webp")
            try:
                img800 = Image.open(str(out_path)).convert("RGB")
                img800 = smart_crop(img800, (800, 420))
                img800.save(str(small_path), "WEBP", quality=80, method=6)
                print(f"    Saved srcset 800w variant")
            except Exception:
                pass

        entry = {
            "slot":         slot_name,
            "file":         file,
            "web_path":     web_path,
            "size":         f"{w}x{h}",
            "alt":          alt,
            "caption":      caption,
            "source":       chosen["source"],
            "photographer": chosen["photographer"],
            "photo_url":    chosen["photo_url"],
            "loading":      loading,
            "html":         html,
        }
        manifest.append(entry)
        results[slot_name] = entry

        time.sleep(0.3)   # be polite to APIs

    save_log(slug, manifest)
    _write_html_output(slug, results, topic)
    return results


def _write_html_output(slug: str, results: dict, topic: str):
    """Write a standalone HTML preview file with all images."""
    lines = [
        f"<!-- AUTO-GENERATED IMAGE TAGS for: {slug} -->",
        f"<!-- Topic: {topic} -->",
        f"<!-- Generated: {__import__('datetime').date.today()} -->",
        "",
    ]
    for slot_name, data in results.items():
        lines.append(f"<!-- ── {slot_name.upper()} ({data['size']}) ── -->")
        lines.append(data["html"])
        lines.append("")

    out_path = IMAGES_ROOT / slug / "image-tags.html"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Image HTML written to: images/{slug}/image-tags.html")


# ── OG meta tag ───────────────────────────────────────────────────────────
def og_image_tag(slug: str) -> str:
    return (
        f'<meta property="og:image" '
        f'content="https://outreachrecruitment.net/images/{slug}/{slug}-hero.webp" />\n'
        f'<meta property="og:image:width" content="1200" />\n'
        f'<meta property="og:image:height" content="630" />\n'
        f'<meta name="twitter:image" '
        f'content="https://outreachrecruitment.net/images/{slug}/{slug}-hero.webp" />'
    )


# ── CLI entry point ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Fetch 7 real images for a blog article.")
    parser.add_argument("--auto", action="store_true", help="Auto-pick top result for every slot")
    parser.add_argument("--slug", type=str, default="", help="Article slug")
    parser.add_argument("--topic", type=str, default="", help="Article topic")
    args = parser.parse_args()

    print()
    print("━" * 62)
    print("  Outreach Recruitment — Article Image Fetcher (7 images)")
    print("━" * 62)

    load_keys()
    if not UNSPLASH_KEY and not PEXELS_KEY:
        print("\n  ERROR: No API keys found in image-api-keys.json\n")
        sys.exit(1)

    slug  = args.slug  or input("\n  Article slug (e.g. study-in-malta-complete-guide):\n  > ").strip()
    topic = args.topic or input("\n  Article topic (e.g. Study in Malta 2026):\n  > ").strip()

    if not slug:
        print("  No slug entered. Exiting.")
        sys.exit(0)

    results = fetch_images_for_article(slug, topic, auto=args.auto)

    print("\n" + "━" * 62)
    print(f"  Done. {len(results)} images saved to images/{slug}/")
    print()
    print("  OG / Twitter image meta tags:")
    print("  " + og_image_tag(slug).replace("\n", "\n  "))
    print()
    print("  All image HTML tags in:")
    print(f"  images/{slug}/image-tags.html")
    print("━" * 62)


if __name__ == "__main__":
    main()
