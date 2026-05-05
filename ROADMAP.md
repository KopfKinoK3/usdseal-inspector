# USDseal Inspector — Roadmap

**Repo:** [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)
**Live:** [kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/)
**Aktueller Stand:** v0.25.3 (EN-Toggle browser-übergreifend repariert, released 2026-05-04, Commit `fe5fa87`). Patch-Welle v0.25.4/.5 in Vorbereitung.
**Maintainer:** viSales GmbH (Mitglied Alliance for OpenUSD)
**Lizenz:** Apache 2.0
**Stand dieses Dokuments:** 2026-05-04

> Übergeordnete Roadmap. Detail-Briefings pro Release liegen als
> `docs/ROADMAP-v0.21.md`, `docs/ROADMAP-v0.22.md` etc.

---

## 1. Mission & Positionierung

Der USDseal Inspector hat **zwei Hüte**, die parallel bedient werden:

1. **USDseal-Verifikation** — prüft signierte USDZ-Dateien (C2PA-analoge Provenance für 3D-Assets, Ed25519 / COSE_Sign1). Aktuell der einzige sichtbare Web-Viewer dieser Art am Markt.
2. **Allgemeiner USDZ-Inspektor** — niedrigschwelliges Onboarding-Tool für Konferenzbesucher, Grafiker, Blender-/Unity-/Unreal-Anwender. Schließt die Lücke zwischen *"USD-Talk verstanden"* und *"selbst was tun können"*, ohne dass Omniverse, Mac-Setup oder CLI nötig ist.

**Strategischer Kern:** Senkt die Einstiegshürde zu OpenUSD nach Konferenzvorträgen massiv. Zwischen Bühne und *"selbst gemacht"* sollen 30 Sekunden statt 30 Minuten liegen.

**Tagline (englisch, für Repo / Slides):**
> *The USD Swiss Army knife for non-technical B2B users — browser-based, no install, no Omniverse setup.*

---

## 2. Marktlücke / Abgrenzung

| Tool | Was es tut | Was es nicht tut |
|---|---|---|
| **NVIDIA Omniverse Composer** | Volle DCC-Suite mit umfassender GUI | Schwerer Install, Windows + NVIDIA-GPU, Overkill für Inspektion |
| **Apple Reality Composer Pro** | USDZ-Authoring auf Mac | Nur macOS, keine Inspektion fremder Files mit Validierung |
| **Pixars `usdview`** | Standard-Viewer | Lokaler Install, technisch, keine Web-Variante |
| **needle-tools, ponahoum, usdz-viewer.net, imagetostl** | Web-basierte 3D-Preview | Zeigen das Modell, sagen aber nicht, **warum** AR Quick Look streikt; keine Provenance / keine Signatur-Verifikation |
| **USDseal Inspector** | Inspektion + Validierung + Provenance + AR-Quick-Look-Diagnose, browserbasiert | DCC-Funktionen — bewusst kein Konkurrent zu Omniverse / Reality Composer |

**Positionierung in einem Satz:**
> Schlankes Web-Tool für B2B-Kunden, die nur 3–5 Operationen brauchen — kein DCC-Konkurrent, sondern ein USD-Schweizermesser für Nicht-Techniker.

---

## 3. Status quo (v0.22 — bereits implementiert)

**v0.2-Basis** (seit erstem Public-Release):

| Bereich | Feature |
|---|---|
| State-Detection | SIGNED / DRAFT / INVALID / NO_MANIFEST als farbcodiertes Banner |
| Hash-Verifikation | SHA-256 jeder USDZ-Member gegen `credentials/usdseal-manifest.json` |
| Asset Inventory | tracked / mismatch / extra / missing / structure |
| USD-Metadaten USDA | Regex-Parser für `defaultPrim`, `upAxis`, `metersPerUnit`, `customLayerData` |
| USD-Metadaten USDC | Best-Effort-String-Extraktion |
| Texturen | Native PNG / JPEG / WebP Reader, Live-Thumbnails |
| Manifest-Anzeige | Issuer, Lizenz, Asset-Policy, Provenance Chain, Signatur-Block |
| Distribution | GitHub Pages, Standalone-HTML, iframe-Embed |
| Architektur | 100 % Frontend, kein Backend, JSZip via CDN |

