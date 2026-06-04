# Roadmap v0.28.2 — Texture-Polyfills KTX2 + TIFF

**Status:** Vorbereitungs-Dokument · 2026-06-04
**Story-Slot:** *"Inspector Advanced zeigt jetzt auch GPU-optimierte Texturen — KTX2 und TIFF werden im Texture-Modal als echtes Bild gerendert."*
**Ziel:** KTX2-Decoder (Khronos `ktx-parse` + Basis-Universal Transcoder) und TIFF-Decoder (UTIF.js) im Inspector Advanced. On-Demand-Lazy-Load — Polyfill wird erst geladen wenn USDZ tatsächlich KTX2 oder TIFF enthält. Preview erscheint ausschließlich im Texture-Vollbild-Modal (v0.24-Pattern). Standard bleibt unangetastet (Schlank-Anker).
**Aufwand:** M (1.0–1.5 Tage)

> Sequenz-Tausch 2026-06-04 (Duke-Entscheidung): v0.28.2 = Polyfills (schneller Win, GitHub Pages reicht), v0.28.3 = USDC-Material-Parser (vormals v0.28.2 — größere Hosting-Frage, eigene Strategie-Klärung).

> ASTC bewusst rausgenommen aus v0.28.2 — Polyfill-Komplexität (GPU-spezifisch, 500 KB–1 MB Software-Decoder, langsam) rechtfertigt eigenen Folge-Sprint v0.28.2.1.

---

## 1. Befund

Seit v0.25.5 erkennt Inspector KTX2/TIFF/ASTC via Magic-Bytes — zeigt aber nur das **Format-Label** ohne echte Vorschau. AVIF und HEIC werden seitdem nativ via Browser-Support (Safari) gerendert. KTX2 und TIFF bleiben **textbasierte Information** statt visueller Inspektion.

**Heutige Realität:**
- KTX2 ist Pro-Tier-Format für GPU-optimierte Texturen — wird in Carl-Hamm-Möbel-Workflows, CAD-Exporten von SolidWorks/NX und Unity/Unreal-Pipelines genutzt
- TIFF ist Stand-Format in CAD-/Architektur-Workflows (oft als Quell-Format für Texturen)
- User mit komplexen B2B-Assets sehen *"Format: KTX2"* — können aber nicht prüfen ob Textur visuell stimmt
- Workaround heute: USDZ entpacken, KTX2 manuell mit externem Tool öffnen → ist mühsam, hebt Inspector-USP aus

**Was Advanced jetzt liefern kann:**
- Texture-Vollbild-Modal aus v0.24 wird mit Polyfill-Pipeline erweitert
- User klickt auf KTX2/TIFF-Texture-Thumbnail → Modal öffnet → Polyfill lädt on-demand → echtes Bild erscheint
- Standard bleibt schlank — keine Polyfills, kein Bundle-Wachstum

**Strategischer Hebel:** Inspector Advanced wird zum **einzigen Browser-USDZ-Inspector im OpenUSD-Ökosystem, der KTX2 öffnet**. Konkrete Lücke geschlossen, kein Marketing-Bullshit nötig. Plus: stärkster technischer Mehrwert seit v0.28.0-Three.js — passt zum *"Inspector Advanced kann mehr"*-Versprechen.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Bestehende KTX2/TIFF-Detection-Pfade lokalisieren
grep -n "KTX2\|ktx2\|tiff\|TIFF" src/inspector.html | head -20
# - Wo wird Magic-Bytes erkannt? (v0.25.5-Pattern)
# - Wie wird Format-Label heute gerendert?
# - Wo ist der Texture-Vollbild-Modal aus v0.24?

# B) Modal-Render-Stelle finden
grep -n "openTextureModal\|texture-modal\|texturePreviewModal" src/inspector.html | head -10
# - Welche Funktion öffnet den Modal?
# - Wo wird das Bild eingesetzt? Img-Tag mit src?
# - Wie behandelt der Modal heute AVIF (das funktioniert ja schon)?

# C) Lazy-Load-Pattern aus v0.28.0.2 für Three.js als Vorbild
grep -n "loadThreeBundle\|bundleLoaded" src/inspector.html | head -10
# - Wie ist das Lazy-Load-Pattern strukturiert?
# - Lässt es sich für Polyfills wiederverwenden?

