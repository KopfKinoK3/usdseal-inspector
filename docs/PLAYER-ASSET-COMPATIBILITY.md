# Player Asset Compatibility — USDseal Inspector Advanced

**Stand:** v0.28.0.3 · 2026-05-25  
**Renderer:** Three.js USDLoader r184  
**Quelle:** Empirischer Spike gegen 6 Real-World-Assets + Three.js Issue-Tracker

---

## Drei Klassen

### ✓ PASS — Rendert zuverlässig

Asset-Eigenschaften:
- Root-USD ist eine **self-contained USDC** (groß, >1 MB, die Geometrie ist direkt eingebettet)
- Keine Kompositions-Arcs (keine `references`, keine `variantSetNames` im Root-Layer)
- Keine eingebetteten Sub-USDZ
- Datei-Größe unter 20 MB
- Wenige USDC-Dateien (1 USDC = ideal)

Beispiel-Typ: Pixar-Stil-Assets, einfache Produkt-Scans mit einer Geometrie und Standard-PBR-Materialien.

**Bekannte PASS-Assets aus dem Test-Pool:**
- `SalmonPastaWithInfo.usdz` — 5 MB, 1 USDC (4.6 MB self-contained), 4 JPG-Texturen
- `AR-Wohnzimmer-_12_01_2022.usdz` — 14.9 MB, 1 USDC (3.3 MB), keine Arcs

---

### ⚠ CAUTION — Rendert möglicherweise, mit Einschränkungen

Asset-Eigenschaften:
- Datei-Größe > 20 MB (große self-contained USDC)
- 2–4 USDC-Module im ZIP
- Komplexe PBR-Materialien (ORM-Texturen, kombinierte Channels)

Erwartetes Verhalten: Geometrie rendert sichtbar, aber Materialien können dunkler erscheinen als auf dem echten Gerät. Browser-Performance kann bei sehr großen Assets leiden.

**Bekannte CAUTION-Assets:**
- `DIEGOsat_TK_280426_01.usdz` — 26 MB, 1 USDC (21.5 MB), ORM-Textur → Geo OK, Material dunkel
  - Root-USDC ist self-contained aber nutzt `material0_occlusion_roughness_metallic.png` (kombinierter PBR-Channel, Three.js parst ihn nicht vollständig)

---

### ⊘ BLOCK — Rendert nicht zuverlässig

#### BLOCK-Grund A: Eingebettete Sub-USDZ

Das USDZ enthält verschachtelte `.usdz`-Dateien. Three.js USDLoader kann nicht in eingebettete ZIP-Archive recursen — externe Komponenten fehlen im Render.

Beispiel: `Frankfurt_Varianten_TK_271125_01.usdz` (enthält `0/ID_Leg_5_Star.usdz`, `0/TischMicro.usdz`)

#### BLOCK-Grund B: Viele USDC-Module (≥ 5)

Das USDZ ist eine Multi-Komponenten-Szene mit 5 oder mehr USDC-Dateien. Three.js löst die Kompositions-Arcs zwischen den Modulen nicht auf — ein Teil der Szene fehlt oder ist leer.

Beispiel: `Vitra_ID_Demo_TK_201125_01.usdz` (10 USDC-Module), `Frankfurt_Varianten_TK_271125_01.usdz` (21 USDC-Module)

#### BLOCK-Grund C: Tiny-Coordinator-USDC mit Kompositions-Arcs

Die Root-USDC-Datei ist sehr klein (<100 KB) und enthält `references`- oder `variantSetNames`-Einträge. Das bedeutet: der Root-Layer ist ein Koordinator, die eigentliche Geometrie liegt in externen Dateien, die Three.js nicht auflöst.

Ergebnis: schwarzes Canvas (RENZ-Muster) oder leeres Canvas (keine Fehlermeldung, nur leere Szene).

**Bekannte BLOCK-Assets:**
- `RENZ_Showtime_Demo.usdz` — Root-USDC 3.8 KB mit `variantSetNames` + `references` → schwarz, kein Toast
- `Vitra_ID_Demo_TK_201125_01.usdz` — Root-USDC 13.6 KB mit `references` + `variantSelection`, 10 USDC → BLOCK
- `Frankfurt_Varianten_TK_271125_01.usdz` — 21 USDC + 2 eingebettete USDZ → BLOCK

---

## Warum das so ist

Three.js USDLoader r184 hat fundamentale Grenzen bei USD Composition Arcs:

- **Variants werden ignoriert.** `variantSet`-Definitionen werden nicht aufgelöst — der Loader nimmt den `defaultVariant` oder rendert gar nichts.
- **References werden nicht verfolgt.** Externe Dateipfade in `references`-Arcs werden nicht geladen.
- **Sub-USDZ werden nicht ausgepackt.** Verschachtelte ZIP-in-ZIP-Strukturen werden übersprungen.
- **Payloads/SubLayers werden ignoriert.** Multi-Layer-Komposition bleibt unvollständig.

Diese Einschränkungen betreffen genau die Asset-Klasse, die im B2B-Vertrieb Standard ist: Produktkonfiguratoren mit Variants, Multi-Modell-Szenen, modulare Asset-Bibliotheken.

**Konsequenz für den Inspector:** Die 3D-Preview ist Demo-Klasse für einfache Assets. Für vollständige B2B-Variant-Vorschau → USDconfig.

---

## USDconfig als Lösung

Für Assets der BLOCK-Klasse (insbesondere Variants-Assets) bietet **USDconfig** eine Lösung außerhalb des Browsers:

> *USDconfig wandelt durch eine non-web-software erst ein solches asset um. diesen prozess kann man nicht via dem kostenlosen USDseal Inspector umsetzen.*

USDconfig konvertiert Variants-Assets in eine playerbare Einzelform — dieser Prozess läuft nicht im Browser, sondern als Desktop-Software.

→ [Mehr zu USDconfig](https://kopfkinok3.github.io/USDconfig-demo-player/landingpage/deutsch/)

---

## v0.29 Ausblick

Falls Three.js USDLoader für die B2B-Asset-Klasse strukturell unzureichend bleibt, wird v0.29 die Renderer-Frage neu stellen:
- `usd-wasm` (WebAssembly-Wrapper für OpenUSD — volle Variants-Unterstützung, aber deutlich größerer Bundle)
- Babylon.js mit USD-Import-Plugin
- `model-viewer` (Google, WebXR-fokussiert)

→ Entscheidung nach Analyse der Spike-Daten aus v0.28.0.3 und User-Feedback-Sammlung.

---

*Doku: Maid Evelyn — v0.28.0.3 Spike 2026-05-25*
