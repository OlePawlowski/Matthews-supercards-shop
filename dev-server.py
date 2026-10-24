#!/usr/bin/env python3
"""Entwicklungsserver fuer die Startseite.

Wie `python3 -m http.server`, schickt aber `Cache-Control: no-store`. Ohne das
haelt der Browser CSS und JS fest, waehrend am Entwurf gearbeitet wird — man
sieht dann alte Staende und sucht Fehler, die laengst behoben sind.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class OhneCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        # Erlaubt, Bilder von hier in eine fremde Seite zu laden — beim
        # Erstellen von Konfigurator-Screenshots gebraucht.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):        # knapper als der Standard
        sys.stderr.write('%s  %s\n' % (self.log_date_time_string(), format % args))


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    ordner = sys.argv[2] if len(sys.argv) > 2 else 'website'
    handler = partial(OhneCache, directory=ordner)
    print('Startseite auf http://localhost:%d  (aus %s/, ohne Cache)' % (port, ordner))
    ThreadingHTTPServer(('127.0.0.1', port), handler).serve_forever()
