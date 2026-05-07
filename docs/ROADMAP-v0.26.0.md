# Roadmap v0.26.0 — Geometry-Stats-Sektion im PDF

**Status:** Vorbereitungs-Dokument · 2026-05-06
**Story-Slot:** *"Geometrie wird audit-tauglich — alle 10 Kennzahlen jetzt auch im PDF"*
**Ziel:** Neue PDF-Sektion **GEOMETRIE** zwischen Texture-Inventar und USDseal-Block einfügen. Daten kommen aus `extractGeometryStats()` (v0.25), Layout im jsPDF-Stil der bestehenden Sektionen.
**Aufwand:** 0.5–1 Tag.

> Erster Sub-Sprint der v0.26-Welle (PDF-Template-Update). Master-Übersicht in `../ROADMAP.md`.

---

## 1. Befund

**v0.25 hat Geometry-Vollscope eingeführt:** 10 Kennzahlen pro USDZ — Polygons, Vertices, Meshes, Triangles, Animation-Type, Time-Range, FPS, etc. Sichtbar im UI seit 2026-05-04.

**ABER:** PDF-Audit-Report (v0.23-Basis) zeigt diese Daten **nicht**. PDF aktuell hat nur:
1. Datei-Identität
2. AR Quick Look · Diagnose
3. Texture-Inventar
4. USDseal · Trust & Provenance
5. Disclaimer

**Geometry-Stats fehlen vollständig.** Das ist die größte Lücke nach der v0.25.6-Reorder — User sieht im UI 10 Kennzahlen, im PDF-Audit nichts.

→ **v0.26.0 schließt die Lücke** mit einer neuen Sektion zwischen Texture-Inventar und USDseal-Block.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "extractGeometryStats\|geometryStats\|polyCount\|vertexCount" index.html | head -30
grep -n "generatePDF\|doc.text.*TEXTURE\|doc.text.*USDSEAL" index.html | head -20
```

→ Lokalisiert:
1. Wo `extractGeometryStats()` definiert ist (v0.25)
2. Welche Felder im Result-Objekt liegen
3. Wo in `generatePDF()` die neue Sektion zwischen Texture und USDseal eingefügt wird

**Konsistenz-Check:** Wie heißen die 10 Kennzahlen genau? Code-Chat soll Liste extrahieren und im Briefing dokumentieren (kommt ggf. ins README-Update).

---

## 3. Scope

### 3.1 Neue PDF-Sektion "GEOMETRIE"

**Position:** zwischen Texture-Inventar und USDseal-Block (Reihenfolge konsistent mit UI-Layout v0.25.6).

**Layout:**

```
GEOMETRIE
─────────────────────────────────────────
Meshes              N
Polygons            N (formatiert mit Tausender-Trennzeichen)
Vertices            N
Triangles           N

Animation:          [Type-Bezeichnung] / "Statisch"
  Time-Range:       startTimeCode – endTimeCode
  FPS:              timeCodesPerSecond
  Dauer:            (endTime - startTime) / fps  Sekunden

Bounding Box:       (W × H × D) Einheit (falls verfügbar)
Up-Axis:            Y / Z / X
Skala (m/unit):     metersPerUnit
─────────────────────────────────────────
```

(Die genauen 10 Felder ergeben sich aus `extractGeometryStats()`-Output. Phase 5.0 listet sie auf.)

**Visueller Stil:** orange Akzentleiste analog "USDSEAL · TRUST"-Sektion (v0.25.6). Konsistente Layout-Sprache.

**i18n DE+EN** für Sektion-Header, Feldnamen, Animations-Labels.

### 3.2 Spezialfall: keine Geometrie-Daten verfügbar

Wenn USDC-Binary (Frankfurt-Style) → `extractGeometryStats()` liefert ggf. nur Teilwerte. **Hinweis-Box analog v0.25.7:**

```
ⓘ Geometrie-Daten teilweise unvollständig — USDC-Binary kann nicht voll
  geparsed werden. Beste-Schätzung aus Header-Strings.
