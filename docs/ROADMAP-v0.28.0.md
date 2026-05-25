# Roadmap v0.28.0 — Two-File-Pattern + Inspector Advanced: Three.js Desktop-3D-Preview

**Status:** Vorbereitungs-Dokument · 2026-05-24
**Story-Slot:** *"Inspector kommt jetzt in zwei Geschmacksrichtungen — Standard schlank, Advanced mit Desktop-3D-Preview. Drag eine USDZ, dreh sie im Browser."*
**Ziel:** Pattern-Sprint für die Two-File-Architektur (gemeinsamer Source, Python-Build-Step, zwei Distributions-Files). Erstes Advanced-Feature: Three.js-basierte Desktop-3D-Preview, inline-eingebettet, Read-only-Orbit. Standard bleibt single-file und unverändert in Funktion; bekommt Click-Through-Button zur Advanced-URL.
**Aufwand:** M (1.5–2.5 Tage)

> Erster v0.28-Sprint. Validiert das Two-File-Pattern an einem echten Feature (nicht an einem leeren Platzhalter). Begründung Reihenfolge siehe `docs/v0.28-konsumer-patterns-backlog.md` § 3 (final 2026-05-24): Three.js zuerst, danach LLM (v0.28.1), USDC-Parser (v0.28.2), Polyfills (v0.28.3). QR-Modus-C verschoben in bezahlte Pro-Variante.

---

## 1. Befund

Stand v0.27.3 (released 2026-05-09):
- Inspector ist **single-file**, läuft 100% clientseitig, kein Backend
- Standard-Inspector deckt: Manifest-Inspektion, Verify-UI (3-Layer Bytestream Trust), Geometrie-Sektion im PDF, Texturen-Tabelle, AR-Quick-Look-Diagnose, USDC-Limitation transparent
- **3D-Preview existiert nur via iOS-Conditional-Model-Viewer** (v0.25) — Desktop-User sehen kein 3D
- Power-User-Pfad fehlt — wer "mehr" will (3D im Desktop-Browser, USDC-Material-Parsing, Format-Polyfills), bekommt heute nur Hinweis-Boxen mit "siehe Future Work"
- Konferenz-Demos (AOUSD, OpenUSD-Talks) brauchen visuellen Wow-Effekt — heute ist die Story textbasiert (Findings, Tabellen, Hash-Diff)

**Architektur-Anker-Druck:** ADR-PC5 ("Architektur-Anker schlägt Feature") hat seit v0.25.2 (QR-Pivot) konsequent jedes Feature blockiert, das Single-File-Anker, Privacy-First oder den **Schlank-Anker des Standards** bricht. Lösung war jeweils Verzicht + ehrliche Kommunikation. v0.28 löst diesen Stau strukturell auf: **zwei separate Distributions** — Standard bleibt schlank (Privacy-Reviewer-tauglich, AOUSD-Talk-Story *"100 KB Browser-Tool"*), Advanced trägt alles was Standard schwer machen würde (Three.js, später LLM-Bridge, USDC-Parser-WASM, Polyfills). Click-Through statt Bundle-Bloat im Standard.

**Wichtige Begriffsklärung 2026-05-24 (Phase 5.0):** "Advanced" bezeichnet die **Power-Distribution mit Feature-Tiefe**, nicht die "braucht mehr als 1 File"-Distribution. Ob Advanced technisch single-file oder multi-file ist, ist Implementierungs-Detail pro Sub-Sprint:
- v0.28.0 Three.js: passt in single-file via manuell konsolidiertem IIFE (~700-800 KB)
- v0.28.2 USDC-Parser: braucht definitiv multi-file (`.wasm`-Binary separat)
- v0.28.1 LLM-Bridge / v0.28.3 Polyfills: TBD pro Sprint

Der Schlank-Anker des Standards (~100-200 KB, schnell durchlesbar, Reviewer-tauglich) ist der **eigentliche Grund** für das Two-File-Pattern — nicht eine vermeintliche File-Anzahl-Notwendigkeit des Advanced.

**Marketing-Hebel — warum Three.js zuerst:** Visuell sofort verkaufbar (LinkedIn-Video, Karussell, AOUSD-Folie), schließt eine konkrete Lücke (Desktop-3D heute schwarz), kein Hosting-Stress (GitHub Pages reicht), Aufwand M. Stärkster Eyecatcher der drei Advanced-Kandidaten 3/4/2.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Vorgänger-Stand verifizieren
grep -n "INSPECTOR_VERSION" index.html | head -5
grep -n "model-viewer" index.html | head -10        # iOS-Lösung aus v0.25
grep -n "version-badge" index.html | head -5        # ADR-38-Bindung sichtbar?