# D) Recherche Polyfill-Größen (Code-Chat verifiziert real)
# - ktx-parse + Basis-Universal Transcoder von Khronos:
#   https://github.com/donmccurdy/KTX-Parse
#   Größenmessung: minified+gzipped
# - UTIF.js: https://github.com/photopea/UTIF.js
#   Größenmessung: minified+gzipped
# - Beide müssen IIFE-konsolidiert werden für Inline-Embed
#   (analog v0.28.0 Three.js-Bundle-Strategie via vendor/)
```

→ Lokalisiert:
1. Magic-Bytes-Detection für KTX2/TIFF — bestehend, Render-Pfad: heute "Format: KTX2"-Label
2. Texture-Vollbild-Modal aus v0.24 — Render-Stelle wo das Bild erscheint
3. Lazy-Load-Pattern aus v0.28.0.2 als Vorbild — Polyfill-Loading-Funktion analog
4. Real-World-Größen der Polyfills — Bundle-Plan
5. IIFE-Konsolidierungs-Strategie analog Three.js-Bundle (vendor/-Verzeichnis)

**Konsistenz-Check:**
- Polyfills sind **ADVANCED-ONLY** (STANDARD-Distribution bleibt unangetastet) — Build-Step muss das via Marker handhaben
- Polyfills sind **separate Files in vendor/** (analog Three.js-Bundle aus v0.28.0)
- Polyfills werden **on-demand** geladen (analog Lazy-Load-Pattern aus v0.28.0.2)
- Theme-Check (v0.28.0.7) greift weiterhin
- Headless-Pool 18/18 darf nicht regredieren (Standard ist unverändert)

---

## 3. Scope

### 3.1 Polyfill-Bundles via vendor/

**KTX2-Bundle:**
- Quelle: Khronos `ktx-parse` + Basis-Universal Transcoder
- Konsolidierung: IIFE-Wrapper analog `vendor/three-usdloader-r184-bundle.js` (v0.28.0-Pattern)
- Datei: `vendor/ktx2-polyfill-bundle.js`
- Größe-Ziel: 200-300 KB (gzipped)
- Konsolidierungs-Doku in `vendor/README.md` ergänzen

**TIFF-Bundle:**
- Quelle: UTIF.js (Photopea)
- Konsolidierung: ggf. UMD direkt nutzbar (kein IIFE-Wrapper nötig wenn UMD vorhanden)
- Datei: `vendor/tiff-polyfill-bundle.js`
- Größe-Ziel: 50-80 KB (gzipped)
- Konsolidierungs-Doku in `vendor/README.md` ergänzen

**Build-Step:**
- `build.py` wird um Polyfill-Inject-Marker erweitert (analog Three.js-BUILD-INJECT-Pattern):
  ```html
  <!-- ADVANCED-ONLY:START ktx2-polyfill -->
  <script id="ktx2-polyfill" type="text/template">
    <!-- BUILD-INJECT: vendor/ktx2-polyfill-bundle.js -->
  </script>
  <!-- ADVANCED-ONLY:END ktx2-polyfill -->
  ```
- **Achtung:** Polyfill-Bundle wird im `<script type="text/template">` als Text injiziert (NICHT als ausführbares `<script>`), damit es **nicht beim Page-Load ausgeführt wird**. Wird erst on-demand evaluiert (siehe § 3.3 Lazy-Load).
- Alternative: Bundles bleiben separate Files im `advanced/`-Output (kein Inline-Inject), werden via `<script src="ktx2-polyfill-bundle.js">` on-demand nachgeladen. Code-Chat entscheidet was sauberer ist.

### 3.2 Polyfill-Loader-Funktionen

Analog `loadThreeBundle()` aus v0.28.0.2:

```javascript
let ktx2Loaded = false;
let ktx2LoadPromise = null;

async function loadKtx2Polyfill() {
  if (ktx2Loaded) return;
  if (ktx2LoadPromise) return ktx2LoadPromise;
  ktx2LoadPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'ktx2-polyfill-bundle.js'; // oder template-evaluation
    script.onload = () => { ktx2Loaded = true; resolve(); };
    script.onerror = reject;
    document.head.appendChild(script);
  });
  return ktx2LoadPromise;
}

