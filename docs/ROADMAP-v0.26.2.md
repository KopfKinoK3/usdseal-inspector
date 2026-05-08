# Roadmap v0.26.2 — Texture-Tabelle threshold-basiert

**Status:** Vorbereitungs-Dokument · 2026-05-08
**Story-Slot:** *"PDF-Audit-Report wird Großfile-tauglich — kompakte Tabelle statt 8-Seiten-Marathon"*
**Ziel:** Bei vielen Texturen (Threshold) wechselt die TEXTUREN-Sektion vom 3-Zeilen-Block-Layout (v0.26.1) auf eine **kompakte Tabelle**. Kleine Files behalten den hübschen Block, Großfiles kriegen Tabellen-Layout. UX-Polish vor v0.27-PR-Welle.
**Aufwand:** 0.3–0.5 Tag.

> Polish-Sprint vor v0.27. Master-Übersicht in `../ROADMAP.md`. Vorgänger: `ROADMAP-v0.26.1.md` (Texturen-Sektion released 2026-05-08).

---

## 1. Befund

**Browser-Verifikation v0.26.1 mit Frankfurt (2026-05-08):** PDF-Audit-Report erstreckt sich über **8 Seiten** — TEXTUREN-Sektion alleine nimmt Seiten 2–5 ein, weil jede der 55 Texturen drei Zeilen bekommt:

```
textures/Frontbezug.jpg
  JPEG · 315.5 KB · 950x934
  Channel: unknown    Status: unknown
```

Bei DIEGOsat (4 Texturen) ist das Block-Layout **schön und lesbar**. Bei Frankfurt (55 Texturen) wird der Report **lang und unhandlich** — schlecht für PR-Material auf Landingpage und LinkedIn-Karussells.

**Lösung:** Threshold-basiertes Layout-Switching. Kleine Files behalten den Block, große Files kriegen kompakte Tabelle. Beste-aus-beiden-Welten.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "renderTexturesSection" index.html | head -10
grep -n "ASSET-INVENTORY\|renderAssetInventory\|doc.autoTable\|doc.table" index.html | head -20
```

→ Lokalisiert:
1. Wo `renderTexturesSection(doc, ctx)` definiert ist (v0.26.1)
2. Wie Asset-Inventory die Tabelle rendert (jsPDF-Pattern, vermutlich manuell mit `doc.text` + `doc.line` oder via autoTable-Plugin)
3. Insertion-Point für Threshold-Check

**Konsistenz-Check:** Asset-Inventory-Tabellen-Pattern muss wiederverwertbar sein. Falls jsPDF-autoTable nicht im Build ist, manuelle Tabellen-Logik aus Asset-Inventory kopieren — kein neuer Dep.

---

## 3. Scope

### 3.1 Threshold-Konstante

```javascript
const TEXTURE_TABLE_THRESHOLD = 20;
```

In `renderTexturesSection(doc, ctx)`:

```javascript
if (textures.length > TEXTURE_TABLE_THRESHOLD) {
  renderTexturesAsTable(doc, ctx, textures);
} else {
  renderTexturesAsBlocks(doc, ctx, textures);  // bestehende v0.26.1-Logik
}
```

(Methoden-Namen sind Vorschlag — Code-Chat darf umbenennen wenn Konvention im Repo anders ist.)

### 3.2 Tabellen-Layout

**Spalten:** Pfad | Format | Größe | Auflösung | Channel | Status

**Beispiel-Zeile:**

```
0/textures/Image_43.avif    AVIF    338.1 KB    2048×2048    unknown    unknown
```

**Stil:**
- Konsistent mit Asset-Inventory-Tabelle (gleiche Schriftgröße, Spalten-Header-Stil, Zeilen-Trennung)
- Header-Zeile bei jedem Page-Break wiederholen (sonst unleserlich)
- Pfad-Spalte ggf. truncaten bei extrem langen Pfaden (`…`-Suffix)

**USDC-Binary-Hint-Box** bleibt **vor** der Tabelle, identisch zu v0.26.1.

**Zusammenfassungs-Zeile** unter der Tabelle bleibt:

```
55 Texturen gesamt · 55 unknown · 18.0 MB · JPEG/PNG RGBA 8-bit/AVIF
```

(Code-Chat hat das in v0.26.1 als Bonus eingeführt — bleibt erhalten in beiden Layouts.)

### 3.3 i18n DE+EN

6 neue Keys (Spalten-Header):

| Key | DE | EN |
|---|---|---|
| `pdf_tex_col_path` | Pfad | Path |
| `pdf_tex_col_format` | Format | Format |
| `pdf_tex_col_size` | Größe | Size |
| `pdf_tex_col_resolution` | Auflösung | Resolution |
| `pdf_tex_col_channel` | Channel | Channel |
| `pdf_tex_col_status` | Status | Status |

(Status-/Channel-/Format-Werte selbst sind bereits in v0.26.1 i18n-fähig — keine neuen Werte-Keys nötig.)

### 3.4 Was NICHT in v0.26.2

- **Kein Layout-Switch im UI** — UI-Texture-Sektion bleibt unverändert
- **Kein anderer Threshold als 20** — 20 ist gewählt weil bei ≤20 das Block-Layout 60 PDF-Zeilen ergibt = unter 1 Seite. Ab 21 würde die zweite Seite anfangen → Tabelle besser.
- **Kein Sortier-/Filter-Feature in der Tabelle** — Reihenfolge bleibt wie textures-Array sie liefert
- **Keine Threshold-Konfiguration durch User** — Konstante im Code, kein Settings-UI

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt, jsPDF unverändert |
| Asset-Inventory-Tabellen-Pattern | vorhanden seit v0.23 | wird im neuen Renderer wiederverwendet |
| `renderTexturesSection` | vorhanden seit v0.26.1 | wird mit Threshold-Switch ergänzt |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.26.1 stabil released | ✓ Tag online seit 2026-05-08 |
| 2 | Asset-Inventory-Tabellen-Pattern als Referenz | ✓ |
| 3 | Test-Pool mit ≤20-Textur-File (DIEGOsat 4 Texturen) | ✓ |
| 4 | Test-Pool mit >20-Textur-File (Frankfurt 55 Texturen) | ✓ |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep `renderTexturesSection`, Asset-Inventory-Tabellen-Pattern lokalisieren |
| **5.1 Tabellen-Renderer bauen** | 0.15 Tag | `renderTexturesAsTable(doc, ctx, textures)`-Funktion, Spalten-Layout, Header-Wiederholung bei Page-Break, Pfad-Truncation |
| **5.2 Threshold-Switch** | 0.05 Tag | Konstante `TEXTURE_TABLE_THRESHOLD = 20`, if/else in `renderTexturesSection` |
| **5.3 i18n DE+EN** | 0.05 Tag | 6 neue Spalten-Header-Keys |
| **5.4 Browser-Verifikation** | 0.05 Tag | Frankfurt PDF (55 Texturen) → Tabelle; DIEGOsat PDF (4 Texturen) → Block-Layout. Beide in Chrome + Safari |
| **5.5 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt (kein Validator-Touch) |
| **5.6 README + CHANGELOG** | 0.05 Tag | "Threshold-basierte Texture-Tabelle für Großfiles" |
| **5.7 ADR-37** | inkludiert | Template § 9 |
| **5.8 INSPECTOR_VERSION + Snapshot + Tag** | 0.05 Tag | INSPECTOR_VERSION='0.26.2', Snapshot v0.26.2-snapshot.html, Tag v0.26.2, Push |

**Total: 0.4–0.5 Tag.**

---

## 7. Strategischer Hebel

v0.26.2 ist **PR-Vorbereitungs-Polish-Sprint**:

1. **Großfile-Reports werden handlich** — Frankfurt-Report von 8 → vermutlich 4–5 Seiten. Asset-Inventory-Tabelle ist eh schon da, die zweite Tabelle (Texturen) fügt sich konsistent ein.
2. **PR-Material wird besser** — v0.27.1-Landingpage zeigt Audit-Report-PDFs als Beleg ("so sieht ein Inspector-Report aus"). Mit kompakter Tabelle = bessere visuelle Story.
3. **B2B-Audit-Tauglichkeit** — Engineering-Kunden mit 30+ Texturen pro Asset bekommen lesbaren Report statt Marathon-PDF.
4. **Kein Scope-Konflikt mit v0.27** — Verify-UI-Sprint bleibt fokussiert auf Self-Tests + Diff-View, kein Polish-Vermisch.

---

## 8. Konkrete Pre-v0.26.2-Steps

Keine — alle Vorbedingungen erfüllt. Briefing kann direkt an Code-Chat.

---

## 9. Decision-Log-Template

```markdown
### ADR-37 Threshold-basierte Texture-Tabelle — 2026-05-XX

