# Roadmap v0.28.0.2 — Lazy-Load Player + Graceful Degradation

**Status:** Vorbereitungs-Dokument · 2026-05-25
**Story-Slot:** *"Standard-Report läuft IMMER. 3D-Preview ist additiv, kein Totalausfall mehr — und wird nur geladen, wenn der User sie startet."*
**Ziel:** Render-Reihenfolge umkehren (Standard-Report zuerst, Player additiv). Three.js-Bundle on-demand laden statt Page-Load. Player-Initialisierung in Try/Catch. Frankfurt-Browser-Freeze unmöglich machen, DIEGOsat-Schwarzbild sichtbar dokumentieren.
**Aufwand:** S (1.0–1.5 Tage)

> Patch-Sprint nach v0.28.0.1 (Click-Through-Links beidseitig). Antwort auf Erst-Test-Befunde 2026-05-25: nur SalmonPasta rendert sauber, Frankfurt friert Safari ein, DIEGOsat zeigt schwarzen Canvas. Lösung: Graceful Degradation statt USDLoader-Bugjagd.

---

## 1. Befund

Erst-Test mit Live-URLs `kopfkinok3.github.io/usdseal-inspector/advanced/` am 2026-05-25 ergab:

| Asset | Standard-Inspektion | 3D-Render | Browser-Verhalten |
|---|---|---|---|
| SalmonPasta | ✓ | ✓ | sauber (47.456 Triangles) |
| DIEGOsat_master.usdz | ✓ | ❌ schwarz | Canvas wird gemalt, Geometrie unsichtbar |
| Frankfurt | ✓ | ❌ blockt | Safari friert beim Ladevorgang ein |

**Strukturelles Problem:** Three.js + USDLoader r184 sind heute auf der Render-Pipeline-Ebene **eng-limitiert**. Nur eine schmale Asset-Klasse läuft zuverlässig (single-prim, simple Materialien, kleine Größe). Bei den Frankfurt-/DIEGOsat-Klassen kippt entweder der Browser komplett (Safari-Freeze) oder die Visualisierung silent (schwarzer Canvas).

**Auswirkung in v0.28.0:** Advanced wirkt für 2 von 3 getesteten Real-World-Assets **kaputt**. Standard-Inspektion läuft daneben unverändert, aber der User sieht das nicht — er sieht nur "die Seite ist eingefroren" oder "der Canvas ist schwarz" und schließt: *"Inspector Advanced funktioniert nicht."*

**Ehrliche Diagnose:** Three.js USDLoader r184 ist für die viSales-Asset-Klasse nicht produktionsreif. v0.28.0.2 darf nicht versuchen, das mit Workarounds zu kompensieren — das wäre ADR-PC4-Verstoß ("Spec-Vision schlägt Realität"). Stattdessen wird die Player-Funktion **opt-in und ausfall-tolerant** designed.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Aktuelle Player-Init-Stelle finden
grep -n "USDLoader\|loader.parse" src/inspector.html | head -10
grep -n "ADVANCED-ONLY:START three" src/inspector.html | head -5

# B) Drop-Handler-Flow nachvollziehen
grep -n "handleDrop\|processFile\|renderReport" src/inspector.html | head -10

# C) Wie ist heute die Reihenfolge im Advanced?
#    Vermutung: USDZ-Drop → erst Three.js-Player-Init → dann Standard-Report
#    Ziel:      USDZ-Drop → erst Standard-Report → dann Player on-demand on-Click

# D) Bundle-Größe heute messen
ls -lh advanced/index.html
ls -lh vendor/three-usdloader-r184-bundle.js