// Analog: loadTiffPolyfill()
```

**Verhalten:**
- Beim ersten KTX2/TIFF-Treffer im USDZ wird Polyfill **automatisch nachgeladen** (Modus C-b aus Duke-Entscheidung 2026-06-04)
- Wenn USDZ kein KTX2/TIFF enthält: Polyfill wird **nie** geladen — Performance hält
- Wenn USDZ mehrere KTX2-Texturen hat: Polyfill wird **einmal** geladen, cached via Promise

### 3.3 UI-Integration — Modal-only (Modus B aus Duke-Entscheidung)

**Inline-Texture-Block (im Report):** bleibt wie heute — Format-Label "KTX2" / "TIFF" + Magic-Bytes-Info, kein Preview-Bild. Schlank-Anker im Report-Layout.

**Texture-Vollbild-Modal:** wird erweitert:
- User klickt auf KTX2/TIFF-Thumbnail → Modal öffnet
- Modal-Init prüft: ist Format KTX2/TIFF?
- Wenn ja: `await loadKtx2Polyfill()` oder `await loadTiffPolyfill()`
- Während Polyfill lädt: Spinner + Text *"KTX2-Polyfill wird geladen…"* / *"TIFF-Polyfill wird geladen…"*
- Nach Polyfill geladen: Decode + Canvas-Render in Modal
- Bei Decode-Fehler: Fallback-Hinweis *"KTX2-Decode fehlgeschlagen — Format-Info bleibt sichtbar im Report unten"* (Graceful Degradation analog v0.28.0.2)

**Bei Modal-Schließen:** Polyfill bleibt geladen (für nächste Textur des gleichen Formats). Page-Reload setzt zurück — wir bauen kein persistentes Cache.

### 3.4 Format-Erkennung im Polyfill-Trigger

Beim USDZ-Drop läuft heute Magic-Bytes-Erkennung pro Textur. Wenn KTX2 oder TIFF erkannt: **Polyfill-Pre-Load-Hint** in der Texture-Block-Anzeige:

```
🖼 holz_eiche.ktx2 — KTX2 [▶ Vorschau (Polyfill wird geladen)]
```

Der Hinweis-Text macht klar dass beim ersten Klick eine Verzögerung kommt. Optional aber empfohlen für ehrliche Erwartungs-Kommunikation.

### 3.5 i18n

3-5 neue Keys DE+EN:
- `polyfill_loading_ktx2` — *"KTX2-Polyfill wird geladen…"* / *"Loading KTX2 polyfill…"*
- `polyfill_loading_tiff` — analog
- `polyfill_decode_failed_ktx2` — *"KTX2-Decode fehlgeschlagen — Format-Info bleibt sichtbar im Report."* / analog EN
- `polyfill_decode_failed_tiff` — analog
- `polyfill_preview_hint` — *"Vorschau (Polyfill wird geladen)"* / *"Preview (polyfill loads on demand)"*

### 3.6 Was NICHT in v0.28.2

- **Kein ASTC** — eigener Folge-Sprint v0.28.2.1 wegen Komplexität (GPU-Hardware-Abhängigkeit, große Software-Decoder)
- **Keine Inline-Preview im Report** — bewusst nur Modal (Schlank-Anker im Report-Layout)
- **Kein eager Page-Load** — Polyfills sind on-demand
- **Keine Polyfills im Standard** — Schlank-Anker hält strikt
- **Kein Persistent Cache** (Service Worker o.ä.) — Page-Reload setzt zurück
- **Kein Texture-Editor** — Inspector zeigt, modifiziert nicht
- **Keine Polyfill-Konfiguration im UI** — alles automatisch

### 3.7 v0.28.2.1 (Folge-Sprint, nicht in v0.28.2)

ASTC-Polyfill nachziehen. Eigener Sprint wegen:
- GPU-Hardware-Decoding ist Browser/Device-spezifisch (Apple Silicon kann's nativ, viele Desktop-GPUs nicht)
- Software-Decoder existieren aber ~500 KB-1 MB groß und langsam
- Frage ob Render im Modal trotz Software-Decoder akzeptabel performt
- Recherche-Aufwand: welcher ASTC-Decoder ist Browser-tauglich? (`astc-decode-wasm`, `bptc-decoder`, andere?)

Wird gebrieft nach v0.28.2-Erfahrungen.

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| ktx-parse (Khronos) | neu, inline | https://github.com/donmccurdy/KTX-Parse, MIT |
| Basis-Universal Transcoder | neu, inline | Khronos, für KTX2-Decoding |
| UTIF.js (Photopea) | neu, inline | https://github.com/photopea/UTIF.js, MIT |
| Bestehendes Texture-Modal (v0.24) | recycelt | wird um Polyfill-Trigger erweitert |
| Bestehender Magic-Bytes-Reader (v0.25.5) | recycelt | liefert Format-Detection |
| Lazy-Load-Pattern (v0.28.0.2 Three.js) | Vorbild | analoge Loader-Funktionen |
| Build-Step (v0.28.0) | recycelt | wird um Polyfill-Inject-Marker erweitert |
| Theme-Check (v0.28.0.7) | greift | verhindert CSS-Fallback-Bugs in neuem Modal-Code |

GitHub Pages reicht weiterhin. Kein COOP/COEP, kein Hosting-Wechsel. Schlank-Anker im Standard bleibt.

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.28.1 released | ✓ (2026-06-04) |
| 2 | Magic-Bytes-Detection KTX2/TIFF funktional (v0.25.5) | ✓ |
| 3 | Texture-Vollbild-Modal (v0.24) funktional | ✓ |
| 4 | Lazy-Load-Pattern (v0.28.0.2) als Vorbild | ✓ |
| 5 | Build-Step kann Polyfill-Inject (v0.28.0 erweiterbar) | ✓ |
| 6 | Theme-Check (v0.28.0.7) aktiv | ✓ |

**6 von 6 grün.** Keine Strategie-Klärung nötig (keine Hosting-Migration, kein COOP/COEP).

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose + Polyfill-Recherche** | 0.15 Tag | grep + Real-World-Größen-Check der zwei Polyfill-Bibliotheken (ktx-parse + Basis-Universal vs. UTIF.js), Bundle-Plan |
| **5.1 KTX2-Bundle konsolidieren** | 0.25 Tag | IIFE-Wrapper analog Three.js-Bundle, vendor/ktx2-polyfill-bundle.js, vendor/README.md ergänzen |
| **5.2 TIFF-Bundle vorbereiten** | 0.1 Tag | UTIF.js als UMD oder IIFE-Wrapper, vendor/tiff-polyfill-bundle.js |
| **5.3 Build-Step Polyfill-Inject** | 0.1 Tag | build.py um ADVANCED-ONLY-Marker für Polyfill-Bundles erweitern (Strategie inline-template oder separate Files, Code-Chat entscheidet) |
| **5.4 Loader-Funktionen** | 0.1 Tag | loadKtx2Polyfill() + loadTiffPolyfill() analog loadThreeBundle(), Promise-Caching |
| **5.5 Modal-Integration** | 0.2 Tag | Modal-Init prüft Format, ruft passenden Loader, Decode + Canvas-Render, Spinner während Load, Fallback-Toast bei Decode-Fehler |
| **5.6 Inline-Hinweis-Text** | 0.05 Tag | Polyfill-Pre-Load-Hint in Texture-Block-Anzeige für KTX2/TIFF |
| **5.7 i18n** | 0.05 Tag | 5 neue Keys DE+EN |
| **5.8 Browser-Verifikation** | 0.2 Tag | Chrome+Safari: Test mit echtem KTX2-Asset (synthetisch oder aus Pool falls vorhanden), Test mit TIFF-Asset, Modal-Lazy-Load verifizieren, Standard ohne Polyfills prüfen |
| **5.9 Headless-Pool** | 0.05 Tag | 18/18 bleibt grün — wenn Pool keine KTX2/TIFF-Assets enthält, läuft alles wie bisher (Polyfills werden nie getriggert) |
| **5.10 README + CHANGELOG** | 0.05 Tag | Sprint-Eintrag, Konvention für v0.28.2.1 |
| **5.11 ADR-49** | inkludiert | Polyfill-Lazy-Load-Pattern dokumentiert (§ 9) |
| **5.12 Tag v0.28.2 + Push** | 0.05 Tag | Tag, Push, Latenz |
| **5.13 Memory-Update** | 0.05 Tag | inspector_project.md v0.28.2-Block |

**Total: 1.35 Tage.**

---

## 7. Strategischer Hebel

1. **Konkrete Lücke geschlossen** — Inspector Advanced zeigt jetzt visuell was bisher nur als Label-Text stand. CAD-/Möbel-/Architektur-Workflows profitieren direkt.
2. **Story-stark als USP** — *"Einziger Browser-USDZ-Inspector im OpenUSD-Ökosystem, der KTX2 öffnet"* ist konkret und prüfbar. Kein Marketing-Bullshit.
3. **Anker-treu** — Lazy-Load + Modal-only + Advanced-only hält Schlank-Anker für Standard, Polyfills laden nur bei Bedarf. Privacy-First bleibt (alles lokal).
4. **Anschluss-Sprint v0.28.2.1 (ASTC) ist klein geboren** — Strategie-Sprint-Trennung verhindert ASTC-Komplexität in v0.28.2-Scope zu bringen.
5. **Vorbereitet für v0.28.3 (USDC-Parser)** — Polyfill-Lazy-Load-Pattern wird in v0.28.3 wiederverwendet wenn usd-wasm dort separate Bundles braucht. Sauber gestapelt.

---

## 8. Konkrete Pre-v0.28.2-Steps

1. **v0.28.1 muss released sein** — Theme-Check greift weiterhin für neue Modal-Klassen
2. **Test-Asset mit KTX2-Textur** — falls Pool keines hat, synthetisch erzeugen (z. B. via `toktx`-CLI aus Khronos-Tools). Phase 5.8 braucht echtes Test-Material
3. **Test-Asset mit TIFF-Textur** — analog, falls Pool keines hat

Falls 2+3 fehlen: Code-Chat erzeugt synthetisch oder Plan-Chat-Rückfrage.

---

## 9. Decision-Log-Template

```markdown
### ADR-49 Texture-Polyfills via On-Demand-Lazy-Load im Modal — 2026-06-04

