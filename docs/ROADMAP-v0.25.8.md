# Roadmap v0.25.8 — AR-QL-Regel-Korrekturen aus Recherche-Audit

**Status:** Vorbereitungs-Dokument · 2026-05-06
**Story-Slot:** *"Validator-Regeln gegen Apple/OpenUSD verifiziert und korrigiert"*
**Ziel:** Drei Befunde aus dem AR-QL-Sources-Recherche-Audit umsetzen — Regel-Texte, Schwellen und Disclaimer korrigieren.
**Aufwand:** 0.3–0.5 Tag.

> Patch-Sprint nach v0.25.7. Master-Übersicht in `../ROADMAP.md`. Diagnose-Quelle: `docs/AR-QL-RULES-SOURCES.md`.

---

## 1. Befund

**Recherche-Audit 2026-05-06** (`docs/AR-QL-RULES-SOURCES.md`) belegte 20 AR-QL-Validator-Regeln gegen Apple-Doku und OpenUSD-Spec. Befund: 6 solide ✅ / 6 indirekt ⚠️ / 6 nur Praxis ❌ / 2 USDseal-eigen.

**Drei kritische Korrektur-Bedarfe** wurden identifiziert:

### Befund 1 — KRITISCH: WebP in `TEXTURE_FORMAT_UNSUPPORTED` (#9)

**Aktuelle Regel (falsch):**
> *"AR Quick Look unterstützt nur PNG, JPEG und (eingeschränkt) WebP für Texturen."*

