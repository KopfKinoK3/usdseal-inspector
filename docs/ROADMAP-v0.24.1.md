# Roadmap v0.24.1 — Multi-File Drop & Texture-Status-Refinement

**Status:** ✅ COMPLETED · released 2026-05-03 (Tag `v0.24.1` online auf GitHub, Commit `67fe5419`)
**Story-Slot:** *"Multi-Asset im Blick"* — Patch nach v0.24, vor v0.25
**Ziel (erfüllt):** Drei Mini-Themen in einem Patch-Sprint sauber durchgezogen.
**Verifikation:** DIEGOsat-Pair Multi-Drop → ↻-Card sichtbar. DIEGOsat_master.usdz: 3× Diffuse + 1× Normal. Headless-Pool 7/7 PASS. tests/headless-pool-test-results.md mit neuen manifest_ids aktualisiert.
**Geliefert mit:**
- ADR-18 (Multi-Drop-Layout: gestapelt vertikal)
- ADR-19 (Texture-Status: used / unused / unknown)
- ADR-20 *entfallen* — Phase 5.0-Verifikation zeigte: Channel-Parser war schon type-agnostisch, `normal3f inputs:normal.connect` wurde korrekt erkannt
- Plus Diagnose-Fix während Sprint: `detectCrossRefsInSession` brauchte Path B (derived→master via `parent_manifest_id`), weil neuer Master-USDZ leeres `lineage:{}` hat — kein Scope-Creep, sauber gefixt

**Aufwand-Schätzung:** 1.5–2.5 Tage geplant, 1.5 Tage tatsächlich (Channel-Parser-Erweiterung entfallen).

**Cross-Sync-Hinweis an CLI-Plan-Chat (zur Akte):** Master-`lineage:{}` ist neu (alter Master hatte `lineage.role="master"` mit `import_history[]`). Inspector funktioniert via Path B, aber Re-Import-↻-Topology ist nicht mehr im Test-Pool getestet. Variante A (gewollt) oder B (Regression) — Antwort vom CLI-Plan-Chat steht aus.

> Patch-Release nach v0.24 (Texture Modal + Channel Detection). Master-Übersicht in `../ROADMAP.md`.

---

## 1. Scope

### 1.1 Multi-File-Drop

User kann mehrere USDZs gleichzeitig in die Drop-Zone ziehen. Inspector zeigt die Manifeste **gestapelt vertikal** (gemäß ROADMAP-v0.22.2 §7.2 ADR-3) — jede USDZ als eigenes Mini-Dashboard. Cross-Reference-Linien (↻) erscheinen zwischen Dashboards, wenn ein Manifest auf ein anderes verweist (master ↔ derived via `parent_manifest_id` / `import_history`).

**UI-Pattern:**
- Drop-Zone akzeptiert mehrere Files via `e.dataTransfer.files` (heute: einzelner File)
- Pro USDZ ein Mini-Dashboard (compact-Variante des Hauptviews): Trust-Status-Banner + Asset-Inventory + Lineage-Karte
- Cross-Reference-↻-Cards zwischen Dashboards mit Pfad-Liste (wie heute in Single-View)
- Cache-Logik aus v0.22.2 wird wiederverwendet (localStorage-Spuren) — Multi-Drop ist **direkter Cross-Check ohne Cache**

**Edge-Cases:**
- 1 File → wie bisher (Single-View)
- 2+ Files → Multi-Dashboard-Layout
- Mismatch in einem File → Banner rot, andere Dashboards unverändert

### 1.2 Texture-Status-Refinement: *unused* vs *unknown*

Aktuell rendert v0.24 für unreferenzierte Texturen einen grauen *"unknown"*-Badge. Das ist semantisch ungenau — es vermischt zwei Fälle:

| Status | Bedeutung | Heutiger Render | v0.24.1 Render |
|---|---|---|---|
| `used` | Texture wird von Material referenziert, Channel erkannt | Channel-Badge (Diffuse/Normal/...) | unverändert |
| `unused` | Texture liegt im ZIP, **kein Material referenziert sie** | "unknown" (grau) | **"unused" (gelb-grau, Hint-Style)** |
| `unknown` | Texture **wird referenziert**, aber unter Alias, den Inspector nicht kennt | "unknown" (grau) | **"unknown" (rot-grau, Bug-Style)** — echte Alias-Lücke |

