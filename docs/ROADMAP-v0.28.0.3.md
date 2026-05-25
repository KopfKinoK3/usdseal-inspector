# Roadmap v0.28.0.3 — Asset-Klassifikation + Pre-Renderer-Check

**Status:** Vorbereitungs-Dokument · 2026-05-25
**Story-Slot:** *"Inspector Advanced weiß vor dem Klick, ob der Player Erfolg hat — und sagt es dem User ehrlich."*
**Ziel:** Pre-Renderer-Check analysiert das gedroppte USDZ und prädiziert Render-Erfolg. Button-Text wird dynamisch nach Klassifikation. Heuristik wird im Sprint **empirisch entwickelt**, nicht spekulativ — Phase 5.0 misst zuerst, was tatsächlich rendert vs. crasht.
**Aufwand:** M (1.5–2.5 Tage)

> Folge-Sprint von v0.28.0.2 (Lazy-Load + Try/Catch). Spike-Charakter — die Heuristik ist hypothesengetrieben und wird gegen Real-World-Pool validiert. Wenn die Heuristik in Phase 5.0 als unzuverlässig erweist, wird der Sprint kleiner (nur statischer Beta-Banner-Text mit Klassifikations-Kategorien als Hinweis, keine dynamische Button-Anzeige).

---

## 1. Befund

v0.28.0.2 hat den Player ausfall-tolerant gemacht — Standard-Report läuft IMMER, Player ist opt-in. Aber: der User weiß nicht im voraus, ob sein Klick auf *"3D-Preview starten"* Erfolg hat. Er klickt, wartet auf den Spinner, sieht im schlimmsten Fall den Fallback-Toast — und denkt *"war wohl Pech, probiere ich nochmal"*.

**Bessere User-Experience:** Inspector Advanced **prädiziert vorab**, ob das gedroppte USDZ render-kompatibel ist, und kommuniziert das im Button-Text:

- *"▶ 3D-Preview starten ✓"* — Asset gehört zur SalmonPasta-Klasse, Rendering wahrscheinlich erfolgreich
- *"⚠ 3D-Preview testen — Render-Erfolg unsicher"* — Asset hat Risiko-Indikatoren, User entscheidet bewusst
- *"⊘ 3D-Preview nicht empfohlen"* + Begründung — Asset hat bekannte Crash-Trigger (USDC-Binary-Materials, Variants etc.)

**Voraussetzung:** Heuristik muss messbar funktionieren. Das ist nicht trivial — Three.js' USDLoader r184 hat eigene undokumentierte Limits. Phase 5.0 dieses Sprints ist deshalb ein **Spike**: gegen den realen Test-Pool messen, welche Asset-Eigenschaften mit Render-Erfolg korrelieren.

**Memory-Hinweise aus heutiger Diagnose:**
- SalmonPasta (simple USDA, single-prim, single-material) rendert ✓
- DIEGOsat (komplexer Master mit Re-Import, mehrere Materialien) rendert schwarz
- Frankfurt (USDC-Binary mit 22 Sub-Files) friert Browser ein

**Hypothesen-Kandidaten für Heuristik (Spike testet):**
- **USDC-Binary-Detection:** Wenn ZIP-Inhalte USDC-Binary-Materials enthalten → wahrscheinlich Crash/Freeze
- **Polycount-Threshold:** Über N Triangles → Browser-Risiko (N empirisch ermitteln)
- **Material-Count:** Mehr als M Materialien → schwarze Visualisierung wahrscheinlich
- **Variants/Animation:** Wenn detektiert → USDLoader rendert nicht
- **Multi-Layer / References:** Komposition wird nicht aufgelöst → fehlende Inhalte
- **File-Size:** Über X MB → Risiko-Indikator (X empirisch)

---

## 2. Phase 5.0 — Diagnose (Spike, kritischer Schritt!)

**Dieser Sprint steht und fällt mit Phase 5.0.** Hier wird die Heuristik geboren oder verworfen.

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Test-Pool inventarisieren — welche Assets stehen für den Spike zur Verfügung
ls -lh ../usdz/ ../usdz/review-pool/

