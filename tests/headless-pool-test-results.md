# Headless Validator — Pool-Test-Ergebnisse v0.22.2

**Datum:** 2026-05-02  
**Script:** `tests/headless_validator.py`  
**Pool:** `../usdz/review-pool/` (7 Files)  
**Ergebnis: 7/7 PASS**

---

## Einzelergebnisse

| File | Ampel | State | E/W/I | Soll-Erwartung | Verdict |
|---|---|---|---|---|---|
| `DIEGOsat_master.usdz` | 🟢 green | SIGNED | 0/0/0 | green, SIGNED | ✓ PASS |
| `bare_no_manifest.usdz` | 🟢 green | NO_MANIFEST | 0/0/1 | NO_MANIFEST + MANIFEST_MISSING | ✓ PASS |
| `error_explicit.usdz` | 🟠 orange | INVALID | 0/1/0 | orange, INVALID + MANIFEST_HASH_MISMATCH | ✓ PASS |
| `master_three_levels.usdz` | 🟢 green | SIGNED | 0/0/0 | green, SIGNED | ✓ PASS |
| `tochter_marketing.usdz` | 🟠 orange | SIGNED | 0/1/0 | green/orange (metersPerUnit fehlt) | ✓ PASS |
| `wrong_first_file.usdz` | 🔴 red | SIGNED | 1/0/0 | red, STRUCTURE_ROOT_LAYER_NOT_FIRST | ✓ PASS |
| `z_up_axis.usdz` | 🟠 orange | SIGNED | 0/1/0 | orange, SCALE_UP_AXIS_NOT_Y | ✓ PASS |

---

## Fixtures-Dokumentation

### `error_explicit.usdz` — Hash-Mismatch-Fixture

Bewusst fehlerhafter Member: `hull/textures/basecolor.png`

| | SHA-256 (gekürzt) |
|---|---|
| Manifest erwartet | `f2591226266ffb9a…` |
| Tatsächliche Bytes | `c93f9a98b1d97ed8…` |

Alle anderen 6 Inventory-Einträge matchen korrekt. Headless-Port und Browser-UI stimmen überein: Inspector erkennt den Mismatch korrekt als INVALID + MANIFEST_HASH_MISMATCH (warn) → Ampel orange.

**Script-Korrektur v0.22.2:** Die Script-Erwartung stand auf `ampel: 'green'` (Altlast). Korrekt ist `orange/INVALID`. Die Test-Results-Doku war bereits korrekt; nur die Script-Zeile wurde jetzt angepasst.

Diese Datei dient als Regression-Fixture für den MANIFEST_HASH_MISMATCH-Pfad. Nicht reparieren.

### `bare_no_manifest.usdz` — No-Manifest-Fixture

Valides USDZ ohne `credentials/usdseal-manifest.json`. Inspector zeigt State NO_MANIFEST, AR-QL-Validator läuft durch und liefert MANIFEST_MISSING (info). Ampel grün (kein error/warn).

### `wrong_first_file.usdz` — Struktur-Fixture

Erstes ZIP-Member ist kein Top-Level-USD. Triggert `STRUCTURE_ROOT_LAYER_NOT_FIRST` (error). Alle `requires: 'valid_root'`-Regeln werden via Engine-Loop unterdrückt — korrekter Single-Trigger.

---

## Browser-Vergleich

Browser-Inspector (v0.22.2, `file://`) und Headless-Port produzieren identische Ergebnisse für alle 7 Files.

*Hinweis: Cache/↻-Detection ist Browser-only — kein localStorage im Headless-Script. AR-QL-Validator-Logik bleibt identisch.*

---

## Abdeckungs-Lücken (bekannt, für v0.23+)

- Kein File mit absichtlich falschem Hash via direkter Byte-Manipulation (separat von error_explicit)
- Kein File >25 MB für `STRUCTURE_FILE_SIZE_LIMIT`-Test
- Kein File mit NPOT-Texturen für `TEXTURE_NPOT`-Test
- Kein File mit `.DS_Store` für `STRUCTURE_HIDDEN_FILES`-Test
