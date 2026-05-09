# Roadmap v0.27 — Verify-UI Self-Tests + Diff-View

**Status:** Vorbereitungs-Dokument · 2026-05-09
**Story-Slot:** *"Trust wird verifizierbar — 3-Layer-Architektur live im UI sichtbar, Diff-View bei Hash-Mismatch, Avalanche-Live-Demo"*
**Ziel:** Den USDseal-Trust-Block im Inspector um eine **VERIFY**-Sektion erweitern, die die 3-Layer-Bytestream-Architektur (ADR-PC6) sichtbar macht — plus Diff-View bei Mismatch + Live-Avalanche-Demo + Verlinkungen auf alle 5 CLI-Outputs.
**Aufwand:** ~1.0–1.3 Tag (M).

> Letzter Sprint vor v0.28 (Konsumer-Pattern-Sprint mit Single-File-Inspector als Kern). Master-Übersicht in `../ROADMAP.md`. Voraussetzungen: CLI-Plan-Chat-Outputs (Spec, Verifier, Threat Model, Determinismus-Audit, Test-Vektoren) ausgeliefert seit 2026-05-07.

---

## 1. Befund

**v0.26.x hat den PDF-Audit-Report material-vollständig gemacht** (Geometrie + Texturen + Großfile-Tabelle, ADR-35–38). Trust-Block bleibt aber **opak**: "Signiert & versiegelt" als Banner, Counter `Tracked / Mismatch / Extra / Missing / Structure` — ohne dass der User die **3-Layer-Architektur** sieht oder selber nachvollziehen kann.

**Was fehlt heute im UI:**

1. **Komponenten-Hash-Tabelle** — Inspector berechnet sie intern, zeigt aber nur Counter. Bei Mismatch sieht man nur "1 Mismatch", nicht **welche** Komponente.
2. **Pre-Seal-Hash-Anzeige** — `pre_seal_sha256` aus dem Manifest wird nicht visualisiert.
3. **Manifest-Signatur-Hinweis** — COSE_Sign1/Ed25519-Vorhandensein wird nicht ehrlich kommuniziert (Verify ist v0.3-Roadmap).
4. **Avalanche-Live-Demo** — Klassische Hash-Lawine ist im Inspector demonstrierbar, fehlt aber.
5. **Verlinkungen** — auf CLI-Spec, Verifier-Skript, Threat Model, Determinism-Audit fehlen komplett.

