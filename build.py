#!/usr/bin/env python3
"""Erzeugt die Unterseiten des Shops und hält die Navigation einheitlich.

Die Startseite (website/index.html) wird von Hand gepflegt; dieses Skript
tauscht dort nur den Navigationsblock zwischen den Markern aus. Alle anderen
Seiten entstehen vollständig hier aus den Daten weiter unten.

    python3 build.py
"""
import io, os, re, html

ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'website')

# ── Daten ────────────────────────────────────────────────────────────────
# TODO Kunde: Preise, Auflagen und Liefertermine sind mit Matthias
# abzustimmen. Die Freischalttermine stammen aus den Konfiguratoren.

# Preis je Spiel in Euro (brutto). TODO Kunde: für ADAC bestätigen.
PREIS = {'creme21': 38.40, 'adac': 38.40}

KONFIGURATOREN = {
    'creme21': dict(
        name='Creme 21 Youngtimer Rallye',
        kurz='Creme 21',
        jahr='2026',
        url='https://creme21-spielkartengenerator.visionwerk.agency/',
        start='16.09.2026',
        farbe='#EE7C36',
    ),
    'adac': dict(
        name='ADAC Westfalen Classic',
        kurz='ADAC Westfalen Classic',
        jahr='2026',
        url='https://adac-spielkartengenerator.visionwerk.agency/',
        start='11.10.2026',
        farbe='#FFCF00',
    ),
}

# Offene Generatoren — jeder kann damit eine eigene Karte bauen.
GENERATOREN = [
    dict(id='oldtimer', name='Oldtimer', unter='Klassiker aller Marken',
         url='https://oldtimer-spielkartengenerator.visionwerk.agency/'),
    dict(id='rallye', name='Rallye', unter='Crew, Startnummer, Fahrzeug',
         url='https://ralley-spielkartengenerator.visionwerk.agency/'),
    dict(id='mofa', name='Mofa', unter='Zweitakt und Dolce Vita',
         url='https://mofa-spielkartengenerator.visionwerk.agency/'),
]

# art: rallye | thema | marke     konf: Schlüssel oben oder None
QUARTETTE = [
    dict(id='creme21', titel='Creme 21 Youngtimer Rallye', jahr='2026',
         art='rallye', konf='creme21', bild='q-creme21.jpg',
         unter='Jubiläumsausgabe · 25 Jahre',
         text='Teilnehmerquartett der Youngtimer Rallye. Jede Crew gestaltet '
              'ihre Karte im eigenen Konfigurator; dazu Schuber und Stanzform '
              'im Rallye-Design.',
         bestellbar=True),
    dict(id='adac', titel='ADAC Westfalen Classic', jahr='2026',
         art='rallye', konf='adac', bild='q-adac.jpg',
         unter='7. Int. ADAC Classic Tour',
         text='Teilnehmerquartett der Westfalen Classic. Gleiches Kartenbild '
              'wie Creme 21, übertragen auf Rapport, Logo und Startschild '
              'des ADAC.',
         bestellbar=True),
    dict(id='belmot', titel='Belmot Swiss Classic', jahr='2026',
         art='rallye', konf=None, bild='q-belmont.jpg',
         unter='World Rallye',
         text='Schuber im Karo-Rapport für die Schweizer Ausfahrt — Gestaltung, '
              'Stanzkontur und Konfektionierung.',
         bestellbar=False),
    dict(id='oldrockets', titel='Old Rockets · US Cars', jahr='2025',
         art='marke', konf=None, bild='q-oldrockets.jpg',
         unter='für Borrmann Motors',
         text='Themenquartett für den Werkstattauftritt: US-Klassiker, '
              'recherchierter Datensatz, Werkstattlogo auf jeder Karte.',
         bestellbar=False),
    dict(id='mofa1a', titel='Mofa 1A', jahr='2026',
         art='thema', konf=None, bild='q-mofa.jpg',
         unter='32 Mofas, 32 Geschichten',
         text='Quartett und Faltschachtel im Retro-Design. Von Piaggio bis '
              'Zündapp — jede Karte erzählt ihre eigene Geschichte.',
         bestellbar=False),
    dict(id='cipere', titel='CiPeRe · Der Franzose', jahr='2003',
         art='thema', konf=None, bild='q-franzose.jpg',
         unter='Citroën Peugeot Renault',
         text='Jeu d’Atouts — französisches Autoquartett mit gezeichnetem '
              'Rapport und dreisprachiger Spielanleitung.',
         bestellbar=False),
    dict(id='supercars', titel='Amerikanische Supercars', jahr='—',
         art='thema', konf=None, bild='q-supercars.jpg',
         unter='mit Supertrumpf',
         text='Auto-Quartett mit amerikanischen Klassikern. Klassisches '
              'Kartenbild mit Supertrumpf-Stern.',
         bestellbar=False),
    dict(id='wilden', titel='Die Wilden 1979–1989', jahr='—',
         art='thema', konf=None, bild='q-wilden.jpg',
         unter='mit Supertrumpf',
         text='Youngtimer aus einem Jahrzehnt, in dem Autos noch Kanten '
              'hatten. Mit Supertrumpf.',
         bestellbar=False),
]

