# Roadmap v0.25.4 — Severity-Recal + AVIF-Detection

**Status:** ✅ **COMPLETED 2026-05-05** · Commit `885cf4d`, Tag `v0.25.4` online
**Story-Slot:** *"Validator kalibriert — Apple-Realität statt Spec-Strenge + AVIF angekommen"*
**Ziel:** AR-Quick-Look-Validator-Severity gegen reale Apple-Toleranz kalibrieren + AVIF-Texture-Detection einbauen. ✓ erreicht.
**Aufwand:** 1–1.5 Tag konzentrierter Build. ✓ eingehalten.

## Release-Befund 2026-05-05

| Phase | Status | Ergebnis |
|---|---|---|
| 5.0 Diagnose-Lesen | ✅ | `tests/real-world-2026-05-05.md` + ROADMAP gelesen |
| 5.1 Severity-Felder | ✅ | DEFAULT_PRIM_MISSING + NESTED_USDZ: error → warning, Kommentar referenziert Sweep |
| 5.2 3-Stufen-Banner | ✅ | i18n DE+EN: "Läuft mit Vorbehalt" / "Runs with caveats" (orange) |
| 5.3 AVIF-Detection + Preview | ✅ | `readAvifSignature()` + Routing in `analyzeTexture()` + Native-Preview-Versuch |
| 5.4 Test-Pool-Erwartungen | ✅ | Headless-EXPECTED um 5 Real-World-Files erweitert |
| 5.5 Browser-Verifikation | ✅ | Chrome JS-Ebene (preview_eval) + Safari Live-Test: Frankfurt-Banner "Läuft mit Vorbehalt" 🟠, **AVIF Teppich.avif Native-Preview gerendert** (Screenshot-Beleg), DIEGOsat_master Trust 🟢 |
| 5.6 Headless-Pool | ✅ | 12/12 PASS (DIEGOsat_TK_280426_01 fehlt noch im Pool für 13/13 — nachzureichen) |
| 5.7 README + CHANGELOG | ✅ | v0.25.4-Eintrag + AR-QL-Sektion + Texture-Zeile + Roadmap-Zeile |
| 5.8 ADR-28 + ADR-29 | ✅ | In `CLAUDE-Inspector-private.md` dokumentiert |
| 5.9 Snapshot + Tag | ✅ | `v0.25.4-snapshot.html` + Commit `885cf4d` + Tag `v0.25.4` |

**Highlight-Beleg:** Frankfurt-File (39 MB, 15× AVIF) wechselte von "AR Quick Look bricht" 🔴 (2 Fehler) zu **"Läuft mit Vorbehalt"** 🟠 (0 Fehler / 4 Warnungen / 3 Hinweise). Subtitle: *"Warnungen erkannt — Asset läuft, Apple-Verhalten kann abweichen."* AVIF `Teppich.avif` (640×640, 102.4 KB) öffnet im Texture-Modal mit voller Native-Preview in Safari.

**Offene Punkte (für nächsten Sprint v0.25.4.1 Polish):**
- PDF-Header zeigt weiter `v0.25` statt `v0.25.4` — bestätigt
- Safari-PDF-Button öffnet HTML-Tab statt Direct-Download — bestätigt
- Cache-Counter-UX-Verfeinerung — offen



> Patch-Sprint nach v0.25.3. Master-Übersicht in `../ROADMAP.md`. Diagnose-Quelle: `tests/real-world-2026-05-05.md`.

---

## 1. Befund

**Real-World-Test-Sweep 2026-05-05** mit 6 viSales-Kunden-/Demo-USDZs (Frankfurt, Vitra, RENZ, AR-Wohnzimmer, SalmonPasta, DIEGOsat) zeigt **zwei zusammenhängende Probleme**:

### Problem 1: Severity-Krise (Hauptanteil)

**100% Trefferquote (6/6 Files) bei zwei Regeln, die fälschlich als 🔴 Hard-Fail markiert werden:**

