# Roadmap v0.25.4.1 — UX-Polish-Patch

**Status:** ✅ **COMPLETED 2026-05-05** · Commit `03799f0`, Tag `v0.25.4.1` online
**Story-Slot:** *"Drei Mini-Bugs aus dem Real-World-Sweep aufräumen"*
**Ziel:** Drei UX-Befunde fixen. ✓ erreicht.
**Aufwand:** 0.3–0.5 Tag. ✓ eingehalten.

## Release-Befund 2026-05-05

| Bug | Status | Lösung |
|---|---|---|
| 1 — PDF-Header `v0.25` hardcoded | ✅ | `INSPECTOR_VERSION` dynamisch aus Versions-Badge gezogen |
| 2 — Safari-PDF öffnet HTML-Tab | ✅ | **Variante A** (Anchor-Click-Pattern) hat Cross-Browser funktioniert — Variante B als ungenutzter Fallback im Briefing |
| 3 — Cache-Tooltip irreführend | ✅ | i18n DE+EN präzisiert: "Manifest-IDs aus signierten USDZs" |
| Headless-Pool | ✅ | 13/13 PASS (DIEGOsat_TK_280426_01-Erwartung nachgetragen) |
| ADR-30 | ✅ | In CLAUDE-Inspector-private.md dokumentiert |

**Live-Verifikation:** Duke hat in Safari + Chrome alle 4 Tests bestätigt — Direct-Download funktioniert in beiden Browsern, PDF-Header zeigt `v0.25.4.1`, Cache-Tooltip präziser.



> Mini-Patch nach v0.25.4. Master-Übersicht in `../ROADMAP.md`.

---

## 1. Befund

Aus dem Real-World-Test-Sweep 2026-05-05 (Quelle: `../tests/real-world-2026-05-05.md`) sind drei UX-Befunde übrig geblieben, die nicht in v0.25.4 reinpassten (dort Severity + AVIF):

| # | Bug | Severity | Effekt |
|---|---|---|---|
| 1 | PDF-Header zeigt `v0.25` statt aktueller Version | low | Alle 6 Real-World-Reports zeigen "Inspector v0.25" obwohl auf v0.25.3 (und nach v0.25.4 erst recht). PDF-Audit-Tauglichkeit leidet. |
| 2 | Safari-PDF-Button öffnet HTML-Tab statt Direct-Download | **medium** | Safari-User kriegen kaputten Workflow. Beim ersten Versuch sieht User nur Embed-Vorschau (Page 1), denkt PDF wäre unvollständig. |
| 3 | Cache-Counter zählt nur Manifest-IDs — auf leeren/unsignierten Sessions verwirrend | low | Counter zeigt 1, obwohl 6 Files reingeworfen wurden — User-Verwirrung |

---

## 2. Phase 5.0 — Diagnose

Phase 5.0 ist im Sweep durchgespielt. Ergänzende Code-Inspection für jeden Punkt:

### Bug 1: PDF-Header

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "v0.25\|Inspector v" index.html | head -10
```

→ Findet die Stelle wo `"USDseal Inspector v0.25"` als String hardcoded im jsPDF-Header-Aufruf steht. Sollte dynamisch aus dem Versions-Badge gezogen werden:

```javascript
const version = document.querySelector('.version-badge').textContent.trim();
// dann an jsPDF: doc.text(`USDseal Inspector ${version}`, ...)
```

### Bug 2: Safari-PDF-Download

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "doc.save\|doc.output" index.html | head -10
```

→ Findet die jsPDF-Output-Methode. Vermutlich `doc.save("filename.pdf")`. Chrome triggert das als Download, Safari öffnet als data-URL-Tab.

**Fix-Versuch A (sauber, Cross-Browser):**

```javascript
// statt doc.save("filename.pdf"):
const pdfBlob = doc.output("blob");
const blobUrl = URL.createObjectURL(pdfBlob);
const a = document.createElement("a");
a.href = blobUrl;
a.download = filename;
document.body.appendChild(a);
a.click();        // muss synchron zum User-Click sein!
a.remove();
URL.revokeObjectURL(blobUrl);
```

Der Click muss **synchron im Click-Handler** ausgelöst werden — nicht in einer async-Callback. Sonst blockiert Safari mangels User-Activation.

**Fix-Fallback B (Browser-Weiche, falls A nicht funktioniert):**

```javascript
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
if (isSafari) {
  // Button-Text "HTML-Report ↓"
  // Hinweis im Output: "Sichere als PDF via Drucken-Funktion (Cmd+P → Als PDF speichern)"
} else {
  // Direct-Download wie Chrome
}
```

