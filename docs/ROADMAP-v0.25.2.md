# Roadmap v0.25.2 — QR-Code-Pivot

**Status:** ✅ **COMPLETED 2026-05-04** · Commit `ff8e208`, Tag `v0.25.2` online
**Story-Slot:** *"QR-Code zurückgezogen — ehrlich Privacy-First"*
**Ziel:** QR-Code-Feature ersatzlos rausbauen + ehrliche UI-Hilfe für iOS-AR-Test einbauen. ✓ erreicht.
**Aufwand:** 0.5 Tag konzentrierter Build (Pivot-Hotfix). ✓ eingehalten.

> Pivot-Release. Master-Übersicht in `../ROADMAP.md`.

## Release-Befund 2026-05-04

| Phase | Status | Ergebnis |
|---|---|---|
| 5.1 Code-Removal | ✅ | ~58 Zeilen raus, null QR-Artefakte |
| 5.2 iOS-Hilfe-Block | ✅ | DE+EN, AirDrop/iCloud/Mail, ~14 Zeilen HTML |
| 5.3 Browser-Verifikation | ✅ | Chrome + Safari grün, kein qrcode-svg im Network-Tab |
| 5.4 Headless-Pool | ✅ | 7/7 PASS |
| 5.5 README + CHANGELOG | ✅ | Sektion ersetzt, v0.25.2-Eintrag mit Pivot-Begründung |
| 5.6 ADR-PC5 | ✅ | In `CLAUDE-Inspector-private.md` dokumentiert |
| 5.7 Snapshot + Tag | ✅ | `v0.25.2-snapshot.html` + Tag `v0.25.2` (Commit `ff8e208`) |

**Mini-Patch (Polish auf gleichen Tag):** `by viSales GmbH`-Space-Fix (Flexbox-Whitespace-Pitfall, Span-Wrap-Lösung) + Cache-Counter nur bei `count > 0` sichtbar (UX-Polish auf leerem Inspector). Phase 3 + 4 erneut grün vor Push.



---

## 1. Befund — der Architektur-Konflikt

User-Report 2026-05-04 (Real-World-Test mit eigenem 26 MB TK-Asset): QR-Code aus v0.25 zeigt URL der GitHub-Pages-Inspector-Seite — Scan startet **kein** USDZ in AR Quick Look, sondern öffnet nur den Inspector erneut. Hard-Fail.

**Spike-Auswertung 2026-05-04 (`inspector-spikes/spike-b-url-parameter.html` + `spike-c-direct-ar.html`):**

| Versuch | Warum es scheitert |
|---|---|
| Data-URI in QR (`data:model/vnd.usdz+zip;base64,...`) | QR-Code-Limit ~3 KB Text, USDZ sind MB-groß. Technisch unmöglich. |
| Blob-URL (`blob:https://...`) | Nur in der erstellenden Browser-Session gültig, iPhone hat keinen Zugriff. |
| Service Worker / Local Cache | Funktioniert nur im selben Browser-Kontext, nicht cross-device. |
| Temp-Upload zu Server | Bricht Privacy-First + Single-File + No-Backend gleichzeitig. |
| WebRTC / WLAN-Tunnel | Inspector ist Single-File-HTML, kein Server möglich. |

**Konklusion:** Drag&Drop-USDZs haben **keine öffentliche URL**, die ein iPhone erreichen könnte. QR-Code-Feature für Drag&Drop ist mit den Architektur-Ankern technisch unvereinbar.

---

## 2. Phase 5.0 — Diagnose vor Pivot (ADR-PC4 strikt)

Phase 5.0 wurde via Sandbox-Spikes durchgespielt (`inspector-spikes/`). Beide Spikes zeigten den Architektur-Konflikt empirisch — kein weiterer Diagnose-Bedarf.

**Spike-Files behalten** als Lessons-Learned-Doku (Beleg: "Wir haben es versucht, es geht nicht"). Sie sind ein gültiges **Negativ-Spike-Ergebnis**.