**v0.22-Sprung** (ausgeliefert gebündelt mit v0.21-Scope, 2026-05-01):

| Bereich | Feature |
|---|---|
| **Lineage-Renderer** | Master-Modus + Derived-Modus mit Role-Badge, Pfad-Breakdown, Parent-Reference, Klassifikationen. `↻ Re-Import`-Marker für zyklische Beziehungen. |
| **Provenance-Timeline** | Chronologische Liste mit Step-Badges (`sealed`/`merged`/`derived`), optional `notes`. |
| **AR-Quick-Look-Validator** | 20 Regeln in sechs Kategorien: Struktur, Texturen, Skalierung, externe Refs, Manifest, Animation, Performance. Ampel-Anzeige pro Regel mit Klartext-Erklärungen. |
| **Compat-Hint** | `spec_version`-Whitelist `["0.1", "0.2"]` mit Übergangs-Toleranz für pre-bump CLI-v0.2-Manifeste — empfiehlt `usdseal migrate`. |
| **Versions-spezifische Renderer** | `renderForSpecVersion(version, manifest)`-Pattern, kein Tolerant-Mode (siehe Inspector-ADR-3). |
| **Validator-Suppression** | ADR-6: bei strukturellem Hard-Fail werden abhängige Folgeregeln unterdrückt, um Doppel-Findings zu vermeiden. |
| **Bugfixes** | X-1 (INVALID-State bei Hash-Mismatch), W-1 (Memory-Leak in Texture-Thumbnails). |

**Bekannt offen — folgt in v0.22.1:**
- W-3: TEXTURE_PATH_ABSOLUTE Regex erweitern
- W-4: TEXTURE_NOT_IN_USDZ case-/type-/prefix-tolerant machen
- W-5/W-6: Parallel-Hashing der ZIP-Members + Loading-Indicator
- EN-Pfad: Sprach-Toggle (DE/EN) für v0.22 deaktiviert, vollständige EN-Übersetzung folgt

---

## 4. Versions-Story v0.21 → v0.3

Jedes Release hat einen **eigenen Talk-Slide**. Drei strategische Story-Punkte vorne (v0.21–v0.23), dann Komfort-Schritte, dann zwei Klimaxe (v0.29 MCP + v0.3 Crypto).