**v0.27 schließt diese Lücken** — macht Trust verifizierbar statt deklarativ. Story für v0.27.1-Landingpage: *"Don't trust, verify."*

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "Signiert & versiegelt\|Mismatch\|usdsealCheck\|pre_seal_sha256" index.html | head -30
grep -n "renderUsdsealSection\|trust-block\|provenance" index.html | head -20
grep -n "components\[\]\|sha256.*member\|JSZip" index.html | head -20
```

→ Lokalisiert:
1. Wo der USDseal-Trust-Block heute gerendert wird (UI + PDF)
2. Wie `_currentReport.usdsealCheck` aussieht — welche Hash-Daten schon da sind, was neu rein muss
3. Ob Inspector bereits `pre_seal_sha256` ausm Manifest extrahiert (vermutlich ja, nur nicht angezeigt)
4. Wie Komponenten-Member-Hashes berechnet werden (Worker-Pool seit v0.22.1)

**Konsistenz-Check:** Wenn Pre-Seal-Hash-**Verify** (also: ZIP ohne Manifest rekonstruieren + SHA-256 berechnen + matchen) im Browser zu tricky ist (deterministisches Re-Zipping mit ZIP_STORED + ZipInfo-Default-Datetime + 64-Byte-Alignment), dann wandert es in **Phase 2** und v0.27 zeigt nur den Wert **aus dem Manifest** an mit Hinweis *"Pre-Seal-Hash-Verify ab v0.3 (Browser-Re-Zipping deterministisch noch zu klären)"*. ADR-PC4-konform: nicht spekulieren, Realität checken.

---

## 3. Scope

### 3.1 Neue Sub-Sektion "VERIFY · 3-LAYER-TRUST"

**Position:** innerhalb des USDseal-Trust-Blocks, **nach** "Signiert & versiegelt"-Banner und **vor** Counter-Tabelle. Sub-Block mit oranger Akzentleiste analog v0.25.6-Pattern.

**Layout (UI):**

```
USDSEAL · TRUST & PROVENANCE
─────────────────────────────────────────
✓ Signiert & versiegelt
  COSE_Sign1 / Ed25519 — Manifest kryptographisch gesiegelt

  ┌─────────────────────────────────────────┐
  │ VERIFY · 3-LAYER-TRUST                  │
  │ ─────────────────────────────────────── │
  │ Layer 1: Komponenten-Hashes             │
  │   23 Komponenten · 23 OK · 0 Mismatch   │
  │   [Tabelle anzeigen ▾]                  │
  │                                         │
  │ Layer 2: Pre-Seal-Hash                  │
  │   pre_seal_sha256: 7edc6407cbade…       │
  │   ⚠ Verify ab v0.3 (Browser-Re-Zipping) │
  │                                         │
  │ Layer 3: Manifest-Signatur              │
  │   COSE_Sign1 / Ed25519 vorhanden        │
  │   ⚠ Signatur-Verify ab v0.3             │
  │                                         │
  │ [Avalanche-Live-Demo ▸]                 │
  │                                         │
  │ Don't trust, verify:                    │
  │   • Spec v1.0 (USDseal-CLI)            │
  │   • Independent Verifier (usdseal-verify)│
  │   • Threat Model                        │
  │   • Determinism Audit                   │
  └─────────────────────────────────────────┘

Counter (bestehend):
  Tracked: 4 | Mismatch: 0 | Extra: 0 | Missing: 0 | Structure: 2
```

### 3.2 Layer 1 — Komponenten-Hash-Tabelle

**Klick auf [Tabelle anzeigen ▾]:** klappt eine Tabelle aus mit allen ZIP-Members und ihren Hashes:

```
Komponente                        Erwartet          Aktuell           Status
textures/foo.png                  abc12345…         abc12345…         ✓ OK
textures/bar.png                  789def01…         789def01…         ✓ OK
…
```

Bei `mismatch > 0`: betroffene Zeile hat Status ❌ und Hash-Werte sind farbig hervorgehoben.

**Threshold-Pattern wie v0.26.2:** bei `>20 Komponenten` kompakte Tabelle, sonst Block-Style — konsistent mit Texture-Sektion.

### 3.3 Layer 2 — Pre-Seal-Hash-Anzeige

Wert aus `manifest.pre_seal_sha256` anzeigen. **Verify-Status:** ehrlich als *"Phase 2 (v0.3)"* markieren, mit Erklärung dass Browser-Re-Zipping deterministisch noch zu klären ist (ADR-PC5: Architektur-Anker bei Polyfills).

**Falls Phase 5.0 zeigt dass Re-Zipping mit JSZip-Optionen (`compression: 'STORE'`, manuelle ZipInfo) deterministisch machbar ist:** Verify hier doch live einbauen. Ggf. als Sub-Story v0.27.x später nachreichen.

### 3.4 Layer 3 — Manifest-Signatur-Hinweis

Anzeigen ob `cose_sign1` im Manifest vorhanden ist. **Status:** *"Signatur-Verify ab v0.3 (Ed25519/WebCrypto-API)"* — ehrlich, nicht versprechen was Inspector heute nicht kann.

### 3.5 Avalanche-Live-Demo

Button **[Avalanche-Live-Demo ▸]** — bei Klick:
1. Inspector wählt **erste Texture-Komponente** (z. B. `textures/material0_basecolor.png`)
2. Liest die Bytes
3. **Flippt das letzte Bit** des Bytes-Arrays
4. Berechnet SHA-256 über die modifizierten Bytes
5. Zeigt **Original-Hash** und **modifizierten Hash** nebeneinander
6. Berechnet **Hamming-Distanz** (z. B. *"127 von 256 Bits geändert (49.6%)"*)
7. Erklärung: *"1 Bit geändert → komplett anderer Hash. Das ist die Avalanche-Eigenschaft von SHA-256. Genau deshalb erkennt USDseal jede Manipulation."*

→ Klein, live, demonstrativ. Funktioniert auch bei unsignierten Files (man flippt ja nur eine beliebige Komponente).

### 3.6 Verlinkungen auf CLI-Outputs

Im Sub-Block unten *"Don't trust, verify:"*:

| Link-Text | Ziel |
|---|---|
| Spec v1.0 (USDseal-CLI) | `https://github.com/KopfKinoK3/usdseal-cli/blob/main/docs/USDSEAL-SPEC-v1.0.md` *(privates Repo — vorerst Inspector-eigene Verify-Strategy verlinken)* |
| Independent Verifier | `https://github.com/KopfKinoK3/usdseal-verify` *(falls public, sonst auf Inspector-Doku)* |
| Threat Model | analog |
| Determinism Audit | analog |
| Inspector Verify-Strategy | `docs/USDSEAL-VERIFY-STRATEGY.md` *(Inspector-Repo, public)* |

