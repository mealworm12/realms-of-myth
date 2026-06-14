"""
AAA block textures (32x32) for Realms of Myth.

3 blocks: ancient_altar, dragon_egg, mythril_ore

Each block:
- 32x32 target, 4x supersampled
- Multi-tone shading (5-7 tones)
- Detailed sub-features (cracks, veins, speckles, runes, stones)
- Proper "block" silhouette (filled, not floating)
- Outlined for definition
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
from gen_armor_aaa import hex_c
import os, math

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
BLOCKS = f'{RP}/textures/blocks'

# ═══════════════════════════════════════════════════════════════════
# MYTHRIL ORE — stone block with embedded blue crystals
# ═══════════════════════════════════════════════════════════════════

def draw_mythril_ore():
    c = PixelCanvas(32, 32, 4)
    stone = M['stone']
    o = M['shadow'][0]
    mythril = M['mythril']
    # Fill entire block with stone
    # Use noise pattern for natural variation
    import random
    random.seed(42)
    for y in range(32):
        for x in range(32):
            n = random.randint(0, 6)
            base_idx = 2 + (n % 4)  # varies between stone[2] and stone[5]
            c.px(x, y, stone[base_idx])
    # Cracks (random dark lines)
    crack_segments = [
        [(2, 3), (6, 3), (6, 6), (10, 6), (10, 10), (14, 10)],
        [(20, 1), (24, 1), (24, 4), (28, 4)],
        [(1, 16), (5, 16), (5, 20), (8, 20)],
        [(15, 22), (18, 22), (18, 26), (22, 26)],
        [(26, 14), (30, 14), (30, 18)],
        [(13, 28), (16, 28), (16, 30)],
    ]
    for seg in crack_segments:
        for i in range(len(seg) - 1):
            x1, y1 = seg[i]; x2, y2 = seg[i+1]
            c.line_diag(x1, y1, x2, y2, stone[1])
    # Crystal cluster 1 (top-left, large)
    # Main crystal cluster: 6-7x6 shape
    crystal_clusters = [
        # (cx, cy, radius)
        (6, 5, 3),
        (24, 11, 3),
        (12, 22, 3),
        (26, 25, 2),
        (5, 26, 2),
    ]
    for cx, cy, r in crystal_clusters:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                dx = x - cx
                dy = y - cy
                d = (dx*dx + dy*dy) ** 0.5
                if d < r * 0.4: c.px(x, y, mythril[6])  # center bright
                elif d < r * 0.7: c.px(x, y, mythril[5])
                elif d < r * 0.9: c.px(x, y, mythril[4])
                elif d < r + 0.5: c.px(x, y, mythril[3])
                elif d < r + 1.0: c.px(x, y, mythril[2])  # edge
        # Outline
        for y in range(cy - r - 1, cy + r + 2):
            for x in range(cx - r - 1, cx + r + 2):
                dx = x - cx
                dy = y - cy
                d = (dx*dx + dy*dy) ** 0.5
                if abs(d - r) < 1.2 and 0 <= x < 32 and 0 <= y < 32:
                    c.px(x, y, o)
    # Small specks
    for x, y in [(15, 5), (18, 18), (28, 8), (2, 12), (22, 30)]:
        c.px(x, y, mythril[4])
        c.px(x, y+1, mythril[3])
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# DRAGON EGG — full-block oval with red speckles
# ═══════════════════════════════════════════════════════════════════

def draw_dragon_egg():
    c = PixelCanvas(32, 32, 4)
    egg_base = '#D8C4A8'  # base egg color
    egg_dark = '#A88862'
    egg_hi = '#F0E4D0'
    o = M['shadow'][0]
    speckle = '#A02010'
    speckle_dark = '#600800'
    # Fill entire block with stone-ish background (since block is cube)
    for y in range(32):
        for x in range(32):
            # Dark rocky background
            if (x + y) % 7 == 0: c.px(x, y, M['stone'][1])
            elif (x * y) % 11 == 0: c.px(x, y, M['stone'][2])
            else: c.px(x, y, M['stone'][0])
    # Egg (oval, large, fills most of block)
    # Center: (15, 16), rx=12, ry=14
    for y in range(32):
        for x in range(32):
            dx = (x - 15) / 12.0
            dy = (y - 16) / 14.0
            d = dx*dx + dy*dy
            if d < 1.0:
                # Shading: top-left bright, bottom-right dark
                if dx + dy < -0.5: c.px(x, y, hex_c(egg_hi))
                elif dx + dy < 0.0: c.px(x, y, hex_c(egg_base))
                elif dx + dy < 0.5: c.px(x, y, hex_c(egg_dark))
                else: c.px(x, y, hex_c(speckle_dark))
    # Egg outline
    for y in range(32):
        for x in range(32):
            dx = (x - 15) / 12.0
            dy = (y - 16) / 14.0
            d = dx*dx + dy*dy
            if 0.95 < d < 1.10 and 0 <= x < 32 and 0 <= y < 32:
                c.px(x, y, o)
    # Red speckles across the egg
    speckles = [
        (9, 8), (10, 9), (11, 7), (12, 10), (13, 8), (14, 9), (15, 7), (16, 10), (17, 8), (18, 9), (19, 7), (20, 10), (21, 8), (22, 9),
        (8, 13), (9, 14), (10, 13), (11, 15), (12, 14), (13, 13), (14, 14), (15, 13), (16, 14), (17, 13), (18, 15), (19, 14), (20, 13), (21, 14), (22, 13),
        (7, 17), (8, 18), (9, 17), (10, 19), (11, 18), (12, 17), (13, 19), (14, 18), (15, 17), (16, 19), (17, 18), (18, 17), (19, 19), (20, 18), (21, 17), (22, 19), (23, 18),
        (8, 22), (9, 23), (10, 22), (11, 24), (12, 23), (13, 22), (14, 24), (15, 23), (16, 22), (17, 24), (18, 23), (19, 22), (20, 24), (21, 23), (22, 22),
        (10, 27), (11, 28), (12, 27), (13, 29), (14, 28), (15, 27), (16, 29), (17, 28), (18, 27), (19, 29), (20, 28),
    ]
    for x, y in speckles:
        c.px(x, y, hex_c(speckle))
    # Darker speckles
    dark_speckles = [(7, 11), (16, 16), (11, 19), (20, 21), (15, 26), (8, 21), (24, 13), (22, 26)]
    for x, y in dark_speckles:
        c.px(x, y, hex_c(speckle_dark))
    # Top highlight (specular)
    c.px(13, 6, hex_c('#FFFAF0')); c.px(14, 6, hex_c('#FFFAF0')); c.px(15, 6, hex_c('#FFFAF0'))
    c.px(13, 7, hex_c('#FFFAF0')); c.px(14, 7, hex_c('#FFFAF0')); c.px(15, 7, hex_c('#FFFAF0')); c.px(16, 7, hex_c('#FFFAF0'))
    c.px(14, 8, hex_c('#FFFAF0')); c.px(15, 8, hex_c('#FFFAF0'))
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# ANCIENT ALTAR — stone altar with glowing runes
# ═══════════════════════════════════════════════════════════════════

def draw_ancient_altar():
    c = PixelCanvas(32, 32, 4)
    stone = M['stone']
    gold = M['gold']
    gem = M['gem_frost']  # cyan magic gem
    o = M['shadow'][0]
    # Background (top portion is altar top, bottom is stone)
    # Altar top (rows 0-7)
    for y in range(8):
        for x in range(32):
            if y == 0: c.px(x, y, stone[5])  # top highlight
            elif y == 7: c.px(x, y, stone[1])  # bottom shadow of top
            else:
                if x == 0: c.px(x, y, stone[4])
                elif x == 31: c.px(x, y, stone[2])
                else: c.px(x, y, stone[3])
    # Top surface gold border (rows 1 and 6)
    for x in range(1, 31):
        c.px(x, 1, gold[3])
        c.px(x, 6, gold[3])
    c.px(0, 1, gold[2]); c.px(31, 1, gold[2])
    c.px(0, 6, gold[2]); c.px(31, 6, gold[2])
    # Gold corner studs
    c.px(0, 0, gold[5]); c.px(31, 0, gold[5])
    c.px(0, 7, gold[1]); c.px(31, 7, gold[1])
    # Central rune (top surface, rows 2-5)
    # Diamond pattern in cyan
    rune_pixels = [
        (15, 2), (16, 2),
        (14, 3), (15, 3), (16, 3), (17, 3),
        (13, 4), (14, 4), (15, 4), (16, 4), (17, 4), (18, 4),
        (14, 5), (15, 5), (16, 5), (17, 5),
        (15, 6), (16, 6),  # wait, row 6 is border
    ]
    # Adjust rune to fit rows 2-5
    rune_pixels = [
        (15, 2), (16, 2),
        (14, 3), (15, 3), (16, 3), (17, 3),
        (13, 4), (14, 4), (15, 4), (16, 4), (17, 4), (18, 4),
        (14, 5), (15, 5), (16, 5), (17, 5),
    ]
    for x, y in rune_pixels:
        dx = abs(x - 15.5); dy = abs(y - 3.5)
        d = (dx*dx + dy*dy) ** 0.5
        if d < 0.7: c.px(x, y, gem[6])  # brightest
        elif d < 1.5: c.px(x, y, gem[5])
        elif d < 2.5: c.px(x, y, gem[4])
        else: c.px(x, y, gem[3])
    # Side body (rows 8-31)
    for y in range(8, 32):
        for x in range(32):
            if x == 0: c.px(x, y, stone[2])
            elif x == 31: c.px(x, y, stone[1])
            else:
                # Top vs bottom shading
                t = (y - 8) / 24
                base_idx = 2 if t < 0.5 else 1
                if x < 4 or x > 27:
                    c.px(x, y, stone[base_idx + 1])  # column
                else:
                    c.px(x, y, stone[base_idx])
    # Vertical columns (rows 8-31)
    for y in range(8, 32):
        for x in range(3, 7):
            c.px(x, y, stone[4])
            c.px(x, y - 1, stone[2]) if y > 8 else None
        for x in range(25, 29):
            c.px(x, y, stone[4])
    # Column outlines
    c.line_diag(3, 8, 3, 31, o)
    c.line_diag(6, 8, 6, 31, o)
    c.line_diag(25, 8, 25, 31, o)
    c.line_diag(28, 8, 28, 31, o)
    # Central vertical beam (rune) on side
    for y in range(11, 30):
        c.px(15, y, gem[5])
        c.px(16, y, gem[5])
    # Side rune accents
    for y in [12, 16, 20, 24, 28]:
        c.px(2, y, gem[4])
        c.px(29, y, gem[4])
        c.px(2, y+1, gem[3]); c.px(29, y+1, gem[3])
    # Outline of altar top edge (horizontal lines at row 7 and 8)
    for x in range(32):
        c.px(x, 7, o)
    # Bottom outline
    for x in range(32):
        c.px(x, 31, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# GENERATE
# ═══════════════════════════════════════════════════════════════════

def main():
    draw_mythril_ore().save(f'{BLOCKS}/mythril_ore.png')
    draw_dragon_egg().save(f'{BLOCKS}/dragon_egg.png')
    draw_ancient_altar().save(f'{BLOCKS}/ancient_altar.png')
    print(f"✅ Generated 3 block textures (32x32)")

if __name__ == '__main__':
    main()
