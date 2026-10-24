# Matthews SuperCards — Startseite

Designentwurf der Startseite für den neuen Onlineshop. Statisches HTML/CSS/JS
ohne Framework und ohne Build-Schritt — direkt zeigbar und später in jedes
Shopsystem portierbar.

## Woher die Gestaltung kommt

**Farben und Schriften stammen aus den bestehenden Konfiguratoren**
(`creme21-app`, `adac-app`), nicht aus einer neu erfundenen Palette. Der Shop
und die Generatoren sollen als ein Auftritt wirken, deshalb ist das
Farbsystem 1:1 übernommen — samt der Benennung:

```
--paper #EFEADA   --surface #FAF7EA   --feld #FBF7F1
--ink   #17160F   --muted   #6E6C58   --line rgba(23,22,15,.16)
--asphalt #22241F --signal  #C8341F   --tanne #0E4A2B
--marke <Markenfarbe>
```

`--marke` ist in den Konfiguratoren die Farbe der jeweiligen Rallye
(Creme 21 `#EE7C36`, ADAC `#FFCF00`). Für den Shop selbst steht dort das Rot
aus dem SuperCards-Logo, `#CD1719`; das Logo-Gelb `#FFD500` ist zweiter Akzent.
Schriften ebenfalls wie dort: Arial Black als Display, System-Stack für den
Fließtext — keine Webfonts, nichts nachzuladen.

**Aus dem Flyer** kommen die Motive und drei ergänzende Farben: das
Kartencreme `#F3E9C8`, das Navy der SuperCard-Balken `#101A3D` und das
Werkbank-Holz `#8C7A65`, das die Sektion über Matthias trägt. Das Hero-Bild
ist der Flyer selbst — die Karten so, wie sie dort auf der Werkbank liegen.

**Wiederkehrende Elemente aus den Konfiguratoren:** das Absperrband als
Trenner und die Sektionskennungen (A1, B1, C1 …) im Duktus der Quartettkarte.

## Sektionen

| Kennung | Sektion | Zweck |
|---|---|---|
| A1 | Hero | Flyer-Claim und -Motiv, Werteleiste |
| — | Auftraggeber | Laufband mit den realen Referenzen |
| B1 | Sortiment | Vier Produktwege; die Kartenmotive sind CSS-Platzhalter im Hausstil |
| B2 | Konfigurator | **Beide Generatoren live eingebettet**, umschaltbar |
| C1 | Kartenvorschau | **Live-Vorschau der Quartettkarte**, maßgetreu |
| C2 | Matthias Hellwege | Porträt über seine eigene „A1 · Ihr Ansprechpartner"-Karte |
| C3 | Bewertungen | Google-Rezensionen |
| D1 | Für Unternehmen | B2B-Sektion mit Anfrageformular (eigener Menüpunkt) |
| D | Kontakt | Abschluss-CTA |

## Die Konfiguratoren

Fünf Generatoren sind eingebunden, alle unter ihrer öffentlichen Adresse —
im Code steht kein `localhost` mehr:

| Generator | Adresse | Wo |
|---|---|---|
| Oldtimer | `oldtimer-spielkartengenerator.visionwerk.agency` | Startseite, Tab 1 |
| Rallye | `ralley-spielkartengenerator.visionwerk.agency` | Startseite, Tab 2 |
| Mofa | `mofa-spielkartengenerator.visionwerk.agency` | Startseite, Tab 3 |
| Creme 21 | `creme21-spielkartengenerator.visionwerk.agency` | `rallye-creme21.html` |
| ADAC Westfalen Classic | `adac-spielkartengenerator.visionwerk.agency` | `rallye-adac.html` |

Die drei **offenen** Generatoren stehen jedem zur Verfügung und sind auf der
Startseite eingebettet (Tabs, Klick und Pfeiltasten). Die beiden
**veranstaltungsgebundenen** stehen auf der jeweiligen Rallye-Seite.

Jeder Rahmen lädt erst, wenn man hinscrollt — bei Tabs zusätzlich erst beim
Umschalten. Die Generatoren brauchen gemessen rund 7 Sekunden bis zum
`load`-Ereignis; der Notfall-Timeout steht deshalb bei 25 Sekunden. Greift er,
erscheint statt eines leeren Rahmens ein Hinweis mit Direktlink.

Die Server setzen weder `X-Frame-Options` noch `frame-ancestors`, das Einbetten
funktioniert also. Falls das später gesperrt wird, bleibt der Direktlink unter
den Tabs als Weg.

## Telefon-Optimierung

- **Topbar** zeigt unter 800 px statt der ausgeschriebenen Nummer einen gelben
  **Anrufen**-Knopf; der Claim rückt auf zwei Zeilen.
