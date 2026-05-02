# Roadmap v0.22.1 — Polish & Polyglot

**Status:** Vorbereitungs-Dokument · 2026-05-01
**Story-Slot:** *"v0.22 wird mehrsprachig und reibungsfrei"*
**Ziel:** Bekannte Findings aus dem v0.22-Release abräumen — EN-Translation-Pfad öffnen, drei Validator-Schwächen beheben, Performance-Wahrnehmung beim Hashing verbessern.
**Aufwand:** 2–4 Tage konzentrierter Build.

> Punkt-Release zwischen v0.22 und v0.23. Detail-Briefings nach Bedarf.
> Master-Übersicht in `ROADMAP.md`.

---

## 1. Scope — was v0.22.1 inhaltlich bedeutet

Vier Themenblöcke aus den v0.22-Release-Notes als bekannt offen markiert:

### 1.1 EN-Translation-Pfad

v0.22 ist **monolingual Deutsch** ausgeliefert — Sprach-Toggle (DE/EN) wurde im Build-Sprint via W-2 deaktiviert (`CURRENT_LANG = 'de'` hartkodiert), die I18N-Map mit DE+EN-Strings liegt aber bereits inline vor. v0.22.1 reaktiviert den vollständigen EN-Pfad:

- **EN-Pfad in bestehender Inline-Object-Struktur** (`I18N = { key: { de, en } }`) ergänzen — der v0.22-CURRENT_LANG-Hartkode wird wieder dynamisch.
- Toggle reaktivieren (Position oben rechts in der Topbar — siehe v0.22-Build-Stand vor W-2-Fix).
- **Validator-Regeln** der AR-Quick-Look-Diagnose: die DE+EN-Texte pro Regel (`explanation` + `fixHint`) sind in v0.22 schon hinterlegt — Aufgabe ist Vollständigkeits-Audit, nicht Neu-Übersetzung.
- Default-Sprache: Browser-Locale (`navigator.language`) → Fallback DE.
- Sprach-Wahl in `localStorage` persistieren (`I18N_STORAGE_KEY = 'usdseal-inspector.lang'`).

**Architektur-Anker bleibt:** Single-File HTML, kein Build-Step, keine i18n-Library, kein Bundle-Split. Inline-Object-Pattern wird beibehalten — siehe ADR-7. JSZip + jsPDF (kommt in v0.23) sind die einzigen externen Deps.

### 1.2 W-3 — `TEXTURE_PATH_ABSOLUTE` Regex erweitern

Aktuell deckt die Regex nur Standard-Pfade ab. Erweiterung um:

- Windows-Style: `C:\` / `D:\` etc. (auch in Backslash-Schreibweise)
- macOS-Volumes: `/Volumes/...`
- Unix-Home: `~/`, `$HOME/`
- UNC-Pfade: `\\server\share\...`
- File-URIs: `file:///...`

**Test-Vektoren** als JSON-Datei in `tests/textures-absolute-paths.json` ablegen, damit Regex-Erweiterungen reproduzierbar prüfbar sind.

### 1.3 W-4 — `TEXTURE_NOT_IN_USDZ` Toleranz

Die Regel feuert aktuell zu strikt. Erweiterung auf:

- **Case-Insensitive-Matching:** `Texture.png` matcht `texture.png` (vor allem für Windows-erstellte USDZ).
- **Type-Toleranz:** `.jpg` / `.jpeg` / `.JPG` als gleichwertig.
- **Prefix-Toleranz:** `./textures/foo.png` matcht `textures/foo.png` (führender Punkt-Slash optional).

**Aber:** Toleranz nur in der **Existenz-Prüfung**, nicht im **Path-Resolution** für Texture-Anzeige. Wenn der USDA-Path und der ZIP-Eintrag tatsächlich verschiedene Cases haben, bleibt das ein Hint *"Pfad-Schreibweise abweichend — möglicherweise Plattform-Inkompatibilität"*.

### 1.4 W-5/W-6 — Parallel-Hashing + Loading-Indicator

