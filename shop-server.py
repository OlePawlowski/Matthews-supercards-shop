#!/usr/bin/env python3
"""Entwicklungsserver mit Stripe-Checkout für die Testbuchung.

Liefert wie dev-server.py die Seiten aus website/ (ohne Cache) und bietet
zusätzlich einen Endpunkt, der eine Stripe-Checkout-Sitzung anlegt:

    POST /api/checkout   -> {"url": "https://checkout.stripe.com/..."}

Der geheime Schlüssel kommt ausschließlich aus der Umgebung oder aus der
Datei .env im Projektordner — er steht nie im ausgelieferten HTML oder JS.

    python3 shop-server.py [port]
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HIER = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.join(HIER, 'website')
STRIPE_API = 'https://api.stripe.com/v1/checkout/sessions'

# Artikel, die bestellt werden können. Preise in Cent (brutto).
# TODO Kunde: Versandkosten bestätigen.
# cent = Einzelpreis, cent_ab_2 = Stückpreis ab zwei Spielen
# cent = Quartett im Schuber, cent_aufsteller = Zusatz mit persönlicher Karte
ARTIKEL = {
    'creme21': dict(name='Creme 21 Youngtimer Rallye 2026 — Quartett im Schuber',
                    cent=2940, cent_aufsteller=540),
    'adac':    dict(name='ADAC Westfalen Classic 2026 — Quartett im Schuber',
                    cent=2940, cent_aufsteller=540),
    # Derselbe Aufsteller einzeln, ohne Quartett
    'aufsteller-creme21': dict(
        name='Creme 21 Youngtimer Rallye 2026 — Aufsteller mit persönlicher Spielkarte',
        cent=740, cent_aufsteller=0),
    'aufsteller-adac': dict(
        name='ADAC Westfalen Classic 2026 — Aufsteller mit persönlicher Spielkarte',
        cent=740, cent_aufsteller=0),
}
VERSAND_CENT = 495
MAX_MENGE = 10


def umgebung(name):
    """Wert aus der Umgebung oder aus .env lesen."""
    w = os.environ.get(name, '').strip()
    if w:
        return w
    pfad = os.path.join(HIER, '.env')
    if os.path.exists(pfad):
        for zeile in open(pfad, encoding='utf-8'):
            zeile = zeile.strip()
            if zeile.startswith(name + '='):
                return zeile.split('=', 1)[1].strip().strip('"\'')
    return ''


def schluessel():
    return umgebung('STRIPE_SECRET_KEY')


def oeffentlicher_schluessel():
    return umgebung('STRIPE_PUBLISHABLE_KEY')


class Handler(SimpleHTTPRequestHandler):

    # ── Hilfen ───────────────────────────────────────────────────────────
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        super().end_headers()

    def antwort(self, code, daten):
        roh = json.dumps(daten).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(roh)))
        self.end_headers()
        self.wfile.write(roh)

    def log_message(self, format, *args):
        sys.stderr.write('%s  %s\n' % (self.log_date_time_string(), format % args))

    # ── Zahlungsstatus abfragen (Danke-Seite) ────────────────────────────
    def do_GET(self):
        if self.path.split('?')[0].rstrip('/') != '/api/sitzung':
            return super().do_GET()

        kennung = urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query).get('id', [''])[0]
        if not kennung.startswith('cs_'):
            return self.antwort(400, {'fehler': 'Keine gültige Vorgangsnummer'})

        key = schluessel()
        if not key:
            return self.antwort(500, {'fehler': 'Kein Schlüssel hinterlegt'})

        anfrage = urllib.request.Request(
            'https://api.stripe.com/v1/checkout/sessions/'
            + urllib.parse.quote(kennung, safe=''),
            headers={'Authorization': 'Bearer ' + key})
        try:
            with urllib.request.urlopen(anfrage, timeout=15) as a:
                d = json.loads(a.read())
            return self.antwort(200, {
                'status': d.get('status'),
                'bezahlt': d.get('payment_status') == 'paid',
                'betrag': d.get('amount_total'),
                'email': (d.get('customer_details') or {}).get('email'),
            })
        except Exception as e:
            self.log_message('Statusabfrage fehlgeschlagen: %s', e)
            return self.antwort(502, {'fehler': 'Status nicht abrufbar'})

    # ── Checkout ─────────────────────────────────────────────────────────
    def do_POST(self):
        if self.path.rstrip('/') != '/api/checkout':
            return self.antwort(404, {'fehler': 'Unbekannter Endpunkt'})

        key = schluessel()
        if not key:
            return self.antwort(500, {'fehler':
                'Kein STRIPE_SECRET_KEY gesetzt. Schlüssel in .env eintragen '
                'und den Server neu starten.'})
        # Nur Testschlüssel zulassen. Live-Schlüssel gibt es in mehreren
        # Formen (sk_live_, rk_live_, pk_live_) — deshalb nicht auf ein
        # Präfix prüfen, sondern alles ablehnen, was nicht Test ist.
        if not key.startswith(('sk_test_', 'rk_test_')):
            return self.antwort(400, {'fehler':
                'Hinterlegt ist kein Testschlüssel. Für Testbuchungen den '
                'Schlüssel bei eingeschaltetem Testmodus holen (sk_test_…). '
                'Live-Schlüssel werden hier bewusst abgewiesen.'})

        try:
            laenge = int(self.headers.get('Content-Length') or 0)
            eingang = json.loads(self.rfile.read(laenge) or b'{}')
        except (ValueError, json.JSONDecodeError):
            return self.antwort(400, {'fehler': 'Fehlerhafte Anfrage'})

        artikel = ARTIKEL.get(str(eingang.get('artikel', '')))
        if not artikel:
            return self.antwort(400, {'fehler': 'Unbekannter Artikel'})

        try:
            menge = max(1, min(MAX_MENGE, int(eingang.get('menge', 1))))
        except (TypeError, ValueError):
            menge = 1

        # Hinter dem Proxy des Hosters kommt die Anfrage per HTTP an,
        # die öffentliche Adresse ist aber HTTPS — sonst leitet Stripe
        # nach der Zahlung auf eine tote Adresse zurück.
        herkunft = self.headers.get('Origin')
        if not herkunft:
            wirt = self.headers.get('Host') or 'localhost:4173'
            schema = self.headers.get('X-Forwarded-Proto') or (
                'http' if wirt.startswith('localhost') else 'https')
            herkunft = schema + '://' + wirt
        felder = [
            ('mode', 'payment'),
            # Eingebettet statt Weiterleitung: der Zahlungsblock sitzt auf
            # unserer Seite, nur das Formular selbst kommt von Stripe.
            ('ui_mode', 'embedded_page'),
            ('return_url', herkunft + '/danke.html?sitzung={CHECKOUT_SESSION_ID}'),
            ('line_items[0][price_data][currency]', 'eur'),
            ('line_items[0][price_data][unit_amount]', str(artikel['cent'])),
            ('line_items[0][price_data][product_data][name]', artikel['name']),
            ('line_items[0][quantity]', str(menge)),
            ('shipping_address_collection[allowed_countries][0]', 'DE'),
            ('shipping_address_collection[allowed_countries][1]', 'AT'),
            ('shipping_address_collection[allowed_countries][2]', 'CH'),
            ('shipping_options[0][shipping_rate_data][type]', 'fixed_amount'),
            ('shipping_options[0][shipping_rate_data][display_name]', 'Versand'),
            ('shipping_options[0][shipping_rate_data][fixed_amount][amount]', str(VERSAND_CENT)),
            ('shipping_options[0][shipping_rate_data][fixed_amount][currency]', 'eur'),
            ('automatic_tax[enabled]', 'false'),
            # Welche Zahlungsarten erscheinen, steuert seit 2025 allein das
            # Stripe-Dashboard (Einstellungen → Zahlungsmethoden). Der
            # Parameter payment_method_types wird nicht mehr angenommen.
        ]
        # Angaben aus dem Formular als Notiz an die Zahlung hängen
        for name in ('startnr', 'name'):
            wert = str(eingang.get(name, ''))[:80].strip()
            if wert:
                felder.append(('metadata[%s]' % name, wert))
        if eingang.get('email'):
            felder.append(('customer_email', str(eingang['email'])[:120]))

        # Aufsteller als eigene Position, damit er auf der Rechnung steht
        if eingang.get('aufsteller') and artikel['cent_aufsteller']:
            felder += [
                ('line_items[1][price_data][currency]', 'eur'),
                ('line_items[1][price_data][unit_amount]', str(artikel['cent_aufsteller'])),
                ('line_items[1][price_data][product_data][name]',
                 'Aufsteller mit persönlicher Spielkarte'),
                ('line_items[1][quantity]', str(menge)),
            ]

        anfrage = urllib.request.Request(
            STRIPE_API,
            data=urllib.parse.urlencode(felder).encode('utf-8'),
            headers={'Authorization': 'Bearer ' + key,
                     'Content-Type': 'application/x-www-form-urlencoded'})
        try:
            with urllib.request.urlopen(anfrage, timeout=20) as a:
                sitzung = json.loads(a.read())
            return self.antwort(200, {
                'client_secret': sitzung.get('client_secret'),
                'publishable_key': oeffentlicher_schluessel(),
            })
        except urllib.error.HTTPError as e:
            try:
                meldung = json.loads(e.read())['error']['message']
            except Exception:
                meldung = 'Stripe hat die Anfrage abgelehnt (HTTP %d).' % e.code
            self.log_message('Stripe-Fehler: %s', meldung)
            return self.antwort(502, {'fehler': meldung})
        except Exception as e:
            self.log_message('Netzwerkfehler: %s', e)
            return self.antwort(502, {'fehler': 'Stripe ist nicht erreichbar.'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 4173))
    k = schluessel()
    zustand = ('Testmodus' if k.startswith(('sk_test_', 'rk_test_'))
               else 'LIVE-Schlüssel — wird abgewiesen!' if k
               else 'kein Schlüssel hinterlegt')
    print('Shop auf http://localhost:%d  ·  Stripe: %s' % (port, zustand))
    # Lokal nur an den eigenen Rechner binden, beim Hoster an alle
    # Schnittstellen — sonst erreicht Render den Dienst nicht.
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    ThreadingHTTPServer((host, port),
                        partial(Handler, directory=ORDNER)).serve_forever()
