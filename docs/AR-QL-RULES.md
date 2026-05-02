# AR Quick Look — Validator-Regeln

Anhang zu `ROADMAP-v0.22.md`. Kuratierte Liste der Regeln, die der Inspector v0.22 gegen jedes USDZ prüft. Quelle: Apple Developer Docs (*Creating USDZ Files for AR Quick Look*, *AR Quick Look — Best Practices*), Reality Composer Pro Documentation, USDZ-Spec bei Pixar/AOUSD, plus Praxis-Erfahrung mit AR-Quick-Look-Brüchen in B2B-Pipelines.

**Stand:** 2026-05-01 · Pre-Build-Vorbereitung für Inspector v0.22.

---

## 1. Severity-Mapping

| Severity | Bedeutung                                         | Ampel-Auswirkung |
|----------|---------------------------------------------------|------------------|
| `error`  | AR Quick Look bricht — Datei wird nicht angezeigt | Rot              |
| `warn`   | Funktioniert, aber Apple empfiehlt anders         | Orange (wenn kein error) |
| `info`   | Hinweis ohne Funktions-Auswirkung                 | Grün-Status bleibt, Card sichtbar |

Ampel-Logik: ein einziger `error` macht rot. Mindestens ein `warn` ohne `error` macht orange. Sonst grün.

---

## 2. Was der Inspector aus v0.21-Context tatsächlich sehen kann

| Datenquelle              | Verfügbar in v0.21 | Reicht für AR-QL-Regel?                    |
|--------------------------|---------------------|--------------------------------------------|
| ZIP-Member-Liste         | ✓                   | Datei-Reihenfolge, Dateinamen, Größen      |
| Root-Layer-Bytes         | ✓                   | USDA-Header parsen (Regex)                 |
| `defaultPrim`            | ✓ (USDA-Parser)     | direkt prüfbar                             |
| `upAxis`, `metersPerUnit`| ✓ (USDA-Parser)     | direkt prüfbar                             |
| Texturen                 | ✓ (PNG/JPG/WebP-Reader) | Format, Dimensionen, NPOT                  |
| Asset-Inventory          | ✓ (Manifest)        | Sub-Asset-Liste, falls USDseal-signiert    |
| Material-Bindings        | ✗                   | Braucht USD-Komposition — v0.4+            |
| Material-Definitionen    | ✗                   | Braucht USDA-Material-Parsing — v0.23+ ggf.|
| Animation-Timecodes      | ✗ (nur grob)        | USDA-Header gibt Hinweise, kein Walk       |
| External References      | △ (Heuristik)       | Suche nach `@./` oder `@asset:` im USDA    |

**Konsequenz:** Regel-Set v0.22 prüft nur Felder aus dem Inspector-v0.21-Context. Materialvalidierung wandert in v0.23 oder später.

---

## 3. Regel-Katalog

Spalten: `id`, `severity`, `category`, `Klartext-DE`, `Klartext-EN`, `fix`, `prüfbar in v0.22`.

