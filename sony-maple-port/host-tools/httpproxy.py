#!/usr/bin/env python3
"""Minimal forward proxy for plain-HTTP GET/HEAD (apk repositories) for the phone on the USB network."""
import http.server, socketserver, sys, urllib.request, shutil

class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    def _fwd(self, head=False):
        if not self.path.startswith("http://"):
            self.send_error(400); return
        req = urllib.request.Request(self.path, method="HEAD" if head else "GET",
                                     headers={"User-Agent": self.headers.get("User-Agent", "apk")})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                self.send_response(r.status)
                for k in ("Content-Type", "Content-Length", "Last-Modified", "ETag"):
                    if r.headers.get(k): self.send_header(k, r.headers[k])
                self.end_headers()
                if not head: shutil.copyfileobj(r, self.wfile, 256 * 1024)
        except urllib.error.HTTPError as e:
            self.send_error(e.code)
        except Exception:
            self.send_error(502)
    def do_GET(self): self._fwd()
    def do_HEAD(self): self._fwd(True)
    def log_message(self, *a): pass

class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

S((sys.argv[1], int(sys.argv[2])), H).serve_forever()
