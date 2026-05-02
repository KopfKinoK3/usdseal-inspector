# Changelog — USDseal Inspector

All notable changes to this project will be documented in this file.

## [0.22.2] — 2026-05-02

### Added
- **localStorage-Cache** — Inspector schreibt beim Laden jedes Manifests einen kompakten Eintrag in `localStorage` (`usdseal-inspector.cache.v1`). Schema: `{ manifest_id, sha256, role, import_history_ids, parent_manifest_id, filename, seen_at }`. Max 20 Einträge, FIFO. Datenschutz-Versprechen unverändert — kein Datenaustausch mit Servern.
- **Cache-Clear-Button** in der Topbar (neben Version-Badge). Zeigt aktuellen Eintragszähler. Confirm-Dialog vor dem Löschen. Counter wird beim Seitenstart und nach jedem Cache-Schreib-/Löschvorgang aktualisiert.
- **Re-Import-↻-Detection** — `detectReImports(manifest, cache)` erkennt bidirektionale Zyklen zwischen Master und Derived in Single-Drop-Szenario. Zwei Pfade: (A) Master geladen: prüft ob importierte Derived-IDs im Cache als Kinder des aktuellen Masters bekannt sind. (B) Derived geladen: prüft ob ein gecachter Master dieses Derived in `import_history_ids` führt. Ergebnis erscheint als ↻-Card(s) unterhalb der Lineage-Sektion.
- **↻-Card UI** — eigene `reimport-card`-Komponente (cyan-Akzentfarbe, passend zur Lineage-Sektion). Zweisprachig (DE/EN). Klartext-Message mit Manifest-IDs, Dateinamen und Cache-Timestamp. Abschluss-Note: *"Bewusster Workflow, kein Schema-Bruch."*

### Fixed
- **Headless-Test-Erwartung für `error_explicit.usdz`** korrigiert — Script-Expected war `ampel: 'green'`, korrekt ist `orange` (MANIFEST_HASH_MISMATCH → warn). Test-Results-Doku war schon korrekt, Script-Zeile fehlte. Headless-Pool-Test jetzt 7/7 PASS mit richtiger Erwartung.

### Architecture
- **ADR-1** (Cache-Backend localStorage, 2026-05-02): localStorage statt IndexedDB. 20 Einträge, kein Query-Bedarf, triviale R/W-API, kein Polyfill.
- **ADR-2** (Cache-Größe 20 Einträge FIFO, 2026-05-02): localStorage-Quota (~5 MB) wird nie ausgeschöpft. Älteste Einträge werden bei Überschreitung entfernt.
- **§1.4 Übergangs-Toleranz abräumen** — NICHT in diesem Sprint. CLI-SP-11 (`usdseal migrate`) noch nicht durch. Toleranz bleibt unverändert wie in v0.22.1. Wandert nach v0.22.3 oder v0.22.4.

### Tests
- **Headless-Pool-Test 7/7 PASS** (v0.22.2) — Cache/↻-Logic ist Browser-only und wird vom Headless-Script nicht mitgetestet. AR-QL-Validator: alle 7 Files unverändert korrekt. Script-Erwartung für `error_explicit.usdz` auf `orange/INVALID` korrigiert.

### Notes
- §1.3 Multi-File-Drop: verschoben nach v0.22.3 (ADR-PC3).
- Bundle-Größe: ~89 KB (Cache-Layer + Detection + ↻-UI).

---

## [0.22.1] — 2026-05-02 (in Vorbereitung, lokal)