ART_NAME = {'rallye': 'Rallye-Quartett', 'thema': 'Themen-Quartett',
            'marke': 'Marken-Quartett'}

NAV = [
    ('index.html#angebot',      'Angebot'),
    ('rallyes.html',            'Rallyes'),
    ('index.html#konfigurator', 'Konfigurator'),
    ('archiv.html',             'Archiv'),
    ('index.html#matthias',     'Über uns'),
    ('index.html#unternehmen',  'Unternehmen'),
]

TEL_ANZEIGE = '0441 / 23 32 252'
TEL_LINK    = '+494412332252'
MAIL        = 'matthias-hellwege@web.de'


def e(s):
    return html.escape(str(s), quote=False)


# ── Bausteine ────────────────────────────────────────────────────────────

def nav_links(aktiv, praefix=''):
    aus = []
    for ziel, text in NAV:
        z = ziel if not ziel.startswith('index.html') or praefix else ziel
        cls = ' class="is-cur"' if ziel.split('#')[0] == aktiv else ''
        aus.append('<a href="%s"%s>%s</a>' % (z, cls, e(text)))
    return aus


def kopf(titel, beschreibung, aktiv, favicon_pfad='assets/img/favicon.svg'):
    links = nav_links(aktiv)
    return '''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titel)s — Matthews SuperCards</title>
<meta name="description" content="%(besch)s">
<link rel="icon" href="%(fav)s" type="image/svg+xml">
<meta name="theme-color" content="#17160F">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Matthews SuperCards">
<meta property="og:title" content="%(titel)s — Matthews SuperCards">
<meta property="og:description" content="%(besch)s">
<meta property="og:image" content="assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<a class="skip" href="#inhalt">Zum Inhalt springen</a>

<div class="topbar">
  <div class="wrap topbar__in">
    <p class="topbar__claim"><b>Matthews SuperCards<sup>&reg;</sup></b> — Quartett-Manufaktur, Oldenburg</p>
    <ul class="topbar__meta">
      <li>Eigene Gestaltung</li>
      <li>Druck &amp; Konfektionierung</li>
      <li><a href="tel:%(tell)s">%(tela)s</a></li>
    </ul>
  </div>
</div>

<header class="head" id="head">
  <div class="wrap head__in">
    <a class="head__logo" href="index.html" aria-label="Matthews SuperCards — Startseite">
      <img src="assets/img/logo.png" alt="Matthews SuperCards" width="504" height="101">
    </a>
    <!-- NAV:START -->
    <nav class="nav" aria-label="Hauptnavigation">
      %(nav)s
    </nav>
    <!-- NAV:END -->
    <div class="head__act">
      <a class="btn btn--marke" href="rallyes.html">Quartett bestellen</a>
    </div>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="mobnav" aria-label="Men&uuml; &ouml;ffnen">
      <span></span><span></span><span></span>
    </button>
  </div>
  <!-- MOBNAV:START -->
  <div class="mobnav" id="mobnav" hidden>
    %(mobnav)s
    <a class="btn btn--marke" href="rallyes.html">Quartett bestellen</a>
  </div>
  <!-- MOBNAV:END -->
</header>

<main id="inhalt">
''' % dict(titel=e(titel), besch=e(beschreibung), fav=favicon_pfad,
           nav='\n      '.join(links), mobnav='\n    '.join(links),
           tell=TEL_LINK, tela=TEL_ANZEIGE)


