# Changelog — USDseal Inspector

All notable changes to this project will be documented in this file.

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