### 3.1 Struktur

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `STRUCTURE_DEFAULT_PRIM_MISSING` | error | AR Quick Look braucht einen `defaultPrim`-Eintrag im Haupt-USD-File. Ohne diesen weiß AR Quick Look nicht, welches 3D-Objekt es anzeigen soll. | AR Quick Look requires a `defaultPrim` in the root USD file. Without it, AR Quick Look can't determine which 3D object to display. | Im USDA-Header: `defaultPrim = "<Root-Prim-Name>"` setzen. | ✓ |
| `STRUCTURE_ROOT_LAYER_NOT_FIRST` | error | Im USDZ-Container muss die erste Datei das Haupt-USD-File sein (`.usda`, `.usdc` oder `.usd`). | The first file in the USDZ container must be the root USD layer (`.usda`, `.usdc`, or `.usd`). | USDZ neu packen mit dem Root-Layer als ersten Eintrag (z. B. via `usdcat` oder `usdzip`). | ✓ |
| `STRUCTURE_ROOT_LAYER_FORMAT` | error | Der Root-Layer muss ein USD-File sein. Andere Formate (z. B. JSON, OBJ) brechen AR Quick Look. | The root layer must be a USD file. Other formats (e.g. JSON, OBJ) will break AR Quick Look. | Asset in USDA/USDC neu exportieren. | ✓ |
| `STRUCTURE_NESTED_USDZ` | error | USDZ darf keine weiteren USDZ-Dateien enthalten. AR Quick Look unterstützt kein Nesting. | USDZ must not contain other USDZ files. AR Quick Look does not support nesting. | Inhalt des inneren USDZ extrahieren und ins äußere USDZ flach übernehmen. | ✓ |
| `STRUCTURE_FILE_SIZE_LIMIT` | warn | Apple empfiehlt USDZ-Files unter 25 MB für AR Quick Look. Größere Files laden langsam, brechen aber nicht. | Apple recommends USDZ files below 25 MB for AR Quick Look. Larger files load slowly but won't break. | Texturen verkleinern, Mesh decimieren, ungenutzte Sub-Assets entfernen. | ✓ |
| `STRUCTURE_HIDDEN_FILES` | info | USDZ enthält versteckte Files (`.DS_Store`, `__MACOSX`). Apple ignoriert sie, aber sie blähen das File auf. | USDZ contains hidden files (`.DS_Store`, `__MACOSX`). Apple ignores them, but they bloat the file. | Vor dem Packen `find . -name '.DS_Store' -delete` ausführen. | ✓ |

### 3.2 Skalierung & Achsen

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `SCALE_UP_AXIS_NOT_Y` | warn | AR Quick Look erwartet `upAxis = "Y"`. Andere Achsen werden intern transformiert, können aber zu unerwarteten Rotationen führen. | AR Quick Look expects `upAxis = "Y"`. Other axes get transformed internally but may cause unexpected rotations. | Im Export-Tool Y-up als Up-Achse wählen oder im USDA-Header `upAxis = "Y"` setzen. | ✓ |
| `SCALE_METERS_PER_UNIT_MISSING` | warn | `metersPerUnit` fehlt — AR Quick Look nimmt 0.01 (Centimeter) als Default an. Bei abweichendem Maßstab erscheint das Modell zu groß oder zu klein. | `metersPerUnit` is missing — AR Quick Look assumes 0.01 (centimeters). With a different scale, the model appears too large or too small. | Im USDA-Header: `metersPerUnit = 1` (für Meter) oder den korrekten Wert. | ✓ |
| `SCALE_METERS_PER_UNIT_UNREALISTIC` | warn | `metersPerUnit` ist auf einen ungewöhnlichen Wert gesetzt (`<0.001` oder `>1000`). Modell könnte mikroskopisch oder gigantisch erscheinen. | `metersPerUnit` is set to an unusual value (`<0.001` or `>1000`). Model may appear microscopic or gigantic. | Wert auf realistische Skala (0.01 bis 1.0) korrigieren. | ✓ |

