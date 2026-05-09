# Roadmap v0.27.2 — Layer-2-Feldname-Fix + Soft-Check-Anzeige

**Status:** Vorbereitungs-Dokument · 2026-05-09
**Story-Slot:** *"Pre-Seal-Hash war die ganze Zeit da — wir haben unter dem falschen Namen gesucht."*
**Ziel:** Inspector v0.27 hat in Layer 2 nach `pre_seal_sha256` gesucht und gemeldet *"nicht im Manifest"*. **Der tatsächliche Feldname ist `subject_asset.sha256`** (verifiziert im Independent-Verifier-Code 2026-05-09). Patch korrigiert Feldzugriff und macht Layer 2 als **Soft-Check** sichtbar (wie in Spec §4 / Verifier-README dokumentiert).
**Aufwand:** 0.2–0.3 Tag (XS).

> Korrektur-Patch nach v0.27. Master-Übersicht in `../ROADMAP.md`. Kein neuer Sprint im klassischen Sinne — strukturelle Korrektur eines Phase-5.0-Diagnose-Fehlers.

---

## 1. Befund

**v0.27 Phase-5.0-Diagnose 2026-05-09** hat angenommen, das Pre-Seal-Hash-Feld heißt `pre_seal_sha256`. Real heißt es **`subject_asset.sha256`** im Manifest-Schema. Inspector zeigt Layer 2 deshalb fälschlich als *"nicht im Manifest, geplant für Spec v0.3"* — obwohl das Feld da ist.

**Quelle der Korrektur:** Independent-Verifier-Code (`~/Documents/Claude/USDseal/usdseal-verify/usdseal_verify.py`), Zeile 104:

```python
pre_seal_expected = manifest.get("subject_asset", {}).get("sha256", "")
```

Plus README-Block "What does it check?":

| Layer | Check |
|---|---|
| 1 — Component hashes | SHA-256 each ZIP member vs `asset_inventory[].sha256` (HARD-FAIL) |
| 2 — Pre-Seal hash | SHA-256 of current USDZ vs `subject_asset.sha256` — **informational only (Soft-Check, by spec design — see Spec §4)** |
| 3 — Manifest signature | Ed25519 / COSE_Sign1 over canonicalized manifest (HARD-FAIL) |

**Befund-Schwere:** Mittel. Inspector lügt nicht — die Anzeige *"nicht im Manifest"* ist sachlich falsch, aber nicht trust-gefährdend. Bevor PR-Welle startet aber zu fixen, weil:
- Independent Verifier zeigt Layer 2 als Soft-Check mit Wert
- Inspector zeigt Layer 2 als "fehlt"
- Reviewer sieht Inkonsistenz zwischen den beiden Implementierungen → Vertrauensverlust

**ADR-PC4-Lehre:** Phase-5.0-Diagnose hätte das echte Manifest **lesen** müssen, nicht aus dem Briefing-Text das Feldnamen-Pattern übernehmen. *"Code-Realität-Verifikation vor Spec-Vision"* (ADR-PC6) gilt genau hier.

---

## 2. Phase 5.0 — Diagnose

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "pre_seal_sha256\|subject_asset" index.html | head -10
```

→ Lokalisiert wo Inspector heute den (falschen) Feldnamen liest. Plus: prüfen wie das Manifest-Schema-Objekt im Inspector heißt (vermutlich `manifest.subject_asset.sha256` analog zum Verifier).

**Test-Manifest:**

```bash
python3 -c "
import zipfile, json
with zipfile.ZipFile('../usdz/DIEGOsat_master.usdz') as z:
    m = json.loads(z.read('credentials/usdseal-manifest.json'))
print('subject_asset.sha256:', m.get('subject_asset', {}).get('sha256', 'NOT FOUND')[:16])
print('Top-level keys:', list(m.keys()))
"
```

→ Bestätigt: `subject_asset.sha256` ist da, Wert ist ein 64-stelliger Hex-String (SHA-256).

---

## 3. Scope

### 3.1 Feldname-Fix in Layer-2-Anzeige

**Im Code:** `manifest.pre_seal_sha256` → `manifest.subject_asset?.sha256`. Defensiv mit Optional-Chaining wegen alter Manifest-Versionen die das Feld evtl. nicht haben.

### 3.2 Layer-2-Anzeige als Soft-Check umstellen

**Vorher (v0.27):**

```
Layer 2: Pre-Seal-Hash
  pre_seal_sha256: nicht im Manifest, geplant für Spec v0.3
