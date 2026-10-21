#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fixed TCP routes for local diagnostics. TLS remains end to end."""
import selectors
import socket
import socketserver
import threading

ROUTES = {8443: 'control-plane', 8444: 'effect-receiver', 8445: 'worker-a',
          8446: 'worker-b', 8447: 'verifier'}
SLOTS = threading.BoundedSemaphore(32)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        if not SLOTS.acquire(blocking=False):
            return
        try:
            with socket.create_connection((self.server.target, 8443), timeout=5) as upstream:
                self.request.settimeout(5)
                with selectors.DefaultSelector() as events:
                    events.register(self.request, selectors.EVENT_READ, upstream)
                    events.register(upstream, selectors.EVENT_READ, self.request)
                    while True:
                        ready = events.select(timeout=30)
                        if not ready:
                            return
                        for key, _ in ready:
                            chunk = key.fileobj.recv(65536)
                            if not chunk:
                                return
                            key.data.sendall(chunk)
        except OSError:
            return
        finally:
            SLOTS.release()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


for port, target in ROUTES.items():
    server = Server(('0.0.0.0', port), Handler)
    server.target = target
    threading.Thread(target=server.serve_forever, daemon=True).start()
threading.Event().wait()
