#!/usr/bin/env python3
"""
vendor/bundle.py — Erzeugt three-usdloader-r184-bundle.js

Kombiniert six Quell-Files aus vendor/src/ zu einem einzigen IIFE-Bundle
das in advanced/index.html inline eingebettet werden kann.

Reihenfolge:
  1. three.core.min.js    — Three.js Core (standalone ESM → IIFE)
  2. three.module.min.js  — Three.js Extras: WebGLRenderer etc. (importiert Core)
  3. fflate.module.js     — USDZ-Entpacken
  4. USDAParser.js        — USDA-Text-Parser (keine Imports)
  5. USDCParser.js        — USDC-Binary-Parser (keine Imports)
  6. USDComposer.js       — USD-Komposition (importiert von 'three')
  7. USDLoader.js         — Haupt-Loader (importiert alles oben)
  8. OrbitControls.js     — Orbit-Controls (importiert von 'three')

Aufruf: python3 vendor/bundle.py
Ausgabe: vendor/three-usdloader-r184-bundle.js

ADR-44 (2026-05-24): Three.js r184 · USDLoader (USDZLoader deprecated seit r179)
"""

import re
from pathlib import Path

SRC = Path(__file__).parent / "src"
OUT = Path(__file__).parent / "three-usdloader-r184-bundle.js"


# ─── Hilfsfunktionen ────────────────────────────────────────────────────────

def read(name):
    return (SRC / name).read_text(encoding="utf-8")


def parse_named_exports(export_block: str) -> list[tuple[str, str]]:
    """
    Parst 'export { Ia as Foo, Bar, Baz as Qux }' → [(internal, public), ...]
    Bei 'Bar' (kein 'as'): (Bar, Bar)
    """
    pairs = []
    for part in export_block.split(","):
        part = part.strip()
        if not part:
            continue
        if " as " in part:
            internal, public = [x.strip() for x in part.split(" as ", 1)]
        else:
            internal = public = part
        pairs.append((internal, public))
    return pairs


def parse_named_imports(import_block: str) -> list[tuple[str, str]]:
    """
    Parst 'import { Foo as x, Bar as y }' → [(public, alias), ...]
    Gleiche Logik wie exports, aber semantisch: (imported_name, local_alias)
    """
    pairs = []
    for part in import_block.split(","):
        part = part.strip()
        if not part:
            continue
        if " as " in part:
            pub, alias = [x.strip() for x in part.split(" as ", 1)]
        else:
            pub = alias = part
        pairs.append((pub, alias))
    return pairs


# ─── Transformationen ────────────────────────────────────────────────────────

def transform_core(content: str) -> str:
    """
    three.core.min.js:
    - Entfernt das abschließende 'export { X as Y, ... };'
    - Ersetzt durch 'window.THREE = { PublicName: InternalMinifiedName, ... }'
    Alle 444 Core-Exports (inkl. Loader, FileLoader, Controls) landen in window.THREE.
    three.module.min.js erweitert window.THREE danach um ~7 zusätzliche Namen.
    ADR-44-fix (2026-05-25): window.THREE statt var-Scope-Bridge — vollständige API.
    """
    m = re.search(r'export\s*\{([^}]+)\}\s*;?\s*$', content, re.DOTALL)
    if not m:
        raise ValueError("three.core.min.js: kein export-Block am Ende gefunden")

    export_block = m.group(1)
    pairs = parse_named_exports(export_block)

    # window.THREE = { PublicName: minifiedInternal, ... }
    props = ", ".join(
        f"{pub}: {intern}" if pub != intern else pub
        for intern, pub in pairs
    )

    result = content[: m.start()] + f"\n// three.core: alle 444 Exports → window.THREE\nwindow.THREE = {{ {props} }};\n"
    return result