# B) Pro Asset: Standard-Report aufnehmen (was sagt der Inspector über die Struktur)
# - SalmonPasta:    triangles, materials, USDA/USDC, file-size, prims, variants?
# - DIEGOsat:       wie oben
# - Frankfurt:      wie oben
# - review-pool/*:  wie oben (7 Files)
# - error_explicit: wie oben

# C) Pro Asset: Player-Versuch im Browser (mit v0.28.0.2-Lazy-Load) und Resultat protokollieren
# Resultat-Kategorien: PASS / SCHWARZ / CRASH / BROWSER-FREEZE / PARTIAL

# D) Korrelations-Matrix aufstellen:
# | Asset | USDC? | Polys | Mats | Variants | File-MB | Resultat |
# Daraus Heuristik ableiten.

# E) Three.js-Issue-Tracker durchsuchen nach bekannten Limits:
# https://github.com/mrdoob/three.js/issues?q=USDLoader
# Welche Asset-Eigenschaften melden andere als problematisch?
```

→ **Output Phase 5.0:** `docs/v0.28.0.3-spike-results.md` mit:
1. Asset-Matrix (mindestens 10 Assets, Eigenschaften + Render-Resultat)
2. Identifizierte Crash-Trigger (welche Eigenschaft korreliert wie stark mit Failure)
3. Heuristik-Entwurf (3-stufige Klassifikation: ✓ / ⚠ / ⊘)
4. **Go/No-Go-Entscheidung:** Heuristik funktioniert oder nicht?

**Wenn Heuristik nicht funktioniert** (Resultate sind chaotisch, keine klare Korrelation): Sprint wird kleiner — nur ein **statischer Hinweis-Text** *"Beta funktioniert zuverlässig nur mit einfachen USDZs — siehe Dokumentation für Asset-Klassen"* + eine `docs/PLAYER-ASSET-COMPATIBILITY.md` mit Tipps wann Player ausprobieren. Keine dynamische Button-Anzeige.

**Wenn Heuristik funktioniert:** Phasen 5.1-5.5 setzen sie um.

---

## 3. Scope (abhängig vom Spike-Ergebnis)

### 3.1 Klassifikations-Funktion `classifyAssetForPlayer()`

Nach dem Standard-Report (der bereits in v0.28.0.2 zuerst läuft), läuft eine schmale Klassifikations-Funktion über die bereits geparsten Asset-Daten:

```javascript
function classifyAssetForPlayer(assetReport) {
  // assetReport ist das Output des Standard-Inspectors
  // (enthält: components, materials, geometryStats, hasUsdcBinary,
  //  hasVariants, hasAnimation, hasMultiLayer, etc.)
  
  // Heuristik aus Spike-Phase 5.0 — hier exemplarisch:
  if (assetReport.hasUsdcBinary) {
    return {
      level: 'BLOCK',
      reason: 'USDC-Binary-Materials werden von Three.js USDLoader r184 nicht zuverlässig verarbeitet'
    };
  }
  if (assetReport.geometryStats.triangles > 500_000) {
    return {
      level: 'CAUTION',
      reason: 'Hohe Polycount — Browser-Performance kann leiden'
    };
  }
  if (assetReport.hasVariants || assetReport.hasAnimation) {
    return {
      level: 'CAUTION',
      reason: 'Variants/Animation werden im 3D-Preview nicht aufgelöst'
    };
  }
  // ... weitere Regeln aus Spike
  return { level: 'PASS', reason: null };
}
```

Wichtig: Heuristik ist **konservativ** (lieber zu oft CAUTION als zu oft falscher PASS — User-Vertrauen ist wichtiger als Optimismus).

### 3.2 Dynamischer Button-Text

Drei Zustände, je nach `level`:

- **PASS:** `▶ 3D-Preview starten` (Standard-Primärfarbe, voll klickbar)
- **CAUTION:** `⚠ 3D-Preview testen — {reason}` (Warn-Farbe, voll klickbar, User entscheidet bewusst)
- **BLOCK:** `⊘ 3D-Preview nicht empfohlen — {reason}` (Disabled-Look, aber **trotzdem klickbar** auf User-Wunsch — wir bevormunden nicht, wir informieren)

DE+EN, 6-9 neue i18n-Keys (Button-Texte + Reason-Strings für die häufigsten Klassifikations-Gründe).

### 3.3 Banner-Update

Beta-Banner aus v0.28.0.2 wird je nach Klassifikation ergänzt:

- **PASS:** Banner bleibt minimal *"Beta — Read-only-Preview"*
- **CAUTION / BLOCK:** Banner zeigt **konkrete Gründe**: *"Beta — dieses Asset hat {reason}, Render-Erfolg unsicher. Inspection-Report unten zeigt alle Inhalte zuverlässig."*

### 3.4 Compatibility-Doku

`docs/PLAYER-ASSET-COMPATIBILITY.md` (neu) — kuratierte Liste:
- **Gehen heute zuverlässig:** SalmonPasta-Klasse (single-prim USDA, einfache Materialien, < 100k Triangles)
- **Schwarzes Rendering wahrscheinlich:** Komplexe Materialien, PBR mit vielen Channels
- **Browser-Crash-Risiko:** USDC-Binary mit > 20 Sub-Files, große USDZs (> 30 MB)
- **Nicht supportet:** Variants, Animation, Multi-Layer-Komposition

Doku wird in Banner verlinkt: *"Welche Assets gehen, welche nicht? → Compatibility-Doku"*

### 3.5 Was NICHT in v0.28.0.3

- **Keine USDLoader-Bugfixes** — Inspector ist nicht Three.js-Maintainer
- **Keine alternative Renderer** (Babylon.js, model-viewer-Wrapper) — eigener Sprint, wenn Three.js sich als Sackgasse erweist
- **Kein Telemetrie-Crash-Log** → v0.28.0.4 oder später
- **Keine Heuristik-Selbstlern** (z. B. "wenn 3x in Folge BLOCK-klassifiziert, immer als BLOCK") — overengineering für jetzt

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Standard-Inspector-Pipeline | unverändert | liefert Klassifikations-Input (Materials, USDC-Detection, etc.) |
| Three.js Bundle | unverändert | nur Klassifikations-Logik vorne dran |
| Three.js GitHub Issues | extern referenziert | Spike-Recherche in Phase 5.0 |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.28.0.2 released und live | ⏳ |
| 2 | Test-Pool min. 10 Assets | ⏳ heute 7 review-pool + DIEGOsat + Frankfurt + SalmonPasta + error_explicit = 11, reicht |
| 3 | Standard-Inspector liefert hasUsdcBinary / hasVariants / hasAnimation als API | ⚠ klärt Phase 5.0 grep |

**1 grün-pending, 1 grün, 1 zu prüfen.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Spike** | 0.5-0.8 Tag | **Kritisch:** Asset-Matrix erstellen, Heuristik-Hypothesen testen, Go/No-Go-Entscheidung |
| **5.1 Klassifikations-Funktion** | 0.2 Tag | classifyAssetForPlayer() auf Standard-Report aufsetzen, Unit-Tests gegen Asset-Matrix |
| **5.2 Dynamischer Button-Text** | 0.2 Tag | UI-Anbindung, drei Zustände, i18n-Keys |
| **5.3 Banner-Anpassung** | 0.15 Tag | Beta-Banner zeigt Klassifikations-Reason wenn CAUTION/BLOCK |
| **5.4 Compatibility-Doku** | 0.2 Tag | docs/PLAYER-ASSET-COMPATIBILITY.md schreiben, in Banner verlinken |
| **5.5 Browser-Verifikation** | 0.15 Tag | Chrome+Safari, alle 11 Pool-Assets durchklicken, Klassifikation gegen tatsächliches Render-Resultat checken |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 bleibt grün |
| **5.7 README + CHANGELOG** | 0.05 Tag | Sprint-Eintrag mit Heuristik-Übersicht |
| **5.8 ADR-46** | inkludiert | Asset-Klassifikations-Heuristik dokumentiert |
| **5.9 Tag v0.28.0.3 + Push** | 0.05 Tag | Tag, Push, Latenz |
| **5.10 Memory-Update** | 0.05 Tag | inspector_project.md ergänzt v0.28.0.3-Block + Spike-Befunde |

**Total: 1.6–2.5 Tage** (mit Spike); **0.5-0.8 Tag** wenn Spike No-Go ergibt und Sprint zu statischer Doku-Variante schrumpft.

---

## 7. Strategischer Hebel

1. **Erwartungs-Management vor dem Klick** — User klickt nicht ins Leere, sondern mit Vor-Information. Reduziert Frustration drastisch.
2. **Heuristik wird zur Marketing-Story** — *"Inspector Advanced ist ehrlich über seine eigenen Grenzen"* ist stärker als verschleiernde Fehler-Toasts.
3. **Compatibility-Doku als SEO-Magnet** — Asset-Klassen-Beschreibung mit konkreten Beispielen ist Suchmaschinen-Futter (*"warum rendert Three.js USDZLoader mein Asset nicht"*).
4. **Vorbereitung für v0.28.0.4 (Crash-Log) und v0.29 (LLM-Findings)** — Klassifikations-Daten sind Eingabe für beide.

---

## 8. Konkrete Pre-v0.28.0.3-Steps

1. **v0.28.0.2 muss released sein** — Player ist ausfall-tolerant, Standard-Report läuft IMMER
2. **Test-Pool griffbereit** — alle 11 Assets im `../usdz/`-Pfad verfügbar (Spike-Voraussetzung)

Falls beide erfüllt: *"Keine — alle Vorbedingungen erfüllt."*

---

## 9. Decision-Log-Template

```markdown
### ADR-46 Asset-Klassifikation für Player-Erwartungs-Management — 2026-05-25 (oder Sprint-Datum)

