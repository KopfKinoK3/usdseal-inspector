# Changelog — USDseal Inspector

All notable changes to this project will be documented in this file.

## [0.28.0.4] — 2026-05-30

### Added
- **Klappbarer Tester-Block** neben PDF-Report-Button (Default kollabiert): 4 optionale Felder — Name, Firma, Rolle, Notiz (textarea). Merken-Checkbox speichert via localStorage (`usdseal_inspector_tester_remember` + `usdseal_inspector_tester_data`). Felder werden bei Page-Load automatisch befüllt wenn Checkbox aktiv war. Cache-Clear-Button löscht Tester-Keys mit.
- **PDF: Voll-Audit-Sektion** am Anfang (nach File Identity, vor AR Quick Look): orange Akzentleiste (analog v0.26.0-Geometrie-Pattern), Labels fett, Notiz mehrzeilig via `splitTextToSize`, Datum automatisch formatiert (DE: "25. Mai 2026, 14:30 Uhr" / EN: "May 25, 2026, 2:30 PM"), Selbstangabe-Disclaimer dezent. Sektion wird **komplett weggelassen** wenn alle 4 Felder leer.
- **PDF: Footer-Zeile** auf jeder Seite mit Tester-Prefix wenn Name vorhanden: `"Geprüft von (Selbstangabe): Max Müller, viSales GmbH"` — links, kleinschrift, neben der bestehenden Inspector-Versionszeile.
- **11 neue i18n-Keys** DE+EN: `tester_toggle`, `tester_name_label`, `tester_company_label`, `tester_role_label`, `tester_note_label`, `tester_remember_label`, `tester_date_hint`, `pdf_tester_section_title`, `pdf_tester_date_label`, `pdf_tester_disclaimer`, `pdf_tester_footer_prefix`.

### Architecture
- **ADR-47** (Tester-Selbstangabe-Pattern, 2026-05-30): Klappbarer Block opt-in, keine Pflichtfelder (ADR-PC3), keine neuen Deps (ADR-PC5). Selbstangabe-Disclaimer im PDF rechtssichert das Feature. Sektion-Skip bei leeren Feldern verhindert unprofessionelle leere Blöcke. localStorage-Merken-Checkbox als Komfort-Feature für Power-User. Details in CLAUDE-Inspector-private.md § ADR-47.
- PDF wird zur Compliance-Dokumentation: Tester-Signatur + Datum + Notiz = offizieller Audit-Trail. B2B-Story: "Audit-Reports mit Prüfer-Signatur, bereit für Compliance- und Vertriebs-Workflows."

### Notes
- `INSPECTOR_VERSION = '0.28.0.4'`
- 18/18 PASS (Headless-Pool — Standard-Pipeline unverändert)
- Standard-Build: 213.4 KB (+9.2 KB gegenüber v0.28.0.3)
- Advanced-Build: 238.2 KB

---

## [0.28.0.3] — 2026-05-25

### Added (Inspector Advanced)
- **Asset-Klassifikation `classifyAssetForPlayer()`** (ADR-46): Analysiert ZIP-Struktur und Root-Layer-Binary bevor der User den Player startet. Drei Stufen: PASS / CAUTION / BLOCK. Heuristik aus Spike gegen 6 Real-World-Assets empirisch abgeleitet (docs/v0.28.0.3-spike-results.md).
  - BLOCK A: eingebettete Sub-USDZ im ZIP (Frankfurt-Muster)
  - BLOCK B: ≥ 5 USDC-Module (Multi-Kompositions-Szene)
  - BLOCK C: Root-USDC <100 KB + `references`/`variantSetNames` im Binary (RENZ-Muster, Tiny-Coordinator)
  - CAUTION: Datei >20 MB oder 2–4 USDC-Module
- **Dynamischer Button-Text**: PASS = `▶ 3D-Preview starten ✓` (orange), CAUTION = `⚠ 3D-Preview testen` (amber), BLOCK = `⊘ 3D-Preview nicht empfohlen` (grau, trotzdem klickbar). DE+EN.
- **Klassifikations-Reason im Beta-Banner**: bei CAUTION/BLOCK erscheint der Klassifikations-Grund direkt im Banner (z. B. "Variants/References erkannt — Three.js rendert nur Root-Layer").
- **USDconfig-Brücken-Block** unter dem Player (§ 3.6): Erklär-Box "Warum die 3D-Preview Grenzen hat" — erklärt Three.js USDLoader-Limits (Variants, USDC, Multi-Layer, Animation), B2B-Kontext, USDconfig-Pitch (Duke-Text wortgetreu). Sichtbar IMMER nach File-Drop. Link auf USDconfig-Landingpage DE/EN. 28 neue i18n-Keys (`player_limits_*`).
- **Parse-Fail-Toast** (§ 3.7.b): Nach `loader.parse()` wird `group.children.length` geprüft. Leere Gruppe = "3D-Preview konnte das Asset nicht laden — vermutlich Variants oder Komposition." (Frankfurt-Muster). Toast-Key `adv_toast_parse_fail`.
- **Blank-Canvas-Toast** (§ 3.7.a): 2 Frames nach Render wird Bounding-Box geprüft. `size === 0` = "Canvas bleibt leer — möglicherweise Variants/Komposition nicht aufgelöst." (RENZ-Muster). Toast-Key `adv_toast_empty_canvas`.
- **docs/v0.28.0.3-spike-results.md**: Vollständige Spike-Dokumentation mit Asset-Matrix, Korrelationsmatrix, Heuristik-Entwurf, Go/No-Go-Begründung.
- **docs/PLAYER-ASSET-COMPATIBILITY.md**: Kuratierte Kompatibilitäts-Dokumentation — PASS/CAUTION/BLOCK-Klassen mit Beispielen und technischer Erklärung.

