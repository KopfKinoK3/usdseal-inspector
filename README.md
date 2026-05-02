# USDseal Inspector

**Browser-based USDZ file analyzer — no upload, no server, no installation.**

The USDseal Inspector reads USDZ files entirely in your browser using the [JSZip](https://stuk.github.io/jszip/) library. All processing happens locally. No data leaves your machine.

→ **[Try it live](https://kopfkinok3.github.io/usdseal-inspector/)** (GitHub Pages)

---

## What it does

| Feature | USDseal files | Any USDZ |
|---|---|---|
| **AR Quick Look traffic-light** — green/orange/red diagnosis with plain-language findings (DE + EN) | ✓ *(v0.22.1)* | ✓ *(v0.22.1)* |
| **Parallel hashing via Web Workers** + loading indicator | ✓ *(v0.22.1)* | ✓ *(v0.22.1)* |
| State detection (SIGNED / DRAFT / INVALID / NO MANIFEST) | ✓ | — |
| SHA-256 asset verification against manifest | ✓ | — |
| **Lineage panel** — Master ⬇ (`import_history[]`) / Derived ⬆ (`parent_manifest_id`) | ✓ *(v0.21)* | — |
| **Provenance timeline** — sealed / merged / derived steps with notes | ✓ *(v0.21)* | — |
| **Spec-version compatibility** — graceful handling of `0.1` and `0.2` manifests | ✓ *(v0.21)* | — |
| Signature details (Ed25519 public key, timestamp) | ✓ | — |
| USD metadata (defaultPrim, upAxis, metersPerUnit) | ✓ | ✓ |
| Texture analysis (PNG, JPEG, WebP dimensions + thumbnails) | ✓ | ✓ |
| Asset inventory (filenames, sizes) | ✓ | ✓ |

## What is USDseal?

USDseal is a companion tool that adds cryptographically signed provenance metadata to USDZ files (Ed25519 / COSE_Sign1, C2PA-compatible). The Inspector is its verification counterpart — but works with any USDZ file, signed or not.

## Origin

The first version of this tool was built on the evening of April 27, 2026 — after day one of the [XR Expo Stuttgart](https://www.messe-stuttgart.de/xrexpo/), and the night before a talk on OpenUSD by Gerhard Schröder, the developer of this tool. The idea was simple: after explaining provenance and trust for 3D assets on stage, attendees should be able to open a USDZ file and see exactly what was inside — right then, in the browser, with no install. v0.1 was a proof of concept. v0.2 shipped the next day.

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

## Roadmap

**Released**

- **v0.1** *(2026-04-27, internal)* — Proof of concept: JSZip-based USDZ parsing, first manifest detection
- **v0.2** *(2026-04-28)* — State detection, SHA-256 verification, USD metadata, texture analysis with thumbnails, provenance chain, signature details

**Plan**

- **v0.22** — AR Quick Look traffic-light validator (20 rules, DE/EN), Lineage panel (Master/Derived), Provenance timeline, spec-version compatibility
- **v0.22.1** — Full EN translation, regex hardening, parallel hashing via Web Workers, loading indicator
- **v0.22.2** — Re-import ↻ detection via localStorage cross-manifest cache, optional multi-file drop
- **v0.23** — PDF audit report (jsPDF): hash integrity + AR Quick Look findings + compliance disclaimer
- **v0.24** — Texture detail view: full-size modal, channel detection (Diffuse / Normal / Roughness / …)
- **v0.25** — Geometry stats (polycount, bounding box, mesh/material/joint count) + 3D preview via `<model-viewer>`
- **v0.26** — Composition explorer: layer stack, references, payloads and variants as a tree
- **v0.27** — Diff view on hash mismatch: byte delta, texture resolution delta
- **v0.28** — Web Component (`<usdseal-inspector>`), QR-code conference pack

**Vision**

- **v0.29** — MCP server wrapper (`usdseal-inspector-mcp`, separate repo) — makes any USDZ inspection AI-agent-callable
- **v0.3** — Ed25519 cryptographic signature verification via WebCrypto API, batch analysis, CSV export

The full roadmap lives in [ROADMAP.md](ROADMAP.md). Compatibility matrix: [COMPATIBILITY.md](COMPATIBILITY.md).

## License

Apache 2.0 — see [LICENSE](LICENSE)

## Legal

USD and USDZ are trademarks of Pixar. OpenUSD is an open standard maintained by the [Alliance for OpenUSD (AOUSD)](https://aousd.org). viSales GmbH is a member of the Alliance for OpenUSD. USDseal and the USDseal Inspector are independent open-source tools developed by viSales GmbH and are not affiliated with or endorsed by Pixar or the AOUSD.

---

Built by [Gerhard Schröder](https://media.visales.de/gerhard-schroeder) / [viSales GmbH](https://visales.de) · Bochum, Germany
