#!/usr/bin/env python3
"""
Build-Step für Inspector Standard + Inspector Advanced.
Quelle: src/inspector.html
Ziel:   index.html          (Standard, ADVANCED-ONLY-Blöcke entfernt)
        advanced/index.html (Advanced, STANDARD-ONLY-Blöcke entfernt + BUILD-INJECT aufgelöst)

Marker:
  <!-- ADVANCED-ONLY:START id --> ... <!-- ADVANCED-ONLY:END id -->
  <!-- STANDARD-ONLY:START id --> ... <!-- STANDARD-ONLY:END id -->
  <!-- BUILD-INJECT: vendor/filename.js -->  → ersetzt durch Datei-Inhalt (nur im Advanced-Build)

Aufruf: python3 build.py

ADR-43 Two-File-Pattern (2026-05-24):
  Standard = schlanker Privacy-First-Inspector (~200 KB)
  Advanced = Inspector + Three.js 3D-Preview (~1-1.5 MB)
  Beide Files sind single-file, file://-öffenbar, keine externen Deps zur Laufzeit.
"""
import re
import shutil
from pathlib import Path


def check_theme_variables(src_html: str) -> None:
    """
    Vergleicht var(--*)-Calls mit :root-Deklarationen.
    Gibt WARNING aus bei undefinierten Variablen — stoppt den Build nicht.
    """
    defined = set(re.findall(r'--([a-zA-Z0-9_-]+)\s*:', src_html))
    used = set(re.findall(r'var\(--([a-zA-Z0-9_-]+)', src_html))
    undefined = used - defined
    if undefined:
        print("\n⚠  THEME-VARIABLE-WARNING: Folgende var(--*)-Calls haben keine :root-Deklaration:")
        for v in sorted(undefined):
            print(f"   var(--{v})")
        print("   → Mapping-Hilfe: docs/CSS-THEME-REFERENCE.md")
        print("   (Build läuft weiter — bitte vor dem Commit prüfen)\n")
    else:
        print("   Theme-Check: alle var(--*) definiert ✓")

SRC     = Path("src/inspector.html")
STD     = Path("index.html")
ADV     = Path("advanced/index.html")
VENDOR  = Path("vendor")
NOJEKYLL = Path(".nojekyll")


def strip_blocks(html: str, marker: str) -> str:
    """Entfernt alle <!-- marker:START id --> ... <!-- marker:END id --> Blöcke."""
    pattern = re.compile(
        rf"<!--\s*{re.escape(marker)}:START[^>]*?-->.*?<!--\s*{re.escape(marker)}:END[^>]*?-->",
        re.DOTALL,
    )
    return pattern.sub("", html)


def inject_vendor(html: str) -> str:
    """Ersetzt <!-- BUILD-INJECT: vendor/filename --> durch Datei-Inhalt."""
    def replace_match(m):
        rel_path = m.group(1).strip()
        vendor_file = VENDOR / Path(rel_path).name  # sicherheitshalber nur Filename
        if not vendor_file.exists():
            print(f"  WARN: {vendor_file} nicht gefunden — Marker bleibt stehen")
            return m.group(0)
        content = vendor_file.read_text(encoding="utf-8")
        size_kb = vendor_file.stat().st_size / 1024
        print(f"  INJECT: {vendor_file} ({size_kb:.1f} KB)")
        return f"<script>\n{content}\n</script>"

    pattern = re.compile(r"<!--\s*BUILD-INJECT:\s*(vendor/[^\s>]+)\s*-->")
    return pattern.sub(replace_match, html)


def main():
    if not SRC.exists():
        print(f"FEHLER: {SRC} nicht gefunden.")
        raise SystemExit(1)

    src = SRC.read_text(encoding="utf-8")

    # ── Theme-Variable-Check ──────────────────────────────────────────────────
    check_theme_variables(src)

    # ── Standard-Build: ADVANCED-ONLY entfernen, BUILD-INJECT NICHT auflösen ──
    std_html = strip_blocks(src, "ADVANCED-ONLY")
    STD.write_text(std_html, encoding="utf-8")
    print(f"OK: {STD} ({STD.stat().st_size / 1024:.1f} KB)")

    # ── Advanced-Build: STANDARD-ONLY entfernen + Bundle separat kopieren ──
    ADV.parent.mkdir(exist_ok=True)
    adv_html = strip_blocks(src, "STANDARD-ONLY")
    adv_html = inject_vendor(adv_html)   # no-op wenn kein BUILD-INJECT-Marker im Src
    ADV.write_text(adv_html, encoding="utf-8")
    print(f"OK: {ADV} ({ADV.stat().st_size / 1024:.1f} KB)")

    # ── v0.28.0.2 ADR-45: Bundle als separates File (Lazy-Load) ──────────
    bundle_src = VENDOR / "three-usdloader-r184-bundle.js"
    bundle_dst = ADV.parent / "three-usdloader-r184-bundle.js"
    if bundle_src.exists():
        shutil.copy2(bundle_src, bundle_dst)
        print(f"OK: {bundle_dst} ({bundle_dst.stat().st_size / 1024:.1f} KB, kopiert)")

    # ── v0.28.2 ADR-49: Polyfill-Bundles als separate Files (On-Demand-Lazy-Load) ──
    for polyfill_name in ("ktx2-polyfill-bundle.js", "tiff-polyfill-bundle.js", "basis_transcoder.wasm"):
        p_src = VENDOR / polyfill_name
        p_dst = ADV.parent / polyfill_name
        if p_src.exists():
            shutil.copy2(p_src, p_dst)
            size = p_dst.stat().st_size
            print(f"OK: {p_dst} ({size / 1024:.1f} KB, kopiert)")

    # ── .nojekyll — Versicherungspolice für GitHub Pages + künftige Unterordner ──
    if not NOJEKYLL.exists():
        NOJEKYLL.touch()
        print(f"OK: {NOJEKYLL} (created)")

    print("\nBuild abgeschlossen. Vor Commit: git diff index.html advanced/index.html prüfen.")


if __name__ == "__main__":
    main()