- `STRUCTURE_DEFAULT_PRIM_MISSING` — alle 6 Files laufen auf iPhone in AR Quick Look, Apple fällt auf "first prim" zurück. Inspector schreit "AR Quick Look bricht" — Trust-Killer.
- `STRUCTURE_NESTED_USDZ` — Frankfurt hat 2 nested USDZ-Files, läuft trotzdem. Inspector schreit "bricht".

**Auch das signierte DIEGOsat-File ist betroffen:** USDseal-Sealing setzt nicht defaultPrim (sauberer Provenance-Layer-Cut), also leiden auch unsere eigenen Demo-Files unter falscher Severity.

### Problem 2: AVIF-Lücke (Bonus)

Frankfurt-File enthält **15 AVIF-Texturen** (eine sogar 4.1 MB) — Inspector erkennt das Format nicht. Aktuelle Detection ist Extension-First (`.png`, `.jpg`, `.webp`) ohne AVIF-Routing.

**HEIC, KTX2, TIFF, ASTC kommen in 6 Real-World-Files NICHT vor** — Spec-Vollständigkeit ohne Praxis-Druck → verschoben in Backlog.

### Detail-Quelle

Vollständige Befunde in `../tests/real-world-2026-05-05.md` — Findings-Matrix, Texture-Format-Reality-Check, Cross-Browser-Notiz.

---

## 2. Phase 5.0 — Diagnose-Status (bereits durchgespielt)

✅ **Phase 5.0 ist erledigt** durch den Real-World-Sweep. Code-Chat soll als erste Aktion `tests/real-world-2026-05-05.md` lesen — alle Befunde + Severity-Verdikte stehen drin.

**Ergänzende Code-Inspection** (~5 Min):

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "AR_QL_RULES\|severity:" index.html | head -30
```

→ Zeigt die Validator-Rules-Tabelle und ihre aktuellen Severity-Felder.

---

## 3. Scope

### 3.1 Severity-Recal (Hauptanteil ~0.5–0.7 Tag)

**Konkrete Severity-Anpassungen** (basierend auf Real-World-Sweep):

| Regel | Alt | Neu | Begründung |
|---|---|---|---|
| `STRUCTURE_DEFAULT_PRIM_MISSING` | 🔴 Fehler | 🟠 Warnung | 6/6 Files laufen, Apple fällt zurück |
| `STRUCTURE_NESTED_USDZ` | 🔴 Fehler | 🟠 Warnung | Frankfurt läuft trotzdem |
| Alle anderen | unverändert | unverändert | Sweep bestätigt korrekte Severity |

**3-Stufen-Severity-Modell** (definitiv etabliert):

| Stufe | Bedeutung | Banner-Text |
|---|---|---|
| 🔴 Hard-Fail | "AR Quick Look bricht garantiert" — z. B. ZIP korrupt, Hauptdatei fehlt, unsupported Format | "AR Quick Look bricht" |
| 🟠 Warnung | "Läuft, aber mit Default-Verhalten oder Surprise" | "Läuft mit Vorbehalt" |
| 🔵 Hinweis | "Schönheitsfehler, kein sichtbarer Effekt" | (Banner-Status unverändert, state-driven) |

**Banner-Logik:**

```javascript
findings.filter(f => f.severity === 'hard-fail').length > 0
  → State-Banner: "AR Quick Look bricht"  🔴
sonst findings.filter(f => f.severity === 'warning').length > 0
  → State-Banner: "Läuft mit Vorbehalt"  🟠
sonst
  → State-Banner unverändert (Trust-Layer-driven: SIGNED / DRAFT / NO_MANIFEST)
