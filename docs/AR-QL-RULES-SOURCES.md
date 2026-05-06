# AR Quick Look — Validator-Regeln: Quellen-Audit

**Stand:** 2026-05-06
**Zweck:** Beleg-Audit für die 20 AR-Quick-Look-Validator-Regeln. Pro Regel eine konkrete Quelle (Apple-Doku, OpenUSD-Spec, WWDC-Session, Forum) mit Zitat oder Begründung. Belegstärke transparent: ✅ solide / ⚠️ indirekt / ❌ nur Praxis.

> Anlass: externer Entwickler will Inspector ausprobieren, viSales braucht Glaubwürdigkeits-Beleg dass die Regeln echt Apple-/Spec-konform sind. Recherche durch Plan-Chat-Agent 2026-05-06.

---

## Wichtiger Disclaimer (zu Beginn)

**Apple publiziert keinen offiziellen USDZ-Validator-Standard.** Diese Regeln kombinieren:
- **OpenUSD-Spec** (USDZ-Format-Definition)
- **Apple Developer-Dokumentation** (AR Quick Look, ARKit, RealityKit)
- **WWDC-Sessions** (USDZ-Authoring-Best-Practices)
- **Apple Developer Forums** (DTS-Antworten)
- **viSales-Praxiserfahrung** mit AR-Quick-Look-Brüchen in B2B-Pipelines

Belegtiefe ist gemischt — das ist nichts Ausgedachtes, aber auch keine reine Apple-Spec-Liste.

---

## Belegstärke im Überblick

| Bewertung | Bedeutung | Anzahl |
|---|---|---|
| ✅ solide | Direkt aus Apple-Doku oder OpenUSD-Spec belegbar | 6 |
| ⚠️ indirekt | WWDC-Session, Apple-Tutorial, Forum-DTS-Antwort | 6 |
| ❌ nur Praxis | viSales-Heuristik / Marketplace-Folklore — kein offizielles Apple-Doc | 6 |
| n/a | USDseal-eigene Regel, kein Apple-Bezug nötig | 2 |

**Korrektur-Bedarf identifiziert:** 3 Regeln (siehe § 4 unten).

---

## 1. STRUKTUR (6 Regeln)

### STRUCTURE_DEFAULT_PRIM_MISSING (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html) + USD Stage Spec
- **Beleg:** USDZ Spec definiert die "Default Layer" als erste USD-Datei im Package, die beim Öffnen mit `SdfLayer::FindOrOpen` zurückgegeben und auf einer `UsdStage` als Root-Layer verwendet wird. `defaultPrim` ist die Stage-Metadata, die diesen Einstieg markiert. Apple's Reality Converter / `usdzconvert` setzen `defaultPrim` automatisch.
- **Confidence:** ⚠️ indirekt — Spec verlangt eine Default-Layer, `defaultPrim` selbst ist USD-Stage-Metadata. AR Quick Look verweigert mehrdeutige Stages in der Praxis.
- **Empfehlung:** Als "AR Quick Look Best Practice" labeln.

### STRUCTURE_ROOT_LAYER_NOT_FIRST (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)
- **Beleg-Zitat:** *"If you wish the package to be presentable on a UsdStage 'as is' [...] then the first file in the package must be a native usd file."*
- **Confidence:** ✅ solide

### STRUCTURE_NESTED_USDZ (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)
- **Beleg:** Die Spec listet erlaubte Inhalte (usda/usdc/usd, image/audio formats); USDZ-in-USDZ ist **nicht** in der Allowlist. Plus: USDZ ist als ZIP ohne Kompression definiert — verschachtelte ZIPs würden das Memory-Mapping-Prinzip brechen.
- **Confidence:** ✅ solide (Negativ-Beleg via Allowlist)

