# Roadmap v0.28.1 — Findings-Klartext (Erklärbär-Sprint)

**Status:** Vorbereitungs-Dokument · 2026-06-04
**Story-Slot:** *"Inspector erklärt jetzt — jedes Finding wird zum verständlichen Satz mit konkretem Fix-Vorschlag."*
**Ziel:** Statische Klartext-Erklärungen für die Top 10-15 häufigsten Finding-Typen, DE+EN. Inline-Aufklapp pro Finding im UI. Im PDF opt-in via Checkbox neben PDF-Report-Button. Kein LLM, kein API-Key, kein Privacy-Bruch — vollständig lokal.
**Aufwand:** M (1.0–1.5 Tage)

> Erster Inhalts-Sprint nach der v0.28.0-Welle. Antwort auf den USP-Gap: technische Finding-Codes wie *"TEXTURE_TOO_LARGE"* versteht nur ein 3D-Spezialist — Marketing- und Vertriebs-Verantwortliche brauchen Klartext mit Lösungs-Vorschlag. Umgewidmet 2026-05-25: dynamische LLM-Bridge wandert in bezahlte Premium-Variante, kostenloser Inspector bekommt kuratierten Lookup-Tisch.

---

## 1. Befund

Inspector zeigt heute Findings als technische Codes:

```
⚠ TEXTURE_TOO_LARGE — Textur überschreitet 4096×4096
🔴 STRUCTURE_DEFAULT_PRIM_MISSING — defaultPrim fehlt im Manifest
⚠ USDC_BINARY_LIMITATION — Material-Channels können nicht ausgelesen werden
```

Das versteht der 3D-Spezialist sofort. **Marketing-Verantwortliche beim Kunden, Vertriebler im Erstgespräch, Empfänger einer Lieferanten-USDZ verstehen es nicht.** Folge: der Inspector wird abgegeben an *"unseren Tech-Menschen, der versteht das schon"* — die Brücke vom Diagnose-Tool zur sofortigen Handlung fehlt.

**Lücke heute:**
- Findings sind technisch korrekt, aber nicht handlungsleitend
- Keine Fix-Vorschläge in der UI
- Marketing-/Compliance-Zielgruppe braucht Übersetzung durch Dritte

**Was Erklärbär leistet (v0.28.1):**

```
⚠ TEXTURE_TOO_LARGE — Textur überschreitet 4096×4096    [?]
   ↓ Klick auf [?] öffnet:

   Die Datei 'holz_eiche.png' ist 8192×8192 Pixel groß. 
   Apple AR Quick Look akzeptiert maximal 4096×4096 — das 
   iPhone zeigt die Textur entweder unscharf herunterskaliert 
   oder gar nicht. 
   
   Lösung: Textur in Photoshop oder via macOS-Befehl 
   `sips -Z 4096 holz_eiche.png` auf 4096 Pixel verkleinern, 
   dann USDZ neu exportieren.
```

