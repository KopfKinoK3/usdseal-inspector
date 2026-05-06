# Roadmap v0.25.7 — USDC-Material-Limitation ehrlich kommunizieren

**Status:** ✅ **COMPLETED 2026-05-06** · Commit `627f86b`, Tag `v0.25.7` online
**Story-Slot:** *"Was wir nicht wissen können — und wie wir's sagen"*
**Ziel:** UNUSED-Befund aus Frankfurt-Live-Test mit ehrlicher UI-Kommunikation lösen. ✓ erreicht.
**Aufwand:** 0.3–0.5 Tag. ✓ eingehalten.

## Release-Befund 2026-05-06

| Phase | Status | Ergebnis |
|---|---|---|
| 5.1 Detection-Heuristik | ✅ | `buildChannelMap` erkennt `usdcBinaryMaterials`-Trigger |
| 5.2 UI-Status-Badge | ✅ | UNKNOWN statt UNUSED bei USDC-Binary |
| 5.3 Hinweis-Box | ✅ | DE+EN i18n im Texture-Inventar |
| 5.4 PDF-Report | ✅ | Gleicher Hint als Box in der Asset-Inventory-Sektion |
| 5.5 Verifikation Browser | ✅ | Frankfurt: 55 Texturen UNKNOWN + Hinweis-Box ✓ ; DIEGOsat (signiert + USDC-binary): UNKNOWN-Texturen + Trust-Banner grün — schöner Beleg dass beide Layer parallel funktionieren |
| 5.6 Headless-Pool | ✅ | 18/18 PASS |
| 5.7 README + CHANGELOG | ✅ | v0.25.7-Eintrag |
| 5.8 ADR-33 | ✅ | In `CLAUDE-Inspector-private.md` |
| 5.9 Snapshot + Tag | ✅ | `v0.25.7-snapshot.html` + Commit `627f86b` + Tag |

**Bonus-Bugfix:** `t` als Loop-Var in `forEach`/`map` überschattete die i18n-`t()`-Funktion. Code-Chat hat das beim USDC-Refactor gefangen und auf `tex` umbenannt. Klassischer JavaScript-Shadow-Bug — wurde nur durch das Refactor sichtbar. ADR-PC4 (Verification before Hypothesis) hält.



> Patch-Sprint nach v0.25.6. Master-Übersicht in `../ROADMAP.md`. Diagnose-Quelle: `tests/real-world-2026-05-05.md`.

---

## 1. Befund

**Frankfurt-Real-World-Test 2026-05-05 (v0.25.4-Sweep):** Frankfurt_Varianten_TK_271125_01.usdz hat 22 `.usdc`-Sub-Files (USDC-Binary). Inspector zeigt **alle Texturen als UNUSED** — obwohl die Datei nachweislich auf iPhone in AR Quick Look läuft und alle Texturen sichtbar sind.

**Diagnose:** Used-Detector aus v0.24.1 parsed `inputs:*.connect`-Edges **nur in USDA-Text-Files**. Bei USDC-Binary-Material-Definitionen (wie in Frankfurt) findet er keine Connects → alle referenzierten Texturen werden als UNUSED markiert.

**Bug oder Feature?** Inspector ist **technisch korrekt** — er kann USDC-Binary nicht parsen. Aber die UI-Aussage "UNUSED" ist **falsch**: wir wissen es nicht, wir können es nicht prüfen.

**Architektur-Begrenzung:** USDC-Binary-Decode würde `usd-wasm` (~5-15 MB Bundle) oder Python-Backend benötigen — bricht ADR-PC5 (Architektur-Anker schlägt Feature) und Privacy-First-Anker.

→ **Lösung:** Ehrliche UI-Kommunikation — "unknown" statt "unused", plus Hinweis-Box "USDC-Binary-Materials nicht analysierbar".

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "USDC\|usdc\|inputs:.*connect\|used\|unused" index.html | head -30
```

→ Used-Detector und Texture-Status-Logik lokalisieren. Quelle ist v0.24.1 (Texture-Status-Refinement: used/unused/unknown).

**Wichtig:** "unknown" als Status existiert bereits in v0.24.1. Wir müssen lediglich die **Logik erweitern**: wenn Frankfurt-style USDC-Binary-Materials → automatisch "unknown" statt "unused".

---

## 3. Scope

### 3.1 Detection-Logik

**Heuristik:** wenn USDZ-Container `.usdc`-Dateien enthält UND der USDA-Connect-Parser in keiner USDA-Datei Material-Bindings findet → markiere ALLE Texturen als "unknown" statt "unused".

```javascript
// Pseudocode
function refineTextureStatus(textures, usdaFiles, usdcFiles) {
  const hasUsdcBinary = usdcFiles.length > 0;
  const usdaConnectsFound = usdaFiles.some(f => /inputs:[a-z]+\.connect/.test(f.text));
  
  if (hasUsdcBinary && !usdaConnectsFound) {
    // Wir können Material-Bindings nicht prüfen
    return textures.map(t => ({ ...t, status: 'unknown', reason: 'USDC-Binary-Materials' }));
  }
  
  // Existing v0.24.1-Logik für USDA-Files
  return /* ... */;
}
```

### 3.2 UI-Anpassungen

**Texture-Modal-Status-Badge:**
- Heute: "USED" (grün), "UNUSED" (rot/orange), "UNKNOWN" (grau)
- Neu: bei USDC-Binary-Files automatisch "UNKNOWN" mit Tooltip *"USDC-Binary-Materials können nicht analysiert werden — Texture-Verwendung unklar"*

**Inspector-Banner / Hinweis-Box (neu, oben):**
Wenn Heuristik "USDC-Binary-Materials erkannt" greift, zeige Hinweis:

```
ⓘ Diese USDZ enthält USDC-Binary-Materials.
   Inspector kann Material-Bindings nicht analysieren.
   Texture-Status zeigt "unknown" statt "used/unused".