### STRUCTURE_FILE_SIZE_LIMIT (warn, <25 MB)
- **Quelle:** [Apple Developer Forum #118710](https://developer.apple.com/forums/thread/118710) + Marketplace-Praxis
- **Beleg:** Apple-Forum-Antworten von DTS bestätigen *"Quick Look determines that the in-memory size is too large"* — kein API-Hard-Limit. **25 MB ist verbreitete Marketplace-Empfehlung** (AR Code, AR-Plattformen), **nicht von Apple dokumentiert**.
- **Confidence:** ❌ nur Praxis
- **⚠️ Korrektur-Bedarf:** Als "viSales/Marketplace-Empfehlung" labeln, nicht als Apple-Anforderung.

### STRUCTURE_HIDDEN_FILES (info)
- **Quelle:** keine Apple-Doku
- **Begründung:** macOS-Metadaten (`.DS_Store`, `__MACOSX/`) sind keine zulässigen USDZ-Inhalte laut Spec-Allowlist — Hygiene + Größe.
- **Confidence:** ❌ nur Praxis — info-Severity korrekt.

---

## 2. SKALIERUNG (3 Regeln)

### SCALE_UP_AXIS_NOT_Y (warn)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html) (verweist auf USD Stage Up Axis); Apple's `usdzconvert` / Reality Converter exportieren standardmäßig Y-up
- **Beleg:** USDZ Spec verweist auf "preferred conventions" inkl. Up-Axis. Apple-Tooling und ARKit/RealityKit erwarten Y-up; Z-up Modelle werden gekippt dargestellt.
- **Confidence:** ⚠️ indirekt — als AR-Quick-Look-Konvention labeln.

### SCALE_METERS_PER_UNIT_MISSING (warn)
- **Quelle:** [Apple Developer Forum #694706](https://developer.apple.com/forums/thread/694706)
- **Beleg-Zitat:** *"Quick Look will respect the metersPerUnit defined in the USDZ's metadata to determine the scale unit with respect to the real world."* Default 0.01 entspricht USD-Konvention (Centimeter).
- **Confidence:** ✅ solide für Existenz; ⚠️ indirekt für 0.01-Default (USD-Konvention, nicht Apple-Doku).

### SCALE_METERS_PER_UNIT_UNREALISTIC (warn, <0.001 oder >1000)
- **Quelle:** Forum-Threads + [WWDC 2023 #10274](https://developer.apple.com/videos/play/wwdc2023/10274/) "Create 3D models for Quick Look"
- **Beleg:** Modelle mit falschem Scale erscheinen riesig oder unsichtbar. Schwellen <0.001 und >1000 sind heuristisch.
- **Confidence:** ❌ nur Praxis — als Sanity-Check labeln.

---

## 3. TEXTUREN (5 Regeln)

### TEXTURE_FORMAT_UNSUPPORTED (error, Apple supportet nur PNG/JPEG/WebP)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)
- **Beleg:** Spec listet erlaubte Texturformate: **PNG, JPEG, OpenEXR, AVIF**. WebP ist NICHT in der Spec. Apple AR Quick Look produktiv: nur PNG/JPEG, plus HEIC auf visionOS — siehe [variant3d.com/blog/quicklooks-on-ios](https://www.variant3d.com/blog/quicklooks-on-ios).
- **Confidence:** ✅ solide für PNG/JPEG-Pflicht — **aber Regel-Text fehlerhaft**.
- **⚠️ Korrektur-Bedarf (KRITISCH):** Aktuelle Regel sagt "PNG, JPEG, WebP" — das stimmt nicht. **WebP ist NICHT in der USDZ-Spec.** Korrekt: "Apple AR Quick Look: PNG, JPEG (auf visionOS zusätzlich HEIC). USDZ-Spec erlaubt zusätzlich OpenEXR/AVIF, AR Quick Look unterstützt diese aber nicht zuverlässig auf iOS." Plus: in v0.25.4 haben wir AVIF-Detection eingebaut, in v0.25.5 HEIC/KTX2/TIFF/ASTC — diese Regel müsste mit den neuen Format-Detectoren konsistent werden.

### TEXTURE_TOO_LARGE (warn, >4096)
- **Quelle:** [WWDC 2023 #10274](https://developer.apple.com/videos/play/wwdc2023/10274/) + Apple Forums "Triangle count and texture size"
- **Beleg:** Apple empfiehlt **2048×2048** als Target. AR Quick Look downsampelt zur Laufzeit. >4096 wird auf älteren Geräten reduziert/verworfen.
- **Confidence:** ⚠️ indirekt
- **⚠️ Korrektur-Bedarf:** Apple-Empfehlung ist **2048**, nicht 4096. Schwelle korrigieren — ggf. zweistufig: warn >2048, error >4096.

### TEXTURE_NPOT (info)
- **Quelle:** GPU-Standardpraxis, Mipmap-Anforderung
- **Beleg:** Power-of-Two für effizientes Mipmapping ist GPU-Konvention; Apple-Tooling akzeptiert NPOT, Performance leidet.
- **Confidence:** ❌ nur Praxis — info-Severity passt.

### TEXTURE_PATH_ABSOLUTE (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html)
- **Beleg:** Spec verlangt "anchored paths" (./ oder ../) innerhalb USDZ. Absolute Pfade verletzen das Encapsulation-Prinzip. USD-Pfade sind relativ zur referenzierenden Datei.
- **Confidence:** ✅ solide

### TEXTURE_NOT_IN_USDZ (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html) — Encapsulation-Prinzip
- **Beleg:** USDZ ist als self-contained Package definiert; referenzierte Assets müssen im Package sein, sonst bricht Asset-Resolution.
- **Confidence:** ✅ solide

---

## 4. EXTERNAL REFERENCES (2 Regeln)

### EXTERNAL_HTTP_REFERENCE (error)
- **Quelle:** [OpenUSD USDZ Spec](https://openusd.org/release/spec_usdz.html) (Encapsulation), [IANA model/vnd.usdz+zip](https://www.iana.org/assignments/media-types/model/vnd.usdz+zip) Security Considerations
- **Beleg:** Spec erlaubt formal externe Referenzen ("does not forbid"), aber AR Quick Look's `ArDefaultResolver` löst keine HTTP-URLs auf. Apple-Resolver = lokales Filesystem + Package.
- **Confidence:** ⚠️ indirekt — Spec erlaubt theoretisch, AR Quick Look nicht.

### EXTERNAL_FILE_REFERENCE (error)
- **Quelle:** dieselbe
- **Beleg:** Encapsulation-Prinzip — Pfade außerhalb des Package werden vom Resolver nicht aufgelöst.
- **Confidence:** ✅ solide für AR Quick Look-Kontext.

---

## 5. MANIFEST (USDseal-eigen, 2 Regeln — kein Apple-Beleg nötig)

### MANIFEST_MISSING (info)
- **Quelle:** USDseal-Eigenheit
- **Confidence:** n/a — als "USDseal-spezifisch" dokumentiert.

### MANIFEST_HASH_MISMATCH (warn)
- **Quelle:** USDseal-Eigenheit
- **Confidence:** n/a — wie oben.

---

## 6. ANIMATION (1 Regel)

### ANIMATION_TIMECODE_MISSING (warn)
- **Quelle:** [OpenUSD Time and Animated Values](https://openusd.org/dev/user_guides/time_and_animated_values.html)
- **Beleg-Zitat:** *"If timeCodesPerSecond is not set it defaults to 24"* und *"If the start and end time codes are not set there is no playback range specified."* Ohne Timecodes spielt AR Quick Look Animation nicht ab.
- **Confidence:** ✅ solide (OpenUSD-Spec)

---

## 7. PERFORMANCE (2 Regeln)

### PERFORMANCE_MANY_TEXTURES (info, >16)
- **Quelle:** [WWDC 2023 #10274](https://developer.apple.com/videos/play/wwdc2023/10274/) (Texture-Memory-Budget)
- **Beleg:** Kein hartes Limit; viele Texturen erhöhen Memory-Druck, GPU-Texture-Slots auf älteren Geräten begrenzt. Schwelle 16 ist heuristisch.
- **Confidence:** ❌ nur Praxis

### PERFORMANCE_LARGE_INVENTORY (info, >100 Files)
- **Quelle:** keine Apple-Doku
- **Begründung:** Heuristisches Hygiene-Signal; viele Files = ungesäubertes Export-Resultat.
- **Confidence:** ❌ nur Praxis

---

## 8. Korrektur-Befunde — gehören in v0.25.8

### Befund 1 — KRITISCH: WebP in #9 falsch
**Aktuelle Regel:** *"AR Quick Look unterstützt nur PNG, JPEG und (eingeschränkt) WebP für Texturen."*
**Korrekt:** Apple AR Quick Look unterstützt produktiv nur PNG und JPEG. **WebP ist NICHT in der USDZ-Spec.** Auf visionOS zusätzlich HEIC. USDZ-Spec erlaubt zusätzlich OpenEXR und AVIF (formal), AR Quick Look unterstützt diese aber nicht zuverlässig auf iOS.
**Action:** Regel-Text in `index.html` und `AR-QL-RULES.md` umformulieren. Plus: Verhältnis zu v0.25.4 (AVIF-Detection) + v0.25.5 (HEIC/KTX2/TIFF/ASTC-Detection) klären — werden diese Formate jetzt fälschlich als "unsupported" markiert?

### Befund 2: 25-MB-Limit in #4 unbelegt
**Aktuelle Regel:** *"Apple empfiehlt USDZ-Files unter 25 MB für AR Quick Look."*
**Korrekt:** Apple publiziert kein hartes MB-Limit. 25 MB ist Marketplace-Folklore.
**Action:** Als "viSales/Marketplace-Empfehlung" labeln, nicht als Apple-Anforderung.

### Befund 3: TEXTURE_TOO_LARGE Schwelle in #10
**Aktuelle Regel:** *"Textur ist größer als 4096 × 4096 Pixel."*
**Korrekt:** Apple empfiehlt 2048 als Target.
**Action:** Schwelle anpassen — empfohlen zweistufig: warn >2048, error >4096.

---

## 9. Empfehlungen für die Doku

1. **Pro Regel ein Quellen-Block** in `AR-QL-RULES.md` ergänzen (URL + Spec-Klausel oder Apple-Doku-Verweis)
2. **Severity-Tags konsistent erklären:**
   - `error` = Spec-Verletzung (etwas bricht garantiert)
   - `warn` = Apple-Best-Practice-Verstoß (läuft mit Vorbehalt)
   - `info` = viSales-Hygieneempfehlung (Schönheitsfehler)
3. **MANIFEST_*-Regeln** klar als "USDseal-eigene Provenance-Layer" abgrenzen
4. **Disclaimer ganz oben** (siehe Anfang dieser Doku) — Apple hat keinen Validator-Standard, wir kombinieren Quellen.

---

## 10. Zusammenfassung

**Bottom Line:** Die Validator-Regeln sind **nicht ausgedacht**, aber die Belegtiefe ist gemischt:
- ~33% direkt OpenUSD-Spec-belegt
- ~33% indirekt (WWDC, Forum, Tooling-Konventionen)
- ~33% viSales-Praxis-Heuristiken
- 2 Regeln USDseal-eigen

Mit den drei Korrekturen aus § 8 (vor allem WebP-Fix in #9) und sauberer Severity/Source-Annotation ist der Inspector technisch verteidigbar.

---

**Stand:** 2026-05-06 · Recherche durch Plan-Chat-Agent · gehört in v0.25.8-Sprint zur Anwendung.
