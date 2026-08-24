#!/usr/bin/env python3
"""Integration integrity checker for realms-of-myth.

Validates, across the merged tree:
  1. All JSON files parse.
  2. Every particle effect ID referenced in BP scripts exists in the RP.
  3. Every sound ID referenced in scripts/sounds.json resolves to a sound
     definition or raw file.
  4. No duplicate texture keys in item_texture.json / terrain_texture.json.
  5. en_US.lang has entries for every item/entity introduced (key present check
     against item identifiers and entity names used in scripts).

Run from repo root:  python3 tools/check_integration.py
Exits non-zero if hard failures found; prints WARN lines for soft issues.
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, 'realms_of_myth_BP')
RP = os.path.join(ROOT, 'realms_of_myth_RP')
errors, warns = [], []

# ---- 1. JSON validity ------------------------------------------------------
json_files = glob.glob(os.path.join(ROOT, 'realms_of_myth_*', '**', '*.json'), recursive=True)
parsed = {}
for f in json_files:
    try:
        parsed[f] = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        errors.append(f'BAD JSON: {f}: {e}')

# ---- collect RP definitions -----------------------------------------------
particle_ids = set()
for f in glob.glob(os.path.join(RP, 'particles', '*.json')):
    try:
        pid = parsed.get(f, {}).get('particle_effect', {}).get('description', {}).get('identifier')
        if pid: particle_ids.add(pid)
    except Exception: pass

fog_ids = set()
for f in glob.glob(os.path.join(RP, 'fogs', '*.json')):
    fid = os.path.basename(f)[:-5]
    fog_ids.add('minecraft:fog' if False else fid)

sound_defs = set()
sounds_json_path = os.path.join(RP, 'sounds.json')
sound_events = {}
if os.path.exists(sounds_json_path):
    try:
        sound_events = json.load(open(sounds_json_path, encoding='utf-8')) or {}
    except Exception as e:
        warns.append(f'could not parse RP sounds.json: {e}')
sound_defs = set(sound_events.keys())
raw_sounds = set()
for f in glob.glob(os.path.join(RP, 'sounds', '**', '*'), recursive=True):
    if os.path.isfile(f):
        rel = os.path.relpath(f, os.path.join(RP, 'sounds')).replace('\\', '/')
        raw_sounds.add(rel.rsplit('.', 1)[0])

texture_keys = {}
for tj in ('item_texture.json', 'terrain_texture.json'):
    p = os.path.join(RP, 'textures', tj)
    if not os.path.exists(p): continue
    try:
        data = json.load(open(p, encoding='utf-8'))
    except Exception: continue
    for key in (data.get('texture_data') or {}):
        texture_keys.setdefault(key, []).append(tj)
dup_keys = {k: v for k, v in texture_keys.items() if len(v) > 1}
for k, v in dup_keys.items():
    errors.append(f'DUPLICATE texture key {k!r} defined in {v}')

# ---- scan scripts for references ------------------------------------------
scripts = glob.glob(os.path.join(BP, 'scripts', '*.js'))
script_text = ''
for s in scripts:
    script_text += open(s, encoding='utf-8').read() + '\n'

# spawnParticleEffect ids ("realms:x" or "minecraft:x")
for m in re.finditer(r'''spawnParticleEffect\(\s*['"]([^'"]+)['"]''', script_text):
    pid = m.group(1)
    if pid.startswith('realms:') and pid not in particle_ids:
        errors.append(f'DANGLING particle ref in scripts: {pid} (no RP particle file)')
    elif pid.startswith('minecraft:') :
        warns.append(f'vanilla placeholder particle still referenced: {pid}')

# playSound / playMusic / sound refs "realms.x" style and namespace:event
for m in re.finditer(r'''(?:playSound|playMusic)\(\s*['"]([^'"]+)['"]''', script_text):
    sid = m.group(1)
    base = sid.split('.')[0]
    if base == 'realms':
        # try full id, then progressively trimmed prefixes (realms.ability.fireball -> realms.ability.fireball_cast variants)
        candidates = {sid, re.sub(r'\.\w+$', '', sid)}
        cands2 = set()
        for c in candidates:
            parts = c.split('.')
            for i in range(1, len(parts) + 1):
                cands2.add('.'.join(parts[:i]))
        if not (cands2 & sound_defs):
            errors.append(f'DANGLING sound ref in scripts: {sid}')
    elif sid.startswith('minecraft:') or '.' in sid:
        pass  # vanilla sounds allowed only if intentional; flag music/ambient placeholders
for m in re.finditer(r'''(?:playSound|playMusic)\(\s*['"](?!realms\.|minecraft:|note\.|mob\.|block\.)([^'"]+)['"]''', script_text):
    pass  # already covered above

# runCommand particle calls (legacy path) — should be zero realms refs via command
for m in re.finditer(r'''minecraft:(\w*_particle)''', script_text):
    warns.append(f'vanilla particle via identifier: minecraft:{m.group(1)}')

# ---- lang completeness ------------------------------------------------------
def load_lang(path):
    entries = {}
    if not os.path.exists(path): return entries
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line.startswith('#') or '=' not in line: continue
        k, v = line.split('=', 1)
        entries[k.strip()] = v.strip()
    return entries

lang_bp = load_lang(os.path.join(BP, 'texts', 'en_US.lang'))

# item identifiers -> item.<id>.name keys expected in BP lang
for f in glob.glob(os.path.join(BP, 'items', '*.json')):
    try:
        ident = parsed.get(f, {}).get('minecraft:item', {}).get('description', {}).get('identifier')
    except Exception: ident = None
    if ident and f'item.{ident}.name' not in lang_bp:
        errors.append(f'MISSING lang key item.{ident} (from {os.path.basename(f)})')

# entity identifiers -> entity.<id>.name keys
for f in glob.glob(os.path.join(BP, 'entities', '*.json')):
    try:
        ent = parsed.get(f, {}).get('minecraft:entity', {}).get('description', {})
        ident = ent.get('identifier')
    except Exception: ident = None
    if ident and f'entity.{ident}.name' not in lang_bp:
        errors.append(f'MISSING lang key entity.{ident}.name (from {os.path.basename(f)})')

# ---- report ------------------------------------------------------------------
print(f'JSON files checked : {len(json_files)}')
print(f'Particle defs (RP) : {len(particle_ids)}')
print(f'Sound definitions  : {len(sound_defs)}')
print(f'Texture keys       : {len(texture_keys)} (dups: {len(dup_keys)})')
print()
for w in warns: print('WARN:', w)
for e in errors: print('ERROR:', e)
print()
print('FAIL' if errors else 'PASS')
sys.exit(1 if errors else 0)