def fuss():
    return '''</main>

<div class="rufleiste" id="rufleiste" hidden>
  <a class="rufleiste__ruf" href="tel:%(tell)s">
    <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="currentColor"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1l-2.3 2.2Z"/></svg>
    Anrufen</a>
  <a class="rufleiste__tun" href="rallyes.html">Quartett bestellen</a>
</div>

<footer class="foot">
  <div class="wrap foot__in">
    <div class="foot__brand">
      <img src="assets/img/logo.png" alt="Matthews SuperCards" width="504" height="101">
      <p>Quartett-Manufaktur aus Oldenburg.<br>Gestaltung, Druck und Konfektionierung aus einer Hand.</p>
    </div>
    <nav class="foot__col" aria-label="Sortiment">
      <h4>Sortiment</h4>
      <a href="rallyes.html">Rallye-Quartette</a>
      <a href="index.html#unternehmen">Marken-Quartett</a>
      <a href="archiv.html?art=thema">Themen-Quartett</a>
      <a href="index.html#unternehmen">Schuber &amp; Faltschachtel</a>
    </nav>
    <nav class="foot__col" aria-label="Service">
      <h4>Service</h4>
      <a href="index.html#konfigurator">Konfigurator</a>
      <a href="archiv.html">Archiv</a>
      <a href="index.html#matthias">&Uuml;ber uns</a>
      <a href="index.html#unternehmen">F&uuml;r Unternehmen</a>
    </nav>
    <div class="foot__col">
      <h4>Kontakt</h4>
      <p>Matthias Hellwege<br>Hauptstra&szlig;e 58<br>26122 Oldenburg</p>
      <a href="tel:%(tell)s">%(tela)s</a>
      <a href="mailto:%(mail)s">%(mail)s</a>
    </div>
  </div>
  <div class="wrap foot__legal">
    <p>&copy; <span id="jahr">2026</span> Matthews SuperCards<sup>&reg;</sup></p>
    <nav aria-label="Rechtliches">
      <a href="#">Impressum</a><a href="#">Datenschutz</a><a href="#">AGB</a><a href="#">Widerruf</a><a href="#">Versand &amp; Zahlung</a>
    </nav>
  </div>
</footer>

<script src="assets/js/main.js"></script>
</body>
</html>
''' % dict(tell=TEL_LINK, tela=TEL_ANZEIGE, mail=MAIL)


# ── Archiv ───────────────────────────────────────────────────────────────

