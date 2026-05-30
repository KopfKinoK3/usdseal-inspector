# Roadmap v0.28.0.4 — PDF Tester-Signatur (Audit-Sektion)

**Status:** Vorbereitungs-Dokument · 2026-05-25
**Story-Slot:** *"Der PDF-Audit-Report bekommt eine menschliche Prüfer-Signatur. Wer hat wann mit welcher Notiz geprüft — direkt im Report dokumentiert."*
**Ziel:** Klappbarer Tester-Block neben dem PDF-Report-Button mit vier Eingabefeldern (Name, Firma, Rolle, Notiz). Voll-Audit-Sektion am Anfang des PDF + Footer-Zeile mit Selbstangabe-Hinweis auf jeder Seite. localStorage-Merken-Checkbox. Standard und Advanced beide.
**Aufwand:** S (0.5–0.8 Tag)

> Patch-Sprint nach v0.28.0.3. Antwort auf Duke-Frage 2026-05-25 *"wie bekommen wir ein eingabefeld ins html für den namen des testers"*. Erweitert von Mini-Name-Feld zu vollem Audit-Look (Duke-Entscheidung: "full audit"). Macht den PDF-Report zur offiziellen Compliance-Dokumentation und liefert starke B2B-Audit-Story.

---

## 1. Befund

Der PDF-Audit-Report ist seit v0.23 vollständig (Geometrie + Texturen + AR-Diagnose + USDseal-Trust + Verify-UI). Was fehlt: **menschliche Prüfer-Signatur**. Wer hat den Report wann erstellt, mit welcher Notiz, in welchem Kontext?

**B2B-Use-Case heute:** Marketing-Verantwortlicher empfängt USDZ vom Lieferanten, prüft mit Inspector, lädt PDF runter, mailt an Compliance/Vertrieb. Im PDF steht aber nur *"Inspector v0.28.0.3 — 2026-05-25 14:30"* — der Empfänger weiß nicht wer geprüft hat.

**Lücke:**
- Kein Audit-Trail im PDF (wer-wann-warum)
- Keine Compliance-Dokumentation möglich
- Vertriebs-/Audit-Story bleibt unsichtbar ("wir liefern geprüfte Reports" hat keinen Beleg)

**Lösung:** Tester-Signatur via klappbarem Eingabe-Block neben dem PDF-Report-Button. Vier Felder (Name, Firma, Rolle, Notiz), localStorage-Merken-Checkbox, Voll-Audit-Sektion am PDF-Anfang plus Footer-Zeile auf jeder Seite. Klar als **Selbstangabe** gekennzeichnet (rechtlich sauber — wir können den Namen nicht verifizieren).

**Strategischer Hebel:** Der PDF-Report wird zur **offiziellen Compliance-Dokumentation**. Verkaufsargument: *"Wir liefern Audit-Reports mit Prüfer-Signatur — bereit für Compliance- und Vertriebs-Workflows."* Passt zur USDseal-Trust-Familie ("Don't trust, verify" aus v0.27): Signatur der Datei + Signatur des Prüfers = zwei Vertrauensschichten in einem Report.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Aktuelle PDF-Generierung lokalisieren
grep -n "jsPDF\|generatePdf\|PDF-Report" src/inspector.html | head -10
grep -n "addPage\|setFontSize\|footerText" src/inspector.html | head -10

# B) Aktuelle Header-/Footer-Struktur des PDF (v0.26.x)
# - Wie wird Versions-Zeile gerendert? (Phase 5.0 v0.26.0-Vorgänger als Vorlage)
# - Wo wäre der natürliche Platz für eine neue Tester-Sektion am Anfang?
# - Wo wird der Footer pro Seite gerendert? (für Tester-Selbstangabe-Zeile)

# C) UI-Position des PDF-Report-Buttons
grep -n "pdf-report\|generatePdfButton" src/inspector.html | head -5
# - Welche Container/Klasse umgibt den Button?
# - Wo kann das klappbare Element sauber rechts daneben sitzen?

# D) localStorage-Pattern aus v0.22.2 (Re-Import-Cache) als Vorlage
grep -n "localStorage" src/inspector.html | head -10
# - Welche Keys gibt es schon? Tester-Keys müssen kollisionsfrei sein
# - Welches JSON-Schema verwenden andere localStorage-Items?

