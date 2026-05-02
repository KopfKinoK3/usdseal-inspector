# Roadmap v0.22.2 — Re-Import-Detection (Patch)

**Status:** ✅ COMPLETED · released 2026-05-02 (Tag `v0.22.2` online auf GitHub)
**Story-Slot:** *"Sieht jetzt auch die Schleifen"* — Patch-Release
**Ziel (erfüllt):** Re-Import-Zyklen sichtbar — der ↻-Marker via localStorage-Cache.
**Verifikation:** Demo-Sequenz ↻-Card grün, Cache-Clear grün, Headless-Pool 7/7 PASS.
**Geliefert mit Plan-Chat-Cuts (ADR-PC3):** Multi-Drop verschoben nach v0.22.3, Übergangs-Toleranz-Abräumen pending CLI-SP-11.

> Patch nach v0.22.1 (Polish & Polyglot, ✅ done mit Headless-Pool 7/7).
> Schließt eine v0.21-Lücke. Master-Übersicht in `../ROADMAP.md`.

---

## 1. Scope — was v0.22.2 inhaltlich bedeutet

Inspector v0.21 zeigt Lineage als **Single-View** — was im aktuell geladenen Manifest steht. v0.22.2 erweitert das um zwei Cross-Manifest-Mechanismen:

### 1.1 localStorage-Cache der zuletzt gesehenen Manifeste

Wenn ein USDZ geladen wird, schreibt der Inspector eine kompakte Spur ins `localStorage`:

```json
{
  "manifest_id": "visales-2026-05-fc1e",
  "sha256": "3803f97f...",
  "role": "master",
  "import_history_ids": ["visales-derived-c8c4"],   // master only
  "parent_manifest_id": null,                        // derived only
  "filename": "DIEGOsat_master.usdz",
  "seen_at": "2026-05-02T08:45:00Z"
}
```

Cache-Größe: **letzte 20 Manifeste**. Cache-Key: `usdseal-inspector.cache.v1`. Älteste werden FIFO ersetzt. User kann den Cache jederzeit über einen Button in der Topbar leeren.

**Privacy-Versprechen bleibt unverändert** — `localStorage` ist lokal, keine Daten verlassen den Rechner.

### 1.2 Re-Import-↻-Detection

Beim Render eines Manifests prüft der Inspector den Cache auf umgekehrte Beziehungen:

- **Master geladen:** für jeden `import_history[].imported_from_manifest_id` → schau im Cache, ob ein Manifest mit diesem `manifest_id` existiert UND dessen `parent_manifest_id` gleich dem aktuellen Master ist.
- **Derived geladen:** schau im Cache, ob ein Master mit `import_history[]` auf das aktuelle Derived existiert.

Wenn ja → ↻-Card mit Crossref-Daten erscheint:

> ↻ **Re-Import erkannt** — Master `visales-2026-05-fc1e` importiert `hull/*` aus seiner Tochter `visales-derived-c8c4` (gesehen am 2026-05-01 14:32). Bewusster Workflow, kein Schema-Bruch.

### 1.3 ~~Optionaler Multi-File-Drop~~ — **VERSCHOBEN nach v0.22.3** (ADR-PC3)

Multi-File-Drop ist UI-Aufwand mit gestapelten Mini-Dashboards. Plan-Chat-Entscheidung 2026-05-02: kompakter v0.22.2-Sprint mit Single-Drop als Kern, Multi-Drop bekommt eigenen Sprint v0.22.3, sobald UI-Bandbreite frei ist.

Original-Scope (für späteren v0.22.3-Sprint dokumentiert):
> User kann mehrere USDZs gleichzeitig in die Drop-Zone ziehen. Inspector zeigt die Manifeste **nebeneinander** (oder gestaffelt) und macht den Cross-Check direkt — ohne auf den Cache angewiesen zu sein. UI-Pattern: gestapelte Cards, jede USDZ ein eigenes Mini-Dashboard. Cross-Reference-Linien werden als ↻-Cards zwischen den Dashboards gerendert.

### 1.4 Übergangs-Toleranz für `0.1`-mit-lineage abräumen — **KONDITIONAL** (ADR-PC3)

ADR-4 in v0.21 hat Bestandsfixtures (DIEGOsat) toleriert, die noch `spec_version: "0.1"` mit `lineage`-Block tragen. Plan-Chat-Entscheidung 2026-05-02: dieser Punkt feuert nur, wenn CLI-SP-11 (`usdseal migrate`) **vor v0.22.2-Tag bestätigt durch ist**. Sonst verschoben nach v0.22.3 oder v0.22.4.

**Wenn CLI-SP-11 durch ist** — Übergangs-Toleranz entfernen:
- `0.1`-Manifest **ohne** `lineage`: weiterhin gerendert wie bisher.
- `0.1`-Manifest **mit** `lineage`: jetzt **gelber Banner** *"Manifest stammt aus pre-bump CLI v0.2 — bitte `usdseal migrate` ausführen"* statt grauem Hint. Render trotzdem best-effort.
- `0.2`-Manifest: vollständige Behandlung wie in v0.21 etabliert.

