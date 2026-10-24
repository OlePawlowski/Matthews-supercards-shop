#!/usr/bin/env python3
"""Prüft die erzeugten Seiten auf tote Verweise und fehlende Bilder.

    python3 check.py
"""
import io, re, os, glob, sys

ORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website')


def main():
    os.chdir(ORT)
    seiten = sorted(glob.glob('*.html'))
    ids = {s: set(re.findall(r'id="([^"]+)"', io.open(s, encoding='utf-8').read()))
           for s in seiten}
    fehler = []

    for s in seiten:
        h = io.open(s, encoding='utf-8').read()

        for href in re.findall(r'href="([^"]+)"', h):
            if href.startswith(('http', 'mailto:', 'tel:', 'assets/')) or href == '#':
                continue
            pfad, _, anker = href.partition('#')
            datei = pfad.split('?')[0]          # Query gehört nicht zum Dateinamen
            ziel = datei or s
            if datei and not os.path.exists(datei):
                fehler.append('%s → Datei fehlt: %s' % (s, datei))
            elif anker and ziel in ids and anker not in ids[ziel]:
                fehler.append('%s → Anker fehlt: %s' % (s, href))

        for src in re.findall(r'src="(assets/[^"]+)"', h):
            if not os.path.exists(src.split('?')[0]):
                fehler.append('%s → Bild fehlt: %s' % (s, src))

        if h.count('<h1') != 1:
            fehler.append('%s → %d <h1> (genau eine erwartet)' % (s, h.count('<h1')))
        for img in re.findall(r'<img [^>]*>', h):
            if 'alt=' not in img:
                fehler.append('%s → <img> ohne alt: %s' % (s, img[:60]))

    offen = sum(io.open(s, encoding='utf-8').read().count('TODO Kunde') for s in seiten)
    print('%d Seiten geprüft: %s' % (len(seiten), ', '.join(seiten)))
    print('Offene Punkte (TODO Kunde): %d' % offen)
    if fehler:
        print('\nProbleme (%d):' % len(fehler))
        for f in sorted(set(fehler)):
            print('  ', f)
        return 1
    print('Keine toten Verweise, keine fehlenden Bilder.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
