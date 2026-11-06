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

# Preise in Euro (brutto). TODO Kunde: für ADAC bestätigen.
PREIS       = {'creme21': 29.40, 'adac': 29.40}
# Aufsteller mit personalisierter Karte — als Zusatz wählbar
PREIS_AUFST = {'creme21':  7.90, 'adac':  7.90}
# Derselbe Aufsteller einzeln, ohne Quartett
PREIS_AUFST_SOLO = 7.90
# Die Spielkarte selbst — neben dem Schuber auf der Produktseite
KARTE       = {'creme21': 'karte-creme21.png', 'adac': 'q-adac.jpg'}

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
    ('rallyes.html',            'Rallyequartetts'),
    # Auf Kundenwunsch vorerst ausgeblendet:
    # ('index.html#konfigurator', 'Konfigurator'),
    # ('index.html#unternehmen',  'Unternehmen'),
]

TEL_ANZEIGE = '0441 / 23 32 252'
TEL_LINK    = '+494412332252'
MAIL        = 'matthias-hellwege@web.de'


def e(s):
    return html.escape(str(s), quote=False)


# ── Bausteine ────────────────────────────────────────────────────────────

NAV_ICON = (
    '<svg class="navkarten" viewBox="0 0 26 22" width="22" height="19" aria-hidden="true">'
    '<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">'
    '<rect x="3.2" y="5.4" width="9.6" height="14.2" rx="1.6" transform="rotate(-22 8 12.5)"/>'
    '<rect x="8.4" y="3.2" width="9.6" height="14.6" rx="1.6" transform="rotate(-9 13.2 10.5)"/>'
    '<rect x="14.6" y="2.2" width="9.6" height="14.8" rx="1.6"/>'
    '</g></svg>')


def nav_links(aktiv, praefix=''):
    aus = []
    for ziel, text in NAV:
        z = ziel if not ziel.startswith('index.html') or praefix else ziel
        cls = ' is-cur' if ziel.split('#')[0] == aktiv else ''
        # Die Rallye-Spiele bekommen den Kartenfächer davor
        icon = NAV_ICON if text == 'Rallyequartetts' else ''
        aus.append('<a href="' + z + '" class="navlink' + cls + '">'
                   + icon + e(text) + '</a>')
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

<header class="head" id="head">
  <div class="wrap head__in">
    <a class="head__logo" href="index.html" aria-label="Matthews SuperCards — Startseite">
      <img src="assets/img/logo.png" alt="Matthews SuperCards" width="504" height="101">
    </a>
    <span class="head__claim">Spielkartenmanufaktur&nbsp;Oldenburg</span>
    <!-- NAV:START -->
    <nav class="nav" aria-label="Hauptnavigation">
      %(nav)s
    </nav>
    <!-- NAV:END -->
    <button class="burger" id="burger" aria-expanded="false" aria-controls="mobnav" aria-label="Men&uuml; &ouml;ffnen">
      <span></span><span></span><span></span>
    </button>
  </div>
  <!-- MOBNAV:START -->
  <div class="mobnav" id="mobnav" hidden>
    %(mobnav)s
  </div>
  <!-- MOBNAV:END -->
</header>

<main id="inhalt">
''' % dict(titel=e(titel), besch=e(beschreibung), fav=favicon_pfad,
           nav='\n      '.join(links), mobnav='\n    '.join(links),
           tell=TEL_LINK, tela=TEL_ANZEIGE)


def fuss(stripe=False):
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
      <a href="impressum.html">Impressum</a><a href="datenschutz.html">Datenschutz</a><a href="agb.html">AGB</a><a href="widerruf.html">Widerruf</a><a href="versand.html">Versand &amp; Zahlung</a>
    </nav>
  </div>
</footer>

%(stripejs)s<script src="assets/js/main.js"></script>
</body>
</html>
''' % dict(tell=TEL_LINK, tela=TEL_ANZEIGE, mail=MAIL,
           stripejs=('<script src="https://js.stripe.com/v3/"></script>\n'
                     if stripe else ''))


# ── Archiv ───────────────────────────────────────────────────────────────

def direkt(url):
    """Adresse, die die Startseite des Konfigurators überspringt."""
    return url + ('&' if '?' in url else '?') + 'direkt=1'