```

**i18n DE+EN.**

### 3.3 PDF-Report

PDF-Texture-Inventar zeigt analog "unknown" statt "unused" für USDC-betroffene Dateien. Plus: gleiche Hinweis-Box im PDF-Report-Header (in der TEXTURE-INVENTAR-Sektion oder als eigene Notiz oben).

### 3.4 Was NICHT in v0.25.7

- **Kein** USDC-Binary-Decode-Polyfill (wäre ADR-PC5-Verletzung)
- **Keine** neuen Channel-Erkennungs-Pfade für USDC
- **Keine** Validator-Severity-Änderungen — nur UI-Status

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt |
| USDC-Format-Definition | bekannt | OpenUSD-Spec — wir lesen nicht, wir markieren als "unknown" |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.6 stabil released | ✓ Tag online seit 2026-05-06, Commit `962ce00` |
| 2 | UNUSED-Befund-Dokumentation | ✓ `tests/real-world-2026-05-05.md` |
| 3 | Test-Pool mit USDC-Binary-File | ✓ Frankfurt im Pool — Live-Verifikation möglich |

**3 von 3 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | Used-Detector + Texture-Status-Logik in index.html grep |
| **5.1 Detection-Heuristik** | 0.1 Tag | "USDC-Binary erkannt + keine USDA-Connects" → alle Texturen auf "unknown" |
| **5.2 UI-Status-Badge** | 0.05 Tag | "UNKNOWN"-Badge mit Tooltip-Reason "USDC-Binary-Materials" |
| **5.3 Hinweis-Box** | 0.1 Tag | Neuer Banner-Block oben im Inspector + i18n DE+EN |
| **5.4 PDF-Anpassung** | 0.05 Tag | PDF-TEXTURE-INVENTAR zeigt "unknown" + Hinweis-Notiz |
| **5.5 Verifikation Browser** | 0.05 Tag | Frankfurt: alle Texturen "unknown" statt "unused" + Hinweis sichtbar. DIEGOsat (USDA): bleibt unverändert. |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 PASS + neue Frankfurt-Erwartung "unknown" statt "unused" für alle Texturen |
| **5.7 README + CHANGELOG** | 0.05 Tag | "USDC-Material-Limitation transparent kommuniziert" |
| **5.8 ADR-33** | inkludiert | Template § 9 |
| **5.9 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.7, Tag, Push |

**Total: 0.5 Tag konzentrierter Build.**

---

## 7. Strategischer Hebel

v0.25.7 ist **Trust-Anker-Sprint**:

1. **"Inspector lügt nicht":** "UNUSED" bei USDC-Binary war faktisch falsch — "unknown" ist ehrlich. Trust steigt.
2. **ADR-PC5-Bestätigung erneut:** Wir bauen kein USDC-Polyfill, wir kommunizieren ehrlich was wir nicht wissen können.
3. **Konferenz-Slide:** *"Wenn der Inspector etwas nicht prüfen kann, sagt er das. Kein false-positive."* — Differenzierung gegenüber generischen USDZ-Validatoren.
4. **Frankfurt als Test-Asset:** Real-World-Beleg für die USDC-Binary-Behandlung. Reproduzierbar im Headless-Pool.

---

## 8. Konkrete Pre-v0.25.7-Steps

Keine — alle Vorbedingungen erfüllt.

---

## 9. Decision-Log-Template

```markdown
### ADR-33 USDC-Material-Limitation transparent — 2026-05-XX

**Kontext:** Real-World-Test 2026-05-05: Frankfurt-USDZ (22 USDC-Sub-Files) zeigt alle Texturen als UNUSED — obwohl AR Quick Look auf iPhone alle anzeigt. Used-Detector parsed nur USDA-Text-Files.

**Entscheidung:**
- KEIN USDC-Binary-Polyfill (würde ADR-PC5 brechen)
- Heuristik: USDC-Binary erkannt + keine USDA-Connects → Texture-Status auf "unknown"
- UI-Hinweis-Box "USDC-Binary-Materials können nicht analysiert werden"
- PDF-Report analog

**Konsequenz:** Inspector lügt nicht mehr bei USDC-Binary-Files. Privacy-First + Single-File-Anker bestätigt. Frankfurt-Befund reproduzierbar im Headless-Pool dokumentiert.
```

---

## 10. Quellen

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.25.6.md` (PDF-Report User-First)
- Diagnose-Quelle: `../tests/real-world-2026-05-05.md`
- v0.24.1: Texture-Status-Refinement (used/unused/unknown — wo "unknown" erstmals entstand)

---

**Ende v0.25.7-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.7`, Push. Dann v0.25.8 (Regel-Korrekturen).
