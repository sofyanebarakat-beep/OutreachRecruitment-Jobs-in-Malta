#!/usr/bin/env python3
"""
Comprehensive SEO fix script.
Fixes: duplicate canonicals, meta description length, meta title length,
JSON-LD schema fields, sitemap freshness, and hub page internal links.
"""

import glob, re, json, os
from datetime import date

BASE = '/Users/sof/Documents/Projects/OutreachRecruitmentwebsite/OutreachRecruitment-Jobs-in-Malta'
BASE_URL = 'https://outreachrecruitment.net'
TODAY = date.today().strftime('%Y-%m-%d')

# ── Category → hub page mapping ──────────────────────────────────────────────

HUB_CATEGORIES = {
    'hospitality-jobs-in-malta': [
        'Food Service Workers',
        'Hospitality and Facilities Management',
        'Arts, Design, Entertainment, Sports, and Media Occupations',
    ],
    'it-jobs-in-malta': [
        'Computer and Mathematical Occupations',
    ],
    'finance-jobs-in-malta': [
        'Business and Financial Operations Occupations',
        'Administrative Services Managers',
        'Management',
    ],
    'construction-jobs-in-malta': [
        'Installation, Maintenance, and Repair Workers',
        'Heavy and Tractor-Trailer Truck Drivers / Construction Equipment Operators',
        'Transportation and Material Moving Occupations',
    ],
    'marine-jobs-in-malta': [
        'Maritime & Shipping',
        '13-2011.00',
    ],
    'sales-jobs-in-malta': [
        'Sales and Related Occupations',
        'Retail Sales Workers',
    ],
    'engineering-jobs-in-malta': [
        'Healthcare Support Occupations',
        'HR & Recruitment',
        'Office and Administrative Support Occupations',
    ],
}


# ── Fix 1: Duplicate canonical tags ─────────────────────────────────────────

def fix_canonical(content, abs_url):
    """Remove duplicate canonicals; keep only the absolute one."""
    all_canonicals = re.findall(r'<link[^>]*canonical[^>]*/?>', content)
    if len(all_canonicals) <= 1:
        return content
    # Strip all canonical links
    content = re.sub(r'\s*<link[^>]*canonical[^>]*/?>',  '', content)
    # Re-insert single absolute canonical right after charset meta
    tag = f'<link href="{abs_url}" rel="canonical"/>'
    content = re.sub(r'(<meta charset=[^/]*/?>)', r'\1' + tag, content, count=1)
    return content


# ── Fix 2: Meta description length ──────────────────────────────────────────

def fix_description(content):
    """Trim meta description to 120–155 characters."""
    def _fix(m):
        prefix = m.group(1)
        desc = m.group(2)
        suffix = m.group(3)
        if len(desc) <= 155:
            return m.group(0)
        # Try sentence boundary
        truncated = desc[:152]
        for sep in ['. ', '! ', '? ']:
            pos = truncated.rfind(sep)
            if pos >= 110:
                desc = truncated[:pos + 1]
                break
        else:
            # word boundary
            word_cut = desc[:149].rsplit(' ', 1)[0]
            desc = word_cut + '...' if len(word_cut) >= 110 else desc[:152] + '...'
        # Ensure CTA present
        if not any(cta in desc.lower() for cta in ['apply now', 'apply today', 'apply directly']):
            # Replace trailing period if space permits
            if len(desc) + len(' Apply now.') <= 160:
                desc = desc.rstrip('.') + '. Apply now.'
        return prefix + desc + suffix

    # Handle content="..." name="description"
    content = re.sub(
        r'(<meta[^>]*content=")([^"]{156,})("[^>]*name="description"[^>]*/>)',
        _fix, content)
    # Handle name="description" content="..."
    content = re.sub(
        r'(<meta[^>]*name="description"[^>]*content=")([^"]{156,})("[^>]*/>)',
        _fix, content)
    return content


# ── Fix 3: Meta title length ─────────────────────────────────────────────────

