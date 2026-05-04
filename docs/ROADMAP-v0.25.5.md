# Roadmap v0.25.5 — Severity-Recalibration

**Status:** Skeleton-Briefing · 2026-05-04 · **Test-Pool von Duke ausstehend**
**Story-Slot:** *"Validator kalibriert — Apple-Realität statt Spec-Strenge"*
**Ziel:** AR-Quick-Look-Validator sagt nicht mehr "AR Quick Look bricht" wenn Apple die Datei trotzdem in Quick Look zeigt.
**Aufwand:** 0.5–1 Tag (abhängig von Test-Pool-Umfang).

> Patch-Sprint nach v0.25.4 (Texture-Coverage). Master-Übersicht in `../ROADMAP.md`.

---

## 1. Befund — der Validator ist zu pessimistisch

User-Report 2026-05-04 mit iPhone-Screenshot: USDZs, die in AR Quick Look auf iPhone nachweislich **funktionieren**, werden vom Inspector als **"AR Quick Look bricht — Hard-Fail"** angezeigt (rotes Banner, Fehler-Badge).

**Konkret aus dem Screenshot:**

| Regel | Aktuelle Severity | Apple-Realität | Soll |
|---|---|---|---|
| `STRUCTURE_DEFAULT_PRIM_MISSING` | 🔴 Fehler | Apple fällt auf "first prim" zurück → läuft | 🟠 Warnung |
| `SCALE_METERS_PER_UNIT` (fehlt) | 🟠 Warnung | Apple nimmt 1.0 als Default → läuft | 🔵 Hinweis (oder Warnung wenn Werte krass) |

**Diagnose:** Inspector-Validator wurde damals (v0.22) **theoretisch nach Spec** kalibriert, nicht **empirisch nach Apple-Verhalten**. Apple ist deutlich gnädiger als die OpenUSD-Spec.

---

## 2. Phase 5.0 — Diagnose vor Fix (ADR-PC4 strikt)

**Pflicht vor Code-Change:** Test-Pool gegen reales Apple-AR-Quick-Look-Verhalten kalibrieren.

### Diagnose-Ablauf

**Schritt 1 — Test-Pool von Duke einsammeln**

Duke hat zugesagt: 5–10 echte USDZs, die **definitiv auf iPhone in AR Quick Look laufen**, aber **vom aktuellen Inspector als Hard-Fail markiert** werden. Mindestens umfassen:
- 1–2 mit `defaultPrim` fehlend
- 1–2 mit `metersPerUnit` fehlend oder unrealistisch
- 1–2 mit doppelten Material-Bindings
- 1–2 mit Animation-Edge-Cases (FPS, Time-Range)
- Optional: weitere Edge-Cases die im viSales-Kunden-Pool aufgetaucht sind

**Schritt 2 — Live-Verifikation pro File**

Für jede Datei aus dem Pool:
1. iPhone-Test: USDZ via AirDrop ans iPhone, tap → AR Quick Look öffnet? → Notiz.
2. Inspector-Diagnose: welche Regeln triggern? Welche Severity?
3. Diff: Inspector sagt "Fehler" → Apple läuft = **falsche Severity**

**Schritt 3 — Severity-Re-Kategorisierung**

Pro Regel entscheiden:
- Bleibt Hard-Fail (rot) — wenn AR Quick Look in der Praxis tatsächlich bricht
- Wird Warnung (orange) — wenn Apple Default-Verhalten greift, läuft aber mit Surprise
- Wird Hinweis (blau) — wenn nur Best-Practice-Verstoß ohne sichtbaren Effekt

---

## 3. 3-Stufen-Severity-Modell

| Stufe | Bedeutung | Banner-Logik | UI-Farbe |
|---|---|---|---|
| **Hard-Fail** | "AR Quick Look bricht garantiert" — z. B. ZIP korrupt, Hauptdatei fehlt, Apple-unsupported Format | Banner: "AR Quick Look bricht" | 🔴 rot |
| **Warnung** | "Läuft, aber Apple wendet Default an / Verhalten unklar" — z. B. defaultPrim fehlt, metersPerUnit fehlt, doppelter Material-Bind | Banner: "Läuft mit Vorbehalt" | 🟠 orange |
| **Hinweis** | "Schönheitsfehler / Best-Practice-Verstoß" — z. B. überflüssige `extra`-Files, unbenutzte Texturen | Banner-Status unverändert (manifest-state-driven) | 🔵 blau |

**State-Banner-Logik wird:**