# E) i18n-Pattern aktuell
grep -n "data-i18n\|t('" src/inspector.html | head -5
# - Wie werden neue Keys hinzugefügt? Welche Datei?
```

→ Lokalisiert:
1. PDF-Header-Struktur ab v0.26.0 — Tester-Sektion kommt zwischen Title-Block und AR-Diagnose-Sektion (vor allen v0.26-Sektionen)
2. Footer-Render-Stelle pro Seite — Tester-Selbstangabe-Zeile in jeden Footer
3. UI-Container für PDF-Report-Button — klappbarer Block sitzt rechts daneben, kollabiert Default
4. localStorage-Pattern + Key-Namespace
5. i18n-Datei für ~10 neue Keys DE+EN

**Konsistenz-Check:**
- Tester-Block in `<!-- ADVANCED-ONLY -->`- oder Standard-Bereich? Antwort: **STANDARD-Bereich** (beide Distributions kriegen das Feature, Build-Step generiert beide korrekt)
- localStorage-Keys mit Prefix `usdseal_inspector_tester_*` damit klar woher
- PDF-Sektion-Position: am Anfang nach Title, vor AR-Diagnose — Begründung: Audit-Signatur muss prominent sein, aber nicht den Content verdrängen

---

## 3. Scope

### 3.1 UI — Klappbarer Tester-Block neben PDF-Report-Button

**Layout im UI:**

```
┌─────────────────────────────────────────────────────────────────┐
│ [PDF-Report ↓]  ▾ Geprüft von                                  │
└─────────────────────────────────────────────────────────────────┘

Beim Klick auf ▾:

┌─────────────────────────────────────────────────────────────────┐
│ [PDF-Report ↓]  ▴ Geprüft von                                  │
│                                                                 │
│   Name:       [_____________________________]                  │
│   Firma:      [_____________________________]                  │
│   Rolle:      [_____________________________]                  │
│   Notiz:      [_____________________________]                  │
│               [_____________________________]                  │
│               [_____________________________]                  │
│                                                                 │
│   ☐ Angaben merken (lokal in diesem Browser)                  │
│                                                                 │
│   ⓘ Datum wird automatisch beim PDF-Export gesetzt.            │
└─────────────────────────────────────────────────────────────────┘
```

**Komponenten:**

1. **Trigger-Element** neben PDF-Report-Button — kleines `▾ Geprüft von` (oder Icon + Label)
2. **Klappbarer Container** öffnet sich darunter (CSS `display: none/block`, keine Animation in v0.28.0.4 nötig)
3. **4 Eingabefelder:**
   - `Name` (`<input type="text">`, ~200 Zeichen)
   - `Firma` (`<input type="text">`, ~200 Zeichen)
   - `Rolle` (`<input type="text">`, ~100 Zeichen — z. B. "Vertrieb", "Compliance", "Audit", "Marketing")
   - `Notiz` (**`<textarea>`** mit `rows="3"`, ~500 Zeichen — Audit-Kontext, mehrzeilig)
4. **Merken-Checkbox:** `<input type="checkbox">` mit Label *"Angaben merken (lokal in diesem Browser)"*
5. **Datum-Hinweis:** statischer Text *"Datum wird automatisch beim PDF-Export gesetzt."*

**Verhalten:**

- **Default:** Block kollabiert. Beim ersten Page-Load wird der Trigger sichtbar.
- **Wenn localStorage-Werte vorhanden:** beim Page-Load werden Felder automatisch befüllt, Block bleibt aber kollabiert (User sieht ihn nur wenn er klickt)
- **Beim Klick auf PDF-Report-Button:** Werte werden ausgelesen, in PDF eingesetzt
- **Wenn Merken-Checkbox aktiv:** beim PDF-Generieren werden Werte in localStorage geschrieben
- **Wenn Merken-Checkbox nicht aktiv:** Werte werden NICHT gespeichert, müssen jedes Mal neu eingegeben werden

### 3.2 localStorage-Schema

**Key-Namespace:** `usdseal_inspector_tester_*`

```javascript
{
  "usdseal_inspector_tester_remember": true,  // Boolean-Flag
  "usdseal_inspector_tester_data": {
    "name": "Max Müller",
    "company": "viSales GmbH",
    "role": "Vertrieb",
    "note": "Eingangsprüfung Frankfurt-Asset für Showroom Q3"
  }
}
```

- Wenn `remember = false`: `_data`-Key wird beim PDF-Export NICHT geschrieben
- Wenn `remember = true`: `_data`-Key wird bei jedem PDF-Export überschrieben (aktuelle Werte)
- Bei Cache-Clear-Button im UI: Tester-Keys werden mit-gelöscht (analog Re-Import-Cache aus v0.22.2)

### 3.3 PDF — Voll-Audit-Sektion am Anfang

**Position im PDF:** Nach Title-Block (Logo + "USDseal Inspector Report"), vor AR-Diagnose-Sektion. **Eigene Sektion mit oranger Akzentleiste** (analog v0.26.0-Geometrie-Sektion-Pattern).

**Sektion-Inhalt:**

```
═══════════════════════════════════════════════════════════════
PRÜFER-SIGNATUR (Selbstangabe)
───────────────────────────────────────────────────────────────

