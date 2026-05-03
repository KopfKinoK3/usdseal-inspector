# Roadmap v0.24 — UX Polish: Texture Modal & Channel Detection

**Status:** Vorbereitungs-Dokument · 2026-05-03
**Story-Slot:** *"Klick & sieh"* — Texture-UX-Welle
**Ziel:** Texturen werden interaktiv (Vollbild-Modal) und semantisch eingeordnet (Channel-Erkennung). Inspector wird dadurch nicht nur USDZ-Validator, sondern auch **Material-Inspektor** für Designer und Material-Reviewer.
**Aufwand:** 1.5–2 Tage konzentrierter Build.

> Erster UX-Polish-Sprint nach den drei Architektur-/Story-Releases (v0.22, v0.22.1/v0.22.2, v0.23). Master-Übersicht in `../ROADMAP.md`.

---

## 1. Scope — was v0.24 inhaltlich bedeutet

Inspector zeigt heute Texturen als 40×40-Mini-Thumbnails mit Format-/Auflösung-Tag. v0.24 macht zwei Sprünge:

### 1.1 Thumbnail-Vollbild-Modal

- Klick auf Thumbnail → Modal-Overlay mit voller Auflösung
- Modal-Mechanik: Backdrop (semi-transparent), zentrales Bild, Close-Button + ESC + Backdrop-Click zum Schließen
- Bild wird via Blob-URL gerendert (wie heute), Lifecycle: URL bei Modal-Close mit `URL.revokeObjectURL()` freigeben (kein Memory-Leak — siehe v0.22.1 W-1-Fix)
- **Download-Button** im Modal: `download`-Attribut auf `<a>`-Element mit Original-Filename
- Optional Stretch: Pinch-to-Zoom auf Mobile, Pfeiltasten für Navigation zwischen Texturen (eher v0.25 falls v0.24 zeitlich knapp wird)

### 1.2 Texturen-Channel-Erkennung

Inspector zeigt heute *"texture.png 1024×1024 PNG"*. v0.24 ergänzt: **welcher Channel** ist das?

**Erkennungs-Strategie:** USDA-Parser folgt den `inputs:*.connect`-Verweisen vom Material zur Texture. Pattern:

```
def "Material" {
  token outputs:surface.connect = </Material/PBRShader.outputs:surface>
  def Shader "PBRShader" {
    token info:id = "UsdPreviewSurface"
    color3f inputs:diffuseColor.connect = </Material/Tex_Diffuse.outputs:rgb>
    float inputs:roughness.connect = </Material/Tex_Roughness.outputs:r>
    ...
  }
  def Shader "Tex_Diffuse" {
    asset inputs:file = @./textures/basecolor.png@
    ...
  }
}
```

→ `basecolor.png` wird als **Diffuse**-Channel identifiziert.

**Channel-Set für v0.24** (10 Core + 1 Fallback):

| Channel | USDA-Input-Namen (Aliases) |
|---|---|
| Diffuse | `diffuseColor`, `baseColor`, `albedo` |
| Normal | `normal`, `normalMap` |
| Roughness | `roughness` |
| Metallic | `metallic`, `metalness` |
| Emissive | `emissiveColor`, `emissive` |
| Occlusion | `occlusion`, `ambientOcclusion`, `ao` |
| Opacity | `opacity`, `alpha` |
| Displacement | `displacement`, `heightMap`, `height` |
| Subsurface | `subsurface`, `subsurfaceColor` |
| Clearcoat | `clearcoat`, `clearcoatRoughness` |
| **Fallback** | unknown / generic — Texture wird als *"used"* markiert ohne spezifischen Channel |

**UI-Integration:** Channel als farbcodiertes Badge ans Thumbnail anhängen (z. B. *Diffuse* in türkis, *Normal* in blau, *Roughness* in violett). Fallback "unknown" als grauer Badge.

**Edge-Case:** Texture kann von **mehreren** Channels referenziert werden (selten, aber möglich) → mehrere Badges nebeneinander oder kommasepariert.

---

## 2. Externe Quellen

| Komponente              | Status                       | Bemerkung                                                     |
|-------------------------|------------------------------|---------------------------------------------------------------|
| JSZip                   | bereits eingebunden          | Reicht.                                                       |
| jsPDF 3.0.3             | bereits eingebunden (v0.23)  | Reicht. PDF-Report wird in v0.24 nicht angefasst (Logo-Cover verschoben). |
| Web Workers API         | bereits eingebunden (v0.22.1)| Reicht.                                                       |
| **Keine neuen Deps**    |                              | Modal ist pures DOM, Channel-Erkennung ist USDA-Regex-Erweiterung. |

---

## 3. Architektur-Optionen

### 3.1 Modal-Pattern

**Option A — `<dialog>`-Element (Empfehlung)**
- HTML-natives Modal, Browser-Support seit 2022 in allen Zielbrowsern
- Eingebaute ESC-Behandlung, automatischer Backdrop, A11y-konform
- `dialog.showModal()` / `dialog.close()` als API

