#!/usr/bin/env python3
"""Cross-check RP/sounds.json entries against actual WAV files."""
import json, os, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "realms_of_myth_RP")

with open(os.path.join(RP, "sounds.json")) as f:
    data = json.load(f)

errors = []
for sid, entry in data.items():
    for snd in entry.get("sounds", []):
        name = snd["name"] if isinstance(snd, dict) else snd
        p = os.path.join(RP, name + ".wav")
        if not os.path.exists(p):
            errors.append(f"{sid}: missing file {name}.wav")
            continue
        with wave.open(p) as w:
            if w.getframerate() != 22050 or w.getnchannels() != 1 or w.getsampwidth() != 2:
                errors.append(f"{sid}: bad format in {name}.wav")

# orphan check: wav files under sounds/ not referenced anywhere
referenced = set()
for entry in data.values():
    for snd in entry.get("sounds", []):
        referenced.add(snd["name"] if isinstance(snd, dict) else snd)
sound_dir = os.path.join(RP, "sounds")
orphans = []
for root, _, files in os.walk(sound_dir):
    for fn in files:
        if not fn.endswith(".wav"):
            continue
        rel = os.path.relpath(os.path.join(root, fn), RP)[:-4]
        if rel not in referenced:
            orphans.append(rel)

print(f"sounds.json events: {len(data)}")
if errors:
    print("ERRORS:")
    [print(" ", e) for e in errors]
if orphans:
    print("ORPHAN wavs (not in sounds.json):")
    [print(" ", o) for o in orphans]
if not errors and not orphans:
    print("OK: all references resolve, all formats PCM 22050Hz mono 16-bit, no orphans.")
sys.exit(1 if errors else 0)
