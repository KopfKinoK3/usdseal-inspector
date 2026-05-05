# Roadmap v0.25.3 — EN-Toggle-Hotfix

**Status:** ✅ **COMPLETED 2026-05-04** · Commit `fe5fa87`, Tag `v0.25.3` online
**Story-Slot:** *"Polyglot wirklich"* — bekannter Bug-Fix
**Ziel:** Sprach-Toggle DE↔EN funktioniert browser-übergreifend. ✓ erreicht.
**Aufwand:** 0.25–0.5 Tag konzentrierter Build (Hotfix). ✓ eingehalten.

> Patch-Sprint. Master-Übersicht in `../ROADMAP.md`.
> **Sequenz-Hinweis:** Ursprünglich als v0.25.1 geplant. Nach v0.25.2-Release umnummeriert auf v0.25.3, damit die Reihenfolge optisch konsistent bleibt (kein "v0.25.1 nach v0.25.2").

## Release-Befund 2026-05-04

| Phase | Status | Ergebnis |
|---|---|---|
| 5.0 Diagnose | ✅ | **Hypothese E** mit Sub-Variante "statische HTML-Elemente nicht per `t()` angeschlossen" — I18N-Map war vollständig, aber Buttons/Headlines/Banner-Texte lasen die Werte nie ab |
| 5.1 Fix | ✅ | 5 I18N-Keys + 5 DOM-IDs + 5 `t()`-Calls, ~15 Zeilen Code |
| 5.2 Browser-Verifikation | ✅ | Chrome (Code-Chat) + Safari (Duke live-Test) — DE→EN→DE Round-Trip sauber, kein JS-Fehler |
| 5.3 Headless-Pool | ✅ | 7/7 PASS |
| 5.4 CHANGELOG | ✅ | v0.25.3-Eintrag mit Hypothese-E-Befund |
| 5.5 ADR-27 | ✅ | In `CLAUDE-Inspector-private.md` dokumentiert (nicht ADR-26 wie im Decision-Log-Template — ADR-26 war schon durch v0.25.2-QR-Rollback vergeben) |
| 5.6 Snapshot + Tag | ✅ | `v0.25.3-snapshot.html` + Tag `v0.25.3` (Commit `fe5fa87`) |

**Lerneffekt:** Hypothese E aus dem Briefing-Katalog hatte den Sub-Pfad "statische HTML-Elemente nicht per t() angeschlossen" nicht explizit. Echte Welt war zwischen E (Map-Lücken) und einer neuen Variante: I18N-Map vollständig, aber Konsumenten-Pfad nicht verdrahtet. Phase 5.0 hat den Befund sauber rausgeholt — ADR-PC4 Verification-before-Hypothesis hält ein viertes Mal.

---

## 1. Befund

User-Report 2026-05-04: Sprach-Toggle EN funktioniert nicht — weder auf Safari noch auf Chrome. Klick auf EN-Button löst sichtbar nichts aus, auch nach Hard-Reload bleibt UI auf Deutsch. Browser-übergreifend, also kein Cache-Problem.

**Plan-Chat-Hypothesen** (Phase 5.0 verifiziert):

- **A)** Click-Handler bindet nicht: `getElementById('lang-btn-de'/'lang-btn-en')` returnt null, `setupLangToggle()` returnt early ohne Listener
- **B)** Click-Handler bindet, aber `localStorage.setItem()` schlägt silent fehl (Privacy-Mode? Quota?)
- **C)** localStorage wird gesetzt, aber `location.reload()` wird nicht ausgeführt oder rehydriert aus Page-Cache (Safari-Page-Cache-Eigenheit)
- **D)** localStorage gesetzt, Reload OK, aber CURRENT_LANG-IIFE liest nicht 'en' (return-Logik defekt)
- **E)** CURRENT_LANG ist 'en', aber `t()`-Aufrufe greifen auf alte Map-Werte oder `I18N`-Map hat unvollständige EN-Strings

---

## 2. Phase 5.0 — Diagnose vor Fix (ADR-PC4 strikt)

**Pflicht vor jedem Code-Change.** Code-Chat soll als **erste Aktion** Browser-Console-Befehle gegen den Live-Inspector laufen lassen, um zu identifizieren wo der Toggle klemmt.

### Diagnose-Ablauf

**Schritt 1 — Buttons im DOM?**
```javascript
console.log('DE:', document.getElementById('lang-btn-de'));
console.log('EN:', document.getElementById('lang-btn-en'));
```
→ Beide sollten `<button>`-Elemente zeigen.

**Schritt 2 — localStorage-Vorzustand?**
```javascript
localStorage.getItem('usdseal-inspector.lang')
```

**Schritt 3 — Manueller Toggle-Test**
```javascript
localStorage.setItem('usdseal-inspector.lang', 'en');
location.reload();
```
- Wenn UI nach Reload auf EN: **Hypothese A oder B bestätigt** — Click-Handler oder Setter klemmt
- Wenn UI auf DE bleibt: **Hypothese D oder E bestätigt** — Reader oder I18N-Map klemmt

