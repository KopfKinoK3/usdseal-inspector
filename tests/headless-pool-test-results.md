# Headless Validator — Pool-Test-Ergebnisse v0.24.1

**Datum:** 2026-05-03  
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
| `tochter_marketing.usdz` | 🟠 orange | SIGNED | 0/1/0 | orange, SIGNED + SCALE_METERS_PER_UNIT_MISSING | ✓ PASS |
| `wrong_first_file.usdz` | 🔴 red | SIGNED | 1/0/0 | red, STRUCTURE_ROOT_LAYER_NOT_FIRST | ✓ PASS |
| `z_up_axis.usdz` | 🟠 orange | SIGNED | 0/1/0 | orange, SCALE_UP_AXIS_NOT_Y | ✓ PASS |

---

## Test-Asset-Sync v0.24.1 (2026-05-03)

### `DIEGOsat_master.usdz` — neue manifest_id

| Feld | Alt (v0.22.x) | Neu (v0.24.1) |
|---|---|---|
| `manifest_id` | `visales-2026-05-fc1e` | `visales-2026-05-bbeb` |
| hull.usda SHA-256 | `7ea5db7b…737a` | `a82ce509…2794` |
| Texturen Browser | 3× Diffuse + 1× unknown | 3× Diffuse + 1× Normal |

**Hintergrund:** CLI-Plan-Chat hat 2026-05-03 die DIEGOsat-Files erneuert. `hull.usda` hat jetzt `normal3f inputs:normal.connect → NormalTex` (mit `sourceColorSpace="raw"`). Channel-Parser erkennt `normal3f`-Type korrekt (type-agnostischer Regex — Phase 5.4 entfallen).

### Neue DIEGOsat-Dateien (außerhalb review-pool, in `../usdz/`)

| File | manifest_id |
|---|---|
| `DIEGOsat_master.usdz` | `visales-2026-05-bbeb` |
| `DIEGOsat_master_marketing.usdz` | `visales-derived-f555` |
| `DIEGOsat_master_CAD_marketing.usdz` | `visales-derived-f26a` |
| `DIEGOsat_master_NDA.usdz` | `visales-derived-95c0` |

### Texture-Status-Erwartungen (Browser, nach v0.24.1)

| File | Texturen | Erwartung |
|---|---|---|
| `DIEGOsat_master.usdz` | 4 | 3× Diffuse, 1× Normal, 0× unused, 0× unknown |
| `DIEGOsat_master_marketing.usdz` | 1 | 1× Diffuse, 0× unused, 0× unknown |

---

## Fixtures-Dokumentation

### `error_explicit.usdz` — Hash-Mismatch-Fixture

Bewusst fehlerhafter Member: `hull/textures/basecolor.png`

| | SHA-256 (gekürzt) |
|---|---|
| Manifest erwartet | `f2591226266ffb9a…` |
| Tatsächliche Bytes | `c93f9a98b1d97ed8…` |

Alle anderen 6 Inventory-Einträge matchen korrekt. Headless-Port und Browser-UI stimmen überein: Inspector erkennt den Mismatch korrekt als INVALID + MANIFEST_HASH_MISMATCH (warn) → Ampel orange.

Diese Datei dient als Regression-Fixture für den MANIFEST_HASH_MISMATCH-Pfad. Nicht reparieren.

### `bare_no_manifest.usdz` — No-Manifest-Fixture

Valides USDZ ohne `credentials/usdseal-manifest.json`. Inspector zeigt State NO_MANIFEST, AR-QL-Validator läuft durch und liefert MANIFEST_MISSING (info). Ampel grün (kein error/warn).

### `wrong_first_file.usdz` — Struktur-Fixture

Erstes ZIP-Member ist kein Top-Level-USD. Triggert `STRUCTURE_ROOT_LAYER_NOT_FIRST` (error). Alle `requires: 'valid_root'`-Regeln werden via Engine-Loop unterdrückt — korrekter Single-Trigger.

---

## Browser-Vergleich

Browser-Inspector (v0.24.1, `http://localhost:8765`) und Headless-Port produzieren identische Ergebnisse für alle 7 Files.

*Hinweis: Cache/↻-Detection ist Browser-only — kein localStorage im Headless-Script. Multi-Drop, Channel-Badges und Texture-Status-Badges sind Browser-only.*

---

## Abdeckungs-Lücken (bekannt, für v0.25+)

- Kein File mit absichtlich falschem Hash via direkter Byte-Manipulation (separat von error_explicit)
- Kein File >25 MB für `STRUCTURE_FILE_SIZE_LIMIT`-Test
- Kein File mit NPOT-Texturen für `TEXTURE_NPOT`-Test
- Kein File mit `.DS_Store` für `STRUCTURE_HIDDEN_FILES`-Test
