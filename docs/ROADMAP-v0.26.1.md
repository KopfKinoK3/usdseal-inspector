# Roadmap v0.26.1 — Texturen-Sektion im PDF

**Status:** Vorbereitungs-Dokument · 2026-05-08
**Story-Slot:** *"Texturen werden audit-tauglich — PBR-Channels, Format-Details und Auflösung jetzt auch im PDF"*
**Ziel:** Neue PDF-Sektion **TEXTUREN** zwischen Geometrie und USDseal-Block. Daten kommen aus `extractTextures()` + `buildChannelMap()` (vorhanden seit v0.24/v0.25.5), Layout im jsPDF-Stil der bestehenden Sektionen.
**Aufwand:** 0.6–0.8 Tag.

> Zweiter Sub-Sprint der v0.26-Welle (PDF-Template-Update). Master-Übersicht in `../ROADMAP.md`. Vorgänger: `ROADMAP-v0.26.0.md` (Geometrie-Sektion released 2026-05-07, Commit `f65084a`).

---

## 1. Befund

**v0.26.0 hat den PDF-Audit-Report Geometrie-vollständig gemacht** — 10 Geometry-Kennzahlen sichtbar, USDC-Binary-Hint korrekt aktiv. Saubere Reihenfolge AR → Geometrie → USDseal → Asset-Inventory.

**ABER:** Die Texture-Daten im PDF sind nur im **Asset-Inventory**-Tabellen-Stil sichtbar (Pfad / Größe / SHA-256-8 / Status). **Was fehlt:**

1. **PBR-Channel-Erkennung** (v0.24, 10 Channels: BaseColor / Normal / Occlusion / Roughness / Metallic / Emissive / Opacity / Displacement / Subsurface / Clearcoat plus ORM-kombiniert) — nur im UI sichtbar
2. **Format-Details** (v0.25.4 AVIF, v0.25.5 HEIC/KTX2/TIFF/ASTC) — Magic-Bytes-Reader liefern Format-Label, im PDF unsichtbar
3. **Auflösung** (Breite × Höhe in Pixeln) — UI zeigt sie, PDF nicht

→ **Inspector-USP "Texture-Audit für B2B-Engineering" hat im PDF eine Lücke.** Kunde sieht im UI 10 PBR-Channels + Format-Details + Auflösung, im PDF-Audit-Report gibt's nur Pfad + SHA-256.

→ **v0.26.1 schließt die Lücke** mit einer neuen Sektion zwischen Geometrie und USDseal-Block.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "extractTextures\|buildChannelMap\|pbrChannel\|analyzeTexture" index.html | head -30
grep -n "_currentReport.textures\|textures\[\]\|textures:.*\[" index.html | head -20
grep -n "renderTexturesSection\|renderMiniDashboard" index.html | head -10
```

→ Lokalisiert:
1. Welche Felder in der `textures[]`-Datenstruktur liegen (per File: name / extension / format / width / height / channel / status / sha256 / size)
2. Wo im UI die Texturen mit Channels + Format gerendert werden (`renderTexturesSection` v0.24/v0.25)
3. Welche Werte bei USDC-Binary auf `unknown` gesetzt werden (ADR-33-Pattern)
4. Insertion-Point in `generatePDF()` zwischen Geometrie-Sektion und USDseal-Block

**Konsistenz-Check:** `_currentReport.textures` muss alle Felder enthalten, die im UI verwendet werden. Falls nicht: gleicher Mini-Patch-Move wie bei v0.26.0 (`_currentReport.geoStats` ergänzen) — Code-Chat dokumentiert es im Briefing-Output.

---

## 3. Scope

### 3.1 Neue PDF-Sektion "TEXTUREN"

**Position:** zwischen Geometrie-Sektion und USDseal-Block (analog v0.26.0-Pattern, ADR-32-User-First).

**Reihenfolge nach v0.26.1:**

```
1. DATEI-IDENTITÄT
2. AR QUICK LOOK · DIAGNOSE
3. GEOMETRIE
4. TEXTUREN          ← NEU
5. USDSEAL · TRUST & PROVENANCE
6. ASSET-INVENTORY
7. PROVENANCE-TIMELINE
8. DISCLAIMER
```

**Layout:**

```
TEXTUREN
─────────────────────────────────────────
[USDC-Binary-Hint-Box wenn aktiv — analog ADR-33]

textures/material0_basecolor.png
  PNG · 318 KB · 2048×2048
  Channel: BaseColor    Status: tracked

textures/material0_normal.png
  PNG · 1.3 MB · 2048×2048
  Channel: Normal       Status: tracked

