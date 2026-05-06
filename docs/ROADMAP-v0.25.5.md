# Roadmap v0.25.5 — Texture-Spec-Vollständigkeit (HEIC/KTX2/TIFF/ASTC)

**Status:** Vorbereitungs-Dokument · 2026-05-05
**Story-Slot:** *"OpenUSD-Texture-Spec komplett abgedeckt"*
**Ziel:** Die vier verbleibenden OpenUSD-USDZ-erlaubten Texture-Formate (HEIC, KTX2, TIFF, ASTC) Magic-Bytes-detektieren — Spec-Vollständigkeit für AOUSD-Talk.
**Aufwand:** 0.5–0.7 Tag.

> Patch-Sprint nach v0.25.4.1. Master-Übersicht in `../ROADMAP.md`.

---

## 1. Befund

**Aus dem Real-World-Sweep 2026-05-05** (`tests/real-world-2026-05-05.md` § 4):

| Format | Vorkommen in 6 Kunden-Files | v0.25.4-Status |
|---|---|---|
| PNG / JPG / JPEG | 6/6 | ✅ voll abgedeckt |
| AVIF | 1/6 (Frankfurt 15×) | ✅ Magic-Bytes + Native-Preview (v0.25.4) |
| HEIC | 0/6 | ❌ kein Detection |
| KTX2 | 0/6 | ❌ kein Detection (Extension-Stub aus v0.22) |
| TIFF | 0/6 | ❌ kein Detection |
| ASTC | 0/6 | ❌ kein Detection |

**Strategischer Punkt:** Kein Real-World-Use-Case in Duke's Kunden-Pool — aber **OpenUSD-USDZ-Spec listet alle vier als erlaubt** ([openusd.org/release/spec_usdz.html#file-types](https://openusd.org/release/spec_usdz.html#file-types)). Mit AVIF-Detection (v0.25.4) hat Inspector den Architektur-Pattern für Magic-Bytes-Format-Detection. Die fehlenden vier sind 1:1-Kopien davon → Spec-Vollständigkeit in einem schnellen Sprint.

**Talk-Slide-Wert für AOUSD:** *"USDseal Inspector — der erste Web-USDZ-Inspector mit kompletter OpenUSD-Spec-Texture-Coverage."*

---

## 2. Phase 5.0 — Diagnose vor Fix (ADR-PC4 strikt)

**Pflicht vor Code-Change.** Code-Chat soll als **erste Aktion**:

### Schritt 1 — AVIF-Pattern als Vorlage prüfen

```bash
cd ~/Documents/Claude/USDseal/usdseal-inspector
grep -n "readAvifSignature\|AVIF\|analyzeTexture" index.html | head -20
```

→ Zeigt wie AVIF-Reader strukturiert ist (v0.25.4-Output). Die vier neuen Reader folgen demselben Pattern.

### Schritt 2 — Test-Strategie verifizieren

**Test-Pool-Status:** `ls ../usdz/review-pool/` zeigt 13 Files, **keine** mit HEIC/KTX2/TIFF/ASTC-Texturen (Sweep-bestätigt).

→ **Test-Strategie: synthetische Magic-Bytes-Streams** im Headless-Pool. Kein Real-File nötig — wir testen nur Detection-Logik, nicht Texture-Decoding.

```python
# Beispiel synthetisch im Headless-Test
KTX2_MAGIC = bytes([0xAB, 0x4B, 0x54, 0x58, 0x20, 0x32, 0x30, 0xBB, 0x0D, 0x0A, 0x1A, 0x0A])
TIFF_LE_MAGIC = bytes([0x49, 0x49, 0x2A, 0x00])
ASTC_MAGIC = bytes([0x13, 0xAB, 0xA1, 0x5C])
HEIC_MAGIC = bytes([0,0,0,0x20,  0x66,0x74,0x79,0x70,  0x68,0x65,0x69,0x63])  # ftyp heic
```

---

## 3. Scope

### 3.1 Vier neue Magic-Bytes-Reader (1:1 nach AVIF-Vorlage)