# B) Repo-Struktur prüfen
ls -la                                              # gibts schon ein src/?
ls -la docs/                                        # ROADMAP-Files präsent?
ls -la archive/snapshots/                           # wie heißen v0.27-Snapshots?

# C) Bestehende CSS-Klassen für Click-Through-Button
grep -n "btn btn-" landingpage/deutsch/index.html | head -5
grep -n "class=\"btn" index.html | head -10

# D) Three.js-Realitätscheck — Phase-5.0-Befund 2026-05-24:
# - USDZLoader DEPRECATED seit r179 → USDLoader übernimmt (inkl. USDZ-Support)
# - Three.js r184 hat Issue #28693 gefixt, Loader deutlich besser
# - r184 unterstützt: Primitives, MaterialX UsdPreviewSurface, metersPerUnit
# - Vier ESM-Deps: fflate, USDAParser, USDCParser, USDComposer
# - Three Core hat UMD (three.min.js ~600 KB), Loader nicht → IIFE-Konsolidierung nötig
# - Quelle: https://threejs.org/docs/#examples/en/loaders/USDLoader
# Test: lädt der Loader DIEGOsat_master.usdz ohne Crash? Welche Channels werden gemappt?
```

→ Lokalisiert (teils Plan-Chat-Phase-5.0, teils Code-Chat-Phase-5.0):
1. INSPECTOR_VERSION-Konstante als Single-Source-of-Truth (ADR-38) — Build-Step muss das beim Generieren respektieren ✓ (Plan-Chat-Phase-5.0 bestätigt: '0.27.2' im Code)
2. CSS-Realität: Inspector hat `.btn-primary`, `.btn-reset` — **kein `.btn` oder `.btn-ghost`**. Click-Through-Button minimal nachziehen (Border + Padding inline oder neue Mini-Klasse) — kein Showstopper
3. Three.js + USDLoader-Größe ~700-800 KB konsolidiert (Bundle-Strategie Weg 2, siehe ADR-44)
4. Welche der existierenden Test-USDZs (DIEGOsat-Pool, Frankfurt, review-pool/) der USDLoader sauber rendert vs. wo er ausfällt — Pre-Renderer-Check muss das nachbauen (Code-Chat-Phase-5.0 testet live)

**Konsistenz-Check:**
- Source-File `src/inspector.html` darf bei der Build-Generierung **kein Drift** zu `index.html` aus v0.27.3 produzieren (Diff = nur Pro-Marker entfernt + Click-Through-Button eingefügt, sonst byte-identisch)
- `advanced/index.html` muss als single-file lokal-öffenbar bleiben (file:// im Safari/Chrome funktioniert, kein npm-Server nötig)
- Three.js + USDZLoader inline einbetten ohne Bundle-Tool — direkt UMD-Bundle aus three.js-Distribution in `<script>`-Tag

---

## 3. Scope

### 3.1 Build-Step (Variante Y — Python)

**Source:** `src/inspector.html` (neue Datei, Basis = v0.27.3 `index.html` + Feature-Marker)

**Marker-Pattern:**
```html
<!-- ADVANCED-ONLY:START three-js-3d -->
<!-- Block wird im Advanced-Build aktiv, im Standard-Build entfernt -->
<div id="three-js-viewer-container">...</div>
<!-- ADVANCED-ONLY:END three-js-3d -->

<!-- STANDARD-ONLY:START click-through -->
<!-- Block ist NUR im Standard-Build, im Advanced-Build entfernt -->
<a href="advanced/" class="btn btn-ghost advanced-cta">Mehr Features → Inspector Advanced</a>
<!-- STANDARD-ONLY:END click-through -->
```

**Build-Script:** `build.py` im Repo-Root.

```python
#!/usr/bin/env python3
"""
Build-Step für Inspector Standard + Inspector Advanced.
Quelle: src/inspector.html
Ziel:   index.html (Standard, ADVANCED-ONLY-Blöcke entfernt)
        advanced/index.html (Advanced, STANDARD-ONLY-Blöcke entfernt)

Marker:
  <!-- ADVANCED-ONLY:START id --> ... <!-- ADVANCED-ONLY:END id -->
  <!-- STANDARD-ONLY:START id --> ... <!-- STANDARD-ONLY:END id -->

Aufruf: python3 build.py
"""
import re
from pathlib import Path