SUFFIX = ' | Outreach Recruitment'

def _shorten_title(title):
    if len(title) <= 60:
        return title

    # 1. Remove redundant "Job" before "in"
    t = re.sub(r'\s+Job\s+in\s+', ' in ', title)

    # 2. Try with full "City, Malta"
    if len(t) <= 60:
        return t

    # 3. Replace "City, Malta" or "Malta, Malta" with just "Malta"
    t = re.sub(r'\s+in\s+[A-Za-z\s\.]+,\s*Malta\b', ' in Malta', t)
    t = re.sub(r'\s+in\s+Malta,\s*Malta\b', ' in Malta', t)
    if len(t) <= 60:
        return t

    # 4. Truncate the job title to fit "...TITLE in Malta | Outreach Recruitment"
    max_job = 60 - len(' in Malta') - len(SUFFIX)  # 60 - 9 - 22 = 29
    job_part = re.split(r'\s+in\s+|\s+\|', t)[0].strip()
    if len(job_part) > max_job:
        job_part = job_part[:max_job - 3].rsplit(' ', 1)[0] + '...'
    return job_part + ' in Malta' + SUFFIX

def fix_title(content):
    def _fix(m):
        title = m.group(1)
        fixed = _shorten_title(title)
        return f'<title>{fixed}</title>'
    return re.sub(r'<title>(.{61,}?)</title>', _fix, content)


# ── Fix 4: JSON-LD schema completeness ───────────────────────────────────────

def fix_jsonld(content):
    def _fix_schema(m):
        try:
            obj = json.loads(m.group(1).strip())
        except Exception:
            return m.group(0)
        # Handle array of schemas
        if isinstance(obj, list):
            return m.group(0)
        if obj.get('@type') != 'JobPosting':
            return m.group(0)
        changed = False
        if not obj.get('validThrough'):
            obj['validThrough'] = '2026-12-31'
            changed = True
        if not obj.get('employmentType'):
            obj['employmentType'] = 'FULL_TIME'
            changed = True
        if not obj.get('identifier'):
            slug = re.sub(r'[^a-z0-9]+', '-', obj.get('title', 'job').lower()).strip('-')
            obj['identifier'] = {
                '@type': 'PropertyValue',
                'name': 'Outreach Recruitment Ltd',
                'value': slug,
            }
            changed = True
        if not changed:
            return m.group(0)
        return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'

    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        _fix_schema, content, flags=re.DOTALL)


# ── Fix 5: Sitemap freshness ─────────────────────────────────────────────────

def fix_sitemap():
    sitemap_path = os.path.join(BASE, 'sitemaps/sitemap-jobs.xml')
    sitemap = open(sitemap_path).read()

    in_sitemap = set(re.findall(r'https://outreachrecruitment\.net/jobs/([a-z0-9-]+)', sitemap))
    job_files = glob.glob(os.path.join(BASE, 'jobs/*.html'))
    file_slugs = {f.split('/')[-1].replace('.html', '') for f in job_files} - {'index'}

    missing = file_slugs - in_sitemap
    if not missing:
        print('  Sitemap: already up to date.')
        return

    new_entries = ''
    for slug in sorted(missing):
        new_entries += f'''
  <url>
    <loc>{BASE_URL}/jobs/{slug}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>'''

    # Insert before closing tag
    sitemap = sitemap.replace('</urlset>', new_entries + '\n</urlset>')
    open(sitemap_path, 'w').write(sitemap)
    print(f'  Sitemap: added {len(missing)} missing URLs → {", ".join(sorted(missing))}')


# ── Fix 6: Internal linking from hub pages ───────────────────────────────────