Aktuell läuft das SHA-256-Hashing der ZIP-Members **sequenziell** im Main-Thread. Bei großen USDZ (50+ MB) friert die UI für Sekunden ein.

**Lösung:**
- **Parallel-Hashing** via `Web Workers` — pro ZIP-Member ein Worker, max. `navigator.hardwareConcurrency` parallel.
- **Loading-Indicator** während Verarbeitung: Progress-Bar mit Member-Count-Status (*"Hashing 12/47 files..."*).
- Cancel-Button (Stretch-Goal): laufende Worker terminieren, wenn Nutzer ein neues USDZ reinzieht oder Reset klickt.

**Risiko:** Worker brauchen die ZIP-Daten als `ArrayBuffer` — aktuell hält JSZip das im Main-Thread. Entweder kompletter ArrayBuffer pro Worker (Memory-Spike bei großen USDZ) oder transferable ArrayBuffer mit Ownership-Hand-off.

### 1.5 Finding-Sortier-Strategie verfeinern

v0.22 sortiert Findings primär nach Severity, sekundär nach ID-Alphabet. UX-Schwäche: thematisch verwandte Findings (z. B. zwei Texture-Errors) verteilen sich, weil ID-Alphabet nicht Category-bewusst ist. v0.22.1 fügt Category-Sortierung als Zwischen-Stufe hinzu — Severity primär, Category sekundär (Reihenfolge nach Kritikalität: structure → scale → textures → external → manifest → animation → performance), ID tertiär. Code-Aufwand minimal (Comparator-Erweiterung in `renderFindingsSection`). Siehe ADR-10.

---

## 2. Externe Quellen

| Komponente              | Status                       | Bemerkung                                                            |
|-------------------------|------------------------------|----------------------------------------------------------------------|
| JSZip                   | bereits eingebunden          | Reicht.                                                              |
| Web Workers API         | nativ, keine Lib             | Standard seit 2010 in allen Zielbrowsern.                            |
| `crypto.subtle.digest`  | nativ, keine Lib             | Funktioniert auch im Worker-Kontext.                                  |
| jsPDF                   | **nicht** in v0.22.1          | Kommt erst in v0.23.                                                  |

---

## 3. Architektur-Optionen

### Option A — Worker pro ZIP-Member (Empfehlung)

Ein Pool von Workern, jeder hashed einen Member.

**Pro:** Maximale Parallelität, einfach zu implementieren mit `navigator.hardwareConcurrency`.
**Contra:** Memory-Spike bei Many-Small-Files (Pool-Setup-Overhead).

### Option B — Ein Worker für alle Members (sequenziell im Worker)

UI bleibt responsive, aber Hashing selbst ist nicht schneller.

**Pro:** Kleinster Memory-Footprint.
**Contra:** Kein Performance-Gewinn auf Multi-Core, nur UI-Responsiveness.

### Empfehlung

**Option A.** Multi-Core ist heute Standard, der Performance-Gewinn lohnt den Pool-Overhead. Loading-Indicator macht den Gewinn auch sichtbar.

---

## 4. Vorbedingungen

| # | Vorbedingung                                                       | Status |
|---|--------------------------------------------------------------------|--------|
| 1 | Inspector v0.22 stabil released                                    | ✓      |
| 2 | EN-Translation-Strings gesammelt (UI + 20 Validator-Regeln)        | offen — siehe §7.1 |
| 3 | Test-USDZ mit absolut-pfadigen Texturen verfügbar                  | offen — siehe §7.2 |
| 4 | Test-USDZ mit großen Member-Files (50+ MB) für Worker-Test         | offen — siehe §7.3 |

**1 von 4 grün** — drei kleine Pre-Steps reichen zum Vollstart.

---

## 5. Phasen-Schätzung