SRC = Path("src/inspector.html")
STD = Path("index.html")
ADV = Path("advanced/index.html")
NOJEKYLL = Path(".nojekyll")

def strip_blocks(html: str, marker: str) -> str:
    pattern = re.compile(
        rf"<!--\s*{marker}:START[^>]*?-->.*?<!--\s*{marker}:END[^>]*?-->",
        re.DOTALL,
    )
    return pattern.sub("", html)

def main():
    src = SRC.read_text(encoding="utf-8")
    STD.write_text(strip_blocks(src, "ADVANCED-ONLY"), encoding="utf-8")
    ADV.parent.mkdir(exist_ok=True)
    ADV.write_text(strip_blocks(src, "STANDARD-ONLY"), encoding="utf-8")
    # Versicherungspolice: .nojekyll deaktiviert Jekyll-Filter
    # (Default-Jekyll ignoriert Verzeichnisse mit "_"-Prefix; relevant
    # falls künftige Sub-Sprints Unterordner wie advanced/_libs/ anlegen)
    if not NOJEKYLL.exists():
        NOJEKYLL.touch()
        print(f"OK: {NOJEKYLL} (created)")
    print(f"OK: {STD} ({STD.stat().st_size} B)")
    print(f"OK: {ADV} ({ADV.stat().st_size} B)")

if __name__ == "__main__":
    main()
```

**Aufruf:** `python3 build.py` vor jedem Commit. Manuelle Disziplin in v0.28.0 — GitHub-Action für CI kommt frühestens v0.28.0.1 als Polish.

**Beide Files** (`index.html` und `advanced/index.html`) werden **eingecheckt** — kein `.gitignore`-Eintrag. Begründung: GitHub Pages serviert ohne Build-Step, Reviewer können beide Stände diffen.

**Plus: `.nojekyll`-Versicherungspolice.** Build erzeugt leere `.nojekyll` im Repo-Root falls noch nicht vorhanden. Hintergrund: GitHub-Pages-Default läuft Jekyll, das Verzeichnisse mit `_`-Prefix filtert. Heute irrelevant (Advanced ist single-file, kein `_libs/`-Ordner), aber Versicherung für v0.28.1-v0.28.3 wenn doch mal Unterordner kommen. Hosting-Check 2026-05-24 bestätigte: GitHub-Pages-Default reicht für v0.28.0 — `.nojekyll` ist Defensive für die Zukunft, kein Pflicht-Setup.

### 3.2 Click-Through-Button im Standard

**Position:** Footer-Bereich, dezent. Eine Zeile, vor dem Disclaimer.

**Markup (im Source mit STANDARD-ONLY-Marker):**
```html
<a href="advanced/" class="btn btn-ghost advanced-cta">
  <span data-i18n="advanced_cta_de">Mehr Features → Inspector Advanced</span>
  <span data-i18n="advanced_cta_en" style="display:none">More features → Inspector Advanced</span>
</a>
```

**CSS:** wiederverwendet `.btn` und `.btn-ghost` aus Landingpage-Styling (Phase 5.0 grep). Falls nicht im Inspector-Standard vorhanden, minimal nachziehen (Border + Padding, kein neuer Style-Block).

**i18n:** 1 neuer Key `advanced_cta` DE+EN (`"Mehr Features → Inspector Advanced"` / `"More features → Inspector Advanced"`).

### 3.3 Inspector Advanced — Three.js Desktop-3D-Preview

**Position:** Neue Sektion nach `#manifest-info`, vor `#findings`. Klar abgegrenzt als "Inspector Advanced — 3D Preview (Beta)".

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ 🎬 3D-Preview (Beta)                            │
│ ┌─────────────────────────────────────────────┐ │
│ │                                             │ │
│ │   [Three.js Canvas — Read-only Orbit]       │ │
│ │                                             │ │
│ │     Drag: Rotate   Scroll: Zoom             │ │
│ │                                             │ │
│ └─────────────────────────────────────────────┘ │
│ ⓘ Banner: "3D-Preview Beta — Geometrie und     │
│   Standard-Materialien. Komplexe Materialien    │
│   siehe Inspection-Report unten."               │
└─────────────────────────────────────────────────┘
```

**Komponenten:**

1. **Three.js Inline-Embed:** UMD-Bundle direkt in `<script>`-Tag im Advanced-File. Aus offizieller `three.js`-Distribution. **Inline-eingebettet, nicht via CDN.** Single-File-Anker hält. Plus `USDZLoader` (separater `<script>`-Tag).
2. **Scene-Setup:** PerspectiveCamera, AmbientLight + DirectionalLight, OrbitControls (Read-only via Constraint: kein Pan).
3. **USDZ-Drop-Hook:** Bei USDZ-Drop wird **dieselbe File-Reference** vom bestehenden Drop-Handler an `USDZLoader.parse(arrayBuffer)` weitergereicht. Loader liefert `THREE.Group`, die in die Scene injiziert wird.
4. **Read-only-Orbit:** Maus-Drag = Rotation, Scroll = Zoom, Pan deaktiviert (`controls.enablePan = false`).
5. **Limit-Banner:** Über dem Canvas, immer sichtbar. Text DE+EN. Plus dezenter Link auf `#findings` für Detail-Report.
6. **Pre-Renderer-Check:** Vor dem `USDZLoader.parse` durchsucht der Inspector das USDZ-Manifest auf bekannte Limit-Trigger:
   - `variantSets[]` mit length > 0 → Warnung *"Diese USDZ enthält Variants — werden im 3D-Preview nicht aufgelöst"*
   - Animation-Tracks (USD `timeSamples` außer initial) → Warnung *"Animation wird im 3D-Preview nicht abgespielt"*
   - USDC-Binary ohne USDA-Konvertierung → Warnung *"USDC-Binary-Materialien teilweise — siehe Inspection-Report"*
   - Warnungen erscheinen als Toast über dem Canvas, bleiben sichtbar bis User wegklickt (`localStorage`-Suppression OK)

