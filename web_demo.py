"""Offline, local-only browser demo for the BankGPT snapshot knowledge system.

Run from the project root: python web_demo.py
Requires Python 3.9+ and no third-party packages.
Do not deploy the supplied website snapshots to a public host.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'harness'))
from run_eval import load_snapshots, load_submission

MAX_REQUEST_BYTES = 32_768


class State:
    def __init__(self, folder: Path):
        self.snapshots = load_snapshots(folder)
        if not self.snapshots:
            raise RuntimeError(
                'No website snapshots found. Put the five provided ZIPs in snapshots_zip/ '
                'and restart this demo.'
            )
        self.knowledge = load_submission(ROOT / 'submission')
        for snap in self.snapshots:
            print(f'Loading {snap.taken_on}: {len(snap.pages)} pages', flush=True)
            self.knowledge.ingest(snap)
        self.by_id = {snap.snapshot_id: snap for snap in self.snapshots}
        self.lock = threading.RLock()
        self._conflicts = None
        self.totals = sum(len(s.pages) for s in self.snapshots)

    def get_snap(self, snapshot_id: str):
        return self.by_id.get(snapshot_id or self.snapshots[-1].snapshot_id)


class Handler(BaseHTTPRequestHandler):
    state: State

    def log_message(self, fmt, *args):
        if self.path.startswith('/api/'):
            return
        super().log_message(fmt, *args)

    def reply(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlsplit(self.path)
        qs = parse_qs(u.query)
        get = lambda name, default='': qs.get(name, [default])[0]
        try:
            if u.path in ('/', '/index.html'):
                data = (ROOT / 'web' / 'index.html').read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Content-Security-Policy', "default-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; object-src 'none'")
                self.end_headers()
                self.wfile.write(data)
                return
            if u.path == '/api/snapshots':
                self.reply({
                    'snapshots': [dict(id=s.snapshot_id, date=s.taken_on, pages=len(s.pages),
                                       label=s.snapshot_id.split('_', 2)[-1].replace('_', ' ').title())
                                  for s in self.state.snapshots],
                    'total_pages': self.state.totals,
                })
                return
            if u.path == '/api/pages':
                s = self.state.get_snap(get('snapshot'))
                if not s:
                    return self.reply({'error': 'Invalid snapshot'}, 404)
                query = get('q').lower().strip()[:150]
                hits = []
                if query:
                    toks = query.split()
                    for index, p in enumerate(s.pages):
                        title = (p.title + ' ' + p.url).lower()
                        if all(k in title for k in toks):
                            hits.append((0, index, p))
                        elif all(k in p.markdown.lower() for k in toks):
                            hits.append((1, index, p))
                    hits.sort(key=lambda x: (x[0], x[1]))
                else:
                    hits = [(0, i, p) for i, p in enumerate(s.pages)]
                limit = min(120, max(1, int(get('limit', '80'))))
                self.reply(dict(count=len(hits), pages=[dict(index=i, title=p.title or p.url,
                                                          url=p.url) for _, i, p in hits[:limit]]))
                return
            if u.path == '/api/locate':
                s = self.state.get_snap(get('snapshot'))
                if not s:
                    return self.reply({'error': 'Invalid snapshot'}, 404)
                target = get('url').rstrip('/')
                for index, page in enumerate(s.pages):
                    if page.url.rstrip('/') == target:
                        return self.reply({'index': index})
                return self.reply({'error': 'Source page not in selected snapshot'}, 404)
            if u.path == '/api/page':
                s = self.state.get_snap(get('snapshot'))
                if not s:
                    return self.reply({'error': 'Invalid snapshot'}, 404)
                index = int(get('index', '0'))
                if index < 0 or index >= len(s.pages):
                    return self.reply({'error': 'Invalid page index'}, 404)
                p = s.pages[index]
                self.reply(dict(title=p.title, url=p.url, markdown=p.markdown,
                                fetched_at=p.fetched_at, index=index, snapshot=s.snapshot_id))
                return
            if u.path == '/api/conflicts':
                with self.state.lock:
                    if self.state._conflicts is None:
                        self.state._conflicts = self.state.knowledge.conflicts()
                    all_conflicts = self.state._conflicts
                query = get('q').lower().strip()[:120]
                if query:
                    filtered = [c for c in all_conflicts if query in c.topic.lower() or
                                any(query in str(v).lower() for v in c.values)]
                else:
                    filtered = all_conflicts
                self.reply(dict(count=len(filtered), conflicts=[asdict(c) for c in filtered[:100]]))
                return
            self.reply({'error': 'Unknown endpoint'}, 404)
        except (ValueError, TypeError):
            self.reply({'error': 'Invalid request'}, 400)
        except Exception as exc:
            print('GET error:', repr(exc), file=sys.stderr)
            self.reply({'error': 'Unable to load this content'}, 500)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/answer':
            return self.reply({'error': 'Unknown endpoint'}, 404)
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if not 0 < n <= MAX_REQUEST_BYTES:
                return self.reply({'error': 'Request too large or empty'}, 400)
            body = json.loads(self.rfile.read(n))
            question = str(body.get('question', '')).strip()[:1000]
            if not question:
                return self.reply({'error': 'Enter a question'}, 400)
            as_of = body.get('as_of') or None
            if as_of and as_of not in {s.taken_on for s in self.state.snapshots}:
                return self.reply({'error': 'Select a valid snapshot date'}, 400)
            with self.state.lock:
                result = self.state.knowledge.answer(question, as_of=as_of)
            self.reply(asdict(result))
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            self.reply({'error': 'Invalid input'}, 400)
        except Exception as exc:
            print('Answer error:', repr(exc), file=sys.stderr)
            self.reply({'error': 'Unable to answer the question'}, 500)


def main():
    ap = argparse.ArgumentParser(description='Local credit union website snapshot browser')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--no-open', action='store_true', help='Do not open a browser tab')
    args = ap.parse_args()
    if not (1024 <= args.port <= 65535):
        ap.error('Port must be between 1024 and 65535')
    print('Preparing the local website snapshot browser...', flush=True)
    state = State(ROOT / 'snapshots')
    local_handler = type('LocalHandler', (Handler,), {'state': state})
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), local_handler)
    except OSError as e:
        raise SystemExit(f'Cannot start on port {args.port}: {e} (try --port 8766)')
    url = f'http://127.0.0.1:{args.port}/'
    print(f'\nOpen your browser: {url}\nTo stop: press Ctrl+C in this terminal.\n', flush=True)
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