Name:    Max Müller
Firma:   viSales GmbH
Rolle:   Vertrieb
Datum:   25. Mai 2026, 14:30 Uhr

Notiz:   Eingangsprüfung Frankfurt-Asset für Showroom Q3.
         Datei vom Lieferanten Müller-Möbel erhalten am 23.05.
         Prüfung auf AR-Tauglichkeit + Material-Vollständigkeit.

ⓘ Hinweis: Prüfer-Angaben sind Selbstangaben des User-
   Eingabe-Feldes im Browser und nicht durch viSales verifiziert.
═══════════════════════════════════════════════════════════════
```

**Stil:**
- Orange Akzentleiste links (wie v0.26.0)
- Labels (`Name:`, `Firma:`, `Rolle:`, `Datum:`, `Notiz:`) in fett, Werte daneben/darunter
- Notiz mit Word-Wrap (mehrzeilig sauber gerendert via jsPDF `splitTextToSize`)
- Datum-Format: deutsch *"25. Mai 2026, 14:30 Uhr"* / englisch *"May 25, 2026, 2:30 PM"*
- Hinweis-Zeile am Ende in kleinerer Schrift (dezent, aber sichtbar — Rechtssicherheit)

**Verhalten bei leeren Feldern:**

- **Alle Felder leer:** Sektion wird KOMPLETT WEGGELASSEN (kein leerer Block im PDF, der unprofessionell wirkt)
- **Nur einige Felder leer:** Sektion erscheint, leere Felder werden ausgelassen (kein `Name: ` ohne Wert)
- **Datum erscheint IMMER** wenn Sektion gerendert wird (auch wenn alle anderen Felder leer wären — aber dann erscheint Sektion ja nicht)

### 3.4 PDF — Footer-Zeile auf jeder Seite

**Wenn Tester-Name vorhanden:** Footer enthält zusätzliche Zeile *"Geprüft von (Selbstangabe): Max Müller, viSales GmbH"* — kompakter als die Anfangs-Sektion, immer sichtbar.

**Wenn Tester-Name leer:** Footer bleibt wie bisher (nur Inspector-Version + Datum).

**Format:**

```
Geprüft von (Selbstangabe): Max Müller, viSales GmbH · Inspector v0.28.0.4 · 25.05.2026 14:30
```

Kleinschrift, dezent, auf jeder Seite identisch.

### 3.5 i18n DE+EN

Neue Keys (ca. 10):

| Key | DE | EN |
|---|---|---|
| `tester_toggle` | "Geprüft von" | "Reviewed by" |
| `tester_name_label` | "Name" | "Name" |
| `tester_company_label` | "Firma" | "Company" |
| `tester_role_label` | "Rolle" | "Role" |
| `tester_note_label` | "Notiz" | "Note" |
| `tester_remember_label` | "Angaben merken (lokal in diesem Browser)" | "Remember entries (locally in this browser)" |
| `tester_date_hint` | "Datum wird automatisch beim PDF-Export gesetzt." | "Date is set automatically when exporting the PDF." |
| `pdf_tester_section_title` | "Prüfer-Signatur (Selbstangabe)" | "Reviewer Signature (self-declared)" |
| `pdf_tester_date_label` | "Datum" | "Date" |
| `pdf_tester_disclaimer` | "Prüfer-Angaben sind Selbstangaben des User-Eingabefelds im Browser und nicht durch viSales verifiziert." | "Reviewer entries are self-declared via the browser input field and not verified by viSales." |
| `pdf_tester_footer_prefix` | "Geprüft von (Selbstangabe):" | "Reviewed by (self-declared):" |

### 3.6 Distribution

- **Standard + Advanced beide.** Tester-Block ist im STANDARD-Marker-Bereich (kein ADVANCED-ONLY-Block), Build-Step erzeugt beide Files korrekt.
- INSPECTOR_VERSION auf `0.28.0.4` (ADR-38 hält automatisch).
- Beide Files kriegen gemeinsamen Tag `v0.28.0.4`.

### 3.7 Was NICHT in v0.28.0.4

- **Keine Pflichtfelder** — alle 4 Felder sind optional, PDF wird auch ohne Tester-Daten generiert
- **Keine Validierung** (kein E-Mail-Check, kein "Vor- und Nachname"-Check) — Tester ist frei in Form
- **Keine Auto-Komplettierung** aus Vorgänger-Reports (nur localStorage-Merken)
- **Keine Multi-Tester-Unterstützung** (nur ein Tester pro Report) — wenn später Bedarf für *"erstellt von A, gegengeprüft von B"* eigener Sprint
- **Keine kryptographische Signatur** (Tester unterschreibt nicht digital) — das wäre eigene Geschichte mit Key-Management
- **Keine Tester-Historie** (keine Auflistung aller bisherigen Reports im Browser)
- **Keine UI-Pflicht-Erinnerung** *"willst du wirklich ohne Tester-Name exportieren?"* — Wir bevormunden nicht

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| jsPDF 3.0.3 | unverändert | bestehende Dependency, keine neue |
| localStorage | unverändert | wie v0.22.2 Re-Import-Cache-Pattern |
| CSS für klappbaren Block | minimal nachzuziehen | `display: none/block` Toggle reicht |

Keine neuen Deps. Architektur-Anker hält. ADR-PC5 unangetastet.

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.28.0.3 released | ✓ (2026-05-25) |
| 2 | PDF-Generierung funktional über alle Sektionen | ✓ (seit v0.26.2 stabil) |
| 3 | Build-Step Variante Y | ✓ (seit v0.28.0) |
| 4 | localStorage-Pattern dokumentiert (v0.22.2) | ✓ |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep auf PDF-Render-Stelle + UI-Container für Button + localStorage-Pattern |
| **5.1 UI-Markup klappbarer Block** | 0.1 Tag | HTML im src/inspector.html neben PDF-Button (STANDARD-Bereich), CSS minimal nachziehen |
| **5.2 localStorage-Logik** | 0.1 Tag | Load on page-init, Save on PDF-export, Merken-Checkbox-Toggle, Tester-Keys in Cache-Clear-Button mit-löschen |
| **5.3 PDF-Sektion am Anfang** | 0.15 Tag | jsPDF-Block analog v0.26.0-Geometrie-Pattern, Word-Wrap für Notiz, Sektion-Skip wenn alle Felder leer, Hinweis-Zeile dezent |
| **5.4 PDF-Footer-Zeile** | 0.05 Tag | Footer-Render-Stelle erweitern um Tester-Prefix, nur wenn Name vorhanden |
| **5.5 i18n DE+EN** | 0.05 Tag | ~10 neue Keys |
| **5.6 Browser-Verifikation** | 0.1 Tag | Chrome+Safari, USDZ droppen → Tester-Block aufklappen → ausfüllen → PDF generieren → Audit-Sektion + Footer prüfen. Merken-Checkbox testen (reload → Werte da). Leere Felder: Sektion fehlt im PDF. Cache-Clear: Tester-Keys auch weg. |
| **5.7 Headless-Pool** | 0.05 Tag | 18/18 bleibt grün (Standard-Pipeline unverändert) |
| **5.8 README + CHANGELOG** | 0.05 Tag | Sprint-Eintrag, Audit-Story-Hinweis |
| **5.9 ADR-47** | inkludiert | Tester-Selbstangabe-Pattern (§ 9) |
| **5.10 Tag v0.28.0.4 + Push** | 0.05 Tag | Tag, Push, Latenz |
| **5.11 Memory-Update** | 0.05 Tag | inspector_project.md ergänzt v0.28.0.4-Block + Audit-Story als PR-Material |

**Total: 0.8 Tag** (eng kalkuliert, da viele kleine Schritte).

---

## 7. Strategischer Hebel

1. **PDF-Report wird Audit-Dokumentation** — Tester-Signatur + Datum + Notiz machen den Report zu offizieller Compliance-Doku. B2B-Vertriebs-Hebel: *"Wir liefern geprüfte Reports mit Prüfer-Signatur"* hat jetzt einen Beleg.
2. **Anschluss an USDseal-Trust-Familie** — Signatur der Datei (USDseal-Stempel) + Signatur des Prüfers (v0.28.0.4) = zwei Vertrauensschichten in einem Report. Story-Konsistenz mit *"Don't trust, verify"* aus v0.27.
3. **Rechtlich sauber** — Selbstangabe-Hinweis im PDF + Sektion-Titel macht klar dass viSales nicht verifiziert. Kein Reputations-Risiko durch falsche Tester-Angaben.
4. **Komfort durch Merken-Checkbox** — Power-User tippen einmal, danach Auto-Befüllt bei jedem Report. Senkt die Hürde, Tester-Daten überhaupt einzugeben.
5. **Keine neuen Dependencies** — Architektur-Anker hält, Schlank-Anker (Standard) bleibt unangetastet (kleine UI-Erweiterung, ~50 KB).

---

## 8. Konkrete Pre-v0.28.0.4-Steps

1. **v0.28.0.3 muss released sein** — sonst Konflikt im UI-Layout
2. **localStorage-Schema mit Cache-Clear-Button abgestimmt** — Tester-Keys werden mit-gelöscht (sonst inkonsistent)

Falls beide erfüllt: *"Keine — alle Vorbedingungen erfüllt."*

---

## 9. Decision-Log-Template

```markdown
### ADR-47 PDF Tester-Signatur via Selbstangabe-Eingabefeld — 2026-05-25 (oder Sprint-Datum)

