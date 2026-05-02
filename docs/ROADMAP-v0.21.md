# Roadmap v0.21 — Lineage Visibility & Compatibility

**Status:** ✅ COMPLETED · ausgeliefert gebündelt mit v0.22 (2026-05-01)
**Story-Slot:** *"Sieht jetzt, was die CLI baut"*
**Ziel (erfüllt):** Den Inspector zur vollwertigen Sichtmaschine für die in CLI v0.2 eingeführte Asset-Lineage gemacht.

> **Historisches Briefing** — der Sprint wurde in einem Rutsch mit v0.22
> (AR-Quick-Look-Validator) zusammen gebaut und unter dem v0.22-Tag
> ausgeliefert. Alle Scope-Items aus diesem Briefing sind im
> Inspector-CHANGELOG v0.22 dokumentiert.
>
> Diese Datei bleibt als **Wiedereinstiegs- und Audit-Dokument** erhalten:
> Decision-Records (ADR-1 bis ADR-5), Schema-Strategie und
> Übergangs-Toleranz-Regeln gelten weiterhin als Architektur-Anker für
> Folge-Sprints. Detail-Briefings für die nächsten Sprints
> (v0.22.1, v0.23, …) liegen als eigene `ROADMAP-v0.XX.md` daneben.

---

## 1. Scope — was v0.21 inhaltlich bedeutet

Inspector v0.2 zeigt **State, SHA-256-Verify, USD-Metadaten, Texturen**.
v0.21 ergänzt drei strukturelle Lücken, die mit CLI v0.2 entstanden sind:

### 1.1 Lineage-Panel

CLI v0.2 produziert Manifeste mit asymmetrischer Lineage-Struktur:

- **Master** (`lineage.role = "master"`): zeigt **nach unten**, listet importierte Sub-Assets via `import_history[]` mit `imported_from_manifest_id`, `imported_from_sha256`, `imported_paths[]`, `imported_at`, `actor`.
- **Tochter** (`lineage.role = "derived"`): zeigt **nach oben**, hält `parent_manifest_id`, `parent_sha256`, `exported_classifications[]`, `exporter_tool`, `exported_at`, `actor`.

Inspector v0.2 ignoriert das komplett. v0.21 rendert beide Modi visuell:

- **Lineage-Karte oben** im Manifest-Panel — zwei Zustände je nach `role`.
- **Asset-Liste mit Path-Breakdown** beim Master (welche Pfade stammen aus welchem Eltern-Manifest).
- **Edge-Case Re-Import-Zyklus** — wenn ein Master eine `import_history`-Referenz auf eine Tochter hat, die selbst diesen Master als Eltern-Manifest hat, wird das mit `↻ Re-Import` als **neutrales Label** markiert (kein Warning — bewusster Workflow, vom Maintainer als Feature bestätigt).

### 1.2 Provenance-Timeline

Beide Manifest-Typen haben `provenance_chain[]` als Audit-Trail mit `step` (`sealed` / `merged` / `derived`), `tool` (z. B. `USDseal/0.2.0`), `actor`, `timestamp`, optional `notes`.

Inspector v0.2 zeigt davon nichts — v0.21 rendert eine **chronologische Timeline** unterhalb der Lineage-Karte. Wichtig: **Lineage** sagt *"woher stammen die Bytes"*, **Provenance** sagt *"was wurde damit gemacht"*. Beide zeigen, getrennt.

### 1.3 Compatibility-Matrix

Beide Manifest-Versionen tragen ein Top-Level-Feld `spec_version`. Inspector v0.21 liest es und vergleicht gegen eine interne Whitelist unterstützter Versionen. Bei Mismatch: gelber Hint *"Manifest-Version X.Y, Inspector versteht 0.1–0.2"* statt stilles Brechen.

Plus eine **`COMPATIBILITY.md`** im Repo — dokumentiert die Versions-Matrix für Contributor und Nutzer.

---

## 2. Externe Quellen

Bewusst minimal — kein neuer Lib-Overhead, kein Crypto, kein Server.

