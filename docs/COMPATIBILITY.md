# Compatibility Matrix

Welche Manifest-Versionen versteht welcher Inspector?

USDseal Inspector spiegelt das Manifest-Schema des USDseal CLI. Beide bumpen `spec_version` semver-artig, solange wir pre-1.0 sind. Inspector folgt der CLI-Schema-Disziplin (siehe CLI-ADR §11.14).

---

## 1. Versions-Matrix

| Inspector-Version | Unterstützte `spec_version` | Lineage-Panel | Provenance-Steps | AR-QL-Validator | Re-Import-Detection |
|---|---|---|---|---|---|
| v0.2              | `0.1`                        | ✗ (ignoriert) | `sealed` (basic) | — | — |
| v0.21             | `0.1`, `0.2`                 | ✓ Single-View | `sealed`, `merged`, `derived` (mit Step-Badges + Notes) | — | ✗ |
| v0.22              | `0.1`, `0.2`                | unverändert | unverändert | ✓ Ampel + 20 Regeln, DE only (Toggle deaktiviert via W-2) | ✗ |
| **v0.22.1** (aktuell) | `0.1`, `0.2`              | unverändert | unverändert | ✓ Ampel + 21 Regeln, DE+EN, Sortierung Severity→Category→ID, Web-Worker-Hashing | ✗ (siehe §3) |
| v0.22.2 (Patch nach v0.22.1) | `0.1`, `0.2`         | ✓ + Cross-Manifest-Cache | unverändert | unverändert | ✓ (localStorage + Multi-Drop) |
| v0.3 (geplant)    | `0.1`, `0.2`, `0.3`          | ✓ + C2PA-Block | + `signed_c2pa` | unverändert | unverändert |

---

## 2. Übergangs-Toleranz für `0.1`-Manifeste mit `lineage`-Block

**Kontext:** Während CLI-Subprojekt SP-11 (`usdseal migrate`) noch nicht ausgerollt ist, existieren in Bestandsfixtures Manifeste mit `spec_version = "0.1"`, die jedoch bereits einen `lineage`-Block tragen — z. B. das DIEGOsat-Test-Asset-Paar.

**Inspector-Verhalten in v0.21:**

- Inspector behandelt `0.1`-Manifeste mit `lineage`-Key wie Quasi-`0.2`.
- Lineage-Panel + erweiterte Provenance werden gerendert.
- Grauer Hint oberhalb des Manifest-Blocks: *"Manifest stammt aus pre-bump CLI v0.2 — empfohlen: `usdseal migrate` ausführen."*

Diese Übergangs-Logik entfällt in Inspector v0.22.2, sobald die Migrate-Welle durch ist und alle Bestandsfixtures auf `"0.2"` gehoben sind.

---

## 3. Re-Import-Detection — bewusst nicht in v0.21

**Was ist Re-Import?** Master-Manifest enthält `import_history[]`-Eintrag, der auf eine Tochter zeigt, die wiederum den Master als `parent_manifest_id` führt. Beispiel: DIEGOsat-Master importiert hull-Assets aus `DIEGOsat_master_marketing` (eine eigene Tochter).

**Warum nicht in v0.21?** Aus einem einzelnen Manifest allein nicht erkennbar — der Inspector lädt v0.21 nur ein USDZ zur Zeit. Detection braucht entweder Cross-Manifest-Cache oder Multi-File-Drop.

**Roadmap:**
- v0.21 zeigt `import_history[]` und `parent_manifest_id` als reine Single-View-Information. Kein ↻-Marker.
- v0.22 ist für den AR-Quick-Look-Validator reserviert (eigener Story-Slot der Master-Roadmap) — Re-Import-Detection ist dort nicht Thema.
- **v0.22.2** (Patch-Release nach v0.22) fügt localStorage-basierten Cross-Manifest-Cache hinzu (datenschutz-konform — keine Daten verlassen den Rechner) plus optionalen Multi-File-Drop. ↻-Marker erscheint dort, wo Cross-Reference auflösbar ist. Siehe `ROADMAP-v0.22.2.md`.

Siehe ADR-2 in `ROADMAP-v0.21.md` — überarbeitet 2026-05-01.

---

## 4. Render-Regeln pro `spec_version`

| Feld                              | `spec_version: "0.1"`                                      | `spec_version: "0.2"`                       |
|-----------------------------------|------------------------------------------------------------|---------------------------------------------|
| `lineage`-Block                   | nicht erwartet — wenn vorhanden: Übergangs-Toleranz + Hint | Pflicht — wenn fehlt: Manifest-Integrity-Warning |
| `provenance_chain[].step ∈ {sealed}` | erwartet                                                   | erwartet                                    |
| `provenance_chain[].step ∈ {merged, derived}` | nicht erwartet (toleriert, gerendert)             | erwartet                                    |
| `import_history[]` (im Master)    | nicht erwartet (toleriert wenn `lineage` da)               | erwartet wenn `lineage.role = "master"`     |
| `parent_manifest_id` (in Tochter) | nicht erwartet (toleriert wenn `lineage` da)               | erwartet wenn `lineage.role = "derived"`    |

---

## 5. Verhalten bei unbekannter `spec_version`

**Inspector ist Read-Only.** Anders als das CLI (`verify` verweigert) reagiert Inspector weicher:

- Gelber Banner: *"Manifest-Version X.Y · Inspector versteht 0.1, 0.2"*
- Render wird trotzdem versucht (best-effort, keine Crashes).
- Lineage-Panel wird ausgeblendet, wenn `lineage`-Felder unbekannte Struktur haben.

Forward-Compat ohne Hard-Fails.

---

## 6. Cross-Verweis CLI ↔ Inspector

Wenn das CLI Schema-Disziplin verfeinert (z. B. PATCH-Bumps für sub-strukturelle Änderungen), zieht Inspector-Roadmap nach. Whitelist-Erweiterung = neue Render-Funktion + neuer Eintrag in dieser Tabelle, kein Refactoring der Bestandslogik.

**Quelle der Wahrheit:** CLI-ADR §11.14 in der CLI-Tech-Spec.

---

**Stand:** 2026-05-01 · Inspector v0.21 in Vorbereitung