```

**Rück-Test mit 6 Real-World-Files:** Alle sollen nach der Recal Banner "Läuft mit Vorbehalt" zeigen — **nicht** "bricht".

### 3.2 AVIF-Detection (Bonus ~0.3–0.5 Tag)

**Neue Magic-Bytes-Reader-Funktion:**

```javascript
function readAvifSignature(data) {
  if (data.length < 12) return null;
  // Bytes 4-7: "ftyp"
  if (data[4] !== 0x66 || data[5] !== 0x74 || data[6] !== 0x79 || data[7] !== 0x70) return null;
  // Bytes 8-11: "avif" oder "avis"
  if (data[8] === 0x61 && data[9] === 0x76 && data[10] === 0x69 && (data[11] === 0x66 || data[11] === 0x73)) {
    return { format: 'AVIF' };
  }
  return null;
}
```

**Routing-Anpassung in `analyzeTexture()`:**
- Wenn Extension `.avif` ODER Magic-Bytes-Match → Format='AVIF'
- Native-Preview-Versuch via Blob-URL + `<img>` (Chrome ✓, Safari 16.4+ ✓)
- Bei `img.onerror` → Fallback auf Format-Label "AVIF (kein Browser-Preview)"

**Channel-Erkennung bleibt unverändert** — die liest Texture-Pfade im USDA, nicht Texture-Daten.

### 3.3 Was bleibt unverändert

- AR-Quick-Look-Validator-**Logik** (welche Regeln triggern wann) — unverändert, nur Severity-Felder
- Texture-Modal-UI (v0.24)
- Geometry-Stats (v0.25)
- iOS-Preview (v0.25)
- PDF-Generator (v0.23)

### 3.4 Was NICHT in v0.25.4

- HEIC/KTX2/TIFF/ASTC Format-Detection → Backlog (kein Use-Case in 6 Files)
- PDF-Header-Bug → v0.25.4.1
- Cross-Browser-PDF-Download-Fix → v0.25.4.1
- Cache-Counter-UX → v0.25.4.1
- Magic-Bytes-First-Routing-Refactor → v0.26 oder später

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt |
| Browser-Native AVIF | Verifiziert | Chrome/Safari aktuell |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.3 stabil released | ✓ Tag online seit 2026-05-04, Commit `fe5fa87` |
| 2 | Real-World-Test-Sweep durchgeführt | ✓ siehe `tests/real-world-2026-05-05.md` |
| 3 | Test-Pool definiert | ✓ 6 Real-World-Files (sollen in `../usdz/review-pool/` wandern) + 7 review-pool DIEGOsat-Varianten |
| 4 | Severity-Verdikt pro Regel klar | ✓ 2 Recal-Kandidaten identifiziert |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose-Lesen** | 0.05 Tag | `tests/real-world-2026-05-05.md` lesen, Code-Inspection grep |
| **5.1 Severity-Felder anpassen** | 0.1 Tag | 2 Regeln in `AR_QL_RULES`-Tabelle umstellen |
| **5.2 Banner-Logik refaktoren** | 0.2 Tag | 3-Stufen-Severity-Banner-Funktion, i18n-Strings für "Läuft mit Vorbehalt" (DE+EN) |
| **5.3 AVIF-Reader + Preview** | 0.3 Tag | `readAvifSignature()`, Routing-Anpassung, Native-Preview-Versuch mit Fallback |
| **5.4 Test-Pool-Migration** | 0.1 Tag | 6 Real-World-Files in `../usdz/review-pool/` legen, Headless-Test um Severity-Pool-Pfad erweitern |
| **5.5 Verifikation Browser** | 0.15 Tag | Frankfurt + DIEGOsat in Chrome **und** Safari durchspielen, Banner muss "Läuft mit Vorbehalt" zeigen, AVIF-Preview muss in Frankfurt sichtbar sein |
| **5.6 Headless-Pool** | 0.1 Tag | 7/7 PASS bleibt, plus Severity-Pool-Erweiterung 6/6 |
| **5.7 README + CHANGELOG** | 0.1 Tag | "Validator kalibriert" + "AVIF unterstützt"-Sektionen |
| **5.8 ADR-28 + ADR-29** | inkludiert | ADR-28 Severity-Recal, ADR-29 AVIF-Detection (zwei separate ADRs für sauberen Audit) |
| **5.9 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.4, Tag, Push (mit Cross-Browser-Pflicht hart!) |

**Total: 1–1.5 Tag.**

---

## 7. Strategischer Hebel

v0.25.4 ist Trust-Anker für B2B-Demos:

1. **"Inspector lügt nicht mehr":** Wenn Banner "Läuft mit Vorbehalt" sagt, läuft die USDZ tatsächlich. Konferenz-Demo-Glaubwürdigkeit steigt drastisch.
2. **3-Stufen-Severity** wird Talk-Slide-Wert: zeigt empirische Validierung statt Spec-Strenge — differenziert von "wir lesen nur die Spec"-Tools.
3. **AVIF-Support** macht Inspector zum ersten Web-USDZ-Inspector mit AVIF-Erkennung — Apple-Workflows hinken hier oft hinterher.
4. **Test-Pool-Erweiterung:** 6 echte Files werden Audit-Trail. Künftige Refactors müssen sie grün lassen — Regression-Schutz.
5. **PR-Material:** Real-World-Sweep + Severity-Pivot ist eine Storyline für LinkedIn/Newsletter ("Wir haben unseren eigenen Validator mit echten Kunden-Files konfrontiert — und ihn dann ehrlich repariert").

---

## 8. Konkrete Pre-v0.25.4-Steps

1. **6 Real-World-Files in `review-pool/` kopieren** (von Duke):
   ```bash
   mkdir -p ~/Documents/Claude/USDseal/usdz/review-pool/
   cp <Pfad-zu-Frankfurt> <Pfad-zu-Vitra> ... ~/Documents/Claude/USDseal/usdz/review-pool/
   ```
2. **Briefing lesen** (dieses Dokument + `tests/real-world-2026-05-05.md`)

---

## 9. Decision-Log-Templates

```markdown
### ADR-28 Severity-Recal — 2026-05-XX

