# vendor/ — Inline-Bundle für Inspector Advanced

Dieses Verzeichnis enthält vorgebündelte JavaScript-Dateien, die vom Build-Step
(`build.py`) via `<!-- BUILD-INJECT: vendor/filename.js -->` inline in
`advanced/index.html` eingebettet werden.

**Zweck:** Single-File-Anker (ADR-43/ADR-44) — `advanced/index.html` muss ohne
CDN, ohne npm-Server, ohne Browser-Extension lokal öffenbar bleiben (`file://`).
Daher werden alle Third-Party-Libs vorgebündelt und inline eingebettet.

---

## three-usdloader-r184-bundle.js

**Status:** Phase 5.3 (noch nicht erstellt — wird in Phase 5.3 gebaut)

### Was ist drin

Manuelles IIFE-Bundle aus folgenden Quellen (Three.js r184):

| Datei | Quelle | Funktion |
|---|---|---|
| `three.min.js` | `three@0.184.0/build/three.min.js` | Three.js Core (UMD/IIFE) |
| `fflate.module.js` | `three@0.184.0/examples/jsm/libs/fflate.module.js` | USDZ-Entpacken |
| `USDAParser.js` | `three@0.184.0/examples/jsm/loaders/usd/USDAParser.js` | USDA-Text-Parser |
| `USDCParser.js` | `three@0.184.0/examples/jsm/loaders/usd/USDCParser.js` | USDC-Binary-Parser |
| `USDComposer.js` | `three@0.184.0/examples/jsm/loaders/usd/USDComposer.js` | USD-Komposition |
| `USDLoader.js` | `three@0.184.0/examples/jsm/loaders/USDLoader.js` | Haupt-Loader (USDZLoader deprecated seit r179) |

### Konsolidierungs-Schritte (Phase 5.3)

1. `three.min.js` (UMD) — direkt einfügen, gibt `THREE` global
2. `fflate.module.js` — ES6-Imports entfernen, `export { unzipSync }` → globale Variable `window._fflate = { unzipSync }`
3. `USDAParser.js` — ES6-Imports entfernen (keine externen Deps), `export { USDAParser }` → `window._USDAParser = USDAParser`
4. `USDCParser.js` — analog, `export { USDCParser }` → `window._USDCParser = USDCParser`
5. `USDComposer.js` — ES6-Imports (`USDAParser`, `USDCParser`) durch `window._USDAParser`/`window._USDCParser` ersetzen, `export { USDComposer }` → `window._USDComposer = USDComposer`
6. `USDLoader.js` — ES6-Imports (`three`, `fflate`, `USDAParser`, `USDCParser`, `USDComposer`) durch globale Referenzen ersetzen. `FileLoader`/`Loader` aus `THREE`. `export { USDLoader }` → `window.USDLoader = USDLoader`
7. Alles in einen `(function() { ... })()` IIFE-Wrapper einschließen

### Version-Pin

```
three: 0.184.0
npm-Quelle: https://cdn.jsdelivr.net/npm/three@0.184.0/
Erstellt: Phase 5.3 Sprint v0.28.0 (2026-05-24)
```

### Update-Prozess (künftig)

1. Neue Three.js-Version in `three@X.Y.Z/` tauschen
2. Konsolidierungs-Schritte wiederholen
3. Bundle-File ersetzen, `python3 build.py` ausführen
4. `vendor/README.md` Version-Pin aktualisieren
5. Diff `advanced/index.html` prüfen, Browser-Test

---

**ADR-Referenzen:** ADR-43 Two-File-Pattern, ADR-44 Three.js Desktop-3D-Preview

---

## ktx2-polyfill-bundle.js (v0.28.2)

**Größe:** 75 KB  
**Exposes:** `window.KTXParse` (read, write, VK_FORMAT_*, KHR_SUPERCOMPRESSION_*, KHR_DF_MODEL_*), `window.BasisTranscoderFactory`  
**Auslieferung:** Als separate Datei `advanced/ktx2-polyfill-bundle.js` (via `build.py shutil.copy2`)

### Was ist drin

| Quelle | Version | Zweck |
|---|---|---|
| `ktx-parse.modern.min.js` | 1.1.0 | KTX2-Container-Parser (ESM → IIFE konvertiert) |
| `basis_transcoder.js` | Three.js r184 | Basis Universal Transcoder JS-Wrapper |

Zusätzlich: `vendor/basis_transcoder.wasm` (515 KB) — wird separat nach `advanced/` kopiert.

### Konsolidierungs-Schritte

1. `ktx-parse.modern.min.js` von `https://cdn.jsdelivr.net/npm/ktx-parse@1.1.0/dist/ktx-parse.modern.min.js` herunterladen
2. `basis_transcoder.js` + `basis_transcoder.wasm` von `https://cdn.jsdelivr.net/npm/three@0.184.0/examples/jsm/libs/basis/` herunterladen
3. `python3 -c "..."` Konsolidierungsskript (siehe `bundle.py`-Muster) ausführen: ESM-Export entfernen, IIFE wrappen, `window.KTXParse` + `window.BasisTranscoderFactory` setzen
4. `python3 build.py` ausführen
5. Browser-Test: KTX2-USDZ laden, Modal öffnen, Polyfill-Preview prüfen

### Version-Pin

```
ktx-parse: 1.1.0
basis_transcoder: Three.js 0.184.0
Quelle: https://cdn.jsdelivr.net/npm/ktx-parse@1.1.0/ + https://cdn.jsdelivr.net/npm/three@0.184.0/
Erstellt: Sprint v0.28.2 (2026-06-04)
```

---

## tiff-polyfill-bundle.js (v0.28.2)

**Größe:** 57 KB  
**Exposes:** `window.UTIF` (via `self.UTIF = UTIF` innerhalb UTIF.js)  
**Auslieferung:** Als separate Datei `advanced/tiff-polyfill-bundle.js` (via `build.py shutil.copy2`)

### Was ist drin

| Quelle | Version | Zweck |
|---|---|---|
| `UTIF.js` | Photopea latest | TIFF-Decoder (LZW, PackBits, uncompressed) |

Keine WASM-Abhängigkeit. Rein JavaScript.

### Konsolidierungs-Schritte

1. `UTIF.js` von `https://cdn.jsdelivr.net/npm/utif/UTIF.js` herunterladen
2. Header-Kommentar voranstellen (Lizenz, Version, Expose-Info)
3. Datei als `vendor/tiff-polyfill-bundle.js` speichern
4. `python3 build.py` ausführen

### Version-Pin

```
UTIF.js: Photopea (npm utif, latest)
Quelle: https://cdn.jsdelivr.net/npm/utif/UTIF.js
Erstellt: Sprint v0.28.2 (2026-06-04)
```

---

**ADR-Referenzen:** ADR-43 Two-File-Pattern, ADR-44 Three.js Bundle, ADR-45 Lazy-Load, ADR-49 Polyfill-Lazy-Load
