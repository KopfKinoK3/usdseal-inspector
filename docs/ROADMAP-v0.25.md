# Roadmap v0.25 — Geometry Stats & 3D-Preview

**Status:** Vorbereitungs-Dokument · 2026-05-04
**Story-Slot:** *"Was ist das Modell?"* — vom Material-Inspektor zum Asset-Inspektor
**Ziel:** Inspector zeigt **Geometrie-Kennzahlen** (Vollscope) plus **iOS-natives 3D-Preview** via `<model-viewer>`. Auf Desktop/Android: ehrlicher Hinweis + QR-Code-Brücke zum iPhone des Konferenzbesuchers.
**Aufwand:** 2.5–3 Tage konzentrierter Build.

> Erster Story-Release nach v0.24/v0.24.1 (UX-Polish-Welle). Master-Übersicht in `../ROADMAP.md`.

---

## 1. Scope

### 1.1 Geometrie-Kennzahlen (Vollscope, alle ~10 Werte)

Inspector erweitert den USDA-Parser (analog zur Channel-Erkennung in v0.24) um Geometrie-Walking. Pro Asset werden gerendert:

| Kennzahl | Quelle (USDA) | Aggregation |
|---|---|---|
| **Polycount (Tris)** | `int[] faceVertexCounts` pro Mesh | Sum (Triangle = 3 vertices, Quad = 6 vertices über tri-fan) |
| **Vertex-Count** | `point3f[] points` pro Mesh | Sum array length |
| **Mesh-Count** | `def Mesh "..."` Zähler | Count |
| **Material-Count** | `def Material "..."` Zähler (siehe v0.24-Parser) | Count |
| **Joint/Bone-Count** | `def SkelRoot` + `def Skeleton` mit `uniform token[] joints` | Sum array length pro Skeleton |
| **Time-Range** | `startTimeCode` / `endTimeCode` aus Layer-Header | Read attribute |
| **FPS** | `timeCodesPerSecond` aus Layer-Header | Read attribute |
| **Prim-Count** | Alle `def`-Statements | Count |
| **UV-Sets** | `texCoord2f[] primvars:st` / `:st_0` / `:st_1` etc. pro Mesh | Sum unique-Sets pro Asset |
| **Subdivision-Level** | `uniform token subdivisionScheme` (none / catmullClark / loop) | Read pro Mesh, summieren |

**Edge-Cases:**
- USDC (binär) — Heuristik-String-Extraktion wie v0.22, kein voller binärer Parser. Wenn Werte nicht extraherbar: Zelle als `?` rendern, kein Crash.
- USDA mit Sublayer (DIEGOsat-Pattern: master.usda → hull/inner) — Walker durchläuft alle Sublayer und summiert.
- Animation: Time-Range nur anzeigen wenn `startTimeCode` oder `endTimeCode` gesetzt. Bei statischen Assets: *"static"* statt Range.

**UI-Render:** Kompakte Tabelle (5 Spalten, 2 Zeilen) unter dem Trust-Status-Banner, **vor** Asset-Inventory. Nutzt Warm-Tech-Stat-Card-Pattern aus AR-Quick-Look-Diagnose-Block.

### 1.2 3D-Preview via `<model-viewer>` (iOS-only, conditional)

**Plattform-Realität:**
`<model-viewer>` zeigt USDZ **nur auf iOS Safari** via Quick Look. Auf Desktop/Android/Firefox-iOS wird der Tag zu einem stummen Placeholder. v0.25 macht das **transparent** statt zu täuschen.

**Implementation:**

1. **Feature-Detection** beim Page-Load:
   ```js
   const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
              && /Safari/.test(navigator.userAgent)
              && !/CriOS|FxiOS/.test(navigator.userAgent);
   ```

2. **Wenn iOS:**
   - `<model-viewer>`-Script via CDN nachladen (lazy):
     `https://cdn.jsdelivr.net/npm/@google/model-viewer@4/dist/model-viewer.min.js`
   - `<model-viewer src="blob:..." ar ar-modes="quick-look" camera-controls>` einsetzen
   - Inline unter Trust-Banner gerendert
   - AR-Button automatisch aktiv (model-viewer bringt Quick-Look-Auslöser mit)