| Phase                                | Dauer       | Was passiert                                                  |
|--------------------------------------|-------------|---------------------------------------------------------------|
| **5.1 EN-Translation-Pfad**          | 0.5–1 Tag   | EN-Strings in Inline-`I18N`-Map auf Vollständigkeit prüfen, CURRENT_LANG dynamisch, Toggle reaktivieren, localStorage-Persistence, navigator.language-Default. **Kein Bundle-Split** (siehe ADR-7). |
| **5.2 W-3 Regex-Erweiterung**        | 0.5 Tag     | Regex erweitern, Test-Vektoren, Validator-Anpassung. |
| **5.3 W-4 Toleranz-Logik**           | 0.5 Tag     | Case-/Type-/Prefix-Matching, Hint-Logik bei Abweichung. |
| **5.4 W-5/W-6 Parallel-Hashing**     | 1–1.5 Tage  | Worker-Pool, Progress-Tracking, Loading-Indicator. |
| **5.5 Finding-Sortier-Refinement**   | 0.25 Tag    | Comparator in `renderFindingsSection` erweitern um `catOrd`-Stufe (siehe ADR-10). Test gegen Pool-Files mit Multi-Severity / Multi-Category-Findings. |
| **5.6 Test-Durchlauf**               | 0.5 Tag     | DIEGOsat-Asset DE+EN, große USDZ für Performance-Validation, Finding-Sortierung visuell verifizieren. |
| **5.7 README + CHANGELOG-Update**    | 0.25 Tag    | Sprach-Hinweis raus, Bugfix-Liste rein, ADR-7/8/9/10 verlinken. |
| **5.8 Tag v0.22.1 + Release-Notes**  | 0.25 Tag    | GitHub-Release, Pages-Deploy verifizieren. |

**Total: 3.5–4.5 Tage Build-Zeit.** EN-Pfad sinkt um 0.5 Tage durch A1-Entscheidung (kein Bundle-Split-Refactor), Sortier-Refinement kostet 0.25 Tage zusätzlich.

---

## 6. Strategischer Hebel

v0.22.1 ist **kein Story-Release** — kein neuer Talk-Slide. Aber zwei stille Hebel:

1. **EN-Pfad ist Voraussetzung für AOUSD-Forum-Reichweite.** Internationaler Use-Case startet erst wirklich, wenn EN da ist. Ohne v0.22.1 ist das Forum-Update auf v0.22 nur eine deutsche Geschichte.
2. **Performance-Wahrnehmung als Conversion-Hebel.** Konferenzbesucher, die ein 80-MB-USDZ reinziehen und 10 Sekunden Freeze sehen, schließen den Tab. Loading-Indicator + Parallel-Hashing macht den Unterschied zwischen *"krass, das geht im Browser"* und *"langsam, geh ich woanders hin"*.

---

## 7. Pre-v0.22.1-Steps

### 7.1 EN-Translation-Strings sammeln (1–2 Stunden)

Alle UI-Texte aus `index.html` extrahieren und in `messages.de.js` ablegen — dann `messages.en.js` als Übersetzungs-Vorlage. Validator-Regeln separat, weil Volumen größer (20 Regeln × Klartext-Erklärung × Sprache).

### 7.2 Test-USDZ mit Absolut-Pfaden bauen (30 Minuten)

