# USDseal Inspector

**Browser-based USDZ file analyzer — no upload, no server, no installation.**

The USDseal Inspector reads USDZ files entirely in your browser using the [JSZip](https://stuk.github.io/jszip/) library. All processing happens locally. No data leaves your machine.

→ **[Try it live](https://visales.github.io/usdseal-inspector/)** (GitHub Pages)

---

## What it does

| Feature | USDseal files | Any USDZ |
|---|---|---|
| State detection (SIGNED / DRAFT / INVALID / NO MANIFEST) | ✓ | — |
| SHA-256 asset verification against manifest | ✓ | — |
| Provenance chain (author, version, predecessor) | ✓ | — |
| Signature details (Ed25519 public key, timestamp) | ✓ | — |
| USD metadata (defaultPrim, upAxis, metersPerUnit) | ✓ | ✓ |
| Texture analysis (PNG, JPEG, WebP dimensions + thumbnails) | ✓ | ✓ |
| Asset inventory (filenames, sizes) | ✓ | ✓ |

## What is USDseal?

USDseal is a companion tool that adds cryptographically signed provenance metadata to USDZ files (Ed25519 / COSE_Sign1, C2PA-compatible). The Inspector is its verification counterpart — but works with any USDZ file, signed or not.

## Usage

**Option A — GitHub Pages (no installation):**
Open [visales.github.io/usdseal-inspector](https://visales.github.io/usdseal-inspector/) in any modern browser.

**Option B — Download:**
Download `index.html` and open it locally. No web server needed.

**Option C — Embed (iframe):**
```html
<iframe src="https://visales.github.io/usdseal-inspector/"
        width="100%" height="720" style="border:none;">
</iframe>
```

## Roadmap

- **v0.2** (current) — State detection, SHA-256 verification, USD metadata, texture analysis
- **v0.3** (planned) — Ed25519 cryptographic signature verification via WebCrypto API
- **v0.4** (planned) — Batch analysis, export report

## License

Apache 2.0 — see [LICENSE](LICENSE)

## Legal

USD and USDZ are trademarks of Pixar. OpenUSD is an open standard maintained by the [Alliance for OpenUSD (AOUSD)](https://aousd.org). viSales GmbH is a member of the Alliance for OpenUSD. USDseal and the USDseal Inspector are independent open-source tools developed by viSales GmbH and are not affiliated with or endorsed by Pixar or the AOUSD.

---

Built by [viSales GmbH](https://visales.de) · Bochum, Germany · [visales.de](https://visales.de)
