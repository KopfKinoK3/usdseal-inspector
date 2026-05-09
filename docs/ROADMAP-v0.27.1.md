# Roadmap v0.27.1 — Landingpage "Verify it yourself"

**Status:** Vorbereitungs-Dokument · 2026-05-09
**Story-Slot:** *"Don't trust, verify — die Verify-Story als eigenständige Landingpage-Sektion mit Code-Snippet und Live-Inspector-Verlinkung"*
**Ziel:** Neue Sektion `#verify` auf Inspector-Landingpage (DE+EN). PR-Material für die "Verify it yourself"-Reichweiten-Welle. Anker-Link für externe Verteilung (LinkedIn-Posts, AOUSD-Talk-Folien, Brevo-Newsletter).
**Aufwand:** 0.2–0.4 Tag (S).

> Anschluss-Sprint nach v0.27 (Verify-UI Self-Tests released 2026-05-09). Master-Übersicht in `../ROADMAP.md`. Letzter Inhalts-Sprint vor v0.28-Konsumer-Welle.

---

## 1. Befund

**v0.27 hat den Trust-Layer verifizierbar gemacht** — Inspector zeigt 3-Layer-Architektur live, Avalanche-Demo (138/256 Bits = 53.9%), Diff-View bei Mismatch, Verlinkungen auf CLI-Outputs. **Aber:** das ist nur sichtbar, **wenn** der User das Inspector-UI lädt. Die Landingpage erzählt die Verify-Story heute **nicht**.

**Was fehlt auf der Landingpage:**
- Keine eigene Sektion zu Verify / Trust / Reproduzierbarkeit
- Kein Code-Snippet zum Selber-Prüfen
- Keine Verlinkung auf die CLI-Outputs (Spec, Verifier, Threat Model)
- Kein Anker `#verify` für externe PR-Verteilung

**v0.27.1 schließt die Lücke** — macht aus dem Inspector-UI-Feature eine **PR-fähige Landingpage-Story** mit eigenem Anker-Link.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector/landingpage
grep -n "<section id=" deutsch/index.html | head -20
grep -n "<section id=" english/index.html | head -20
```

→ Ist-Struktur (DE-Version):

```
hero → #modi → #demo → #funktionen → #ar-quick-look →
#anwendung → privacy → datei-lebenszyklus → #visales-stack →
#faq → 30-Minuten-Termin
```

**Vorgesehene Position der neuen `#verify`-Sektion:** zwischen `#ar-quick-look` und `#anwendung`. Begründung: AR-Validator ist die Validator-USP, danach kommt Trust-USP, dann der praktische Anwendungs-Block. Story-Flow: *"Inspector zeigt was drin ist (Funktionen/AR-QL) → Inspector zeigt dass du's verifizieren kannst (Verify) → so nutzt du das (Anwendung)"*.

**Konsistenz-Check:** Visueller Stil der Sektionen identisch übernehmen — gleiche Container-Klasse, gleicher h2-Stil, gleiche Section-Padding-Werte. **Kein neuer CSS-Build-Step**, nur bestehende Klassen wiederverwenden.

---

## 3. Scope

### 3.1 Neue Sektion `#verify` (DE + EN)

**Layout-Skizze:**