```

**Nachher (v0.27.2):**

```
Layer 2: Pre-Seal-Hash (Soft-Check)
  Erwartet (Manifest):  7edc6407cbade61b…
  Aktuell (Datei):      a82ce509944e49e4…
  ⚠ unterscheidet sich (erwartet — Sealing modifiziert das ZIP)
```

**Erklärungs-Text** unter dem Block:

*"Layer 2 ist im Spec §4 als Soft-Check designed: das Manifest wird nach dem Sealing in die USDZ injiziert, deshalb unterscheidet sich der aktuelle File-Hash vom Pre-Seal-Hash. Der Wert dokumentiert den Stand vor Sealing für Provenance-Zwecke. Hard-Verify passiert in Layer 1 (Komponenten-Hashes) und Layer 3 (Manifest-Signatur)."*

(EN-Variante analog.)

### 3.3 Was Inspector live machen kann

**Aktueller File-Hash** kann im Browser via `crypto.subtle.digest('SHA-256', fileBytes)` berechnet werden — Inspector hat den File-Bytes-Stream, das ist machbar.

→ Layer 2 zeigt **beide Werte** (Manifest + aktuell) und markiert Differenz als erwartet (Soft-Check).

### 3.4 PDF-Anteil

PDF-VERIFY-Sektion analog updaten: Layer-2-Zeile zeigt beide Hashes mit Soft-Check-Hinweis.

### 3.5 ADR-39 (v0.27) ergänzen

ADR-39 sagte *"Phase 5.0-Befund: pre_seal_sha256 nicht im Manifest"* — das ist sachlich falsch. ADR-39-Update mit Korrektur-Hinweis + Verlinkung auf ADR-41.

### 3.6 Was NICHT in v0.27.2

- **Kein Layer-3-Verify** — bleibt Phase 2 (v0.3, WebCrypto-Ed25519)
- **Keine Header-Validierung** (Algorithm-Confusion-Schutz wie im Verifier) — kommt mit Layer-3-Verify in v0.3
- **Kein Re-Zipping zur Pre-Seal-Hash-Verifikation** — Soft-Check zeigt informativ beide Werte ohne sie matchen zu müssen
- **Keine Manifest-Schema-Whitelist-Erweiterung** — `subject_asset.sha256` war schon im Schema, nur Inspector hat's nicht gelesen

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| `usdseal_verify.py` | als Code-Referenz | Zeile 104 zeigt korrekten Feldzugriff |
| usdseal-verify README | als Doku-Referenz | "What it checks"-Tabelle Zeile 86–88 |
| Bestehende Layer-2-Logik in Inspector | minimal-Patch | nur Feldzugriff + Anzeige-Struktur |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.27 stable released | ✓ Tag online seit 2026-05-09 |
| 2 | Independent-Verifier-Code als Korrektur-Quelle | ✓ vorhanden in `~/Documents/Claude/USDseal/usdseal-verify/` |
| 3 | DIEGOsat-Pool-Files als Test-Beleg | ✓ |
| 4 | Manifest-Schema kennt `subject_asset.sha256` | ✓ verifiziert via Verifier-Code |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | grep `pre_seal_sha256` + `subject_asset` in index.html, Manifest-Struktur via Python live verifizieren |
| **5.1 Feldname-Fix + Anzeige** | 0.1 Tag | `manifest.subject_asset?.sha256` lesen, Anzeige umstellen auf Soft-Check-Layout (beide Werte + Erklärungs-Text) |
| **5.2 WebCrypto-Live-Hash für aktuellen File** | 0.05 Tag | `crypto.subtle.digest('SHA-256', fileBytes)` aufrufen, Wert anzeigen |
| **5.3 PDF-Anteil updaten** | 0.05 Tag | Layer-2-Zeile in PDF-VERIFY-Sektion analog |
| **5.4 i18n** | 0.02 Tag | DE+EN für Soft-Check-Erklärungs-Texte (~3 Keys) |
| **5.5 Browser-Verifikation** | 0.05 Tag | DIEGOsat in Chrome+Safari, Layer 2 zeigt beide Hashes + Differenz |
| **5.6 Headless-Pool** | 0.05 Tag | 18/18 PASS bleibt |
| **5.7 ADR-41** | inkludiert | Template § 9 |
| **5.8 ADR-39 (v0.27) Korrektur-Annotation** | 0.02 Tag | "siehe ADR-41 für Korrektur"-Vermerk |
| **5.9 INSPECTOR_VERSION + Snapshot + Tag** | 0.05 Tag | INSPECTOR_VERSION='0.27.2', Snapshot, Tag, Push |

**Total: 0.2–0.3 Tag (XS).**

---

## 7. Strategischer Hebel

v0.27.2 ist **Konsistenz-Patch vor PR-Welle**:

1. **Inspector + Independent Verifier zeigen dieselbe Realität** — Reviewer sieht keine Diskrepanz mehr zwischen den beiden Implementierungen
2. **Layer 2 wird ehrlich Soft-Check** — Erklärung im UI + PDF, dass die Differenz **erwartet** ist (nicht "kaputt")
3. **PR-Story bleibt sauber** — *"Don't trust, verify"* funktioniert nur wenn beide Implementierungen konsistent sind
4. **ADR-PC4-Lehre dokumentiert** — Phase-5.0-Diagnose muss Code-Realität verifizieren, nicht Briefing-Annahmen übernehmen
5. **Kein neuer Architektur-Anker-Bruch** — pure Anzeige-Korrektur, ADR-PC5 hält

---

## 8. Konkrete Pre-v0.27.2-Steps

Keine — alle Vorbedingungen erfüllt.

---

## 9. Decision-Log-Template

```markdown
### ADR-41 Layer-2-Feldname-Korrektur + Soft-Check-Anzeige — 2026-05-XX