**Recherche-Befund:**
- **WebP ist NICHT in der OpenUSD-USDZ-Spec.** Die Spec listet PNG, JPEG, OpenEXR, AVIF.
- AR Quick Look produktiv: nur PNG und JPEG. Auf visionOS zusätzlich HEIC.
- Quelle: [variant3d.com/blog/quicklooks-on-ios](https://www.variant3d.com/blog/quicklooks-on-ios) + [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)

**Plus Konsistenz-Frage:** v0.25.4 hat AVIF-Detection eingebaut, v0.25.5 HEIC/KTX2/TIFF/ASTC. Wie verhält sich `TEXTURE_FORMAT_UNSUPPORTED` jetzt mit diesen neuen Format-Detectoren? Werden AVIF/HEIC fälschlich als "unsupported" markiert? **Phase 5.0 muss das prüfen.**

### Befund 2: `STRUCTURE_FILE_SIZE_LIMIT` (#4) — kein Apple-Beleg

**Aktuelle Regel:**
> *"Apple empfiehlt USDZ-Files unter 25 MB für AR Quick Look."*

**Recherche-Befund:**
- Apple publiziert kein hartes MB-Limit. Apple-Forum-Antworten von DTS sagen: *"Quick Look determines that the in-memory size is too large"* — kein API-Hard-Limit.
- 25 MB ist Marketplace-Folklore (AR Code, AR-Plattformen), nicht Apple-Doku.

**Korrektur:** Als **"viSales-/Marketplace-Empfehlung"** labeln, nicht als Apple-Anforderung. Severity bleibt `warn` (passt: lädt langsam, aber bricht nicht).

### Befund 3: `TEXTURE_TOO_LARGE` (#10) — Schwelle falsch

**Aktuelle Regel:**
> *"Textur ist größer als 4096 × 4096 Pixel."*

**Recherche-Befund:**
- Apple empfiehlt **2048×2048** als Target ([WWDC 2023 #10274](https://developer.apple.com/videos/play/wwdc2023/10274/) "Create 3D models for Quick Look").
- AR Quick Look downsampelt zur Laufzeit; >4096 wird auf älteren Geräten reduziert/verworfen.

**Korrektur:** Zweistufig:
- `warn` bei >2048 (Apple-Empfehlung verletzt)
- `error` bei >4096 (älteres iPhone-Verhalten)

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "TEXTURE_FORMAT_UNSUPPORTED\|STRUCTURE_FILE_SIZE_LIMIT\|TEXTURE_TOO_LARGE\|WebP\|webp\|2048\|4096\|25.*MB" index.html | head -40
grep -n "AR_QL_RULES" index.html | head -10
```

→ Regel-Definitionen in `AR_QL_RULES`-Tabelle finden. Plus: prüfen wie `TEXTURE_FORMAT_UNSUPPORTED` aktuell mit AVIF/HEIC/KTX2/TIFF/ASTC interagiert.

**Wichtige Konsistenz-Frage:**
- Wenn `analyzeTexture()` ein AVIF-File erkennt (v0.25.4) — markiert `TEXTURE_FORMAT_UNSUPPORTED` es trotzdem als "unsupported"? → Bug, muss gefixt werden.
- Gleiche Frage für HEIC/KTX2/TIFF/ASTC (v0.25.5).

---

## 3. Scope

### 3.1 Regel-Korrekturen

**TEXTURE_FORMAT_UNSUPPORTED (#9) — neue Texte:**

```javascript
{
  id: 'TEXTURE_FORMAT_UNSUPPORTED',
  severity: 'warn',  // war: 'error' — herabgestuft, weil Apple-Realität gnädiger
  category: 'texture',
  explanation: {
    de: 'AR Quick Look unterstützt produktiv nur PNG und JPEG. Auf visionOS zusätzlich HEIC. OpenUSD-Spec erlaubt zusätzlich OpenEXR und AVIF, aber AR Quick Look auf iOS rendert sie nicht zuverlässig.',
    en: 'AR Quick Look reliably supports only PNG and JPEG. visionOS additionally HEIC. OpenUSD spec also allows OpenEXR and AVIF, but iOS AR Quick Look does not render them reliably.'
  },
  fixHint: {
    de: 'Texturen in PNG (lossless) oder JPEG (lossy, kleiner) konvertieren.',
    en: 'Convert textures to PNG (lossless) or JPEG (lossy, smaller).'
  }
}
```

**Trigger-Logik:**
- Format detected ∉ ['PNG', 'JPEG', 'WebP', 'AVIF', 'HEIC'] → `warn` (KTX2, TIFF, ASTC, OpenEXR, etc.)
- Plus optional: AVIF/HEIC → `info`-Hint *"AR Quick Look auf älteren iOS-Versionen ggf. unzuverlässig"*

**STRUCTURE_FILE_SIZE_LIMIT (#4) — neuer Text:**

```javascript
{
  id: 'STRUCTURE_FILE_SIZE_LIMIT',
  severity: 'warn',
  category: 'structure',
  explanation: {
    de: 'viSales-Empfehlung: USDZ-Files unter 25 MB halten. Apple publiziert kein hartes Limit, aber große Files laden langsam und können auf älteren Geräten Memory-Probleme verursachen.',
    en: 'viSales recommendation: keep USDZ files below 25 MB. Apple publishes no hard limit, but large files load slowly and can cause memory issues on older devices.'
  },
  fixHint: {
    de: 'Texturen verkleinern, Mesh decimieren, ungenutzte Sub-Assets entfernen.',
    en: 'Shrink textures, decimate meshes, remove unused sub-assets.'
  }
}
```

**TEXTURE_TOO_LARGE (#10) — zweistufig:**

```javascript
// Aktuell EINE Regel mit Schwelle 4096
// Neu: zweistufig

{
  id: 'TEXTURE_TOO_LARGE_WARN',
  severity: 'warn',
  category: 'texture',
  threshold: 2048,
  explanation: {
    de: 'Textur überschreitet Apple-Empfehlung 2048×2048 (WWDC 2023 #10274). AR Quick Look downsampelt zur Laufzeit, kostet Memory.',
    en: 'Texture exceeds Apple recommendation of 2048×2048 (WWDC 2023 #10274). AR Quick Look downsamples at runtime, costs memory.'
  }
},
{
  id: 'TEXTURE_TOO_LARGE_ERROR',
  severity: 'error',
  category: 'texture',
  threshold: 4096,
  explanation: {
    de: 'Textur größer 4096×4096. Auf älteren iPhones wird sie verworfen oder massiv reduziert.',
    en: 'Texture larger than 4096×4096. Older iPhones discard or massively reduce it.'
  }
}
```

**ODER:** eine Regel mit dynamischem Severity-Switch — je nach Implementations-Aufwand. Phase 5.0 entscheidet.

### 3.2 Doku-Anpassungen

**`docs/AR-QL-RULES.md`:**
- Disclaimer ganz oben (siehe `AR-QL-RULES-SOURCES.md` § 1)
- Pro Regel ein Quellen-Link auf `AR-QL-RULES-SOURCES.md` § X
- Severity-Tags-Sektion (error/warn/info-Bedeutung)
- Hinweis auf USDseal-eigene Regeln (Manifest-*)

**README.md:**
- AR-QL-Sektion verlinkt auf `AR-QL-RULES-SOURCES.md` für Audit-Tauglichkeit
- "Validator gegen Apple-Doku belegt" als Trust-Statement

### 3.3 Was NICHT in v0.25.8

- Keine neuen Regeln (nur Korrekturen bestehender)
- Keine Backlog-Regeln aus `AR-QL-RULES.md` § 5 (`MATERIAL_NOT_USDPREVIEWSURFACE`, etc. — kommt mit v0.4+ Komposition)
- Kein Severity-Recal weiterer Regeln (das war v0.25.4)

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt |
| Recherche-Audit | ✓ | `docs/AR-QL-RULES-SOURCES.md` ist die Diagnose-Quelle |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.7 stabil released | ⏳ vor v0.25.8 abschließen |
| 2 | AR-QL-Sources-Audit dokumentiert | ✓ `docs/AR-QL-RULES-SOURCES.md` |
| 3 | Korrektur-Befunde klar | ✓ siehe § 1 |
| 4 | Test-Pool für Regel-Tests | ✓ Frankfurt (15 AVIF), DIEGOsat (PNG), 13 review-pool-Files |

**3 von 4 grün, 1 abhängig von v0.25.7.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | Konsistenz-Check zwischen `TEXTURE_FORMAT_UNSUPPORTED` und v0.25.4/v0.25.5-Format-Detectoren |
| **5.1 Regel-Texte korrigieren** | 0.1 Tag | DE+EN für #9 + #4, Severity-Anpassung |
| **5.2 TEXTURE_TOO_LARGE zweistufig** | 0.1 Tag | Logic-Anpassung, ggf. zwei Regel-IDs oder dynamischer Severity-Switch |
| **5.3 Disclaimer + Doku** | 0.1 Tag | `AR-QL-RULES.md`-Disclaimer, Quellen-Verlinkung, README-Updates |
| **5.4 Verifikation Browser** | 0.05 Tag | Frankfurt: AVIF jetzt korrekt, kein "unsupported"-Trigger; >2048-Texturen werden warn, >4096 error |
| **5.5 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt + Frankfurt-Erwartung anpassen wenn nötig |
| **5.6 README + CHANGELOG** | 0.05 Tag | "AR-QL-Regeln gegen Apple-Doku verifiziert + 3 Korrekturen" |
| **5.7 ADR-34** | inkludiert | Template § 9 |
| **5.8 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.8, Tag, Push |

**Total: 0.5 Tag konzentrierter Build.**

---

## 7. Strategischer Hebel

v0.25.8 ist **Glaubwürdigkeits-Sprint**:

1. **Externe Tester können Inspector vertrauen:** Validator-Regeln sind dokumentiert + belegt. Drei Fehler aus eigener Recherche selbst gefunden + behoben.
2. **AOUSD-Talk-Slide:** *"Apple hat keinen Validator-Standard — wir kombinieren OpenUSD-Spec, Apple-Doku, WWDC-Sessions und Praxis. Hier ist unsere Quellen-Liste."*
3. **PR-Material:** "Wir haben 20 Regeln gegen Apple-Doku verifiziert und drei korrigiert" ist eine starke Trust-Story.
4. **Konsistenz mit v0.25.4/v0.25.5:** AVIF und HEIC werden nicht mehr fälschlich als "unsupported" markiert.

---

## 8. Konkrete Pre-v0.25.8-Steps

1. v0.25.7 abschließen (USDC-Material-Limitation)
2. Briefing lesen + `AR-QL-RULES-SOURCES.md` § 8 als Korrektur-Anker

---

## 9. Decision-Log-Template

```markdown
### ADR-34 AR-QL-Regel-Korrekturen aus Recherche-Audit — 2026-05-XX

**Kontext:** AR-QL-Sources-Recherche-Audit 2026-05-06 belegte 20 Validator-Regeln gegen Apple-/OpenUSD-Quellen. Drei Korrektur-Bedarfe identifiziert: WebP-Fehler in #9, 25-MB-Folklore in #4, falsche Schwelle 4096 in #10.

**Entscheidung:**
- TEXTURE_FORMAT_UNSUPPORTED: Severity error → warn, Text-Korrektur (PNG/JPEG produktiv, HEIC visionOS), Trigger-Logik konsistent mit v0.25.4/v0.25.5-Format-Detectoren
- STRUCTURE_FILE_SIZE_LIMIT: als "viSales-Empfehlung" gelabelt, nicht als Apple-Anforderung
- TEXTURE_TOO_LARGE: zweistufig — warn >2048 (WWDC2023-Empfehlung), error >4096 (älteres iPhone-Verhalten)
- AR-QL-RULES.md: Disclaimer + Quellen-Verlinkung auf AR-QL-RULES-SOURCES.md

**Konsequenz:** Inspector ist gegen Apple-Doku verifiziert. Externe Tester können Belegtiefe nachprüfen. Trust-Anker für AOUSD-Talk und B2B-Audit-Tauglichkeit.
```

---

## 10. Quellen

- Master-Roadmap: `../ROADMAP.md`
- **Diagnose-Quelle: `AR-QL-RULES-SOURCES.md`** ← Pflicht-Lektüre
- AR-QL-Regelkatalog: `AR-QL-RULES.md`
- Vorgänger: `ROADMAP-v0.25.7.md` (USDC-Material-Limitation)
- Vorgänger v0.25.4: AVIF-Detection
- Vorgänger v0.25.5: HEIC/KTX2/TIFF/ASTC-Detection

### Externe Belege (aus Audit)

- [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)
- [WWDC 2023 #10274 Create 3D models for Quick Look](https://developer.apple.com/videos/play/wwdc2023/10274/)
- [Apple Forum #118710 (file size)](https://developer.apple.com/forums/thread/118710)
- [variant3d.com — Quick Look on iOS](https://www.variant3d.com/blog/quicklooks-on-ios)

---

**Ende v0.25.8-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.8`, Push.
