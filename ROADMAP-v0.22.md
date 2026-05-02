# Roadmap v0.22 — AR Quick Look Validator

**Status:** Vorbereitungs-Dokument · 2026-05-01
**Story-Slot:** *"Warum streikt AR Quick Look?"* — **USP**
**Ziel:** Inspector wird zur **Diagnose-Ampel** für AR-Quick-Look-Kompatibilität. USDZ rein → grün/orange/rot mit Klartext-Erklärungen pro Fail. Keine Black-Box-Fehlermeldung mehr.
**Aufwand:** 3–5 Tage konzentrierter Build.

> Detail-Briefing der v0.21-Sequenz. Master-Übersicht in `ROADMAP.md`. Vorgänger: `ROADMAP-v0.21.md`. Nachfolger-Patch v0.22.2 (Re-Import-Detection) — siehe `ROADMAP-v0.22.2.md`.

---

## 1. Scope — was v0.22 inhaltlich bedeutet

Inspector v0.21 zeigt **Lineage, Provenance, Compat**. v0.22 fügt eine eigene Diagnose-Schicht hinzu: ein deklaratives Regel-Set, das ein USDZ gegen die AR-Quick-Look-Anforderungen prüft und pro Fail eine **menschenlesbare Klartext-Erklärung** liefert.

Warum ist das die USP-Story? Apple liefert keine sinnvollen Fehlermeldungen, wenn AR Quick Look ein USDZ verweigert. Wer ein 3D-Asset zum Kunden schickt und am iPhone scheitert, hat keinen Diagnose-Pfad. Der Inspector schließt diese Lücke — und zwar ohne Apple-Tools, ohne Mac, ohne Reality Converter.

### 1.1 AR-QL-Ampel

Neue Sektion **oben im Dashboard**, direkt unter dem State-Banner. Drei Zustände:

- **Grün** — *"AR Quick Look kompatibel."* Asset erfüllt alle harten Anforderungen.
- **Orange** — *"Funktioniert mit Caveats."* Soft-Warnings (z. B. große Texturen, fehlende `metersPerUnit`-Empfehlung).
- **Rot** — *"AR Quick Look bricht."* Mindestens ein Hard-Fail (z. B. fehlender `defaultPrim`, falsches Texture-Format).

Plus: pro Finding eine Card mit ID, Severity, Klartext-Begründung, optional **Fix-Hinweis** (*"In Reality Converter neu öffnen und exportieren"*).

### 1.2 Validator-Engine

Regelbasiert. Jede Regel ist ein Objekt:

```js
{
  id: 'AR_QL_DEFAULT_PRIM_MISSING',
  severity: 'error',                    // error | warn | info
  category: 'structure',                // structure | textures | scale | animation | manifest
  check: (ctx) => boolean,              // ctx = { manifest, members, usdMeta, textures }
  explanation: 'AR Quick Look benötigt einen defaultPrim im Root-Layer.',
  fixHint: 'In USDA-Header: defaultPrim = "<dein_root_prim>" setzen.'
}
```

Engine läuft jede Regel gegen den Inspector-Context, sammelt Findings, wertet sie zur Ampel aus.

### 1.3 Regel-Katalog v0.22 (Erstauflage)

Schwerpunkt auf **harten Brechern** und **dokumentierten Apple-Limits**. Kein Anspruch auf Vollständigkeit — Erweiterung in v0.23+.