def bau_ziel(q, k):
    """Konfigurator, in dem sich zu diesem Archiveintrag eine Karte bauen lässt."""
    if k:
        return k['url']
    gid = 'mofa' if q['id'] == 'mofa1a' else (
        'rallye' if q['art'] == 'rallye' else 'oldtimer')
    return next(g['url'] for g in GENERATOREN if g['id'] == gid)


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
        # Zu jedem Eintrag im Archiv lässt sich eine Karte bauen: zur Rallye im
        # eigenen Konfigurator, sonst im passenden offenen Generator.
        aktion += ('\n            <a class="qk2__link qk2__link--bauen" href="%s"'
                   ' target="_blank" rel="noopener">Karte erstellen</a>'
                   % direkt(bau_ziel(q, k)))
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
    <p class="tag">Kartenarchiv</p>
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
      <a class="btn btn--line btn--lg" href="rallyes.html">Rallye-Quartette ansehen</a>
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
        # Auf Kundenwunsch zeigt die Liste vorerst nur laufende Rallyes
        # mit offener Bestellung — die übrigen stehen im Archiv.
        if q['art'] != 'rallye' or not q.get('bestellbar'):
            continue
        if q['konf'] != 'creme21':
            continue
        k = KONFIGURATOREN.get(q['konf'])
        if k and q['bestellbar']:
            stand = ''
            akt = ('<div class="rk__act">'
                   '<a class="btn btn--marke" href="rallye-%s.html#bestellen">'
                   'Quartett bestellen</a>'
                   '<a class="btn btn--grau" href="%s" target="_blank" rel="noopener">'
                   'Spielkarte einreichen</a></div>'
                   % (q['konf'], direkt(KONFIGURATOREN[q['konf']]['url'])))
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
    <p class="tag">Rallye&nbsp;Quartettspiele</p>
    <h1>Mitfahren und mitspielen</h1>
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



# Werbetext der Produktseite, je Rallye. Fehlt ein Eintrag, steht der
# sachliche Standardtext in rallye_seite().
# TODO Kunde: Sammelbestellschluss eintragen (steht unten als [Datum]).
WERBETEXT = {
    'creme21': dict(
        lead='Was f&uuml;r eine genial schrillsch&ouml;ne Zeit auf der Stra&szlig;e! Die '
             'Kilometer sind gefahren, der Staub der Rallye hat sich gelegt, aber die '
             'Erinnerungen an die diesj&auml;hrige Creme 21 Youngtimer Rallye bleiben '
             'unvergesslich.',
        absatz='Ihr habt w&auml;hrend der Rallye online die Spielkarte f&uuml;r euren '
               'Klassiker erstellt &mdash; und jetzt bringen wir das Ganze auf den '
               'K&uuml;chentisch! Holt euch das Creme 21 Jubil&auml;umsquartett mit den '
               'echten Autos eurer Mitstreiter!',
        punkte=[
            ('Euer Auto mittendrin', 'Eure Youngtimer als stolze Quartettkarte.'),
            ('Das handgefertigte Einzelst&uuml;ck',
             'Gedruckt in bester Qualit&auml;t als bleibende Erinnerung.'),
            ('Das ultimative Treffen nach dem Treffen',
             'Wer schl&auml;gt wen beim Hubraum, bei den PS oder dem Baujahr?'),
        ],
        schluss='Schwelgt in Erinnerungen und stecht eure Rallye-Kollegen beim '
                'n&auml;chsten Spieleabend aus!',
        gruss='Mit motorsportlichen (und herrlich orangenen) Gr&uuml;&szlig;en,<br>'
              'das Team von Matthews SuperCards',
        aufsteller_titel='Das Highlight f&uuml;r den Schreibtisch',
        aufsteller='Damit der eigene Klassiker nicht im Kartendeck verschwindet, '
                   'k&ouml;nnt ihr eure pers&ouml;nliche Spielkarte auch als hochwertigen '
                   'Aufsteller f&uuml;r nur %(aufstDE)s&nbsp;&euro; dazubestellen! Ob im '
                   'B&uuml;ro, in der Garage oder im Wohnzimmer &mdash; so habt ihr das '
                   'Prachtst&uuml;ck immer perfekt im Blick und holt die sch&ouml;nsten '
                   'Rallye-Momente jeden Tag aufs Neue zur&uuml;ck in den Alltag.',
        frist='Da es sich um eine exklusive Sonderanfertigung f&uuml;r uns Mitfahrer '
              'handelt, sammeln wir die Bestellungen bis zum [Datum]. Danach geht euer '
              'Spiel in den Druck und wird versandt.',
    ),
}