| Version | Release-Story | Scope (Kurz) | Status |
|---|---|---|---|
| ~~**v0.21**~~ | ~~*Sieht jetzt, was die CLI baut*~~ | Lineage-Panel, Provenance-Timeline, spec_version-Compat | ✅ ausgeliefert gebündelt mit v0.22 (2026-05-01) |
| **v0.22** | *Warum streikt AR Quick Look?* — **USP** | AR-Quick-Look-Validator + alle v0.21-Inhalte + ADR-6 Validator-Suppression + X-1/W-1 Bugfixes | ✅ released 2026-05-01 |
| **v0.22.1** | *Polish & Polyglot* | EN-Translation-Pfad, W-3/W-4-Fixes, Worker-Pool, Sortier-Refinement | ✅ released 2026-05-02 |
| **v0.22.2** | *Sieht jetzt auch die Schleifen* | Re-Import-↻-Detection via localStorage-Cache (Single-Drop), Multi-Drop nach v0.24.1 verschoben, Toleranz pending CLI-SP-11 | ✅ released 2026-05-02, Tag online |
| **v0.23** | *Audit-Report für B2B* | PDF-Report via jsPDF + Layout-Fix + Safari-Fix + ADR-11-14 | ✅ released 2026-05-02, Tag online (Commit `c3f16cf`) |
| **v0.24** | *Klick & sieh* | Thumbnail-Vollbild-Modal + Texturen-Channel-Erkennung (10 PBR-Channels + Fallback) + ADR-15/16/17 + IIFE-Bug-Fix | ✅ released 2026-05-03, Tag online (Commit `03e9cd48`) |
| **v0.24.1** | *Multi-Asset im Blick* | Multi-File-Drop (gestapelt vertikal) + Texture-Status-Refinement (used/unused/unknown) + Test-Asset-Sync. ADR-18/19. Phase 5.0 zeigte: Channel-Parser war schon type-agnostisch → ADR-20 entfallen. Plus `detectCrossRefsInSession` Path B (derived→master) für leeres Master-`lineage:{}`. | ✅ released 2026-05-03, Tag online (Commit `67fe5419`) |
| **v0.25** | *Was ist das Modell?* | Geometrie-Vollscope (10 Kennzahlen inkl. Time-Range/FPS für AR-Animation) + iOS-only 3D-Preview via `<model-viewer>` (Conditional-CDN-Load) + Desktop-QR-Code-Brücke (qrcode-svg). ADR-21-24. iOS-Live-Test ausgelassen (kein iPhone griffbereit, ADR-PC4 Best-Effort). | ✅ released 2026-05-04, Tag online (Commit `76c550a8`) |
| **v0.25.2** | *QR-Code zurückgezogen — ehrlich Privacy-First* | **Pivot-Release nach Spike-Auswertung 2026-05-04.** QR-Code-Workflow war mit Architektur-Ankern (100% client / Single-File / Privacy-First) **technisch unvereinbar** — Drag&Drop-USDZs haben keine öffentliche URL, die ein iPhone erreichen kann. Lösung: QR-Feature ersatzlos rausgebaut, stattdessen UI-Hilfe "So testest du AR Quick Look auf iOS" (AirDrop / iCloud Drive / Mail). Plus Mini-Polish: `by viSales GmbH`-Space-Fix + Cache-Counter nur > 0 zeigen. ADR-PC5 etabliert die Pivot-Disziplin. | ✅ released 2026-05-04, Tag online (Commit `ff8e208`), Briefing `docs/ROADMAP-v0.25.2.md` |
| **v0.25.3** | *Polyglot wirklich* | EN-Toggle Browser-übergreifend repariert (Bug 1 aus v0.25-Real-World-Test). Phase 5.0 Diagnose ergab **Hypothese E** mit Sub-Variante: statische HTML-Elemente waren nicht per `t()` angeschlossen — I18N-Map war vollständig, aber Buttons/Headlines/Banner-Texte lasen die Werte nie. Fix: 5 I18N-Keys + 5 DOM-IDs + 5 `t()`-Calls, ~15 Zeilen. ADR-27 dokumentiert. **Umnummeriert** von ursprünglich v0.25.1. | ✅ released 2026-05-04, Tag online (Commit `fe5fa87`) |
| **v0.25.4** | *Validator kalibriert + AVIF angekommen* | **Refaktoriert nach Real-World-Sweep 2026-05-05:** Severity-Recalibration als Hauptanteil (2 Regeln 🔴→🟠) + AVIF-Detection als Bonus (Frankfurt hat 15× AVIF). 3-Stufen-Severity-Banner. 6 echte Kunden-Files als Test-Pool (`severity-pool/`). HEIC/KTX2/TIFF/ASTC verschoben in Backlog (kein Use-Case). ADR-28 + ADR-29. Diagnose-Quelle: `tests/real-world-2026-05-05.md`. | geplant, 1–1.5 Tag, Briefing in `docs/ROADMAP-v0.25.4.md` |
| **v0.25.4.1** | *Drei Mini-Bugs aus dem Sweep* | UX-Polish-Patch: (1) PDF-Header dynamisch aus Versions-Badge (statt hardcoded `v0.25`), (2) Safari-PDF-Download via Anchor-Click-Pattern (Variante A erst, Browser-Weiche B als Fallback), (3) Cache-Counter-Tooltip präzisieren. ADR-30. | geplant, 0.3–0.5 Tag, Briefing in `docs/ROADMAP-v0.25.4.1.md` |
| **v0.26** | *Komposition entwirrt + PDF aufgeholt* | Layer-Stack, References, Payloads, Variants als Baum + **PDF-Template-Erweiterung** um Channel-Erkennung (v0.24), Geometry-Stats (v0.25), AVIF (v0.25.4) und kalibriertes Severity-Mapping (v0.25.4) — der v0.23-PDF-Builder hinkt aktuell hinterher und zeigt nur den damaligen Stand. Plus: ADR-Diskussion zur USDC-Material-Heuristik (Befund aus 26 MB Real-World-TK-Asset). **Backlog-Aufnahme:** HEIC/KTX2/TIFF/ASTC Spec-Vollständigkeit (kein Use-Case in 6 Real-World-Files, aber Spec-konform). | geplant, 3–4 Tage |
| **v0.27** | *Beweise, was sich geändert hat* | Diff-View bei Hash-Mismatch (Bytes / Texturen-Auflösung) | geplant, 1–2 Tage |
| **v0.28** | *Trag den Inspector überall hin* | README-Embed-Sektion mit Konsumer-Inline-Boilerplate (`<usdseal-inspector>`-Custom-Element via iframe-Wrapper, ~10 Zeilen Copy-Paste). Plus QR-Code-Konferenz-Pack als separates kleines HTML. **Inspector-Code unverändert** — Single-File-Anker bleibt für immer. Web-Component-Pattern wird **dokumentiert**, nicht **distributed**. | geplant, 1–2 Tage |
| **v0.29** | *AI-agent-fähig* — **Konferenz-Klimax** | MCP-Server-Wrapper als **eigenes Repo** `usdseal-inspector-mcp` | geplant, 3–5 Tage |
| **v0.3** | *Trust wird wahr* | Ed25519-WebCrypto-Verify + Batch-Analyse mit CSV-Export | geplant, 4–6 Tage |