**Kontext:** Real-World-Sweep 2026-05-05 mit 6 viSales-Kunden-Files zeigte universelle Severity-Krise: STRUCTURE_DEFAULT_PRIM_MISSING und STRUCTURE_NESTED_USDZ markieren laufende Files als Hard-Fail.

**Entscheidung:** 3-Stufen-Severity-Modell (bricht / Vorbehalt / Schönheitsfehler), Banner-Logik 3-stufig statt 2-stufig. Severities von 2 Regeln runter (🔴 → 🟠).

**Konsequenz:** Inspector lügt nicht mehr. Trust-Anker bleibt erhalten. Validator-USP wird sogar verstärkt durch empirische Kalibration. Severity-Pool als Regression-Schutz.

### ADR-29 AVIF-Detection — 2026-05-XX

**Kontext:** Frankfurt-Kunden-File enthält 15 AVIF-Texturen (eine 4.1 MB). Inspector erkannte sie nicht. AVIF ist OpenUSD-USDZ-Spec-konform und in Apple-Welt zunehmend verbreitet.

**Entscheidung:** Magic-Bytes-Reader für AVIF-Signature. Native-Browser-Preview-Versuch mit Fallback auf Format-Label.

**Konsequenz:** Inspector als erstes Web-USDZ-Tool mit AVIF-Coverage. HEIC/KTX2/TIFF/ASTC verschoben in Backlog (kein Use-Case in 6 Real-World-Files).
```

---

## 10. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Diagnose-Quelle: `../tests/real-world-2026-05-05.md` ← **Pflicht-Lektüre**
- Vorgänger: `ROADMAP-v0.25.3.md` (EN-Toggle)
- Folge: `ROADMAP-v0.25.4.1.md` (Polish-Patch — PDF-Header, Cross-Browser-PDF, Cache-UX)
- AR-QL-Regeln: `AR-QL-RULES.md`

### Externe Specs

- [OpenUSD USDZ — File Types](https://openusd.org/release/spec_usdz.html#file-types)
- [Apple AR Quick Look — USDZ Support](https://developer.apple.com/augmented-reality/quick-look/) — primär PNG/JPEG, AVIF in modernen iOS-Versionen unterstützt
- [AVIF File Format](https://aomediacodec.github.io/av1-avif/) — Magic-Bytes-Spezifikation

---

**Ende v0.25.4-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.4`, Push (Cross-Browser-Pflicht hart!). Dann v0.25.4.1 als Polish-Patch (PDF-Header, Cross-Browser-PDF-Download, Cache-Counter-UX).