| Kategorie | Regel-ID (Beispiel) | Severity |
|---|---|---|
| Struktur | DEFAULT_PRIM_MISSING, ROOT_LAYER_NOT_FIRST, NESTED_USDZ | error |
| Struktur | UP_AXIS_NOT_Y, METERS_PER_UNIT_MISSING | warn |
| Texturen | TEXTURE_FORMAT_UNSUPPORTED (EXR/HDR/TIFF) | error |
| Texturen | TEXTURE_TOO_LARGE (>4096px Kante) | warn |
| Texturen | TEXTURE_NPOT (non-power-of-two) | info |
| Skalierung | NO_PHYSICAL_SCALE_HINT | warn |
| Manifest | NO_MANIFEST_PRESENT (kein USDseal) | info — *Inspector ist Inspector, nicht USDseal-Pflicht* |
| Manifest | MANIFEST_HASH_MISMATCH | warn — bestehende v0.2-Logik wiederverwendet |
| Animation | TIMECODE_RANGE_INVALID | warn |
| Sicherheit | EXTERNAL_REFERENCES (asset:// außerhalb usdz) | error |

**Quelle der Wahrheit für Anforderungen:** Apple Developer Docs für AR Quick Look + Reality Composer Pro Best Practices, gespiegelt in einer kuratierten internen Liste (siehe §7.1).

### 1.4 Klartext-Sprache

Deutsch + Englisch beide hinterlegt, Sprache automatisch via `navigator.language`. Toggle für manuelle Wahl. Klartext ist B2B-tauglich, keine Tech-Jargon-Erklärungen ohne Übersetzung.

---

## 2. Externe Quellen

| Komponente              | Status                      | Bemerkung                                                  |
|-------------------------|-----------------------------|------------------------------------------------------------|
| JSZip                   | bereits eingebunden         | Reicht — Validator arbeitet auf bestehendem Inspector-Context. |
| `<model-viewer>`        | **optional**, später        | Live-Preview erst v0.25. v0.22 nur Diagnose, kein Render. |
| Apple AR Quick Look Docs | externe Referenz           | Anforderungen werden in interne Regel-Liste übersetzt — kein Live-Fetch. |
| Validator-Lib           | **keine**                   | Pure JS, kein JSON-Schema-Validator, kein AJV.            |
| i18n-Lib                | **keine**                   | Deutsch + Englisch als Plain-JS-Object, kein Framework.   |

---

## 3. Architektur-Optionen

### Option A — Regel-Array + Engine-Loop (Empfehlung)

Alle Regeln als Array von Objekten in einer separaten JS-Datei oder im Hauptscript. Engine ist eine kleine Loop-Funktion (`runValidator(ctx) → findings[]`). Renderer übersetzt findings in DOM.

**Pro:** Erweiterung = neuer Eintrag im Array. Tests einfach (Regel isolierbar). Klarer mentaler Overhead.
**Contra:** Bei sehr komplexen Regeln (z. B. Layer-Stack-Auswertung) wird die check-Funktion lang. Aber für v0.22-Scope reicht's.

### Option B — Klassen-basierte Validator-Hierarchie

OOP-Architektur mit Vererbung. Overkill für JS-Frontend dieser Größe.

### Option C — JSON-Schema mit Draft-2020-12

Würde nur Manifest-Felder prüfen, nicht USD-Strukturen oder Texturen. Zu schmal.

### Empfehlung

**Option A.** Konsistent mit v0.21-Pattern (`renderForSpecVersion` ist auch flach + funktional).

---

## 4. Vorbedingungen — was vor v0.22-Start geklärt sein muss

| # | Vorbedingung                                                             | Status |
|---|--------------------------------------------------------------------------|--------|
| 1 | Inspector v0.21 fertiggebaut (Lineage + Provenance + Compat)             | ✓ — 2026-05-01 |
| 2 | AR-Quick-Look-Anforderungen kuratiert in Form einer internen Regel-Liste | ✓ — `AR-QL-RULES.md` (21 Regeln, DE+EN) |
| 3 | Test-Asset-Pool: ein bekannt-funktionierendes + ein bekannt-brechendes USDZ | ✓ — `../usdz/test-pool/` (1 grün + 3 rot + README) |
| 4 | Severity-Mapping entschieden: 3-stufig (error/warn/info) vs. feiner       | ✓ — 3-stufig (siehe ADR-2-Template) |
| 5 | Klartext-Sprache entschieden: nur DE / nur EN / beide                     | ✓ — DE + EN beide (entschieden 2026-05-01) |
| 6 | i18n-Architektur entschieden: Plain-Object vs. JSON-Files                 | ✓ — Plain-Object inline (kein Build-Step) |

**6 von 6 grün — startklar für Build-Chat.**

---

## 5. Realistische Phasen-Schätzung

| Phase                                       | Dauer       | Was passiert                                                       |
|---------------------------------------------|-------------|--------------------------------------------------------------------|
| **5.1 Regel-Array + Engine-Loop**           | 0.5–1 Tag   | `runValidator(ctx) → findings[]` mit erstem Regel-Set (~10 Regeln). |
| **5.2 Ampel-Sektion UI**                    | 0.5–1 Tag   | Banner mit grün/orange/rot, Counter pro Severity. Direkt unter State-Banner. |
| **5.3 Findings-Liste**                      | 0.5–1 Tag   | Card pro Finding: Severity-Pille, ID, Klartext, optional Fix-Hinweis, Kategorie-Tag. |
| **5.4 Klartext-i18n DE/EN**                 | 0.5 Tag     | Plain-Object mit DE/EN-Strings, Toggle in Topbar, Auto-Detect via navigator.language. |
| **5.5 Regel-Katalog ausbauen**              | 0.5–1 Tag   | Vom Erst-Set (~10) auf Solid-Set (~20–25 Regeln). Schwerpunkt: Texturen, externals. |
| **5.6 Test gegen Asset-Pool**               | 0.5 Tag     | Bekannt-grünes + bekannt-rotes USDZ durchspielen. Edge-Cases dokumentieren. |
| **5.7 README + CHANGELOG + COMPATIBILITY**  | 0.5 Tag     | v0.22-Eintrag, Regel-Katalog als Anhang, Cross-Link auf Apple-Docs. |
| **5.8 Lokaler Build-Abschluss**             | 0.25 Tag    | Snapshot-HTML, Optik-Check, ggf. Screenshot für Konferenz-Pack. |

**Total: 3.5–5 Tage Build-Zeit.** Schmaler als v0.21, weil keine neue Datenstruktur.

---

## 6. Strategischer Hebel

v0.22 ist **die USP-Story** der Versions-Sequenz. Drei Hebel:

1. **Konferenz-Demo (Klimax-Material).** USDZ live reinziehen, rot, Klartext erklärt warum, dann gefixtes USDZ → grün. *Vorher–Nachher* in 90 Sekunden. Das ist der Slide, den dein Publikum sich merkt.
2. **AOUSD-Forum-Update.** *"Inspector v0.22 now diagnoses AR Quick Look issues with plain-language explanations — no Mac, no Reality Converter."* Trifft direkt das Pain-Point von Outside-Apple-Devs.
3. **Lead-Magnet für viSales.** Inspector-Page kann zur Beratungs-Pipeline routen: *"Du brauchst AR Quick Look in Production? Lass uns sprechen."*

---

## 7. Konkrete Pre-v0.22-Steps (jetzt machbar)

### 7.1 AR-Quick-Look-Anforderungen kuratieren (1–2 Stunden)

Quellen:
- Apple Developer: *"Creating USDZ Files for AR Quick Look"*
- Apple Developer: *"AR Quick Look — Best Practices"*
- Reality Composer Pro Documentation
- Externes: PXR USDZ-Spec-Dokumente bei Pixar/AOUSD

Output: interne Tabelle mit ~25 Anforderungen, jede gemappt auf Severity + Klartext (DE/EN) + Fix-Hinweis. Wird Anhang von `ROADMAP-v0.22.md` oder eigene Datei `AR-QL-RULES.md`.

### 7.2 Test-Asset-Pool zusammenstellen (1 Stunde)

- **bekannt-grün:** ein USDZ aus Apple-Sample-Library (z. B. `toy_drummer.usdz`) oder ein eigenes sauberes Asset.
- **bekannt-rot:** absichtlich gebrochen — `defaultPrim` entfernen, EXR-Texture einfügen, externe Reference setzen. Drei Versionen, jeweils mit anderem Fail-Pattern.
- DIEGOsat-Bestand: muss **grün** durchlaufen, sonst hat v0.21 ein Lineage-Asset gebaut, das AR-QL nicht mag — Bug-Indikator.

### 7.3 Severity-Mapping & Klartext-Style-Guide (30 Minuten)

Klartext-Regeln:
- **Error**: *"AR Quick Look bricht — Datei wird nicht angezeigt."*
- **Warn**: *"Funktioniert, aber Apple empfiehlt anders."*
- **Info**: *"Hinweis ohne Funktions-Auswirkung."*

Ton: B2B-sachlich, kein Tech-Jargon ohne Übersetzung. Beispiel:

> ❌ Schlecht: *"Required defaultPrim attribute not found in root layer USDA composition."*
> ✓ Gut: *"AR Quick Look braucht einen `defaultPrim`-Eintrag im Haupt-USD-File. Ohne diesen weiß AR Quick Look nicht, welches 3D-Objekt es anzeigen soll."*

---

## 8. Decision-Log-Template (für v0.22-Entscheidungen)

```markdown
### ADR-1 Validator-Architektur: Regel-Array + Engine-Loop — <Datum>

**Kontext:** Validator braucht Erweiterbarkeit pro Regel.
**Optionen:** Regel-Array + Engine / OOP-Hierarchie / JSON-Schema.
**Entscheidung:** Regel-Array, jede Regel = `{id, severity, category, check, explanation, fixHint}`.
**Konsequenz:** Erweiterung = neuer Array-Eintrag. Tests pro Regel isolierbar.

### ADR-2 Severity-Mapping 3-stufig (error/warn/info) — <Datum>

**Kontext:** Findings brauchen klare Priorität.
**Entscheidung:** Drei Severities → drei Ampel-Farben (rot/orange/grün).
**Konsequenz:** Konsistent mit anderen Inspector-Bannern. Kein Stufungs-Streit.

### ADR-3 Klartext zweisprachig DE/EN — <Datum>

**Kontext:** B2B-Kunden international, viSales-Heimat ist DE.
**Entscheidung:** Beide Sprachen inline, Toggle in Topbar, Default via navigator.language.
**Konsequenz:** +50 % Pflege pro Regel-String, aber klarer Wert für Demo + Reichweite.

### ADR-4 i18n als Plain-JS-Object inline — <Datum>

**Kontext:** Externe i18n-Lib oder eigene JSON-Files würden Build-Step erzwingen.
**Entscheidung:** Plain-Object inline im HTML, kein Build-Step.
**Konsequenz:** Inspector bleibt Single-File, keine Cloudflare-CDN-Abhängigkeit für i18n.

### ADR-5 Live-Preview NICHT in v0.22 — <Datum>

**Kontext:** `<model-viewer>` würde AR-QL-Diagnose visuell unterstützen, aber Bundle blowt + COOP/COEP-Probleme.
**Entscheidung:** Live-Preview verschoben auf v0.25 (separater Story-Slot *"Was ist das Modell?"*).
**Konsequenz:** v0.22 bleibt schlank, USP-Fokus auf Diagnose, nicht auf Render.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente
- Master-Roadmap: `ROADMAP.md`
- Vorgänger-Detail: `ROADMAP-v0.21.md`
- Nachfolger-Patch: `ROADMAP-v0.22.2.md` (Re-Import-Detection)
- Compat-Matrix: `COMPATIBILITY.md`
- Test-Assets: `../usdz/DIEGOsat_master.usdz`, `../usdz/DIEGOsat_master_marketing.usdz`
- Anhang (geplant): `AR-QL-RULES.md` mit kuratierter Anforderungs-Liste

### Externe Specs & Dokumente
- [Apple Developer — AR Quick Look](https://developer.apple.com/augmented-reality/quick-look/)
- [Apple Developer — Creating USDZ Files for AR Quick Look](https://developer.apple.com/documentation/arkit/previewing_a_model_with_ar_quick_look)
- [Reality Composer Pro](https://developer.apple.com/augmented-reality/tools/)
- [OpenUSD Specification](https://openusd.org/release/index.html)
- [USDZ Asset Format](https://openusd.org/release/spec_usdz.html)

### Inspector-Repo
- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)
- [Live: kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/)

---

**Ende v0.22-Roadmap.** Nach Build: ADR-Einträge in CHANGELOG einhängen, Git-Tag setzen, Release-Notes aus CHANGELOG generieren. Dann Briefing für v0.23 (Audit-Report PDF) öffnen.