def archiv_seite():
    karten = []
    for q in QUARTETTE:
        k = KONFIGURATOREN.get(q['konf'])
        marken = []
        if k:
            marken.append('<span class="qm qm--konf">Konfigurator</span>')
        marken.append('<span class="qm">%s</span>' % e(ART_NAME[q['art']]))
        ziel = ('rallye-%s.html' % q['konf']) if (k and q['bestellbar']) else None
        aktion = ('<a class="qk2__link" href="%s">Ansehen &amp; bestellen</a>' % ziel
                  if ziel else
                  '<a class="qk2__link qk2__link--leise" href="index.html#unternehmen">'
                  'Ähnliches anfragen</a>')
        karten.append('''        <article class="qk2" data-konf="%(konf)s" data-art="%(art)s">
          <div class="qk2__bild"><img src="assets/img/%(bild)s" alt="%(alt)s" loading="lazy"></div>
          <div class="qk2__text">
            <p class="qk2__marken">%(marken)s</p>
            <h3>%(titel)s</h3>
            <p class="qk2__unter">%(unter)s · %(jahr)s</p>
            <p class="qk2__besch">%(besch)s</p>
            %(aktion)s
          </div>
        </article>''' % dict(
            konf=q['konf'] or 'ohne', art=q['art'], bild=q['bild'],
            alt=e('Quartett %s' % q['titel']), marken=' '.join(marken),
            titel=e(q['titel']), unter=e(q['unter']), jahr=e(q['jahr']),
            besch=e(q['text']), aktion=aktion))

    f_konf = ['<button class="filt is-on" data-f="konf" data-v="alle">Alle</button>']
    for sid, k in KONFIGURATOREN.items():
        anzahl = sum(1 for q in QUARTETTE if q['konf'] == sid)
        f_konf.append('<button class="filt" data-f="konf" data-v="%s">%s <i>%d</i></button>'
                      % (sid, e(k['kurz']), anzahl))
    ohne = sum(1 for q in QUARTETTE if not q['konf'])
    f_konf.append('<button class="filt" data-f="konf" data-v="ohne">Ohne Konfigurator <i>%d</i></button>' % ohne)

    f_art = ['<button class="filt is-on" data-f="art" data-v="alle">Alle</button>']
    for a, name in ART_NAME.items():
        anzahl = sum(1 for q in QUARTETTE if q['art'] == a)
        if anzahl:
            f_art.append('<button class="filt" data-f="art" data-v="%s">%s <i>%d</i></button>'
                         % (a, e(name), anzahl))

    return kopf('Archiv', 'Alle Quartette von Matthews SuperCards — nach Konfigurator '
                'und Art filterbar.', 'archiv.html') + '''
<section class="sec kopfsec">
  <div class="wrap">
    <p class="tag"><span class="tag__id">A</span> Archiv</p>
    <h1>Alles, was wir gemacht haben</h1>
    <p class="sec__lead">Jedes Quartett, das unsere Werkstatt verlassen hat — Rallye-Spiele
      mit eigenem Konfigurator, Themenquartette und Arbeiten für Marken. Filtern Sie nach
      Konfigurator oder nach Art.</p>
  </div>
</section>

<section class="sec sec--eng">
  <div class="wrap">
    <div class="filter">
      <div class="filter__reihe">
        <span class="filter__titel">Konfigurator</span>
        <div class="filter__knoepfe">%(fkonf)s</div>
      </div>
      <div class="filter__reihe">
        <span class="filter__titel">Art</span>
        <div class="filter__knoepfe">%(fart)s</div>
      </div>
    </div>

    <p class="filter__stand" id="filterstand" role="status">%(anz)d Quartette</p>

    <div class="qgrid" id="qgrid">
%(karten)s
    </div>

    <p class="qleer" id="qleer" hidden>Mit dieser Auswahl liegt nichts im Archiv.
      <button class="filt" data-f="reset" data-v="alle">Filter zurücksetzen</button></p>
  </div>
</section>

<section class="cta">
  <div class="wrap cta__in">
    <div>
      <p class="tag tag--light"><span class="tag__id">B</span> Ihr Spiel</p>
      <h2>Fehlt hier Ihres?</h2>
      <p class="sec__lead sec__lead--light">Rallye, Club oder Marke — erzählen Sie uns davon,
        wir melden uns mit Entwurf und Kalkulation.</p>
    </div>
    <div class="cta__act">
      <a class="btn btn--gelb btn--lg" href="index.html#unternehmen">Projekt anfragen</a>
      <a class="btn btn--line btn--lg" href="index.html#angebot">Eigene Karte bauen</a>
    </div>
  </div>
</section>
''' % dict(fkonf='\n          '.join(f_konf), fart='\n          '.join(f_art),
           karten='\n'.join(karten), anz=len(QUARTETTE),
           tell=TEL_LINK, tela=TEL_ANZEIGE) + fuss()


# ── Rallye-Übersicht ─────────────────────────────────────────────────────

