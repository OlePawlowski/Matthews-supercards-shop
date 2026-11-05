#!/usr/bin/env python3
"""Shop und Konfiguratoren zu einem Verzeichnis für den Webspace legen.

Ergebnis ist `dist/` — genau das, was hochgeladen wird:

    dist/
      index.html, rallye-creme21.html, archiv.html, assets/ …   (Shop)
      konfigurator/creme21/   index.php, upload.php, …          (Generator)
      konfigurator/adac/      …

Die Adressen der Generatoren in den Shopseiten werden dabei von
`https://…visionwerk.agency/` auf den eigenen Pfad `konfigurator/<id>/`
umgeschrieben, und der Generator bekommt den Rückweg zur Bestellseite
gesetzt. Beides nur in `dist/` — die Quellen bleiben unberührt.

Aufruf:  python3 zusammenstellen.py
"""

import os
import re
import shutil
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, 'website')
ZIEL = os.path.join(HIER, 'dist')

# Generator-Apps auf dieser Maschine. Fehlt einer, wird er übersprungen
# und der Shop verweist weiter auf die Adresse im Netz.
APPS = {
    'creme21': dict(
        pfad=os.path.expanduser(
            '~/Documents/Creme21-Spielkartengenerator/creme21-app'),
        netz='https://creme21-spielkartengenerator.visionwerk.agency/',
        bestellseite='rallye-creme21.html',
    ),
    'adac': dict(
        pfad=os.path.expanduser(
            '~/Documents/ Adac-Westfalen-Classic/adac-app'),
        netz='https://adac-spielkartengenerator.visionwerk.agency/',
        bestellseite='rallye-adac.html',
    ),
}

# Nichts davon gehört auf den Webspace.
WEG = {'.git', '.DS_Store', '__pycache__', '.gitignore',
       'node_modules', '.vscode', '.idea'}
WEG_ENDUNG = ('.zip', '.af', '.pyc', '.bak', '.original')


def leeren(ordner):
    if os.path.isdir(ordner):
        shutil.rmtree(ordner)
    os.makedirs(ordner)


def kopieren(von, nach, ohne_inhalt=()):
    """Verzeichnis kopieren, Arbeitsdateien weglassen."""
    anzahl = 0
    for wurzel, ordner, dateien in os.walk(von):
        ordner[:] = [o for o in ordner
                     if o not in WEG and o not in ohne_inhalt]
        rel = os.path.relpath(wurzel, von)
        zielordner = nach if rel == '.' else os.path.join(nach, rel)
        os.makedirs(zielordner, exist_ok=True)
        for d in dateien:
            if d in WEG or d.endswith(WEG_ENDUNG):
                continue
            shutil.copy2(os.path.join(wurzel, d), os.path.join(zielordner, d))
            anzahl += 1
    return anzahl


def umschreiben(datei, paare):
    """Adressen in einer Textdatei ersetzen. Gibt die Trefferzahl zurück."""
    with open(datei, encoding='utf-8') as f:
        text = f.read()
    treffer = 0
    for alt, neu in paare:
        treffer += text.count(alt)
        text = text.replace(alt, neu)
    if treffer:
        with open(datei, 'w', encoding='utf-8') as f:
            f.write(text)
    return treffer


def main():
    if not os.path.isdir(QUELLE):
        sys.exit('website/ fehlt — erst python3 build.py laufen lassen.')

    leeren(ZIEL)
    n = kopieren(QUELLE, ZIEL)
    print('Shop: %d Dateien' % n)

    # Welche Generatoren liegen hier wirklich?
    dabei = {}
    for sid, app in APPS.items():
        if not os.path.isdir(app['pfad']):
            print('Generator %s nicht gefunden — bleibt im Netz verlinkt' % sid)
            continue
        ziel = os.path.join(ZIEL, 'konfigurator', sid)
        # uploads/ und storage/ sind Ablagen des Betriebs, nicht des Codes;
        # leer anlegen statt die Einreichungen mitzuschleppen.
        n = kopieren(app['pfad'], ziel, ohne_inhalt=('uploads', 'storage'))
        for ablage in ('uploads', 'storage/private'):
            os.makedirs(os.path.join(ziel, ablage), exist_ok=True)
        print('Generator %s: %d Dateien' % (sid, n))
        dabei[sid] = app

    if not dabei:
        print('\nNur der Shop liegt in dist/.')
        return

    # Shopseiten: Netzadresse → eigener Pfad
    paare = [(app['netz'], 'konfigurator/%s/' % sid)
             for sid, app in dabei.items()]
    gesamt = 0
    for wurzel, _, dateien in os.walk(ZIEL):
        if os.path.join(ZIEL, 'konfigurator') in wurzel:
            continue
        for d in dateien:
            if d.endswith(('.html', '.js')):
                gesamt += umschreiben(os.path.join(wurzel, d), paare)
    print('Verweise auf den eigenen Pfad umgestellt: %d' % gesamt)

    # Generator: Rückweg zur Bestellseite
    for sid, app in dabei.items():
        idx = os.path.join(ZIEL, 'konfigurator', sid, 'index.php')
        if not os.path.exists(idx):
            continue
        with open(idx, encoding='utf-8') as f:
            text = f.read()
        neu, anzahl = re.subn(
            r"window\.SHOP_BESTELLUNG\s*=\s*'[^']*';",
            "window.SHOP_BESTELLUNG = '../../%s';" % app['bestellseite'],
            text)
        if anzahl:
            with open(idx, 'w', encoding='utf-8') as f:
                f.write(neu)
            print('Rückweg in %s gesetzt' % sid)
        else:
            print('ACHTUNG: %s/index.php kennt SHOP_BESTELLUNG nicht' % sid)

    print('\nFertig. Inhalt von dist/ auf den Webspace legen.')
    print('Schreibrechte brauchen je Generator uploads/ und storage/private/.')
    print('zugangsdaten.php (SMTP) von Hand danebenlegen — sie ist absichtlich')
    print('nicht im Repository.')


if __name__ == '__main__':
    main()
