import http.server
import io
import os
import re


class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    # Regex to capture the full nav block and the footer block
    _nav_re = re.compile(r'<div class="navigation w-nav".*?(?=<main\b)', re.DOTALL)
    _footer_re = re.compile(r'<footer class="footer">.*?</footer>', re.DOTALL)
    # Strip Webflow's "hide until GSAP" inline style so text is always visible
    _vis_re = re.compile(
        r'<style>[^<]*html\.w-mod-js:not\(\.w-mod-ix3?\)[^{}]*\{[^{}]*visibility\s*:\s*hidden[^{}]*\}[^<]*</style>',
        re.DOTALL,
    )

    _shared_nav = None
    _shared_footer = None
    _index_mtime = 0

    # Small script injected after the shared nav to mark the active link
    _ACTIVE_SCRIPT = (
        '<script>(function(){'
        'var p=location.pathname.replace(/\\/$/, "");'
        'document.querySelectorAll(".navigation-link,.nav-logo-link").forEach(function(a){'
        'var h=a.getAttribute("href");'
        'if(h&&(h===p||(p===""&&h==="/"))){'
        'a.classList.add("w--current");a.setAttribute("aria-current","page");}});'
        '})();</script>'
    )
    _LOCAL_RUNTIME = '<script src="/assets/site-interactions.js"></script>'

    @classmethod
    def _reload_shared_if_changed(cls):
        try:
            mtime = os.path.getmtime('./index.html')
            if mtime == cls._index_mtime:
                return
            cls._index_mtime = mtime
            with open('./index.html', 'r', encoding='utf-8') as f:
                src = f.read()
            m = cls._nav_re.search(src)
            cls._shared_nav = m.group(0) if m else None
            m = cls._footer_re.search(src)
            cls._shared_footer = m.group(0) if m else None
        except Exception:
            pass

    def _rewrite_clean_url(self):
        original = self.path
        path = original.split('?')[0].split('#')[0]
        suffix = original[len(path):] if len(original) > len(path) else ''
        if not os.path.splitext(path)[1]:
            candidate = path.rstrip('/') + '.html'
            if os.path.exists('.' + candidate):
                self.path = candidate + suffix
                return
            index_candidate = path.rstrip('/') + '/index.html'
            if os.path.exists('.' + index_candidate):
                self.path = index_candidate + suffix

    def send_head(self):
        self._rewrite_clean_url()
        self._reload_shared_if_changed()

        path = self.translate_path(self.path)

        # Process every HTML file: strip visibility-hiding CSS + inject shared nav/footer
        if path.endswith('.html') and os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    html = f.read()

                # Always strip Webflow's "hide until GSAP" rule so text is visible
                html = self._vis_re.sub('', html)

                if self._LOCAL_RUNTIME not in html:
                    html = html.replace('</body>', self._LOCAL_RUNTIME + '</body>')

                data = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                return io.BytesIO(data)
            except Exception:
                pass

        return super().send_head()

    def log_message(self, format, *args):
        pass  # silence request logs


if __name__ == '__main__':
    port = 8000
    CleanURLHandler._reload_shared_if_changed()
    server = http.server.HTTPServer(('', port), CleanURLHandler)
    print(f'Server running at http://localhost:{port}')
    server.serve_forever()
