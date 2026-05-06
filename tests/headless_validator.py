#!/usr/bin/env python3
"""
headless_validator.py — Test-Wrapper für AR_QL_RULES (v0.22.1)

Portiert die Validator-Logik aus index.html 1:1 als Python-Klasse.
index.html wird NICHT angefasst — dieser Wrapper ist ausschliesslich für
headless-Tests gegen den review-pool.

Aufruf:
    python3 tests/headless_validator.py ../../../usdz/review-pool/
"""

import sys
import os
import re
import json
import hashlib
import struct
import zipfile
from pathlib import Path


# ── Konstanten (aus index.html übernommen) ────────────────────────────────────

SUPPORTED_SPEC_VERSIONS = ['0.1', '0.2']
SIDECAR_PATH = 'credentials/usdseal-manifest.json'


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def sha256hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_texture_path(p: str) -> str:
    """normalizeTexturePath() aus index.html — nur für Existenz-Prüfung."""
    if not p:
        return ''
    n = p.lower()
    if n.startswith('./'):
        n = n[2:]
    n = re.sub(r'\.jpeg$', '.jpg', n)
    return n


def find_member_for_manifest_path(member_names: set, normalized_map: dict, manifest_path: str):
    """findMemberForManifestPath() aus index.html."""
    if manifest_path in member_names:
        return manifest_path
    norm = normalize_texture_path(manifest_path)
    return normalized_map.get(norm)


def is_absolute_texture_path(text: str) -> bool:
    """isAbsoluteTexturePath() aus index.html — alle 5 Plattform-Stile."""
    if not text:
        return False
    if re.search(r'@\s*[A-Za-z]:[\\/]', text):
        return True
    if re.search(r'@\s*\\\\[^\s@\\]+\\', text):
        return True
    if re.search(r'@\s*file://', text, re.IGNORECASE):
        return True
    if re.search(r'@\s*(?:~|\$HOME)/', text):
        return True
    if re.search(r'@\s*/(?:Users|home|var|Volumes|tmp|opt|usr|root|mnt|media)/', text, re.IGNORECASE):
        return True
    return False


def read_png_dimensions(data: bytes):
    if len(data) < 26 or data[0] != 0x89 or data[1] != 0x50:
        return None
    w = struct.unpack('>I', data[16:20])[0]
    h = struct.unpack('>I', data[20:24])[0]
    return w, h


def read_jpeg_dimensions(data: bytes):
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        return None
    i = 2
    while i < len(data) - 8:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h = (data[i + 5] << 8) | data[i + 6]
            w = (data[i + 7] << 8) | data[i + 8]
            return w, h
        if i + 3 >= len(data):
            break
        seg_len = (data[i + 2] << 8) | data[i + 3]
        if seg_len < 2:
            return None
        i += 2 + seg_len
    return None