**Kontext:** PDF-Audit-Report seit v0.23 vollständig, aber ohne menschliche Prüfer-Signatur. B2B-Vertrieb/Compliance benötigt Audit-Dokumentation (wer-wann-warum). Reine Inspector-Version + Datum im Footer reicht für Compliance-Workflows nicht.

Alternativen geprüft:
- **Kein Tester-Feld:** PDF bleibt anonym — Compliance-Lücke bleibt offen
- **Pflicht-Tester-Feld vor Drop:** würde Drop-Tool-Charakter brechen, Reibung am Einstieg
- **Tester-Feld als Modal-Dialog beim PDF-Klick:** Click-Overhead, weniger elegant
- **Tester-Feld als klappbarer Block neben PDF-Report-Button + localStorage-Merken:** opt-in, kein Pflicht, Komfort bei Wiederholung

**Entscheidung:** Klappbarer Block (Default kollabiert) neben PDF-Report-Button mit vier optionalen Feldern (Name, Firma, Rolle, Notiz mehrzeilig). Merken-Checkbox speichert via localStorage. Beim PDF-Export werden Werte ausgelesen, in **eigene Voll-Audit-Sektion am PDF-Anfang** (analog v0.26.0-Geometrie-Pattern, orange Akzentleiste) gerendert plus Footer-Zeile auf jeder Seite. Sektion-Titel + Disclaimer machen klar dass es **Selbstangabe** ist (nicht durch viSales verifiziert) — rechtssicher.

