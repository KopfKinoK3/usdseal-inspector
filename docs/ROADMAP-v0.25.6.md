# Roadmap v0.25.6 — User-First-Report-Reihenfolge

**Status:** Vorbereitungs-Dokument · 2026-05-06
**Story-Slot:** *"Vom USDseal-zentrischen zum generischen USDZ-Audit-Report"*
**Ziel:** PDF-Report-Sektion-Reihenfolge umkehren — AR-Quick-Look-Diagnose nach oben, USDseal-Trust/Provenance nach unten. Inhalt unverändert, nur Reihenfolge.
**Aufwand:** 0.3–0.5 Tag.

> Patch-Sprint nach v0.25.5. Master-Übersicht in `../ROADMAP.md`.

---

## 1. Befund

**Aus dem Real-World-Sweep 2026-05-05** (`tests/real-world-2026-05-05.md`):

Der aktuelle PDF-Report ist **USDseal-zentrisch** strukturiert — Trust-Status und Asset-Inventory dominieren oben, AR-Quick-Look-Diagnose erscheint erst nach 2–3 Sektionen. Das hat zwei Probleme:

1. **Unsigniert = "Kein Manifest" prominent oben** → für nicht-USDseal-Kunden wirkt's wie "Werbung" statt Audit
2. **Wichtigste Frage ("Funktioniert auf iPhone?") versteckt** → User muss runterscrollen
3. **Einsatz auf Landingpage / als Sales-Material** schwer, weil USDseal-Bias offensichtlich

**Strategischer Pivot:** Inspector als **generischer USDZ-Auditor**, USDseal als **Plus-Sektion**. Macht Inspector breiter nutzbar (B2B-Kunden ohne USDseal-Setup) und unterstützt PR-Story für Landingpage-Beispiele.

---

## 2. Phase 5.0 — Diagnose

**Phase 5.0 ist im v0.25.4-/v0.25.5-Sweep durchgespielt.** Code-Chat soll als Erstes:

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "generatePDF\|jsPDF\|doc.text\|doc.addPage" index.html | head -30
```

→ Identifiziert die `generatePDF()`-Funktion und die Sektion-Reihenfolge der jsPDF-Aufrufe.

---

## 3. Scope

### 3.1 Neue Reihenfolge

```
1. DATEI-IDENTITÄT          (Dateiname, Größe, SHA-256, Generiert, Inspector-Version)
2. AR QUICK LOOK · DIAGNOSE (Banner: bricht / Vorbehalt / sauber + Findings-Liste)   ← NEU prominent oben
3. TEXTURE-INVENTAR         (Format, Used/Unused, Channel-Map)                        ← NEU prominent
4. GEOMETRIE-STATS          (Polygons, Vertices, Time-Range, FPS)                     ← NEU prominent
5. USDSEAL · TRUST & PROVENANCE                                                       ← USDseal-Block unten
   - Trust-Status (Signiert / Kein Manifest)
   - Manifest-ID + SHA-256
   - Counter (tracked / mismatch / extra / missing / structure)
   - Asset-Inventory (alle Files mit Hashes)
   - Provenance-Timeline (nur bei signiert)
