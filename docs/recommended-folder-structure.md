# Recommended Folder Structure

Use the home page header and footer as the single source of truth for the whole static site.

```text
/
├── index.html
├── components/
│   ├── header.html
│   └── footer.html
├── assets/
├── jobs/
├── blog/
├── clients/
├── tools/
│   └── apply_home_header_footer.py
├── sitemap.xml
├── robots.txt
└── server.py
```

## Shared Header And Footer

- `components/header.html` contains the header from `http://localhost:8000/`.
- `components/footer.html` contains the footer from `http://localhost:8000/`.
- All pages should use these same two components.

After editing the home header/footer, run:

```bash
python3 tools/apply_home_header_footer.py --extract
```

After editing only `components/header.html` or `components/footer.html`, run:

```bash
python3 tools/apply_home_header_footer.py
```