**Kontext:** v0.26.1 hat TEXTUREN-Sektion mit 3-Zeilen-Block-Layout pro Textur eingeführt. Browser-Verifikation Frankfurt 2026-05-08 (55 Texturen → 8 PDF-Seiten) zeigte: bei Großfiles wird der Report unhandlich. Bei DIEGOsat (4 Texturen) bleibt der Block-Layout schön und lesbar.

**Entscheidung:** Threshold-basiertes Layout-Switching in `renderTexturesSection`. Konstante `TEXTURE_TABLE_THRESHOLD = 20`: bei `textures.length > 20` kompakte Tabelle (Spalten: Pfad / Format / Größe / Auflösung / Channel / Status), sonst bestehender Block-Layout. Header-Wiederholung bei Page-Break. Asset-Inventory-Tabellen-Pattern wiederverwendet — kein neuer Dep. USDC-Binary-Hint-Box und Zusammenfassungs-Zeile bleiben in beiden Layouts identisch.

**Konsequenz:** Großfile-Reports sind handlich (Frankfurt vermutlich 4–5 statt 8 Seiten). Kleine Files behalten ästhetisches Block-Layout. UI-Texture-Sektion unverändert. PR-Vorbereitung für v0.27.1-Landingpage: Audit-Report-PDFs sehen unabhängig von Asset-Größe professionell aus.
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.26.1-Briefing: `ROADMAP-v0.26.1.md` (Texturen-Sektion eingeführt, 3-Zeilen-Block-Layout)
- v0.23-Briefing: `ROADMAP-v0.23.md` (jsPDF-Asset-Inventory-Tabellen-Pattern)
- Frankfurt-Verifikations-PDF 2026-05-08 21:27 UTC (8 Seiten, Befund-Trigger)

---

**Ende v0.26.2-Briefing.** Nach Sprint: INSPECTOR_VERSION='0.26.2' setzen, Snapshot, Tag, Push. Dann v0.27 (Verify-UI Self-Tests + Diff-View) — CLI-Spec ist seit 2026-05-07 verfügbar, Sprint unblocked.