```

(Optional — wenn Code-Chat findet dass Frankfurt vs. DIEGOsat-Geometry-Output divergiert. Falls nicht: Nur Werte zeigen.)

### 3.3 Was NICHT in v0.26.0

- Keine **Texture-Inventar**-Erweiterung (kommt in v0.26.1)
- Keine **Channel-Erkennung im PDF** (kommt in v0.26.1)
- Keine neuen Geometry-Stats-Felder im UI (alles unverändert, nur PDF-Sektion neu)
- Keine **Komposition** (Layer-Stack/References) — wandert in v0.28 Pro-Variante

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt, jsPDF unverändert |
| `extractGeometryStats()` | vorhanden seit v0.25 | wird im PDF-Generator wiederverwendet |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.8 stabil released | ✓ Tag online seit 2026-05-06, Commit `2ce334a` |
| 2 | Geometry-Stats-Daten im UI sichtbar | ✓ seit v0.25 |
| 3 | PDF-Layout-Pattern aus v0.25.6 als Referenz | ✓ |
| 4 | Test-Pool: Frankfurt + DIEGOsat als signiert+unsigniert-Beleg | ✓ im review-pool |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep + Stats-Felder-Liste extrahieren |
| **5.1 PDF-Sektion bauen** | 0.3 Tag | Neue `renderGeometrySection()`-Funktion in jsPDF, Layout, i18n DE+EN |
| **5.2 Position in generatePDF()** | 0.05 Tag | Aufruf zwischen Texture-Inventar und USDseal-Block einfügen |
| **5.3 Spezialfall USDC-Binary** | 0.1 Tag | Optional — Hinweis-Box wenn Stats unvollständig |
| **5.4 Browser-Verifikation** | 0.05 Tag | Frankfurt + DIEGOsat in Chrome + Safari → PDF zeigt neue Geometrie-Sektion |
| **5.5 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt (kein Validator-Touch) |
| **5.6 README + CHANGELOG** | 0.05 Tag | "Geometrie-Sektion im PDF" |
| **5.7 ADR-35** | inkludiert | Template § 9 |
| **5.8 Snapshot + Tag** | 0.05 Tag | Snapshot v0.26.0, Tag, Push |

**Total: 0.6–0.8 Tag.**

---

## 7. Strategischer Hebel

v0.26.0 ist **Audit-Vollständigkeits-Sprint**:

1. **PDF-Audit-Report wird vollständig** — alle UI-Inhalte sind jetzt im PDF spiegelbar. Externe Tester / B2B-Kunden / AOUSD-Talk-Demos kriegen ein in-sich geschlossenes Dokument.
2. **Geometrie als USP** — Konkurrenz-USDZ-Tools zeigen 3D-Modell, USDseal Inspector zeigt **die Zahlen dahinter**. Polygons/Vertices/Time-Range im Audit-Report ist B2B-Engineering-Sprache.
3. **Story-Anschluss zu v0.25:** "Wir haben Geometrie-Vollscope eingeführt — jetzt ist sie auch im Audit-Report."

---

## 8. Konkrete Pre-v0.26.0-Steps

Keine — alle Vorbedingungen erfüllt.

---

## 9. Decision-Log-Template

```markdown
### ADR-35 Geometrie-Sektion im PDF — 2026-05-XX

**Kontext:** v0.25 hat 10 Geometry-Kennzahlen im UI eingeführt. PDF-Audit-Report (v0.23-Basis) zeigt sie nicht. Lücke nach v0.25.6-Reorder am größten.

**Entscheidung:** Neue PDF-Sektion "GEOMETRIE" zwischen Texture-Inventar und USDseal-Block. Daten aus `extractGeometryStats()` wiederverwendet. Layout-Stil konsistent mit v0.25.6 (orange Akzentleiste). i18n DE+EN.

**Konsequenz:** PDF-Audit-Report ist vollständig — alle UI-Inhalte spiegelbar. Audit-Tauglichkeit für B2B steigt.
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.25-Briefing: `ROADMAP-v0.25.md` (Geometry-Vollscope eingeführt)
- v0.25.6-Briefing: `ROADMAP-v0.25.6.md` (PDF-Reorder, Layout-Pattern)
- v0.23-Briefing: `ROADMAP-v0.23.md` (jsPDF-Builder originaler Stand)

---

**Ende v0.26.0-Briefing.** Nach Sprint: Snapshot, Tag `v0.26.0`, Push. Dann v0.26.1 (Texture-Inventar erweitern).