**Strategischer Hebel:** Inspector wird vom Diagnose-Tool zum **selbsterklärenden Audit-Tool**. Marketing-Person liest Klartext, leitet Fix an Konstruktion/Agentur weiter. Vertriebs-Story: *"Inspector erklärt sich selbst — kein 3D-Spezialist nötig für die Asset-Vorprüfung."* Anschluss an USDseal-Familien-Story (Don't trust, verify + Audit-Signatur + jetzt Klartext-Erklärung = drei Komfort-Schichten).

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector

# A) Aktuellen Finding-Code-Inventar erstellen
grep -n "type.*:.*['\"]" src/inspector.html | grep -E "TEXTURE|STRUCTURE|MANIFEST|USDC|GEOMETRY" | head -50
# Oder über die AR-Quick-Look-Regel-Definition:
grep -n "RULE_ID\|finding_id\|code.*:" src/inspector.html | head -50

# B) Aktuelles UI-Pattern für Findings nachvollziehen
grep -n "findings\|renderFindings\|finding-item" src/inspector.html | head -10
# Wie werden Findings heute gerendert? Welche DOM-Struktur?
# Wo lässt sich der [?]-Trigger sauber anbringen?

# C) PDF-Generierung für Findings
grep -n "addFinding\|renderFindingPdf\|pdf.*finding" src/inspector.html | head -10
# Wie viel Aufwand ist Erklärung-Block ins PDF einzubauen?

# D) i18n-Pattern für mehrzeilige Texte
grep -n "i18n.*\\\\n\|t(.*)" src/inspector.html | head -5
# Wie wird mehrzeiliger i18n-Text heute strukturiert?

# E) Bestehende CSS-Klassen für aufklappbare Boxen
grep -n "details\|summary\|accordion\|expand" src/inspector.html | head -10
# Bauen wir nativ <details>/<summary> ein oder eigenes Toggle?
```

→ Lokalisiert:
1. Komplette Liste aller Finding-Codes (Top 30-40 erwartet)
2. Render-Stelle pro Finding — `[?]`-Trigger kommt am Ende der Finding-Zeile
3. PDF-Render-Stelle pro Finding — Erklärung-Block kommt unter Finding wenn Checkbox aktiv
4. i18n-Datei für ~30 neue Key-Paare (DE + EN × Erklärung + Fix)
5. UI-Pattern: native `<details>`/`<summary>` reicht — keine CSS-Magie nötig

**Konsistenz-Check:**
- Top 10-15 Findings müssen die **häufigsten 80%** abdecken (Pareto). Code-Chat wählt aus dem Inventar auf Basis: was sehen User in Real-World-Reports? AR-QL-Regeln aus v0.25.8 sind starke Kandidaten weil sie ständig triggern
- Klartext + Fix müssen **kurz** sein — max. 3-4 Sätze Klartext, 1-2 Sätze Fix. Keine Doktorarbeit
- DE und EN sind **separat zu pflegen**, nicht maschinell übersetzt — Sprach-Stil muss in beiden Sprachen sauber sein (DE: Du-Form-Anschluss vermeiden, neutral schreiben; EN: aktive Stimme, Imperativ für Fix-Schritte)

---

## 3. Scope

### 3.1 Klartext-Lookup-Tabelle (Top 10-15 Findings)

**Format pro Finding (im Source als JS-Object):**

```javascript
const FINDING_EXPLANATIONS = {
  TEXTURE_TOO_LARGE: {
    de: {
      explanation: "Eine oder mehrere Texturen überschreiten 4096×4096 Pixel. Apple AR Quick Look akzeptiert maximal 4K-Texturen — das iPhone zeigt die Textur entweder unscharf herunterskaliert oder gar nicht.",
      fix: "Texturen in Photoshop oder via macOS-Befehl `sips -Z 4096 datei.png` auf maximal 4096 Pixel verkleinern, dann USDZ neu exportieren."
    },
    en: {
      explanation: "One or more textures exceed 4096×4096 pixels. Apple AR Quick Look only accepts textures up to 4K — the iPhone either downscales the texture poorly or doesn't display it at all.",
      fix: "Resize textures to a maximum of 4096 pixels in Photoshop or via the macOS command `sips -Z 4096 file.png`, then re-export the USDZ."
    }
  },
  STRUCTURE_DEFAULT_PRIM_MISSING: {
    de: { ... },
    en: { ... }
  },
  // ... weitere 8-13 Einträge
};
```

**Auswahl der Top 10-15 erfolgt in Phase 5.0 auf Basis:**
- AR-QL-Regeln (W-1 bis W-N, X-1 bis X-N aus v0.25.x)
- Häufigste Texture-/Structure-/Manifest-Befunde aus Real-World-Sweep 2026-05-05
- Findings die regelmäßig in DIEGOsat/Frankfurt/RENZ-Reports auftauchen

**Konkrete Vorschlag-Liste (Code-Chat priorisiert in Phase 5.0):**

1. `TEXTURE_TOO_LARGE` (>4096)
2. `TEXTURE_FORMAT_UNSUPPORTED` (z. B. WebP, BMP)
3. `STRUCTURE_DEFAULT_PRIM_MISSING`
4. `STRUCTURE_NESTED_USDZ`
5. `STRUCTURE_FILE_SIZE_LIMIT` (viSales-Empfehlung)
6. `MANIFEST_MISSING` (kein USDseal)
7. `MANIFEST_SIGNATURE_INVALID`
8. `USDC_BINARY_LIMITATION` (Material-Channels nicht lesbar)
9. `GEOMETRY_NO_POLYS` (procedural-only)
10. `TEXTURE_POWER_OF_TWO` (Performance-Warnung)
11. `ASTC_NOT_BROWSER_SUPPORTED`
12. `KTX2_FORMAT_LABEL_ONLY` (Inspector kann es nicht decodieren)
13. (drei weitere nach Real-Use-Häufigkeit)

### 3.2 UI-Pattern — Inline-Aufklapp pro Finding

**Layout:**

```
┌────────────────────────────────────────────────────────────┐
│ ⚠ TEXTURE_TOO_LARGE — Textur überschreitet 4096×4096   [?] │
└────────────────────────────────────────────────────────────┘

Klick auf [?] öffnet:

┌────────────────────────────────────────────────────────────┐
│ ⚠ TEXTURE_TOO_LARGE — Textur überschreitet 4096×4096   [×] │
│                                                            │
│  ▸ Was bedeutet das?                                       │
│    Eine oder mehrere Texturen überschreiten 4096×4096      │
│    Pixel. Apple AR Quick Look akzeptiert maximal 4K-       │
│    Texturen — das iPhone zeigt die Textur entweder         │
│    unscharf herunterskaliert oder gar nicht.               │
│                                                            │
│  ▸ Wie lösen?                                              │
│    Texturen in Photoshop oder via macOS-Befehl             │
│    `sips -Z 4096 datei.png` auf maximal 4096 Pixel         │
│    verkleinern, dann USDZ neu exportieren.                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Technik:**
- Natives `<details>`/`<summary>` — kein eigenes JS-Toggle, kein CSS-Aufwand für Animation
- Trigger-Element: `[?]`-Glyphe oder `▾`-Pfeil, rechtsbündig in der Finding-Zeile
- Bei geöffnetem Details: Pfeil dreht sich automatisch via CSS auf `details[open]`
- Box öffnet sich nach unten, schiebt nachfolgende Findings nach unten (kein Overlay, kein z-index-Drama)
- Default: alle Details zugeklappt
- Findings ohne Erklärung in der Lookup-Tabelle: kein `[?]`-Trigger (sauberer als ein lehrer Aufklapp)

**Falls Finding nicht in Lookup-Tabelle:**
- Trigger-Element nicht rendern
- Finding-Zeile bleibt wie heute (nur Code + Kurztext)
- Kein Hinweis *"Erklärung fehlt"* — leise, ohne Drama

### 3.3 PDF — Opt-in via Checkbox

**Position der Checkbox:** Neben dem PDF-Report-Button in der Topbar, vor dem Klick.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│ [PDF Report ↓]  ☐ mit Erklärungen   ▾ Reviewed by           │
└──────────────────────────────────────────────────────────────┘
```

**Verhalten:**
- Default: Checkbox **deaktiviert** — Audit-Compliance bekommt knappes Original
- Bei aktiver Checkbox: PDF rendert pro Finding zusätzlich einen Erklärung-Block (analog UI-Aufklapp)
- Checkbox-State **wird nicht in localStorage gemerkt** — jeder PDF-Lauf ist bewusste Entscheidung
- Plus: kleines Info-Icon neben Checkbox mit Tooltip *"Erklärungen helfen Marketing- und Vertriebsteams. Für reine Audit-Reports ggf. ausgeschaltet lassen."*

**PDF-Render-Pattern:**

```
═══════════════════════════════════════════════════════════════
⚠ TEXTURE_TOO_LARGE — Textur überschreitet 4096×4096
───────────────────────────────────────────────────────────────

Was bedeutet das?
Eine oder mehrere Texturen überschreiten 4096×4096 Pixel...

Wie lösen?
Texturen in Photoshop oder via macOS-Befehl...
═══════════════════════════════════════════════════════════════
```

**Stil im PDF:**
- Findings-Code-Zeile bleibt wie heute (bold)
- Erklärung darunter in normaler Schrift, mit Einrückung
- Dezent, kein orange Akzent (das ist Audit-/Tester-Bereich)
- Bei nicht-erklärbaren Findings: kein leerer Block

### 3.4 Was NICHT in v0.28.1

- **Keine LLM-Bridge** — dynamische Erklärungen wandern in Premium-Distribution
- **Keine MCP-Anbindung** — gleicher Grund
- **Keine Auto-Übersetzungen** — DE und EN sind manuell gepflegt
- **Keine Variants-spezifischen Erklärungen** — solange Player keine Variants rendert, sind sie nicht im Findings-Set
- **Keine User-Feedback-Channel** *"diese Erklärung war hilfreich/nicht"* — eigenes Sprint-Thema, vermutlich Premium
- **Keine Statistik** *"Du hast Erklärung XY 12× geöffnet"* — Privacy-First-Anker
- **Keine Anpassbarkeit** *"Erklärungen für Compliance vs. Marketing-Variante"* — overengineering für jetzt

### 3.5 v0.28.1.1 (Folge-Sprint, nicht in v0.28.1)

Rest der Findings nachziehen (vermutlich 15-25 weitere Einträge in der Lookup-Tabelle). Kein eigener Briefing-Aufwand — Konvention im README: *"wer einen neuen Finding-Code einführt, schreibt auch die Erklärung in `FINDING_EXPLANATIONS`-Lookup-Tabelle dazu (DE + EN). Findings ohne Erklärung zeigen kein `[?]`-Trigger und werden in v0.28.1.x nachgezogen."*

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Bestehender Findings-Renderer | unverändert | nur Trigger-Element + Aufklapp hinzu |
| jsPDF 3.0.3 | unverändert | nur zusätzlicher Block pro Finding bei Checkbox aktiv |
| Native `<details>`/`<summary>` | Browser-Standard | kein neuer Dep, kein CSS-Bundle |
| AR-QL-Regel-Definitions aus v0.25.8 | recycelt | Code-Liste als Grundlage für Lookup-Tabelle |
| `docs/AR-QL-RULES-SOURCES.md` (v0.25.6) | recycelt | Quelle für Fix-Vorschläge bei AR-bezogenen Findings |

Keine neuen Deps. Architektur-Anker hält. Schlank-Anker bleibt (Lookup-Tabelle ist ~5-10 KB).

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.28.0.7 released | ✓ (2026-06-04) |
| 2 | Finding-Code-Inventar im Source greifbar | ✓ (Code-Chat-Phase 5.0 inventarisiert) |
| 3 | Build-Step (Variante Y) für Standard + Advanced | ✓ |
| 4 | Theme-Variable-Check im Build (v0.28.0.7) | ✓ — verhindert CSS-Fallback-Bugs in neuem UI-Code |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose + Top-15-Auswahl** | 0.15 Tag | grep auf alle Finding-Codes, Häufigkeits-Ranking aus AR-QL + Real-World-Sweep, Auswahl der Top 10-15 |
| **5.1 Lookup-Tabelle befüllen** | 0.4 Tag | 10-15 Einträge × (DE Erklärung + DE Fix + EN Erklärung + EN Fix), kurze Sätze, präzise Fixes. **Längste Phase.** |
| **5.2 UI-Trigger + `<details>`-Integration** | 0.15 Tag | `[?]`-Element neben Finding-Code, native `<details>`-Wrapping, CSS für Pfeil-Rotation bei `details[open]` |
| **5.3 Checkbox neben PDF-Report-Button** | 0.1 Tag | Markup, Listener, State-Variable für `includeExplanations` |
| **5.4 PDF-Rendering mit Erklärung-Block** | 0.15 Tag | jsPDF-Logik: bei Checkbox-State true, pro Finding zusätzlich Erklärung-Block (mit splitTextToSize für mehrzeilig) |
| **5.5 Browser-Verifikation** | 0.1 Tag | Chrome+Safari, alle 10-15 Findings durchklicken: UI-Aufklapp funktioniert, Pfeil dreht sich, ohne JS-Toggle. PDF mit + ohne Checkbox vergleichen |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 bleibt grün |
| **5.7 README + CHANGELOG + Konvention v0.28.1.x** | 0.05 Tag | Sprint-Eintrag, plus Konvention für künftige Sprints: "neue Findings = neue Lookup-Einträge" |
| **5.8 ADR-48** | inkludiert | Findings-Klartext-Pattern dokumentiert (§ 9) |
| **5.9 Tag v0.28.1 + Push** | 0.05 Tag | Tag, Push, Latenz |
| **5.10 Memory-Update** | 0.05 Tag | inspector_project.md ergänzt v0.28.1-Block + Erklärbär-Story als PR-Material |

**Total: 1.25 Tage.**

---

## 7. Strategischer Hebel

1. **Inspector wird selbsterklärend** — Marketing-/Vertriebs-Zielgruppe braucht keinen 3D-Spezialisten mehr für Asset-Vorprüfung. Senkt die Einstiegshürde drastisch.
2. **Konkrete Fix-Vorschläge** — User weiß nach dem Lesen was zu tun ist, nicht nur was kaputt ist. *"Inspector hilft, nicht nur diagnostiziert."*
3. **Anschluss an USDseal-Familien-Story** — drei Komfort-Schichten kombiniert: (a) Diagnose mit Klartext (v0.28.1), (b) Audit-Signatur im PDF (v0.28.0.4), (c) Trust-Verifikation (v0.27). Story-Konsistenz für PR-Welle.
4. **Premium-Abgrenzung sichtbar** — *"Statische Klartext-Erklärungen kostenlos, dynamische LLM-Bridge in Premium"* macht das Premium-Modell ehrlich kommunizierbar ohne den freien Stack zu kannibalisieren.
5. **SEO-Hebel über die Doku** — die Lookup-Tabelle wird perspektivisch als öffentliche Doku verlinkt (*"Was bedeutet TEXTURE_TOO_LARGE im AR Quick Look?"* ist Suchbegriff-Futter). Aber erst ab v0.28.1.x mit vollem Set.

---

## 8. Konkrete Pre-v0.28.1-Steps

1. **v0.28.0.7 muss released sein** — Theme-Check im Build greift, neue UI-Klassen werden gegen Theme validiert.
2. **Real-World-Sweep-Daten greifbar** — `tests/real-world-2026-05-05.md` als Häufigkeits-Quelle für Top-15-Auswahl

Falls beide erfüllt: *"Keine — alle Vorbedingungen erfüllt."*

---

## 9. Decision-Log-Template

```markdown
### ADR-48 Findings-Klartext via statische Lookup-Tabelle — 2026-06-04 (oder Sprint-Datum)

**Kontext:** Inspector zeigt Findings als technische Codes (TEXTURE_TOO_LARGE etc.) — versteht der 3D-Spezialist, nicht aber Marketing-/Vertriebs-/Compliance-Verantwortliche. USP-Gap: Asset-Vorprüfung wird heute an Tech-Personen delegiert. Lösung muss kostenlos, lokal, privacy-konform sein.

Alternativen geprüft:
- **LLM-API-Bridge (Variante A):** dynamische Erklärungen via Claude/GPT — Privacy-Bruch, API-Key-Management, in Premium
- **MCP-Server-Wrapper (Variante B):** lokaler MCP-Server — Infrastruktur-Aufwand, in Premium
- **Statische Lookup-Tabelle (Variante C):** kuratierte Klartext-Erklärungen + Fix-Vorschläge pro Finding-Typ, DE+EN, kein LLM, kein API, vollständig lokal

**Entscheidung:** Variante C. Lookup-Tabelle `FINDING_EXPLANATIONS` als JS-Object im Source, ~10-15 Einträge in v0.28.1 (Pareto-Auswahl der häufigsten Findings), Rest in v0.28.1.x nachgezogen. UI-Pattern: natives `<details>`/`<summary>` für Inline-Aufklapp, `[?]`-Trigger nur bei Findings mit Lookup-Eintrag. PDF opt-in via Checkbox neben PDF-Report-Button (default deaktiviert — Audit-Compliance bekommt knappes Original). Konvention im README: neue Findings müssen Erklärung mitliefern.

**Konsequenz:** Inspector wird vom Diagnose-Tool zum selbsterklärenden Audit-Tool für Nicht-Spezialisten. Architektur-Anker (Privacy, Single-File, Schlank) bleiben unangetastet — Lookup-Tabelle ist ~5-10 KB. Premium-Distribution bekommt klare Abgrenzung: dynamische LLM-Erklärungen wären Premium-USP. SEO-Potenzial für die Doku perspektivisch (Lookup-Texte als Suchbegriff-Futter), aber erst nach v0.28.1.x mit vollem Set.
```

---

## 10. Quellen / Referenz-Links

- Vorgänger v0.28.0.7: `docs/ROADMAP-v0.28.0.7.md` (Theme-Check als Voraussetzung)
- AR-QL-Regel-Definitions: `docs/AR-QL-RULES.md` + `docs/AR-QL-RULES-SOURCES.md`
- Real-World-Sweep-Daten: `tests/real-world-2026-05-05.md`
- Backlog-Begründung Premium-Abgrenzung: `docs/v0.28-konsumer-patterns-backlog.md` § "Verschoben in bezahlte Premium-Variante"
- Memory-Feedback: `[[feedback_inspector_advanced_naming]]` — Begriffs-Konsistenz
- Privates Persona-Anker: `/Users/g/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`

---

**Ende v0.28.1-Briefing.** Nach Sprint: Tag `v0.28.1`, Push, Memory-Update. Dann v0.28.2 (USDC-Material-Parser) — aber Hosting-Frage (COOP/COEP) wird vorher strategisch geklärt.
