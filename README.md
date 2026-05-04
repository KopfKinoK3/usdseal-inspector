# USDseal Inspector

**Browser-based USDZ file analyzer — no upload, no server, no installation.**

Drop any USDZ into your browser and see exactly what's inside. AR Quick Look diagnosis with plain-language fix hints, asset inventory, USD metadata, texture thumbnails, and full Provenance / Lineage panels for USDseal-sealed files. Everything runs locally — no data leaves your machine.

→ **[Try it live](https://kopfkinok3.github.io/usdseal-inspector/)** (GitHub Pages)

---

## What it does — for any USDZ

You don't need USDseal to use this tool. Drop **any** USDZ file in and the Inspector analyzes it locally:

| Feature | Description |
|---|---|
| **AR Quick Look traffic-light** | Green / orange / red diagnosis with 20 rules in 7 categories (structure, scale, textures, external references, manifest, animation, performance). Plain-language fix hints per finding (DE / EN). *(v0.22)* |
| **State detection** | SIGNED / DRAFT / INVALID / NO_MANIFEST as a colored banner |
| **USD metadata** | `defaultPrim`, `upAxis`, `metersPerUnit`, custom layer data |
| **Asset inventory** | Filenames, sizes, SHA-256 — see exactly what's inside the ZIP |
| **Texture analysis** | PNG / JPEG / WebP — dimensions, format, live thumbnails. Click any thumbnail for full-size modal with download. PBR channel badges (Diffuse / Normal / Roughness / Metallic / Emissive / Occlusion / Opacity / Displacement / Subsurface / Clearcoat). Status-aware: `used` (channel badge), `unused` (yellow-gray, orphaned in ZIP), `unknown` (red-gray, alias gap) *(v0.24 / v0.24.1)* |
| **Geometry stats** | 10 asset metrics: Geom-Count (Mesh + Sphere + Cube + procedural types), Poly-Count (tri-fan), Vertex-Count, Material-Count, Prim-Count, Joint/Bone-Count, UV-Sets, Subdivision-Level, Time-Range, FPS. USDA: full parsing across all sublayers. USDC: `?` (binary, not extractable). Procedural prims (Sphere/Cube): `proc`. *(v0.25)* |
| **3D Preview & iOS AR test** | iOS Safari: `<model-viewer>` with AR Quick Look button (lazy CDN load, ~150 KB). Desktop/Android: step-by-step guide to get the USDZ onto iPhone via AirDrop, iCloud Drive, or Mail — tap the file and AR Quick Look launches automatically. *(v0.25 / v0.25.2)* |
| **Parallel hashing** | Web Workers + loading indicator for large USDZ (50+ MB) *(v0.22.1)* |
| **DE / EN** | Full bilingual UI — Browser locale by default, persisted in localStorage *(v0.22.1)* |

**Use case for OpenUSD beginners and AR / Web 3D users:**
After a talk on OpenUSD or AR Quick Look, drop your file in. *"Why is my USDZ rejected by AR Quick Look?"* — the validator tells you, with a fix hint per problem.

---

## Plus — for USDseal-sealed files

If a USDZ has been processed with the **USDseal CLI** (a separate companion tool that adds cryptographically signed provenance metadata), the Inspector unlocks additional verification panels:

| Feature | Description |
|---|---|
| **SHA-256 verification** | Each ZIP member is hashed and compared to the manifest |
| **Lineage panel** | Master ⬇ (`import_history[]`) / Derived ⬆ (`parent_manifest_id`) — shows where assets come from |
| **Provenance timeline** | sealed / merged / derived steps with notes *(v0.21)* |
| **Re-import detection ↻** | Cross-manifest cache (localStorage) detects re-import cycles between USDZ files *(v0.22.2)* |
| **Spec-version compatibility** | Graceful handling of `0.1` and `0.2` manifests with migration hints *(v0.21)* |
| **Signature details** | Ed25519 public key, timestamp, algorithm |

These features are read-only — the Inspector verifies, but does not seal. **Sealing requires the USDseal CLI**, which is a separate tool currently in private development.

---

## What is USDseal?

USDseal is a companion CLI tool that adds **cryptographically signed provenance metadata** to USDZ files (Ed25519 / COSE_Sign1, C2PA-compatible). It writes a `credentials/usdseal-manifest.json` into the ZIP and signs the asset hashes — so any inspector (this one) can later verify whether the file was modified after sealing.

**The Inspector is the public verification half.** Without the CLI to seal files, the lineage and provenance features are dormant — but the universal USDZ-inspection features (AR Quick Look, metadata, textures, asset inventory) work for any file.

---

## Origin

The first version of this tool was built on the evening of April 27, 2026 — after day one of the [XR Expo Stuttgart](https://www.messe-stuttgart.de/xrexpo/), and the night before a talk on OpenUSD by Gerhard Schröder, the developer of this tool. The idea was simple: after explaining provenance and trust for 3D assets on stage, attendees should be able to open a USDZ file and see exactly what was inside — right then, in the browser, with no install. v0.1 was a proof of concept. v0.2 shipped the next day.

---

## Usage

**Option A — GitHub Pages (no installation):**
Open [kopfkinok3.github.io/usdseal-inspector](https://kopfkinok3.github.io/usdseal-inspector/) in any modern browser.

**Option B — Download:**
Download `index.html` and open it locally. No web server needed.

**Option C — Embed (iframe):**
```html
<iframe src="https://kopfkinok3.github.io/usdseal-inspector/"
        width="100%" height="720" style="border:none;">
</iframe>
```

---

## Roadmap

**Released**

- **v0.1** *(2026-04-27, internal)* — Proof of concept: JSZip-based USDZ parsing, first manifest detection
- **v0.2** *(2026-04-28)* — State detection, SHA-256 verification, USD metadata, texture analysis with thumbnails, provenance chain, signature details
- **v0.22** *(2026-05-02)* — AR Quick Look traffic-light validator (20 rules, DE/EN), Lineage panel (Master/Derived), Provenance timeline, spec-version compatibility
- **v0.22.1** *(2026-05-02)* — Full EN translation, regex hardening, parallel hashing via Web Workers, loading indicator, finding-sort refinement
- **v0.22.2** *(2026-05-02)* — Re-import ↻ detection via localStorage cross-manifest cache
- **v0.23** *(2026-05-03)* — PDF Audit Report: client-side A4 PDF export via jsPDF — Cover, Trust-Status, Asset Inventory, AR Quick Look Findings, Provenance + Lineage, Disclaimer
- **v0.24** *(2026-05-03)* — UX polish: full-size texture modal (`<dialog>`) + PBR channel detection (10 channels + unknown fallback via `inputs:*.connect` USDA parsing)
- **v0.24.1** *(2026-05-03)* — Multi-file drop (stacked mini-dashboards, session-based ↻-cards) + texture status refinement (used / unused / orphaned / unknown) + test-asset sync (new manifest_ids, Normal channel verified)
- **v0.25** *(2026-05-04)* — Geometry stats (10 metrics: Geoms, Polys, Vertices, Materials, Prims, Joints, UV-Sets, Subdivision, Time-Range, FPS) + iOS 3D-Preview via `<model-viewer>` (conditional CDN lazy-load, AR Quick Look button) + Desktop QR-code bridge (client-side qrcode-svg, no server roundtrip)
- **v0.25.2** *(2026-05-04)* — QR-code bridge removed (ADR-26 / ADR-PC5): Drag&Drop USDZs have no public URL reachable by iPhone — QR approach is architecturally incompatible with Privacy-First / Single-File / no-backend anchors. Replaced by iOS AR test guide (AirDrop / iCloud Drive / Mail). ~58 lines removed, no new dependencies.

**Plan**
- **v0.26** — Composition explorer: layer stack, references, payloads and variants as a tree
- **v0.27** — Diff view on hash mismatch: byte delta, texture resolution delta
- **v0.28** — Web Component (`<usdseal-inspector>`) embed pattern documented in README (consumer-side inline boilerplate, ~10 lines, wraps an iframe to GitHub Pages) + QR-code conference pack. Inspector code stays single-file for good — web-component pattern lives at the consumer site, not as a second distribution file in this repo.

**Vision**

- **v0.29** — MCP server wrapper (`usdseal-inspector-mcp`, separate repo) — makes any USDZ inspection AI-agent-callable
- **v0.3** — Ed25519 cryptographic signature verification via WebCrypto API, batch analysis, CSV export

The full roadmap lives in [ROADMAP.md](ROADMAP.md). Compatibility matrix: [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md). AR Quick Look rule catalog: [docs/AR-QL-RULES.md](docs/AR-QL-RULES.md). Per-sprint briefings under [docs/](docs/).

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

## Legal

USD and USDZ are trademarks of Pixar. OpenUSD is an open standard maintained by the [Alliance for OpenUSD (AOUSD)](https://aousd.org). viSales GmbH is a member of the Alliance for OpenUSD. USDseal and the USDseal Inspector are independent open-source tools developed by viSales GmbH and are not affiliated with or endorsed by Pixar or the AOUSD.

---

Built by [Gerhard Schröder](https://visales.de/gerhard-schroeder.html) / [viSales GmbH](https://visales.de) · Bochum, Germany