# ── Produktseite je Rallye ───────────────────────────────────────────────

def werbeblock(sid, aufst):
    """Werbetext der Rallye; ohne eigenen Text der sachliche Standard."""
    t = WERBETEXT.get(sid)
    aufstDE = ('%.2f' % aufst).replace('.', ',')
    if not t:
        return ('<p class="sec__lead">Hier bestellt ihr euer eigenes Spiel. Das '
                'f&uuml;r euch angefertigte Einzelst&uuml;ck, im passenden Schuber '
                'mit eurer pers&ouml;nlichen Spielkarte als Aussteller dabei.</p>')

    punkte = '\n'.join(
        '        <li><b>%s:</b> %s</li>' % (kopfz, text)
        for kopfz, text in t['punkte'])

    return ('<p class="sec__lead">%(lead)s</p>\n'
            '      <p class="werb__abs">%(absatz)s</p>\n'
            '      <ul class="werb__punkte">\n%(punkte)s\n      </ul>\n'
            '      <p class="werb__abs">%(schluss)s</p>\n'
            '      <p class="werb__gruss">%(gruss)s</p>\n'
            '      <div class="werb__kasten">\n'
            '        <h2 class="werb__kh">%(atitel)s</h2>\n'
            '        <p>%(auf)s</p>\n'
            '      </div>\n'
            '      <p class="werb__frist"><b>Hinweis:</b> %(frist)s</p>'
            % dict(lead=t['lead'], absatz=t['absatz'], punkte=punkte,
                   schluss=t['schluss'], gruss=t['gruss'],
                   atitel=t['aufsteller_titel'],
                   auf=t['aufsteller'] % dict(aufstDE=aufstDE),
                   frist=t['frist']))


def rallye_seite(sid):
    k = KONFIGURATOREN[sid]
    q = next(x for x in QUARTETTE if x['konf'] == sid)
    preis   = PREIS.get(sid, 34.80)
    karte   = KARTE.get(sid, q['bild'])
    aufst   = PREIS_AUFST.get(sid, 7.90)
    solo    = PREIS_AUFST_SOLO
    werbung = werbeblock(sid, aufst)
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

    <div class="pkar" id="pkar">
      <div class="pkar__spur" id="pkarspur">
        <figure class="pkar__bild">
          <img src="assets/img/%(bild)s" alt="%(alt)s" width="560" height="850">
          <figcaption>Euer Schuber</figcaption>
        </figure>
        <figure class="pkar__bild pkar__bild--karte">
          <img src="assets/img/%(karte)s" alt="Spielkarte der %(kurz)s"
               width="560" height="851" loading="lazy">
          <figcaption>Eure Spielkarte</figcaption>
        </figure>
      </div>
      <button type="button" class="pkar__pfeil pkar__pfeil--zur" id="pkarzur"
              aria-label="Vorheriges Bild">&larr;</button>
      <button type="button" class="pkar__pfeil pkar__pfeil--vor" id="pkarvor"
              aria-label="N&auml;chstes Bild">&rarr;</button>
      <div class="pkar__punkte" id="pkarpunkte" role="tablist"
           aria-label="Bilder"></div>
    </div>

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
      %(werbung)s

      <form class="bestell" id="bestellform" data-preis="%(preis).2f"
            data-aufsteller="%(aufst).2f" data-solo="%(solo).2f" data-artikel="%(sid)s">
        <div class="bestell__preis">
          <span class="bestell__ab" id="preistitel">Quartett im Schuber</span>
          <b class="bestell__zahl" id="preis">%(preisDE)s&nbsp;&euro;</b>
          <span class="bestell__hinweis">zzgl. Versand</span>
        </div>

        <div class="wahl" id="produktwahl">
          <label class="wahl__o">
            <input type="radio" name="produkt" value="quartett" checked>
            <span class="wahl__t"><b>Quartett im Schuber</b>
              <i>Das komplette Spiel mit eurer Karte darin</i></span>
            <span class="wahl__p">%(preisDE)s&nbsp;&euro;</span>
          </label>
          <label class="zusatz" id="zusatzblock">
            <input type="checkbox" id="aufsteller" name="aufsteller" value="1">
            <span class="zusatz__text">
              <b>&hellip; und Aufsteller mit eurer pers&ouml;nlichen Karte</b>
              <span>Eure Spielkarte zum Hinstellen &mdash; als Erinnerung an die Ausfahrt.</span>
            </span>
            <span class="zusatz__preis">+&nbsp;%(aufstDE)s&nbsp;&euro;</span>
          </label>
          <label class="wahl__o">
            <input type="radio" name="produkt" value="aufsteller">
            <span class="wahl__t"><b>Nur Aufsteller</b>
              <i>Eure pers&ouml;nliche Karte zum Hinstellen, ohne Spiel</i></span>
            <span class="wahl__p">%(soloDE)s&nbsp;&euro;</span>
          </label>
        </div>

        <div class="bestell__reihe">
          <label class="vfeld">
            <span>Eure E-Mail-Adresse *</span>
            <input type="text" name="email" maxlength="80" inputmode="email">
          </label>
        </div>
        <div class="bestell__reihe">
          <label class="vfeld">
            <span>Fahrer Nachname *</span>
            <input type="text" name="name" maxlength="60" placeholder="Nachname">
          </label>
          <label class="vfeld vfeld--kurz">
            <span>Start-Nr.</span>
            <input type="text" name="startnr" maxlength="3" inputmode="numeric" placeholder="221">
          </label>
        </div>
        <p class="bestell__klein bestell__klein--oben">Die Lieferanschrift fragen wir im
          n&auml;chsten Schritt bei der Zahlung ab.</p>

        <p class="bestell__summe">Summe: <b id="summe">%(preisDE)s&nbsp;&euro;</b>
          <span id="summehinweis">zzgl. Versand</span></p>

        <div class="bestell__buchen">
          <label class="vfeld vfeld--menge">
            <span class="sr">Menge</span>
            <select id="menge" name="menge">