**Loading-Indicator:** Während `USDZLoader.parse` läuft, zeigt der Canvas einen Spinner + Text "3D-Preview wird gerendert…". Bei Loader-Crash: Canvas zeigt "3D-Preview konnte nicht gerendert werden — siehe Inspection-Report" + Stack-Trace in der Console (nicht User-sichtbar).

**Was NICHT in v0.28.0:**
- Material-Klick-Highlight (Mesh → Texture-Zeile) → wandert in v0.28.0.1 oder v0.28.1
- Wireframe-Toggle → v0.28.0.1
- Camera-Reset-Button → v0.28.0.1
- Multi-USDZ-Drop in 3D-View (stapelt nebeneinander) → unklar ob jemals
- Animation-Playback → eigener Sprint, nicht v0.28-Scope

### 3.4 Advanced-Header-Branding

Header der Advanced-Datei kommuniziert deutlich:
- Logo/Titel-Bereich: *"USDseal Inspector **Advanced**"* (Advanced betont)
- Version-Badge: `v0.28.0` (gleiche Konstante wie Standard, ADR-38-konform)
- Zurück-Link: Dezent neben Header, *"← Standard-Inspector"* / *"← Standard Inspector"* (1 neuer i18n-Key)

### 3.5 Was NICHT in v0.28.0

- **Keine echten neuen Features im Standard** außer dem Click-Through-Button — Standard bleibt funktional v0.27.3, bekommt nur Versions-Bump auf v0.28.0
- **Kein QR-Code** (Modus A/B/C, alle verschoben — siehe Backlog § 2D + § 3)
- **Keine LLM-Findings** — v0.28.1
- **Kein USDC-Parser** — v0.28.2
- **Keine Texture-Polyfills** — v0.28.3
- **Keine Hosting-Migration** zu media.visales.de — Advanced läuft auf GitHub Pages unter `kopfkinok3.github.io/usdseal-inspector/advanced/`
- **Kein Build-CI** (GitHub Action) — manueller `python3 build.py` reicht, CI in v0.28.0.1 oder später
- **Keine Landingpage-Sektion** *"Was kann Advanced?"* — kommt wenn das Pattern und das erste echte Feature live sind, eigener Polish-Sprint

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Three.js (r160+) | neu, inline-eingebettet | UMD-Bundle aus offizieller Distribution. ~600 KB. |
| Three.js `USDZLoader` | neu, inline | Aus `three/examples/jsm/loaders/USDZLoader.js`. ~50 KB. Read-only, Capability-Limits in Banner + Pre-Renderer-Check kommuniziert. |
| Python 3 (Build) | systemweit vorhanden | Mac-System-Python reicht. Kein venv, keine Dependencies. |
| Bestehender CSS-Stack | recycelt | `.btn` + `.btn-ghost` aus Landingpage-Styling, Inspector-Sektion-Pattern aus v0.25-v0.27 |
| JSZip | unverändert | bestehende Dependency, wird im Advanced auch genutzt |
| INSPECTOR_VERSION | ADR-38-Pattern hält | Konstante in src/inspector.html, beide Build-Outputs ziehen automatisch |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.27.3 stable released | ✓ (2026-05-09) |
| 2 | ADR-38 Version-Badge-Bindung live | ✓ (v0.26.2-Patch 2026-05-09) |
| 3 | Test-Asset-Pool 18/18 PASS in Headless | ✓ |
| 4 | Three.js USDZLoader-Capability gegen Test-Pool real getestet | ⏳ Phase 5.0 + Phase 5.4 |
| 5 | Backlog-Naming-Sweep Pro → Advanced | ✓ (2026-05-24) |

