#!/usr/bin/env python3
"""
Build script for Realms of Myth .mcaddon package.
Strips .gitkeep files, creates BP/RP .mcpack files, bundles into .mcaddon.
"""

import zipfile
import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.join(REPO_ROOT, "realms_of_myth_BP")
RP_DIR = os.path.join(REPO_ROOT, "realms_of_myth_RP")
OUT_DIR = REPO_ROOT

def zip_dir(src_dir, dest_file):
    """Zip a directory into a .mcpack file, excluding .gitkeep."""
    count = 0
    with zipfile.ZipFile(dest_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            # Skip .git directories
            dirs[:] = [d for d in dirs if d != '.git']
            for f in files:
                if f == '.gitkeep':
                    continue
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, src_dir)
                zf.write(full, arcname)
                count += 1
    return count

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

    # Step 3: Bundle into .mcaddon
    print("[3/3] Creating .mcaddon bundle...")
    with zipfile.ZipFile(addon, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(bp_pack, "BP.mcpack")
        zf.write(rp_pack, "RP.mcpack")

    # Clean up temp .mcpack files
    os.remove(bp_pack)
    os.remove(rp_pack)

    size_kb = os.path.getsize(addon) / 1024
    print(f"\n✅ Done! {addon} ({size_kb:.1f} KB, {bp_count + rp_count} files)")

if __name__ == '__main__':
    main()