6. DISCLAIMER
```

### 3.2 Was rein kommt

- **Sektion-Reihenfolge in `generatePDF()`** umstellen (rein Reorder, kein neuer Inhalt)
- **Optional:** "USDSEAL · TRUST & PROVENANCE"-Header als visuelle Sektion-Trennung (orange Akzentleiste analog v0.23-Layout-Style)
- **Optional:** wenn unsigniert → USDseal-Sektion zeigt minimal "Kein Manifest — `usdseal init` für Provenance" (kompakt, keine ganze Counter-Tabelle)
- **i18n:** Banner-Text "AR Quick Look · Diagnose" als neue oben-prominente Headline

### 3.3 Was NICHT in v0.25.6

- Kein Logik-Change (Findings, Severity, Texture-Detection alle unverändert)
- Keine neuen Inhalte (Channel-Map, Geometry-Stats kommen aus v0.24/v0.25)
- Kein PDF-Template-Update für Channel/Geometry-PDF-Inhalte (das ist v0.26)
- Kein Asset-Inventory-Refactor (bleibt vollständig, nur jetzt im USDseal-Block)

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt |
| jsPDF (vorhanden seit v0.23) | unverändert | nur Aufruf-Reihenfolge ändert sich |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.5 stabil released | ✓ Tag online seit 2026-05-05, Commit `c1338fd` |
| 2 | PDF-Generator-Sektion-Verständnis | ✓ generatePDF() in index.html identifizierbar |
| 3 | Test-Pool für Cross-Type-Verifikation | ✓ 13 Real-World-Files (5 unsigniert + DIEGOsat-Familie signiert) |

**3 von 3 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep auf generatePDF(), Sektion-Aufruf-Liste extrahieren |
| **5.1 Sektion-Reorder** | 0.15 Tag | Aufruf-Reihenfolge in generatePDF() umstellen |
| **5.2 USDseal-Block-Header** | 0.05 Tag | Visuelle Trennung "USDSEAL · TRUST & PROVENANCE" mit Akzentleiste |
| **5.3 Kompakter NO_MANIFEST-Block** | 0.05 Tag | Wenn unsigniert: nur Mini-Hint statt voller Counter-Tabelle (optional, je nach Code-Komplexität) |
| **5.4 Verifikation Browser** | 0.05 Tag | PDF generieren in Chrome + Safari, Reihenfolge prüfen |
| **5.5 Cross-Type-Test** | 0.05 Tag | Frankfurt (unsigniert) + DIEGOsat (signiert) — beide Reports ansehen |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt (kein Validator-Touch) |
| **5.7 README + CHANGELOG** | 0.05 Tag | "User-First-Report"-Eintrag |
| **5.8 ADR-32** | inkludiert | "PDF-Report-Reihenfolge auf User-First umgestellt" |
| **5.9 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.6, Tag, Push |

**Total: 0.5 Tag konzentrierter Build.**

---

## 7. Strategischer Hebel

v0.25.6 ist **PR-Hebel-Sprint**:

1. **Inspector-Positionierung breiter** — Generic-USDZ-Auditor statt USDseal-Werbung. Apple-/visionOS-Devs ohne USDseal-Setup nutzen Inspector trotzdem.
2. **PR-Material:** Report-Beispiele auf Landingpage zeigen jetzt zuerst "Validator-Wert", USDseal als Add-on.
3. **AOUSD-Talk-Slide:** Demo-PDF zeigt sofort "AR Quick Look · Diagnose" — der USP.
4. **Severity-Recal-Zugkraft:** "Läuft mit Vorbehalt"-Banner aus v0.25.4 wird jetzt **prominent oben sichtbar** im PDF — ehrliche Aussage als Hauptbotschaft.

---

## 8. Konkrete Pre-v0.25.6-Steps

Keine — alle Vorbedingungen erfüllt. Code-Chat kann sofort starten.

---

## 9. Decision-Log-Template

```markdown
### ADR-32 PDF-Report-Reihenfolge User-First — 2026-05-06

**Kontext:** Real-World-Sweep 2026-05-05 zeigte: PDF-Audit-Report ist USDseal-zentrisch. AR-Quick-Look-Diagnose (USP) erscheint erst nach 2–3 Sektionen, "Kein Manifest"-Banner dominiert oben bei unsignierten Files.

**Entscheidung:** Reihenfolge umstellen — Datei-Identität → AR Quick Look · Diagnose → Texture-Inventar → Geometrie-Stats → USDseal · Trust & Provenance → Disclaimer.

**Konsequenz:** Inspector-Report wird generisch nutzbar (Apple-Devs ohne USDseal-Setup), USDseal als Plus-Sektion. PR-Material auf Landingpage tauglicher. Validator-USP prominent oben.
```

---

## 10. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.25.5.md` (Texture-Spec-Vollständigkeit)
- Diagnose-Quelle: `../tests/real-world-2026-05-05.md` (zeigte den USDseal-zentrischen Bias im Layout)
- v0.23-Briefing: `ROADMAP-v0.23.md` (PDF-Report initial eingeführt)
- Folge: `ROADMAP-v0.25.7.md` (USDC-Material-Limitation, Task #56) — kommt nach v0.25.6

---

**Ende v0.25.6-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.6`, Push.