textures/material0_occlusion_roughness_metallic.png
  PNG · 1.8 MB · 2048×2048
  Channel: ORM (kombiniert)    Status: tracked

textures/CiscoBild.jpg
  JPEG · 10.3 MB · 383×...
  Channel: unknown      Status: unknown

[Zusammenfassung: N Texturen | X tracked | Y unknown | Z formate]
─────────────────────────────────────────
```

(Die genauen Felder und Reihenfolge ergeben sich aus Phase 5.0. Falls `_currentReport.textures` weniger Felder als das UI hat: Mini-Patch zur Datenstruktur-Erweiterung.)

**Visueller Stil:** orange Akzentleiste analog v0.26.0-Geometrie-Sektion. Konsistente Layout-Sprache.

**i18n DE+EN** für Sektion-Header, Feldnamen, Channel-Labels (BaseColor, Normal, Occlusion, Roughness, Metallic, Emissive, Opacity, Displacement, Subsurface, Clearcoat, ORM, unknown), Format-Labels (PNG, JPEG, WebP, AVIF, HEIC, KTX2, TIFF, ASTC), Status-Labels (tracked, unknown, mismatch, structure).

### 3.2 Spezialfall USDC-Binary-Materials (analog ADR-33)

Wenn `usdcBinaryMaterials === true`:

```
ⓘ Diese USDZ enthält USDC-Binary-Materials. Inspector kann Material-
  Bindings nicht analysieren. Channels werden als "unknown" markiert.
```

(Box-Stil identisch zu der bereits v0.26.0 implementierten Hinweis-Box. Heuristik existiert seit v0.25.7 in `buildChannelMap`.)

### 3.3 Spezialfall Format-Detail-Hinweis

Bei nicht-Browser-renderbaren Formaten (KTX2/TIFF/ASTC, je nach Browser auch HEIC) — kompakter Hint pro Zeile:

```
textures/foo.ktx2
  KTX2 · 2.4 MB · 2048×2048 (kein Browser-Preview)
  Channel: BaseColor     Status: tracked
```

Konsistent mit v0.25.5-UI-Logik.

### 3.4 Was NICHT in v0.26.1

- **Keine neue Channel-Heuristik** — wir rendern, was `buildChannelMap()` heute liefert
- **Keine Format-Detection-Erweiterung** — AVIF/HEIC/KTX2/TIFF/ASTC reichen (alle OpenUSD-Spec-konform seit v0.25.5)
- **Kein Texture-Preview im PDF** — wäre Bundle-Bloat, jsPDF-Image-Embedding ist eigene Wurmkiste
- **Asset-Inventory-Tabelle bleibt unverändert** — TEXTUREN-Sektion läuft daneben (UI-Pattern: Mini-Dashboard + Tabelle parallel)
- **Keine Komposition** (Layer-Stack/References) — bleibt v0.28-Backlog

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt, jsPDF unverändert |
| `extractTextures()` + `buildChannelMap()` | vorhanden seit v0.24/v0.25.7 | wird im PDF-Generator wiederverwendet |
| `_currentReport.textures` | ggf. Mini-Patch nötig | Phase 5.0 prüft Vollständigkeit |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.26.0 stabil released | ✓ Tag online seit 2026-05-07, Commit `f65084a` |
| 2 | Texture-Daten im UI sichtbar | ✓ seit v0.24/v0.25 |
| 3 | PDF-Layout-Pattern aus v0.26.0 als Referenz | ✓ |
| 4 | USDC-Binary-Hint-Pattern (ADR-33) | ✓ in v0.25.7/v0.26.0 |
| 5 | Test-Pool: Frankfurt (USDC-Binary) + DIEGOsat (signiert) | ✓ im review-pool |

**5 von 5 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep + textures-Felder-Liste extrahieren, ggf. `_currentReport.textures`-Mini-Patch identifizieren |
| **5.1 PDF-Sektion bauen** | 0.3 Tag | Neue `renderTexturesSection(doc, ctx)`-Funktion in jsPDF, Layout, i18n DE+EN für ~25 Keys |
| **5.2 Position in generatePDF()** | 0.05 Tag | Aufruf zwischen Geometrie-Sektion und USDseal-Block einfügen |
| **5.3 USDC-Binary-Hint** | 0.05 Tag | Hinweis-Box analog ADR-33-Pattern (aus v0.26.0 wiederverwertbar) |
| **5.4 Browser-Verifikation** | 0.05 Tag | Frankfurt + DIEGOsat in Chrome + Safari → PDF zeigt neue Texturen-Sektion mit Channels |
| **5.5 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt (kein Validator-Touch) |
| **5.6 README + CHANGELOG** | 0.05 Tag | "Texturen-Sektion im PDF" |
| **5.7 ADR-36** | inkludiert | Template § 9 |
| **5.8 INSPECTOR_VERSION + Snapshot + Tag** | 0.05 Tag | INSPECTOR_VERSION='0.26.1', Snapshot, Tag, Push — **achtsam mit der Konstante**, v0.26.0 hat dort einen Verzug gehabt |

**Total: 0.6–0.8 Tag.**

---

## 7. Strategischer Hebel

v0.26.1 ist **PDF-Audit-Vollständigkeits-Sprint Phase 2**:

1. **PDF-Audit-Report wird material-audit-vollständig** — alle UI-Texture-Inhalte sind jetzt im PDF spiegelbar. B2B-Engineering-Kunden kriegen Channel-Audit auf Papier.
2. **Format-USP wird im PDF sichtbar** — AVIF/HEIC/KTX2/TIFF/ASTC-Coverage (v0.25.5) war bislang nur UI. AOUSD-Talk-Material ("erster Web-USDZ-Inspector mit kompletter OpenUSD-Spec-Texture-Coverage **im Audit-Report**") wird konkret.
3. **Story-Anschluss zu v0.26.0:** "Wir haben Geometrie audit-tauglich gemacht — jetzt sind die Texturen dran."
4. **PR-Story:** "PDF-Audit-Report ist material-tief — von Mesh-Polygon bis PBR-Channel."

Nach v0.26.1 ist der PDF-Audit-Report **inhaltlich vollständig** gegenüber dem UI. Damit wird **v0.27 Verify-UI** der nächste qualitativ andere Sprint (Self-Tests + Diff-View, Trust-Layer).

---

## 8. Konkrete Pre-v0.26.1-Steps

Keine — alle Vorbedingungen erfüllt. Briefing kann direkt an Code-Chat.

---

## 9. Decision-Log-Template

```markdown
### ADR-36 Texturen-Sektion im PDF — 2026-05-XX