%(mengen)s
            </select>
          </label>
          <button type="button" class="btn btn--marke btn--lg" id="weiter">Weiter</button>
        </div>

        <!-- Vorschau: erscheint nach "Weiter" -->
        <div class="vorschau2" id="vorschau2" hidden>
          <p class="vorschau2__titel">So wird euer Spiel</p>
          <div class="vorschau2__karten">
            <figure id="vs-schuber">
              <img src="assets/img/%(bild)s" alt="Schuber">
              <figcaption>Quartett im Schuber</figcaption>
            </figure>
            <figure class="vorschau2__pers" id="vs-pers">
              <img src="assets/img/%(karte)s" alt="Eure Spielkarte">
              <span class="vorschau2__band"><b id="vs-nr">&mdash;</b><i id="vs-name">Nachname</i></span>
              <figcaption>Eure pers&ouml;nliche Karte</figcaption>
            </figure>
            <figure id="vs-aufsteller" hidden>
              <img src="assets/img/%(karte)s" alt="Aufsteller">
              <figcaption>Aufsteller</figcaption>
            </figure>
          </div>
          <p class="vorschau2__summe">Gesamt: <b id="vs-summe">&mdash;</b> <span>zzgl. Versand</span></p>
          <div class="vorschau2__act">
            <button type="button" class="btn btn--ghost" id="zurueck2">&larr; &Auml;ndern</button>
            <button type="submit" class="btn btn--marke btn--lg">Verbindlich bestellen</button>
          </div>
        </div>

        <!-- Zahlungsblock von Stripe, eingebettet auf dieser Seite -->
        <div class="zahlung" id="zahlung" hidden>
          <div class="zahlung__kopf">
            <button type="button" class="btn btn--ghost" id="zurueck3">&larr; Zur&uuml;ck</button>
            <span>Zahlung</span>
          </div>
          <div id="stripe-block"></div>
        </div>

        <p class="bestell__status" id="bestellstatus" hidden></p>
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
      <a class="btn btn--gelb btn--lg" href="%(kurld)s" target="_blank"
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
''' % dict(werbung=werbung, solo=solo,
           soloDE=('%.2f' % solo).replace('.', ','),
           bild=q['bild'], alt=e('Quartettkarte ' + q['titel']), titel=e(k['name']),
           unter=e(q['unter']), jahr=e(k['jahr']), besch=e(q['text']),
           start=e(k['start']), kurl=k['url'], kurld=direkt(k['url']), kname=e(k['kurz']),
           kurz=e(k['kurz']), preis=preis, preisDE=('%.2f' % preis).replace('.', ','),
           mengen=mengen, sid=sid,
           aufst=aufst, aufstDE=('%.2f' % aufst).replace('.', ','),
           karte=karte) + fuss(stripe=True)


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
