# Changelog — USDseal Inspector

All notable changes to this project will be documented in this file.

## [0.2] — 2026-04-28

### Added
- State detection: SIGNED / DRAFT / INVALID / NO MANIFEST
- SHA-256 asset verification against USDseal manifest
- USD metadata extraction: USDA (text parse) + USDC (heuristic string extraction)
- Texture analysis: PNG (IHDR), JPEG (SOF marker), WebP (VP8 header)
- Texture thumbnails via Base64 inline preview
- Provenance chain display (author, version, predecessor file)
- Signature details panel (Ed25519 public key, timestamp, algorithm)
- viSales Warm Tech design system (Orange #F97316, Cyan #0891B2)
- Fully client-side — no data upload, no server, no API

### Notes
- Ed25519 cryptographic signature verification not yet implemented (planned v0.3)
- USDC parsing uses heuristic string extraction (full binary parsing planned)

## [0.1] — 2026-04 (internal)

- Initial proof of concept
- JSZip-based USDZ parsing
- Basic manifest detection
