# Roadmap v0.27.3 — Landingpage Verifier-Link scharf

**Status:** Vorbereitungs-Dokument · 2026-05-09
**Story-Slot:** *"usdseal-verify ist public — Landingpage zeigt jetzt den echten Link statt 'demnächst public auf GitHub'."*
**Ziel:** Landingpage `#verify`-Block (DE + EN) — den `usdseal-verify`-Repo-Hinweis durch einen echten Link auf `github.com/KopfKinoK3/usdseal-verify` ersetzen. Plus optional zweiter CTA-Button. Plus CHANGELOG-Eintrag.
**Aufwand:** 0.1–0.2 Tag (XS).

> Folge-Patch zu v0.27.2 (Inspector-Layer-2-Fix). Master-Übersicht in `../ROADMAP.md`. Kein Inspector-Code-Touch — pure HTML-Edits + CHANGELOG.

---

## 1. Befund

**v0.27.1-Landingpage** (released 2026-05-09 morgens) verlinkt im `#verify`-Block den Independent Verifier mit dem Hinweis *"demnächst public auf GitHub"* (DE) bzw. *"coming soon on GitHub"* (EN), weil das Repo zu dem Zeitpunkt privat war.

**Status 2026-05-09 nachmittags:** Repo ist live unter **`github.com/KopfKinoK3/usdseal-verify`** (Apache-2.0, gepusht von CLI-Plan-Chat-Build-Chat). Der Landingpage-Hinweis ist veraltet — echter Link gehört rein.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector/landingpage
grep -n "demnächst public\|coming soon\|Independent Verifier\|usdseal-verify" deutsch/index.html
grep -n "Independent Verifier\|coming soon\|usdseal-verify" english/index.html
```

→ Lokalisiert die exakten Stellen im `#verify`-Block beider Sprach-Versionen.

---

## 3. Scope

### 3.1 Landingpage Deutsch (`landingpage/deutsch/index.html`)

**Im `#verify`-Block — Suchstring (oder ähnlich):**

> *"Independent Verifier (Python, ~120 Zeilen) macht den vollen Manifest-Roundtrip — demnächst public auf GitHub."*

**Ersetzen durch:**

> *"Independent Verifier (Python, ~120 Zeilen) macht den vollen Manifest-Roundtrip — [github.com/KopfKinoK3/usdseal-verify](https://github.com/KopfKinoK3/usdseal-verify)"*

HTML:
```html
Independent Verifier (Python, ~120 Zeilen) macht den vollen Manifest-Roundtrip —
<a href="https://github.com/KopfKinoK3/usdseal-verify"
   target="_blank" rel="noopener">github.com/KopfKinoK3/usdseal-verify</a>
```

**Optional:** zweiter CTA-Button neben *"Verify-Strategy ansehen"*:

```html
<a href="https://github.com/KopfKinoK3/usdseal-verify"
   class="btn btn-secondary"
   target="_blank" rel="noopener">Independent Verifier auf GitHub</a>
```

(Klasse `btn-secondary` oder welche Klasse auf der Landingpage für sekundäre Buttons verwendet wird — Phase 5.0 prüft.)

### 3.2 Landingpage English (`landingpage/english/index.html`)

Analog zu DE. EN-Suchstring (vermutlich): *"Independent Verifier (Python, ~120 lines) handles the full manifest roundtrip — coming soon on GitHub."*

Ersetzen durch:

> *"Independent Verifier (Python, ~120 lines) handles the full manifest roundtrip — [github.com/KopfKinoK3/usdseal-verify](https://github.com/KopfKinoK3/usdseal-verify)"*

Optional: zweiter CTA-Button *"View Independent Verifier"*.

### 3.3 CHANGELOG-Eintrag

Unter v0.27.3 (oder als Patch-Eintrag unter v0.27.1, je nach CHANGELOG-Konvention im Repo):

> *"Landingpage Verify-Block: usdseal-verify-Repo public unter github.com/KopfKinoK3/usdseal-verify (Apache-2.0), Hinweis 'demnächst public' durch echten Link ersetzt."*

### 3.4 Was NICHT in v0.27.3