def transform_module(content: str) -> str:
    """
    three.module.min.js:
    - Ersetzt 'import{X as y,...}from"./three.core.min.js"' durch 'const y = window.THREE.X;'
      (window.THREE ist durch transform_core gesetzt)
    - Entfernt Re-Export-Statement 'export{...}from"./three.core.min.js"'
    - Ersetzt abschließendes 'export{...}' durch 'Object.assign(window.THREE, {...})'
      (ergänzt ~7 modul-eigene Namen ohne die 444 Core-Namen zu verlieren)
    """
    # 1) Import-Block: 'import { Matrix3 as e } from "./three.core.min.js"'
    #    → 'const e = window.THREE.Matrix3'
    imp_pattern = re.compile(
        r'import\s*\{([^}]+)\}\s*from\s*["\']\.\/three\.core(?:\.min)?\.js["\'];?',
        re.DOTALL,
    )
    m_imp = imp_pattern.search(content)
    if not m_imp:
        raise ValueError("three.module.min.js: import-Block von three.core nicht gefunden")

    import_block = m_imp.group(1)
    pairs = parse_named_imports(import_block)
    # "Matrix3 as e" → const e = window.THREE.Matrix3
    alias_decls = "; ".join(
        f"const {alias} = window.THREE.{pub}" if alias != pub else f"/* {pub} = window.THREE.{pub} */"
        for pub, alias in pairs
        if alias != pub
    )
    content = content[: m_imp.start()] + "// three.module aliases (aus window.THREE):\n" + alias_decls + ";\n" + content[m_imp.end():]

    # 1b) Re-Export-Statement entfernen: 'export{PublicName,...}from"./three.core.min.js"'
    reexport_pat = re.compile(
        r'export\s*\{[^}]+\}\s*from\s*["\']\.\/three\.core(?:\.min)?\.js["\'];?',
        re.DOTALL,
    )
    content = reexport_pat.sub("", content)

    # 2) Finaler Export-Block: nicht ersetzen sondern erweitern via Object.assign
    #    So bleiben alle 444 Core-Namen in window.THREE erhalten.
    m_exp = re.search(r'export\s*\{([^}]+)\}\s*;?\s*$', content, re.DOTALL)
    if not m_exp:
        raise ValueError("three.module.min.js: export-Block am Ende nicht gefunden")

    export_block = m_exp.group(1)
    pairs_exp = parse_named_exports(export_block)
    props = ", ".join(
        f"{pub}: {intern}" if pub != intern else pub
        for intern, pub in pairs_exp
    )
    content = content[: m_exp.start()] + f"\n// three.module ergänzt window.THREE um modul-eigene Exports:\nObject.assign(window.THREE, {{ {props} }});\n"
    return content


def transform_fflate(content: str) -> str:
    """
    fflate.module.js:
    - Entfernt 'export ' Präfix vor Funktionen/Klassen/Vars
    - Entfernt standalone 'export { ... }' Statements
    - Am Ende: window._unzipSync = unzipSync
    """
    # Entferne 'export function' → 'function', 'export class' → 'class', 'export const' → 'const'
    content = re.sub(r'\bexport\s+(function|class|const|let|var)\s', r'\1 ', content)
    # Entferne standalone export { ... } Statements
    content = re.sub(r'\bexport\s*\{[^}]*\}\s*;?', '', content)
    content += "\nwindow._unzipSync = unzipSync;\n"
    return content


def transform_no_imports(content: str, export_name: str) -> str:
    """
    USDAParser.js + USDCParser.js:
    - Keine imports → nur export-Zeile am Ende entfernen
    - Global-Zuweisung am Ende
    """
    content = re.sub(r'\bexport\s*\{[^}]*\}\s*;?\s*$', '', content, flags=re.DOTALL)
    content += f"\nwindow.{export_name} = {export_name};\n"
    return content


def transform_with_three_import(content: str, export_name: str, extra_exports=None) -> str:
    """
    USDComposer.js + OrbitControls.js:
    - Importiert von 'three' → ersetzen durch 'const { ... } = window.THREE'
    - Export am Ende entfernen + global setzen
    """
    # Import von 'three'
    imp_pat = re.compile(
        r'import\s*\{([^}]+)\}\s*from\s*[\'"](three|../../../three)[\'"];?',
        re.DOTALL,
    )
    def replace_three_import(m):
        names_raw = m.group(1)
        pairs = parse_named_imports(names_raw)
        # "name as alias" → const alias = THREE.name
        # "name" → no-op if same, but destructure anyway
        parts = []
        for pub, alias in pairs:
            if alias == pub:
                parts.append(pub)
            else:
                parts.append(f"{pub}: {alias}")
        return f"const {{ {', '.join(parts)} }} = window.THREE;"

    content = imp_pat.sub(replace_three_import, content)

    # Export am Ende
    content = re.sub(r'\bexport\s*\{[^}]*\}\s*;?\s*$', '', content, flags=re.DOTALL)
    content += f"\nwindow.{export_name} = {export_name};\n"
    if extra_exports:
        for name in extra_exports:
            content += f"window.{name} = {name};\n"
    return content