---

## 3. ADR-PC5 (neu) — Architektur-Anker schlägt Feature

**Kontext:** v0.25 hatte den QR-Code-Workflow als Komfort-Feature eingebaut, ohne die Architektur-Anker (100% client / Single-File / Privacy-First / kein Backend) gegen die Mechanik gegenzuprüfen.

**Entscheidung:** Wenn ein Feature einen Architektur-Anker bricht, **fliegt das Feature, nicht der Anker**. Die Anker sind das viSales-Differenzierungsmerkmal — sie zu erweichen kostet mehr als jeder Komfort-Gewinn.

**Konsequenz:** v0.25.2 baut QR-Code ersatzlos zurück. README + UI kommunizieren den Privacy-First-Pfad transparent als bewusste Entscheidung, nicht als Limitation.

---

## 4. Scope

### 4.1 Was rausfliegt

| Element | Lokation | Bemerkung |
|---|---|---|
| `<button id="show-qr">` und alle Click-Handler | `index.html` | Komplett raus |
| `qrcode-svg` CDN-Lazy-Load-Logik | `index.html` `<script>`-Section | Komplett raus |
| QR-Modal `<dialog id="qr-modal">` | `index.html` | Komplett raus |
| QR-bezogene CSS-Klassen | `index.html` `<style>` | Komplett raus |
| QR-bezogene i18n-Keys (`qr.button`, `qr.title` etc.) | `I18N`-Map | Aus DE + EN entfernen |
| QR-Erwähnung in README | `README.md` | Sektion "QR-Code-Brücke" durch "iOS AR-Test"-Sektion ersetzen |

**Zeilen-Schätzung:** ~50–70 Zeilen Code raus.

### 4.2 Was reinkommt

**UI-Hilfe-Block** (an Stelle des QR-Buttons, gleicher Platz):

```
🍎 So testest du AR Quick Look auf deinem iPhone

Drei Wege, die USDZ aufs iPhone zu bekommen:
  1. AirDrop (Mac → iPhone, sofort, AR Quick Look startet beim Tap)
  2. iCloud Drive (Datei reinziehen → auf iPhone "Files"-App öffnen)
  3. Mail / Slack / Messages an dich selbst
  
Beim Tap auf die USDZ-Datei auf iPhone startet AR Quick Look automatisch.
```

**Mini-Block, ~10–15 Zeilen HTML.** Keine neuen Dependencies.

### 4.3 Was bleibt unverändert

- `<model-viewer>`-Preview auf iOS-Safari (funktioniert wenn Inspector schon auf iPhone läuft)
- AR-Quick-Look-Validator (20 Regeln — bekommt in v0.25.4 die Severity-Recal)
- Geometry-Stats
- Multi-Drop, Lineage, alles andere aus v0.21–v0.25

---

## 5. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| `qrcode-svg` CDN-Lazy-Load | **entfernt** | Keine externe Lib mehr nötig für v0.25.2 |
| Keine neuen Deps | — | Pivot reduziert Bundle-Surface |

---

## 6. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25 stabil released | ✓ Tag online seit 2026-05-04 |
| 2 | Spike-Auswertung dokumentiert | ✓ `inspector-spikes/spike-b/c.html` zeigen Konflikt empirisch |
| 3 | Plan-Chat-Pivot bestätigt | ✓ Duke 2026-05-04: "ja mach pivot - schade aber ist so" |

**3 von 3 grün.** Reihenfolge zu v0.25.1 (EN-Toggle) flexibel — beide Hotfixes sind technisch unabhängig. v0.25.2 vor v0.25.1 möglich.

---