- **Hero** stellt auf dem Telefon um: Überschrift, Text und Knöpfe zuerst, das
  Bild danach (`display:contents` plus `order`). Der Handlungsaufruf liegt damit
  über der Falz — gemessen bei 507 px auf einem 812 px hohen Fenster.
- **Feste Aktionsleiste** am unteren Rand (`#rufleiste`, unter 860 px): Anrufen
  und Quartett bestellen. Sie fährt ein, sobald die Hero-Knöpfe weggescrollt
  sind, und berücksichtigt `safe-area-inset-bottom`.
- **Drei Knöpfe am Konfigurator** stapeln unter 700 px als 1 + 2: der primäre
  über die volle Breite, die beiden sekundären nebeneinander.

## Google-Bewertungen

Die Sektion ist fertig gebaut — Gesamtnote, Sterne, Rezensionskarten —, zeigt
aber **Beispieldaten mit sichtbarem Hinweis**, solange keine Verbindung
besteht. Bewusst keine erfundenen Rezensionen: Genau das macht die alte Seite
(spielkarten.projekteverwaltung.de) mit „99 % Kundenzufriedenheit" falsch.

Die Rezensionen laufen in einem **Karussell** (`#rezkarussell`): Scroll-Snap,
Pfeile und Punkte, drei Karten nebeneinander ab 860 px, darunter eine. Die
Steuerung blendet sich aus, wenn alles gleichzeitig sichtbar ist.

Zum Anschließen in `assets/js/main.js` das Objekt `BEISPIEL` durch die Antwort
der Google-Places-API ersetzen (`rating`, `user_ratings_total`, `reviews[]`).
Die Feldnamen im Code entsprechen bereits der API. Der API-Key gehört auf den
Server, nicht ins Frontend; üblich ist ein kleiner Proxy-Endpunkt, der die
Antwort zwischenspeichert. Die API liefert maximal fünf Rezensionen je Abruf.
`data.demo = false` blendet den Hinweiskasten aus.

## Seiten

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite — von Hand gepflegt; Sektion A2 ist die Weggabelung |
| `rallyes.html` | Übersicht der Rallye-Quartette (bestellbar) |
| `rallye-creme21.html` | Produktseite Creme 21: bestellen **und** Konfigurator |
| `rallye-adac.html` | Produktseite ADAC Westfalen Classic |
| `archiv.html` | Archiv aller Quartette, filterbar |

### Erzeugen und prüfen

```bash
python3 build.py     # erzeugt alle Seiten außer index.html
python3 check.py     # tote Verweise, fehlende Bilder, alt-Texte, TODOs
python3 dev-server.py  # lokal auf http://localhost:4173 (ohne Cache)
```

`build.py` enthält die Daten aller Quartette und Konfiguratoren an einer Stelle.
Neue Rallye hinzufügen: Eintrag in `KONFIGURATOREN` und `QUARTETTE` ergänzen,
Bild nach `assets/img/q-<id>.jpg` legen, `build.py` laufen lassen — Archiv,
Übersicht, Produktseite und Filter aktualisieren sich mit.

Die Startseite bleibt handgepflegt; `build.py` tauscht dort nur den
Navigationsblock zwischen `<!-- NAV:START -->` und `<!-- NAV:END -->` aus,
damit das Menü auf allen Seiten gleich ist.

## Rallye-Quartette: zwei Wege

Jede laufende Rallye hat eine eigene Seite, die beides verbindet:

- **Bestellen** — Mengenwahl mit Live-Summe, Lieferhinweis „ca. 14 Tage".
  Gedruckt wird, sobald der Upload geschlossen ist.
- **Selbst gestalten** — der Konfigurator der Rallye ist auf derselben Seite
  eingebettet und lädt erst, wenn man dort hinscrollt.

Die Termine stammen aus den Konfiguratoren (Creme 21 ab 16.09.2026,
ADAC Westfalen Classic ab 11.10.2026).

## Archiv

Alle acht Quartette mit zwei Filterachsen: **nach Konfigurator** (Creme 21,
ADAC Westfalen Classic, ohne Konfigurator) und **nach Art** (Rallye-, Themen-,
Marken-Quartett). Die Auswahl steht in der Adresszeile, Links wie
`archiv.html?art=thema` sind also teilbar — die Startseite nutzt das bereits.
Quartette mit laufendem Konfigurator führen direkt auf ihre Produktseite.

## So läuft es ab (B2)

