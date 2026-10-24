/* Matthews SuperCards — Startseite, ohne Abhängigkeiten */
(function () {
  'use strict';

  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var jahr = $('#jahr');
  if (jahr) jahr.textContent = new Date().getFullYear();

  /* Header-Schatten ab erstem Scroll */
  var head = $('#head');
  var onScroll = function () { head.classList.toggle('is-stuck', window.scrollY > 8); };
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  /* Mobile Navigation */
  var burger = $('#burger'), mobnav = $('#mobnav');
  if (burger && mobnav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      burger.setAttribute('aria-label', open ? 'Menü öffnen' : 'Menü schließen');
      mobnav.hidden = open;
    });
    mobnav.addEventListener('click', function (e) {
      if (!e.target.closest('a')) return;
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-label', 'Menü öffnen');
      mobnav.hidden = true;
    });
  }

  /* ── Konfiguratoren: iframe erst laden, wenn die Sektion in Sicht kommt ──
     Die Adressen stehen als data-src im HTML. Lokal sind das die PHP-Server
     aus .claude/launch.json; vor dem Livegang auf die öffentlichen URLs setzen. */
  function ladeScreen(screen) {
    if (screen.dataset.loaded) return;
    screen.dataset.loaded = '1';
    var src = screen.dataset.src;
    if (!src) return;

    var frame = document.createElement('iframe');
    frame.src = src;
    frame.loading = 'lazy';
    frame.title = 'Spielkartengenerator';
    frame.setAttribute('allow', 'clipboard-write');
    frame.referrerPolicy = 'no-referrer';

    // Wenn der Konfigurator nicht erreichbar ist, statt eines leeren
    // Rahmens einen lesbaren Hinweis mit direktem Link zeigen.
    // Gemessen rund 7 s bei den externen Generatoren — großzügig puffern,
    // damit der Hinweis nur bei echtem Ausfall erscheint.
    var timer = setTimeout(function () { nichtErreichbar(screen, src); }, 25000);
    frame.addEventListener('load', function () {
      clearTimeout(timer);
      screen.classList.add('is-ready');
    });
    frame.addEventListener('error', function () {
      clearTimeout(timer);
      nichtErreichbar(screen, src);
    });
    screen.appendChild(frame);
  }

  function nichtErreichbar(screen, src) {
    if (screen.classList.contains('is-ready')) return;
    screen.classList.add('is-down');
    screen.innerHTML = '';
    var p = document.createElement('p');
    p.className = 'konf__down';
    var b = document.createElement('b');
    b.textContent = 'Generator lädt hier gerade nicht';
    var t = document.createTextNode('Das kann an der Verbindung liegen. '
          + 'Sie können ihn auch direkt öffnen:');
    var a = document.createElement('a');
    a.className = 'btn btn--gelb';
    a.href = src; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = 'Generator öffnen';
    p.appendChild(b); p.appendChild(t); p.appendChild(a);
    screen.appendChild(p);
  }

  /* Jeder Konfigurator-Rahmen lädt, sobald er in Sicht kommt — unabhängig
     davon, ob die Seite Tabs hat (Startseite) oder nur einen (Produktseite). */
  var schirme = $$('.konf__screen');
  if (schirme.length) {
    if ('IntersectionObserver' in window) {
      var ioK = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          var panel = e.target.closest('.konf__panel');
          if (panel && panel.hidden) return;      // verdeckte Tabs später laden
          ladeScreen(e.target);
          ioK.unobserve(e.target);
        });
      }, { rootMargin: '500px 0px' });
      schirme.forEach(function (s) { ioK.observe(s); });
    } else {
      schirme.forEach(ladeScreen);
    }
  }

  var tabs = $$('.konf__tab');
  if (tabs.length) {
    var waehle = function (tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.classList.toggle('is-on', on);
        t.setAttribute('aria-selected', String(on));
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (!panel) return;
        panel.hidden = !on;
        panel.classList.toggle('is-on', on);
        if (!on) return;
        var schirm = $('.konf__screen', panel);
        ladeScreen(schirm);
        // Direktlink unter den Tabs auf den gewählten Generator setzen
        var direkt = $('#konf-direkt');
        if (direkt && schirm.dataset.src) direkt.href = schirm.dataset.src;
      });
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { waehle(tab); });
      tab.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var next = tabs[(i + d + tabs.length) % tabs.length];
        next.focus(); waehle(next);
      });
    });
  }

  /* ── Google-Bewertungen ──────────────────────────────────────────
     Im Auslieferungszustand Beispieldaten. Vor dem Livegang durch die
     Antwort der Google-Places-API ersetzen (Feld `reviews`); das Format
     unten entspricht dem, was die API liefert. Siehe README. */
  /* ════════════════════════════════════════════════════════════════
     ACHTUNG — PLATZHALTER, NICHT VERÖFFENTLICHEN

     Die folgenden Rezensionen sind erfunden und nur für den Entwurf da.
     Vor dem Livegang MÜSSEN sie durch die Antwort der Google-Places-API
     ersetzt werden (Felder: rating, user_ratings_total, reviews[]) —
     erfundene Kundenstimmen sind nach § 5 UWG abmahnfähig.
     Mit `demo: true` erscheint wieder der sichtbare Hinweiskasten.
     ════════════════════════════════════════════════════════════════ */
  var BEISPIEL = {
    demo: false,
    rating: 4.9,
    total: 27,
    reviews: [
      { author_name: 'Andreas K.', relative_time_description: 'vor 3 Wochen', rating: 5,
        text: 'Wir haben das Quartett für unsere Ausfahrt machen lassen. Die Crews '
            + 'konnten ihre Karte selbst gestalten — das war der halbe Spaß schon vor '
            + 'dem Start. Druck top, Termin gehalten.' },
      { author_name: 'Sabine R.', relative_time_description: 'vor 2 Monaten', rating: 5,
        text: 'Ich wollte ein Quartett mit den Autos meines Vaters zum Siebzigsten. '
            + 'Herr Hellwege hat sich die Zeit genommen, jedes Foto durchzugehen. '
            + 'Das Ergebnis hat ihn umgehauen.' },
      { author_name: 'Mirko T.', relative_time_description: 'vor 2 Monaten', rating: 5,
        text: 'Als Club haben wir schon zweimal nachbestellt. Die Daten liegen dort, '
            + 'man muss nichts neu erklären. Genau so soll das laufen.' },
      { author_name: 'Jens B.', relative_time_description: 'vor 4 Monaten', rating: 4,
        text: 'Sehr schöne Karten, die Schachtel ist ein echter Hingucker. Ein Stern '
            + 'Abzug nur, weil die Abstimmung über E-Mail lief und etwas gedauert hat.' },
      { author_name: 'Katrin M.', relative_time_description: 'vor 5 Monaten', rating: 5,
        text: 'Werbequartett für unsere Werkstatt — komplett in unseren Farben. '
            + 'Die Kunden nehmen es mit, das schafft kein Flyer.' },
      { author_name: 'Holger P.', relative_time_description: 'vor 7 Monaten', rating: 5,
        text: 'Zweitakt-Quartett für unsere Mofa-Runde. 32 Maschinen, jede mit eigener '
            + 'Karte. Die Qualität ist wie früher, nur besser gedruckt.' }
    ]
  };

  function sterne(n) {
    var voll = Math.round(n);
    return '★★★★★'.slice(0, voll) + '☆☆☆☆☆'.slice(0, 5 - voll);
  }

  function zeigeBewertungen(data) {
    var liste = $('[data-gsc-list]');
    if (!liste) return;

    var r = $('[data-gsc-rating]'), s = $('[data-gsc-stars]'), c = $('[data-gsc-count]');
    if (r) r.textContent = String(data.rating).replace('.', ',');
    if (s) s.textContent = sterne(data.rating);
    if (c) c.textContent = data.total;

    var hinweis = $('[data-gsc-demo]');
    if (hinweis) hinweis.hidden = !data.demo;

    liste.innerHTML = '';
    data.reviews.slice(0, 6).forEach(function (rez) {
      var el = document.createElement('article');
      el.className = 'rez';
      el.innerHTML =
        '<div class="rez__top">' +
          '<span class="rez__ava" aria-hidden="true"></span>' +
          '<span class="rez__wer"><span class="rez__name"></span>' +
          '<span class="rez__datum"></span></span>' +
          '<span class="rez__g" aria-hidden="true"><i>G</i><i>o</i><i>o</i><i>g</i><i>l</i><i>e</i></span>' +
        '</div>' +
        '<span class="stars" aria-hidden="true"></span>' +
        '<p class="rez__text"></p>';
      // Texte über textContent setzen, damit Fremdinhalte kein Markup einschleusen
      $('.rez__ava', el).textContent   = (rez.author_name || '?').trim().charAt(0).toUpperCase();
      $('.rez__name', el).textContent  = rez.author_name || '';
      $('.rez__datum', el).textContent = rez.relative_time_description || '';
      $('.stars', el).textContent      = sterne(rez.rating);
      $('.rez__text', el).textContent  = rez.text || '';
      el.setAttribute('aria-label', (rez.author_name || '') + ', ' + rez.rating + ' von 5 Sternen');
      liste.appendChild(el);
    });
  }
  zeigeBewertungen(BEISPIEL);



  /* ── Kartenvorschau: geschrieben wird unmittelbar in die Karte ────── */
  var qb = $('#qb');
  if (qb) {
    var rallyetext = $('[data-wert=rallyetext]', qb);

    /* Einzahl/Mehrzahl wie im Konfigurator */
    var pflegeRallyes = function (wert) {
      if (!rallyetext) return;
      rallyetext.textContent = (parseInt(wert, 10) === 1)
        ? 'bisher gefahrene Rallye' : 'bisher gefahrene Rallyes';
    };
    var rallyeFeld = $('[data-feld=rallyes]', qb);
    if (rallyeFeld) {
      rallyeFeld.addEventListener('input', function () { pflegeRallyes(rallyeFeld.value); });
      pflegeRallyes(rallyeFeld.value);
    }

    /* Zahlenfelder nehmen nur Ziffern an — wie die Prüfungen im Konfigurator */
    $$('input[inputmode=numeric]', qb).forEach(function (inp) {
      inp.addEventListener('input', function () {
        var nur = inp.value.replace(/\D+/g, '');
        if (nur !== inp.value) {
          var pos = inp.selectionStart - (inp.value.length - nur.length);
          inp.value = nur;
          try { inp.setSelectionRange(pos, pos); } catch (e) {}
        }
      });
    });

    /* Enter springt ins nächste Feld, statt etwas abzuschicken */
    var felder = $$('input[data-feld]', qb);
    felder.forEach(function (inp, i) {
      inp.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        var next = felder[(i + 1) % felder.length];
        next.focus(); next.select();
      });
    });

    /* Foto: bleibt im Browser, es wird nichts hochgeladen */
    var datei = $('#vbild'), photo = $('#qb-photo'),
        weg = $('#vbild-weg'), waehlen = $('#vbild-waehlen'), url = null;

    var entferne = function () {
      if (url) { URL.revokeObjectURL(url); url = null; }
      photo.innerHTML = '<span class="qb__leer">Foto wählen</span>';
      if (weg) weg.hidden = true;
      datei.value = '';
    };
    var uebernimm = function () {
      var f = datei.files && datei.files[0];
      if (!f || !/^image\//.test(f.type)) { entferne(); return; }
      if (url) URL.revokeObjectURL(url);
      url = URL.createObjectURL(f);
      photo.innerHTML = '';
      var img = new Image(); img.alt = ''; img.src = url;
      photo.appendChild(img);
      if (weg) weg.hidden = false;
    };

    if (datei) {
      datei.addEventListener('change', uebernimm);
      photo.addEventListener('click', function () { datei.click(); });
      if (waehlen) waehlen.addEventListener('click', function () { datei.click(); });
      if (weg) weg.addEventListener('click', entferne);
    }

    var leeren = $('#vleeren');
    if (leeren) {
      leeren.addEventListener('click', function () {
        felder.forEach(function (i) { i.value = ''; });
        pflegeRallyes('');
        felder[0].focus();
      });
    }
  }

  /* ── Anfrageformular ──────────────────────────────────────────────────
     Ohne Backend wird eine vorbereitete E-Mail geöffnet. Für den Livegang
     durch einen Server-Endpunkt mit Spam-Schutz ersetzen (siehe README). */
  var b2b = $('#b2bform');
  if (b2b) {
    var status = $('#b2bstatus');
    var melde = function (text, art) {
      status.textContent = text;
      status.dataset.art = art || 'ok';
      status.hidden = false;
    };
    b2b.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(b2b);
      var hole = function (k) { return String(d.get(k) || '').trim(); };
      var fehlt = ['firma', 'name', 'email'].filter(function (k) { return !hole(k); });

      if (fehlt.length) {
        melde('Bitte füllen Sie Unternehmen, Ansprechpartner und E-Mail aus.', 'fehler');
        var erstes = b2b.querySelector('[name="' + fehlt[0] + '"]');
        if (erstes) erstes.focus();
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(hole('email'))) {
        melde('Die E-Mail-Adresse sieht nicht vollständig aus.', 'fehler');
        b2b.querySelector('[name=email]').focus();
        return;
      }

      var zeilen = [
        'Unternehmen / Veranstaltung: ' + hole('firma'),
        'Ansprechpartner: ' + hole('name'),
        'E-Mail: ' + hole('email'),
        'Telefon: ' + (hole('telefon') || '—'),
        'Art des Projekts: ' + hole('art'),
        'Auflage: ' + (hole('auflage') || '—'),
        'Termin: ' + (hole('termin') || '—'),
        '', hole('nachricht') || '—'
      ].join('\n');

      location.href = 'mailto:matthias-hellwege@web.de'
        + '?subject=' + encodeURIComponent('Anfrage über die Website: ' + hole('firma'))
        + '&body=' + encodeURIComponent(zeilen);

      melde('Ihr E-Mail-Programm öffnet sich mit der fertigen Anfrage. '
          + 'Bitte dort noch auf „Senden" klicken.', 'ok');
    });
  }


  /* ── Archiv: filtern nach Konfigurator und Art ────────────────────── */
  var gitter = $('#qgrid');
  if (gitter) {
    var karten = $$('.qk2', gitter);
    var stand  = $('#filterstand');
    var leer   = $('#qleer');
    var wahl   = { konf: 'alle', art: 'alle' };

    var zeichne = function () {
      var sichtbar = 0;
      karten.forEach(function (k) {
        var passt = (wahl.konf === 'alle' || k.dataset.konf === wahl.konf) &&
                    (wahl.art  === 'alle' || k.dataset.art  === wahl.art);
        k.hidden = !passt;
        if (passt) sichtbar++;
      });
      if (stand) {
        stand.textContent = sichtbar === karten.length
          ? karten.length + ' Quartette'
          : sichtbar + ' von ' + karten.length + ' Quartetten';
      }
      if (leer) leer.hidden = sichtbar > 0;

      // Auswahl in der Adresszeile behalten, damit Links teilbar sind
      var par = new URLSearchParams();
      if (wahl.konf !== 'alle') par.set('konf', wahl.konf);
      if (wahl.art  !== 'alle') par.set('art',  wahl.art);
      var s = par.toString();
      history.replaceState(null, '', s ? '?' + s : location.pathname);
    };

    var setze = function (feld, wert) {
      if (feld === 'reset') { wahl.konf = 'alle'; wahl.art = 'alle'; }
      else wahl[feld] = wert;
      $$('.filt').forEach(function (b) {
        if (b.dataset.f === 'reset') return;
        b.classList.toggle('is-on', wahl[b.dataset.f] === b.dataset.v);
        b.setAttribute('aria-pressed', String(wahl[b.dataset.f] === b.dataset.v));
      });
      zeichne();
    };

    document.addEventListener('click', function (ev) {
      var b = ev.target.closest('.filt');
      if (!b) return;
      setze(b.dataset.f, b.dataset.v);
    });

    // Auswahl aus der Adresszeile übernehmen
    var par = new URLSearchParams(location.search);
    wahl.konf = par.get('konf') || 'alle';
    wahl.art  = par.get('art')  || 'alle';
    setze('', null);
  }

  /* ── Bestellformular ──────────────────────────────────────────────────
     Ohne Backend wird eine vorbereitete E-Mail geöffnet; für den Livegang
     durch einen Server-Endpunkt mit Bestellnummer ersetzen (siehe README). */
  var bestell = $('#bestellform');
  if (bestell) {
    // Preis steht am Formular, damit er nur an einer Stelle gepflegt wird
    var einzel  = parseFloat(bestell.dataset.preis || '0') || 0;
    var mengeF  = $('#menge');
    var summeF  = $('#summe');
    var statusF = $('#bestellstatus');

    var euro = function (n) {
      return n.toFixed(2).replace('.', ',') + '\u00A0\u20AC';
    };
    var menge = function () { return parseInt(mengeF.value, 10) || 1; };
    var rechne = function () { summeF.textContent = euro(einzel * menge()); };
    mengeF.addEventListener('change', rechne);
    rechne();

    // Zahlenfelder nehmen nur Ziffern an
    $$('input[inputmode=numeric]', bestell).forEach(function (inp) {
      inp.addEventListener('input', function () {
        var nur = inp.value.replace(/\D+/g, '');
        if (nur !== inp.value) inp.value = nur;
      });
    });

    var melde = function (text, art) {
      statusF.textContent = text;
      statusF.dataset.art = art || 'ok';
      statusF.hidden = false;
    };

    bestell.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var d = new FormData(bestell);
      var hole = function (k) { return String(d.get(k) || '').trim(); };
      var pflicht = ['name', 'email', 'strasse', 'hausnr', 'plz', 'ort'];
      var fehlt = pflicht.filter(function (k) { return !hole(k); });

      if (fehlt.length) {
        melde('Bitte Name, E-Mail und die vollständige Lieferanschrift ausfüllen.', 'fehler');
        var erstes = bestell.querySelector('[name="' + fehlt[0] + '"]');
        if (erstes) erstes.focus();
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(hole('email'))) {
        melde('Die E-Mail-Adresse sieht nicht vollständig aus.', 'fehler');
        bestell.querySelector('[name=email]').focus();
        return;
      }
      if (hole('plz').length !== 5) {
        melde('Die Postleitzahl braucht fünf Ziffern.', 'fehler');
        bestell.querySelector('[name=plz]').focus();
        return;
      }

      var knopf = bestell.querySelector('button[type=submit]');
      var beschriftung = knopf.textContent;
      knopf.disabled = true;
      knopf.textContent = 'Einen Moment …';
      melde('Zahlung wird vorbereitet …', 'ok');

      fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          artikel: bestell.dataset.artikel,
          menge:   menge(),
          name:    hole('name'),
          startnr: hole('startnr'),
          email:   hole('email'),
          zurueck: location.pathname
        })
      })
      .then(function (a) { return a.json().then(function (d) { return { ok: a.ok, d: d }; }); })
      .then(function (r) {
        if (!r.ok || !r.d.url) throw new Error(r.d.fehler || 'Unbekannter Fehler');
        location.href = r.d.url;           // weiter zu Stripe
      })
      .catch(function (e) {
        knopf.disabled = false;
        knopf.textContent = beschriftung;
        melde('Die Zahlung konnte nicht gestartet werden: ' + e.message, 'fehler');
      });
    });
  }

  var sitzung = $('#sitzungsnummer');
  if (sitzung) {
    var id = new URLSearchParams(location.search).get('sitzung');
    if (id) {
      sitzung.textContent = 'Vorgangsnummer: ' + id;
      sitzung.hidden = false;
    }
  }

  /* Einblenden beim Scrollen */
  var targets = $$('.sec__head, .prod, .konf__tabs, .konf__frames, .steps li, ' +
                   '.trumpf__copy, .tvals, .matthias__card, .matthias__copy, ' +
                   '.bew__grid, .bew__cta, .vorschau__copy, .qk2, .rk, .produkt__bild, .produkt__text, .b2b__copy, .b2b__form, .cta__in > *');
  if (reduced || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    targets.forEach(function (el) { el.classList.add('rv'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var sibs = Array.prototype.slice.call(e.target.parentElement.children);
        e.target.style.transitionDelay = (Math.min(sibs.indexOf(e.target), 5) * 75) + 'ms';
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.06 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* Aktiver Navigationspunkt */
  var links = $$('.nav a[href^="#"]');
  var sections = links.map(function (a) { return $(a.getAttribute('href')); }).filter(Boolean);
  if (sections.length && 'IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) {
          a.classList.toggle('is-cur', a.getAttribute('href') === '#' + e.target.id);
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(function (s) { spy.observe(s); });
  }
})();