def build_hub_links():
    """Map each hub to the list of job slugs + titles in its categories."""
    cat_to_hub = {}
    for hub, cats in HUB_CATEGORIES.items():
        for cat in cats:
            cat_to_hub[cat] = hub

    hub_jobs = {hub: [] for hub in HUB_CATEGORIES}

    for f in sorted(glob.glob(os.path.join(BASE, 'jobs/*.html'))):
        slug = f.split('/')[-1].replace('.html', '')
        if slug == 'index':
            continue
        content = open(f, errors='ignore').read()
        schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        for s in schemas:
            try:
                obj = json.loads(s.strip())
                if obj.get('@type') == 'JobPosting':
                    cat = obj.get('occupationalCategory', '')
                    hub = cat_to_hub.get(cat)
                    if hub:
                        title = obj.get('title', slug.replace('-', ' ').title())
                        hub_jobs[hub].append((slug, title))
            except:
                pass

    return hub_jobs


LINK_SECTION_MARKER = '<!-- seo-internal-links -->'

def fix_hub_internal_links(hub_jobs):
    for hub_slug, jobs in hub_jobs.items():
        if not jobs:
            continue

        hub_path = os.path.join(BASE, f'{hub_slug}.html')
        if not os.path.exists(hub_path):
            continue

        content = open(hub_path, errors='ignore').read()

        # Build the links HTML
        links_html = '\n'.join(
            f'<a href="{BASE_URL}/jobs/{slug}" style="display:inline-block;margin:4px 8px;font-size:14px;">{title}</a>'
            for slug, title in sorted(jobs, key=lambda x: x[1])
        )
        section = (
            f'\n{LINK_SECTION_MARKER}\n'
            f'<section aria-label="All {hub_slug.replace("-jobs-in-malta","").replace("-"," ").title()} roles" '
            f'style="padding:24px 0;display:none;">\n'
            f'{links_html}\n'
            f'</section>\n'
        )

        if LINK_SECTION_MARKER in content:
            # Replace existing section
            content = re.sub(
                rf'{re.escape(LINK_SECTION_MARKER)}.*?</section>',
                section.strip(), content, flags=re.DOTALL)
        else:
            # Append before </main>
            if '</main>' in content:
                content = content.replace('</main>', section + '</main>', 1)
            else:
                content = content.replace('</body>', section + '</body>', 1)

        open(hub_path, 'w', encoding='utf-8').write(content)
        print(f'  Hub links: {hub_slug}.html → {len(jobs)} links added/updated')


# ── Main ─────────────────────────────────────────────────────────────────────

def process_job_pages():
    all_html = (
        glob.glob(os.path.join(BASE, 'jobs/*.html')) +
        glob.glob(os.path.join(BASE, 'jobs/*/index.html'))
    )

    canonical_fixed = desc_fixed = title_fixed = schema_fixed = 0

    for path in all_html:
        # Derive absolute canonical URL from path
        rel = path.replace(BASE, '').replace('/index.html', '').replace('.html', '')
        abs_url = BASE_URL + rel

        content = open(path, errors='ignore').read()
        orig = content

        content = fix_canonical(content, abs_url)
        if content != orig:
            canonical_fixed += 1

        prev = content
        content = fix_description(content)
        if content != prev:
            desc_fixed += 1

        prev = content
        content = fix_title(content)
        if content != prev:
            title_fixed += 1

        prev = content
        content = fix_jsonld(content)
        if content != prev:
            schema_fixed += 1

        if content != orig:
            open(path, 'w', encoding='utf-8').write(content)

    print(f'  Canonicals fixed:       {canonical_fixed}')
    print(f'  Meta descriptions fixed:{desc_fixed}')
    print(f'  Meta titles fixed:      {title_fixed}')
    print(f'  JSON-LD schemas fixed:  {schema_fixed}')


if __name__ == '__main__':
    print('=== SEO Fix: Job pages ===')
    process_job_pages()

    print('\n=== SEO Fix: Sitemap ===')
    fix_sitemap()

    print('\n=== SEO Fix: Hub page internal links ===')
    hub_jobs = build_hub_links()
    fix_hub_internal_links(hub_jobs)

    print('\nDone.')
