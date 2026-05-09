# USDseal Verifizierbarkeit — Strategie-Plan

**Status:** Strategie-Dokument · 2026-05-06
**Anlass:** Duke fordert auf, Verifizierbarkeit auf ein Niveau zu heben, das einem skeptischen Reviewer (Maschinenbau-IT, Compliance, OpenUSD-Community) standhält.
**Kern-Botschaft:** *"Don't trust, verify."* Kein Marketing-Vertrauen, sondern unabhängig nachprüfbares Verfahren.
**Cross-Repo:** Inspector + CLI + übergreifende Doku.

> Dieses Dokument lebt im Inspector-Repo, weil Inspector der **öffentliche** Touchpoint ist. Inhaltlich ist es übergreifend.

---

## 1. Strategische Einordnung

**Aktuelle Außensicht:** Inspector zeigt grünen "SIGNED & versiegelt"-Banner, aber **niemand** kann von außen verifizieren, dass die Signatur deterministisch aus dem USD-Inhalt abgeleitet wurde — und nicht z. B. eine Zufallszahl oder Timestamp-Wrapper ist.

**Das Problem:**
- Marketing-Trust statt verifizierbarer Trust
- Kein "Reproduzierbarkeit"-Beweis öffentlich
- Keine zweite Implementierung zum Cross-Check
- Keine Spec, keine Test-Vektoren, kein Threat Model

**Die Lösung (in 7 Workstreams):**
1. Self-Tests im Inspector (Determinismus + Avalanche sichtbar)
2. Algorithmus-Spec öffentlich
3. Python-Referenz-Verify-Skript
4. Test-Vektoren + CI
5. Landingpage "Verify it yourself"
6. Threat Model dokumentiert
7. Phase 2: Signed Seals (Ed25519, asymmetrisch)

---

## 2. Workstream-Übersicht — Wer macht was