Manuell ein Test-USDZ konstruieren, das in der USDA-Datei verschiedene Pfad-Stile referenziert (Windows, macOS, UNIX-Home, UNC, file://). Für W-3-Validation.

### 7.3 Performance-Test-USDZ besorgen (15 Minuten)

Großes USDZ-Beispiel (50+ MB, 30+ Members) für Worker-Pool-Performance-Test. Kann ein DIEGOsat-Variant mit allen Texturen in voller Auflösung sein.

---

## 8. Decision-Log-Template

```markdown
### ADR-7 i18n-Strategie: Inline-Object-Pattern beibehalten — 2026-05-02

**Kontext:** v0.22.1 reaktiviert den DE/EN-Toggle. Erwogene Optionen: Inline-Object (A1) oder Bundle-Split (A2 — `messages.de.js` / `messages.en.js`).

**Entscheidung:** A1 — Inline-Object `I18N = { key: { de, en } }` wird beibehalten und um die noch fehlenden EN-Strings ergänzt. Toggle wird reaktiviert. Kein i18next / kein Polyglot / kein Bundle-Split.

**Begründung:** Single-File-Architektur-Anker (siehe Master-ROADMAP) bleibt intakt. Standalone-Download (`file://`) und iframe-Embed funktionieren weiter ohne CORS-Probleme. String-Volumen (~30 KB für 130 Strings, 2 Sprachen) ist im Inline-Pattern bezahlbar — Inspector wiegt eh ~80 KB.

**Konsequenz:** Wenn jemals eine 4./5. Sprache dazukommt und das Volumen unhandlich wird, wird ADR-7 in v0.X+ neu evaluiert. Bis dahin: Inline.

### ADR-8 Worker-Pool-Strategie: pro ZIP-Member statt Single-Worker — 2026-05-02

**Kontext:** W-5/W-6 Parallel-Hashing.
**Entscheidung:** Worker-Pool mit `navigator.hardwareConcurrency`-Limit, gecappt bei 8. Cap-Begründung: Diminishing Returns ab ~8 Cores bei USDZ-typischen Dateigrößen (74 B–2 KB pro Member); zudem vermeidet der Cap Memory-Spikes bei USDZs mit vielen kleinen Members.
**Konsequenz:** Performance-Gewinn auf Multi-Core, Memory-Spike akzeptabel bei realistischen USDZ-Größen. Auf Maschinen >8 Cores läuft der Pool unter `hardwareConcurrency` — bewusster Trade-off.

### ADR-9 W-4 Toleranz: Existenz-Prüfung tolerant, Path-Resolution strikt — <Datum>

**Kontext:** Case-/Type-/Prefix-Toleranz vs. Plattform-Kompatibilitäts-Hint.
**Entscheidung:** Toleranz in der Existenz-Prüfung, Hint bei tatsächlichem Pfad-Mismatch.
**Konsequenz:** False-Negatives reduziert, aber Plattform-Probleme weiterhin sichtbar.

### ADR-10 Finding-Sortier-Strategie: Severity → Category → ID — 2026-05-02

**Kontext:** v0.22 sortiert Findings primär nach Severity, sekundär ID-alphabetisch. Bei vielen gleichzeitigen Findings (8–15 bei schlechtem USDZ) wirkte das verteilt — verwandte Themen standen nicht nebeneinander.

**Erwogene Optionen:**
- B1 Severity-First (Status quo v0.22)
- B2 Category-First (versteckt rote Findings hinter unkritischen Categories)
- B3 Hybrid Severity-primär, Category-sekundär
- B4 Array-Order (Implementation-Reihenfolge — UX-fragil)

**Entscheidung:** B3. Comparator wird drei-stufig:
1. Severity (`error` → `warn` → `info`)
2. Category (`structure` → `scale` → `textures` → `external` → `manifest` → `animation` → `performance`)
3. ID alphabetisch

**Begründung:** Severity bleibt leitend (User sieht Hard-Fails zuerst), Categories gruppieren verwandte Themen innerhalb jeder Severity. Category-Reihenfolge spiegelt ungefähr Kritikalität wider.

**Konsequenz:** Wenn neue Categories in v0.23+ dazukommen, werden sie via `?? 99`-Fallback hintenan sortiert. Alte Categories bleiben deterministisch. Kein Refactor bei Erweiterung.
```

---

## 9. Quellen / Referenz-Links

### Interne Dokumente
- Master-Roadmap: `ROADMAP.md`
- v0.21-Briefing (historisch): `ROADMAP-v0.21.md`

### Externe Specs
- [Web Workers API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [SubtleCrypto.digest() (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest)
- [Transferable Objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)

### Inspector-Repo
- [github.com/KopfKinoK3/usdseal-inspector](https://github.com/KopfKinoK3/usdseal-inspector)
- [Live: kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/)

---

**Ende v0.22.1-Roadmap.** Nach Build: ADR-Einträge in CHANGELOG einhängen, Git-Tag setzen. Dann Briefing für v0.23 (PDF-Audit-Report) öffnen — das ist der nächste Story-Release.