| Komponente              | Status                       | Bemerkung                                                            |
|-------------------------|------------------------------|----------------------------------------------------------------------|
| JSZip                   | bereits in v0.2 eingebunden  | Reicht für USDZ-Inhalt-Parsing — keine Erweiterung nötig.            |
| WebCrypto API           | **nicht** in v0.21            | Kommt erst in v0.3 (Ed25519-Verify).                                  |
| D3.js / Mermaid         | **nicht** in v0.21            | Lineage-Visualisierung in v0.21 mit reinem DOM. Lib-Diskussion in v0.4+. |
| Manifest-Schema         | Referenz im CLI-Repo         | Inspector spiegelt die Schema-Felder, kein separates Schema-Loading.  |

---

## 3. Architektur-Optionen

### Option A — Pures DOM-Rendering + versions-spezifische Renderer (Empfehlung)

Lineage-Karte und Provenance-Timeline mit den bestehenden Render-Patterns aus v0.2: Cards, Tabellen, Pillen für Klassifikationen. Keine externen Libraries. **Plus:** Code-Struktur ist `renderForSpecVersion(version, manifest)` mit klar getrennten Render-Pfaden pro Version (siehe §7.1).

**Pro:** Konsistent mit v0.2-Codebase und Warm-Tech-Design-System. Bundle-Size bleibt klein. Versions-Disziplin ab Tag 1 macht Erweiterung auf 0.3 / 0.4 später zur One-Liner-Aufgabe.
**Contra:** Multi-Asset-Graph-Visualisierung wird in v0.4+ unangenehm, aber das ist nicht v0.21-Problem.

### Option B — D3.js / Mermaid

Komplexere Beziehungen als gerichteter Graph. Overkill für 1:N-Fall in v0.21.

### Empfehlung

**Option A.** Lib-Frage erst dann, wenn Cross-Asset-Linking zum Default wird (v0.4+).

---

## 4. Vorbedingungen — was vor v0.21-Start geklärt sein muss

| # | Vorbedingung                                                       | Status |
|---|--------------------------------------------------------------------|--------|
| 1 | Inspector v0.2 läuft live auf GitHub Pages                         | ✓      |
| 2 | CLI v0.2 produziert Manifeste mit `lineage`-Block                  | ✓      |
| 3 | Test-Asset-Paar (Master + Tochter) verfügbar                       | ✓ — `DIEGOsat_master.usdz` + `DIEGOsat_master_marketing.usdz` |
| 4 | Re-Import-Edge-Case dokumentiert und entschieden                   | ✓ — als Feature (Re-Import-Workflow, neutrales Label) |
| 5 | `spec_version`-Whitelist + Versions-Architektur entschieden        | ✓ — `["0.1", "0.2"]` mit Übergangs-Toleranz, siehe §7.1 |
| 6 | Alte HTML-Vorversion aufgeräumt                                     | ✓ — gelöscht 2026-05-01 |

**6 von 6 grün — startklar für Build-Chat.**

---

## 5. Realistische Phasen-Schätzung

| Phase                                        | Dauer       | Was passiert                                                       |
|----------------------------------------------|-------------|--------------------------------------------------------------------|
| **5.1 Lineage-Panel UI**                     | 1–2 Tage    | Render-Logik für `lineage.role`-Switch (master vs. derived). Cards für `import_history[]` und `parent_manifest_id`. Re-Import-Zyklus-Detection mit `↻`-Marker. |
| **5.2 Provenance-Timeline**                  | 0.5–1 Tag   | Chronologische Liste der `provenance_chain[]`-Einträge. Tool-Version-Pille, Timestamp, optional `notes`. |
| **5.3 Compatibility-Check**                  | 0.5 Tag     | `spec_version`-Lesen, Whitelist-Vergleich, Hint-Banner bei Mismatch. |
| **5.4 `COMPATIBILITY.md` schreiben**         | 0.5 Tag     | Tabelle Inspector-Version ↔ unterstützte `spec_version`-Range. README-Cross-Link. |
| **5.5 README + CHANGELOG Update**            | 0.5 Tag     | Roadmap-Sektion erweitern (Cross-Link auf `../ROADMAP.md`). CHANGELOG-Eintrag für v0.21. |
| **5.6 Test gegen DIEGOsat-Asset**            | 0.5 Tag     | Manifeste in den Inspector ziehen, alle drei Modi (Master, Tochter, Re-Import-Zyklus) durchgespielt. Edge-Case-Screenshots für PR-Beschreibung. |
| **5.7 Git-Tag v0.21 + GitHub-Release**       | 0.25 Tag    | Tag setzen, Release-Notes aus CHANGELOG, GitHub-Pages-Deploy verifizieren. |

