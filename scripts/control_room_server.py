#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse, json, urllib.parse

class ReadOnlyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
    def do_POST(self): self.send_error(405,'read-only Control Room')
    def do_PUT(self): self.send_error(405,'read-only Control Room')
    def do_PATCH(self): self.send_error(405,'read-only Control Room')
    def do_DELETE(self): self.send_error(405,'read-only Control Room')
    def log_message(self, fmt, *args):
        print('%s - %s' % (self.address_string(), fmt % args), flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bind',default='127.0.0.1')
    ap.add_argument('--port',type=int,default=8777)
    ap.add_argument('--directory',default='dashboard')
    a=ap.parse_args()
    root=Path(a.directory).resolve()
    if not (root/'index.html').exists(): raise SystemExit('dashboard/index.html missing')
    handler=partial(ReadOnlyHandler,directory=str(root))
    httpd=ThreadingHTTPServer((a.bind,a.port),handler)
    print(f'ENGINEERINGOS_CONTROL_ROOM_READY http://{a.bind}:{a.port}/ root={root}',flush=True)
    httpd.serve_forever()
if __name__=='__main__': main()