def is_pot(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


# ── USD-Metadaten-Extraktion (USDA) ──────────────────────────────────────────

def extract_usd_metadata(data: bytes, name: str) -> dict:
    is_ascii = name.lower().endswith('.usda')
    result = {
        'sourceFile': name,
        'defaultPrim': None,
        'upAxis': None,
        'metersPerUnit': None,
        'fullText': None,
    }
    try:
        text = data.decode('utf-8', errors='replace')
        result['fullText'] = text
        if is_ascii:
            _parse_usda_metadata(text, result)
        else:
            _parse_usdc_strings(text[:65536], result)
    except Exception:
        pass
    return result


def _parse_usda_metadata(text: str, result: dict):
    # Header: alles vor erster def/over/class-Zeile
    m = re.match(r'^[\s\S]*?(?=\n\s*(?:def|over|class)\s)', text)
    header = m.group(0) if m else text[:4000]

    m = re.search(r'defaultPrim\s*=\s*"([^"]+)"', header)
    if m:
        result['defaultPrim'] = m.group(1)

    m = re.search(r'upAxis\s*=\s*"([^"]+)"', header)
    if m:
        result['upAxis'] = m.group(1)

    m = re.search(r'metersPerUnit\s*=\s*([0-9.]+)', header)
    if m:
        try:
            result['metersPerUnit'] = float(m.group(1))
        except ValueError:
            pass


def _parse_usdc_strings(text: str, result: dict):
    m = re.search(r'upAxis[\s\S]{0,16}([YZyz])\b', text)
    if m:
        result['upAxis'] = m.group(1).upper()


# ── Kontext-Aufbau ────────────────────────────────────────────────────────────

def build_context(usdz_path: Path) -> dict:
    """Öffnet USDZ, baut den ctx-Dict wie render() in index.html."""
    file_size = usdz_path.stat().st_size
    members = []
    manifest = None
    usd_meta = None
    textures = []

    with zipfile.ZipFile(usdz_path, 'r') as zf:
        names = [i.filename for i in zf.infolist() if not i.is_dir()]

        for name in names:
            data = zf.read(name)
            sha = sha256hex(data)
            members.append({'name': name, 'size': len(data), 'sha256': sha, '_data': data})

        # Manifest
        if SIDECAR_PATH in names:
            manifest = json.loads(zf.read(SIDECAR_PATH).decode('utf-8'))

        # Root-Layer: erstes USD-File in member-Reihenfolge
        root_member = next(
            (m for m in members if re.search(r'\.(usda|usdc|usd)$', m['name'], re.IGNORECASE)),
            None
        )
        if root_member:
            usd_meta = extract_usd_metadata(root_member['_data'], root_member['name'])

        # Texturen — Dimensionen aus Binary-Header
        for m in members:
            ext = m['name'].rsplit('.', 1)[-1].lower() if '.' in m['name'] else ''
            if ext not in ('png', 'jpg', 'jpeg', 'webp', 'exr', 'hdr', 'ktx', 'ktx2', 'tif', 'tiff', 'avif'):
                continue
            tex = {'name': m['name'], 'size': m['size'], 'width': None, 'height': None}
            d = m['_data']
            if ext == 'png':
                dims = read_png_dimensions(d)
                if dims:
                    tex['width'], tex['height'] = dims
            elif ext in ('jpg', 'jpeg'):
                dims = read_jpeg_dimensions(d)
                if dims:
                    tex['width'], tex['height'] = dims
            textures.append(tex)

    # mismatchCount — wie in render()
    inventory = (manifest or {}).get('asset_inventory', [])
    inv_by_path = {i['path']: i for i in inventory if i.get('path')}
    member_names_set = {m['name'] for m in members}
    mismatch = 0
    missing = 0
    for m in members:
        if m['name'] == SIDECAR_PATH:
            continue
        inv = inv_by_path.get(m['name'])
        if inv and inv.get('sha256') and inv['sha256'] != m['sha256']:
            mismatch += 1
    for inv in inventory:
        if inv.get('path') and inv['path'] not in member_names_set:
            missing += 1

    # Strip _data aus members (kein Memory-Leak im Output)
    clean_members = [{'name': m['name'], 'size': m['size'], 'sha256': m['sha256']} for m in members]

    return {
        'manifest': manifest,
        'members': clean_members,
        'usdMeta': usd_meta,
        'textures': textures,
        'mismatchCount': mismatch + missing,
        'fileSize': file_size,
    }


# ── Validator-Regeln (1:1 Port aus AR_QL_RULES in index.html) ────────────────

AR_QL_RULES = [
    # ── Structure
    {
        'id': 'STRUCTURE_DEFAULT_PRIM_MISSING',
        # Severity-Recal 2026-05-05 — Real-World-Sweep 6/6 laufende Files. Apple fällt auf first prim zurück.
        'severity': 'warn',
        'category': 'cat_structure',
        'check': lambda ctx: not (ctx.get('usdMeta') or {}).get('defaultPrim'),
    },
    {
        'id': 'STRUCTURE_ROOT_LAYER_NOT_FIRST',
        'severity': 'error',
        'category': 'cat_structure',
        'check': lambda ctx: (
            bool(ctx.get('members')) and (
                not re.search(r'\.(usda|usdc|usd)$', ctx['members'][0]['name'], re.IGNORECASE)
                or '/' in ctx['members'][0]['name']
            )
        ),
    },
    {
        'id': 'STRUCTURE_NESTED_USDZ',
        # Severity-Recal 2026-05-05 — Frankfurt läuft trotz Nesting. Apple toleriert.
        'severity': 'warn',
        'category': 'cat_structure',
        'check': lambda ctx: any(
            re.search(r'\.usdz$', m['name'], re.IGNORECASE)
            for m in ctx.get('members', [])
        ),
    },
    {
        'id': 'STRUCTURE_FILE_SIZE_LIMIT',
        'severity': 'warn',
        'category': 'cat_structure',
        'check': lambda ctx: (ctx.get('fileSize') or 0) > 25 * 1024 * 1024,
    },
    {
        'id': 'STRUCTURE_HIDDEN_FILES',
        'severity': 'info',
        'category': 'cat_structure',
        'check': lambda ctx: any(
            re.search(r'(^|/)\.DS_Store$', m['name']) or
            re.search(r'(^|/)__MACOSX(/|$)', m['name']) or
            re.search(r'(^|/)\.git(/|$)', m['name'])
            for m in ctx.get('members', [])
        ),
    },
    # ── Scale & Axes (requires valid_root)
    {
        'id': 'SCALE_UP_AXIS_NOT_Y',
        'severity': 'warn',
        'category': 'cat_scale',
        'requires': 'valid_root',
        'check': lambda ctx: bool(
            (ctx.get('usdMeta') or {}).get('upAxis') and
            ctx['usdMeta']['upAxis'] != 'Y'
        ),
    },
    {
        'id': 'SCALE_METERS_PER_UNIT_MISSING',
        'severity': 'warn',
        'category': 'cat_scale',
        'requires': 'valid_root',
        'check': lambda ctx: (
            ctx.get('usdMeta') is not None and
            ctx['usdMeta'].get('metersPerUnit') is None
        ),
    },
    {
        'id': 'SCALE_METERS_PER_UNIT_UNREALISTIC',
        'severity': 'warn',
        'category': 'cat_scale',
        'requires': 'valid_root',
        'check': lambda ctx: (
            (ctx.get('usdMeta') or {}).get('metersPerUnit') is not None and
            (lambda m: not (0.001 <= m <= 1000))(float(ctx['usdMeta']['metersPerUnit']))
        ),
    },
    # ── Textures
    {
        'id': 'TEXTURE_FORMAT_UNSUPPORTED',
        'severity': 'error',
        'category': 'cat_textures',
        'check': lambda ctx: any(
            re.search(r'\.(exr|hdr|tif|tiff|ktx|ktx2|tga|psd)$', m['name'], re.IGNORECASE)
            for m in ctx.get('members', [])
        ),
    },
    {
        'id': 'TEXTURE_TOO_LARGE',
        'severity': 'warn',
        'category': 'cat_textures',
        'check': lambda ctx: any(
            (t.get('width') or 0) > 4096 or (t.get('height') or 0) > 4096
            for t in ctx.get('textures', [])
        ),
    },
    {
        'id': 'TEXTURE_NPOT',
        'severity': 'info',
        'category': 'cat_textures',
        'check': lambda ctx: any(
            t.get('width') and t.get('height') and
            (not is_pot(t['width']) or not is_pot(t['height']))
            for t in ctx.get('textures', [])
        ),
    },
    {
        'id': 'TEXTURE_PATH_ABSOLUTE',
        'severity': 'error',
        'category': 'cat_textures',
        'requires': 'valid_root',
        'check': lambda ctx: is_absolute_texture_path(
            (ctx.get('usdMeta') or {}).get('fullText') or ''
        ),
    },
    {
        'id': 'TEXTURE_NOT_IN_USDZ',
        'severity': 'error',
        'category': 'cat_textures',
        'check': lambda ctx: _check_texture_not_in_usdz(ctx),
    },
    {
        'id': 'TEXTURE_PATH_DIFFERENT_CASE',
        'severity': 'info',
        'category': 'cat_textures',
        'check': lambda ctx: _check_texture_path_different_case(ctx),
    },
    # ── External References (requires valid_root)
    {
        'id': 'EXTERNAL_HTTP_REFERENCE',
        'severity': 'error',
        'category': 'cat_external',
        'requires': 'valid_root',
        'check': lambda ctx: bool(re.search(
            r'@\s*https?://', (ctx.get('usdMeta') or {}).get('fullText') or '', re.IGNORECASE
        )),
    },
    {
        'id': 'EXTERNAL_FILE_REFERENCE',
        'severity': 'error',
        'category': 'cat_external',
        'requires': 'valid_root',
        'check': lambda ctx: bool(re.search(
            r'@\s*(\.\.\/|file://)', (ctx.get('usdMeta') or {}).get('fullText') or '', re.IGNORECASE
        )),
    },
    # ── Manifest
    {
        'id': 'MANIFEST_MISSING',
        'severity': 'info',
        'category': 'cat_manifest',
        'check': lambda ctx: ctx.get('manifest') is None,
    },
    {
        'id': 'MANIFEST_HASH_MISMATCH',
        'severity': 'warn',
        'category': 'cat_manifest',
        'check': lambda ctx: (ctx.get('mismatchCount') or 0) > 0,
    },
    # ── Animation (requires valid_root)
    {
        'id': 'ANIMATION_TIMECODE_MISSING',
        'severity': 'warn',
        'category': 'cat_animation',
        'requires': 'valid_root',
        'check': lambda ctx: _check_animation_timecode(ctx),
    },
    # ── Performance
    {
        'id': 'PERFORMANCE_MANY_TEXTURES',
        'severity': 'info',
        'category': 'cat_performance',
        'check': lambda ctx: len(ctx.get('textures', [])) > 16,
    },
    {
        'id': 'PERFORMANCE_LARGE_INVENTORY',
        'severity': 'info',
        'category': 'cat_performance',
        'check': lambda ctx: len(ctx.get('members', [])) > 100,
    },
]


def _check_texture_not_in_usdz(ctx) -> bool:
    inv = (ctx.get('manifest') or {}).get('asset_inventory', [])
    if not inv:
        return False
    member_names = {m['name'] for m in ctx.get('members', [])}
    normalized_map = {normalize_texture_path(m['name']): m['name'] for m in ctx.get('members', [])}
    return any(
        i.get('type') == 'texture' and i.get('path') and
        not find_member_for_manifest_path(member_names, normalized_map, i['path'])
        for i in inv
    )


def _check_texture_path_different_case(ctx) -> bool:
    inv = (ctx.get('manifest') or {}).get('asset_inventory', [])
    if not inv:
        return False
    member_names = {m['name'] for m in ctx.get('members', [])}
    normalized_map = {normalize_texture_path(m['name']): m['name'] for m in ctx.get('members', [])}
    for i in inv:
        if i.get('type') != 'texture' or not i.get('path'):
            continue
        if i['path'] in member_names:
            continue
        matched = find_member_for_manifest_path(member_names, normalized_map, i['path'])
        if matched and matched != i['path']:
            return True
    return False


def _check_animation_timecode(ctx) -> bool:
    txt = (ctx.get('usdMeta') or {}).get('fullText') or ''
    has_anim = bool(re.search(r'\b(startTimeCode|endTimeCode|timeSamples)\b', txt))
    has_tcps = bool(re.search(r'\btimeCodesPerSecond\b', txt))
    return has_anim and not has_tcps


# ── Validator-Runner (1:1 wie runValidator() und ampelStatus() in index.html) ─

def run_validator(ctx: dict) -> list:
    root_rule = next((r for r in AR_QL_RULES if r['id'] == 'STRUCTURE_ROOT_LAYER_NOT_FIRST'), None)
    root_broken = False
    if root_rule:
        try:
            root_broken = root_rule['check'](ctx)
        except Exception:
            pass

    findings = []
    for rule in AR_QL_RULES:
        if root_broken and rule.get('requires') == 'valid_root':
            continue
        try:
            if rule['check'](ctx):
                findings.append(rule)
        except Exception as e:
            print(f'  [warn] {rule["id"]} check raised: {e}', file=sys.stderr)
    return findings


def ampel_status(findings: list) -> str:
    sevs = {f['severity'] for f in findings}
    if 'error' in sevs:
        return 'red'
    if 'warn' in sevs:
        return 'orange'
    return 'green'


def detect_state(manifest, mismatch_count: int = 0) -> str:
    if not manifest:
        return 'NO_MANIFEST'
    has_sig = bool((manifest.get('signature') or {}).get('value_base64'))
    if mismatch_count > 0 and has_sig:
        return 'INVALID'
    return 'SIGNED' if has_sig else 'DRAFT'


# ── Ausgabe ───────────────────────────────────────────────────────────────────

AMPEL_SYMBOL = {'red': '🔴', 'orange': '🟠', 'green': '🟢'}
SEV_ORDER = {'error': 0, 'warn': 1, 'info': 2}
CAT_ORDER = {
    'cat_structure': 0, 'cat_scale': 1, 'cat_textures': 2,
    'cat_external': 3, 'cat_manifest': 4, 'cat_animation': 5, 'cat_performance': 6
}

# Soll-Erwartungen — 7 Original-Pool-Files + 5 Real-World-Files (Severity-Recal v0.25.4)
# Real-World-Sweep 2026-05-05: alle 5 unsignierten Files haben DEFAULT_PRIM_MISSING (jetzt warn)
# → ampel orange (nicht mehr red). Quelle: tests/real-world-2026-05-05.md
EXPECTED = {
    'master_three_levels.usdz':  {'ampel': 'green',  'state': ['SIGNED', 'DRAFT']},
    'tochter_marketing.usdz':    {'ampel': ['green', 'orange'], 'state': ['SIGNED', 'DRAFT']},
    'error_explicit.usdz':       {'ampel': 'orange', 'state': 'INVALID'},
    'DIEGOsat_master.usdz':      {'ampel': 'green',  'state': ['SIGNED', 'DRAFT']},
    'bare_no_manifest.usdz':     {'ampel': ['green', 'orange'], 'state': 'NO_MANIFEST'},
    'wrong_first_file.usdz':     {'ampel': 'red',    'state': 'any'},
    'z_up_axis.usdz':            {'ampel': 'orange', 'state': 'any'},
    # Real-World-Sweep 2026-05-05 (6 viSales-Kunden-/Demo-Files, unsigniert)
    'Frankfurt_Varianten_TK_271125_01.usdz': {'ampel': 'orange', 'state': 'NO_MANIFEST'},
    'Vitra_ID_Demo_TK_201125_01.usdz':       {'ampel': 'orange', 'state': 'NO_MANIFEST'},
    'RENZ_Showtime_Demo.usdz':               {'ampel': 'orange', 'state': 'NO_MANIFEST'},
    'AR-Wohnzimmer-_12_01_2022.usdz':        {'ampel': 'orange', 'state': 'NO_MANIFEST'},
    'SalmonPastaWithInfo.usdz':              {'ampel': 'orange', 'state': 'NO_MANIFEST'},
    # Duke nachgereicht 2026-05-06 (v0.25.4.1-Sweep)
    'DIEGOsat_TK_280426_01.usdz':           {'ampel': 'orange', 'state': 'SIGNED'},
}


def check_expectation(filename, ampel, state, findings) -> str:
    exp = EXPECTED.get(filename)
    if not exp:
        return '— (keine Erwartung definiert)'
    issues = []

    exp_ampel = exp['ampel']
    if isinstance(exp_ampel, list):
        if ampel not in exp_ampel:
            issues.append(f'Ampel: erwartet {"/".join(exp_ampel)}, ist {ampel}')
    elif exp_ampel != 'any' and ampel != exp_ampel:
        issues.append(f'Ampel: erwartet {exp_ampel}, ist {ampel}')

    exp_state = exp.get('state')
    if exp_state and exp_state != 'any':
        exp_states = exp_state if isinstance(exp_state, list) else [exp_state]
        if state not in exp_states:
            issues.append(f'State: erwartet {"/".join(exp_states)}, ist {state}')

    note = exp.get('note', '')
    if not issues:
        return f'✓ PASS' + (f'  [{note}]' if note else '')
    return '⚠ FAIL — ' + '; '.join(issues) + (f'  [{note}]' if note else '')


def print_report(usdz_path: Path):
    filename = usdz_path.name
    print(f'\n{"─"*60}')
    print(f'File: {filename}  ({usdz_path.stat().st_size / 1024:.1f} KB)')

    try:
        ctx = build_context(usdz_path)
    except Exception as e:
        print(f'  ERROR beim Öffnen: {e}')
        return

    findings = run_validator(ctx)
    ampel = ampel_status(findings)
    state = detect_state(ctx['manifest'], ctx['mismatchCount'])

    # Severity-Counts
    counts = {'error': 0, 'warn': 0, 'info': 0}
    for f in findings:
        counts[f['severity']] = counts.get(f['severity'], 0) + 1

    print(f'  State  : {state}')
    print(f'  Ampel  : {AMPEL_SYMBOL.get(ampel, ampel)} {ampel}')
    print(f'  Counts : {counts["error"]} error · {counts["warn"]} warn · {counts["info"]} info')

    # Members-Überblick
    member_count = len(ctx['members'])
    usd_root = next((m['name'] for m in ctx['members'] if re.search(r'\.(usda|usdc|usd)$', m['name'], re.IGNORECASE)), '—')
    print(f'  Members: {member_count}  root={usd_root}')

    # USD-Metadaten
    meta = ctx.get('usdMeta') or {}
    print(f'  usdMeta: defaultPrim={meta.get("defaultPrim")!r}  upAxis={meta.get("upAxis")!r}  mpu={meta.get("metersPerUnit")!r}')

    # Top-3 Findings (ADR-10-Reihenfolge)
    sorted_findings = sorted(
        findings,
        key=lambda f: (SEV_ORDER.get(f['severity'], 9), CAT_ORDER.get(f['category'], 99), f['id'])
    )
    if sorted_findings:
        print(f'  Top-3 Findings:')
        for f in sorted_findings[:3]:
            print(f'    [{f["severity"].upper():5}] {f["id"]}')
    else:
        print(f'  Findings: keine')

    # Soll/Ist-Vergleich
    verdict = check_expectation(filename, ampel, state, findings)
    print(f'  Soll/Ist: {verdict}')


# ── Synthetische Magic-Bytes-Reader-Tests (v0.25.5) ──────────────────────────

def read_heic_signature(data: bytes):
    if len(data) < 12: return None
    if data[4:8] != b'ftyp': return None
    brand = data[8:12].decode('ascii', errors='replace')
    if brand in ('heic', 'heix', 'mif1', 'msf1'): return {'format': 'HEIC'}
    return None

def read_ktx2_signature(data: bytes):
    expected = bytes([0xAB, 0x4B, 0x54, 0x58, 0x20, 0x32, 0x30, 0xBB, 0x0D, 0x0A, 0x1A, 0x0A])
    if len(data) < 12: return None
    if data[:12] == expected: return {'format': 'KTX2'}
    return None

def read_tiff_signature(data: bytes):
    if len(data) < 4: return None
    if data[:4] == bytes([0x49, 0x49, 0x2A, 0x00]): return {'format': 'TIFF', 'endian': 'LE'}
    if data[:4] == bytes([0x4D, 0x4D, 0x00, 0x2A]): return {'format': 'TIFF', 'endian': 'BE'}
    return None

def read_astc_signature(data: bytes):
    if len(data) < 4: return None
    if data[:4] == bytes([0x13, 0xAB, 0xA1, 0x5C]): return {'format': 'ASTC'}
    return None


def run_reader_tests() -> tuple[int, int]:
    """4 synthetische Magic-Bytes-Reader-Tests (kein USDZ-Wrapper nötig)."""
    tests = [
        ('HEIC ftyp heic',  bytes([0,0,0,0x20, 0x66,0x74,0x79,0x70, 0x68,0x65,0x69,0x63]), read_heic_signature,  'HEIC'),
        ('KTX2 12-Byte Magic', bytes([0xAB,0x4B,0x54,0x58,0x20,0x32,0x30,0xBB,0x0D,0x0A,0x1A,0x0A]), read_ktx2_signature, 'KTX2'),
        ('TIFF LE II*\\0',   bytes([0x49,0x49,0x2A,0x00]),  read_tiff_signature,  'TIFF'),
        ('ASTC 4-Byte Magic', bytes([0x13,0xAB,0xA1,0x5C]), read_astc_signature, 'ASTC'),
    ]
    passed = 0
    failed = 0
    print('\n── Synthetische Reader-Tests (v0.25.5) ────────────────────')
    for name, data, fn, expected_format in tests:
        result = fn(data)
        ok = result is not None and result.get('format') == expected_format
        status = '✓ PASS' if ok else f'⚠ FAIL (got {result!r})'
        print(f'  [{expected_format:<5}] {name:<30} {status}')
        if ok: passed += 1
        else:  failed += 1
    # Negative: falscher Magic → None
    neg = read_ktx2_signature(bytes([0x00] * 12))
    neg_ok = neg is None
    print(f'  [NEG  ] KTX2 falsche Bytes → None         {"✓ PASS" if neg_ok else "⚠ FAIL"}')
    if neg_ok: passed += 1
    else:      failed += 1
    return passed, failed


def main():
    pool_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent / 'usdz' / 'review-pool'

    if not pool_dir.is_dir():
        print(f'ERROR: Verzeichnis nicht gefunden: {pool_dir}', file=sys.stderr)
        sys.exit(1)

    files = sorted(pool_dir.glob('*.usdz'))
    if not files:
        print(f'Keine .usdz-Files in {pool_dir}', file=sys.stderr)
        sys.exit(1)

    print(f'USDseal Inspector — Headless Validator (v0.22.1 port)')
    print(f'Pool: {pool_dir}  ({len(files)} files)')

    pass_count = 0
    fail_count = 0
    for usdz in files:
        print_report(usdz)
        # Zählung aus letzter Zeile des Reports — vereinfacht via re-scan
    print(f'\n{"═"*60}')

    # Kompakt-Tabelle
    print(f'\n{"File":<35} {"Ampel":<8} {"State":<12} {"E/W/I":<9} Verdict')
    print('─' * 85)
    for usdz in files:
        try:
            ctx = build_context(usdz)
            findings = run_validator(ctx)
            ampel = ampel_status(findings)
            state = detect_state(ctx['manifest'], ctx['mismatchCount'])
            counts = {'error': 0, 'warn': 0, 'info': 0}
            for f in findings:
                counts[f['severity']] += 1
            verdict = check_expectation(usdz.name, ampel, state, findings)
            status = '✓' if verdict.startswith('✓') else '⚠'
            if status == '✓':
                pass_count += 1
            else:
                fail_count += 1
            ewi = f'{counts["error"]}/{counts["warn"]}/{counts["info"]}'
            print(f'{usdz.name:<35} {ampel:<8} {state:<12} {ewi:<9} {verdict}')
        except Exception as e:
            fail_count += 1
            print(f'{usdz.name:<35} ERROR: {e}')

    print('─' * 85)

    reader_pass, reader_fail = run_reader_tests()
    total_pass = pass_count + reader_pass
    total_fail = fail_count + reader_fail
    total = len(files) + reader_pass + reader_fail
    print(f'\nErgebnis: {pass_count} PASS · {fail_count} FAIL / {len(files)} Pool-Files')
    print(f'          {reader_pass} PASS · {reader_fail} FAIL / {reader_pass + reader_fail} Reader-Tests (synthetisch)')
    print(f'Gesamt:   {total_pass} PASS · {total_fail} FAIL / {total} Cases')


if __name__ == '__main__':
    main()
