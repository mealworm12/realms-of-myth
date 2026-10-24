#!/usr/bin/env python3
"""
Static contract checks for the Realms of Myth behavior pack.

These checks exist because the pack targets a pinned script API version and a
wrong event name or a dimension-context command fails silently (or takes the
whole script module down) at runtime — neither shows up in a JSON validator.

Checks
------
1. Every .json file in both packs parses.
2. BP/RP manifests: required fields, module entry file exists, no duplicate
   UUIDs (header + modules, across both packs).
3. Every ``world.afterEvents.X`` / ``world.beforeEvents.X`` / ``system.*``
   subscription exists in the pinned API version (tools/api_contract.json).
4. ``dimension.runCommand(...)`` is not used with position-relative selectors
   (@p/@a/@e/@r): those resolve from the world origin, not the caller.
5. Every exported ``register*()`` hook is invoked somewhere in the pack.
6. Optional: ``node --check`` on each .js file when node is available.

Exit code 0 = all checks pass, 1 = at least one failure.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "realms_of_myth_BP")
RP = os.path.join(ROOT, "realms_of_myth_RP")
SCRIPTS = os.path.join(BP, "scripts")
CONTRACT = os.path.join(ROOT, "tools", "api_contract.json")

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


# --------------------------------------------------------------------------
# 1. JSON validity
# --------------------------------------------------------------------------
def check_json_files() -> None:
    count = 0
    for pack in (BP, RP):
        for dirpath, dirnames, filenames in os.walk(pack):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for name in filenames:
                if not name.endswith(".json"):
                    continue
                path = os.path.join(dirpath, name)
                count += 1
                try:
                    with open(path, encoding="utf-8") as fh:
                        json.load(fh)
                except Exception as exc:  # noqa: BLE001 - report any parse error
                    fail(f"{rel(path)}: invalid JSON ({exc})")
    notes.append(f"JSON files parsed: {count}")


# --------------------------------------------------------------------------
# 2. Manifests
# --------------------------------------------------------------------------
def check_manifests() -> None:
    seen: dict[str, str] = {}
    for pack, expected_modules in ((BP, {"data", "script"}), (RP, {"resources"})):
        path = os.path.join(pack, "manifest.json")
        if not os.path.exists(path):
            fail(f"{rel(path)}: missing")
            continue
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        for key in ("format_version", "header", "modules"):
            if key not in data:
                fail(f"{rel(path)}: missing '{key}'")
        header = data.get("header", {})
        for key in ("name", "uuid", "version", "min_engine_version"):
            if key not in header:
                fail(f"{rel(path)}: header missing '{key}'")

        uuids = [("header", header.get("uuid", ""))]
        for i, module in enumerate(data.get("modules", [])):
            uuids.append((f"modules[{i}]", module.get("uuid", "")))
            if module.get("type") == "script":
                entry = module.get("entry")
                if not entry:
                    fail(f"{rel(path)}: script module missing 'entry'")
                elif not os.path.exists(os.path.join(pack, entry)):
                    fail(f"{rel(path)}: script entry '{entry}' does not exist")

        module_types = {m.get("type") for m in data.get("modules", [])}
        missing = expected_modules - module_types
        if missing:
            fail(f"{rel(path)}: missing module type(s) {sorted(missing)}")

        for label, uuid in uuids:
            if not uuid:
                fail(f"{rel(path)}: {label} has no uuid")
                continue
            if uuid in seen:
                fail(f"duplicate UUID {uuid} in {rel(path)} ({label}) and {seen[uuid]}")
            seen[uuid] = f"{rel(path)} ({label})"


# --------------------------------------------------------------------------
# 3. Event contract
# --------------------------------------------------------------------------
EVENT_RE = re.compile(r"\b(world|system)\.(afterEvents|beforeEvents)\.([A-Za-z_][A-Za-z0-9_]*)")


def check_event_contract() -> None:
    with open(CONTRACT, encoding="utf-8") as fh:
        contract = json.load(fh)
    allowed = {
        ("world", "afterEvents"): set(contract["worldAfterEvents"]),
        ("world", "beforeEvents"): set(contract["worldBeforeEvents"]),
        # system before/after event names are stable and tiny; keep explicit.
        ("system", "afterEvents"): {"scriptEventReceive"},
        ("system", "beforeEvents"): {"shutdown", "startup"},
    }
    legacy = contract.get("allowedLegacy", {})

    for name in sorted(os.listdir(SCRIPTS)):
        if not name.endswith(".js"):
            continue
        path = os.path.join(SCRIPTS, name)
        text = open(path, encoding="utf-8").read()
        for match in EVENT_RE.finditer(text):
            obj, phase, event = match.groups()
            if event in allowed.get((obj, phase), set()):
                continue
            if event in legacy:
                # Only allowed as a fallback: the same line must offer a valid
                # primary event via `??`.
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.start())
                line = text[line_start: line_end if line_end != -1 else len(text)]
                if "??" in line:
                    notes.append(f"{name}: guarded legacy fallback {obj}.{phase}.{event}")
                    continue
            line_no = text.count("\n", 0, match.start()) + 1
            fail(
                f"{name}:{line_no}: {obj}.{phase}.{event} is not in the "
                f"@minecraft/server {contract['version']} contract"
            )


# --------------------------------------------------------------------------
# 4. Command origin lint
# --------------------------------------------------------------------------
DIM_COMMAND_RE = re.compile(
    r"\b(?:dim|dimension|player\.dimension|entity\.dimension)\.runCommand\(\s*[`'\"]([^`'\"]*)"
)
SELECTOR_RE = re.compile(r"@[pae](?:\[|\b)|@r(?:\[|\b)")


def check_command_origin() -> None:
    for name in sorted(os.listdir(SCRIPTS)):
        if not name.endswith(".js"):
            continue
        path = os.path.join(SCRIPTS, name)
        text = open(path, encoding="utf-8").read()
        for match in DIM_COMMAND_RE.finditer(text):
            command = match.group(1)
            if not SELECTOR_RE.search(command):
                continue
            if "execute positioned" in command or "execute at" in command:
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            fail(
                f"{name}:{line_no}: dimension-context command uses a relative "
                f"selector without 'execute positioned' — it will resolve from "
                f"world origin: {command[:90]}"
            )


# --------------------------------------------------------------------------
# 5. Registration hooks are called
# --------------------------------------------------------------------------
def check_registration_hooks() -> None:
    defined: list[tuple[str, str]] = []
    all_text: dict[str, str] = {}
    for name in sorted(os.listdir(SCRIPTS)):
        if not name.endswith(".js"):
            continue
        text = open(os.path.join(SCRIPTS, name), encoding="utf-8").read()
        all_text[name] = text
        for match in re.finditer(r"export function (register[A-Za-z0-9_]+)\s*\(", text):
            defined.append((match.group(1), name))

    for func, defining_file in defined:
        call_re = re.compile(rf"(?<!function )\b{func}\s*\(")
        called_in = [name for name, text in all_text.items() if call_re.search(text)]
        if not called_in:
            fail(f"{defining_file}: {func}() is exported but never called")


# --------------------------------------------------------------------------
# 6. JS syntax
# --------------------------------------------------------------------------
def check_js_syntax() -> None:
    node = shutil.which("node")
    if not node:
        notes.append("node not on PATH — JS syntax check skipped")
        return
    for name in sorted(os.listdir(SCRIPTS)):
        if not name.endswith(".js"):
            continue
        proc = subprocess.run(
            [node, "--check", os.path.join(SCRIPTS, name)],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            fail(f"{name}: node --check failed\n{proc.stderr.strip()}")


def main() -> int:
    check_json_files()
    check_manifests()
    check_event_contract()
    check_command_origin()
    check_registration_hooks()
    check_js_syntax()

    for note in notes:
        print(f"  · {note}")
    if failures:
        print(f"\nFAIL — {len(failures)} problem(s):")
        for item in failures:
            print(f"  ✗ {item}")
        return 1
    print("\nPASS — manifests, event contract, command origins, hooks, syntax")
    return 0


if __name__ == "__main__":
    sys.exit(main())