Statt einer nachgebauten Vorschau zeigt die Sektion **echte Aufnahmen aus dem
laufenden Generator** — vier Schritte: Generator öffnen, leere Karte, Daten
eintragen, Foto setzen und einschicken. Die Bilder liegen als
`assets/img/schritt-1..4.jpg`.

Eine frühere Fassung ließ Besucher Werte in eine nachgebaute Karte tippen. Das
ist entfallen: Es führte zu nichts — der echte Konfigurator steht direkt
darunter und kann dasselbe, nur vollständig. Wer die Schritte neu aufnehmen
will (etwa nach einer Überarbeitung des Generators), macht Screenshots bei
760 px Breite und legt sie unter denselben Namen ab.

## Für Unternehmen (D1)

Eigener Menüpunkt für Rallye-Veranstalter, Clubs und Marken — mit vier
Nutzenpunkten und einem Anfrageformular (Unternehmen, Ansprechpartner, E-Mail,
Telefon, Projektart, Auflage, Termin, Nachricht).

**Ohne Backend öffnet das Formular eine vorbereitete E-Mail** an
`matthias-hellwege@web.de`; Pflichtfelder und E-Mail-Format werden vorher im
Browser geprüft. Vor dem Livegang gehört dort ein Server-Endpunkt hin — mit
Spam-Schutz (Honeypot oder Captcha), Bestätigungsseite und einer Kopie an den
Absender. Die mailto-Lösung ist für den Entwurf gedacht, nicht für den Betrieb.

## Dateien

```
website/
├── index.html
└── assets/
    ├── css/style.css
    ├── js/main.js     (Navigation, Tabs, iframes, Bewertungen, Scroll-Einblendung)
    └── img/           (aus dem Flyer aufbereitet)
```

## Lokal ansehen

```bash
cd website && python3 -m http.server 4173
```

---

## Vor dem Livegang zu klären

Im Code als `TODO Kunde` markiert:

**Preise.** Alle vier Produkte stehen auf „auf Anfrage".

**Produktionsdaten.** Die frühere Tabelle mit Grammatur, Mindestauflage und
Produktionszeit ist entfallen — diese Werte waren ohnehin nur Annahmen. Was
jetzt noch auf der Seite steht, ist belegt: **Kartenformat 65 × 100 mm**,
**Eckradius 3,25 mm**, Linien 0,353 mm (aus `OFFENE-PUNKTE.md` und
`includes/functions.php` beider Konfiguratoren), 300 dpi im Hero sowie
32 Karten je Spiel (Schachteltext „Mofa 1A"). Sollen Auflage und Lieferzeit
doch genannt werden, brauchen wir die echten Werte.

**Formular-Endpunkte.** Unternehmensanfrage *und* Bestellformular öffnen
derzeit eine vorbereitete E-Mail. Für den Betrieb braucht es einen
Server-Endpunkt mit Spam-Schutz, Bestellnummer und Bestätigungsmail — eine
Bestellung darf nicht davon abhängen, dass jemand im Mailprogramm auf „Senden"
klickt.

**Preis.** Auf den Rallye-Seiten stehen 24,90 € je Spiel als Platzhalter
(`einzel` in `assets/js/main.js`, Anzeige in `build.py`). Dazu fehlen
Versandkosten, Staffelpreise und die Frage, ob Teilnehmer einen anderen Preis
zahlen als Sammler.

**Rechtliches für den Verkauf.** Mit echten Bestellungen werden Widerrufs-
belehrung, AGB, Versand- und Zahlungsangaben sowie eine Datenschutzerklärung
zur Pflicht; außerdem eine Zahlungsart (derzeit ist nur „auf Rechnung nach
Bestätigung" impliziert).

**Adresse.** Der Flyer nennt Hauptstraße 58, Oldenburg — die PLZ fehlt.

**Telefon.** `0441 / 2332252` stammt von der Ansprechpartner-Karte des Flyers.

**Text über Matthias.** Die Sektion ist aus dem vorhandenen Material
geschrieben. Bitte von ihm gegenlesen lassen — besonders, seit wann es die
Quartette gibt; im Hero steht „seit über 20 Jahren", das ist noch unbelegt.

**Produktmotive.** Die vier Karten im Sortiment sind CSS-Platzhalter im
Hausstil und sollten durch freigegebene Produktfotos ersetzt werden.

**Rechtstexte.** Impressum, Datenschutz, AGB, Widerruf, Versand/Zahlung sind
verlinkt, aber noch nicht verfasst.

## Nächster Schritt

Nach Freigabe der Startseite steht die Entscheidung über das Shopsystem an.
Die beiden Konfiguratoren bleiben in jedem Fall eigenständige PHP-Anwendungen
und werden eingebettet, nicht neu gebaut.
