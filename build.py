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
from pathlib import Path

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

    # ── Standard-Build: ADVANCED-ONLY entfernen, BUILD-INJECT NICHT auflösen ──
    std_html = strip_blocks(src, "ADVANCED-ONLY")
    STD.write_text(std_html, encoding="utf-8")
    print(f"OK: {STD} ({STD.stat().st_size / 1024:.1f} KB)")

    # ── Advanced-Build: STANDARD-ONLY entfernen + BUILD-INJECT auflösen ──
    ADV.parent.mkdir(exist_ok=True)
    adv_html = strip_blocks(src, "STANDARD-ONLY")
    adv_html = inject_vendor(adv_html)
    ADV.write_text(adv_html, encoding="utf-8")
    print(f"OK: {ADV} ({ADV.stat().st_size / 1024:.1f} KB)")

    # ── .nojekyll — Versicherungspolice für GitHub Pages + künftige Unterordner ──
    if not NOJEKYLL.exists():
        NOJEKYLL.touch()
        print(f"OK: {NOJEKYLL} (created)")

    print("\nBuild abgeschlossen. Vor Commit: git diff index.html advanced/index.html prüfen.")


if __name__ == "__main__":
    main()
