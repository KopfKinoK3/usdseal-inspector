# Real-World-Test-Sweep — 2026-05-05

**Zweck:** Phase-5.0-Diagnose-Anker für v0.25.4-Sprint. 6 echte viSales-Kunden-/Demo-USDZs durch Inspector v0.25.3 geschickt, Audit-Reports gesammelt, Validator-Befunde gegen iPhone-AR-Realität abgeglichen.

**Inspector-Stand:** v0.25.3 (`fe5fa87`), live auf `kopfkinok3.github.io/usdseal-inspector`
**Generiert:** Audit-Reports vom 2026-05-05 21:23–21:34 UTC

---

## 1. Test-Pool

| # | File | Größe | Trust | Brwsr |
|---|---|---|---|---|
| 1 | `Frankfurt_Varianten_TK_271125_01.usdz` | 39.0 MB | unsigniert | Chrome |
| 2 | `Vitra_ID_Demo_TK_201125_01.usdz` | 17.8 MB | unsigniert | Chrome |
| 3 | `RENZ_Showtime_Demo.usdz` | 25.1 MB | unsigniert | Chrome |
| 4 | `AR-Wohnzimmer-_12_01_2022.usdz` | 14.9 MB | unsigniert | Chrome |
| 5 | `SalmonPastaWithInfo.usdz` | 5.0 MB | unsigniert | Chrome |
| 6 | `DIEGOsat_TK_280426_01.usdz` | 26.3 MB | **signiert** (`visales-2026-04-63e7`) | Safari + Chrome |

**Bestätigung:** Alle 6 Files laufen auf iPhone in AR Quick Look einwandfrei.

---

## 2. Findings-Matrix

| File | 🔴 Fehler | 🟠 Warnungen | 🔵 Hinweise |
|---|---|---|---|
| Frankfurt | DEFAULT_PRIM_MISSING, NESTED_USDZ | FILE_SIZE_LIMIT, METERS_PER_UNIT_MISSING | NPOT, MANIFEST_MISSING, MANY_TEXTURES |
| Vitra | DEFAULT_PRIM_MISSING | METERS_PER_UNIT_MISSING | MANIFEST_MISSING, MANY_TEXTURES |
| RENZ | DEFAULT_PRIM_MISSING | FILE_SIZE_LIMIT, METERS_PER_UNIT_MISSING | MANIFEST_MISSING |
| AR-Wohnzimmer | DEFAULT_PRIM_MISSING | METERS_PER_UNIT_MISSING | MANIFEST_MISSING |
| SalmonPasta | DEFAULT_PRIM_MISSING | METERS_PER_UNIT_MISSING | MANIFEST_MISSING |
| DIEGOsat | DEFAULT_PRIM_MISSING | FILE_SIZE_LIMIT, METERS_PER_UNIT_MISSING | (keine — manifest ist da, kein MANIFEST_MISSING-Hinweis) |

---

## 3. Severity-Verdikt — pro Regel

| Regel | Trefferquote | Apple-Realität | aktuelle Severity | Sollte sein | Begründung |
|---|---|---|---|---|---|
| `STRUCTURE_DEFAULT_PRIM_MISSING` | **6/6** (100%) | läuft überall | 🔴 Fehler | 🟠 Warnung | Apple fällt auf "first prim" zurück — universelles Verhalten, kein Hard-Fail |
| `STRUCTURE_NESTED_USDZ` | 1/6 (Frankfurt) | läuft trotzdem | 🔴 Fehler | 🟠 Warnung | Nested USDZ in viSales-Kunden-Workflow vorhanden, Apple toleriert |
| `SCALE_METERS_PER_UNIT_MISSING` | 6/6 (100%) | läuft (Default 0.01) | 🟠 Warnung | 🟠 Warnung ✅ | Default kann zu Skalierungs-Surprise führen — Severity korrekt |
| `STRUCTURE_FILE_SIZE_LIMIT` | 3/6 (Frankfurt 39, RENZ 25.1, DIEGOsat 26.3) | läuft, lädt langsam | 🟠 Warnung | 🟠 Warnung ✅ | Apple-Empfehlung 25 MB ist soft limit |
| `TEXTURE_NPOT` | 1/6 (Frankfurt) | läuft | 🔵 Hinweis | 🔵 Hinweis ✅ | Best-Practice-Verstoß ohne sichtbaren Effekt |
| `MANIFEST_MISSING` | 5/6 (alle unsignierten) | irrelevant für AR | 🔵 Hinweis | 🔵 Hinweis ✅ | USDseal-spezifischer Hint |
| `PERFORMANCE_MANY_TEXTURES` | 2/6 (Frankfurt 78, Vitra 52) | läuft auf älteren iPhones langsam | 🔵 Hinweis | 🔵 Hinweis ✅ | Performance-Hint korrekt |