**Kontext:** v0.28.0.2 hat den Player ausfall-tolerant gemacht, aber User klickt blind in den Crash. Drei Asset-Klassen wurden im Erst-Test identifiziert (PASS / SCHWARZ / FREEZE) — aber keine Heuristik, die das vorab erkennt.

Alternativen geprüft:
- **Keine Heuristik, nur Beta-Banner:** Ehrlich aber unspezifisch — User lernt nicht aus dem Banner welches Asset welches Risiko hat
- **Heuristik mit Selbst-Lern (3x BLOCK = immer BLOCK):** Overengineering für jetzt, bringt erst Wert wenn Telemetrie da ist
- **Konservative regelbasierte Heuristik mit Compatibility-Doku:** Spike-getrieben, ehrlich, erweiterbar, kein Lern-Risiko

**Entscheidung:** Konservative Heuristik mit drei Klassifikations-Stufen (PASS / CAUTION / BLOCK). Regeln aus Spike-Phase 5.0 abgeleitet, konkret: {Regeln einfügen, sobald Spike fertig}. Button-Text dynamisch, Banner zeigt Klassifikations-Reason, Compatibility-Doku verlinkt aus Banner.

**Konsequenz:** User klickt mit Vor-Information statt blind. Klassifikation kann später als Eingabe für Crash-Log-Sammler (v0.28.0.4?) und LLM-Findings-Erklärungen (v0.28.1) verwendet werden. Heuristik bleibt **statisch regelbasiert** — keine Selbst-Lern-Logik, keine Telemetrie nötig. Bei Three.js-Update wird Heuristik überprüft.
```

---

## 10. Quellen / Referenz-Links

- Vorgänger v0.28.0.2: `docs/ROADMAP-v0.28.0.2.md`
- ADR-44 (Three.js Inline-Embed): warum überhaupt USDLoader
- ADR-45 (Graceful Degradation): Pre-Renderer-Check ist additive Schicht
- Three.js USDLoader Issue-Tracker: extern, Spike recherchiert
- `docs/PLAYER-ASSET-COMPATIBILITY.md`: wird in diesem Sprint erstellt

---

**Ende v0.28.0.3-Briefing.** Spike-Sprint mit Go/No-Go in Phase 5.0. Nach Sprint: Tag `v0.28.0.3`, Push, Memory-Update.