def rallye_uebersicht():
    karten = []
    for q in QUARTETTE:
        if q['art'] != 'rallye':
            continue
        k = KONFIGURATOREN.get(q['konf'])
        if k and q['bestellbar']:
            stand = ('<p class="rk__stand"><b>Konfigurator offen</b> seit %s</p>' % e(k['start']))
            akt = ('<div class="rk__act">'
                   '<a class="btn btn--marke" href="rallye-%s.html#einreichen">'
                   'Spielkarte einreichen</a>'
                   '<a class="btn btn--ghost" href="rallye-%s.html#bestellen">'
                   'Quartett bestellen</a></div>' % (q['konf'], q['konf']))
        else:
            stand = '<p class="rk__stand rk__stand--aus">Abgeschlossenes Projekt</p>'
            akt = '<a class="btn btn--ghost" href="archiv.html">Im Archiv ansehen</a>'
        karten.append('''      <article class="rk">
        <div class="rk__bild"><img src="assets/img/%(bild)s" alt="%(alt)s" loading="lazy"></div>
        <div class="rk__text">
          <p class="rk__jahr">%(unter)s · %(jahr)s</p>
          <h2>%(titel)s</h2>
          <p>%(besch)s</p>
          %(stand)s
          %(akt)s
        </div>
      </article>''' % dict(bild=q['bild'], alt=e('Quartett ' + q['titel']),
                           unter=e(q['unter']), jahr=e(q['jahr']), titel=e(q['titel']),
                           besch=e(q['text']), stand=stand, akt=akt))

    return kopf('Rallye-Quartette', 'Quartette zu laufenden Rallyes — selbst gestalten '
                'oder fertig bestellen.', 'rallyes.html') + '''
<section class="sec kopfsec">
  <div class="wrap">
    <p class="tag"><span class="tag__id">A</span> Rallye-Quartette</p>
    <h1>Mitfahren oder mitspielen</h1>
    <p class="sec__lead">Zu jeder Rallye, die wir begleiten, gibt es zwei Wege: Teilnehmer
      gestalten ihre eigene Karte im Konfigurator — alle anderen bestellen das fertige
      Spiel. Gedruckt wird, sobald der Upload geschlossen ist.</p>
  </div>
</section>

<section class="sec sec--eng">
  <div class="wrap rliste">
%(karten)s
  </div>
</section>

<section class="sec sec--eng wahl">
  <div class="wrap">
    <header class="sec__head sec__head--mitte">
      <p class="tag"><span class="tag__id">B</span> Keine Rallye dabei?</p>
      <h2>Eigene Spielkarte bauen</h2>
      <p class="sec__lead">Drei Generatoren stehen jedem offen — unabhängig von einer
        Veranstaltung.</p>
    </header>
    <div class="wahl__genListe wahl__genListe--breit">
%(gens)s
    </div>
  </div>
</section>

<section class="sec sec--dark">
  <div class="wrap">
    <header class="sec__head sec__head--light">
      <p class="tag tag--light"><span class="tag__id">C</span> Ablauf</p>
      <h2>Vom Upload zum fertigen Spiel</h2>
    </header>
    <ol class="steps steps--drei">
      <li><span class="steps__n">01</span><h3>Konfigurator offen</h3>
        <p>Die Crews tragen ihre Fahrzeugdaten ein und setzen ihr Foto in die Karte.</p></li>
      <li><span class="steps__n">02</span><h3>Upload schlie&szlig;t</h3>
        <p>Wir montieren den Bogen, prüfen jede Karte und geben in den Druck.</p></li>
      <li><span class="steps__n">03</span><h3>Nach rund 14 Tagen</h3>
        <p>Das fertige Spiel geht an alle Besteller — Teilnehmer wie Sammler.</p></li>
    </ol>
  </div>
</section>
''' % dict(karten='\n'.join(karten), gens='\n'.join(
        '      <a class="gen" href="%s" target="_blank" rel="noopener">'
        '<b>%s</b><span>%s</span></a>' % (g['url'], e(g['name']), e(g['unter']))
        for g in GENERATOREN)) + fuss()


# ── Produktseite je Rallye ───────────────────────────────────────────────

def rallye_seite(sid):
    k = KONFIGURATOREN[sid]
    q = next(x for x in QUARTETTE if x['konf'] == sid)
    preis = PREIS.get(sid, 38.40)
    mengen = '\n'.join(
        '              <option value="%d"%s>%d&nbsp;Spiel%s</option>'
        % (n, ' selected' if n == 1 else '', n, '' if n == 1 else 'e')
        for n in range(1, 11))
    return kopf('%s %s' % (k['name'], k['jahr']),
                'Quartett zur %s %s — im Konfigurator gestalten oder fertig bestellen.'
                % (k['name'], k['jahr']), 'rallyes.html') + \