# E) Browser-Test mit Console-Logs:
#    DIEGOsat: gibt USDLoader.parse() einen Error? Silent return? THREE.Group leer?
#    Frankfurt in Safari: bei welchem Schritt friert es? Loader.parse selbst oder erst Renderer-Frame?
```

→ Lokalisiert:
1. Bestehende Player-Init-Reihenfolge — welche Funktion ruft Three.js auf, in welchem Lifecycle-Punkt
2. Wo der Standard-Report aktuell **nach** dem Player-Init kommt (sollte vorher kommen)
3. Wie das Bundle heute eingehängt ist (`<script>` im Head? Inline? Async?) — Voraussetzung für Lazy-Load-Refactoring
4. Failure-Modes von USDLoader: silent / loud / browser-freeze — bestimmt Try/Catch-Strategie

**Konsistenz-Check:**
- Advanced-File-Größe **nach** Lazy-Load muss spürbar kleiner sein als heute (~800 KB → ~150 KB initial, Bundle wird on-demand nachgeladen)
- Standard-Report muss bei jedem USDZ-Drop **immer** durchlaufen, unabhängig von Player-State
- Bei deaktiviertem Player muss Advanced-Header trotzdem klar als "Advanced" markiert bleiben (Schlank-Anker-Kommunikation)

---

## 3. Scope

### 3.1 Render-Reihenfolge umkehren

**Heute:** USDZ-Drop → Three.js-Player-Init → Standard-Report  
**Soll:** USDZ-Drop → Standard-Report → Player-Bereich zeigt "starten"-Button

Drop-Handler refactoren: Standard-Inspector-Pipeline (Manifest-Parse, Verify-UI, Geometrie-Stats, Texturen, AR-Diagnose, PDF) läuft **synchron zuerst** und befüllt das DOM. Player-Bereich (oberhalb des Reports im Advanced) zeigt **Platzhalter** + Start-Button.

### 3.2 Three.js-Bundle als Lazy-Load

**Bundle wird nicht initial in `<script>` geladen** — sondern dynamisch on-Click:

```javascript
// Vereinfacht — Code-Chat passt an reale Pipeline an
let bundleLoaded = false;