### 3.3 Texturen

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `TEXTURE_FORMAT_UNSUPPORTED` | error | AR Quick Look unterstützt nur PNG, JPEG und (eingeschränkt) WebP für Texturen. Formate wie EXR, HDR, TIFF, KTX brechen das Asset. | AR Quick Look only supports PNG, JPEG, and (limited) WebP for textures. Formats like EXR, HDR, TIFF, KTX will break the asset. | Texturen in PNG (lossless) oder JPEG (lossy, kleiner) konvertieren. | ✓ |
| `TEXTURE_TOO_LARGE` | warn | Textur ist größer als 4096 × 4096 Pixel. AR Quick Look reduziert sie zur Laufzeit, was Speicher und Performance kostet. | Texture exceeds 4096 × 4096 pixels. AR Quick Look downsamples at runtime, costing memory and performance. | Auf 2048 oder 4096 px Kantenlänge reduzieren — meist ausreichend für AR. | ✓ |
| `TEXTURE_NPOT` | info | Textur hat keine Power-of-Two-Auflösung (z. B. 1500 × 1024). Funktioniert, kostet aber GPU-Memory. | Texture is non-power-of-two (e.g. 1500 × 1024). Works but uses extra GPU memory. | Auf Power-of-Two-Werte runden: 256, 512, 1024, 2048, 4096. | ✓ |
| `TEXTURE_PATH_ABSOLUTE` | error | Textur-Pfad ist absolut (z. B. `/Users/...` oder `C:\...`). AR Quick Look findet die Datei nicht. | Texture path is absolute (e.g. `/Users/...` or `C:\...`). AR Quick Look can't find the file. | Pfade relativ zum USDZ-Root machen (z. B. `./textures/basecolor.png`). | △ Heuristik via USDA-Scan |
| `TEXTURE_NOT_IN_USDZ` | error | Manifest oder USDA referenziert eine Textur, die nicht im USDZ-Container liegt. | Manifest or USDA references a texture that's not in the USDZ container. | Fehlende Textur ins USDZ packen oder Reference entfernen. | ✓ (via Inventory-Diff) |

### 3.4 External References

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `EXTERNAL_HTTP_REFERENCE` | error | USDA enthält eine externe HTTP-Referenz (`@http://...`). AR Quick Look lädt keine externen Assets. | USDA contains an external HTTP reference (`@http://...`). AR Quick Look does not load external assets. | Asset ins USDZ einbetten oder Reference entfernen. | ✓ Heuristik |
| `EXTERNAL_FILE_REFERENCE` | error | USDA enthält eine externe File-Referenz außerhalb des USDZ. AR Quick Look findet die Datei nicht. | USDA contains an external file reference outside the USDZ. AR Quick Look can't find it. | Asset ins USDZ einbetten oder Reference entfernen. | ✓ Heuristik |

### 3.5 Manifest (USDseal-spezifisch)

Diese Regeln laufen nur, wenn ein USDseal-Manifest vorhanden ist. Sind `info`-Severity, weil sie AR Quick Look nicht direkt betreffen — der Inspector macht hier seinen USP sichtbar.

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `MANIFEST_MISSING` | info | Kein USDseal-Manifest vorhanden. AR Quick Look funktioniert auch ohne, aber Provenance und Hash-Verifikation entfallen. | No USDseal manifest present. AR Quick Look works without one, but provenance and hash verification are unavailable. | `usdseal init` + `usdseal sign` ausführen, um das USDZ zu signieren. | ✓ |
| `MANIFEST_HASH_MISMATCH` | warn | Mindestens ein Asset-Hash stimmt nicht mit dem Manifest überein. Asset wurde nach dem Siegeln verändert. | At least one asset hash does not match the manifest. Asset was modified after sealing. | `usdseal verify` lokal ausführen, dann `usdseal sign` neu. | ✓ (v0.2-Logik wiederverwendet) |

### 3.6 Animation (eingeschränkt)

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `ANIMATION_TIMECODE_MISSING` | warn | USDA deutet auf Animation hin, aber `startTimeCode`/`endTimeCode`/`timeCodesPerSecond` fehlen. AR Quick Look spielt nichts ab. | USDA indicates animation but `startTimeCode`/`endTimeCode`/`timeCodesPerSecond` are missing. AR Quick Look won't play anything. | Im USDA-Header die drei Felder setzen, z. B. `startTimeCode = 0`, `endTimeCode = 120`, `timeCodesPerSecond = 30`. | ✓ Heuristik via USDA-Scan |

### 3.7 Performance (Hinweise)

| ID | Sev | Klartext DE | Klartext EN | Fix | v0.22 |
|---|---|---|---|---|---|
| `PERFORMANCE_MANY_TEXTURES` | info | USDZ enthält mehr als 16 Texturen. AR Quick Look kann das, aber Performance auf älteren iPhones leidet. | USDZ contains more than 16 textures. AR Quick Look handles it, but performance on older iPhones suffers. | Texturen kombinieren (Atlas) oder PBR-Setup vereinfachen. | ✓ |
| `PERFORMANCE_LARGE_INVENTORY` | info | USDZ enthält mehr als 100 Files. Ladezeit auf mobilen Geräten kann spürbar werden. | USDZ contains more than 100 files. Load time on mobile devices may be noticeable. | Sub-Assets zu größeren USD-Files konsolidieren. | ✓ |