**4 von 5 grün, 1 läuft in Phase 5.0/5.4 des Sprints.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.1 Tag | grep + Three.js-USDZLoader-Capability gegen DIEGOsat-Pool + Frankfurt + review-pool real testen (vor dem Bau, nicht danach) |
| **5.1 Build-Step bauen** | 0.2 Tag | `build.py` schreiben, `src/inspector.html` aus v0.27.3-`index.html` extrahieren, Spike: leerer ADVANCED-ONLY-Marker + STANDARD-ONLY-Click-Through-Button, ein `python3 build.py`-Lauf erzeugt beide Files, Diff gegen v0.27.3 prüfen (Standard byte-identisch außer Button) |
| **5.2 Click-Through-Button im Standard** | 0.1 Tag | Footer-Markup im Source mit STANDARD-ONLY-Marker, i18n-Key `advanced_cta` DE+EN, CSS-Klassen prüfen (vorhanden / nachziehen), Build + lokal-öffnen verifizieren |
| **5.3 Three.js + USDLoader IIFE-konsolidieren** | 0.3-0.4 Tag | Vier ESM-Deps (`fflate`/`USDAParser`/`USDCParser`/`USDComposer`) plus `three.min.js` r184 holen, händisch zu IIFE-Bundle konsolidieren (ESM→IIFE-Wrapper), als `vendor/three-usdloader-r184-bundle.js` ablegen, Konsolidierungs-Anleitung in `vendor/README.md` dokumentieren, Build-Inject-Marker im Source, Größencheck, Sanity-Test "Three + USDLoader verfügbar nach Page-Load" |
| **5.4 Scene + Loader-Integration** | 0.4 Tag | Container-Div im Advanced-Source, Scene/Camera/Lights/OrbitControls-Setup, USDZ-Drop-Hook in Three.js-Pipeline einklinken, Test mit DIEGOsat (sollte funktionieren), Test mit Frankfurt (USDC-Binary — wahrscheinlich teil-broken, Pre-Renderer-Check muss greifen) |
| **5.5 Limit-Banner + Pre-Renderer-Check** | 0.2 Tag | Banner-Markup + Toast-Komponente, Manifest-Scan für Variants/Animation/USDC, i18n-Keys (4-6 neue) |
| **5.6 Advanced-Header-Branding + Zurück-Link** | 0.1 Tag | Titel anpassen, Zurück-Link, i18n-Key `back_to_standard` |
| **5.7 Browser-Verifikation** | 0.2 Tag | Standard: Chrome+Safari+Firefox, Click-Through funktioniert, kein Drift zu v0.27.3. Advanced: Chrome+Safari+Firefox, DIEGOsat dreht sich, Frankfurt zeigt Banner + best-effort Geometrie, AVIF-Texturen werden via Three.js gerendert oder grau-fallback |
| **5.8 Headless-Pool** | 0.1 Tag | 18/18 PASS bestehender Pool muss weiterhin grün — Standard-Funktionalität darf nicht regredieren. Advanced-File-Headless-Test (nur Page-Load + Three.js-globale-Verfügbarkeit + USDZLoader-instance) zusätzlich. |
| **5.9 README + CHANGELOG** | 0.1 Tag | Sprint-Eintrag in beiden Files (Standard CHANGELOG mit Pattern-Hinweis, Advanced CHANGELOG mit Feature-Liste), README-Hinweis auf Build-Step + Advanced-Pfad |
| **5.10 ADR-43** | inkludiert | Two-File-Pattern dokumentiert in CLAUDE-Inspector-private.md, plus ADR-PC5-Annotation ("Anker gilt für Standard und Advanced je single-file") |
| **5.11 Snapshot + Tag** | 0.05 Tag | Tag `v0.28.0` für commit (Standard + Advanced gemeinsam), Push, GitHub-Pages-Latenz-Hinweis |
| **5.12 Memory-Update** | 0.05 Tag | inspector_project.md ergänzt v0.28.0-Block (Pattern + Three.js), Architektur-Anker-Notiz |