**Total: 4–5 Tage Build-Zeit.** Eine konzentrierte Woche.

---

## 6. Strategischer Hebel

v0.21 ist klein, aber öffentlich sichtbar. Drei Hebel:

1. **AOUSD-Forum-Update.** Kurzer Beitrag: *"Inspector v0.21 now visualizes asset lineage and provenance — try it with your own USDZ."*
2. **Konferenz-Demo.** Live USDZ reinziehen, Re-Import-Zyklus als visueller Wow-Moment. CLI bleibt im Hintergrund (privat), Inspector trägt die Story.
3. **Contributor-Magnet.** Lineage + Provenance ist abgeschlossene Funktionalität — Anlaufstelle für externe PRs.

---

## 7. Konkrete Pre-v0.21-Steps (jetzt machbar)

### 7.1 `spec_version`-Whitelist & Versions-Architektur (entschieden 2026-05-01)

**Befund:** DIEGOsat-Test-Manifeste tragen `spec_version = "0.1"`, obwohl der `lineage`-Block strukturell ein v0.2-Feature ist.

**CLI-Entscheidung** (ADR §11.14, accepted 2026-05-01):
1. CLI bumpt `spec_version` auf `"0.2"` für jede Schema-relevante Erweiterung (semver-artige Disziplin pre-1.0).
2. Bestandsfixtures (DIEGOsat-Manifeste) werden via `usdseal migrate`-Subcommand auf `"0.2"` gehoben **vor v0.2.0-Tag** (CLI-Action SP-11).
3. CLI verweigert `verify` bei unbekannter `spec_version` mit klarer Fehlermeldung — **kein** Tolerant-Modus.

**Inspector-Konsequenz:**
- Inspector folgt der gleichen Disziplin: **versions-spezifische Renderer**, nicht Toleranz auf Feld-Anwesenheit.
- Code-Pattern: `renderForSpecVersion(version, manifest)` mit klar getrennten Render-Pfaden pro Version.

**Inspector-Whitelist und Übergangsstrategie:**

| Inspector-Version | Whitelist | Renderer-Pfade |
|---|---|---|
| v0.21 (initial) | `["0.1", "0.2"]` | `0.1`: kein Lineage-Panel, kein Provenance-Step `merged`/`derived`. `0.2`: vollständiges Lineage-Panel + Provenance-Timeline. |
| v0.3+ (mit C2PA) | `["0.1", "0.2", "0.3"]` | + `0.3`: zusätzlicher C2PA-Block (siehe CLI v0.3-Roadmap). |

**Übergangs-Toleranz für v0.21 (zeitlich befristet):**

Während CLI-SP-11 noch nicht durch ist (Bestandsfixtures noch auf `"0.1"` mit lineage-Block), behandelt Inspector v0.21 ein `0.1`-Manifest mit `lineage`-Key als **Quasi-`0.2`** und rendert das Lineage-Panel trotzdem. Begleitet von einem grauen Hint *"Manifest stammt aus pre-bump CLI v0.2 — empfohlen: `usdseal migrate` ausführen"*. Diese Übergangs-Logik fällt in Inspector v0.22 weg, sobald die Migrate-Welle durch ist.

**Versions-spezifische Render-Regeln für v0.21:**

| Feld | `spec_version: "0.1"` | `spec_version: "0.2"` |
|---|---|---|
| `lineage`-Block | nicht erwartet (Übergangs-Toleranz: ja, mit Hint) | Pflicht — wenn fehlt: Manifest-Integrity-Warning |
| `provenance_chain[].step ∈ {sealed}` | erwartet | erwartet |
| `provenance_chain[].step ∈ {merged, derived}` | nicht erwartet (Übergangs: tolerieren) | erwartet |
| `import_history[]` (im Master) | nicht erwartet | erwartet wenn `lineage.role = "master"` |

**Cross-Verweis:** Inspector-Compat-Strategie ist explizit gekoppelt an CLI-ADR §11.14. Wenn das CLI später nochmal Schema-Disziplin verfeinert (z. B. PATCH-Bumps für sub-strukturelle Änderungen), zieht Inspector-Roadmap nach.

### 7.2 Test-Asset für Talk-Demos vorbereiten (1 Stunde, optional)