**Wenn CLI-SP-11 NICHT durch ist** — Status quo der Übergangs-Toleranz beibehalten, in v0.22.3 oder v0.22.4 erneut aufgreifen.

**Vorbedingung-Check:** Vor Build-Start im CLI-Chat fragen *"Ist `usdseal migrate` (SP-11) durch? DIEGOsat-Fixtures auf 0.2 migriert?"*. Antwort entscheidet, ob §1.4 in diesem Sprint mitläuft.

---

## 2. Externe Quellen

| Komponente              | Status                       | Bemerkung                                                  |
|-------------------------|------------------------------|------------------------------------------------------------|
| JSZip                   | bereits eingebunden          | Multi-Drop = mehrere parallele Loads, keine neuen Libs.    |
| `localStorage` API      | nativ                        | Kein Polyfill, kein Wrapper.                               |
| Manifest-Schema         | unverändert                  | Inspector ist Read-Only — kein Schema-Update.              |

---

## 3. Architektur-Optionen

### Option A — Pure-JS Cache + Render-Erweiterung (Empfehlung)

`localStorage` direkt, Cache als Array unter einem Key. Cross-Check ist ein einfacher Loop in der Render-Funktion. Multi-Drop wird durch Schleife über `e.dataTransfer.files` gelöst, mit visueller Stapelung der Mini-Dashboards.

**Pro:** Konsistent mit v0.21-Architektur, keine neuen Dependencies, klein.
**Contra:** Cache-Code muss sauber abgeschottet werden (Schema-Migration bei Cache-Format-Änderungen).

### Option B — IndexedDB statt localStorage

Mehr Speicher, strukturierte Queries. Overkill für 20 Einträge.

### Option C — Cache als optional in URL-Hash

Persistenz ohne `localStorage`. Cache muss nach jedem Reload neu geladen werden. Verliert den Punkt.

### Empfehlung

**Option A.** `localStorage` ist die einfachste Antwort, die das Problem löst.

---

## 4. Vorbedingungen — was vor v0.22.2-Start geklärt sein muss

| # | Vorbedingung                                                       | Status |
|---|--------------------------------------------------------------------|--------|
| 1 | Inspector v0.21 lokal fertig                                        | ✓ — 2026-05-01 |
| 2 | CLI-SP-11 (`usdseal migrate`) durch — Bestandsfixtures auf 0.2     | ☐ — abhängig vom CLI-Build-Stand |
| 3 | Cache-Key + Schema-Version entschieden                              | ✓ — `usdseal-inspector.cache.v1`, max 20 Einträge |
| 4 | UI-Pattern für Multi-Drop entschieden                              | ☐ — Vorschlag: gestaffelte Cards |
| 5 | Cache-Clear-Button entschieden                                     | ✓ — Topbar, neben Version-Badge |
| 6 | Test-Asset-Paar mit Re-Import-Topologie verfügbar                  | ✓ — DIEGOsat_master + DIEGOsat_master_marketing |

**4 von 6 grün — eine harte (CLI-SP-11) und eine weiche (Multi-Drop-UI) Vorbedingung offen.**

---

## 5. Realistische Phasen-Schätzung

| Phase                                       | Dauer       | Was passiert                                                       |
|---------------------------------------------|-------------|--------------------------------------------------------------------|
| **5.1 Cache-Layer**                         | 0.5 Tag     | `cacheManifest(...)`, `getCachedManifests()`, `clearCache()`. Cache-Key, FIFO-Logik, Schema-Version. |
| **5.2 Re-Import-Detection-Logik**          | 0.5 Tag     | `detectReImports(currentManifest, cache) → [crossrefs]`. Beidseitige Suche (master ↔ derived). |
| **5.3 ↻-Card UI**                           | 0.5 Tag     | Card-Design, integriert in Lineage-Sektion. Klartext mit Cache-Timestamp. |
| **5.4 Multi-File-Drop UI**                  | 0.5–1 Tag   | Drop-Zone akzeptiert mehrere Files, gestaffelte Mini-Dashboards, Cross-Reference-Visualisierung. |
| **5.5 Übergangs-Toleranz abräumen**         | 0.25 Tag    | Hint-Banner für `0.1`-mit-lineage von grau auf gelb umstellen. Code-Pfad in `compatCheck`. |
| **5.6 Cache-Clear-Button + Topbar**         | 0.25 Tag    | Button in Topbar, Confirm-Dialog, Cache-Counter (*"X Manifeste im Cache"*). |
| **5.7 Test gegen DIEGOsat-Paar**            | 0.25 Tag    | Beide USDZs nacheinander → ↻ erscheint beim zweiten. Multi-Drop → ↻ direkt. |
| **5.8 README + CHANGELOG + COMPATIBILITY**  | 0.25 Tag    | v0.22.2-Eintrag, Übergangs-Toleranz als entfernt markieren, Cache-Privacy-Hinweis. |

