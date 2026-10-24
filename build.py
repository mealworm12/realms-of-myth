#!/usr/bin/env python3
"""
Build script for Realms of Myth .mcaddon package.
Strips .gitkeep files, creates BP/RP .mcpack files, bundles into .mcaddon.

The archive is written deterministically — entries sorted by path and every
entry stamped with a fixed timestamp — so rebuilding the same sources produces
a byte-identical .mcaddon. That makes release artifacts verifiable.
"""

import zipfile
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO_ROOT, "realms_of_myth_BP")
RP_DIR = os.path.join(REPO_ROOT, "realms_of_myth_RP")
OUT_DIR = REPO_ROOT

# 1980-01-01 is the earliest timestamp the ZIP format can represent; using a
# constant keeps rebuilds reproducible.
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def _collect(src_dir):
    """Return sorted (archive_name, absolute_path) pairs, skipping .gitkeep."""
    entries = []
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for f in sorted(files):
            if f == ".gitkeep":
                continue
            full = os.path.join(root, f)
            arcname = os.path.relpath(full, src_dir).replace(os.sep, "/")
            entries.append((arcname, full))
    entries.sort(key=lambda item: item[0])
    return entries


def _writestr(zf, arcname, data):
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def zip_dir(src_dir, dest_file):
    """Zip a directory into a .mcpack file, excluding .gitkeep."""
    entries = _collect(src_dir)
    with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, full in entries:
            with open(full, "rb") as fh:
                _writestr(zf, arcname, fh.read())
    return len(entries)


def main():
    print("Building Realms of Myth .mcaddon...\n")

    bp_pack = os.path.join(OUT_DIR, "BP.mcpack")
    rp_pack = os.path.join(OUT_DIR, "RP.mcpack")
    addon = os.path.join(OUT_DIR, "realms-of-myth.mcaddon")

    # Step 1: Create BP .mcpack
    print("[1/3] Packaging Behavior Pack...")
    bp_count = zip_dir(BP_DIR, bp_pack)
    print(f"       {bp_count} files")

    # Step 2: Create RP .mcpack
    print("[2/3] Packaging Resource Pack...")
    rp_count = zip_dir(RP_DIR, rp_pack)
    print(f"       {rp_count} files")

    # Step 3: Bundle into .mcaddon (deterministic order + timestamps)
    print("[3/3] Creating .mcaddon bundle...")
    with zipfile.ZipFile(addon, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, path in (("BP.mcpack", bp_pack), ("RP.mcpack", rp_pack)):
            with open(path, "rb") as fh:
                _writestr(zf, arcname, fh.read())

    # Clean up temp .mcpack files
    os.remove(bp_pack)
    os.remove(rp_pack)

    size_kb = os.path.getsize(addon) / 1024
    print(f"\n✅ Done! {addon} ({size_kb:.1f} KB, {bp_count + rp_count} files)")

if __name__ == '__main__':
    main()