## 7. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | ✓ erledigt via Spikes | — |
| **5.1 Code-Removal** | 0.2 Tag | QR-Button + Modal + qrcode-svg-CDN + i18n-Keys raus |
| **5.2 UI-Hilfe-Block einbauen** | 0.1 Tag | iOS-AR-Test-Anleitung statt QR-Button |
| **5.3 Verifikation Browser** | 0.05 Tag | Desktop-Inspector ohne QR-Spuren prüfen, iOS-Preview unverändert |
| **5.4 Headless-Pool-Regression** | 0.05 Tag | 7/7 PASS bleibt (Validator unverändert, nur UI-Cut) |
| **5.5 README + CHANGELOG** | 0.1 Tag | "QR-Code zurückgezogen"-Sektion mit Begründung |
| **5.6 ADR-PC5 dokumentieren** | inkludiert | In private CLAUDE-Inspector-private.md |
| **5.7 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.2, Tag, Push |

**Total: 0.5 Tag konzentrierter Pivot.**

---

## 8. Strategischer Hebel

v0.25.2 ist Pivot-Release — und genau **deshalb** strategisch stark:

1. **Trust-Anker:** "Wir haben es versucht, gemerkt dass es nicht zu unserer Architektur passt, und ehrlich zurückgezogen statt verkrüppelt zu lassen." Das ist Engineering-Reife, nicht Schwäche.
2. **Privacy-First-Positionierung:** Privacy-First wird zum **aktiven Verkaufsargument** statt zur passiven Eigenschaft. AR-Quick-Look-Validator liefert Mehrwert ohne dass Daten den Browser verlassen — Punkt.
3. **ADR-PC5-Disziplin:** Vierter ADR-PC, der vor v0.3 gesetzt wurde. Zeigt: Plan-Chat funktioniert auch für strategische Cuts, nicht nur für Bug-Diagnose.

---

## 9. Konkrete Pre-v0.25.2-Steps

Keine — v0.25.1 muss vorher fertig sein, dann Pivot-Sprint anschließen. Die Spike-Files in `inspector-spikes/` bleiben unverändert als Doku (oder werden später bei v0.3-Aufräumarbeiten archiviert).

---

## 10. Decision-Log-Template

```markdown
### ADR-26 QR-Code-Rollback — 2026-05-XX

**Kontext:** Bug 4 aus v0.25-Real-World-Test: QR-Code-Workflow für Drag&Drop-USDZs technisch unmöglich (keine öffentliche URL für iPhone-Reach erreichbar).

**Spike-Auswertung 2026-05-04:** Variante B (URL-Parameter) und Variante C (Direct AR + QR) beide erfolgreich getestet — gegen den Use-Case "lokale Drag&Drop-USDZ" sind beide unbrauchbar, da sie öffentlich gehostete USDZs voraussetzen.

**Entscheidung:** Feature ersatzlos zurückziehen. UI-Hilfe für AirDrop/iCloud/Mail-Workflow als Ersatz.

**Konsequenz:** Inspector-Bundle leichter (~50 Zeilen weniger, keine qrcode-svg-CDN), Architektur-Anker bestätigt. ADR-PC5 etabliert die Pivot-Disziplin.
```

---

## 11. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.25.md` (QR-Code ursprünglich eingeführt)
- Spike-Sandbox: `../../inspector-spikes/`
- Privater Persona-Anker: `../../CLAUDE-Inspector-private.md` (ADR-PC5 dokumentiert)

### Externe Specs

- [Apple AR Quick Look — Adding ar to web pages](https://developer.apple.com/documentation/arkit/previewing_a_model_with_ar_quick_look)
- [iCloud Drive auf iPhone öffnen](https://support.apple.com/de-de/guide/iphone/iph12f51d0a/ios)

---

**Ende v0.25.2-Roadmap.** Nach Pivot: Snapshot, Tag `v0.25.2`, Push. Plan-Chat schreibt dann `docs/ROADMAP-v0.25.3.md` (Texture-Format-Coverage) und `docs/ROADMAP-v0.25.4.md` (Severity-Recalibration mit Test-Pool von Duke).
