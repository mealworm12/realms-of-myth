#!/usr/bin/env python3
"""Content-schema checks for Bedrock 1.21.60+ / script API 2.x.

These rules were established by booting the pack on Bedrock Dedicated Server
1.26.52.3 and reading its content log. They catch the failure modes that a
generic JSON validator cannot:

  * item definitions outside ``items/`` (armour in ``armor/`` never registers)
  * removed item components (``minecraft:armor``) and bad enchantable slots
  * menu_category.group without the ``minecraft:itemGroup`` namespace
  * recipes without ``unlock`` data (1.20+ requires it)
  * BP entity sound components (moved to the RP client entity)
  * ``run_command`` inside entity events (must be ``queue_command``)
  * unsupported script-module versions for the pinned engine
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "realms_of_myth_BP")
RP = os.path.join(ROOT, "realms_of_myth_RP")
ITEMS = os.path.join(BP, "items")
ENTITIES = os.path.join(BP, "entities")
RECIPES = os.path.join(BP, "recipes")

ENCHANT_SLOTS = {
    "none", "all", "g_armor", "armor_head", "armor_torso", "armor_feet",
    "armor_legs", "sword", "bow", "spear", "crossbow", "melee_spear", "g_tool",
    "hoe", "shears", "flintsteel", "shield", "g_digging", "axe", "pickaxe",
    "shovel", "fishing_rod", "carrot_stick", "elytra", "cosmetic_head",
}
REMOVED_ITEM_COMPONENTS = {"minecraft:armor", "minecraft:protection"}
BP_SOUND_COMPONENTS = {"minecraft:ambient_sound", "minecraft:hurt_sound", "minecraft:death_sound"}
SUPPORTED_SERVER = {"2.4.0", "2.5.0", "2.6.0", "2.7.0", "2.8.0", "2.9.0", "2.10.0"}
MIN_SERVER_UI = (2, 0, 0)

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def load(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_manifests() -> None:
    bp = load(os.path.join(BP, "manifest.json"))
    for dep in bp.get("dependencies", []):
        name, version = dep.get("module_name"), dep.get("version", "")
        if name == "@minecraft/server" and version not in SUPPORTED_SERVER:
            fail(f"manifest: @minecraft/server {version} is not exposed by current engines "
                 f"(supported: {', '.join(sorted(SUPPORTED_SERVER))})")
        if name == "@minecraft/server-ui":
            parts = tuple(int(p) for p in version.split("."))
            if parts < MIN_SERVER_UI:
                fail(f"manifest: @minecraft/server-ui {version} is not exposed by current "
                     f"engines (minimum 2.0.0)")
    notes.append(f"script API: {[d['version'] for d in bp.get('dependencies', [])]}")


def check_item_locations() -> None:
    legacy = os.path.join(BP, "armor")
    if os.path.isdir(legacy):
        fail("behavior pack: 'armor/' folder exists — Bedrock only loads item "
             "definitions from 'items/'; those items will not register")
    for name in sorted(os.listdir(ITEMS)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(ITEMS, name)
        data = load(path)
        item = data.get("minecraft:item")
        if not item:
            continue
        desc = item.get("description", {})
        ident = desc.get("identifier", name)
        comps = item.get("components", {})

        for removed in REMOVED_ITEM_COMPONENTS & set(comps):
            fail(f"{name}: '{removed}' is removed in format 1.21.60 (use "
                 f"minecraft:wearable.protection for defence)")

        enc = comps.get("minecraft:enchantable")
        if isinstance(enc, dict):
            slot = enc.get("slot")
            if slot not in ENCHANT_SLOTS:
                fail(f"{name} ({ident}): enchantable.slot '{slot}' is not a valid slot")

        group = desc.get("menu_category", {}).get("group")
        if group and not group.startswith("minecraft:"):
            fail(f"{name}: menu_category.group '{group}' needs a namespace "
                 f"(e.g. minecraft:itemGroup.name.ore)")

        wearable = comps.get("minecraft:wearable")
        if isinstance(wearable, dict):
            if "protection" not in wearable:
                fail(f"{name}: armour item is missing wearable.protection (defence points)")
            slot = wearable.get("slot", "")
            if not slot.startswith("slot.armor"):
                fail(f"{name}: wearable.slot '{slot}' is not an armour slot")


def check_recipes() -> None:
    count = 0
    for name in sorted(os.listdir(RECIPES)):
        if not name.endswith(".json"):
            continue
        count += 1
        data = load(os.path.join(RECIPES, name))
        for key, body in data.items():
            if not key.startswith("minecraft:recipe") or not isinstance(body, dict):
                continue
            if "unlock" not in body:
                fail(f"{name}: recipe has no 'unlock' data (required since 1.20)")


def check_entities() -> None:
    for name in sorted(os.listdir(ENTITIES)):
        if not name.endswith(".json"):
            continue
        data = load(os.path.join(ENTITIES, name))
        ent = data.get("minecraft:entity", {})
        comps = ent.get("components", {})
        for comp in BP_SOUND_COMPONENTS & set(comps):
            fail(f"{name}: '{comp}' is not in the current BP entity schema — "
                 f"move audio to RP/entity/*.entity.json 'sounds'")

        def walk(events: dict, trail: str = "") -> None:
            for event_name, body in events.items():
                if not isinstance(body, dict):
                    continue
                if "run_command" in body:
                    fail(f"{name}: event '{trail}{event_name}' uses run_command — "
                         f"current schema requires queue_command")
                if "sequence" in body and isinstance(body["sequence"], list):
                    for i, step in enumerate(body["sequence"]):
                        if isinstance(step, dict) and "run_command" in step:
                            fail(f"{name}: event '{trail}{event_name}.sequence[{i}]' uses "
                                 f"run_command — requires queue_command")
                walk(body.get("sequence", []) if isinstance(body.get("sequence"), dict) else {},
                     trail + event_name + ".")

        walk(ent.get("events", {}))


def main() -> int:
    check_manifests()
    check_item_locations()
    check_recipes()
    check_entities()

    for note in notes:
        print(f"  · {note}")
    if failures:
        print(f"\nFAIL — {len(failures)} content problem(s):")
        for item in failures:
            print(f"  ✗ {item}")
        return 1
    print("\nPASS — item locations, item components, recipe unlocks, entity events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