**Kontext:** Inspector v0.27 Phase-5.0-Diagnose 2026-05-09 hat angenommen, das Pre-Seal-Hash-Feld heißt `pre_seal_sha256`. Korrektur via Independent-Verifier-Code-Inspektion 2026-05-09: tatsächlicher Feldname ist `subject_asset.sha256`. Inspector zeigte Layer 2 deshalb fälschlich als "nicht im Manifest, geplant für Spec v0.3" — der Wert ist seit Spec v1.0 da. Plus: Layer 2 ist im Spec §4 explizit als **Soft-Check** designed (Manifest wird nach Sealing in die USDZ injiziert, deshalb unterscheidet sich aktueller File-Hash vom Pre-Seal-Hash — das ist die Soll-Mechanik).

**Entscheidung:** Inspector liest `manifest.subject_asset?.sha256` mit Optional-Chaining. Layer-2-Anzeige zeigt beide Werte (Manifest-Erwartet + aktuell-via-WebCrypto) mit Soft-Check-Erklärung. PDF-VERIFY-Sektion analog updated. ADR-39 (v0.27) bekommt Korrektur-Annotation. Manifest-Schema bleibt unverändert — kein Cross-Repo-Auftrag an CLI nötig (Verifier zeigt: das Feld war die ganze Zeit korrekt benannt).

**Konsequenz:** Inspector + Independent Verifier zeigen dieselbe Realität. Layer 2 ehrlich Soft-Check mit Erklärung. PR-Welle kann starten ohne Implementierungs-Diskrepanz. ADR-PC4-Lehre dokumentiert: Phase-5.0-Diagnose muss Code-Realität verifizieren, nicht Briefing-Annahmen. Kein Architektur-Anker berührt.
```

---

## 10. Quellen / Referenz-Links

- Master-Roadmap: `../ROADMAP.md`
- v0.27-Briefing: `ROADMAP-v0.27.md` (Verify-UI mit fehlerhaftem Feldzugriff)
- ADR-PC4 Verification before Hypothesis: `~/Documents/Claude/USDseal/CLAUDE-Inspector-private.md`
- Independent Verifier Code: `~/Documents/Claude/USDseal/usdseal-verify/usdseal_verify.py` (Zeile 104)
- Independent Verifier README "What it checks": `~/Documents/Claude/USDseal/usdseal-verify/README.md`
- USDSEAL-VERIFY-STRATEGY.md Sektion 9 (Bytestream-3-Layer-Spec): `docs/USDSEAL-VERIFY-STRATEGY.md`

---

**Ende v0.27.2-Briefing.** Nach Sprint: INSPECTOR_VERSION='0.27.2', Snapshot, Tag `v0.27.2`, Push. Dann ist Inspector + Verifier konsistent — PR-Welle kann starten.