```
findings.filter(f => f.severity === 'hard-fail').length > 0
  → Banner: "AR Quick Look bricht"
sonst findings.filter(f => f.severity === 'warning').length > 0
  → Banner: "Läuft mit Vorbehalt"
sonst
  → Banner unverändert (state-driven: SIGNED / DRAFT / NO_MANIFEST)
```

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Reine Severity-Re-Kategorisierung im Code |
| Apple AR Quick Look-Verhalten | Empirisch | Test-Pool ist die Wahrheits-Quelle, keine Apple-Doku reicht |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | v0.25.4 (Texture-Coverage) released | ⏳ kommt vor v0.25.5 |
| 2 | Test-Pool von Duke (5–10 USDZs) | ⏳ Duke liefert |
| 3 | Pro Pool-File: iPhone-Test-Notiz + Inspector-Diagnose | ⏳ Phase 5.0 |
| 4 | i18n-Keys für 3-Stufen-Banner-Texte | ⏳ in 5.1 |

**0 von 4 grün — Skeleton-Status.** Detail-Briefing wird gefüllt sobald Test-Pool vorliegt.

---

## 6. Phasen-Schätzung (vorläufig)

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.2–0.4 Tag | Test-Pool durchspielen, pro Regel Severity-Empfehlung |
| **5.1 Code-Anpassung** | 0.2–0.4 Tag | `AR_QL_RULES`-Severity-Felder anpassen, Banner-Logik refaktoren, i18n-Keys nachziehen |
| **5.2 Verifikation Browser** | 0.05 Tag | Test-Pool-Files in Inspector reinwerfen, neue Severity-Korrekt? |
| **5.3 Headless-Pool-Regression** | 0.05 Tag | 7/7 PASS bleibt — Test-Erwartungen müssen entsprechend angepasst werden |
| **5.4 README + CHANGELOG** | 0.1 Tag | "Validator kalibriert"-Sektion mit konkreten Beispielen |
| **5.5 ADR-27 dokumentieren** | inkludiert | "Severity gegen Apple-Realität, nicht gegen Spec-Strenge" |
| **5.6 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.5, Tag, Push |

**Total: 0.5–1 Tag** (abhängig wie viele Regeln betroffen sind).

---

## 7. Strategischer Hebel

v0.25.5 ist Trust-Anker für B2B-Demos:

1. **"Inspector lügt nicht":** wenn Banner "Läuft mit Vorbehalt" sagt, läuft die USDZ tatsächlich. Konferenz-Demo-Glaubwürdigkeit steigt.
2. **3-Stufen-Severity** wird Talk-Slide-Wert: zeigt empirische Validierung statt Spec-Strenge — differenziert von "wir lesen nur die Spec"-Tools.
3. **Test-Pool-Asset** als Cross-Sync-Output: alle 5–10 Files können (mit Duke's Erlaubnis) in den Public-Repo `tests/severity-pool/` wandern und werden Teil des Headless-Pools.

---

## 8. Konkrete Pre-v0.25.5-Steps

1. v0.25.3 EN-Toggle released
2. v0.25.4 Texture-Coverage released
3. **Duke liefert Test-Pool** — am besten zusammen mit Notizen "auf welchem iPhone-iOS getestet"
4. Plan-Chat überarbeitet dieses Skeleton zum vollen Briefing mit konkreter Severity-Tabelle pro Regel

---

## 9. Decision-Log-Template

```markdown
### ADR-27 Severity-Recalibration — 2026-05-XX

**Kontext:** Real-World-Test zeigt: Inspector markiert iPhone-laufende USDZs als Hard-Fail. Validator zu pessimistisch.

**Test-Pool-Befund (aus Phase 5.0):**
- N Files getestet, davon X mit Severity-Mismatch
- Konkrete Regel-Anpassungen: ___ (Tabelle)

**Entscheidung:** 3-Stufen-Severity (Hard-Fail / Warnung / Hinweis), Banner-Logik orientiert sich an Apple-Verhalten, nicht an OpenUSD-Spec.

**Konsequenz:** State-Banner zeigt drei Stufen statt zwei. Headless-Pool-Erwartungen aktualisiert. AR-QL-Validator-USP bleibt erhalten — wird sogar verstärkt durch empirische Kalibration.
```

---

## 10. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.22.md` (AR-QL-Validator originaler Stand)
- AR-QL-Regeln: `AR-QL-RULES.md`
- Test-Asset-Pool: `tests/severity-pool/` (legen wir an wenn Duke-Pool kommt)

### Externe Specs

- [Apple AR Quick Look — Validator Tool `usdARKitChecker`](https://developer.apple.com/augmented-reality/quick-look/) — Apple's eigener Checker als Referenz-Vergleich
- [OpenUSD USDZ Specification](https://openusd.org/release/spec_usdz.html) — die Spec gegen die wir bisher kalibriert haben (zu streng für Apple-Realität)

---

**Ende v0.25.5-Skeleton.** Wird vor Sprint-Start zum vollen Briefing erweitert, sobald Test-Pool vorliegt.