**Total: 1.5–2.5 Tage Build-Zeit.** Klein und fokussiert.

---

## 6. Strategischer Hebel

v0.22.2 ist Patch — kein eigener Konferenz-Slide. Aber drei stille Hebel:

1. **Demo-Robustheit.** v0.21-Konferenz-Demo zeigte ↻ noch nicht. Mit v0.22.2 kann der Re-Import-Aha-Moment live demonstriert werden.
2. **CLI-Sync.** v0.22.2-Tag fixiert das Ende der Übergangs-Toleranz. Ab hier ist die Schema-Disziplin durchgesetzt — wichtige Hygiene-Marke.
3. **Privacy-Story als Differentiator.** localStorage-Cache mit klarem Clear-Button + Privacy-Versprechen ist ein leiser, aber starker Punkt im B2B-Verkauf gegen Cloud-First-Tools.

---

## 7. Konkrete Pre-v0.22.2-Steps

### 7.1 Cache-Schema-Version festlegen (5 Minuten)

Cache-Key: `usdseal-inspector.cache.v1` — falls Schema sich später ändert, neuer Key (`v2`), alter wird beim ersten Read migriert oder gelöscht.

### 7.2 Multi-Drop-UI-Pattern entscheiden (20 Minuten)

Drei Optionen:
- **A) Gestaffelt vertikal** — Mini-Dashboard pro USDZ untereinander. Einfach, aber lange Seite.
- **B) Tabs** — eine Karte aktiv, andere als Tab-Pillen oben. Kompakter, aber Cross-Reference weniger sichtbar.
- **C) Side-by-Side** — bei zwei USDZs nebeneinander, ab drei gestaffelt. Hybrid.

**Vorschlag:** A für Erst-Build, C für Ausbau in v0.22+.

### 7.3 Cache-Clear-Button-Wording (5 Minuten)

*"Cache leeren (X Manifeste)"* mit Confirm-Dialog *"Lokal gespeicherte Manifest-Spuren der letzten Sessions werden gelöscht. Geladene USDZs bleiben unverändert."*

---

## 8. Decision-Log-Template (für v0.22.2-Entscheidungen)

```markdown
### ADR-1 Cache-Backend: localStorage statt IndexedDB — <Datum>

**Kontext:** 20 Einträge, kompakt, kein Query-Bedarf.
**Entscheidung:** localStorage mit JSON-Array.
**Konsequenz:** Trivial einzubauen, keine API-Asymmetrie zwischen Schreiben/Lesen.

### ADR-2 Cache-Größe 20 Einträge, FIFO — <Datum>

**Kontext:** Cache soll Wiedersehen erkennen, nicht permanent lagern.
**Entscheidung:** Max 20 Manifeste, älteste werden FIFO ersetzt.
**Konsequenz:** localStorage-Quota (~5 MB) wird nie ausgeschöpft.

### ADR-3 Multi-Drop-UI: gestaffelt vertikal — <Datum>

**Kontext:** Multi-File-Drop braucht klares Layout.
**Entscheidung:** Mini-Dashboards untereinander, Cross-Reference-↻-Cards zwischen ihnen.
**Konsequenz:** Konsistent mit Single-View, keine neuen UI-Pattern.

### ADR-4 Übergangs-Toleranz beendet ab v0.22.2 — <Datum>

**Kontext:** ADR-4 aus ROADMAP-v0.21 hat 0.1-mit-lineage als Quasi-0.2 toleriert.
**Entscheidung:** Ab v0.22.2 wird der graue Hint zu einem gelben Banner. Render bleibt best-effort, aber Migration wird klar verlangt.
**Konsequenz:** Sauberere Versions-Disziplin. Setzt voraus, dass CLI-SP-11 vorher durch ist.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente
- Master-Roadmap: `../ROADMAP.md`
- Vorgänger-Briefings: `ROADMAP-v0.21.md` (Lineage), `ROADMAP-v0.22.md` (AR-Quick-Look), `ROADMAP-v0.22.1.md` (Polish & Polyglot)
- Nachfolger: `ROADMAP-v0.23.md` (PDF-Audit-Report) — folgt
- Compat-Matrix: `COMPATIBILITY.md`
- Test-Assets: `../usdz/DIEGOsat_master.usdz`, `../usdz/DIEGOsat_master_marketing.usdz`

### Externe Specs
- [MDN — localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [OpenUSD Specification](https://openusd.org/release/index.html)

### Inspector-Repo
- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)

---

**Ende v0.22.2-Roadmap.** Nach Build: ADR-Einträge in CHANGELOG einhängen, Git-Tag setzen (`v0.22.2`). Dann v0.23-Briefing (PDF-Audit-Report) öffnen.