**Schritt 4 — wenn Schritt 3 nichts ändert: I18N-Map-Vollständigkeit**
```javascript
// Anzahl Keys mit DE-Text vs. EN-Text
const i18n = window.I18N || {}; // falls global expose'd; sonst über Source-Tracking
Object.keys(i18n).filter(k => !i18n[k].en).length
// → wenn > 0: Map hat EN-Lücken
```

### Befund-basierte Fix-Strategie

| Befund | Fix |
|---|---|
| A) Buttons null | DOM-IDs prüfen, ggf. Tipfehler in `index.html` korrigieren |
| B) Setter schlägt fehl | try/catch um setItem, Fallback auf sessionStorage oder cookie. Console-Warnung. |
| C) Reload rehydriert | `location.replace(location.href)` statt `reload()` — umgeht Safari-Page-Cache |
| D) Reader-Logik defekt | CURRENT_LANG-IIFE überprüfen, Fall-Through in return-Statement |
| E) I18N-Map-Lücken | Map auf Vollständigkeit auditen, fehlende EN-Keys nachtragen |

---

## 3. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Hotfix, kein Feature |

---

## 4. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.2 stabil released | ✓ Tag online seit 2026-05-04, Commit ff8e208 |
| 2 | Bug-Reproduktion bestätigt (Safari + Chrome) | ✓ User-Report |
| 3 | Phase 5.0-Diagnose-Plan steht | ✓ siehe §2 |

**3 von 3 grün.**

---

## 5. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.1 Tag | Browser-Console-Befehle, Hypothese identifizieren |
| **5.1 Fix anwenden** | 0.1–0.25 Tag | Je nach Befund: 1–10 Zeilen Code |
| **5.2 Verifikation Browser** | 0.05 Tag | Toggle DE→EN→DE Round-Trip auf Safari + Chrome |
| **5.3 Headless-Pool-Regression** | 0.05 Tag | 7/7 PASS bleibt (Toggle ist UI-Feature, kein Validator-Impact) |
| **5.4 README + CHANGELOG** | 0.1 Tag | v0.25.3-Hotfix-Eintrag mit Befund-Dokumentation |
| **5.5 Snapshot + Tag** | 0.1 Tag | Snapshot v0.25.3, Tag, Push |

**Total: 0.5 Tag konzentrierter Hotfix.**

---

## 6. Strategischer Hebel

v0.25.3 ist Hotfix — kein Story-Release. Aber zwei stille Hebel:

1. **Trust-Anker:** v0.22.1 hat den EN-Pfad versprochen, v0.25.3 macht ihn endlich stabil. Englischsprachige Konferenz-Besucher (AOUSD-Forum-Reichweite) sehen ein funktionierendes Tool.
2. **Diagnose-Disziplin:** Phase 5.0 ist Pflicht. ADR-PC4 wird ein viertes Mal in der Praxis bewährt — diesmal für einen lange offenen Bug, den wir erst jetzt strukturiert ansprechen.

---

## 7. Konkrete Pre-v0.25.3-Steps

Keine — Hotfix-Sprint, alle Vorbedingungen aus dem User-Report erfüllt.

---

## 8. Decision-Log-Template

**Hinweis Nummerierung:** Decision-Log-Template hatte ursprünglich ADR-26 als Platzhalter. ADR-26 ist aber durch v0.25.2 (QR-Rollback) bereits vergeben. EN-Toggle-Fix ist daher **ADR-27**.

```markdown
### ADR-27 EN-Toggle-Befund — 2026-05-04

**Kontext:** EN-Toggle klickte sichtbar, aber UI blieb auf DE nach Reload. Browser-übergreifend (Safari + Chrome).

**Diagnose-Befund (aus Phase 5.0):**
- Hypothese E bestätigt mit Sub-Variante: I18N-Map war vollständig (DE+EN für alle Keys vorhanden), aber statische HTML-Elemente waren nicht per `t()`-Funktion an die Map angeschlossen — d. h. Buttons/Headlines/Banner-Texte lasen die Werte nie ab.
- Konkret: 5 statische Elemente in `index.html` ohne `data-i18n`-Attribut bzw. ohne `t()`-Call beim Sprachwechsel.

**Entscheidung:** 5 I18N-Keys ergänzen + 5 DOM-IDs vergeben + 5 `t()`-Calls in der `applyLanguage()`-Funktion nachziehen.

**Konsequenz:** EN-Toggle funktioniert browser-übergreifend. Englisch-sprechende AOUSD-Forum-Besucher sehen ab v0.25.3 einen funktionierenden Inspector. Kein Architektur-Anker berührt.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.22.1.md` (EN-Pfad ursprünglich angekündigt mit ADR-7)
- Vorgänger-Patch: `ROADMAP-v0.25.2.md` (QR-Pivot, ADR-PC5)

### Externe Specs

- [MDN — localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN — location.reload() vs location.replace()](https://developer.mozilla.org/en-US/docs/Web/API/Location)

---

**Ende v0.25.3-Roadmap.** Nach Hotfix: Snapshot, Tag `v0.25.3`, Push. Plan-Chat schreibt dann `docs/ROADMAP-v0.25.4.md` (Texture-Format-Coverage AVIF/HEIC/KTX2/TIFF/ASTC) und `docs/ROADMAP-v0.25.5.md` (Severity-Recalibration mit Test-Pool von Duke).
