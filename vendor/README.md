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