function loadThreeBundle() {
  return new Promise((resolve, reject) => {
    if (bundleLoaded) return resolve();
    const script = document.createElement('script');
    // Bundle-Inhalt ist im Build-Step entweder:
    //   (a) als separates File vendor/three-usdloader-r184-bundle.js, oder
    //   (b) als data:-URL inline (für single-file-Anker — Code-Chat entscheidet)
    script.src = 'three-usdloader-r184-bundle.js';
    script.onload = () => { bundleLoaded = true; resolve(); };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}
```

**Wichtig:** Bundle bleibt **im Repo** (Architektur-Anker hält — Privacy + Offline). Bei Lazy-Load via separates File: `advanced/three-usdloader-r184-bundle.js` wird ausgeliefert und beim Klick nachgeladen. Single-File-Anker wird hier **bewusst gelockert für Advanced** — Begründung in ADR-45 (Schlank-Anker + Graceful Degradation rechtfertigen Two-File-Distribution für Advanced).

**Alternative:** Bundle inline als Base64-encoded `data:`-URL im Source — dann bleibt Advanced single-file, aber Lazy-Load ist nur "JS-Execution-Verzögerung", nicht "Netzwerk-Spar". Code-Chat entscheidet in Phase 5.0 was technisch sauberer ist.

### 3.3 Player-UI-Layout

**Im Advanced, oberhalb des Standard-Reports:**

```
┌────────────────────────────────────────────────────────────┐
│ 🎬 3D-Preview (Beta · v0.28.0.2)                          │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │                                                        │ │
│ │          [Platzhalter / Player-Canvas]                 │ │
│ │                                                        │ │
│ │   ⓘ 3D-Preview ist eine Beta-Funktion und              │ │
│ │     funktioniert heute zuverlässig nur mit             │ │
│ │     einfachen USDZs (single-prim, single-material).    │ │
│ │     Für komplexe Assets bleibt der Inspection-         │ │
│ │     Report unten die zuverlässige Quelle.              │ │
│ │                                                        │ │
│ │           [▶ 3D-Preview starten]                       │ │
│ │                                                        │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│ 📋 Inspection-Report                                       │
│ (Standard-Output: Manifest, Verify, Geometrie, Texturen,   │
│  AR-Diagnose, USDseal-Trust, PDF-Download)                 │
└────────────────────────────────────────────────────────────┘
```

**Zustände des Player-Bereichs:**

1. **Vor USDZ-Drop:** *"USDZ ziehen um Player zu aktivieren"*-Text, Button disabled
2. **Nach USDZ-Drop, vor Player-Start:** Platzhalter + Beta-Hinweis + Button enabled
3. **Beim Klick auf "starten":** Spinner *"Three.js-Bundle wird geladen…"* → bei Erfolg: Canvas wird befüllt → bei Crash: Toast *"3D-Preview konnte nicht gerendert werden. Asset bleibt unten im Inspection-Report verfügbar."*
4. **Nach erfolgreichem Render:** Canvas mit Orbit-Controls, Banner "Beta — Geometrie und Standard-Materialien" wie in ADR-44

### 3.4 Try/Catch um die ganze Player-Pipeline

```javascript
async function startPlayer(usdzBuffer) {
  try {
    await loadThreeBundle();
    const loader = new THREE.USDLoader();
    const group = await Promise.resolve(loader.parse(usdzBuffer));
    initSceneWithGroup(group);
  } catch (err) {
    console.error('[v0.28.0.2] Player-Crash:', err);
    showPlayerFallback(err);
    // Standard-Report ist bereits oben fertig — kein Cascade-Fail
  }
}

function showPlayerFallback(err) {
  // Toast über Canvas-Bereich:
  // "3D-Preview konnte nicht gerendert werden — Inspection-Report unten unverändert verfügbar"
  // Plus dezenter Detail-Link "Fehler anzeigen" → öffnet <details> mit err.message
}
```

**Wichtig:** Try/Catch fängt sowohl Bundle-Load-Errors als auch Parser-Errors als auch Renderer-Errors. Standard-Report ist **unabhängig** in der DOM, Crash dort betrifft ihn nicht.

### 3.5 Beta-Banner (immer sichtbar)

Oberhalb des Player-Bereichs eine schmale Banner-Zeile:

> **Beta:** Die 3D-Preview ist experimentell. Sie funktioniert heute zuverlässig nur mit einfachen USDZs. Für die zuverlässige Inhalts-Analyse nutze den Inspection-Report unten.

DE+EN, 2 neue i18n-Keys (`player_beta_banner_de` / `player_beta_banner_en`).

### 3.6 Was NICHT in v0.28.0.2

- **Keine Asset-Klassifikation** (Pre-Renderer-Check mit USDA-vs-USDC-Heuristik, Variants-Detection etc.) → das ist v0.28.0.3-Scope
- **Keine dynamischen Button-Texte** je nach Asset → v0.28.0.3
- **Kein Crash-Log-Sammler** → v0.28.0.4 oder später
- **Keine USDLoader-Bugfixes** — Bugs bleiben in Three.js, wir reagieren nur darauf
- **Keine v0.28.0.1-Funktionalität verändern** — Click-Through-Links beidseitig bleiben wie sind

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Three.js + USDLoader r184 Bundle | unverändert | bleibt im Repo, nur Lade-Strategie ändert sich |
| Standard-Inspector-Pipeline | unverändert | wird nur zeitlich nach vorn gezogen |
| INSPECTOR_VERSION | Bump auf 0.28.0.2 | ADR-38 hält |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.28.0 released und live | ✓ |
| 2 | v0.28.0.1 Click-Through-Links beidseitig released | ⏳ läuft beim Code-Chat |
| 3 | Erst-Test-Befunde verfügbar | ✓ (2026-05-25) |
| 4 | Build-Step Variante Y funktioniert | ✓ (v0.28.0) |

**3 von 4 grün, 1 läuft parallel — kann nach v0.28.0.1-Tag direkt starten.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.1 Tag | grep + Bundle-Größe + Failure-Mode-Test im Browser |
| **5.1 Render-Reihenfolge umkehren** | 0.2 Tag | Drop-Handler refactoren, Standard-Report-Pipeline läuft zuerst synchron |
| **5.2 Bundle-Lazy-Load-Mechanik** | 0.2 Tag | Entscheidung separates File vs data-URL, loadThreeBundle()-Funktion bauen, Bundle-Größe-Verifikation |
| **5.3 Player-UI-Layout** | 0.2 Tag | Platzhalter-Container, Button, Beta-Banner, i18n-Keys (3-4 neue) |
| **5.4 Try/Catch + Fallback-Toast** | 0.15 Tag | Async-Wrapper um Three.js-Pipeline, showPlayerFallback() mit Detail-Link |
| **5.5 Browser-Verifikation** | 0.15 Tag | Chrome+Safari mit SalmonPasta (sollte gehen), DIEGOsat (sollte Toast zeigen), Frankfurt (sollte Toast oder Spinner-Hang zeigen — egal, Standard-Report ist sichtbar) |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 muss grün bleiben (Standard-Pipeline unverändert) |
| **5.7 README + CHANGELOG** | 0.05 Tag | Sprint-Eintrag in beiden Files, Beta-Hinweis im Advanced |
| **5.8 ADR-45** | inkludiert | Graceful-Degradation-Pattern dokumentiert (siehe § 9) |
| **5.9 Tag v0.28.0.2 + Push** | 0.05 Tag | Tag, Push, GitHub-Pages-Latenz |
| **5.10 Memory-Update** | 0.05 Tag | inspector_project.md ergänzt v0.28.0.2-Block |

**Total: 1.0–1.5 Tage.**

---

## 7. Strategischer Hebel

1. **Kein Totalausfall mehr** — User sieht bei jedem Asset den Standard-Report, auch wenn Player crasht. Inspector-Advanced fühlt sich nie kaputt an.
2. **Ehrliche Beta-Kommunikation** — wir täuschen keine Production-Reife vor, der User weiß was ihn erwartet. Passt zur USDseal-Familien-Story ("ehrlich kommunizieren statt überversprechen").
3. **Schlank-Anker zurückgewonnen für Advanced** — initial 150 KB statt 800 KB. Marketing-Argument *"Inspector Advanced ist trotz Power-Features schlank im Erstkontakt"* wird ehrlich.
4. **Safari-Freeze unmöglich solange User nicht aktiv klickt** — Frankfurt-Asset löst keinen Browser-Hänger mehr aus, User entscheidet selbst ob er Risiko nimmt.
5. **Vorbereitung für v0.28.0.3** — Player-Bereich ist jetzt isoliert, Pre-Renderer-Check (Asset-Klassifikation) lässt sich sauber als separate Schicht draufpacken.

---

## 8. Konkrete Pre-v0.28.0.2-Steps

1. **v0.28.0.1 muss released sein** (Click-Through-Links beidseitig) — sonst Konflikt im Header-Layout
2. **Asset-Failure-Pattern dokumentiert** — Erst-Test-Befunde 2026-05-25 in den Memory-Block aufgenommen, Code-Chat hat Kontext

Falls beide erfüllt: *"Keine — alle Vorbedingungen erfüllt."*

---

## 9. Decision-Log-Template

```markdown
### ADR-45 Graceful Degradation für Advanced-Player — 2026-05-25

**Kontext:** v0.28.0 Erst-Test zeigte, dass Three.js USDLoader r184 nur eine schmale Asset-Klasse zuverlässig rendert (SalmonPasta-Klasse: single-prim, simple Materialien). Frankfurt friert Safari ein, DIEGOsat zeigt schwarzen Canvas. Inspector Advanced wirkt für 2 von 3 Real-World-Assets kaputt — obwohl Standard-Report unverändert funktioniert.

Alternativen geprüft:
- **USDLoader-Bugfix-Tiefe:** Three.js-Upstream-Fixes warten oder selbst forken — Aufwand L bis XL, Disziplin-Bruch (Inspector ist nicht Three.js-Maintainer)
- **Player komplett rausnehmen:** Ehrlich, aber Three.js-Investition aus v0.28.0 wäre verschenkt
- **Render-Reihenfolge umkehren + Try/Catch + Lazy-Load:** Standard-Report läuft IMMER, Player ist additiv + ausfall-tolerant + opt-in

**Entscheidung:** Graceful-Degradation-Pattern. Drei zusammenhängende Maßnahmen: (1) Standard-Report rendert synchron zuerst, (2) Three.js-Bundle wird on-demand on-Click geladen, (3) Player-Pipeline läuft komplett in Try/Catch mit Fallback-Toast. Plus immer-sichtbares Beta-Banner mit klarer Erwartungs-Kommunikation.

**Konsequenz:** Inspector Advanced verliert für Edge-Case-Assets nicht mehr seine Hauptfunktion. Schlank-Anker für Advanced wird zurückgewonnen (initial ~150 KB statt ~800 KB). Lazy-Load lockert Single-File-Anker für Advanced **bewusst** — Bundle ist separates File `advanced/three-usdloader-r184-bundle.js` (oder data-URL-encoded, Code-Chat entscheidet). Begründung: Schlank-Anker des Advanced schlägt Single-File-Anker des Advanced, ADR-PC5 hält in der allgemeinen Form *"Architektur-Anker schlägt Feature, Anker-Konflikte werden pro Distribution gelöst"*. Pre-Renderer-Check (Asset-Klassifikation) folgt in v0.28.0.3 als zweite Schicht.
```

---

## 10. Quellen / Referenz-Links

- Vorgänger v0.28.0: `docs/ROADMAP-v0.28.0.md`
- Vorgänger v0.28.0.1 (UI-Polish): wird parallel released
- ADR-44 (Three.js Inline-Embed): Kontext für Bundle-Strategie-Lockerung
- ADR-PC5 (Architektur-Anker schlägt Feature): wird in der allgemeinen Form bestätigt
- Erst-Test-Befunde: Plan-Chat-Memory 2026-05-25
- Privates Persona-Anker: `/Users/g/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`

---

**Ende v0.28.0.2-Briefing.** Nach Sprint: Tag `v0.28.0.2`, Push, Memory-Update. Dann v0.28.0.3 (Asset-Klassifikation + Pre-Renderer-Check) als Folge-Briefing.