**Wichtig:** CLI-Repo ist privat. v0.27.1-Landingpage muss klären welche Links extern publik werden. Für v0.27-UI: Verify-Strategy.md als Hauptlink, andere als "demnächst öffentlich" markieren.

### 3.7 Diff-View bei Hash-Mismatch (Bestandteil Layer-1-Tabelle)

Wenn `mismatch > 0`: Tabelle automatisch ausgeklappt, Mismatch-Zeilen oben einsortiert. Sub-Hint: *"X Komponenten wurden nach dem Sealing modifiziert. Welche, siehst du in der Tabelle."*

Test-Beleg: `error_explicit.usdz` (Pool-Datei mit künstlichem Mismatch).

### 3.8 i18n DE+EN

~15 neue Keys:
- Sub-Block-Header (`verify_3layer_title`)
- Layer-Labels (`layer1_components`, `layer2_preseal`, `layer3_signature`)
- Status-Texte (`verify_phase2_v03`, `verify_browser_rezip`)
- Avalanche-Demo-Texte (`avalanche_btn`, `avalanche_explain`, `hamming_label`)
- Link-Labels (`link_spec`, `link_verifier`, `link_threat`, `link_determinism`, `link_strategy`)
- Tabellen-Header für Layer-1 (`tbl_component`, `tbl_expected`, `tbl_actual`, `tbl_status`)

### 3.9 PDF-Anteil

Der **PDF-Audit-Report** kriegt eine kompakte VERIFY-Sektion (NICHT die volle UI-Tabelle, das wäre zu viel). Inhalt:
- 3-Layer-Status-Zeilen (Layer 1: X/Y OK, Layer 2: Pre-Seal-Hash anzeigen, Layer 3: Signatur vorhanden)
- Bei Mismatch: betroffene Komponenten als kompakte Tabelle
- Verlinkungen-Block (URLs ausgeschrieben)
- Avalanche-Demo nicht im PDF (live-only)

Position im PDF: **innerhalb USDseal-Block**, vor Asset-Inventory.

### 3.10 Was NICHT in v0.27