**Total: 1.7–2.7 Tage** (Phase 5.3 +0.1-0.2 Tag wegen IIFE-Konsolidierung, sonst unverändert).

---

## 7. Strategischer Hebel

1. **Pattern-Validierung am echten Feature** — Build-Step beweist sich nicht an leerem Platzhalter, sondern an Three.js-Integration. Wenn das Pattern hält, sind v0.28.1/v0.28.2/v0.28.3 reine Feature-Sprints.
2. **Visueller Wow-Effekt für Marketing** — Drag USDZ → 3D-Rotation Live im Browser. LinkedIn-Video, Karussell-Post, AOUSD-Folie alle ab Tag eins drehbar. Stärkster Demo-Hebel der USDseal-Familie bisher.
3. **Lücke schließen, die Apple offen lässt** — AR Quick Look ist iOS-only, Desktop hatte bisher schwarzes Loch. Advanced füllt es. *"USDZ in Desktop-Browser — kein Plugin, kein App-Store."*
4. **Konferenz-Story komplett** — Standard für die Privacy-First/Reviewer-Schwelle-Erzählung, Advanced als Bonus-Slide mit dem visuellen Effekt. Zwei Zielgruppen, eine Codebase.
5. **Monetarisierungs-Pfad offen** — bezahlte Pro-Variante (QR-Modus-C mit Server-Backend, später) bleibt als dritte Distribution möglich. Two-File-Pattern skaliert zu Three-File-Pattern wenn Bedarf konkret.

---

## 8. Konkrete Pre-v0.28.0-Steps

1. **Three.js-Version-Entscheidung:** ✅ erledigt 2026-05-24 (Phase 5.0 Plan-Chat). **r184** — Loader-Issue #28693 gefixt, USDLoader ersetzt deprecated USDZLoader, MaterialX UsdPreviewSurface + metersPerUnit supportet.
2. **Test-Asset-Set für 3D-Capability:** DIEGOsat_master (vorhanden, Standard-Fall), Frankfurt (USDC-Binary, Edge-Case), review-pool 7 Files (Stress-Test), error_explicit.usdz (sollte sauber crashen mit Limit-Banner). Pool ist bereits da, keine neuen Assets nötig.
3. **GitHub-Pages-Pfad-Check:** ✅ erledigt 2026-05-24. Standard-Inspector live unter `kopfkinok3.github.io/usdseal-inspector/`, Subordner-Pattern beweisbar via `kopfkinok3.github.io/usdseal-inspector/landingpage/deutsch/`. Sobald `advanced/index.html` gepusht ist, ist sie unter `kopfkinok3.github.io/usdseal-inspector/advanced/` erreichbar. `.nojekyll` als Defensive im Build-Step (siehe § 3.1) für künftige Unterordner-Sprints. **Keine Hoster-Migration nötig.**

4. **Chrome MCP verbunden:** ✅ erledigt 2026-05-24. `Browser 1` (macOS, lokal) ist verfügbar — Code-Chat kann Phase 5.7 Browser-Verifikation automatisiert mitlaufen lassen.

---

## 9. Decision-Log-Template