```javascript
// HEIC (ISO BMFF mit heic/heix/mif1/msf1 brand)
function readHeicSignature(data) {
  if (data.length < 12) return null;
  if (data[4] !== 0x66 || data[5] !== 0x74 || data[6] !== 0x79 || data[7] !== 0x70) return null;
  const brand = String.fromCharCode(data[8], data[9], data[10], data[11]);
  if (['heic', 'heix', 'mif1', 'msf1'].includes(brand)) {
    return { format: 'HEIC' };
  }
  return null;
}

// KTX2 (12-Byte Magic Identifier)
function readKtx2Signature(data) {
  if (data.length < 12) return null;
  const expected = [0xAB, 0x4B, 0x54, 0x58, 0x20, 0x32, 0x30, 0xBB, 0x0D, 0x0A, 0x1A, 0x0A];
  for (let i = 0; i < 12; i++) {
    if (data[i] !== expected[i]) return null;
  }
  return { format: 'KTX2' };
}

// TIFF (Little-endian II*\0 oder Big-endian MM\0*)
function readTiffSignature(data) {
  if (data.length < 4) return null;
  if (data[0] === 0x49 && data[1] === 0x49 && data[2] === 0x2A && data[3] === 0x00) {
    return { format: 'TIFF', endian: 'LE' };
  }
  if (data[0] === 0x4D && data[1] === 0x4D && data[2] === 0x00 && data[3] === 0x2A) {
    return { format: 'TIFF', endian: 'BE' };
  }
  return null;
}

// ASTC (4-Byte Magic)
function readAstcSignature(data) {
  if (data.length < 4) return null;
  if (data[0] === 0x13 && data[1] === 0xAB && data[2] === 0xA1 && data[3] === 0x5C) {
    return { format: 'ASTC' };
  }
  return null;
}
```

### 3.2 Routing-Anpassung in `analyzeTexture()`

Routing-Reihenfolge analog AVIF:
- Wenn Extension-Match ODER Magic-Bytes-Match → Format-Routing
- Reihenfolge in Code: PNG → JPEG → WebP → KTX2 → AVIF → **HEIC** → **TIFF** → **ASTC** → Extension-Fallback

### 3.3 Preview-Strategie

| Format | Strategie |
|---|---|
| **HEIC** | Native-Preview-Versuch via Blob-URL + `<img>` (analog AVIF). **Nur Safari** rendert HEIC nativ. Bei `img.onerror` (Chrome): Fallback Format-Label `"HEIC (kein Browser-Preview in Chrome)"` |
| **KTX2** | Format-Label only: `"KTX2 (GPU-Texture, kein Browser-Preview)"` — bisheriges KTX-Verhalten beibehalten |
| **TIFF** | Format-Label only: `"TIFF (kein nativer Browser-Support)"` |
| **ASTC** | Format-Label only: `"ASTC (GPU-compressed, kein Browser-Preview)"` |

**Wichtig:** Kein Polyfill für KTX2/TIFF/ASTC — Single-File-Anker bleibt, ADR-PC5 verstärkt.

### 3.4 Was bleibt unverändert

- AR-Quick-Look-Validator-Logik
- Texture-Modal-UI
- Channel-Erkennung (v0.24, basiert auf USD-Pfaden, nicht auf Texture-Daten)
- Headless-Pool-Setup für PNG/JPG/WebP/AVIF (bereits getestet)

### 3.5 Was NICHT in v0.25.5

- Echte HEIC/KTX2/TIFF/ASTC-Test-Files (nicht im Pool, kein Use-Case bei Duke)
- Channel-Erkennung pro Format (gehört zu v0.24-Logik, ist Format-agnostisch)
- KTX2/TIFF/ASTC-Decode-Polyfills (Single-File-Anker)

---

## 4. Externe Quellen

| Komponente | Status | Bemerkung |
|---|---|---|
| Keine neuen Deps | — | Single-File-Anker bleibt |
| Browser-Native HEIC | nur Safari (16+) | Chrome rendert nicht — Fallback aktiv |

---

## 5. Vorbedingungen

| # | Vorbedingung | Status |
|---|---|---|
| 1 | Inspector v0.25.4.1 stabil released | ✓ Tag online seit 2026-05-05, Commit `03799f0` |
| 2 | AVIF-Reader-Pattern als Vorlage | ✓ in v0.25.4 etabliert |
| 3 | Test-Strategie: synthetische Magic-Bytes | ✓ kein Real-File nötig |
| 4 | Headless-Pool-Erweiterungs-Pattern | ✓ wie in v0.25.4 |

**4 von 4 grün.**

---

## 6. Phasen-Schätzung