- **Kein Ed25519-Signatur-Verify** — das ist v0.3 (WebCrypto-API)
- **Keine eigene Sealing-Logik** — Inspector ist Verifier, nicht Sealer
- **Kein Determinismus-Live-Test** — Inspector sealt nicht, Determinismus ist CLI-/Verifier-Skill (USDSEAL-DETERMINISM-AUDIT.md)
- **Keine usd-wasm/Three.js/Polyfills** — ADR-PC5 hält
- **Kein Pre-Seal-Hash-Verify** — wenn Phase 5.0 nicht zeigt dass JSZip deterministisch re-zippen kann, dann v0.3 oder Sub-Sprint

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt, JSZip + jsPDF unverändert |
| `usdsealCheck`-Daten | vorhanden | wird im neuen Renderer wiederverwendet |
| WebCrypto SubtleCrypto.digest() | im Browser nativ | für Avalanche-Demo SHA-256-Berechnung |
| CLI-Spec v1.0 | public via Inspector-Verlinkung | privates Repo, Sichtbarkeit für v0.27.1 klären |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.26.2 stable + Patch-Bug fix | ✓ Tag online seit 2026-05-09, Commit `af794c4` |
| 2 | CLI-Plan-Chat-Spec ausgeliefert | ✓ seit 2026-05-07 (5 Workstreams complete) |
| 3 | USDSEAL-VERIFY-STRATEGY.md aktualisiert auf Bytestream-Realität | ✓ seit 2026-05-07 (Sektion 9 + 12) |
| 4 | ADR-PC6 dokumentiert | ✓ in CLAUDE-Inspector-private.md |
| 5 | Test-Pool: signierte (DIEGOsat) + unsignierte (Frankfurt) + Mismatch (error_explicit) | ✓ |

**5 von 5 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep `usdsealCheck`-Datenstruktur, Pre-Seal-Hash-Vorhandensein prüfen, JSZip-Re-Zipping-Mechanik checken |
| **5.1 Sub-Sektion VERIFY UI bauen** | 0.3 Tag | Sub-Block in Trust-Sektion, Layout, Akzentleiste |
| **5.2 Layer-1-Tabelle (Komponenten-Hash)** | 0.2 Tag | Tabelle mit Threshold-Pattern (>20), Diff-Highlighting bei Mismatch |
| **5.3 Layer-2/Layer-3-Anzeige** | 0.05 Tag | Pre-Seal-Hash + Signatur-Hinweis, Phase-2-Status ehrlich |
| **5.4 Avalanche-Live-Demo** | 0.2 Tag | Button + Bit-Flip-Logik + WebCrypto-Hash + Hamming-Distanz-Berechnung + UI |
| **5.5 Verlinkungen + CLI-Output-URLs** | 0.05 Tag | DE+EN, Status-Markierungen "demnächst public" für privates CLI-Repo |
| **5.6 PDF-Anteil** | 0.15 Tag | Kompakte VERIFY-Sektion im PDF (nicht die volle UI-Tabelle) |
| **5.7 i18n DE+EN** | 0.05 Tag | ~15 neue Keys |
| **5.8 Browser-Verifikation** | 0.1 Tag | DIEGOsat (signiert) + Frankfurt (unsigniert) + error_explicit (Mismatch). Chrome + Safari (Chrome-MCP wieder verbunden? sonst manuell) |
| **5.9 Headless-Pool** | 0.05 Tag | 18/18 PASS — kein Validator-Touch erwartet |
| **5.10 README + CHANGELOG** | 0.05 Tag | "Verify-UI Self-Tests + Diff-View + Avalanche-Live-Demo" |
| **5.11 ADR-39** | inkludiert | Template § 9 |
| **5.12 INSPECTOR_VERSION + Snapshot + Tag** | 0.05 Tag | INSPECTOR_VERSION='0.27', Snapshot v0.27-snapshot.html, Tag v0.27, Push |

**Total: 1.0–1.3 Tag (M).**

---

## 7. Strategischer Hebel

v0.27 ist **Trust-Layer-Sichtbarkeits-Sprint** — und damit **strategisch der wichtigste Sprint vor v0.28**:

1. **Trust wird verifizierbar** — Inspector sagt nicht mehr nur "vertrau mir, ist signiert", sondern zeigt **wie** man es selbst nachprüft. *"Don't trust, verify."* wird zur sichtbaren Story.
2. **3-Layer-Architektur (ADR-PC6) wird konkret** — die Bytestream-Hashing-Spec von 2026-05-07 wird im UI greifbar, nicht nur in der Spec-Doku.
3. **Avalanche-Demo ist Konferenz-Material** — AOUSD-Talk-Slide-Material *"so funktioniert Hash-Integrität, hier live im Browser"*.
4. **Diff-View macht Forensik möglich** — bei Mismatch sieht man **welche** Komponente modifiziert wurde. B2B-Audit-USP.
5. **PR-Story für v0.27.1-Landingpage** — Verify-Sektion + Code-Snippet + CLI-Verifier verlinkt = *"reproduzierbar in 5 Zeilen Python"*.
6. **Letzter saubere Single-File-Sprint vor v0.28-Konsumer-Welle** — danach kommen Web-Component-Boilerplate, MCP-Server-Wrapper, Pro-Variante. v0.27 muss **Single-File-USP-perfekt** sein.

---

## 8. Konkrete Pre-v0.27-Steps

Keine — alle Vorbedingungen erfüllt.

---

## 9. Decision-Log-Template

```markdown
### ADR-39 Verify-UI Self-Tests + Diff-View + Avalanche-Demo — 2026-05-XX

**Kontext:** v0.26.x hat PDF-Audit-Report material-vollständig gemacht. USDSEAL-VERIFY-STRATEGY.md (2026-05-07) und CLI-Spec v1.0 (Bytestream-Hashing, ADR-PC6) liegen vor. Inspector zeigte Trust bislang als opakes "Signiert & versiegelt"-Banner — die 3-Layer-Architektur war im UI unsichtbar.

**Entscheidung:** Sub-Sektion "VERIFY · 3-LAYER-TRUST" innerhalb USDseal-Trust-Block. Layer 1 (Komponenten-Hash-Tabelle mit Diff-View bei Mismatch, Threshold-Pattern wie v0.26.2), Layer 2 (Pre-Seal-Hash-Anzeige, Verify als Phase 2 markiert wenn JSZip-Re-Zipping nicht deterministisch im Browser), Layer 3 (Signatur-Vorhandensein mit Phase-2-Hinweis). Plus Avalanche-Live-Demo (Bit-Flip + WebCrypto-SHA-256 + Hamming-Distanz). Plus Verlinkungen auf CLI-Spec, Verifier-Skript, Threat Model, Determinism Audit. PDF kriegt kompakte VERIFY-Sektion (nicht volle Tabelle).

**Konsequenz:** Trust wird verifizierbar im UI — *"Don't trust, verify."* wird sichtbare Story. Avalanche-Live-Demo ist Konferenz-/AOUSD-Material. Diff-View ermöglicht Forensik bei Mismatch. PR-Vorbereitung für v0.27.1-Landingpage. Letzter Single-File-Sprint vor v0.28-Konsumer-Welle clean abgeschlossen.
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- Verify-Strategie: `docs/USDSEAL-VERIFY-STRATEGY.md` (Inspector-Repo, public)
- ADR-PC6 Bytestream-Hashing: `~/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`
- CLI-Spec v1.0 (privat): `usdseal-cli/docs/USDSEAL-SPEC-v1.0.md`
- Independent Verifier: `~/Documents/Claude/USDseal/usdseal-verify/`
- Threat Model: `usdseal-cli/docs/USDSEAL-THREAT-MODEL.md`
- Determinism Audit: `usdseal-cli/docs/USDSEAL-DETERMINISM-AUDIT.md`
- v0.26.2-Briefing: `ROADMAP-v0.26.2.md` (Threshold-Pattern als Referenz für Layer-1-Tabelle)

---

**Ende v0.27-Briefing.** Nach Sprint: INSPECTOR_VERSION='0.27' setzen, Snapshot, Tag, Push. Dann v0.27.1 (Landingpage "Verify it yourself") — kann direkt anschließen, hat alle Inhalte aus v0.27-UI als Material.