`DIEGOsat`-Asset enthält Re-Import-Zyklus — gut für Edge-Case-Demo. Optional zusätzlich ein **sauberes** Master/Tochter-Paar ohne Zyklus erzeugen, damit Konferenz-Demos die Standard-Geschichte auch zeigen können.

### 7.3 Contributor-Hint im README (15 Minuten)

Im Inspector-README-Roadmap-Block: kurzen Hinweis, dass v0.21 in Arbeit ist mit Link auf diese Datei. Macht den Roadmap-Pfad sichtbar.

---

## 8. Decision-Log-Template (für v0.21-Entscheidungen)

```markdown
### ADR-1 Lineage-Render-Strategie: DOM-only statt D3/Mermaid — <Datum>

**Kontext:** Lineage-Panel braucht Rendering für Master/Tochter/Re-Import.
**Optionen:** Pures DOM / D3.js / Mermaid.js
**Entscheidung:** Pures DOM für v0.21.
**Konsequenz:** Bundle bleibt klein, kein neuer Dep. Multi-Asset-Graph in v0.4+ braucht ggf. Lib-Wechsel.

### ADR-2 Re-Import-Zyklus: Feature, nicht Warning — <Datum>

**Kontext:** Master kann Sub-Assets aus eigener Tochter importieren.
**Entscheidung:** Inspector zeigt `↻ Re-Import` als neutrales Label, kein Warning-Banner.
**Konsequenz:** CLI-Workflow als bewusster Pattern dokumentiert, nicht als Schema-Inkonsistenz.

### ADR-3 Versions-spezifische Renderer statt Toleranz — 2026-05-01

**Kontext:** CLI-ADR §11.14 etabliert spec_version-Bump-Disziplin. Inspector folgt dem.
**Entscheidung:** Code-Pattern `renderForSpecVersion(version, manifest)` mit klar getrennten Render-Pfaden pro Version. Whitelist `["0.1", "0.2"]` ab v0.21.
**Konsequenz:** Saubere Versions-Trennung ab Tag 1. Erweiterung auf 0.3 / 0.4 = neue Render-Funktion + Whitelist-Eintrag, kein Refactoring der Bestandslogik.

### ADR-4 Übergangs-Toleranz für pre-bump 0.1-Manifeste — 2026-05-01

**Kontext:** Während CLI-SP-11 noch nicht durch ist, existieren `0.1`-Manifeste mit lineage-Block.
**Entscheidung:** Inspector v0.21 behandelt `0.1`-Manifeste mit `lineage`-Key als Quasi-`0.2`, mit grauem Hint *"empfohlen: `usdseal migrate` ausführen"*. Übergangs-Logik fällt in v0.22 weg.
**Konsequenz:** Bestandsfixtures funktionieren in v0.21, ohne dass Inspector auf CLI-Migration warten muss. Saubere Architektur ab v0.22 dann ohne Übergangs-Code.

### ADR-5 spec_version-Mismatch außerhalb Whitelist: Hint statt Brechen — <Datum>

**Kontext:** Inspector trifft auf zukünftige Manifest-Versionen, die nicht in der Whitelist stehen.
**Entscheidung:** Gelber Banner *"Manifest-Version X.Y · Inspector versteht 0.1, 0.2"*, Render-Versuch best-effort, keine Render-Crashes.
**Konsequenz:** Forward-Compat ohne Hard-Fails — anders als CLI, die `verify` verweigert. Inspector ist Read-Only-Tool, darf weicher reagieren.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente
- Master-Roadmap: `../ROADMAP.md`
- CLI Tech-Spec v0.1 (privat): `../USDseal-Tech-Spec-v0.1.md`
- Manifest-Schema (privat): `../usdseal-manifest-schema-v0.1.json`
- Test-Assets: `../usdz/DIEGOsat_master.usdz`, `../usdz/DIEGOsat_master_marketing.usdz`

### Externe Specs
- [OpenUSD Specification](https://openusd.org/release/index.html)
- [USDZ Asset Format](https://openusd.org/release/spec_usdz.html)
- [Alliance for OpenUSD (AOUSD)](https://aousd.org)

### Inspector-Repo
- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)
- [Live: kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/)

---

**Ende v0.21-Roadmap.** Nach Build: ADR-Einträge in CHANGELOG einhängen, Git-Tag setzen, Release-Notes aus CHANGELOG generieren. Dann Briefing für v0.22 (AR-Quick-Look-Validator) öffnen.