**Kontext:** v0.26.0 hat PDF-Audit-Report Geometrie-vollständig gemacht. UI zeigt aber zusätzlich pro Textur PBR-Channel (v0.24, 10 Channels), Format-Details (v0.25.4 AVIF + v0.25.5 HEIC/KTX2/TIFF/ASTC) und Auflösung — im PDF unsichtbar. Asset-Inventory-Tabelle zeigt Texture-Files nur als Pfad+Größe+SHA-256.

**Entscheidung:** Neue PDF-Sektion "TEXTUREN" zwischen Geometrie und USDseal-Block. Daten aus `extractTextures()` + `buildChannelMap()` wiederverwendet. Layout-Stil konsistent mit v0.26.0 (orange Akzentleiste). USDC-Binary-Hint analog ADR-33-Pattern. i18n DE+EN für ~25 Keys. Asset-Inventory bleibt unverändert (parallel zur TEXTUREN-Sektion, UI-Pattern bestätigt).

**Konsequenz:** PDF-Audit-Report ist material-audit-vollständig. AOUSD-Talk-Story "komplette OpenUSD-Spec-Texture-Coverage im Audit-Report" konkret nachweisbar. v0.27-Sprint kann mit klarer Trust-Layer-Story starten (Verify-UI Self-Tests).
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.26.0-Briefing: `ROADMAP-v0.26.0.md` (Geometrie-Sektion eingeführt, Pattern für v0.26.1)
- ADR-33 USDC-Material-Limitation: `CLAUDE-Inspector-private.md` (Hinweis-Box-Pattern)
- v0.24-Briefing: `ROADMAP-v0.24.md` (PBR-Channel-Erkennung)
- v0.25.4-Briefing: `ROADMAP-v0.25.4.md` (AVIF-Detection)
- v0.25.5-Briefing: `ROADMAP-v0.25.5.md` (HEIC/KTX2/TIFF/ASTC-Detection)
- v0.25.7-Briefing: `ROADMAP-v0.25.7.md` (USDC-Material-Limitation, `usdcBinaryMaterials`-Flag)

---

**Ende v0.26.1-Briefing.** Nach Sprint: INSPECTOR_VERSION-Konstante hochsetzen (NICHT vergessen!), Snapshot, Tag `v0.26.1`, Push. Dann v0.27 (Verify-UI Self-Tests + Diff-View) — CLI-Spec ist seit 2026-05-07 verfügbar.
