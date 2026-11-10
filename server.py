#!/usr/bin/env python3
"""
Local dev server that resolves extensionless URLs to .html files.
Usage: python3 server.py
"""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Always serve from the directory containing this script
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

class HTMLFallbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0].split('#')[0]
        base = path.lstrip('/')

        # Resolve clean article URLs before falling back to ordinary root pages.
        if '.' not in os.path.basename(path):
            article_slug = base.strip('/')
            candidates = []
            is_directory_index = path.endswith('/') and os.path.isfile(
                os.path.join(ROOT, base, 'index.html')
            )
            if article_slug and '/' not in article_slug and not is_directory_index:
                candidates.extend([
                    article_slug + '.html',
                    os.path.join('blog', article_slug + '.html'),
                ])
            if not path.endswith('/'):
                candidates.extend([
                    base + '.html',
                    os.path.join(base, 'index.html'),
                ])
            for candidate in candidates:
                if os.path.isfile(os.path.join(ROOT, candidate)):
                    self.path = '/' + candidate
                    break

        super().do_GET()

    def log_message(self, format, *args):
        print(f"  {self.address_string()} — {format % args}")

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('', port), HTMLFallbackHandler)
    print(f"Serving at http://localhost:{port}  (Ctrl+C to stop)")
    print(f"Root: {ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