**Erkennungs-Logik:**
- Beim USDA-Parse alle `asset inputs:file = @...@`-Verweise sammeln (Texture-File-Set)
- Beim USDA-Parse alle `inputs:*.connect = .../Tex.outputs:rgb`-Verweise sammeln (Channel-Map)
- Pro Texture im ZIP:
  - Wenn in Channel-Map → `used` mit Channel
  - Wenn im Texture-File-Set, aber nicht in Channel-Map → `unused` (orphaned)
  - Wenn weder noch → `unused` (im ZIP, aber gar nicht referenziert)

### 1.3 Test-Asset-Sync vom CLI-Plan-Chat

CLI-Plan-Chat hat am 2026-05-03 die DIEGOsat-Files erneuert. Cross-Sync-Inhalt:

**Neue manifest_ids:**
| File | Alt | Neu |
|---|---|---|
| DIEGOsat_master.usdz | visales-2026-05-fc1e | **visales-2026-05-bbeb** |
| DIEGOsat_master_marketing.usdz | visales-derived-c8c4 | **visales-derived-f555** |
| DIEGOsat_master_CAD_marketing.usdz | — | **visales-derived-f26a** |
| DIEGOsat_master_NDA.usdz | — | **visales-derived-95c0** |

**Neuer hull.usda SHA-256:** `7ea5db7b...737a` → `a82ce509...2794`

**Neue Material-Bindings im hull.usda:**

```
def Shader "PBRShader" {
    color3f inputs:diffuseColor.connect = .../BaseColorTex.outputs:rgb
    normal3f inputs:normal.connect = .../NormalTex.outputs:rgb     ← NEU, normal3f-Type
    ...
}
def Shader "NormalTex" {
    asset inputs:file = @hull/textures/normal.png@
    token inputs:sourceColorSpace = "raw"
    float3 outputs:rgb
}
```

**Schema unverändert** — kein spec_version-Bump, kein neuer renderForSpecVersion-Pfad.

**Inspector-Erwartung ändert sich:**
- Vorher: 3× Diffuse + 1× unknown (normal.png ohne Material-Binding)
- Nachher: 3× Diffuse + 1× Normal (alle 4 Texturen referenziert)

**⚠ Verifikations-Risiko:** v0.24-Channel-Parser wurde gegen `color3f`-Patterns gebaut (Diffuse, Emissive). Wenn der Regex strikt auf `color3f inputs:*.connect` matcht, übersieht er `normal3f inputs:normal.connect` → Inspector rendert weiterhin "unknown" trotz korrektem USDA. **Phase 5.0 verifiziert das vor allen Änderungen.**

---

## 2. Externe Quellen

| Komponente              | Status                       | Bemerkung                                                     |
|-------------------------|------------------------------|---------------------------------------------------------------|
| JSZip / jsPDF           | bereits eingebunden          | Reicht.                                                       |
| **Keine neuen Deps**    |                              | Multi-Drop ist DOM, Status-Refinement ist Parser-Logik.       |

---

## 3. Architektur-Optionen

### 3.1 Multi-Drop-Layout

Plan-Chat-Entscheidung in ADR-3 v0.22.2 (gestapelt vertikal als Erst-Build) gilt weiter. **Side-by-Side-Variante** in v0.25 oder v0.26 wenn UX-Bandbreite frei.

### 3.2 Channel-Parser-Erweiterung

**Option A — Type-tolerant matchen (Empfehlung)**

Regex erweitern: matcht `color3f`, `normal3f`, `float`, `float3`, `vector3f`, `point3f` als Input-Type-Präfix. Pattern wäre statt `color3f inputs:*.connect = ...` etwa `(?:color3f|normal3f|float\d?|vector3f|point3f)\s+inputs:(\w+)\.connect`.

**Pro:** Robust gegen alle USDA-Type-Varianten, future-proof.
**Contra:** Regex wird länger, Test-Coverage größer.

**Option B — Type-agnostisch matchen**

Regex matcht **alle** Input-Type-Präfixe (greedy), prüft Inputs nur über den `:connect`-Suffix.

**Pro:** Einfachster Code, unaufwendig.
**Contra:** Könnte versehentlich auch USDA-Konstrukte matchen, die kein Material-Input sind. Nicht selektiv genug.

**Empfehlung:** **Option A**. Whitelist der bekannten USDA-Input-Types ist sicherer und selbstdokumentierend.

---

## 4. Vorbedingungen