**Bisher geliefert:** v0.21 → v0.25.3 in 10 Releases (2026-05-01 bis 2026-05-04). **Nächster Sprint:** v0.25.4 Severity-Recal + AVIF (refaktoriert nach Real-World-Sweep), gefolgt von v0.25.4.1 Polish-Patch. **Total verbleibend:** ~24–36 Build-Tage über v0.25.4 → v0.3.

---

## 5. Architektur-Optionen für tiefere USD-Analyse

Aktuell arbeitet der Inspector mit String- und Regex-Analyse. Für **echte USD-Komposition** (References, Payloads, Variants auflösen, Layer-Flattening) reichen Regex-Parser nicht. Drei Wege:

### Option A — Bleibt rein im Browser

USDA via Regex/Klammer-Zähler, USDC via String-Scan. Erweiterungen rein in JS.

- **Pro:** Keine Architektur-Änderung, GitHub Pages reicht.
- **Grenze:** Komposition (Sublayers / References / Variants auflösen) bleibt unmöglich.
- **Status:** Default für v0.21–v0.29.

### Option B — `usd-wasm` im Browser

WASM-Builds der USD-Bindings (z. B. `lighttransport/tinyusdz` mit JS-Binding, oder Autodesks WASM-USD via `needle-tools/usd-viewer`).

- **Pro:** Volle Komposition im Browser, Privacy-First-Versprechen bleibt.
- **Contra:** +5–15 MB Bundle, SharedArrayBuffer / COOP-COEP-Header (auf GitHub Pages problematisch).
- **Status:** Kandidat für v0.4+ wenn Komposition zum Pflicht-Feature wird.

### Option C — Optionales Python-Backend mit `pxr`-Bindings

Wrapper um Pixars offizielle USD-Pythonbindings. Lokal als Service oder serverseitig.

- **Pro:** Maximaler Funktionsumfang. Synergie mit MCP-Server (v0.29) und Sealer-Tool — gleicher Stack.
- **Contra:** Bricht *"kein Install"* wenn lokal genutzt.
- **Status:** Teilen sich Stack mit MCP-Wrapper und potenziellem Sealer.

### Empfehlung

**Hybrid:** Browser-only bleibt Default für 90 % der Use-Cases. Tiefere Komposition kommt entweder via usd-wasm (v0.4+) oder via Python-Backend (gemeinsam mit MCP-Server). **Frontend bleibt aber immer vorrangig browserbasiert** — das ist das viSales-Differenzierungsmerkmal gegenüber Omniverse & Co.

---

## 6. Konferenz-Story-Bogen

Drei Phasen für drei Vortrag-Generationen:

- **v0.21–v0.23 (Foundation):** *"Vom Hash-Check zur Audit-Story"* — Lineage sichtbar, AR-Quick-Look diagnostiziert, PDF-Report für Compliance.
- **v0.24–v0.28 (Reach):** *"Vom Inspektor zum Embed"* — UX-Polish, Komposition entwirrt, Web Component für überall einbettbar.
- **v0.29 + v0.3 (Klimax):** *"Vom Tool zum AI-Agent-Asset"* — MCP-Server macht den Inspector AI-aufrufbar, Crypto-Verify schließt den Trust-Anker. **Das ist die Story-Klimax, die kein anderer Anbieter im OpenUSD-Ökosystem aktuell erzählen kann.**

