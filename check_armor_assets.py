"""Verify all armor assets referenced by attachables exist, JSON parses,
and every BP armor piece has an icon + attachable. Exit non-zero on failure."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BP = os.path.join(ROOT, "realms_of_myth_BP", "armor")
RP_ITEMS = os.path.join(ROOT, "realms_of_myth_RP", "textures", "items")
RP_ARMOR = os.path.join(ROOT, "realms_of_myth_RP", "textures", "armor")
ATTACH = os.path.join(ROOT, "realms_of_myth_RP", "attachables")

errors = []

# 1. All BP armor JSONs parse
pieces = sorted(f for f in os.listdir(BP) if f.endswith(".json"))
if len(pieces) != 28:
    errors.append(f"expected 28 BP armor pieces, found {len(pieces)}")
for f in pieces:
    try:
        with open(os.path.join(BP, f)) as fh:
            data = json.load(fh)
        ident = data["minecraft:item"]["description"]["identifier"]
    except Exception as e:
        errors.append(f"BP {f}: {e}")
        continue
    name = ident.split(":")[1]
    # 2. icon exists
    if not os.path.exists(os.path.join(RP_ITEMS, name + ".png")):
        errors.append(f"missing item icon textures/items/{name}.png")
    # 3. attachable exists and parses; texture path resolves
    apath = os.path.join(ATTACH, name + ".json")
    if not os.path.exists(apath):
        errors.append(f"missing attachable {name}.json")
        continue
    try:
        with open(apath) as fh:
            adata = json.load(fh)
        adesc = adata["minecraft:attachable"]["description"]
    except Exception as e:
        errors.append(f"attachable {name}: {e}")
        continue
    if adesc["identifier"] != ident:
        errors.append(f"attachable identifier mismatch for {name}")
    tex = adesc["textures"]["default"] + ".png"
    if not os.path.exists(os.path.join(ROOT, "realms_of_myth_RP", tex)):
        errors.append(f"attachable texture missing: {tex}")

# 4. worn layers exist for all 7 sets
for s in ["mythril", "dragonscale", "mage_master", "ranger_master",
          "berserker_master", "paladin_master", "druid_master"]:
    for suffix in ("_humanoid.png", "_humanoid_leggings.png"):
        p = os.path.join(RP_ARMOR, s + suffix)
        if not os.path.exists(p):
            errors.append(f"missing worn layer {s}{suffix}")
        else:
            from PIL import Image
            im = Image.open(p)
            if im.size != (64, 32):
                errors.append(f"{s}{suffix} wrong size {im.size}")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: {len(pieces)} pieces verified (icons, attachables, worn layers, sizes)")