### Added
- **Sprach-Toggle DE/EN reaktiviert** (W-2 aus v0.22 rückgängig). `CURRENT_LANG` ist wieder dynamisch — Default via `navigator.language`, persistiert in `localStorage` (`I18N_STORAGE_KEY = 'usdseal-inspector.lang'`), Toggle in der Topbar oben rechts. Inline-Object-Pattern bleibt — siehe ADR-7.
- **Finding-Sortier-Refinement** (ADR-10) — Comparator in `renderFindingsSection` ist jetzt drei-stufig: Severity → Category → ID. Categories sortieren nach Kritikalität (`structure → scale → textures → external → manifest → animation → performance`). Forward-Compat via `?? 99`-Fallback für unbekannte Categories.
- **W-3 — `TEXTURE_PATH_ABSOLUTE` Regex erweitert** auf alle 5 Plattform-Stile: Windows-Drive (`C:\`, `C:/`), UNC (`\\server\share`), `file://`, Unix-Home (`~/`, `$HOME/`), Unix-Absolute (`/Users/`, `/home/`, `/var/`, `/Volumes/`, `/tmp/`, `/opt/`, `/usr/`, `/root/`, `/mnt/`, `/media/`). Helper-Funktion `isAbsoluteTexturePath()` mit eigenen Test-Vektoren in `tests/textures-absolute-paths.json` (17/17 Pass).
- **W-4 — `TEXTURE_NOT_IN_USDZ` Toleranz** — Pfad-Vergleich ist jetzt tolerant gegen Case (`Texture.png` matcht `texture.png`), Type (`.jpg`/`.jpeg` gleichwertig) und Prefix (`./textures/foo.png` matcht `textures/foo.png`). Helper-Funktionen `normalizeTexturePath()` + `findMemberForManifestPath()`.
- **Neue Regel `TEXTURE_PATH_DIFFERENT_CASE`** (info, cat_textures) — wenn die tolerante Match greift aber der exakte Pfad abweicht, erscheint ein Plattform-Inkompatibilitäts-Hint *"Pfad-Schreibweise abweichend — möglicherweise Plattform-Inkompatibilität"*. Damit hat das Validator-Set jetzt **21 Regeln** (vorher 20).
- **W-5/W-6 — Parallel-Hashing via Web-Worker-Pool** (ADR-8). `HashWorkerPool`-Klasse mit Pool-Größe nach `navigator.hardwareConcurrency` (gecappt bei 8). Worker-Code inline via Blob-URL — Single-File-Versprechen bleibt intakt, kein externes `.js`-File. Memory-Strategie: Kopie pro Worker (Memory-Spike akzeptiert).
- **Loading-Indicator** mit fünf Stages (Unzip → Hashing → USD-Metadaten → Texturen → Render) und Member-Count-Status (z. B. *"Hashing 12/47"*). UI bleibt responsive bei großen USDZs.

### Architecture
- **ADR-7** (i18n-Strategie, 2026-05-02): Inline-Object-Pattern (`I18N = { key: { de, en } }`) wird beibehalten und um EN-Strings vervollständigt. Erwogene Alternative: Bundle-Split (`messages.de.js` / `messages.en.js`). Entscheidung **A1 Inline** wegen Single-File-Architektur-Anker, Standalone-Download via `file://` (Bundle-Split würde CORS-Probleme erzeugen) und überschaubarem String-Volumen (~30 KB).
- **ADR-8** (Worker-Pool-Strategie, 2026-05-02): Pool pro ZIP-Member statt Single-Worker. Performance-Gewinn auf Multi-Core, Memory-Spike akzeptabel bei realistischen USDZ-Größen. Worker-Code inline via Blob-URL.
- **ADR-9** (W-4 Toleranz, 2026-05-02): Toleranz nur in der Existenz-Prüfung, Path-Resolution für Texture-Anzeige bleibt strikt. Bei tolerantem Match → eigene `TEXTURE_PATH_DIFFERENT_CASE`-info-Regel als Plattform-Hint.
- **ADR-10** (Finding-Sortier-Strategie, 2026-05-02): Drei-stufiger Comparator Severity → Category → ID. Severity erhält UX-Anker, Category gruppiert verwandte Findings, ID-Alphabet als deterministischer Tie-Breaker (wichtig für Snapshot-Tests).

### Tests
- **Headless-Port** `tests/headless_validator.py` eingeführt — portiert AR_QL_RULES + Validator-Logik als eigenständiges Python-Script für CI-fähige Regression-Tests. Kein Build-Step, keine externen Deps außer Python 3 stdlib.
- **Pool-Test 7/7 PASS** dokumentiert in `tests/headless-pool-test-results.md`. Headless und Browser-UI stimmen für alle 7 Files überein.
- **`error_explicit.usdz`** ist korrekt als Hash-Mismatch-Fixture bestätigt: Inspector erkennt `MANIFEST_HASH_MISMATCH` + State INVALID zuverlässig. Dient als Regression-Fixture für diesen Pfad.

### Notes
- Bundle-Größe: ~85 KB (vorher 81 KB) — Worker-Pool + Loading-Indicator + W-3/W-4-Helper.
- Sprach-Toggle macht weiterhin `location.reload()` bei Wechsel — dynamic re-render bleibt für später (Inspector-Use-Case ist drag-and-drop, Reload kostet nichts).
- ADR-8 Worker-Pool-Cap bei 8: Diminishing Returns + Memory-Spike-Prävention bei Many-Small-Files — bewusster Trade-off, im ADR dokumentiert.
- Lokaler Build, kein Git-Tag, kein GitHub-Release.

---

## [0.22] — 2026-05-02 (in Vorbereitung, lokal)

### Added
- **AR Quick Look-Diagnose-Ampel** — neue Sektion direkt unter dem State-Banner. Drei Zustände:
  - 🟢 *Grün*: Asset erfüllt alle harten AR-QL-Anforderungen.
  - 🟠 *Orange*: Soft-Warnings — Apple empfiehlt Anpassungen (z. B. fehlendes `metersPerUnit`).
  - 🔴 *Rot*: Mindestens ein Hard-Fail — AR Quick Look bricht.
- **Validator-Engine** mit Regel-Array (`AR_QL_RULES`, 20 Regeln). Jede Regel: `{id, severity, category, requires?, check, explanation, fixHint}`. Engine läuft jede Regel gegen den Inspector-Context.
- **Findings-Liste** unterhalb der Ampel — Card pro Finding mit Severity-Pille, Klartext-Erklärung, optionalem Fix-Hinweis. Eingeklappt by default, Klick auf Header expand'd.
- **Sprach-Toggle DE/EN** in der Topbar — Auswahl persistiert in `localStorage`, Default via `navigator.language`.
- **`requires: 'valid_root'`-Mechanik** — wenn `STRUCTURE_ROOT_LAYER_NOT_FIRST` triggert (Inspector kann den Root-Layer nicht zuverlässig lesen), werden alle Regeln, die `usdMeta` brauchen, sauber unterdrückt. Verhindert Fehlalarme auf falschem Layer.
- **`AR-QL-RULES.md`** — kuratierte Regel-Tabelle mit allen 21 Regeln, Klartext-DE+EN, Fix-Hinweisen, Inspector-Check-Strategien.
- **Test-Asset-Pool** unter `../usdz/test-pool/` — 1 grünes + 3 rote USDZs mit isolierten Single-Triggern, plus README mit Reproduktions-Anleitung.

### Architecture
- **ADR-1** (Validator-Architektur, 2026-05-02): Regel-Array + Engine-Loop statt OOP-Hierarchie. Erweiterung = neuer Array-Eintrag, Tests pro Regel isolierbar.
- **ADR-2** (Severity-Mapping 3-stufig, 2026-05-02): error/warn/info → rot/orange/grün. Konsistent mit anderen Inspector-Bannern.
- **ADR-3** (Klartext zweisprachig DE+EN, 2026-05-02): Beide Sprachen inline, Toggle in Topbar.
- **ADR-4** (i18n als Plain-JS-Object inline, 2026-05-02): Kein Build-Step, kein externer Lib-Bedarf.
- **ADR-5** (Live-Preview NICHT in v0.22, 2026-05-02): `<model-viewer>` verschoben auf v0.25 — v0.22 bleibt schlank.
- **ADR-6** (`requires: 'valid_root'`-Pattern, 2026-05-02): Regel-Suppression bei kaputtem Root-Layer, transparent über die Engine-Loop. Verhindert Fehlalarme auf falschem USD-Layer.

### Notes
- Bundle bleibt klein: pures DOM-Rendering, keine neuen externen Libraries.
- Test gegen Asset-Pool durchlaufen: alle 4 Pool-Files + 2 DIEGOsat-Bestand-Files liefern erwartete Ampel-Zustände.
- Sprach-Toggle: bei Wechsel wird die Seite neu geladen (einfachste Lösung; dynamisches Re-Rendering verschoben auf v0.22.1).
- Lokaler Build, kein Git-Tag, kein GitHub-Release.

---

## [0.21] — 2026-05-01 (in Vorbereitung, lokal)

### Added
- **Lineage-Panel** — neue Sektion oberhalb des Manifest-Blocks. Zwei Modi:
  - **Master** (`lineage.role = "master"`): listet alle `import_history[]`-Einträge mit `imported_from_manifest_id`, SHA-256-Prefix, `imported_paths[]`, Timestamp und Actor.
  - **Derived** (`lineage.role = "derived"`): zeigt `parent_manifest_id`, `parent_sha256`, `exported_classifications[]`, `exporter_tool`, `exported_at`.
- **Provenance-Timeline** aufgemöbelt — Step-Badges (sealed/merged/derived) mit eigenen Icons (✓ ⊕ ↳), Tool-Pille (z. B. `USDseal/0.2.0`), Render von `notes` (z. B. *"Merged 3 path(s) from visales-derived-c8c4"*).
- **Compat-Layer**: `compatCheck(manifest)` → Whitelist `["0.1", "0.2"]`, Hint-Banner bei unbekannter Version (gelb) oder Übergangs-Toleranz (grau, *"Manifest stammt aus pre-bump CLI v0.2 — empfohlen: `usdseal migrate`"*).
- `COMPATIBILITY.md` — Versions-Matrix Inspector ↔ `spec_version`, Übergangs-Toleranz dokumentiert, Re-Import-Detection-Roadmap.

### Architecture
- **ADR-3** (renderForSpecVersion-Pattern, 2026-05-01): Versions-spezifische Renderer statt Toleranz auf Feld-Anwesenheit. Erweiterung auf 0.3 / 0.4 später = neue Render-Funktion + Whitelist-Eintrag, kein Refactoring der Bestandslogik.
- **ADR-4** (Übergangs-Toleranz pre-bump 0.1, 2026-05-01): `0.1`-Manifeste mit `lineage`-Block werden wie Quasi-`0.2` behandelt, mit grauem Migrate-Hint. Logik fällt in v0.22.2 weg, sobald CLI-SP-11 (`usdseal migrate`) durch ist.
- **ADR-2** überarbeitet (Re-Import-Detection auf v0.22.2 verschoben, 2026-05-01): Single-View-Inspector kann Re-Import nicht aus einem Manifest allein erkennen. Patch-Release v0.22.2 (nach v0.22, vor v0.23) bringt Cross-Manifest-Cache via localStorage + optionalen Multi-Drop. v0.22 bleibt für die AR-Quick-Look-Validator-Story reserviert.

### Notes
- Test-Asset-Paar DIEGOsat (master + master_marketing) deckt Master-Modus mit Re-Import-Topologie ab — ↻-Marker noch nicht aktiv (siehe ADR-2).
- Bundle bleibt klein: pures DOM-Rendering, keine neuen externen Libraries.
- Lokaler Build, kein Git-Tag, kein GitHub-Release. Snapshot-Vorschau: `v0.21-snapshot.html`.

---

## [0.2] — 2026-04-28

### Added
- State detection: SIGNED / DRAFT / INVALID / NO MANIFEST
- SHA-256 asset verification against USDseal manifest
- USD metadata extraction: USDA (text parse) + USDC (heuristic string extraction)
- Texture analysis: PNG (IHDR), JPEG (SOF marker), WebP (VP8 header)
- Texture thumbnails via Base64 inline preview
- Provenance chain display (author, version, predecessor file)
- Signature details panel (Ed25519 public key, timestamp, algorithm)
- viSales Warm Tech design system (Orange #F97316, Cyan #0891B2)
- Fully client-side — no data upload, no server, no API

### Notes
- Ed25519 cryptographic signature verification not yet implemented (planned v0.3)
- USDC parsing uses heuristic string extraction (full binary parsing planned)

## [0.1] — 2026-04 (internal)

- Initial proof of concept
- JSZip-based USDZ parsing
- Basic manifest detection