**Kontext:** Seit v0.25.5 erkennt Inspector KTX2/TIFF/ASTC via Magic-Bytes, zeigt aber nur Format-Label. Visuelle Inspektion fehlt — User mit komplexen B2B-Assets müssen extern decodieren. CAD-/Möbel-/Architektur-Workflows betroffen. Sprint v0.28.2 (Sequenz-Tausch mit v0.28.3 wegen Hosting-Frage) schließt die Lücke für KTX2 und TIFF.

Alternativen geprüft:
- **Inline-Preview im Report:** Polyfills würden Bundle-Größe stark heben — bricht Schlank-Anker auch für Advanced
- **Eager Page-Load:** Polyfills bei jedem Advanced-Start laden — Performance-Kosten ohne Nutzen für Users mit reinen PNG/JPEG-Assets
- **Modal-only + On-Demand-Lazy-Load:** Polyfill wird nur bei tatsächlichem KTX2/TIFF-Treffer geladen, nur wenn User Modal öffnet — Best of Both

**Entscheidung:** Modal-only Preview, On-Demand-Lazy-Load. Polyfills als separate Bundles in `vendor/`-Verzeichnis (analog Three.js-Bundle aus v0.28.0). Build-Step injiziert Bundles in Advanced via Marker-Pattern. Loader-Funktionen analog `loadThreeBundle()` aus v0.28.0.2 mit Promise-Caching. Modal-Init prüft Format und ruft passenden Loader. Spinner während Load, Fallback-Toast bei Decode-Fehler. Standard bleibt vollständig unangetastet (Schlank-Anker).