3. **Wenn nicht iOS:**
   - Block mit Klartext: *"3D-Preview ist auf iOS Safari verfügbar. Öffne diese Seite auf iPhone/iPad für AR Quick Look."*
   - **QR-Code** der aktuellen URL — Konferenzbesucher scannt mit iPhone, USDZ-Demo läuft dort
   - Plus dezent: *"Tip: bring this URL to an iPhone for the live AR preview."*

**Zwecks Konferenz-Use-Case:** Pattern setzt schon Architektur für **v0.28-QR-Code-Pack** — gleicher Generator-Code, andere Inhalte.

### 1.3 QR-Code-Generierung

QR-Code-Generierung im Browser, kein Server-Roundtrip. Drei Optionen:

- **A)** Inline-Implementation (~30–50 Zeilen Code, ECI-Mode-Encoder + Reed-Solomon) — riskant, Test-Heavy
- **B)** [`qrcode-svg`](https://www.npmjs.com/package/qrcode-svg) (~5 KB, MIT, keine externen Deps) — sauber, klein
- **C)** [`qrcode.js`](https://github.com/davidshimjs/qrcodejs) (~10 KB, MIT, Canvas-basiert) — klein

**Empfehlung:** **B** (qrcode-svg) — SVG ist zoom-fest, Inspector hat schon SVG-Pattern. Plus: SVG-Output integriert sich nahtlos ins DOM, kein Canvas-Boilerplate.

**Lazy-Loading:** Nur laden, wenn Desktop-User aufs USDZ klickt (oder direkt beim Render der QR-Card). Keine 5 KB für iOS-User, die den QR gar nicht brauchen.

---

## 2. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| JSZip | bereits eingebunden | Reicht für USDZ-Parsing. |
| jsPDF 3.0.3 | bereits eingebunden (v0.23) | Reicht. |
| **`<model-viewer>` v4** | **NEU in v0.25 (conditional)** | ~150 KB, MIT, CDN: `cdn.jsdelivr.net/npm/@google/model-viewer@4/dist/model-viewer.min.js`. Nur auf iOS via Feature-Detection geladen — nicht im Default-Bundle. Single-File-Anker bleibt unverletzt (kein neues File im Repo, dritte Dep ist conditional CDN-Load). |
| **`qrcode-svg`** | **NEU in v0.25 (conditional)** | ~5 KB, MIT, CDN: `cdn.jsdelivr.net/npm/qrcode-svg@1/dist/qrcode-svg.min.js`. Nur auf nicht-iOS geladen (umgekehrte Conditional). |

**Architektur-Anker bleibt:** Single-File `index.html`, 100% Frontend. Beide neuen Deps sind **CDN-Conditional-Lazy-Loads**, also nie im Default-Bundle. Inspector im File-Download (`file://`) funktioniert weiterhin — nur die 3D-Preview/QR-Card-Sektion bleibt auf Standalone-iOS leer (Standalone+iOS+file:// ist sehr exotisch und kein Use-Case).

---

## 3. Architektur-Optionen

### 3.1 Geometry-Parser

**Option A — Erweiterung des bestehenden USDA-Parsers (Empfehlung)**
Konsistent mit v0.24-ADR-16 (Channel-Erkennung im selben Parser). USDA-Walker durchläuft Sublayer, summiert pro Asset.

**Option B — Eigener Walker-Klasse**
Klare Trennung von Material- und Geometrie-Walking. Mehr Code, sauberer.

**Empfehlung:** **A**. Single-File-Disziplin gilt weiter, Walker-Refactor erst in v0.26 (Komposition braucht ohnehin tieferes Walking).

### 3.2 3D-Preview-Mount-Strategie

**Option C — Conditional Lazy-Load via `<script>`-Tag-Injection (Empfehlung)**
Beim Page-Load wird je nach iOS-Detection ein dynamischer `<script src="...model-viewer..."></script>` ins `<head>` eingefügt. ES-Module-Import oder klassisches Script-Tag — beides ok.

**Option D — Always-Load**
model-viewer immer laden, aber Tag nur auf iOS rendern.

**Empfehlung:** **C**. 150 KB on-demand statt always-load — schneller initialer Page-Render auf Desktop, kein Verschenken.

### 3.3 QR-Code-Pattern

**Option E — Inline qrcode-svg auf Desktop (Empfehlung)**
Lazy-Load nur auf nicht-iOS, generiert SVG mit aktueller `window.location.href`. Render in Hint-Block.

**Option F — Externe QR-API (z. B. Google Charts)**
Server-Roundtrip, schneller in Code, aber bricht Privacy-First-Anker (URL geht an Google Charts).

**Empfehlung:** **E**. Privacy-First gilt — keine externen Roundtrips für triviale QR-Generierung.

---

## 4. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.24.1 stabil released | ✓ — Tag online seit 2026-05-03 |
| 2 | Geometry-Kennzahlen-Set entschieden (Vollscope C) | ✓ — Plan-Chat 2026-05-04 |
| 3 | 3D-Plattform-Strategie entschieden (D Hybrid mit QR-Brücke) | ✓ |
| 4 | model-viewer als Conditional-Dep entschieden (C iOS-only Lazy) | ✓ |
| 5 | UI-Position entschieden (A unter Trust-Banner) | ✓ |
| 6 | QR-Code-Library entschieden (qrcode-svg, Option E) | ✓ |
| 7 | Test-USDZ mit Geometry-Daten verfügbar | ✓ — DIEGOsat (Sphere-Mesh, Cube-Meshes) für Polycount/BBox-Tests |

**7 von 7 grün — startklar für Build-Chat.**

---

## 5. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.1 USDA-Parser-Geometrie-Erweiterung** | 0.75 Tag | Walker für Polycount, Vertex-Count, Mesh-Count, Material-Count, UV-Sets, Subdivision-Level, Time-Range, FPS, Prim-Count, Joint-Count. Sublayer-Traversal. USDC-Best-Effort (Heuristik). |
| **5.2 Geometry-Stats-UI-Render** | 0.5 Tag | Kompakte Stat-Card-Tabelle unter Trust-Banner, vor Asset-Inventory. Warm-Tech-Stil, responsive auf Mobile. |
| **5.3 iOS-Feature-Detection + model-viewer-Conditional-Load** | 0.25 Tag | UA-Sniffing für iOS Safari, Lazy-Script-Injection. |
| **5.4 model-viewer-Mount + Blob-URL-Verdrahtung** | 0.5 Tag | `<model-viewer src="blob:..." ar ar-modes="quick-look" camera-controls>` einsetzen. Blob-URL-Lifecycle (revoke bei neuem Drop). |
| **5.5 Desktop-Hint-Block + QR-Code** | 0.5 Tag | qrcode-svg lazy-laden, SVG-QR generieren mit `window.location.href`, Hint-Text DE+EN. |
| **5.6 Test gegen review-pool/** | 0.25 Tag | DIEGOsat-Files: Geometry-Stats verifizieren (Sphere=Polycount, Cubes=Quads, Skel-Joints in NDA?). Alle Pool-Files durchspielen. |
| **5.7 iOS-Live-Test** | 0.25 Tag | iPhone mit der GitHub-Pages-URL öffnen — model-viewer + AR-Button funktional? **Wichtig:** ohne iPhone-Zugriff fällt diese Phase aus, dann Code muss Best-Effort-Logik einbauen und User testet später live. |
| **5.8 Headless-Pool-Regression** | 0.1 Tag | 7/7 PASS bleibt. Geometry-Stats sind Browser-Feature, beeinflussen Headless-Validator nicht. |
| **5.9 README + CHANGELOG-Update** | 0.25 Tag | v0.25-Eintrag, Geometry-Tabelle in Feature-Liste, iOS-3D-Preview-Hinweis, ADR-21 bis ADR-24 verlinken. |
| **5.10 Snapshot + Tag** | 0.25 Tag | `archive/snapshots/v0.25-snapshot.html`, Tag, Push. |

**Total: 2.6–2.85 Tage**, je nach iOS-Verfügbarkeit für Phase 5.7.

---

## 6. Strategischer Hebel

v0.25 ist Story-Release mit drei Hebeln:

1. **Asset-Inspektor-Vollkreis.** Inspector zeigt jetzt: Material (v0.24), Texturen (v0.22-v0.24), Provenance/Lineage (v0.21), AR-QL (v0.22), PDF-Audit (v0.23), **Geometrie + Preview (v0.25)**. Damit ist die *"was ist drin in dieser USDZ"*-Frage end-to-end beantwortet.

2. **Konferenz-Demo-tauglich auf jedem Device.** Desktop-User auf der Konferenz: scannt QR-Code → iPhone öffnet → AR Quick Look läuft. Pattern, das **kein anderes Web-Inspektor-Tool** so elegant löst (andere zeigen "USDZ wird nicht unterstützt"-Fehler).

3. **Pattern für v0.28 etabliert.** QR-Code-Generator und Conditional-CDN-Load sind ab heute im Inspector-Vokabular. v0.28 kann diese Mechanik direkt für das Konferenz-Pack nutzen.

---

## 7. Konkrete Pre-v0.25-Steps

### 7.1 Geometry-Test-Anker im DIEGOsat verifizieren (5 Minuten)

USDA-Files extrahieren und manuell zählen:
- `hull/hull.usda`: 1× `def Sphere "HullMesh"` → 1 Mesh, 1 Material (`HullMaterial`)
- `inner/inner_cad.usda`: 1× `def Cube "CADBox"` → 1 Mesh, 1 Material
- `inner/inner_nda.usda`: 1× `def Cube "NDABox"` → 1 Mesh, 1 Material
- Total: **3 Meshes, 3 Materials**, statisch (kein Time-Range), keine Joints

Diese Werte sind die Erwartung im Headless-Pool-Test (Phase 5.6).

### 7.2 model-viewer-CDN-URL + Lizenz finalisieren (5 Minuten)

- Version 4 ist aktuell stabil
- MIT-Lizenz, kompatibel mit Apache 2.0
- CDN: `https://cdn.jsdelivr.net/npm/@google/model-viewer@4/dist/model-viewer.min.js`
- Dokumentation: [modelviewer.dev](https://modelviewer.dev/)

### 7.3 qrcode-svg-CDN finalisieren (5 Minuten)

- Stable: 1.x
- MIT
- CDN: `https://cdn.jsdelivr.net/npm/qrcode-svg@1/dist/qrcode.min.js`

### 7.4 iOS-Detection-Strategie (10 Minuten)

User-Agent-Sniffing ist erprobt und für unseren Use-Case ausreichend:

```js
const isIOSSafari = (() => {
  const ua = navigator.userAgent;
  return /iPad|iPhone|iPod/.test(ua)
      && /Safari/.test(ua)
      && !/CriOS|FxiOS/.test(ua); // Chrome/Firefox auf iOS auschließen
})();
```

Edge-Case: iPad in *"Request Desktop Site"*-Modus zeigt Mac-UA — würde fälschlich als nicht-iOS erkannt. Das ist akzeptabel: iPad-Desktop-Mode-User sehen den QR-Code, der zur iPad-Seite linkt, scannen ihn nicht (sind ja schon dort), aber finden über den Hint-Block den Hinweis und können *"Request Mobile Site"* aktivieren. Kleiner UX-Bumper, kein Showstopper.

---

## 8. Decision-Log-Template

```markdown
### ADR-21 3D-Preview iOS-only via Feature-Detection — 2026-05-XX

**Kontext:** `<model-viewer>` zeigt USDZ nur auf iOS Safari. GLB-Konvertierung im Browser via three-usdz-loader ist möglich, aber braucht SharedArrayBuffer + COOP/COEP-Header (auf GitHub Pages problematisch) und ist Test-/Wartungs-aufwendig.
**Entscheidung:** model-viewer wird nur auf iOS Safari conditional geladen. Auf Desktop/Android: ehrlicher Hinweis-Block + QR-Code zur iOS-Brücke.
**Begründung:** Plattform-Realität ehrlich darstellen statt mit GLB-Hack täuschen. QR-Code-Brücke ist Konferenz-tauglich und löst den Use-Case ohne komplexen Konvertierungs-Code.
**Konsequenz:** Pattern für v0.28 (Konferenz-QR-Pack) etabliert. Single-File-Anker bleibt — model-viewer ist CDN-Conditional, kein neues File im Repo.

### ADR-22 model-viewer als Conditional-CDN-Lazy-Load — 2026-05-XX

**Kontext:** model-viewer ist ~150 KB. Always-Load würde initial-Page-Render auf Desktop unnötig verlangsamen.
**Entscheidung:** Lazy-Script-Injection nach Page-Load + iOS-Detection. Nur auf iOS wird der Script-Tag eingefügt.
**Konsequenz:** Inspector-Bundle bleibt klein für Desktop-User (95% der Konferenz-Besucher beim Erst-Drop). model-viewer wird *On-Demand* auf iOS aktiviert.

### ADR-23 QR-Code via qrcode-svg, Conditional auf nicht-iOS — 2026-05-XX

**Kontext:** Desktop-User braucht QR-Code für iOS-Brücke, iOS-User braucht ihn nicht.
**Entscheidung:** qrcode-svg (~5 KB, MIT, SVG-Output) wird umgekehrt-conditional geladen — nur auf nicht-iOS. SVG-Pattern integriert sich nahtlos ins DOM, keine Canvas-Boilerplate.
**Konsequenz:** Vier externe Deps insgesamt (JSZip, jsPDF, model-viewer, qrcode-svg), aber nie alle gleichzeitig — pro Plattform sind nur 2–3 aktiv. Privacy-First gewahrt (kein externer QR-API-Roundtrip).

### ADR-24 Geometry-Vollscope (10 Kennzahlen) — 2026-05-XX

**Kontext:** Plan-Chat-Wahl zwischen PBR-Core, Erweitert, Vollscope. viSales-Pipeline arbeitet mit Time-Range für AR-Sequenzen — Vollscope ist berechtigt.
**Entscheidung:** Alle 10 Kennzahlen rendern: Polycount, Vertex-Count, Mesh-Count, Material-Count, Joint/Bone-Count, Time-Range, FPS, Prim-Count, UV-Sets, Subdivision-Level. Bei nicht-extrahierbaren Werten (USDC-Heuristik): `?` statt Crash.
**Konsequenz:** Inspector wird Asset-Inspektor mit voller Coverage. AR-Animation-Use-Cases (viSales-Pipeline) sind abgedeckt.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger-Briefings: `ROADMAP-v0.24.md`, `ROADMAP-v0.24.1.md`

### Externe Specs

- [`<model-viewer>` Documentation](https://modelviewer.dev/docs/index.html)
- [model-viewer GitHub (Apache 2.0 + iOS USDZ-Support)](https://github.com/google/model-viewer)
- [qrcode-svg npm](https://www.npmjs.com/package/qrcode-svg)
- [USD Mesh Schema](https://openusd.org/release/api/class_usd_geom_mesh.html)
- [USD UsdSkel API (Joints/Bones)](https://openusd.org/release/api/usd_skel_page_front.html)

### Inspector-Repo

- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)

---

**Ende v0.25-Roadmap.** Nach Build: Snapshot, Tag `v0.25`, Push. Plan-Chat schreibt dann `docs/ROADMAP-v0.26.md` (Composition Explorer — Layer-Stack, References, Variants als Baum).