→ Phase 5.1: erst A versuchen. Wenn das Cross-Browser sauber läuft → fertig. Wenn Safari trotz Anchor-Click weiter Tab öffnet → B als Fallback dokumentieren.

### Bug 3: Cache-Counter-UX

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "cache-clear-btn\|cache-count\|usdseal-inspector.cache" index.html | head -10
```

→ Aktueller Tooltip: "Lokal gespeicherte Manifest-Spuren löschen". Gut, aber der **Button-Text** sagt nur "Cache (N)" — nicht klar dass es Manifest-IDs zählt.

**Fix-Vorschlag:**
- Button-Text: "Spuren (N)" oder "Sealed (N)" — klarer was es zählt
- ODER: Tooltip-Text in den Button selbst zeigen wenn Hover (i18n-Anpassung)
- ODER: einfach Tooltip ausführlicher: "Manifest-Hashes aus früher gesehenen signierten USDZs"

Plan-Chat-Empfehlung: minimaler Eingriff = nur Tooltip präzisieren, Button-Text "Cache" lassen (vertraut). Kein Verhaltens-Change.

---

## 3. Scope

### 3.1 Was rein kommt

- **Bug 1 Fix:** PDF-Header dynamisch aus Versions-Badge ziehen, Footer auch ("Page X of Y | filename | Inspector v0.25.4.1" o.ä.)
- **Bug 2 Fix Variante A:** Anchor-Click-Pattern für Cross-Browser-Download, **synchron** im Click-Handler
- **Bug 2 Fix Variante B:** Browser-Weiche als Fallback (nur falls A nicht klappt — Code-Chat entscheidet nach Live-Test)
- **Bug 3 Fix:** Tooltip präzisieren (DE+EN i18n), Button-Text bleibt

### 3.2 Was bleibt unverändert

- jsPDF-Inhalt (Findings-Layout, Layout-Logik aus v0.23)
- Cache-Verhalten selbst (nur Beschriftung)
- Versions-Badge-HTML

---

## 4. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose-Lesen** | 0.05 Tag | Sweep-Log + Code-Inspection |
| **5.1 PDF-Header dynamisch** | 0.05 Tag | jsPDF-Aufrufe von hardcoded auf Badge-textContent umstellen |
| **5.2 Cross-Browser-Download Variante A** | 0.1 Tag | Anchor-Click-Pattern, in Chrome **und** Safari testen |
| **5.3 Falls A fail't: Variante B** | 0.1 Tag | Browser-Weiche, Safari-Hint-Text |
| **5.4 Cache-Tooltip präzisieren** | 0.05 Tag | i18n-Text DE+EN |
| **5.5 Verifikation Browser** | 0.05 Tag | DIEGOsat in Chrome **und** Safari → Header zeigt korrekte Version + Direct-Download (oder dokumentierter Safari-Fallback) |
| **5.6 Headless-Pool** | 0.05 Tag | 7/7 PASS bleibt (kein Validator-Touch) |
| **5.7 README + CHANGELOG** | 0.05 Tag | "v0.25.4.1 Polish-Patch"-Eintrag |
| **5.8 ADR-30 dokumentieren** | inkludiert | "PDF-Output-Polish: dynamische Version + Cross-Browser-Download" |
| **5.9 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.4.1, Tag, Push |

**Total: 0.3–0.5 Tag.**

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.25.4 released | ⏳ vor v0.25.4.1 abschließen |
| 2 | Befund-Quellen gesammelt | ✓ `../tests/real-world-2026-05-05.md` |
| 3 | Lösungsstrategie pro Bug klar | ✓ A→B-Pattern für Bug 2, sonstige trivial |

**2 von 3 grün, 1 abhängig von v0.25.4.**

---

## 6. Decision-Log-Template

```markdown
### ADR-30 PDF-Output-Polish — 2026-05-XX

**Kontext:** Real-World-Sweep 2026-05-05 zeigte drei PDF-/UX-Befunde:
- PDF-Header hardcoded "v0.25"
- Safari-PDF-Button öffnet Tab statt Download
- Cache-Counter UX-irreführend

**Entscheidung:**
- PDF-Header dynamisch aus DOM-Versions-Badge gezogen
- Cross-Browser-Download via Anchor-Click-Pattern (Variante ___)
- Cache-Tooltip präzisiert

**Konsequenz:** PDF-Reports zeigen immer aktuelle Inspector-Version. Safari-User kriegen Direct-Download oder klaren Hinweis-Pfad. Cache-Counter ist klarer dokumentiert.
```

---

## 7. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- Diagnose-Quelle: `../tests/real-world-2026-05-05.md`
- Vorgänger: `ROADMAP-v0.25.4.md` (Severity + AVIF)

---

**Ende v0.25.4.1-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.4.1`, Push.