'''
<section class="sec produkt" id="bestellen">
  <div class="wrap produkt__in">

    <figure class="produkt__bild">
      <img src="assets/img/%(bild)s" alt="%(alt)s" width="560" height="850">
    </figure>

    <div class="produkt__text">
      <p class="tag tag--flagge">
        <span class="zielflagge" aria-hidden="true">
          <svg viewBox="0 0 30 26" width="30" height="26" fill="none">
            <path d="M3 1.5v23.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>
            <path d="M6 3c4.5-2 8.5 2 13 0 2.2-1 4.2-1 6-.3v13c-1.8-.7-3.8-.7-6 .3-4.5 2-8.5-2-13 0V3Z"
                  fill="#fff" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M6 3c2.3-1 4.4-.6 6.5 0v4.6c-2.1-.6-4.2-1-6.5 0V3Zm13 .6c2-.6 4-.9 6-.3v4.4c-2-.6-4-.4-6 .3V3.6Z"
                  fill="currentColor"/>
            <path d="M12.5 7.6c2.2.7 4.4.7 6.5 0v4.6c-2.1.7-4.3.7-6.5 0V7.6ZM6 12.2c2.3-1 4.4-.6 6.5 0v4.6c-2.1-.6-4.2-1-6.5 0v-4.6Zm13 0c2-.7 4-.9 6-.3v4.4c-2-.6-4-.4-6 .3v-4.4Z"
                  fill="currentColor"/>
          </svg>
        </span>
        Rallye-Quartett
      </p>
      <h1>%(titel)s</h1>
      <p class="produkt__unter">%(unter)s &middot; Ausgabe %(jahr)s</p>
      <p class="sec__lead">Hier zum Teilnehmerquartett der %(kurz)s. Bestellt hier euer
        eigenes, einmaliges Spiel im Schuber mit eurer Startnummer, sowie eurer eigenen
        Spielkarte als Aufsteller.</p>

      <dl class="specs specs--hell">
        <div><dt>Karten je Spiel</dt><dd>32</dd></div>
        <div><dt>Produktion</dt><dd>14 Tage bis 4 Wochen</dd></div>
      </dl>

      <form class="bestell" id="bestellform" data-preis="%(preis).2f" data-artikel="%(sid)s">
        <div class="bestell__preis">
          <span class="bestell__ab">Preis je Spiel</span>
          <b class="bestell__zahl" id="preis">%(preisDE)s&nbsp;&euro;</b>
          <span class="bestell__hinweis">zzgl. Versand &middot; Steuer wird im Checkout ausgewiesen</span>
        </div>

        <div class="bestell__reihe">
          <label class="vfeld vfeld--kurz">
            <span>Start-Nr.</span>
            <input type="text" name="startnr" maxlength="3" inputmode="numeric" placeholder="221">
          </label>
          <label class="vfeld">
            <span>Name *</span>
            <input type="text" name="name" maxlength="60" placeholder="Vor- und Nachname">
          </label>
        </div>
        <div class="bestell__reihe">
          <label class="vfeld">
            <span>E-Mail *</span>
            <input type="text" name="email" maxlength="80" inputmode="email">
          </label>
        </div>
        <div class="bestell__reihe">
          <label class="vfeld"><span>Stra&szlig;e *</span>
            <input type="text" name="strasse" maxlength="70"></label>
          <label class="vfeld vfeld--kurz"><span>Haus-Nr. *</span>
            <input type="text" name="hausnr" maxlength="10"></label>
        </div>
        <div class="bestell__reihe">
          <label class="vfeld vfeld--kurz"><span>PLZ *</span>
            <input type="text" name="plz" maxlength="5" inputmode="numeric"></label>
          <label class="vfeld"><span>Ort *</span>
            <input type="text" name="ort" maxlength="60"></label>
        </div>

        <p class="bestell__summe">Summe: <b id="summe">%(preisDE)s&nbsp;&euro;</b>
          <span id="summehinweis">zzgl. Versand</span></p>

        <div class="bestell__buchen">
          <label class="vfeld vfeld--menge">
            <span class="sr">Menge</span>
            <select id="menge" name="menge">
%(mengen)s
            </select>
          </label>
          <button type="submit" class="btn btn--marke btn--lg">Verbindlich bestellen</button>
        </div>

        <p class="bestell__status" id="bestellstatus" hidden></p>
        <p class="bestell__klein">Wir best&auml;tigen jede Bestellung von Hand und melden uns
          mit dem genauen Liefertermin. Druck startet, sobald der Upload geschlossen ist.</p>
      </form>
    </div>
  </div>
</section>

<section class="sec sec--dark" id="einreichen">
  <div class="wrap">
    <header class="sec__head sec__head--light">
      <p class="tag tag--light"><span class="tag__id">B</span> F&uuml;r Teilnehmer</p>
      <h2>Ihre eigene Karte gestalten</h2>
      <p class="sec__lead sec__lead--light">Sie fahren mit? Dann geh&ouml;rt Ihnen eine Karte im
        Spiel. Der Konfigurator ist seit dem %(start)s offen — Fahrzeugdaten eintragen,
        Foto ins Kartenfenster setzen, fertig.</p>
    </header>

    <div class="konf__frames">
      <div class="konf__panel is-on">
        <div class="konf__screen" data-src="%(kurl)s">
          <noscript><a href="%(kurl)s">Konfigurator %(kname)s &ouml;ffnen</a></noscript>
        </div>
      </div>
    </div>
    <div class="konf__act">
      <a class="btn btn--gelb btn--lg" href="%(kurl)s" target="_blank"
         rel="noopener">Konfigurator in eigenem Fenster</a>
      <a class="btn btn--line btn--lg" href="#bestellen">Quartett bestellen</a>
    </div>
  </div>
</section>

<section class="sec sec--eng">
  <div class="wrap">
    <p class="weiter"><a href="rallyes.html">&larr; Alle Rallye-Quartette</a>
      <a href="archiv.html">Archiv ansehen &rarr;</a></p>
  </div>
</section>
''' % dict(bild=q['bild'], alt=e('Quartettkarte ' + q['titel']), titel=e(k['name']),
           unter=e(q['unter']), jahr=e(k['jahr']), besch=e(q['text']),
           start=e(k['start']), kurl=k['url'], kname=e(k['kurz']),
           kurz=e(k['kurz']), preis=preis, preisDE=('%.2f' % preis).replace('.', ','),
           mengen=mengen, sid=sid) + fuss()