- **Kein Inspector-Code-Touch** — Layer-2-Fix läuft separat in v0.27.2
- **Keine inhaltliche Änderung** der Verify-Sektion — nur Link-Update
- **Kein neuer CSS-Block** — bestehende Klassen wiederverwenden für optionalen 2. CTA

---

## 4. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | usdseal-verify-Repo public | ✓ seit 2026-05-09 |
| 2 | Inspector v0.27.1 Landingpage als Basis | ✓ |
| 3 | Drei Inspector-Doku-Verweise (USDSEAL-VERIFY-STRATEGY.md + ROADMAP-v0.27.1.md) bereits aktualisiert | ✓ durch Inspector-Plan-Chat 2026-05-09 |

**3 von 3 grün.**

---

## 5. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.02 Tag | grep `#verify`-Block-Inhalt in beiden Sprach-Versionen, CSS-Klassen für Sekundär-Button checken |
| **5.1 Deutsch-Link scharf machen** | 0.03 Tag | Inline-Link ersetzen, optional 2. CTA-Button |
| **5.2 English-Link scharf machen** | 0.03 Tag | analog |
| **5.3 CHANGELOG-Eintrag** | 0.02 Tag | unter v0.27.3 |
| **5.4 Cross-Browser-Verifikation** | 0.03 Tag | DE + EN in Chrome+Safari, Link öffnet Repo (200 OK), Anker `#verify` weiterhin direkt erreichbar |
| **5.5 ADR-42** | 0.02 Tag | Template § 7 |
| **5.6 Tag + Push** | 0.02 Tag | Tag `v0.27.3`, Push. **INSPECTOR_VERSION bleibt — Landingpage-only-Change.** |

**Total: 0.1–0.2 Tag (XS).**

---

## 6. Strategischer Hebel

v0.27.3 ist **PR-Welle-Enabler**:

1. **Landingpage-CTA funktioniert** — Reviewer/Lead klickt *"Independent Verifier"* → 200 OK statt 404
2. **Story rund** — *"5 Zeilen Python für Layer 1 + 120 Zeilen Python für vollen Roundtrip — beides public"* funktioniert ohne Pflaster
3. **Konsistenz mit Inspector v0.27.2** — sobald beide Patches durch sind, sind Inspector-UI + Landingpage + Verifier-Repo + Inspector-Doku **alle synchron**

---

## 7. Decision-Log-Template

```markdown
### ADR-42 Landingpage Verifier-Link scharf gestellt — 2026-05-XX

**Kontext:** v0.27.1 (released 2026-05-09 morgens) hatte den Independent-Verifier-Link auf der Landingpage als "demnächst public auf GitHub" / "coming soon on GitHub" markiert, weil das Repo privat war. Push erfolgt 2026-05-09 nachmittags durch CLI-Plan-Chat-Build-Chat unter `github.com/KopfKinoK3/usdseal-verify` (Apache-2.0).

**Entscheidung:** Landingpage `#verify`-Block (DE + EN) — Hinweis durch echten Link ersetzt. Inline-Anker auf den Repo plus optional zweiter CTA-Button. CSS-Klassen wiederverwendet, kein neues File. Kein Inspector-Code-Touch (Layer-2-Fix läuft separat in v0.27.2).

**Konsequenz:** PR-Welle kann mit funktionierendem CTA laufen. Story rund: Inspector-UI live + Landingpage-Link scharf + Verifier-Repo public + Spec via VERIFY-STRATEGY (public). Auditor-Pfad geschlossen.
```

---

## 8. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.27.1-Briefing: `ROADMAP-v0.27.1.md` (Verifier-Link als "demnächst public" eingebaut)
- v0.27.2-Briefing: `ROADMAP-v0.27.2.md` (Inspector-Layer-2-Fix, läuft parallel)
- Verifier-Repo: `https://github.com/KopfKinoK3/usdseal-verify`

---

**Ende v0.27.3-Briefing.** Nach Sprint: Tag `v0.27.3`, Push. Sobald v0.27.2 + v0.27.3 beide durch sind: PR-Welle-Start frei.