---

## 7. Architektur-Entscheidungen (verbindlich)

### Was bleibt
- **100 % Frontend** für die Inspektor-Web-App — keine Datenübertragung, Privacy-First.
- **Single-File `index.html`** — eine Datei, lokal öffenbar, embedbar. **Single-File-Anker gilt für immer.** Web-Component-Embed (ab v0.28) erfolgt via Konsumer-Inline-Boilerplate (Custom-Element-Wrapper um iframe, lebt beim Konsumer-Code, nicht im Inspector-Repo). Kein zweites Distribution-File, keine Hybrid-Welle, kein Build-Tool.
- **JSZip** als einzige externe JS-Abhängigkeit im Browser-Pfad.
- **Apache 2.0** Lizenz.
- **Kein User-Account, kein Login, keine Telemetrie.**

### Was kommt dazu (versionsweise)
- **WebCrypto** (nativ, keine Lib) — ab v0.3.
- **`<model-viewer>`** als optionale CDN-Abhängigkeit — ab v0.25.
- **jsPDF** als optionale CDN-Abhängigkeit — ab v0.23.
- **Optionales Backend** ausschließlich für MCP-Server (separates Repo `usdseal-inspector-mcp`) — ab v0.29.

### Was nicht kommt
- Kein eigener User-Account, kein Login.
- Kein File-Upload zu fremden Servern.
- Keine Telemetrie / Analytics.

### Schema-Compatibility-Strategie

Inspector folgt der **CLI-Schema-Disziplin** (CLI-ADR §11.14, accepted 2026-05-01):

- **Versions-spezifische Renderer**, nicht Toleranz-Modell. Code-Pattern: `renderForSpecVersion(version, manifest)` mit klar getrennten Render-Pfaden pro Version.
- **Explizite Whitelist** statt Wildcard. Pro Inspector-Release wird die Whitelist um neue `spec_version`-Werte erweitert, sobald CLI sie ausliefert.
- **Forward-Compat:** Inspector zeigt bei unbekannter `spec_version` einen gelben Hint, render-best-effort, **keine** Render-Crashes (anders als CLI, die `verify` bei unbekannter Version verweigert — Inspector ist Read-Only-Tool und darf weicher reagieren).
- **Übergangs-Toleranz** für pre-bump-Bestandsmanifeste fällt schritteweise raus, sobald CLI-Migrate-Welle (CLI-SP-11) durch ist.

Detaillierte Regeln pro Sprint im jeweiligen `docs/ROADMAP-v0.XX.md`.

---

## 8. Begleit-Initiativen außerhalb des Inspector-Repos

- **`usdseal-cli`** (privat) — produziert die Manifeste, die der Inspector verifiziert. Eigene Roadmap unter `04-roadmap-v03-c2pa.md` (CLI v0.3 = C2PA-Voll-Integration).
- **`usdseal-inspector-mcp`** (geplant, eigenes öffentliches Repo) — MCP-Server-Wrapper. Trigger ab Inspector v0.29.
- **`usdseal-sealer`** (Park-Doku, separates Tool) — Web-SaaS für Sealing als Counterpart zum Inspector. Detail in `05-roadmap-usdseal-sealer.md`.
- **`visales.de/usdseal/`** — Landingpage / Doku-Hub (parallel).

---

## 9. Detail-Briefings pro Release

Jeder Sprint bekommt eine eigene Datei `docs/ROADMAP-v0.XX.md` mit:
- Scope (was inhaltlich rein muss)
- Externe Quellen (Libraries, Specs)
- Architektur-Optionen für diesen Sprint
- Vorbedingungen (was vorher klar sein muss)
- Phasen-Schätzung
- Pre-Build-Steps
- Decision-Log-Template