| Phase | Dauer | Was passiert |
|---|---|---|
| **5.0 Diagnose** | 0.05 Tag | AVIF-Pattern grep, Test-Strategie verifizieren |
| **5.1 Vier Reader-Funktionen** | 0.15 Tag | HEIC, KTX2, TIFF, ASTC nach Code-Snippet |
| **5.2 Routing-Anpassung** | 0.05 Tag | `analyzeTexture()`-Cases ergänzen, Format-Labels DE+EN |
| **5.3 HEIC-Preview-Versuch** | 0.05 Tag | Native-Preview-Logik wie AVIF, Fallback-Pfad |
| **5.4 Headless-Tests synthetisch** | 0.1 Tag | 4 neue Test-Cases mit synthetischen Magic-Bytes-Streams |
| **5.5 Smoke-Test Browser** | 0.05 Tag | Frankfurt + DIEGOsat in Safari → Banner + AVIF unverändert (nichts kaputt) |
| **5.6 Headless-Pool** | 0.05 Tag | 13/13 PASS bleibt + 4 synthetische Tests grün = 17 Cases |
| **5.7 README + CHANGELOG** | 0.05 Tag | "Spec-Vollständigkeit erreicht" |
| **5.8 ADR-31 dokumentieren** | inkludiert | Template § 9 |
| **5.9 Snapshot + Tag** | 0.05 Tag | Snapshot v0.25.5, Tag, Push |

**Total: 0.5–0.6 Tag.** Mini-Sprint, perfekt für Abend-Slot.

---

## 7. Strategischer Hebel

v0.25.5 ist Spec-Vollständigkeits-Sprint mit drei Hebeln:

1. **AOUSD-Talk-Slide:** "Erster Web-USDZ-Inspector mit kompletter OpenUSD-Spec-Texture-Coverage." Differenzierung gegenüber needle-tools, ponahoum, usdz-viewer.net — die unterstützen meist nur PNG/JPG.
2. **Architektur-Bestätigung:** AVIF-Pattern (v0.25.4) skaliert auf weitere Formate ohne Polyfill-Bloat. ADR-PC5 viertes Mal in der Praxis bewährt.
3. **Future-Proof:** Wenn morgen ein Kunde ein KTX2-USDZ liefert, ist Inspector ready. Kein Hotfix nötig.

---

## 8. Konkrete Pre-v0.25.5-Steps

Keine — alle Vorbedingungen erfüllt. AVIF-Pattern aus v0.25.4 ist im Code, Test-Strategie ist klar.

---

## 9. Decision-Log-Template

```markdown
### ADR-31 OpenUSD-Texture-Spec-Vollständigkeit — 2026-05-XX

**Kontext:** Real-World-Sweep 2026-05-05 zeigte: AVIF im Kunden-Pool vorhanden (1/6), HEIC/KTX2/TIFF/ASTC nicht. Aber OpenUSD-USDZ-Spec listet alle vier als erlaubt. Inspector hatte sie nicht detektiert.

**Entscheidung:**
- Magic-Bytes-Reader für HEIC/KTX2/TIFF/ASTC nach AVIF-Pattern
- HEIC mit Native-Preview-Versuch (nur Safari)
- KTX2/TIFF/ASTC nur Format-Label, kein Polyfill (Single-File-Anker)
- Test-Strategie: synthetische Magic-Bytes-Streams (kein Real-File nötig)

**Konsequenz:** Inspector hat komplette OpenUSD-Spec-Texture-Coverage. AOUSD-Talk-Slide-Material. Bundle-Wachstum minimal (~50 Zeilen). Single-File-Anker bestätigt — keine Polyfill-Schulden für GPU-Formate.
```

---

## 10. Quellen / Referenz-Links

### Interne Dokumente

- Master-Roadmap: `../ROADMAP.md`
- Vorgänger: `ROADMAP-v0.25.4.md` (AVIF-Pattern + Severity-Recal)
- Diagnose-Quelle: `../tests/real-world-2026-05-05.md` (§ 4 Format-Reality-Check)
- AR-QL-Regeln: `AR-QL-RULES.md`

### Externe Specs

- [OpenUSD USDZ — File Types](https://openusd.org/release/spec_usdz.html#file-types) — Quelle der Format-Liste
- [HEIF/HEIC ISO Base Media File Format](https://nokiatech.github.io/heif/technical.html) — Magic-Bytes
- [KTX 2.0 Specification](https://registry.khronos.org/KTX/specs/2.0/ktxspec.v2.html) — 12-Byte Magic
- [TIFF Revision 6.0](https://www.adobe.io/open/standards/TIFF.html) — LE/BE Magic
- [ASTC File Format](https://github.com/ARM-software/astc-encoder/blob/main/Docs/FileFormat.md) — 4-Byte Magic

---

**Ende v0.25.5-Briefing.** Nach Sprint: Snapshot, Tag `v0.25.5`, Push.