```
┌─────────────────────────────────────────────────────────────┐
│  Verify it yourself                          (DE/EN-Headline)│
│  Don't trust, verify.                              (Sub-Hint)│
│                                                              │
│  USDseal-Signaturen sind reproduzierbar.                     │
│  Jede signierte USDZ trägt SHA-256-Hashes pro Komponente —   │
│  du kannst sie unabhängig nachrechnen, in 5 Zeilen Python.   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 3-Layer-Trust-Architektur                           │    │
│  │ Layer 1 — Komponenten-Hash (SHA-256 pro ZIP-Member) │    │
│  │ Layer 2 — Pre-Seal-Hash (Spec v0.3, in Arbeit)      │    │
│  │ Layer 3 — Manifest-Signatur (COSE_Sign1 / Ed25519)  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Selber prüfen — 5 Zeilen Python:                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ import zipfile, hashlib                              │    │
│  │ z = zipfile.ZipFile('signed.usdz')                   │    │
│  │ for member in z.namelist():                          │    │
│  │     h = hashlib.sha256(z.read(member)).hexdigest()   │    │
│  │     print(member, h)                                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  → Inspector zeigt dieselben Hashes live im Browser.         │
│  → Independent Verifier (~120 Zeilen Python) macht den       │
│    Manifest-Roundtrip (Komponenten + COSE_Sign1).            │
│                                                              │
│  [Inspector öffnen]  [Verify-Strategy ansehen]               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Inhalt — DE-Texte

**Headline:** *Selber prüfen*
**Untertitel:** *Don't trust, verify.*
**Pitch-Absatz:**
> *USDseal-Signaturen sind reproduzierbar. Jede signierte USDZ trägt SHA-256-Hashes pro ZIP-Komponente — du kannst sie unabhängig nachrechnen, in 5 Zeilen Python. Inspector zeigt dieselben Hashes live im Browser, der Independent Verifier prüft den vollen Manifest-Roundtrip.*

**3-Layer-Block:**
- **Layer 1 — Komponenten-Hash:** *SHA-256 pro ZIP-Member. Wenn ein Byte sich ändert, ändert sich der Hash. Inspector zeigt jede Komponente.*
- **Layer 2 — Pre-Seal-Hash:** *Hash des gesamten USDZ vor Manifest-Injection. In Spec v1.0 vorgesehen, im Sealing-Code in Arbeit.*
- **Layer 3 — Manifest-Signatur:** *COSE_Sign1 / Ed25519. Independent-Verifier-Script implementiert, Inspector-Live-Verify ab v0.3.*

**Code-Snippet:** Python (5 Zeilen, siehe Layout-Skizze).

**CTAs:** *"Inspector öffnen"* (führt auf `kopfkinok3.github.io/usdseal-inspector/`) + *"Verify-Strategy ansehen"* (führt auf `docs/USDSEAL-VERIFY-STRATEGY.md` im Repo).

### 3.3 Inhalt — EN-Texte

**Headline:** *Verify it yourself*
**Untertitel:** *Don't trust, verify.*
**Pitch-Absatz:**
> *USDseal signatures are reproducible. Every signed USDZ carries SHA-256 hashes per ZIP component — you can recompute them independently in 5 lines of Python. Inspector shows the same hashes live in the browser, the Independent Verifier handles the full manifest roundtrip.*

**3-Layer-Block:** analog DE, übersetzt.

**Code-Snippet:** identisch (Python ist sprach-neutral).

**CTAs:** *"Open Inspector"* + *"View Verify Strategy"*.

### 3.4 Verlinkungen (3 Stück, beide Sprachen)

| Anchor-Text DE | Anchor-Text EN | Ziel |
|---|---|---|
| Inspector öffnen | Open Inspector | `https://kopfkinok3.github.io/usdseal-inspector/` |
| Verify-Strategy ansehen | View Verify Strategy | `https://github.com/KopfKinoK3/usdseal-inspector/blob/main/docs/USDSEAL-VERIFY-STRATEGY.md` |
| Independent Verifier (Python) | Independent Verifier (Python) | [github.com/KopfKinoK3/usdseal-verify](https://github.com/KopfKinoK3/usdseal-verify) (public, Apache-2.0) — Inspector verlinkt direkt |

**Falls Verifier-Repo noch privat:** Link aus dem CTA-Block raus, dafür Hinweis-Zeile *"Independent Verifier wird kommende Woche öffentlich"* — ehrlich, kein Tot-Link. ADR-PC4-konform.

### 3.5 Was NICHT in v0.27.1

- **Keine Avalanche-Demo auf der Landingpage** — die lebt im Inspector-UI, hier nur Verlinkung
- **Kein Diff-View-Demo** — auch nur Inspector-UI-Material
- **Kein neues CSS-File** — bestehende Klassen wiederverwenden
- **Kein JavaScript-Block** — pure HTML/CSS-Sektion
- **Keine Test-Vektoren-Verlinkung** — kommt erst wenn Build-Chat sie erzeugt + öffentlich publik macht (CLI-Backlog-Punkt)
- **Keine Live-Hash-Berechnung auf Landingpage** — schon im Inspector-UI vorhanden

### 3.6 Single-File-Anker hält

Pure HTML-Änderung. Kein neuer Dep. Konsistent mit Inspector-Architektur.

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Bestehende Landingpage-Struktur | ✓ | nur Sektion ergänzen, keine Refactorings |
| CSS-Klassen (Container, Section, Button, Code-Block) | ✓ vorhanden | wiederverwenden |
| Verify-Strategy.md im Inspector-Repo | ✓ public | Verlinkung sicher |
| Inspector-Live-URL | ✓ kopfkinok3.github.io | bestehend |
| usdseal-verify-Repo | Status klären in Phase 5.0 | privat oder public? |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.27 stable released | ✓ Tag online seit 2026-05-09 |
| 2 | Verify-Strategy.md auf Bytestream-Realität aktualisiert | ✓ seit 2026-05-07 |
| 3 | Bestehende DE+EN-Landingpage-Files | ✓ in `landingpage/{deutsch,english}/index.html` |
| 4 | Layout-Pattern aus #ar-quick-look + #funktionen als Referenz | ✓ |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | Section-Struktur + CSS-Klassen-Inventar in beiden Sprach-Files prüfen, usdseal-verify-Repo-Sichtbarkeit klären |
| **5.1 DE-Sektion bauen** | 0.1 Tag | `<section id="verify">` in `landingpage/deutsch/index.html` einfügen zwischen `#ar-quick-look` und `#anwendung` |
| **5.2 EN-Sektion bauen** | 0.05 Tag | Übersetzte Variante in `landingpage/english/index.html`, identische Struktur |
| **5.3 Code-Snippet styling** | 0.05 Tag | Falls noch kein Code-Block-CSS vorhanden: minimal-CSS für `<pre><code>`-Block einfügen (monospace, leicht eingerückt, dezent grauer Hintergrund) |
| **5.4 CTAs verdrahten** | 0.05 Tag | `target="_blank" rel="noopener"` + IDs für etwaige spätere GA-Tracking |
| **5.5 Cross-Browser-Verifikation** | 0.05 Tag | DE + EN in Chrome + Safari prüfen, Code-Block lesbar, Buttons klickbar, Anker `#verify` per direkter URL erreichbar |
| **5.6 README + CHANGELOG** | 0.05 Tag | "Landingpage Verify-Sektion (DE+EN)" |
| **5.7 ADR-40** | inkludiert | Template § 9 |
| **5.8 Snapshot + Tag** | 0.05 Tag | Tag `v0.27.1`, Push. **INSPECTOR_VERSION bleibt '0.27' — Landingpage-Änderung berührt index.html nicht.** |

**Total: 0.2–0.4 Tag (S).**

---

## 7. Strategischer Hebel

v0.27.1 ist **PR-Story-Sprint** — die Verify-UI aus v0.27 wird **außen sichtbar**:

1. **Anker-Link `#verify` für externe Verteilung** — LinkedIn-Posts, GBP-Posts, AOUSD-Folien können direkt auf die Story zeigen.
2. **Code-Snippet als Beweisstück** — *"5 Zeilen Python, das war's"* ist die kürzeste mögliche Reviewer-Schwelle. Genau das was ADR-PC6 als Argument 2 bringt.
3. **CTA-Funnel:** Landingpage-Sektion → Inspector öffnen → Verify-UI live sehen → reproduziert mit Python. Drei Stufen, jede selbstständig wertvoll.
4. **Brevo-Newsletter-Material** — diese Sektion ist die Newsletter-Hauptstory für die kommende Verify-Welle.
5. **AOUSD-Talk-Folie** — *"Don't trust, verify"* mit Live-Demo-Link, Code-Snippet, Avalanche-Wert (138/256 Bits aus v0.27). Konferenz-Material steht.
6. **Letzter Inhalts-Sprint vor v0.28-Konsumer-Welle** — danach kommt Architektur-Erweiterung (Web-Component-Embed-Boilerplate).

---

## 8. Konkrete Pre-v0.27.1-Steps

Keine — alle Vorbedingungen erfüllt. Phase 5.0 muss nur usdseal-verify-Repo-Sichtbarkeit klären.

---

## 9. Decision-Log-Template

```markdown
### ADR-40 Landingpage Verify-Sektion — 2026-05-XX

**Kontext:** v0.27 hat Verify-UI im Inspector live gemacht (3-Layer-Architektur, Avalanche-Demo, Diff-View). Externe PR-Verteilung brauchte einen Anker-Link auf der Landingpage — die Verify-Story war intern sichtbar, extern nicht.

**Entscheidung:** Neue Sektion `#verify` zwischen `#ar-quick-look` und `#anwendung` in beiden Sprach-Versionen der Landingpage. Inhalt: Pitch-Absatz "Don't trust, verify", 3-Layer-Architektur-Block, Python-Code-Snippet (5 Zeilen), CTAs auf Inspector-Live-URL und Verify-Strategy.md. Pure HTML-Änderung, bestehende CSS-Klassen wiederverwendet, kein neuer Dep, kein Build-Step. Independent-Verifier-Link bedingt — falls Repo noch privat, Hinweis "demnächst public" statt Tot-Link (ADR-PC4-konform).

**Konsequenz:** Verify-Story ist extern verlinkbar (`#verify`-Anker). PR-Material für LinkedIn, Brevo-Newsletter, AOUSD-Talk steht. CTA-Funnel Landingpage → Inspector → Python-Verify dreistufig. Letzter Inhalts-Sprint vor v0.28-Konsumer-Welle abgeschlossen.
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.27-Briefing: `ROADMAP-v0.27.md` (Verify-UI im Inspector, Material für Landingpage)
- Verify-Strategy: `docs/USDSEAL-VERIFY-STRATEGY.md` (CTA-Ziel)
- ADR-PC6 Bytestream-Hashing (Argument 2 — Reviewer-Schwelle): `~/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`
- Bestehende Landingpages: `landingpage/{deutsch,english}/index.html`
- PR-Schwester-Memory: `pr_project.md` — koordiniert kommende Verteilungs-Welle

---

**Ende v0.27.1-Briefing.** Nach Sprint: Tag `v0.27.1`, Push. Dann v0.27.2 (Reserve-Slot, falls aus Browser-Verifikation oder Landingpage-Test was nachzuschärfen ist). Sonst: v0.27-Welle clean abgeschlossen, v0.28-Konsumer-Sprint kann später beginnen.