Aktuell vorhanden:
- `docs/ROADMAP-v0.21.md` — Lineage Visibility (✅ released gebündelt mit v0.22)
- `docs/ROADMAP-v0.22.md` — AR-Quick-Look-Validator (✅ released)
- `docs/ROADMAP-v0.22.1.md` — Polish & Polyglot (✅ released)
- `docs/ROADMAP-v0.22.2.md` — Re-Import-Detection (✅ released)
- `docs/ROADMAP-v0.23.md` — PDF Audit Report (✅ released)
- `docs/ROADMAP-v0.24.md` — Texture Modal + Channel Detection (✅ released)
- `docs/ROADMAP-v0.24.1.md` — Multi-File-Drop + Status-Refinement + Test-Asset-Sync (✅ released 2026-05-03)
- `docs/ROADMAP-v0.25.md` — Geometry Vollscope + 3D-Preview iOS-only + QR-Code-Brücke (✅ released)
- `docs/ROADMAP-v0.25.2.md` — QR-Code-Pivot (✅ released 2026-05-04, Commit `ff8e208`, ADR-PC5)
- `docs/ROADMAP-v0.25.3.md` — EN-Toggle Hotfix (✅ released 2026-05-04, Commit `fe5fa87`, ADR-27, Hypothese E)
- `docs/ROADMAP-v0.25.4.md` — Severity-Recal + AVIF-Detection (📋 Vorbereitung, ADR-28 + ADR-29)
- `docs/ROADMAP-v0.25.4.1.md` — Polish-Patch (📋 Vorbereitung, ADR-30 — folgt nach v0.25.4)
- `tests/real-world-2026-05-05.md` — Real-World-Test-Sweep mit 6 Kunden-Files als Diagnose-Quelle für v0.25.4
- ~~`docs/ROADMAP-v0.25.5.md`~~ — *gestrichen, Severity-Recal-Inhalt wandert in v0.25.4 (refaktoriert)*

**Sandbox-Spikes für v0.25.2** (Lessons-Learned: Architektur-Konflikt → Pivot, Negativ-Beleg):
- `inspector-spikes/spike-b-url-parameter.html` — Variante B: `?url=...`-Parameter, clientseitiges Fetch
- `inspector-spikes/spike-c-direct-ar.html` — Variante C: Direct AR Quick Look via `rel=ar` + QR
- `inspector-spikes/README.md` — Test-Plan + Befund: Drag&Drop-USDZs sind nicht QR-fähig

Folge-Briefings werden geschrieben, sobald der jeweilige Sprint startet. Vorlauf: ~1 Tag Briefing-Zeit vor Build-Start reicht.

---

## 10. Offene Fragen aus dem Spaziergang-Plan

1. **`<model-viewer>` USDZ-Support:** funktioniert auf iOS Safari (Quick Look). Auf Desktop/Android wird USDZ nicht direkt gerendert — entweder GLB-Konvertierungs-Tool ergänzen oder *"iOS-only Preview, sonst nur Metadaten"* dokumentieren.
2. **Three.js + GitHub Pages:** SharedArrayBuffer-Header (COOP/COEP) sind auf GitHub Pages problematisch. Falls v0.25 Three.js-Inspector-Modus bekommt → eigener Hostpfad oder Service-Worker-Workaround.
3. **MCP-Server-Hosting:** selbst hosten (Hetzner / Render / Cloudflare Workers) oder als npm-Package zum Self-Hosting?
4. **AR-Quick-Look-Regelwerk:** Apples Anforderungen ändern sich mit jeder iOS-Version. Versioniertes Regelwerk im Inspector.
5. **MCP-Tool-Granularität:** ein großes `inspect_usdz` oder feinere Tools (`verify_signature`, `list_textures`, `validate_arkit`)?

---

## 11. Quellen / Referenz-Links

### Specs
- [OpenUSD Specification](https://openusd.org/release/index.html)
- [USDZ Asset Format](https://openusd.org/release/spec_usdz.html)
- [Alliance for OpenUSD (AOUSD)](https://aousd.org)

### Verwandte Tools / Marktlücken
- [needle-tools/usd-viewer](https://github.com/needle-tools/usd-viewer)
- [ponahoum/usdz-web-viewer](https://github.com/ponahoum/usdz-web-viewer)
- [Apple AR Quick Look Validator (`usdARKitChecker`)](https://developer.apple.com/augmented-reality/quick-look/)

### Inspector
- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)
- [Live: kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/)

---

**Ende Master-Roadmap.** Nächster Schritt: `ROADMAP-v0.21.md` für Lineage-Visibility-Sprint reviewen, dann Build-Chat öffnen.
