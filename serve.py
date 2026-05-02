#!/usr/bin/env python3
"""Tiny static server for the timegate WebGL harness.

Usage: python3 serve.py [port]   (default port 8000)
Then open http://localhost:8000 in a browser.
"""
import http.server
import socketserver
import sys


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".glsl": "text/plain; charset=utf-8",
    }

    def end_headers(self):
        # Disable caching so edits to timegate.glsl appear on refresh.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write(f"{self.address_string()} {fmt % args}\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Serving cttimegate at http://localhost:{port}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