def transform_usd_loader(content: str) -> str:
    """
    USDLoader.js:
    - 5 Import-Statements → globale Referenzen
    - Export → window.USDLoader
    """
    # import { FileLoader, Loader } from 'three'
    content = re.sub(
        r"import\s*\{([^}]+)\}\s*from\s*['\"]three['\"];?",
        lambda m: "const { " + ", ".join(x.strip() for x in m.group(1).split(",")) + " } = window.THREE;",
        content,
    )
    # import { unzipSync } from '../libs/fflate.module.js'
    content = re.sub(
        r"import\s*\{([^}]+)\}\s*from\s*['\"]\.\.\/libs\/fflate\.module\.js['\"];?",
        "const unzipSync = window._unzipSync;",
        content,
    )
    # import { USDAParser } from './usd/USDAParser.js'
    content = re.sub(
        r"import\s*\{[^}]*USDAParser[^}]*\}\s*from\s*['\"][^'\"]+USDAParser\.js['\"];?",
        "const USDAParser = window.USDAParser;",
        content,
    )
    # import { USDCParser } from './usd/USDCParser.js'
    content = re.sub(
        r"import\s*\{[^}]*USDCParser[^}]*\}\s*from\s*['\"][^'\"]+USDCParser\.js['\"];?",
        "const USDCParser = window.USDCParser;",
        content,
    )
    # import { USDComposer } from './usd/USDComposer.js'
    content = re.sub(
        r"import\s*\{[^}]*USDComposer[^}]*\}\s*from\s*['\"][^'\"]+USDComposer\.js['\"];?",
        "const USDComposer = window.USDComposer;",
        content,
    )
    # export { USDLoader }
    content = re.sub(r'\bexport\s*\{[^}]*\}\s*;?\s*$', '', content, flags=re.DOTALL)
    content += "\nwindow.USDLoader = USDLoader;\n"
    return content


# ─── Bundle zusammensetzen ───────────────────────────────────────────────────

def build():
    sections = []

    def add(label, code):
        kb = len(code.encode()) / 1024
        print(f"  [{kb:6.1f} KB] {label}")
        # Block-Scope: jeder Section-Code bekommt eigene {} damit minified const-Namen
        # (wie 'e', 't', 'i' in three.core/module) nicht kollidieren (ADR-44-fix).
        # var-Deklarationen in transform_core() entkommen dem Block (function-scoped).
        sections.append(f"\n// ══════════════════════════════════════\n// {label}\n// ══════════════════════════════════════\n{{\n")
        sections.append(code)
        sections.append("\n}\n")

    print("Lade + transformiere Quell-Files...")

    add("three.core.min.js (r184)",     transform_core(read("three.core.min.js")))
    add("three.module.min.js (r184)",   transform_module(read("three.module.min.js")))
    add("fflate.module.js",             transform_fflate(read("fflate.module.js")))
    add("USDAParser.js",                transform_no_imports(read("USDAParser.js"), "USDAParser"))
    add("USDCParser.js",                transform_no_imports(read("USDCParser.js"), "USDCParser"))
    add("USDComposer.js",               transform_with_three_import(read("USDComposer.js"), "USDComposer", extra_exports=["SpecType"]))
    add("USDLoader.js",                 transform_usd_loader(read("USDLoader.js")))
    add("OrbitControls.js",             transform_with_three_import(read("OrbitControls.js"), "OrbitControls"))

    iife = (
        "// three-usdloader-r184-bundle.js\n"
        "// Three.js r184 + USDLoader + OrbitControls — inline IIFE bundle\n"
        "// Erzeugt von vendor/bundle.py · Sprint v0.28.0 · 2026-05-24\n"
        "// ADR-44: Single-File-Anker — keine CDN-Deps zur Laufzeit\n"
        "// Globals nach Ausführung: window.THREE, window.USDLoader, window.OrbitControls\n"
        "//                          window._unzipSync, window.USDAParser, window.USDCParser, window.USDComposer\n"
        "\n"
        "(function () {\n"
        "'use strict';\n"
    )
    iife += "".join(sections)
    iife += "\n})();\n"

    OUT.write_text(iife, encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"\nOK: {OUT} ({size_kb:.1f} KB)")
    return True


if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