**Option B — Custom Div-Overlay**
- Vollkontrolle über Animation, Backdrop-Style
- Manuelle ESC-Handler, manuelle Focus-Trap

**Empfehlung:** **Option A** (`<dialog>`). Browser-native, weniger Code, A11y by default. Single-File-Anker bleibt unverletzt.

### 3.2 Channel-Erkennung — Wo läuft der Parser?

**Option C — Im bestehenden USDA-Parser erweitern (Empfehlung)**
- Inspector hat schon einen USDA-Parser für `defaultPrim`, `upAxis`, `metersPerUnit`
- Erweitern um `inputs:*.connect`-Tracking → Texture-zu-Channel-Mapping
- Output: `Map<TextureFilename, Channel[]>`

**Option D — Separate Material-Walker-Klasse**
- Eigenständiger Walker, der den Material-Graph traversiert
- Mehr Code, aber sauberer von der Architektur her

**Empfehlung:** **Option C**. Inspector ist Single-File, kein Bundle-Split — Erweiterung des bestehenden Parsers ist konsistent. Walker-Refactor kann in v0.26 (Komposition-Sprint) kommen, wenn Layer-Stack ohnehin tieferes Walking braucht.

---

## 4. Vorbedingungen

| # | Vorbedingung                                                       | Status |
|---|--------------------------------------------------------------------|--------|
| 1 | Inspector v0.23 stabil released                                    | ✓ — Tag online seit 2026-05-02 |
| 2 | Modal-Pattern entschieden (Option A `<dialog>`)                    | ✓ — Plan-Chat 2026-05-03 |
| 3 | Channel-Erkennungs-Strategie entschieden (Option C im USDA-Parser) | ✓ — Plan-Chat 2026-05-03 |
| 4 | Channel-Set finalisiert (10 PBR + Fallback)                        | ✓ — Plan-Chat 2026-05-03 |
| 5 | Test-USDZ mit mehreren Texturen + klaren Material-Bindings         | ✓ — DIEGOsat_master.usdz hat hull/textures/* + inner/* |

**5 von 5 grün — startklar für Build-Chat.**

---

## 5. Phasen-Schätzung

| Phase                                | Dauer       | Was passiert                                                       |
|--------------------------------------|-------------|--------------------------------------------------------------------|
| **5.1 Modal-Markup + CSS**           | 0.25 Tag    | `<dialog>`-Element ins Inspector-DOM, CSS für Backdrop + Centering + Close-Button. Warm-Tech-Design-System. |
| **5.2 Modal-Verdrahtung**            | 0.25 Tag    | Click-Handler auf Texture-Card → `dialog.showModal()`. Bild via Blob-URL setzen. ESC + Backdrop-Click + X-Button → `dialog.close()` + Blob-URL revoken. |
| **5.3 Download-Button im Modal**     | 0.25 Tag    | `<a download="filename.png" href="blob:...">` als Button-Style. Filename aus ZIP-Member-Pfad. |
| **5.4 USDA-Parser-Erweiterung**      | 0.5 Tag     | `inputs:*.connect` parsen, Texture-Filename ↔ Channel-Mapping aufbauen. Aliases beachten (siehe §1.2-Tabelle). |
| **5.5 Channel-Badge-Render**         | 0.25 Tag    | Texture-Cards bekommen Channel-Badge. Mehrfach-Channels → mehrere Badges. Fallback "unknown" als grauer Badge. |
| **5.6 Test gegen review-pool/**      | 0.25 Tag    | DIEGOsat-Master + alle Pool-Files durchspielen. Modal-Toggle, Channel-Erkennung verifizieren. Edge-Case: Pool-File mit minimalem USDA. |
| **5.7 Headless-Pool-Regression**     | 0.1 Tag     | `python3 tests/headless_validator.py ../usdz/review-pool/` muss 7/7 PASS bleiben. Channel-Erkennung ist Browser-Feature, sollte den Headless-Validator nicht beeinflussen. |
| **5.8 README + CHANGELOG-Update**    | 0.25 Tag    | v0.24-Eintrag, neue Feature-Tabellen-Zeilen für Modal + Channels. |
| **5.9 Snapshot + Tag**               | 0.25 Tag    | `archive/snapshots/v0.24-snapshot.html`, Commit, Tag, Push. |

**Total: 2 Tage Build-Zeit.** Kompakter Sprint, keine Überraschungs-Komplexität erwartet.

---

## 6. Strategischer Hebel

v0.24 erweitert den Inspector vom **USDZ-Validator** zum **Material-Inspektor**. Drei Hebel:

1. **Designer-Use-Case:** Material-Reviewer sehen pro Texture sofort, welcher Channel das ist. Spart minutenweises USDA-Lesen pro Asset. Direkt Talk-relevant für Konferenzen wo Designer im Publikum sitzen (XR Expo, AWE, AR-Meetups).
2. **PDF-Report-Mehrwert (indirekt):** v0.23 zeigt Texturen ohne Channel-Kontext im PDF. Wenn v0.24 Channels rendert, kann v0.25 oder später die Channel-Info im PDF mit ausgeben. *Nicht* in v0.24 reinpacken (Scope-Disziplin), aber als natürliche Folge im Hinterkopf.
3. **Modal als UI-Pattern für später:** Das `<dialog>`-Pattern aus 5.1 wird in v0.27 (Diff-View) wiederverwendet. Sauberes Setup zahlt sich aus.

---

## 7. Konkrete Pre-v0.24-Steps

### 7.1 USDA-Parser-Stelle finden (5 Minuten, vor Build-Start)

Im aktuellen `index.html` nach der Funktion suchen, die `defaultPrim` / `upAxis` parst — die wird der Erweiterungs-Punkt für 5.4.

### 7.2 Test-USDA visuell durchgehen (10 Minuten)

DIEGOsat_master.usdz extrahieren → `master.usda` und `hull/hull.usda` öffnen. Schauen ob Material-Inputs schon vorhanden sind oder ob das Test-Asset nur Geometrie hat. **Falls nur Geometrie:** ein zusätzliches Test-USDZ mit klaren Material-Bindings beschaffen oder das DIEGOsat-Asset um Material-Block erweitern.

### 7.3 Channel-Farbpalette finalisieren (5 Minuten)

Vorschlag für Badge-Farben (Warm-Tech-konform):

| Channel | Badge-Farbe |
|---|---|
| Diffuse | `#0891b2` (Cyan-Akzent) |
| Normal | `#6366f1` (Indigo) |
| Roughness | `#a855f7` (Violett) |
| Metallic | `#94a3b8` (Slate, metallisch) |
| Emissive | `#f97316` (Orange — Warm-Tech-Primary, weil "leuchtend") |
| Occlusion | `#525252` (Neutral-Grau) |
| Opacity | `#0ea5e9` (Sky) |
| Displacement | `#84cc16` (Lime) |
| Subsurface | `#ec4899` (Pink) |
| Clearcoat | `#eab308` (Yellow) |
| Fallback | `#9ca3af` (Light-Grau) |

Falls dir Farben nicht gefallen — Build-Chat darf adjustieren, ist Detail-Pflege.

---

## 8. Decision-Log-Template

```markdown
### ADR-15 Modal-Pattern: <dialog>-Element statt Custom Div — 2026-05-XX

**Kontext:** Texture-Vollbild-Modal in v0.24.
**Entscheidung:** Browser-natives `<dialog>`-Element via `showModal()` / `close()`.
**Begründung:** A11y-konform out-of-the-box, ESC-Handler eingebaut, Backdrop automatisch. Browser-Support seit 2022 in allen Zielbrowsern (Chrome 37+, Firefox 98+, Safari 15.4+).
**Konsequenz:** Single-File-Anker bleibt unverletzt. Pattern wiederverwendbar in v0.27 (Diff-View).

### ADR-16 Channel-Erkennung: Erweiterung des bestehenden USDA-Parsers — 2026-05-XX

**Kontext:** Inspector hat schon Regex-Parser für `defaultPrim`/`upAxis`. Channel-Erkennung verfolgt `inputs:*.connect`-Pfade vom Material zur Texture.
**Entscheidung:** Erweiterung des bestehenden Parsers, kein separater Walker.
**Konsequenz:** Single-Code-Path, keine zwei Parser parallel. Refactor zu separatem Walker erst in v0.26 (Layer-Stack), wenn tieferes Material-Walking ohnehin nötig wird.

### ADR-17 Channel-Aliases akzeptieren — 2026-05-XX

**Kontext:** USDA hat unterschiedliche Input-Namen für gleichen Channel (`diffuseColor` / `baseColor` / `albedo`).
**Entscheidung:** Alias-Map mit allen gängigen PBR-Bezeichnungen (siehe Briefing §1.2-Tabelle). Fallback "unknown" für nicht erkannte Inputs.
**Konsequenz:** Robuster gegenüber UsdPreviewSurface-, MaterialX- und älteren USDA-Konventionen. Erweiterung der Alias-Map zukunftssicher (neue Aliases einfach in Map ergänzen).
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger-Briefings: `ROADMAP-v0.22.md` (AR-Quick-Look), `ROADMAP-v0.23.md` (PDF Audit Report)
- AR-QL-Regel-Katalog: `AR-QL-RULES.md`

### Externe Specs

- [HTML `<dialog>`-Element (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog)
- [UsdPreviewSurface Spec (Pixar)](https://openusd.org/release/spec_usdpreviewsurface.html)
- [MaterialX Standard Library](https://materialx.org/)

### Inspector-Repo

- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)

---

**Ende v0.24-Roadmap.** Nach Build: Snapshot `archive/snapshots/v0.24-snapshot.html`, Tag `v0.24`, Push. Plan-Chat schreibt dann `docs/ROADMAP-v0.24.1.md` für Multi-File-Drop (Patch zwischen v0.24 und v0.25).