| # | Workstream | Owner | Repo / Ort | Pflicht für Launch | Aufwand |
|---|---|---|---|---|---|
| 1a | **Determinismus-Mechanik** (deterministisches Sealing) | CLI-Plan-Chat | usdseal CLI | ✅ Pflicht | M |
| 1b | **Self-Tests im Inspector-UI** (Determinismus + Avalanche-Visualisierung) | **Inspector-Chat** | usdseal-inspector | ✅ Pflicht | M |
| 2 | **Algorithmus-Spec** (Hash, Feld-Reihenfolge, Floats, Composition, etc.) | CLI-Plan-Chat + übergreifend | `docs/USDSEAL-SPEC-v1.0.md` (CLI-Repo) | ✅ Pflicht | L |
| 3 | **Python-Verify-Referenz-Skript** (~120 Zeilen, ohne `usd-core`) | CLI-Plan-Chat | [github.com/KopfKinoK3/usdseal-verify](https://github.com/KopfKinoK3/usdseal-verify) (public, Apache-2.0) | ✅ DONE | S |
| 4 | **Test-Vektoren** (5–10 USD-Files mit expected signatures + CI) | CLI-Plan-Chat | CLI-Repo `test-vectors/` | ✅ Pflicht | M |
| 5 | **Landingpage "Verify it yourself"** (DE+EN, Code-Snippet, Spec-Link) | **Inspector-Chat** + PR-Chat | usdseal-inspector landingpage | ✅ Pflicht | S |
| 6 | **Threat Model** (was schützt es / was nicht) | CLI-Plan-Chat + übergreifend | `docs/USDSEAL-THREAT-MODEL.md` | ⚠️ vor Launch ratsam | S–M |
| 7 | **Signed Seals (Ed25519/X.509)** | CLI-Plan-Chat (v0.3) | CLI-Repo | 📋 Phase 2 (Ausblick) | L |

**Aufwand-Skala:** S = ≤0.5 Tag · M = 1–2 Tage · L = 3+ Tage

---

## 3. Pflicht-für-Launch vs. Phase 2

### Launch-kritisch (alles vor öffentlicher "Verify-Welle")

```
Pflicht-Reihenfolge:
  1. Algo-Spec schreiben (Workstream 2) — Voraussetzung für 1+3+4+5
  2. Determinismus-Mechanik garantieren im CLI (Workstream 1a)
  3. Python-Verify-Skript implementieren (Workstream 3)
  4. Test-Vektoren erzeugen + CI (Workstream 4)
  5. Self-Tests im Inspector-UI (Workstream 1b)
  6. Landingpage-Sektion "Verify it yourself" (Workstream 5)
  7. Threat Model dokumentieren (Workstream 6)
```

### Phase 2 (nach Launch)

- Signed Seals (Workstream 7) → kommt mit CLI v0.3 (Ed25519-WebCrypto eh schon Inspector-Roadmap-Punkt)
- Erweiterte Audit-Tools (multi-file diff, manifest-history)

---

## 4. Inspector-Sprint-Empfehlungen

Was wir im Inspector-Plan **hier** umsetzen:

### Sprint v0.27 — Verify-UI (vorgeschlagene Umwidmung)

**Aktuell geplant:** v0.27 = Diff-View bei Hash-Mismatch (1-2 Tage)
**Vorschlag-Umwidmung:** v0.27 = Verify-UI-Self-Tests **plus** Diff-View (kombiniert, weil Diff-View thematisch zu Verify gehört)

| Phase | Was |
|---|---|
| Self-Tests-Sektion im Inspector-UI | Determinismus-Check + Avalanche-Visualisierung |
| Visuelle Hamming-Distanz-Anzeige | Bei Avalanche-Test: % der geänderten Bits zeigen |
| Diff-View bei Hash-Mismatch | Original-Geplant — bytes/textur-resolution |
| Verlinkung auf Spec + Python-Verify | Inspector-UI verweist auf CLI-Doku |

**Voraussetzung:** Algo-Spec (Workstream 2) muss vorher fertig sein, sonst weiß Inspector nicht was er testen soll. → **CLI-Plan-Chat muss Spec liefern bevor v0.27 startet.**

**Aufwand:** ~1.5–2 Tage (M)

### Sprint v0.27.1 — Landingpage "Verify it yourself"

**Neue Sektion auf Landingpage** (DE + EN):

```markdown
# Verify it yourself

USDseal-Signaturen sind deterministisch und unabhängig prüfbar.

1. Lade dieses Beispiel-USDZ herunter: [test-vectors/example_001.usdz]
2. Erwartete Signatur: SHA-256: 7edc6407cbade61b...
3. Reproduziere mit Python (~30 Zeilen):
   pip install usd-core
   python verify.py example_001.usdz
4. Vergleiche → muss übereinstimmen.

Vollständige Spec: [USDSEAL-SPEC-v1.0.md]
Python-Verify-Skript: https://github.com/KopfKinoK3/usdseal-verify
Test-Vektoren: [github.com/.../test-vectors/]
```

**Tonalität:** sachlich, kein Marketing — *"Don't trust, verify."*

**Voraussetzung:** Workstreams 2, 3, 4 müssen alle fertig sein.

**Aufwand:** ~0.3–0.5 Tag (S)

---

## 5. CLI-Plan-Chat-Auftrag (nicht hier umzusetzen, aber zu kommunizieren)

Maid Evelyn empfiehlt Duke: bei nächster CLI-Plan-Chat-Session diesen Plan rüberreichen mit folgendem Auftrag:

> **An CLI-Plan-Chat:** Bitte Workstreams 1a, 2, 3, 4, 6 ausarbeiten. Voraussetzung für Inspector-Sprint v0.27 (Verify-UI). Sequenz-Empfehlung:
> 1. Spec-Dokument schreiben (Algorithmus, Felder, Floats, Composition, Refs/Payloads)
> 2. Determinismus-Mechanik im sealing-Code prüfen + ggf. härten (mehrfaches Sealing → byte-identisch)
> 3. Python-Referenz-Skript implementieren
> 4. Test-Vektoren erzeugen (5-10 USD-Files mit expected signatures, JSON-Manifest)
> 5. CI-Pipeline (GitHub Action): bei jedem Commit alle Test-Vektoren reproduzieren
> 6. Threat Model dokumentieren (Was schützt es / was nicht)
>
> Alle Outputs als Markdown-Files im CLI-Repo. Verlinkung im Inspector-Repo erfolgt im v0.27-Sprint hier.

**Cross-Sync-Pattern:** Inspector-Memory verlinkt auf CLI-Repo-Outputs sobald sie da sind. Inspector wartet mit v0.27-Sprint, bis Spec verabschiedet ist.

---

## 6. Konkrete nächste Schritte (Inspector-Seite)

**Reihenfolge bei v0.26-Welle (PDF-Template-Update) UND parallel Verify-Strategy:**

| Schritt | Wer | Wann |
|---|---|---|
| **1.** Diese Strategie-Doku committen + im Memory verankern | Inspector-Chat (jetzt) | sofort |
| **2.** CLI-Plan-Chat über den Plan informieren | Duke | bei nächster CLI-Session |
| **3.** v0.26.0 (Geometrie-Sektion im PDF) wie geplant umsetzen | Inspector-Chat + Code-Chat | parallel |
| **4.** v0.26.1 (Texture-Inventar erweitern) | Inspector-Chat + Code-Chat | nach v0.26.0 |
| **5.** Warten auf CLI-Plan-Chat-Output (Spec, Python-Skript, Test-Vektoren) | beide Chats | abhängig von CLI |
| **6.** v0.27 (Verify-UI mit Self-Tests + Diff-View) | Inspector-Chat + Code-Chat | nachdem Spec fertig |
| **7.** v0.27.1 (Landingpage "Verify it yourself") | Inspector-Chat + PR-Chat | nach v0.27 |
| **8.** ADR-PR2 im PR-Chat — "Don't trust, verify"-Story als Reichweiten-Thema | PR-Chat | parallel zu Launch |

---

## 7. Visualisierung Self-Tests im Inspector-UI

**Determinism-Check** (sichtbar im UI):

```
SELF-TEST · DETERMINISMUS
─────────────────────────────────────────
Datei wurde 2× durch das Sealing geschickt.
Signatur 1: 7edc6407cbade61b2fb5a1f5d997bcaf...
Signatur 2: 7edc6407cbade61b2fb5a1f5d997bcaf...
✅ IDENTISCH — Sealing ist deterministisch
─────────────────────────────────────────
```

**Avalanche-Check** (sichtbar im UI):

```
SELF-TEST · AVALANCHE-EFFEKT
─────────────────────────────────────────
Original-Signatur:  7edc6407cbade61b2fb5a1f5d997bcaf...
Nach 1 Byte-Flip:   3a8b9c2d4e5f6a7b8c9d0e1f2a3b4c5d...
Hamming-Distanz:    127 von 256 Bits geändert (49.6%)
✅ ERWARTET — kleine Änderung → komplett andere Signatur
─────────────────────────────────────────
```

→ Beide Checks rendern in einer eigenen UI-Sektion **unter** dem AR-Quick-Look-Banner und **vor** dem USDseal-Block.

**Optional:** Avalanche-Heatmap (Bit-Change-Distribution) als kleines SVG.

---

## 8. Threat Model — Was USDseal IST und NICHT IST

Vorab-Skizze (CLI-Plan-Chat soll vollständig ausarbeiten):

| Eigenschaft | USDseal aktuell (v1) | USDseal Phase 2 (Signed Seals) | USDseal Phase 3 (mit PKI) |
|---|---|---|---|
| **Integrität** ("nach Sealing nicht verändert") | ✅ Hash-Vergleich | ✅ Hash + Signatur | ✅ Hash + Signatur |
| **Authentizität** ("vom Behaupteten erzeugt") | ❌ ohne PKI | ⚠️ Self-signed | ✅ mit X.509 / CA |
| **Vertraulichkeit** ("Inhalt verborgen") | ❌ kein Verschlüsselung | ❌ | ❌ |
| **Nicht-Abstreitbarkeit** | ❌ | ⚠️ wenn Schlüssel-PKI | ✅ |
| **Timestamp-Authority** | ❌ | ⚠️ optional | ✅ mit RFC 3161 TSA |

**Klare Abgrenzung:**
- **Hash-Seal** = USDseal v1 (heute): nur Integritäts-Check
- **Digital Signature** = USDseal v2 (Phase 2): Integrität + Self-Signed-Authentizität
- **Timestamp Authority** = USDseal v3 (Phase 3): Integrität + Authentizität + Zeitbeweis

Das **muss** klar in der Spec stehen, sonst Reviewer-Risiko: "Ihr nennt das Signatur, aber es ist nur ein Hash."

---

## 9. Spec-Skelett — Bytestream-Hashing (Realität, nicht Vision)

> **Architektur-Entscheidung 2026-05-07 (ADR-PC6):** USDseal v1 hasht **Bytestreams**, nicht semantischen USD-Inhalt. Begründung in Sektion 12. Diese Sektion war früher als Semantic-Hashing-Vision entworfen — die CLI-Realität gibt den Spec-Anker, nicht der Wunsch.

Das **`USDSEAL-SPEC-v1.0.md`** (gepflegt im CLI-Repo) dokumentiert die **3-Layer-Trust-Architektur**:

### Layer 1 — Komponenten-Hash (pro ZIP-Member)

```
für jedes Member im USDZ-Archiv:
  hash = SHA-256(member.bytes_uncompressed)
  → wird in components[].sha256 abgelegt
```

- **Eingabe:** unkomprimierte Bytes des ZIP-Members (nicht der ZIP-Container-Bytes)
- **Algorithmus:** SHA-256, hex-encoded
- **Reihenfolge:** ZIP-Iteration-Order (deterministisch durch Determinismus-Mechanik, siehe Sektion 11)

### Layer 2 — Pre-Seal-Hash (gesamtes USDZ vor Modifikation)

```
pre_seal_hash = SHA-256(usdz_bytes_before_manifest_injection)
→ wird in pre_seal_sha256 abgelegt
```

- **Zweck:** beweist welcher exakte Datei-Stand versiegelt wurde
- **Berechnung:** **vor** Manifest-Injection — nach dem Sealing nicht mehr reproduzierbar ohne Originalfile
- **Wichtig für Verifier:** der Verifier rekonstruiert den Pre-Seal-Stand durch Entfernen des Manifests

### Layer 3 — Manifest-Signatur (COSE_Sign1 / Ed25519)

```
manifest_payload = JSON.dumps({
  manifest_id, spec_version, lineage, components,
  pre_seal_sha256, ...
}, sort_keys=True, separators=(',', ':'))

signature = Ed25519.sign(private_key, manifest_payload)
→ wird in cose_sign1 abgelegt (CBOR-encoded)
```

- **Algorithmus:** Ed25519 (RFC 8032), Container COSE_Sign1 (RFC 9052)
- **Eingabe:** kanonisierter JSON-Body des Manifests (ohne Signatur-Feld selbst)

### Determinismus-Mechanik (Pflicht für reproduzierbare Hashes)

```python
# ZIP-Sealing muss diese Konfiguration nutzen:
zipfile.ZipFile(out, 'w', compression=ZIP_STORED)  # keine Kompression
ZipInfo(filename, date_time=(1980,1,1,0,0,0))     # statisches Datum
# 64-Byte-Alignment für USDC-Sub-Files (USD-Spec)
# JSON: sort_keys=True, separators=(',', ':')     # canonical JSON
```

**Konsequenz:** Mehrfaches Sealing desselben Quell-Files erzeugt **byte-identische** USDZs. Determinismus ist verifizierbar — Self-Test in v0.27 visualisiert es.

### Verify-Schritte (für Python-Referenz-Skript, ~30 Zeilen)

```
1. USDZ öffnen, Manifest extrahieren (.usdseal/manifest.json)
2. Manifest aus USDZ entfernen → rekonstruierter Pre-Seal-Stand
3. SHA-256 über rekonstruierte Bytes  →  vergleich mit pre_seal_sha256
4. Für jeden ZIP-Member: SHA-256 berechnen  →  vergleich mit components[].sha256
5. (Phase 2) Ed25519-Verify(public_key, manifest_payload, cose_sign1)
6. Resultat: integrity_ok = bool, authenticity_ok = bool (Phase 2)
```

### Versionierung

- **Spec v1.0** entspricht Manifest-Schema `spec_version "0.1"` / `"0.2"` (Inspector-Whitelist)
- **Spec v2.0** (Phase 2): Layer 3 wird Pflicht (heute optional)
- Schema-Versionierung folgt CLI-ADR §11.14 (semver-artige Bumps pre-1.0)

---

## 10. Roadmap-Integration

| Inspector-Sprint | Inhalt | Verify-Anteil | Aufwand |
|---|---|---|---|
| v0.26.0 | Geometrie-Sektion im PDF | — | S |
| v0.26.1 | Texture-Inventar erweitern | — | S–M |
| (CLI-Plan-Chat) | Workstreams 1a, 2, 3, 4, 6 | 100% | M–L |
| **v0.27** | Verify-UI Self-Tests + Diff-View (umgewidmet von "nur Diff-View") | 100% | M |
| **v0.27.1** | Landingpage "Verify it yourself" | 100% | S |
| v0.28 | Web-Component-Embed + Pro-Variante | — | M |
| v0.29 | MCP-Server-Wrapper | — | M |
| v0.3 | Ed25519-WebCrypto-Verify (passt zu Workstream 7) | 50% | M |

**Aufwands-Update Bytestream-Entscheidung 2026-05-07:**
- **Workstream 3 (Python-Verify-Skript):** L → **S** (~30 Zeilen statt ~50, weil keine USD-Composition-Resolution nötig — nur ZIP-Iteration + SHA-256)
- **Workstream 2 (Spec):** L → **M** (Bytestream-Spec ist mechanisch beschreibbar, Semantic-Spec wäre Forschungsprojekt gewesen)
- **Reviewer-Schwelle:** drastisch niedriger — jeder Python-Junior versteht ZIP+SHA-256

→ **v0.3 Inspector-Roadmap-Punkt deckt teilweise Phase 2 ab** — CLI muss Signed Seals liefern, Inspector verifiziert sie.

---

## 11. Maid-Evelyn-Empfehlung

1. **Diese Strategie als Doku im Repo.** Erlaubt späterem Reviewer den ganzen Plan zu prüfen.
2. **CLI-Plan-Chat aktivieren** für Workstreams 1a, 2, 3, 4, 6 — das ist der größere Teil und Inspector wartet drauf.
3. **v0.26.0/v0.26.1 erstmal wie geplant** durchziehen (PDF-Template-Update). Verify-Sprint v0.27 startet wenn CLI-Spec da ist.
4. **PR-Chat einbinden** für Punkt 5 (Landingpage) und für die "Don't trust, verify"-Story als Reichweiten-Thema (LinkedIn, Blog, AOUSD-Talk).

---

**Stand:** 2026-05-07 · Cross-Repo-Strategie-Dokument · wird bei jeder Sprint-Welle aktualisiert.

---

## 12. Warum Bytestream-Hashing — und nicht Semantic-Hashing

> Diese Sektion ist der **Audit-Trail** zur Architektur-Entscheidung 2026-05-07. Frühere Entwürfe dieser Strategie-Doku skizzierten Semantic-Hashing (USD-Inhalt canonicalized vor Hash). Die CLI-Realität macht Bytestream-Hashing in 3 Layern. Cross-Repo-Diskussion zwischen Inspector-Plan-Chat und USDseal-CLI-Plan-Chat (Plan-Chat-Übergabe via Memory) führte zur formalen Spec-Anker-Entscheidung. ADR-PC6 in `CLAUDE-Inspector-private.md`. Parallele ADR im CLI-Repo.

**Fünf Argumente, warum Bytestream-Hashing der richtige v1-Anker ist:**

### 1. "What you see is what you sign."

Bytestream-Hash signiert **exakt das, was der User auf der Festplatte hat**. Keine Abstraktion, kein Toolchain-Round-Trip, keine Composition-Resolution-Surprise.

Bei Semantic-Hashing würde dieselbe USDZ — abhängig von der USD-Library-Version, Layer-Reihenfolge, Variant-Default-Selection — unterschiedliche Hashes erzeugen. Reviewer-Frust vorprogrammiert: *"Mein USD-Tool berechnet einen anderen Hash als eures."*

### 2. Reviewer-Schwelle drastisch niedriger.

```python
# Bytestream-Verify:
import zipfile, hashlib, json
z = zipfile.ZipFile('file.usdz')
for member in z.namelist():
    print(hashlib.sha256(z.read(member)).hexdigest())
```

Das versteht **jeder** Python-Junior. Maschinenbau-IT, Compliance-Leute, OpenUSD-Newcomer können das **in 5 Minuten** nachvollziehen. Semantic-Hashing wäre ein Forschungsprojekt — nur Pixar-/Apple-Insider könnten verifizieren.

**USDseal-Trust ist demokratisch nur, wenn die Verify-Mechanik trivial ist.**

### 3. C2PA-Analogie-Konsistenz.

C2PA hasht **Image-Bytes**, nicht semantische Bildbeschreibungen. JPEG-Pixel werden gehasht, nicht "die Szene". Wir positionieren USDseal als "C2PA für USD" — also macht USDseal **dasselbe für USD-Bytes**.

Semantic-Hashing wäre eine Eigenerfindung **ohne** Vorbild im Trust-Ecosystem. Bytestream-Hashing ist **Industry-Standard-Pattern** (PDF-Signing, Code-Signing, Container-Signing — alles bytewise).

### 4. Avalanche-Intuition bleibt erhalten.

```
1 Bit Änderung in einer Texture-Pixel  →  Komponenten-Hash ändert sich  →  Manifest invalid
```

Klassische Hash-Avalanche, im Self-Test (v0.27) **direkt sichtbar**. Bei Semantic-Hashing müsste man "semantisch äquivalente" Änderungen suchen — schwerer zu erklären, schwerer zu testen, schwerer zu zeigen.

### 5. 3-Layer-Trust-Architektur ist robuster als monolithischer Semantic-Hash.

Die CLI macht **drei Layer**:
- Layer 1 (Komponenten-Hash) — granulare Lokalisierung von Manipulationen ("welche Datei wurde geändert?")
- Layer 2 (Pre-Seal-Hash) — atomare Garantie ("der ganze Stand vor Sealing")
- Layer 3 (Manifest-Signatur, Phase 2) — Authentizität ("vom behaupteten Schlüssel signiert")

Ein einziger Semantic-Hash könnte das nicht leisten — er wäre entweder zu grob (kein Diff möglich) oder müsste den Pre-Seal-Stand sowieso bytewise rekonstruieren.

### Trade-off: Was wir aufgeben

**Bytestream-Hashing reagiert auf semantisch belanglose Änderungen** (z. B. Float-Reihenfolge nach Toolchain-Round-Trip, ZIP-Repacking ohne Inhaltsänderung). Das ist **bewusst akzeptiert**:

- Determinismus-Mechanik (ZIP_STORED + statisches Datum + 64-Byte-Alignment + canonical JSON) verhindert die meisten False-Positives **wenn die Toolchain die Mechanik kennt**
- Bei semantisch-äquivalenten-aber-byteweise-unterschiedlichen USDZs liefert Inspector den ehrlichen Befund "INVALID" + Diff-View (v0.27) zeigt **welcher Member** sich geändert hat
- Ein **separates** Tool für semantische Diffs (Backlog-Idee `USDdiff`) gehört in eine andere Roadmap — nicht in v1

### Future Work — wann Semantic-Hashing wieder relevant wird

Falls Toolchain-Roundtrips (Blender → Maya → USDZ) im B2B-Workflow ein Pain-Point werden, wäre eine **separate Spec-Erweiterung** denkbar: `USDseal v2 mit Semantic-Layer als Add-on` (nicht als Ersatz). Bytestream bleibt der Anker, Semantic kommt als zweite Sicht obendrauf.

**Stand 2026-05-07:** kein Bedarf, kein Feature. Backlog-Notiz im CLI-Repo.