**Konsequenz:** PDF-Report wird zur offiziellen Compliance-Dokumentation. Vertriebs-Hebel *"Audit-Reports mit Prüfer-Signatur"* gewinnt Beleg. Story-Konsistenz mit USDseal-Trust-Familie (zwei Vertrauensschichten: Datei-Signatur + Tester-Signatur). Kein Reputations-Risiko durch falsche Angaben (Selbstangabe klar gekennzeichnet). Schlank-Anker des Standards bleibt unangetastet (UI-Erweiterung ~50 KB). Bei Bedarf später erweiterbar zu: Multi-Tester, kryptographische Signatur, Tester-Historie — bewusst NICHT in v0.28.0.4.
```

---

## 10. Quellen / Referenz-Links

- Vorgänger v0.28.0.3: `docs/ROADMAP-v0.28.0.3.md`
- v0.26.0 als PDF-Sektion-Pattern-Vorlage (Geometrie mit oranger Akzentleiste): `docs/ROADMAP-v0.26.0.md`
- v0.22.2 als localStorage-Pattern-Vorlage (Re-Import-Cache): `docs/ROADMAP-v0.22.2.md`
- v0.27 Verify-UI (Trust-Familie-Anschluss): `docs/ROADMAP-v0.27.md`
- ADR-38 (Version-Badge single source of truth): zieht INSPECTOR_VERSION automatisch
- Privates Persona-Anker: `/Users/g/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`

---

**Ende v0.28.0.4-Briefing.** Nach Sprint: Tag `v0.28.0.4`, Push, Memory-Update. Dann v0.28.1 (Findings-Klartext / Erklärbär-Sprint) als nächstes.