**Kern-Verdikt:**
- **2 Regeln müssen Severity runter** (DEFAULT_PRIM_MISSING und NESTED_USDZ)
- **Alle anderen Severities sind korrekt**

---

## 4. Texture-Format-Reality-Check

| Format | Vorkommen in Test-Pool | Use-Case | v0.25.4-Action |
|---|---|---|---|
| PNG | 6/6 | Standard | bereits voll abgedeckt ✅ |
| JPG/JPEG | 5/6 | Standard | bereits voll abgedeckt ✅ |
| **AVIF** | 1/6 (Frankfurt — 15 Stück, eine 4.1 MB!) | **realer viSales-Kunden-Use-Case** | **Magic-Bytes-Reader + Native-Preview** |
| HEIC | 0/6 | kein Use-Case | verschoben (Backlog) |
| KTX2 | 0/6 | kein Use-Case | verschoben (Backlog) |
| TIFF | 0/6 | kein Use-Case | verschoben (Backlog) |
| ASTC | 0/6 | kein Use-Case | verschoben (Backlog) |

**Konsequenz:** v0.25.4 fokussiert auf AVIF (real). HEIC/KTX2/TIFF/ASTC bleiben Spec-Vollständigkeit ohne dringenden Praxis-Druck → Backlog.

---

## 5. Cross-Browser-Befund (PDF-Generator)

**Test:** DIEGOsat in beiden Browsern getestet, Inhalte verglichen.

| Aspekt | Chrome | Safari | Match? |
|---|---|---|---|
| PDF-Inhalt (Findings, Counter, Provenance) | ✓ | ✓ | ✅ identisch |
| Output-Mechanismus | Direct-Download | Öffnet Tab, User muss "Drucken → PDF" | ❌ divergiert |

**Diagnose:** jsPDF-Code in v0.23 nutzt vermutlich `doc.save()`. Chrome interpretiert als Download. Safari öffnet Tab mit `data:application/pdf;base64,...` — User-Activation-Click reicht nicht für Auto-Download.

**Beweis:** Safari-User hatte beim ersten Versuch nur Seite 1 gesehen (Embed-Vorschau, nicht gespeichert). HTML-Reports vom Safari-Versuch sind 0 Bytes.

→ **Polish-Bug, gehört in v0.25.4.1.**

---

## 6. Weitere UX-Befunde aus dem Sweep

| # | Bug | Severity | Sprint |
|---|---|---|---|
| 1 | PDF-Header zeigt `v0.25` statt aktueller Version (`v0.25.3`) — hardcoded statt aus Versions-Badge gezogen | low | v0.25.4.1 |
| 2 | Safari-PDF-Button öffnet HTML-Tab statt Direct-Download | medium | v0.25.4.1 |
| 3 | Cache-Counter zeigt 1 obwohl 6 Files getestet — UX-irreführend (zählt nur Manifest-IDs, was korrekt aber nicht offensichtlich ist) | low | v0.25.4.1 |

---

## 7. Test-Pool-Erweiterung empfohlen

Diese 6 Real-World-Files sollten in den Headless-Test-Pool wandern als permanenter Severity-Regression-Test:

```
~/Documents/Claude/USDseal/usdz/review-pool/
├── Frankfurt_Varianten_TK_271125_01.usdz
├── Vitra_ID_Demo_TK_201125_01.usdz
├── RENZ_Showtime_Demo.usdz
├── AR-Wohnzimmer-_12_01_2022.usdz
├── SalmonPastaWithInfo.usdz
└── DIEGOsat_TK_280426_01.usdz
```

**Erwartungs-Profil pro File:** State, expected Findings (mit korrigierter Severity), Texture-Format-Mix. Wird beim v0.25.4-Sprint zusammen mit Code-Anpassung aktualisiert.

---

## 8. Strategische Konsequenzen für v0.25.4

1. **Severity-Recal ist Hauptanteil** (validated 6/6 — universelle Krise)
2. **AVIF-Detection als Bonus** (1/6 hat 15× — realer Use-Case)
3. **HEIC/KTX2/TIFF/ASTC verschoben** (0/6 — kein Use-Case)
4. **Polish-Bugs separat** als v0.25.4.1 (PDF-Header, Cross-Browser-PDF, Cache-UX)
5. **Trust-Layer ist OK** (DIEGOsat zeigt Provenance-Timeline + grünes "Signiert & versiegelt"-Banner)

---

**Ende Real-World-Test-Sweep 2026-05-05.** Wird vom v0.25.4-Briefing als Diagnose-Quelle referenziert.
