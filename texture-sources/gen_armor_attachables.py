"""
Emit minecraft:attachable definitions for all 28 armor pieces (7 sets x 4 slots).

Output: realms_of_myth_RP/attachables/<piece>.json

Binding follows vanilla armor conventions:
  helmet     -> geometry.humanoid.armor.helmet      + <set>_humanoid
  chestplate -> geometry.humanoid.armor.chestplate  + <set>_humanoid
                 (parent_setup hides the outer layer so chest renders alone)
  leggings   -> geometry.humanoid.armor.leggings    + <set>_humanoid_leggings
  boots      -> geometry.humanoid.armor.boots       + <set>_humanoid

Deterministic JSON output.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "realms_of_myth_RP", "attachables")
os.makedirs(OUT, exist_ok=True)

SETS = [
    "mythril", "dragonscale", "mage_master", "ranger_master",
    "berserker_master", "paladin_master", "druid_master",
]

SLOT_GEO = {
    "helmet": ("geometry.humanoid.armor.helmet", "{set}_humanoid"),
    "chestplate": ("geometry.humanoid.armor.chestplate", "{set}_humanoid"),
    "leggings": ("geometry.humanoid.armor.leggings", "{set}_humanoid_leggings"),
    "boots": ("geometry.humanoid.armor.boots", "{set}_humanoid"),
}

# Vanilla behaviour: wearing a chestplate alone must hide the leggings'
# outer layer; leggings re-enable it.
PARENT_SETUP = {
    "chestplate": "variable.chest_layer_visible = 0.0;",
    "leggings": "variable.chest_layer_visible = 1.0;",
}


def make(slot, set_name):
    geo, tex_tpl = SLOT_GEO[slot]
    piece = f"{set_name}_{slot}"
    desc = {
        "identifier": f"realms:{piece}",
        "materials": {"default": "armor", "enchanted": "armor_enchanted"},
        "textures": {
            "default": f"textures/armor/{tex_tpl.format(set=set_name)}",
            "enchanted": "textures/misc/enchanted_item_glint",
        },
        "geometry": {"default": geo},
        "render_controllers": ["controller.render.armor"],
    }
    if slot in PARENT_SETUP:
        desc["scripts"] = {"parent_setup": PARENT_SETUP[slot]}
    return {
        "format_version": "1.10.0",
        "minecraft:attachable": {"description": desc},
    }


def main():
    count = 0
    for set_name in SETS:
        for slot in SLOT_GEO:
            path = os.path.join(OUT, f"{set_name}_{slot}.json")
            with open(path, "w") as f:
                json.dump(make(slot, set_name), f, indent=2)
                f.write("\n")
            count += 1
    print(f"[armor-attachables] wrote {count} attachables -> {OUT}")


if __name__ == "__main__":
    main()