```markdown
### ADR-43 Two-File-Pattern: Standard + Advanced aus gemeinsamer Source — 2026-05-24

**Kontext:** ADR-PC5 (Architektur-Anker schlägt Feature) hat seit v0.25.2 jedes Feature blockiert, das Single-File-Anker, Privacy-First oder den **Schlank-Anker des Standards** bricht (QR-Modus-C, USDC-Parser via usd-wasm, Three.js Desktop-3D, Texture-Polyfills, LLM-Bridge). Lösung war Verzicht + Hinweis-Box. Damit häuft sich Power-User-Schmerz und Marketing-Eyecatcher fehlen.

**Eigentliches Problem (Phase-5.0-Klärung 2026-05-24):** Nicht die File-Anzahl-Notwendigkeit des Advanced ist der Treiber — Three.js passt z. B. technisch via manuellem IIFE in single-file. Der eigentliche Treiber ist der **Schlank-Anker des Standards**: ~100-200 KB Browser-Tool, schnell durchlesbar, Privacy-Reviewer-tauglich, AOUSD-Talk-Story *"hier ist der ganze Code"*. Three.js würde diesen Anker brechen (~800 KB). Selbst wenn technisch single-file machbar, **wollen wir Three.js nicht im Standard haben**.

Alternativen geprüft:
- **Variante X (manueller Fork):** zwei Files getrennt pflegen — Drift-Risiko, ADR-38-mäßiger Bug ("Standard repariert, Advanced vergessen") garantiert
- **Variante Z (Feature-Flag):** ein File mit `IS_ADVANCED`-Konstante — Standard-File trägt unbenutzten Advanced-Code, bricht Privacy-Argument ("warum ist Three.js im Privacy-Inspector?") UND Schlank-Anker (Standard wird groß)
- **Variante Y (Build-Step):** ein Source-File mit Markern, simpler Python-Build erzeugt zwei Distributions — ein Source of Truth, kein Drift, Standard bleibt schlank, Advanced bündelt Power-Features

**Entscheidung:** Variante Y mit Python `build.py`. Source `src/inspector.html` mit `<!-- ADVANCED-ONLY:START id --> ... <!-- ADVANCED-ONLY:END id -->` und `<!-- STANDARD-ONLY:START id --> ... <!-- STANDARD-ONLY:END id -->`-Marker-Pattern. Build erzeugt `index.html` (Standard, Click-Through-Button drin) und `advanced/index.html` (Advanced, Power-Features aktiv). Gesamt-Versionsnummerierung — beide Files tragen `v0.28.0`, ein Tag, ein Push. INSPECTOR_VERSION-Konstante (ADR-38) im Source, beide Outputs ziehen automatisch.

**Begriffsklärung — "Advanced" ist Feature-Tiefe, nicht File-Anzahl:** Advanced bezeichnet die **Power-Distribution**, die Features bündelt, die Standard absichtlich schlank weglässt. Ob Advanced technisch single-file oder multi-file ist, ist Implementierungs-Detail pro Sub-Sprint:
- v0.28.0 Three.js: passt in single-file via manuellem IIFE
- v0.28.2 USDC-Parser: braucht multi-file (`.wasm`-Binary separat)
- v0.28.1 LLM / v0.28.3 Polyfills: TBD pro Sprint

**Konsequenz:** Single-File-Anker hält **für jede Distribution einzeln, wo technisch möglich** — Standard bleibt definitiv schlank und single-file, Advanced ist single-file wo passend und multi-file wo nötig. ADR-PC5 wird annotiert: "Architektur-Anker gilt pro Distribution. Standard bleibt schlank-anker-treu (~100-200 KB). Advanced darf Features bündeln, die Standard ablehnt — File-Anzahl pro Sub-Sprint nach Bedarf." Build-Step ist manuell (`python3 build.py` vor Commit) — CI-Automation kommt frühestens v0.28.0.1. Drift-Risiko durch Vergessen des Build-Laufs ist real, wird durch CHANGELOG-Eintrag-Disziplin + Sichtkontrolle (`git diff` zeigt Source UND Outputs) mitigiert.

---

### ADR-44 Three.js Desktop-3D-Preview im Inspector Advanced — 2026-05-24

**Kontext:** Standard-Inspector kann auf Desktop kein 3D zeigen (iOS-only via `<model-viewer>` aus v0.25). Power-User wollen 3D ohne iPhone-Wechsel, Konferenz-Demos brauchen visuellen Eyecatcher. Three.js r184 hat `USDLoader` (ersetzt deprecated `USDZLoader` seit r179, inkl. USDZ-Support, MaterialX UsdPreviewSurface, `metersPerUnit`). Loader-Issue #28693 ist in r184 gefixt.

**Phase-5.0-Befund 2026-05-24:** Briefing-Annahme *"USDZLoader, UMD direkt in `<script>`"* war veraltet. Realität: Three.js Core hat noch UMD (`three.min.js`, ~600 KB), aber `USDLoader` hat vier ESM-Deps (`fflate`, `USDAParser`, `USDCParser`, `USDComposer`) — kein direkter `<script>`-Embed ohne Bundle-Step. Plus: kein Node/npm im System-PATH → esbuild scheidet aus.

Alternativen geprüft:
- **Babylon.js:** breitere USDZ-Support-Lücken, andere Lern-Schwelle
- **Server-side-Rendering** (USD → glTF Convert): Privacy-Bruch, Backend-Aufwand, ADR-PC5-Verstoß
- **WebAssembly via usd-wasm:** Bundle 5-15 MB, Build-Komplexität, COOP/COEP-Header — Aufwand L, in v0.28.2 separat angegangen
- **Three.js + USDLoader inline via manuellem IIFE:** Aufwand M, Bundle ~700-800 KB, Read-only-Limits ehrlich kommunizieren, GitHub Pages reicht, alle Anker (Single-File pro Distribution / Privacy / Offline) halten

**Bundle-Strategie-Alternativen (Phase 5.0):**
- **Weg 1 Importmap + CDN:** XS Aufwand, aber bricht Offline-Anker beim Erstkontakt
- **Weg 2 Manuelles IIFE:** ~2-3h Handarbeit, reproduzierbar via Doku, alle Anker halten — **gewählt**
- **Weg 3 Service Worker:** zweites File, bricht Single-File-Anker
- **Weg 4 Python-Build bundled vendor/-Verzeichnis:** reproduzierbar via Script, aber Build-Step wird komplexer + Repo wächst um ~800 KB

**Entscheidung:** Three.js + USDLoader via **manuell konsolidiertem IIFE** (Weg 2) inline-eingebettet im Advanced-File. Vier ESM-Deps (`fflate` ~20 KB + `USDAParser` ~60 KB + `USDCParser` ~30 KB + `USDComposer` ~30 KB) plus `three.min.js` (~600 KB) händisch zu einem `<script>`-Block konsolidiert. Einmaliger Konsolidierungs-Aufwand ~2-3h in Phase 5.3. Reproduzierbarkeit via README-Doku im Repo (welche Files in welcher Reihenfolge konkateniert wurden, mit Three.js-Version-Pin). Bei Three.js-Upgrade: neue Konsolidierung nach gleicher Doku.

Read-only-Orbit (Drag = Rotation, Scroll = Zoom, Pan deaktiviert). Banner über dem Canvas kommuniziert Beta-Status und Limits. Pre-Renderer-Check scannt Manifest auf Variants/Animation/USDC-Binary und zeigt Toast-Warnung bevor Loader läuft.

**Konsequenz:** Advanced-File-Größe wächst auf ~1-1.5 MB (Three.js + USDLoader-Bundle + Standard-Inspector-Funktionalität). **Single-File-Anker hält für Advanced** (ein HTML, lokal-öffenbar via file://). Privacy-Anker hält (kein CDN-Call). Offline-Tauglich ab Tag eins (Konferenz-Stand ohne W-LAN). Loader-Crash bei Edge-Cases ist erlaubt — Canvas zeigt "konnte nicht gerendert werden", Standard-Inspection läuft daneben weiter. Marketing-Material (Video, Karussell) ist ab Tag eins drehbar. v0.28.1/v0.28.2/v0.28.3 erweitern auf dieser Basis — wenn ein Sub-Sprint multi-file braucht (z. B. v0.28.2 mit `.wasm`-Binary), ist das pro Sprint zu entscheiden, der Two-File-Pattern (Standard + Advanced) bleibt strukturell.

**Build-Step-Anpassung:** `build.py` aus § 3.1 nimmt das IIFE-Bundle aus einem Repo-Pfad (z. B. `vendor/three-usdloader-r184-bundle.js`) und fügt es im ADVANCED-Build per Marker-Substitution ein. Konkrete Marker:
```html
<!-- ADVANCED-ONLY:START three-bundle -->
<script><!-- BUILD-INJECT: vendor/three-usdloader-r184-bundle.js --></script>
<!-- ADVANCED-ONLY:END three-bundle -->
```
Build-Script ersetzt den Inject-Marker beim Bauen durch den Bundle-Inhalt. Source `src/inspector.html` bleibt lesbar (kein 600-KB-Klotz im Diff).
```

---

## 10. Quellen / Referenz-Links

- Backlog: `docs/v0.28-konsumer-patterns-backlog.md` (final 2026-05-24 mit Sequenz + Naming)
- ADR-PC5 (Architektur-Anker schlägt Feature): `CLAUDE-Inspector-private.md`
- ADR-38 (Version-Badge single source of truth): `CLAUDE-Inspector-private.md`
- v0.27.3 Vorgänger: `docs/ROADMAP-v0.27.3.md`
- Three.js Doku: https://threejs.org/docs/
- Three.js USDZLoader: https://threejs.org/docs/#examples/en/loaders/USDZLoader
- Memory-Feedback: `[[feedback_inspector_advanced_naming]]` — Advanced statt Pro
- Privates Persona-Anker: `/Users/g/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`

---

**Ende v0.28.0-Briefing.** Nach Sprint: Tag `v0.28.0`, Push, Memory-Update. Dann v0.28.1 (LLM-Findings) als Folge-Briefing.