**Konsequenz:** Inspector Advanced kann KTX2 und TIFF visuell darstellen — einzig im Browser-OpenUSD-Ökosystem. Bundle-Wachstum nur bei tatsächlichem Bedarf (User mit reinen PNG/JPEG-Assets zahlen nichts). Architektur-Anker (Schlank, Privacy, Single-File-pro-Distribution) bleiben unangetastet. Pattern für Polyfill-Lazy-Load ist etabliert und kann in v0.28.2.1 (ASTC) + ggf. v0.28.3 (USDC-Parser-Splitting) wiederverwendet werden.
```

---

## 10. Quellen / Referenz-Links

- Vorgänger v0.28.1: `docs/ROADMAP-v0.28.1.md`
- v0.25.5 Magic-Bytes-Detection-Pattern: `docs/ROADMAP-v0.25.5.md`
- v0.24 Texture-Vollbild-Modal: `docs/ROADMAP-v0.24.md`
- v0.28.0.2 Lazy-Load-Pattern (Vorbild): `docs/ROADMAP-v0.28.0.2.md`
- v0.28.0 Bundle-Strategie via vendor/: `docs/ROADMAP-v0.28.0.md` (ADR-44)
- v0.28.0.7 Theme-Check: `docs/CSS-THEME-REFERENCE.md`
- Polyfill-Quellen:
  - KTX-Parse: https://github.com/donmccurdy/KTX-Parse
  - Basis-Universal: https://github.com/BinomialLLC/basis_universal
  - UTIF.js: https://github.com/photopea/UTIF.js
- Privates Persona-Anker: `/Users/g/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`

---

**Ende v0.28.2-Briefing.** Nach Sprint: Tag `v0.28.2`, Push, Memory-Update, kurzes Artikel-Update. Dann Pause / Wechsel auf andere Themen. v0.28.2.1 (ASTC) wartet auf Bedarf, v0.28.3 (USDC-Parser) braucht Strategie-Klärung wegen COOP/COEP.