### Changed (Inspector Advanced)
- **Button-Farbe** (§ 3.7.c): `#adv-start-btn` nutzt jetzt `--primary-dark` (#C2410C, Orange-700) als Basis-Fill statt outlined-Style. Warm-Tech-Orange konsistent mit viSales-Palette.
- **`resetThreePreview()`**: Reset setzt jetzt auch Klassifikations-Banner zurück (`adv-classify-reason` versteckt, `adv-usdconfig-bridge` versteckt, `_playerReadyClassification = null`).
- **`processFile()`**: Berechnet `classifyAssetForPlayer()` im `memberHashes`-Scope (wo `rootLayerData` verfügbar ist) und übergibt das Ergebnis als 5. Parameter an `setPlayerReady()`.
- `console.error`-Tag aktualisiert auf `[v0.28.0.3]`.

### Architecture
- **ADR-46** (Asset-Klassifikations-Heuristik für Player-Erwartungs-Management, 2026-05-25): Spike-Befund: Variants-Asset-Klasse ist B2B-Norm (3/4 Live-Test-Assets). Three.js USDLoader r184 strukturell limitiert für diese Klasse. Konservative regelbasierte Heuristik mit 3 BLOCK-Triggern aus ZIP-Struktur + Root-Binary-Scan. USDconfig-Brücke positioniert die 3D-Preview als Demo-Klasse, USDconfig als Lösung. Details in CLAUDE-Inspector-private.md § ADR-46.

### Notes
- `INSPECTOR_VERSION = '0.28.0.3'`
- 18/18 PASS (Headless-Pool — Standard-Pipeline unverändert)
- Standard-Build: 204.2 KB
- Advanced-Build: 229.1 KB (ohne Bundle, Bundle 1032.8 KB on-demand)
- Klassifikations-Verifikation gegen 6 echte Assets: 6/6 korrekte Stufe

---

## [0.28.0.2] — 2026-05-25

### Changed (Inspector Advanced)
- **Lazy-Load Three.js-Bundle** (ADR-45): Bundle (~1 MB) wird nicht mehr beim Page-Load injiziert, sondern on-demand on-click geladen. `advanced/index.html` sinkt von ~1244 KB auf ~217 KB Initialgröße. Bundle wird als separates File `advanced/three-usdloader-r184-bundle.js` ausgeliefert.
- **Opt-in Player** (ADR-45): 3D-Preview startet nicht mehr automatisch beim File-Drop. User sieht nach Drop einen aktivierten `▶ 3D-Preview starten`-Button. Player-Bereich ist ab dem ersten Advanced-Load immer sichtbar (nicht mehr `display:none` auf der Section).
- **Try/Catch um die gesamte Player-Pipeline** (ADR-45): `loadThreeBundle()` → `loader.parse()` → Scene-Setup vollständig abgesichert. Crash zeigt Fehler-Toast mit ausklappbarem Detail (`adv_error_detail`) — Standard-Report darunter unberührt. Safari-Freeze bei Frankfurt-Asset unmöglich, solange User nicht aktiv klickt.
- **Render-Reihenfolge explizit** (ADR-45): Standard-Report rendert synchron zuerst, Player-Bereich zeigt Platzhalter mit Button. Keine Kaskade-Abhängigkeit mehr.
- **i18n 4 neue Keys** (ADR-45): `adv_pre_drop`, `adv_start_btn`, `adv_loading_bundle`, `adv_error_detail` — DE+EN.
- **`build.py`** erweitert: kopiert Bundle nach `advanced/three-usdloader-r184-bundle.js` statt es inline zu injizieren.

### Architecture
- **ADR-45** (Graceful Degradation für Advanced-Player, 2026-05-25): Three.js USDLoader r184 ist für die viSales-Asset-Klasse nicht produktionsreif (Erst-Test 2026-05-25: SalmonPasta ✓, DIEGOsat schwarz, Frankfurt Safari-Freeze). Entscheidung: Player opt-in + lazy-load + vollständiger try/catch + immer-sichtbarer Beta-Bereich. Single-File-Anker für Advanced bewusst gelockert: `advanced/` ist jetzt Two-File-Distribution (HTML + Bundle). Begründung: Schlank-Anker schlägt Single-File-Anker für Advanced — 217 KB Initial-Download statt 1244 KB. Vorbereitung für v0.28.0.3 Asset-Klassifikation (Player-Bereich ist jetzt isolierter Layer).

### Notes
- `INSPECTOR_VERSION = '0.28.0.2'`
- 18/18 PASS (Headless-Pool — Standard-Pipeline unverändert)
- Standard-Build: 200.4 KB — unverändert
- Advanced-Build initial: ~217 KB (Bundle on-demand: ~1033 KB)
- Befund-Kontext Erst-Test 2026-05-25: SalmonPasta rendert sauber, DIEGOsat schwarzer Canvas, Frankfurt friert Safari ein

---

## [0.28.0] — 2026-05-25

### Added
- **Inspector Advanced** (`advanced/index.html`): Neue Distribution mit Three.js Desktop-3D-Preview. Inline-eingebettet, kein CDN, single-file, `file://`-öffenbar. Rendert USDA, USDC und USDZ mit Orbit-Controls.
- **Two-File-Pattern** (ADR-43): `src/inspector.html` als gemeinsame Quelle mit `<!-- ADVANCED-ONLY:START/END -->` und `<!-- STANDARD-ONLY:START/END -->` Markern. `build.py` erzeugt beide Distributions automatisch.
- **`build.py`** Build-Script: Standard- und Advanced-Build aus einer Quelle. Unterstützt `BUILD-INJECT:` Vendor-Files (`<script>`-gewrapped).
- **Three.js r184 IIFE-Bundle** (`vendor/three-usdloader-r184-bundle.js`, ~1 MB): Inline-Bundle aus `three.core.min.js` + `three.module.min.js` + fflate + USDAParser + USDCParser + USDComposer + USDLoader + OrbitControls. Erzeugt von `vendor/bundle.py`. Globals: `window.THREE` (451 Keys), `window.USDLoader`, `window.OrbitControls`.
- **Click-Through-Button** im Standard-Footer: `Mehr Features → Inspector Advanced` (STANDARD-ONLY, kein CTA im Advanced).
- **Zurück-Link** im Advanced-Header: `← Standard-Inspector` (ADVANCED-ONLY).
- **`Advanced`-Badge** im Logo (ADVANCED-ONLY).

### Architecture
- **ADR-43** (Two-File-Pattern, 2026-05-25): Single Source → zwei Single-File Distributions. Standard ~200 KB, Advanced ~1.2 MB. Beide privacy-first, keine externen Deps zur Laufzeit.
- **ADR-44** (Three.js r184 inline-embedded, 2026-05-25): `USDZLoader` deprecated seit r179 → `USDLoader`. r184 kein UMD mehr (nur ESM). Manuelles IIFE-Bundle via `vendor/bundle.py`. Block-Scope-Isolation gegen minifizierte Konstanten-Kollisionen (`const e` in core + module). window.THREE enthält alle 444 Core-Exports + 7 Module-Exports.

### Notes
- `INSPECTOR_VERSION = '0.28.0'`
- 18/18 PASS (Headless-Pool, Standard-Build)
- Standard-Build: 200.0 KB — keine Three.js-Abhängigkeit
- Advanced-Build: ~1244 KB — vollständige Three.js-Runtime inline

---

## [0.27.3] — 2026-05-09

### Changed
- **Landingpage Verify-Block (DE + EN)** (ADR-42): Hinweis *"demnächst public auf GitHub"* (DE) / *"coming soon on GitHub"* (EN) durch echten Inline-Link auf `github.com/KopfKinoK3/usdseal-verify` (Apache-2.0) ersetzt. Zusätzlicher CTA-Button *"Independent Verifier auf GitHub"* / *"View Independent Verifier"* neben *"Verify-Strategy ansehen"*.

### Architecture
- **ADR-42** (Landingpage Verifier-Link scharf gestellt, 2026-05-09): `usdseal-verify`-Repo seit 2026-05-09 nachmittags public unter `github.com/KopfKinoK3/usdseal-verify` (Apache-2.0). Pure HTML-Edits, bestehende `btn btn-ghost`-Klasse wiederverwendet, kein neuer Dep, kein Build-Step.

### Notes
- `INSPECTOR_VERSION` unverändert (Landingpage-only-Change, kein Inspector-Code-Touch)
- Cross-Browser-Verifikation: DE + EN, Inline-Link + 3. CTA-Button korrekt im DOM

---

## [0.27.2] — 2026-05-09

### Fixed
- **Layer-2-Feldname-Fix** (ADR-41): `manifest.pre_seal_sha256` → `manifest.subject_asset?.sha256` (Optional-Chaining). Tatsächlicher Feldname laut `usdseal_verify.py:104` und Live-Manifest-Diagnose. v0.27 hatte den falschen Key angenommen — Feld war die ganze Zeit vorhanden.
- **Layer-2-Soft-Check-Anzeige**: beide Hashes jetzt sichtbar — Erwartet (Manifest: `subject_asset.sha256`) und Aktuell (Datei: WebCrypto `crypto.subtle.digest` live). Soft-Check-Erklärung DE+EN: Differenz ist by design, da Manifest nach Sealing in USDZ injiziert wird und ZIP-Struktur verändert.
- **PDF-VERIFY Layer 2**: analog UI — beide Hashes + Soft-Check-Hinweis-Zeile.

### Added
- **`sha256Hex(buf)`-Hilfsfunktion**: `crypto.subtle.digest('SHA-256', buf)` → Hex-String. Nativ WebCrypto, kein neuer Dep.
- **i18n 5 neue Keys** (`layer2_expected_label`, `layer2_actual_label`, `layer2_diff_explain`, `layer2_no_hash`) DE+EN. `layer2_preseal` erweitert um "(Soft-Check)".
- **`fileHash` in `_currentReport`** gespeichert — PDF-Generator kann live File-Hash ausgeben.

### Architecture
- **ADR-41** (Layer-2-Feldname-Korrektur + Soft-Check-Anzeige, 2026-05-09): Phase-5.0-Diagnose (ADR-PC4) hat `manifest.pre_seal_sha256` als falschen Feldnamen identifiziert. Tatsächlich: `manifest.subject_asset.sha256`. Layer 2 ist Spec-§4-Soft-Check by design — Manifest wird nach Sealing injiziert, ZIP-Struktur ändert sich, Differenz zwischen Manifest-Hash und aktuellem File-Hash ist erwartet. Inspector zeigt jetzt beide Hashes transparent statt "nicht im Manifest".
- **ADR-39-Korrektur** (2026-05-09): ADR-39 beschrieb Layer 2 als "Phase-2-Feature weil `pre_seal_sha256` nicht vorhanden" — Annahme falsch. Feld existiert als `subject_asset.sha256`. Siehe ADR-41 für Korrektur-Patch.

### Notes
- `INSPECTOR_VERSION = '0.27.2'` (ADR-38-Konstante; UI-Badge + PDF-Header automatisch)
- 18/18 PASS (Headless-Pool unverändert)
- Browser-Verifikation: DIEGOsat Layer 2 — Manifest-Hash `789d6527…`, File-Hash `b2b8d24e…`, Soft-Check-Text korrekt

---

## [0.27.1] — 2026-05-09

### Added
- **Landingpage Verify-Sektion (DE + EN)** (ADR-40): Neue Sektion `#verify` zwischen `#ar-quick-look` und `#anwendung` in beiden Sprach-Versionen der Landingpage. Inhalt: Pitch-Absatz "Don't trust, verify", 3-Layer-Architektur-Block (Layer 1–3 mit ehrlichen Phase-2-Hinweisen), Python-Code-Snippet (5 Zeilen, sprach-neutral), CTAs auf Inspector-Live-URL und Verify-Strategy.md. Independent-Verifier-Repo-Status geklärt (GitHub 404 → privat): ehrlicher "demnächst public"-Hinweis statt Tot-Link (ADR-PC4-konform).

### Architecture
- **ADR-40** (Landingpage Verify-Sektion, 2026-05-09): Pure HTML-Änderung, bestehende CSS-Klassen wiederverwendet (`wrap`, `eyebrow-primary`, `sub-section sub-section-primary`, `btn btn-primary`, `btn btn-ghost`). Minimal-inline-CSS für `<pre><code>`-Block (monospace, `bg-neutral`, `border-inner`). Kein neuer Dep, kein Build-Step. Single-File-Anker für Inspector-App unberührt — `INSPECTOR_VERSION` bleibt `'0.27'`.

### Notes
- `INSPECTOR_VERSION = '0.27'` (unverändert — nur Landingpage berührt)
- `usdseal-verify`-Repo: 404 / privat → "demnächst public auf GitHub"-Hinweis

---

## [0.27] — 2026-05-09

### Added
- **VERIFY · 3-LAYER-TRUST Sub-Sektion** im USDseal-Trust-Block — macht die 3-Layer-Bytestream-Architektur (ADR-PC6) sichtbar statt deklarativ.
  - **Layer 1 — Komponenten-Hash-Tabelle**: alle ZIP-Members mit Erwartet/Aktuell/Status. Threshold-Pattern wie v0.26.2 (>20 Komponenten = Toggle-Button, sonst direkte Anzeige). Bei Mismatch: Tabelle automatisch ausgeklappt, Mismatch-Zeilen rot highlighted, Mismatch-Hint-Text.
  - **Layer 2 — Pre-Seal-Hash**: `pre_seal_sha256` wird angezeigt falls im Manifest vorhanden. Da aktuelles DIEGOsat/error_explicit-Manifest das Feld nicht enthält: ehrlich als "nicht im Manifest — geplant für Spec v0.3" markiert (ADR-PC4: Diagnose vor Hypothese).
  - **Layer 3 — Manifest-Signatur**: `signature.format` / `signature.algorithm` angezeigt wenn vorhanden; Signatur-Verify ehrlich als "ab v0.3 (Ed25519/WebCrypto API)" markiert.
- **Avalanche-Live-Demo**: Bit-Flip (letztes Bit) + WebCrypto SubtleCrypto.digest('SHA-256') + Hamming-Distanz-Berechnung (Bit-Level). Live im Browser, kein neuer Dep. Erklärungstext: *"1 Bit geändert → komplett anderer Hash."* — Konferenz-/AOUSD-Demo-Material.
- **Diff-View bei Hash-Mismatch**: Layer-1-Tabelle zeigt Mismatch-Zeilen oben (bestehende Sort-Logik), rote Highlighting via CSS `.row-mismatch`, durchgestrichener Expected-Hash vs. roter Actual-Hash. Test-Beleg: `error_explicit.usdz`.
- **5 Verlinkungen** ("Don't trust, verify:"): Inspector Verify-Strategie als aktiver Link auf GitHub; Spec v1.0, Independent Verifier, Threat Model, Determinism Audit als "demnächst öffentlich" (CLI-Repo privat per v0.27).
- **PDF-VERIFY-Sektion**: kompakt im USDseal-Block vor Asset-Inventory. 3-Layer-Statuszeilen, Mismatch-Komponenten als Inline-Tabelle, ausgeschriebene Verlinkungen-URLs. Avalanche-Demo nicht im PDF (live-only).
- **i18n DE+EN**: 26 neue Keys (`verify_*`, `layer*`, `avalanche_*`, `hamming_*`, `link_*`, `tbl_*`, `pdf_verify_*`).
- `window._currentRawBuf` gespeichert in `processFile()` für Avalanche-Demo-Byte-Zugriff.

### Architecture
- **ADR-39** (Verify-UI Self-Tests + Diff-View + Avalanche-Demo, 2026-05-09): v0.26.x hat PDF-Audit-Report material-vollständig gemacht. USDSEAL-VERIFY-STRATEGY.md (2026-05-07) und CLI-Spec v1.0 (Bytestream-Hashing, ADR-PC6) lagen vor. Inspector zeigte Trust bislang als opakes "Signiert & versiegelt"-Banner — die 3-Layer-Architektur war im UI unsichtbar. Sub-Sektion "VERIFY · 3-LAYER-TRUST" innerhalb USDseal-Trust-Block. Layer 2 ehrlich als Phase-2-Feature markiert weil `pre_seal_sha256` in aktuellen Manifesten nicht vorhanden (ADR-PC4). WebCrypto SubtleCrypto nativ im Browser — kein neuer Dep. Single-File-Anker bestätigt. — *Korrektur 2026-05-09: Phase-5.0-Diagnose hatte Feldname `pre_seal_sha256` angenommen — tatsächlich `subject_asset.sha256`. Siehe ADR-41 für Korrektur-Patch.*

### Notes
- `INSPECTOR_VERSION = '0.27'` (ADR-38-Konstante hält)
- 18/18 PASS erwartet (kein Validator-Touch)
- Browser-Verifikation: DIEGOsat (signiert, Layer 3 vorhanden), Frankfurt (unsigniert, no-manifest path), error_explicit (Mismatch, Diff-View + Auto-Expand)
- Letzter Single-File-Sprint vor v0.28 (Konsumer-Patterns)

---

## [0.26.2] — 2026-05-08

### Added
- **Threshold-basierte Texture-Tabelle für Großfiles** (ADR-37): Bei >20 Texturen wechselt die TEXTUREN-Sektion im PDF-Audit-Report vom 3-Zeilen-Block-Layout (v0.26.1) auf eine kompakte 6-Spalten-Tabelle (Pfad · Format · Größe · Auflösung · Channel · Status). Frankfurt (55 Texturen) von ~8 auf ~4 PDF-Seiten reduziert. Kleine Files (≤20 Texturen, z.B. DIEGOsat mit 4) behalten das Block-Layout unverändert.
  - Konstante `TEXTURE_TABLE_THRESHOLD = 20`
  - `drawTexTableHeader()` mit Header-Wiederholung bei Page-Break
  - Pfad-Spalte front-truncated (`...suffix`) analog Asset-Inventory
  - USDC-Binary-Hint-Box und Summary-Zeile bleiben in beiden Layouts identisch
  - i18n DE+EN: 6 neue Spalten-Header-Keys (`pdf_tex_col_*`)
  - Asset-Inventory-Tabellen-Pattern (ADR-12, v0.23) wiederverwendet — kein neuer Dep

### Architecture
- **ADR-37** (Threshold-basierte Texture-Tabelle, 2026-05-08): v0.26.1 Block-Layout produzierte bei Frankfurt (55 Texturen) einen 8-seitigen PDF-Report — unhandlich für PR-Material und B2B-Audit. Threshold 20 gewählt weil ≤20 Texturen unter 1 PDF-Seite bleiben. Asset-Inventory-Tabellen-Pattern (pures `jsPDF.text()/line()`, ADR-12) wiederverwendet — kein autoTable-Plugin, Single-File-Anker bestätigt. UI-Texture-Sektion unverändert.

### Notes
- 18/18 PASS (Headless-Pool unverändert — kein Validator-Touch)
- i18n: 6 neue Keys (`pdf_tex_col_path/format/size/resolution/channel/status`)
- Browser-Verifikation: Frankfurt → Tabellen-Layout; DIEGOsat → Block-Layout (unverändert)

### Patch (Tag force-replaced, 2026-05-09)
- **UI version badge bound to INSPECTOR_VERSION** (ADR-38): HTML-Badge war seit v0.25.8 hardcoded — wurde in v0.26.0/v0.26.1/v0.26.2 nie hochgezogen. `id="version-badge"` + `DOMContentLoaded`-Listener setzt `badge.textContent = 'v' + INSPECTOR_VERSION`. Single source of truth. Tag `v0.26.2` force-replaced.

---

## [0.26.1] — 2026-05-08

### Added
- **Texturen-Sektion im PDF-Audit-Report** (ADR-36): PBR-Channels, Format-Details und Auflösung pro Textur jetzt auch im PDF — zwischen Geometrie und USDseal · Trust & Provenance.
  - Pro Textur: Pfad (truncated), Format · Größe · Auflösung, Channel-Label(s), Status
  - PBR-Channels: BaseColor / Normal / Roughness / Metallic / Emissive / Occlusion / Opacity / Displacement / Subsurface / Clearcoat / ORM (kombiniert) / Diffuse
  - Format-Labels: PNG / JPEG / WebP / AVIF / HEIC / KTX2 / TIFF / ASTC (alle OpenUSD-Spec-konformen Formate seit v0.25.5)
  - USDC-Binary-Hint-Box (orange) analog ADR-33 wenn `usdcBinaryMaterials === true`
  - Summary-Zeile: Anzahl Texturen · tracked/unknown/unused · Gesamtgröße · Formate
  - i18n DE+EN: 22 neue Keys (`pdf_tex_*`, `pdf_ch_*`)
  - `textures` + `channelInfo` jetzt in `_currentReport` gespeichert (Mini-Patch analog v0.26.0)

### Architecture
- **ADR-36** (Texturen-Sektion im PDF, 2026-05-08): PDF-Audit-Report hatte PBR-Channel-Erkennung (v0.24) und Format-Details (v0.25.5) nur im UI — Audit-Lücke. `extractTextures()` + `buildChannelMap()` wiederverwendet. Layout-Stil konsistent mit v0.26.0 (orange Akzentleiste via `secHeader()`). USDC-Binary-Hint analog ADR-33. Single-File-Anker bestätigt.

### Notes
- 18/18 PASS (Headless-Pool unverändert — kein Validator-Touch)
- i18n: 22 neue Keys

---

## [0.26.0] — 2026-05-07

### Added
- **Geometry-Sektion im PDF-Audit-Report** (ADR-35): Alle 10 Geometry-Kennzahlen aus `extractGeometryStats()` (seit v0.25) jetzt auch im PDF sichtbar — zwischen AR Quick Look · Diagnose und USDseal · Trust & Provenance.
  - Felder: Meshes, Polygone (mit Tausender-Trennzeichen), Vertices, Materials, Prims, Joints, UV-Sets, Subdivision, Time-Range, FPS
  - Spezialfall USDC-Binary: Hinweis-Box (orange) wenn Geometrie-Daten nicht extrahierbar
  - Spezialfall Procedural-Only: Hinweis-Box (neutral) wenn nur prozedurale Primitive (Sphere/Cube) erkannt
  - i18n DE+EN: 5 neue Keys `pdf_geo_*`
  - `geoStats` jetzt in `_currentReport` gespeichert

### Architecture
- **ADR-35** (Geometrie-Sektion im PDF, 2026-05-07): PDF-Audit-Report war die einzige Ansicht ohne Geometry-Daten — größte Lücke nach v0.25.6-Reorder. `extractGeometryStats()` wiederverwendet (kein neuer Parser-Code). Layout-Stil konsistent mit v0.25.6 (orange Akzentleiste via `secHeader()`). Single-File-Anker bestätigt.

### Notes
- 18/18 PASS (Headless-Pool unverändert — kein Validator-Touch)
- i18n: 5 neue Keys (`pdf_geo_title`, `pdf_geo_meshes`, `pdf_geo_polygons`, `pdf_geo_usdc_hint`, `pdf_geo_proc_hint`)

---

## [0.25.7] — 2026-05-06

### Changed
- **USDC-Material-Limitation transparent kommuniziert** (ADR-33): Frankfurt-USDZ (22 USDC-Sub-Files) zeigte alle Texturen fälschlicherweise als UNUSED — obwohl AR Quick Look alle rendert. Inspector kann USDC-Binary-Material-Bindings strukturell nicht parsen.
  - `buildChannelMap` erkennt jetzt USDC-Binary-Files + prüft ob USDA-Connect-Edges existieren → `usdcBinaryMaterials: bool` im Return-Value
  - Texture-Status: bei USDC-Binary-Materials werden alle unbindigen Texturen als **"unknown"** (statt "unused") markiert — in Einzel- und Multi-File-View
  - Neu: **Hinweis-Box** oben im Texture-Inventar wenn Heuristik greift (DE+EN i18n)
  - PDF-Audit-Report: gleicher Hint als Box in der Asset-Inventory-Sektion
  - Badge-Tooltip i18n: `usdc_mat_badge_tooltip` DE+EN

### Architecture
- **ADR-33** (USDC-Material-Limitation transparent, 2026-05-06): "unused" war bei USDC-Binary-Files faktisch falsch — wir wissen es nicht, wir kommunizieren "unknown". KEIN USDC-Polyfill (ADR-PC5). Single-File-Anker + Privacy-First bestätigt.

### Notes
- Headless-Pool: Frankfurt-Erwartung aktualisieren auf `textureStatus: 'unknown'`
- i18n: 2 neue Keys (`usdc_mat_hint`, `usdc_mat_badge_tooltip`)

---

## [0.25.6] — 2026-05-06

### Changed
- **PDF-Report: User-First-Reihenfolge** (ADR-32): Sektion-Reihenfolge in `generatePDF()` umgestellt — AR Quick Look · Diagnose jetzt prominent oben, USDseal · Trust & Provenance als dedizierter Block unten.
  - Neu: **AR-State-Banner** im AR-Diagnose-Block ("AR Quick Look: bricht / Laeuft mit Vorbehalt / sauber") — `ampel`-Daten vorhanden, erstmals als Banner gerendert.
  - Neu: Sektion-Header **"USDSEAL · TRUST & PROVENANCE"** mit oranger Akzentleiste.
  - Kompakter NO_MANIFEST-Block: bei unsignierten Files Minimal-Hint + Asset-Inventory, kein voller Counter-Bereich.

### Architecture
- **ADR-32** (PDF-Report-Reihenfolge User-First, 2026-05-06): Real-World-Sweep zeigte USDseal-zentrischen Bias — "Kein Manifest" dominierte oben, AR-Diagnose war versteckt. Neue Reihenfolge: Datei-Identität → AR Quick Look · Diagnose → USDseal · Trust & Provenance → Disclaimer. Inspector-Report generisch nutzbar; USDseal als Plus-Sektion.

### Notes
- Headless-Pool **18/18 PASS** (kein Validator-Touch, nur PDF-Reorder).
- i18n: `pdf_ar_findings_title` → "AR Quick Look · Diagnose" / "AR Quick Look · Diagnostics"; neuer Key `pdf_usdseal_section`.

---

## [0.25.5] — 2026-05-06

### Added
- **OpenUSD-Texture-Spec komplett abgedeckt** (ADR-31): Magic-Bytes-Reader für alle vier verbleibenden OpenUSD-USDZ-Spec-Formate nach AVIF-Pattern (v0.25.4):
  - `readHeicSignature()` — ISOBMFF-ftyp-Box mit Brand `heic`/`heix`/`mif1`/`msf1`
  - `readKtx2Signature()` — 12-Byte KTX2-Magic `\xABKTX 20\xBB\r\n\x1A\n`
  - `readTiffSignature()` — 4-Byte LE (`II*\0`) oder BE (`MM\0*`)
  - `readAstcSignature()` — 4-Byte Magic `\x13\xAB\xA1\x5C`
- **HEIC Native-Preview** analog AVIF: Blob-URL + `<img>` (Safari rendert HEIC nativ ✓); bei `img.onerror` (Chrome) Fallback-Label "HEIC (kein Browser-Preview in Chrome)".
- **Routing-Reihenfolge in `analyzeTexture()`**: PNG → JPEG → WebP → KTX2 → AVIF → HEIC → TIFF → ASTC → Extension-Fallback.
- **Extension-Filter** um `.heic` und `.astc` erweitert (beide Texture-Entry-Loops).
- **Synthetische Headless-Tests** für alle vier Reader (5 Cases, kein USDZ-Wrapper nötig).

### Architecture
- **ADR-31** (OpenUSD-Texture-Spec-Vollständigkeit, 2026-05-06): Kein Real-World-Use-Case in 6 Kunden-Files — aber OpenUSD-USDZ-Spec listet HEIC/KTX2/TIFF/ASTC als erlaubt. AVIF-Pattern aus v0.25.4 skaliert 1:1. KTX2/TIFF/ASTC: Format-Label only, kein Polyfill (Single-File-Anker ADR-PC5). Bundle-Wachstum: ~60 Zeilen.

### Notes
- Headless-Pool **13/13 PASS** (Pool unverändert) + **5/5 synthetische Reader-Tests** = **18/18 Cases gesamt**.
- Inspector ist jetzt das erste Web-USDZ-Tool mit kompletter OpenUSD-Spec-Texture-Coverage.

---

## [0.25.4.1] — 2026-05-06

### Fixed
- **PDF-Header dynamisch** (ADR-30): `INSPECTOR_VERSION` von `'0.25'` auf `'0.25.4.1'` — jetzt immer synchron mit Version-Badge. Alle jsPDF-Aufrufe (Header, Footer, Provenance-Text) nutzen dieselbe Konstante; kein weiteres Hardcoding.
- **Cross-Browser-PDF-Download** (ADR-30): `doc.save()` / `dataurlnewwindow`-Safari-Weiche durch Anchor-Click-Pattern ersetzt (`doc.output('blob')` → `URL.createObjectURL` → `a.click()` synchron im Click-Handler → `revokeObjectURL`). Safari öffnet keinen neuen Tab mehr, direkter Download in Chrome + Safari.
- **Cache-Tooltip präzisiert** (ADR-30): i18n-Key `cache_clear_title` DE: "Lokal gespeicherte Manifest-IDs aus signierten USDZs löschen" / EN: "Locally stored manifest IDs from signed USDZs (clear)". Button-Text "Cache (N)" unverändert.

### Architecture
- **ADR-30** (PDF-Output-Polish, 2026-05-06): Anchor-Click muss synchron im User-Click-Handler laufen — Safari blockt bei async (User-Activation fehlt). Safari-UA-Weiche aus v0.25 entfernt; Variante A (Anchor-Click) Cross-Browser sauber.

### Notes
- Headless-Pool-Test **13/13 PASS** (inkl. `DIEGOsat_TK_280426_01.usdz` nachgereicht + Erwartung definiert).

---

## [0.25.4] — 2026-05-06

### Changed
- **Severity-Recalibration: 2 Regeln 🔴→🟠** (ADR-28): Real-World-Sweep 2026-05-05 mit 6 viSales-Kunden-/Demo-USDZs zeigte 100% Trefferquote bei `STRUCTURE_DEFAULT_PRIM_MISSING` (6/6 Files) und `STRUCTURE_NESTED_USDZ` (Frankfurt) — alle Files laufen auf iPhone in AR Quick Look. Inspector zeigte fälschlich "AR Quick Look bricht". Beide Regeln auf `warn` heruntergestuft. Auch das signierte DIEGOsat-Demo-File war betroffen.
- **3-Stufen-Banner: "Läuft mit Vorbehalt"** (ADR-28): Orange-Banner-Text von "Funktioniert mit Caveats" auf **"Läuft mit Vorbehalt"** (DE) / **"Runs with caveats"** (EN) aktualisiert. Banner-Logik war bereits 3-stufig; i18n-Text jetzt akkurat.

### Added
- **AVIF-Texture-Detection + Native-Preview** (ADR-29): `readAvifSignature()` liest ISOBMFF-ftyp-Box (Bytes 4–11), erkennt `avif`- und `avis`-Brand. `analyzeTexture()` routet AVIF jetzt per Extension-Match ODER Magic-Bytes-Match. Native-Browser-Preview via Blob-URL + `<img>` (Chrome ✓, Safari 16.4+ ✓); bei `onerror` Fallback auf Label "AVIF (kein Browser-Preview)". Extension-Filter für Texture-Entries um `.avif` erweitert.

### Architecture
- **ADR-28** (Severity-Recal, 2026-05-06): Validator-Severity gegen Apple-Realität kalibriert. `STRUCTURE_DEFAULT_PRIM_MISSING` und `STRUCTURE_NESTED_USDZ` von `error` auf `warn`. Empirische Basis: 6 echte Kunden-Files, alle laufend auf iPhone. Inspector-USP gestärkt: Severity-Aussagen sind jetzt praxisvalidiert, nicht Spec-theoretisch.
- **ADR-29** (AVIF-Detection, 2026-05-06): Magic-Bytes-Reader für AVIF-Signature. Native-Preview-Versuch mit Fallback. HEIC/KTX2/TIFF/ASTC verschoben in Backlog (kein Use-Case in Real-World-Sweep).

### Notes
- Headless-Pool-Test **12/12 PASS** (7 Original + 5 Real-World-Files mit aktualisierten Severity-Erwartungen).
- `DIEGOsat_TK_280426_01.usdz` fehlt noch im Pool — wird separat nachgereicht.
- Polish-Bugs (PDF-Header-Version, Safari-PDF-Download, Cache-Counter-UX) kommen separat in v0.25.4.1.

---

## [0.25.3] — 2026-05-05

### Fixed
- **EN-Toggle browser-übergreifend repariert** (ADR-27): Die Drop-Zone (Titel, Untertitel, Button), der Footer und der Cache-Button-Tooltip waren statisch als DE-HTML hart kodiert — kein `t()`-Aufruf, kein DOM-Update bei Page-Load. `CURRENT_LANG` und `localStorage` funktionierten korrekt, aber die sichtbaren UI-Elemente blieben DE. Diagnose-Befund: **Hypothese E** (I18N-Map unvollständig für initiale UI, statische HTML-Texte nicht per `t()` verbunden). Fix: 5 neue I18N-Keys (`drop_title`, `drop_sub`, `drop_btn`, `footer_text`, `cache_clear_title`) + `id`-Attribute auf betroffene DOM-Elemente + `t()`-Calls bei Page-Load (analog bestehendem PDF-Button-Pattern). 15 Zeilen, kein Architektur-Anker berührt.

### Architecture
- **ADR-27** (EN-Toggle-Befund, 2026-05-05): Hypothese E bestätigt (Browser-Console-Verifikation + Code-Analyse). Statische HTML-Elemente der Initial-UI nicht an das `t()`-System angebunden. Fix folgt dem bestehenden Inline-i18n-Pattern (ADR-4 v0.22, ADR-7 v0.22.1) — kein Build-Step, kein Bundle-Split.

### Notes
- Headless-Pool-Test 7/7 PASS (Toggle ist UI-Feature, kein Validator-Impact).
- Safari-Cross-Browser-Test: Pflicht vor Push (Duke bestätigt).

---

## [0.25.2] — 2026-05-04

### Removed
- **QR-Code-Brücke zurückgezogen** (ADR-26 / ADR-PC5): Das in v0.25 eingebaute Desktop/Android-QR-Feature ist mit den Architektur-Ankern technisch unvereinbar. Drag&Drop-USDZs haben keine öffentliche URL, die ein iPhone erreichen könnte — QR-Code öffnet nur die Inspector-Seite, nicht die USDZ in AR Quick Look. Alle vier geprüften Alternativen (Data-URI, Blob-URL, Service-Worker-Cache, Temp-Upload) scheitern an Single-File / No-Backend / Privacy-First-Ankern. Empirisch belegt via Spike-Sandbox (`inspector-spikes/`).
  - `loadQrLib()` + `_qrScriptInjected` entfernt
  - CDN-Lazy-Load `qrcode-svg@1` entfernt (kein externer `script-src` mehr für diesen Pfad)
  - CSS-Klassen `.qr-wrap`, `.qr-wrap svg`, `.qr-placeholder` entfernt
  - I18N-Keys `preview_section_label_qr`, `preview_qr_title`, `preview_qr_sub`, `preview_qr_tip`, `preview_qr_loading` entfernt
  - ~58 Zeilen weniger, keine neuen Dependencies

### Added
- **iOS AR-Test-Hilfe** (ersetzt QR-Block, gleicher Platz): Strukturierter Hilfe-Block mit Titel und nummerierter Anleitung (AirDrop / iCloud Drive / Mail) — drei Wege, die USDZ auf das iPhone zu bringen, damit AR Quick Look beim Tap automatisch startet. DE + EN i18n.

### Architecture
- **ADR-26** (QR-Code-Rollback, 2026-05-04): Bug aus v0.25-Real-World-Test: QR zeigt Inspector-URL, nicht USDZ — AR Quick Look startet nicht. Spike-Auswertung bestätigt: alle QR-Varianten für Drag&Drop-USDZs technisch unmöglich. Feature ersatzlos zurückgezogen, iOS-Hilfe-Block als Privacy-First-konformer Ersatz.
- **ADR-PC5** (Architektur-Anker schlägt Feature, 2026-05-04): Wenn ein Feature einen Architektur-Anker bricht, fliegt das Feature — nicht der Anker. Die Anker (100% client / Single-File / Privacy-First / no-backend) sind das viSales-Differenzierungsmerkmal.

### Notes
- Headless-Pool-Test 7/7 PASS (Validator unverändert, reiner UI-Cut).
- iOS-Live-Test nicht erforderlich — v0.25.2 ändert keine iOS-spezifischen Code-Pfade (nur Desktop-UI-Cut + Hilfe-Text). `<model-viewer>`-Pfad unverändert.

---

## [0.25] — 2026-05-04

### Added
- **Geometry Stats (10 Kennzahlen)** — Neue Sektion "Geometrie · Asset-Kennzahlen" direkt unter dem Trust-Banner. Kompakte 2-Zeilen-Stat-Card-Tabelle (je 5 Werte): Geoms, Polys (Tris), Vertices, Materials, Prims / Joints, UV-Sets, Subdivision, Time-Range, FPS.
  - USDA: Vollscope-Parsing über alle Member im ZIP (Sublayer-Traversal). Explizite `def Mesh`-Prims: Polycount via tri-fan (`faceVertexCounts`), Vertex-Count via `points`-Array. Prozedurale Prims (`def Sphere`, `def Cube`, `def Cylinder` etc.) werden als Geom-Count gezählt, Poly/Vertex-Felder zeigen `proc`.
  - USDC (binär): Alle nicht-extrahierbaren Werte als `?` — kein Crash. Hinweis "USDC binär — Werte nicht extrahierbar".
  - Statische Assets: Time-Range = `static`, FPS = `—`.
- **iOS 3D-Preview via `<model-viewer>`** — Auf iOS Safari: Conditional-CDN-Lazy-Load von `@google/model-viewer@4` (~150 KB, MIT). `<model-viewer ar ar-modes="quick-look" camera-controls>` mit USDZ-Blob-URL. AR-Button automatisch aktiv — öffnet AR Quick Look direkt.
- **Desktop/Android QR-Code-Brücke** — Auf nicht-iOS: Conditional-CDN-Lazy-Load von `qrcode-svg@1` (~5 KB, MIT). QR-Code generiert `window.location.href` vollständig client-side (Privacy-First, kein Server-Roundtrip). Hint-Text leitet Konferenz-Besucher zum iPhone.
- **USDZ Blob-URL Lifecycle** — Blob-URLs werden beim ↩-Reset freigegeben (kein Memory-Leak). Neuer Drop revoked vorherige URL automatisch.

### Architecture
- **ADR-21** (3D-Preview iOS-only via Feature-Detection, 2026-05-04): `<model-viewer>` zeigt USDZ nur auf iOS Safari. GLB-Konvertierung im Browser wäre möglich (three-usdz-loader), braucht aber SharedArrayBuffer + COOP/COEP-Header (auf GitHub Pages problematisch). iOS-only + QR-Bridge ist konferenz-tauglich und täuscht nicht.
- **ADR-22** (model-viewer als Conditional-CDN-Lazy-Load, 2026-05-04): ~150 KB only-on-iOS via `<script type="module">`. Kein Always-Load — Desktop-User zahlen 0 KB extra.
- **ADR-23** (QR-Code via qrcode-svg, Conditional auf nicht-iOS, 2026-05-04): ~5 KB SVG-Output, client-side, kein externer Roundtrip. Vier externe Deps insgesamt (JSZip, jsPDF, model-viewer, qrcode-svg), nie alle gleichzeitig aktiv.
- **ADR-24** (Geometry-Vollscope 10 Kennzahlen, 2026-05-04): `extractGeometryStats(memberHashes)` summiert über alle USDA-Member. Bei USDC-Heuristik: `?` statt Crash. `proc`-Label für prozedurale Prims (Sphere/Cube). Pattern für v0.26 (Composition Explorer) etabliert.

### Notes
- Headless-Pool-Test 7/7 PASS (Geometry-Stats sind Browser-only, Headless-Validator nicht betroffen).
- iOS-Live-Test (Phase 5.7) ist optional — kein iPhone griffbereit. Code baut Best-Effort-Logik, Live-Test folgt separat.
- Pattern für v0.28 (Konferenz-QR-Pack) etabliert: QR-Generator und Conditional-CDN-Load ab jetzt im Inspector-Vokabular.

---

## [0.24.1] — 2026-05-03

### Added
- **Multi-File-Drop** — Mehrere USDZs gleichzeitig in die Drop-Zone ziehen (oder per File-Picker auswählen). Inspector zeigt gestapelte Mini-Dashboards vertikal: je File Trust-Banner, Manifest-ID und kompakte Texture-Liste mit Channel-Badges. Drop-Zone-Subtitle aktualisiert auf "mehrere USDZs gleichzeitig möglich".
- **Cross-Reference-↻-Cards im Multi-Drop** — Direkte Session-Erkennung ohne Cache-Lookup: wenn ein Derived-Manifest `parent_manifest_id` auf ein anderes Manifest im selben Drop zeigt, erscheint eine ↻-Card oberhalb der Mini-Dashboards. Test: DIEGOsat_master + DIEGOsat_master_marketing → Cross-Reference erkannt.
- **Texture-Status-Refinement** — Drei semantisch saubere Kategorien statt globalem "unknown"-Fallback:
  - `used` — Channel-Badge (Diffuse/Normal/…) wie bisher
  - `unused` (gelb-grau, Hint-Style) — Texture liegt im ZIP, wird von keinem Material referenziert. Tooltip: "Texture orphaned".
  - `unknown` (rot-grau, Bug-Style) — Texture ist via `inputs:*.connect` verbunden, aber Input-Alias nicht in `CHANNEL_ALIASES`. Echtfehler im Inspector → Alias-Lücke. Tooltip sagt es klar.
- **Test-Asset-Sync** — Headless-Pool und Browser gegen neue DIEGOsat-Files (CLI-Plan-Chat Cross-Sync 2026-05-03). Neue manifest_ids: `visales-2026-05-bbeb` (Master), `visales-derived-f555` (Marketing-Tochter). `hull.usda` hat jetzt `normal3f inputs:normal.connect → NormalTex`.

### Fixed
- `INSPECTOR_VERSION` war auf `'0.23'` eingefroren — jetzt `'0.24.1'` (war v0.24-Slip, wo die Version-Badge bereits auf `v0.24` gesetzt war, aber die JS-Konstante nicht).

### Architecture
- **ADR-18** (Multi-Drop-Layout: gestapelt vertikal, 2026-05-03): Konsistent mit ADR-3 aus v0.22.2. Side-by-Side auf v0.25/v0.26 verschoben.
- **ADR-19** (Texture-Status: drei Kategorien used/unused/unknown, 2026-05-03): `buildChannelMap` gibt jetzt `{channelMap, unknownMap}` zurück. `renderTexturesSection` und `render` akzeptieren `channelInfo`-Objekt. Backwards-kompatibel via instanceof-Guard.
- **Phase 5.4 (Channel-Parser-Type-Erweiterung) entfallen**: Verifikation (Phase 5.0) ergab, dass `normal3f inputs:normal.connect` bereits korrekt erkannt wird — der Connect-Regex matcht type-agnostisch auf `inputs:(\w+)\.connect`. Kein ADR-20.

### Notes
- Multi-Drop nutzt localStorage-Cache aus v0.22.2 (Cache-Key `usdseal-inspector.cache.v1`): jede geladene Datei wird gecacht. Die ↻-Cross-Reference-Card im Multi-Drop läuft jedoch direkt über Session-Vergleich, nicht über Cache.
- Headless-Pool-Test 7/7 PASS (Multi-Drop und Texture-Status sind Browser-only, kein Headless-Pfad betroffen).

---

## [0.24] — 2026-05-03

### Added
- **Texture Modal** — Klick auf ein Thumbnail öffnet ein Vollbild-Modal via Browser-nativem `<dialog>`-Element. Backdrop (semi-transparent), Bild mit Schachbrett-Hintergrund, ESC / ✕-Button / Backdrop-Click zum Schließen.
- **Download-Button im Modal** — `<a download="filename">` mit Original-Dateinamen direkt aus dem ZIP-Pfad. Kein separater Upload oder Server-Roundtrip.
- **PBR Channel Detection** — Inspector erkennt für jede Textur den Material-Channel via `inputs:*.connect`-Parsing aller USDA-Dateien im ZIP. 10 Channels: Diffuse, Normal, Roughness, Metallic, Emissive, Occlusion, Opacity, Displacement, Subsurface, Clearcoat. Fallback: "unknown" für Texturen ohne erkannte Binding.
- **Channel-Badges** — Farbcodierte Badge-Labels in der Texture-Card (Warm-Tech-Palette, je Channel eigene Farbe).
- **Alias-Map** — `CHANNEL_ALIASES` deckt gängige USDA-Varianten ab: `diffuseColor`/`baseColor`/`albedo` → Diffuse, `metallic`/`metalness` → Metallic etc. Erweiterbar ohne Architektur-Änderung.

### Architecture
- **ADR-15** (`<dialog>`-Element statt Custom Div, 2026-05-03): Browser-nativ, A11y-konform, ESC built-in, Backdrop automatisch. Browser-Support seit 2022 (Chrome 37+, Firefox 98+, Safari 15.4+). Pattern wiederverwendbar in v0.27 (Diff-View).
- **ADR-16** (Channel-Erkennung im bestehenden USDA-Parser, 2026-05-03): Erweiterung von `parseUsdaMetadata` — kein separater Walker. Refactor zu eigenem Material-Walker frühestens v0.26 (Layer-Stack). Single-Code-Path bleibt intakt.
- **ADR-17** (Alias-Map für Channel-Inputs, 2026-05-03): `CHANNEL_ALIASES`-Objekt deckt UsdPreviewSurface- und MaterialX-nahe Konventionen ab. Fallback "unknown" für nicht erkannte Inputs — keine stillen Fehlklassifikationen.

### Notes
- Channel-Erkennung liest ALLE USDA-Dateien im ZIP (nicht nur Root-Layer) — erforderlich weil Material-Bindings typischerweise in Sub-Layern liegen.
- Memory-Leak: Modal-Close revoke-t keine eigene Blob-URL (Modal teilt die Thumbnail-URL). `resetDash()` schließt Modal vor Blob-URL-Revoke.
- Headless-Pool-Test 7/7 PASS unverändert (Channel-Detection ist Browser-only, kein Headless-Pfad betroffen).

---

## [0.23] — 2026-05-03

### Added
- **PDF Audit Report** — Button *"PDF Report ↓"* in der Topbar (erscheint nach USDZ-Load). Generiert clientseitig ein strukturiertes A4-PDF ohne Server-Roundtrip. Dateiname-Pattern: `{usdz-name}-inspector-report-{YYYYMMDD}.pdf`.
- **Cover + Datei-Identität** — Titel, Dateiname, SHA-256-Prefix, Dateigröße (komprimiert + unkomprimiert), Manifest-ID, Generierungs-Zeitstempel, Inspector-Version.
- **Trust-Status-Banner im PDF** — farbiger Roundrect-Block (grün/orange/rot/grau) analog zum UI-Banner, mit Klartext-Erklärung und Mini-Stats-Zeile (Tracked / Mismatch / Extra / Missing / Structure).
- **Asset-Inventory-Tabelle** — manuell via `jsPDF.text()/line()` gerendert (Option A / ADR-12). Spalten: Dateiname, Größe, SHA-256-Prefix (8 Zeichen), Status. Mismatch- und Missing-Zeilen rot hinterlegt. Lange Pfade werden front-truncated (`...suffix`).
- **AR Quick Look Findings** — sortiert nach Severity → Category → ID (ADR-10). Pro Finding: Severity-Badge (farbig), Regel-ID, Kategorie, Klartext-Erklärung, Fix-Hinweis. Leerer Befund erscheint als kompakte Inline-Notiz.
- **Provenance-Timeline** — konditionell (nur wenn Manifest vorhanden). Chronologische Step-Liste mit Tool-Pille, Actor, Timestamp, Notes.
- **Lineage-Karte** — konditionell. Master-Modus: `import_history[]`-Einträge. Derived-Modus: `parent_manifest_id`, SHA-256, Exporter-Meta, Classifications.
- **Disclaimer-Block** (ADR-13) — immer am Ende jedes Reports. DE: *"Hash-Integrität gegen Manifest verifiziert. Kryptographische Signatur-Authentizität: nicht geprüft -- geplant für Inspector v0.3."* EN analog. Kein Apache-2.0-Verweis im Disclaimer.
- **Footer pro Seite** — `USDseal Inspector v0.23 | {filename} | Page X of Y` (Post-Pass via `doc.setPage()`).
- **Sprach-Switch** — PDF folgt UI-Sprache (DE/EN-Toggle).
- **Safari-Fix** — Safari blockiert `a.click()` auf Blob-URLs nach synchroner Berechnung (Gesture-Timeout). Fallback: `doc.output('dataurlnewwindow')` öffnet PDF im neuen Tab, User speichert via Cmd+S.
- **Fließendes Layout** — keine erzwungenen Seitenumbrüche zwischen Sektionen. `chk(n)` prüft vor jedem Block ob Platz reicht, `np()` nur bei echtem Überlauf. Ergebnis: 1–2 Seiten statt 4 für typische USDZ-Files.

### Architecture
- **ADR-11** (jsPDF 3.0.3, 2026-05-03): jsPDF (MIT, ~130 KB, CDN `cdnjs.cloudflare.com`) als zweite externe Dep nach JSZip. 100% client-side. Kein Server-Roundtrip. Single-File-Versprechen bleibt — jsPDF via CDN-Script-Tag.
- **ADR-12** (Tabellen-Strategie: pures `jsPDF.text()/line()`, 2026-05-03): keine AutoTable-Plugin-Dep. Manuelle Spalten mit Farbcoding. Volle Kontrolle über Severity-Markierungen.
- **ADR-13** (Disclaimer-Pflicht in jedem PDF, 2026-05-03): Bis v0.3 verifiziert Inspector nur Hash-Integrität, nicht Signatur-Authentizität. Disclaimer transparent und zwingend in jedem Report.
- **ADR-14** (kein SVG-Logo-Cover in v0.23, 2026-05-03): Deferred auf v0.24. jsPDF SVG-Embed erfordert zusätzliche Evaluierung — nicht blockend für v0.23.

### Notes
- Bundle-Größe: ~100 KB (jsPDF kommt via CDN, nicht in den inline-Bundle).
- Umlaut-Rendering: jsPDF Helvetica (WinAnsi-Encoding) unterstützt alle Latin-1-Zeichen — ä, ö, ü, ß werden korrekt dargestellt.
- Headless-Pool-Test 7/7 PASS unverändert (PDF-Generierung ist Browser-only).

---

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