# ── Navigation in der handgepflegten Startseite nachziehen ───────────────

def startseite_nav():
    p = os.path.join(ZIEL, 'index.html')
    h = io.open(p, encoding='utf-8').read()
    nav = '\n      '.join(nav_links('index.html'))
    mob = '\n    '.join(nav_links('index.html'))
    neu, n1 = re.subn(r'(<!-- NAV:START -->).*?(<!-- NAV:END -->)',
                      '\\1\n    <nav class="nav" aria-label="Hauptnavigation">\n      '
                      + nav + '\n    </nav>\n    \\2', h, flags=re.S)
    neu, n2 = re.subn(r'(<!-- MOBNAV:START -->).*?(<!-- MOBNAV:END -->)',
                      '\\1\n  <div class="mobnav" id="mobnav" hidden>\n    '
                      + mob + '\n    <a class="btn btn--marke" href="rallyes.html">'
                      'Quartett bestellen</a>\n  </div>\n  \\2', neu, flags=re.S)
    if n1 and n2:
        io.open(p, 'w', encoding='utf-8').write(neu)
    return n1 + n2


def danke_seite():
    return kopf('Danke', 'Bestellung eingegangen.', 'rallyes.html') + \
'''
<section class="sec kopfsec">
  <div class="wrap">
    <p class="tag"><span class="tag__id">&#10003;</span> Bestellung</p>
    <h1>Danke &mdash; wir haben Ihre Bestellung</h1>
    <p class="sec__lead">Die Zahlung ist bei uns eingegangen. Sie bekommen gleich eine
      Best&auml;tigung per E-Mail. Gedruckt wird, sobald der Upload der Rallye
      geschlossen ist &mdash; danach dauert es 14&nbsp;Tage bis 4&nbsp;Wochen bis zur
      Lieferung.</p>
  </div>
</section>

<section class="sec sec--eng">
  <div class="wrap">
    <p class="bestell__status" id="sitzungsnummer" hidden></p>
    <p class="weiter"><a href="rallyes.html">&larr; Weitere Rallye-Quartette</a>
      <a href="archiv.html">Archiv ansehen &rarr;</a></p>
  </div>
</section>
''' + fuss()


if __name__ == '__main__':
    seiten = {
        'archiv.html': archiv_seite(),
        'rallyes.html': rallye_uebersicht(),
        'rallye-creme21.html': rallye_seite('creme21'),
        'rallye-adac.html': rallye_seite('adac'),
        'danke.html': danke_seite(),
    }
    for name, inhalt in seiten.items():
        io.open(os.path.join(ZIEL, name), 'w', encoding='utf-8').write(inhalt)
        print('%-22s %6d Zeichen' % (name, len(inhalt)))
    n = startseite_nav()
    print('index.html             Navigation %s' % ('ersetzt' if n == 2 else
          'NICHT ersetzt — Marker fehlen'))