| # | Vorbedingung                                                       | Status |
|---|--------------------------------------------------------------------|--------|
| 1 | Inspector v0.24 stabil released                                    | ✓ — Tag online seit 2026-05-03 |
| 2 | Neue DIEGOsat-Files im review-pool                                 | ✓ — verifiziert 2026-05-03 (manifest_id `visales-2026-05-bbeb`, hull.usda mit NormalTex) |
| 3 | Multi-Drop-UI-Pattern entschieden                                  | ✓ — ADR-3 aus v0.22.2: gestapelt vertikal |
| 4 | Texture-Status-Kategorien entschieden                              | ✓ — used / unused / unknown (siehe §1.2) |

**4 von 4 grün — startklar für Build-Chat.**

---

## 5. Phasen-Schätzung

| Phase                                | Dauer       | Was passiert                                                       |
|--------------------------------------|-------------|--------------------------------------------------------------------|
| **5.0 Verifikation v0.24-Stand gegen neue Test-Assets** | 0.25 Tag | Headless-Pool-Test gegen neue DIEGOsat-Files. Ergebnis bestimmt Phase 5.4 (Channel-Parser-Erweiterung ja/nein). Wenn `normal3f` als "unknown" gerendert wird → 5.4 ist Pflicht. Wenn schon korrekt erkannt → 5.4 entfällt, Sprint wird kürzer. |
| **5.1 Drop-Zone Multi-File-Akzeptanz** | 0.25 Tag    | `e.dataTransfer.files`-Loop, FileList-Iteration, je File ein USDZ-Parse. |
| **5.2 Mini-Dashboard-Render**        | 0.5 Tag     | Compact-Variante des Hauptviews: kleinerer Header, kompaktere Tabellen. CSS-Reuse aus Single-View. |
| **5.3 Cross-Reference-↻-Cards**      | 0.25 Tag    | Cache-Logik aus v0.22.2 wiederverwenden, ↻-Cards zwischen Mini-Dashboards rendern. |
| **5.4 Channel-Parser-Erweiterung** *(konditional)* | 0.25 Tag | Nur wenn Phase 5.0 zeigt, dass `normal3f` nicht erkannt wird. Type-tolerante Regex (Option A). |
| **5.5 Texture-Status-Refinement**    | 0.25 Tag    | `used` / `unused` / `unknown`-Logik in Channel-Map. UI-Badges entsprechend (gelb-grau / rot-grau / Channel-Farbe). |
| **5.6 Test gegen review-pool/**      | 0.25 Tag    | Multi-Drop mit DIEGOsat-Master + DIEGOsat-Tochter → ↻-Card sichtbar. Channel-Erkennung: 3× Diffuse + 1× Normal verifiziert. |
| **5.7 Headless-Pool-Regression**     | 0.1 Tag     | 7/7 PASS bleibt, mit aktualisierten Erwartungen pro File. |
| **5.8 Test-Erwartungen-Update**      | 0.25 Tag    | tests/headless-pool-test-results.md mit neuen manifest_ids und Channel-Erwartungen aktualisieren. |
| **5.9 README + CHANGELOG-Update**    | 0.25 Tag    | v0.24.1-Eintrag mit drei Themen (Multi-Drop, Status-Refinement, Test-Asset-Sync). |
| **5.10 Snapshot + Tag**              | 0.25 Tag    | `archive/snapshots/v0.24.1-snapshot.html`, Tag, Push. |

**Total: 1.5–2.5 Tage** je nach Phase 5.4-Entscheidung.

---

## 6. Strategischer Hebel

v0.24.1 ist Patch — kein eigener Konferenz-Slide. Aber drei stille Hebel:

1. **Multi-Drop = Asset-Pipeline-Demo.** B2B-Kunden mit Asset-Bibliotheken (mehrere USDZs aus einer Pipeline) können jetzt Cross-Reference-Beziehungen direkt sehen. Beispiel: Master + drei Töchter (CAD, NDA, Marketing) auf einen Klick — sofort sichtbar, welche von welchem importiert.
2. **Status-Refinement = Asset-Hygiene-Hinweis.** *"unused"* (gelb) sagt dem Designer: *"diese Texture ist im ZIP, aber niemand benutzt sie — kannst du löschen, spart Bytes"*. Das ist konkrete UX-Verbesserung mit B2B-Mehrwert.
3. **Cross-Repo-Sync mit CLI etabliert.** Erste vollständige Cross-Sync-Iteration zwischen den zwei Plan-Chats. Pattern hat funktioniert: CLI hat Test-Asset erneuert, Inspector zieht in Patch-Sprint nach. Dokumentiert für künftige Schema-Bumps oder größere CLI-Änderungen.

---

## 7. Konkrete Pre-v0.24.1-Steps

### 7.1 Phase 5.0 zuerst (10 Minuten)

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
python3 tests/headless_validator.py ../usdz/review-pool/
```

Pro File checken:
- DIEGOsat_master.usdz: 4 Texturen, davon **erwartet 3× Diffuse + 1× Normal** (statt 3× Diffuse + 1× unknown wie in v0.24)
- Andere Pool-Files: 7/7 PASS bleiben

**Wenn Inspector "1× unknown" zeigt:** Phase 5.4 ist Pflicht (Channel-Parser muss `normal3f` lernen).
**Wenn Inspector "1× Normal" zeigt:** Glück gehabt, Regex matcht eh schon type-agnostisch. Phase 5.4 entfällt.

### 7.2 Cache-Schema unverändert (5 Minuten)

Multi-Drop nutzt die v0.22.2-localStorage-Cache-Struktur unverändert (Cache-Key `usdseal-inspector.cache.v1`). Kein Schema-Bump.

### 7.3 Test-Asset-Erwartungen pro File dokumentieren (15 Minuten)

Vor Build-Start in `tests/headless-pool-test-results.md` (oder einer Spec-Datei) festhalten, was pro File erwartet ist:

```
DIEGOsat_master.usdz
  → 3× Diffuse, 1× Normal, 0× unused, 0× unknown
DIEGOsat_master_marketing.usdz
  → ?
DIEGOsat_master_CAD_marketing.usdz
  → ?
DIEGOsat_master_NDA.usdz
  → ?
```

Die Tochter-Files haben evtl. weniger Texturen (je nach Klassifikation). Phase 5.0 deckt das automatisch auf.

---

## 8. Decision-Log-Template

```markdown
### ADR-18 Multi-Drop-Layout: gestapelt vertikal — <Datum>

**Kontext:** Multi-Drop-UI-Pattern aus v0.22.2-ADR-3 wird umgesetzt.
**Entscheidung:** Mini-Dashboards untereinander, Cross-Reference-↻-Cards zwischen ihnen. Side-by-Side erst in v0.25 oder v0.26.
**Konsequenz:** Konsistent mit Single-View, keine neuen UI-Patterns. Skaliert auf beliebig viele Drops.

### ADR-19 Texture-Status: drei Kategorien (used / unused / unknown) — <Datum>

**Kontext:** v0.24 hat alle nicht-erkannten Texturen als "unknown" gerendert. Das vermischt orphaned Texturen (im ZIP, nicht referenziert) mit Alias-Lücken (referenziert, aber unter unbekanntem Input-Namen).
**Entscheidung:** Drei Kategorien:
- `used` (Channel-Badge wie heute)
- `unused` (gelb-grau, "Hint": Texture orphaned)
- `unknown` (rot-grau, "Bug": Alias-Lücke, Inspector kann Channel nicht erkennen)
**Konsequenz:** Klarere Befund-Semantik. *"unused"* als Asset-Hygiene-Hinweis nutzbar, *"unknown"* als Inspector-Verbesserungs-Trigger (Alias-Erweiterung in zukünftigen Sprints).

### ADR-20 Channel-Parser-Type-Toleranz — <Datum> *(konditional)*

**Kontext:** USDA-Inputs können verschiedene Type-Präfixe haben (color3f, normal3f, float, etc.). v0.24-Parser war gegen color3f gebaut.
**Entscheidung:** Type-tolerante Regex mit Whitelist (color3f, normal3f, float, float3, vector3f, point3f) — siehe §3.2 Option A.
**Konsequenz:** Robust gegen UsdPreviewSurface-Input-Type-Varianten. Test-Coverage über DIEGOsat (Diffuse=color3f, Normal=normal3f).
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger-Briefing: `ROADMAP-v0.24.md` (Texture Modal + Channel Detection)
- Cross-Sync-Quelle: CLI-Plan-Chat 2026-05-03 (Maid Evelyn → Maid Evelyn)

### Externe Specs

- [UsdPreviewSurface Spec — Material-Inputs](https://openusd.org/release/spec_usdpreviewsurface.html#inputs)
- [UsdUVTexture — sourceColorSpace](https://openusd.org/release/spec_usdpreviewsurface.html#texture-reader)

### Inspector-Repo

- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)

---

**Ende v0.24.1-Roadmap.** Nach Build: Snapshot, Tag `v0.24.1`, Push. Plan-Chat schreibt dann `docs/ROADMAP-v0.25.md` für Geometrie-Stats + 3D-Preview.