---

## 4. Regel-Implementierung — Pseudocode-Skelett

```js
const AR_QL_RULES = [
  {
    id: 'STRUCTURE_DEFAULT_PRIM_MISSING',
    severity: 'error',
    category: 'structure',
    explanation: {
      de: 'AR Quick Look braucht einen defaultPrim-Eintrag …',
      en: 'AR Quick Look requires a defaultPrim …'
    },
    fixHint: {
      de: 'Im USDA-Header: defaultPrim = "<Root-Prim-Name>" setzen.',
      en: 'In the USDA header: set defaultPrim = "<root-prim-name>".'
    },
    check: (ctx) => !ctx.usdMeta?.defaultPrim
  },
  // ... weitere Regeln
];

function runValidator(ctx) {
  const findings = [];
  for (const rule of AR_QL_RULES) {
    if (rule.check(ctx)) findings.push(rule);
  }
  return findings;
}

function ampelStatus(findings) {
  if (findings.some(f => f.severity === 'error')) return 'red';
  if (findings.some(f => f.severity === 'warn'))  return 'orange';
  return 'green';
}
```

Inspector-Context (`ctx`) ist exakt das, was `processFile()` heute schon sammelt — keine neuen Datenquellen nötig.

---

## 5. Erweiterungs-Backlog (nicht in v0.22)

Diese Regeln **könnten** geprüft werden, brauchen aber tiefere Analyse als v0.22 leisten will:

- `MATERIAL_NOT_USDPREVIEWSURFACE` — UsdPreviewSurface ist Pflicht für AR Quick Look. Braucht Material-Parsing → v0.23 oder später.
- `MATERIAL_BINDINGS_MISSING` — Mesh ohne Material-Binding wird grau. Braucht Komposition → v0.4+.
- `ANCHORING_TYPE_INVALID` — Plane/Image/Face-Anchoring im USDZ-Header. Braucht erweiterten USDA-Parser.
- `LIGHTING_NO_DOME` — AR Quick Look nutzt Environment-Lighting; eigene Domes überschreiben das. Heuristisch erkennbar.
- `SHADER_CUSTOM_NOT_SUPPORTED` — Eigene Shader (GLSL, MaterialX) brechen AR Quick Look. Material-Walk nötig.

Diese kommen, wenn der Inspector-Komposition-Layer (Roadmap §5 Option B/C: `usd-wasm`) ausgebaut wird.

---

## 6. Quellen

- [Apple Developer — AR Quick Look](https://developer.apple.com/augmented-reality/quick-look/)
- [Apple Developer — Adding visual effects in AR Quick Look](https://developer.apple.com/documentation/arkit/previewing_a_model_with_ar_quick_look)
- [Apple WWDC 2018 — Introducing USDZ](https://developer.apple.com/videos/play/wwdc2018/603/)
- [Apple WWDC 2019 — AR Quick Look, Meet Reality Composer](https://developer.apple.com/videos/play/wwdc2019/612/)
- [OpenUSD — USDZ Specification](https://openusd.org/release/spec_usdz.html)
- [Reality Composer Pro Documentation](https://developer.apple.com/augmented-reality/tools/)

---

**Stand:** 2026-05-02 · **20 Regeln** im Inspector v0.22 implementiert (10 error, 7 warn, 3 info).
`STRUCTURE_ROOT_LAYER_FORMAT` wurde während des Builds als redundant zu `STRUCTURE_ROOT_LAYER_NOT_FIRST` erkannt und entfernt — die kombinierte Regel prüft jetzt: erstes ZIP-File muss USD-Format sein UND auf Top-Level liegen.

Erweiterung in v0.23+ vorgesehen (siehe §5).
