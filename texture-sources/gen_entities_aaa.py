"""
Generate all 6 entity textures using the same hand-pixeled approach.
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
from gen_armor_aaa import hex_c
from gen_dragon_fire import draw_dragon_fire
import os, math

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
ENT = f'{RP}/textures/entity'

# ═══════════════════════════════════════════════════════════════════
# DRAGON FROST — 128x128, ice-blue palette
# ═══════════════════════════════════════════════════════════════════

def draw_dragon_frost():
    """Same anatomy as fire dragon but with frost palette."""
    c = PixelCanvas(128, 128, 4)
    body = M['dragonfrost']
    o = M['shadow'][0]
    flame = M['gem_frost']
    # Reuse dragon_fire logic but swap palette at the end
    img = draw_dragon_fire()
    # Recolor: replace dragonfire colors with dragonfrost
    px = img.load()
    fire_to_frost = {
        # 7-tone swaps
        '#3A0A00': '#0A1A2A',  # body[0]
        '#5A1A00': '#1A2A4A',  # body[1]
        '#7A2A10': '#2A4A6A',  # body[2]
        '#A04020': '#4080A0',  # body[3]
        '#D06030': '#60B0D0',  # body[4]
        '#FF8040': '#80D0E8',  # body[5]
        '#FFA060': '#B0F0FF',  # body[6]
    }
    # Find body pixels and recolor based on luminance (or just track which were red/orange)
    for y in range(128):
        for x in range(128):
            r, g, b, a = px[x, y]
            if a == 0: continue
            # Skip black (outline) and very dark (shadow)
            if (r, g, b) == (10, 10, 26): continue  # outline
            if (r, g, b) == (26, 26, 58): continue  # dark outline
            # Skip flame colors (yellow/orange — for frost, change to white/cyan)
            if r > 200 and g > 100 and b < 100:  # flame yellow
                px[x, y] = (220, 240, 255, 255)  # bright cyan
                continue
            if r > 200 and g > 100 and b > 50:  # orange flame
                px[x, y] = (160, 220, 240, 255)
                continue
            # Skip white flame
            if r > 240 and g > 240 and b < 200:
                px[x, y] = (240, 250, 255, 255)
                continue
            # Red->blue body recolor
            if r > g > b:  # reddish
                # Map based on intensity
                if r < 80: px[x, y] = (40, 80, 120, 255)
                elif r < 130: px[x, y] = (60, 120, 170, 255)
                elif r < 180: px[x, y] = (90, 160, 200, 255)
                elif r < 220: px[x, y] = (140, 200, 230, 255)
                else: px[x, y] = (180, 230, 250, 255)
            elif r > b and g > b:  # brownish
                # Mid-range
                avg = (r + g + b) // 3
                px[x, y] = (avg // 2 + 30, avg + 20, avg + 60, 255)
    return img

# ═══════════════════════════════════════════════════════════════════
# DRAGON WHELP — 64x64, scaled-down fire dragon
# ═══════════════════════════════════════════════════════════════════

def draw_dragon_whelp():
    """Hand-pixeled baby dragon, same pose as adult but at 64x64."""
    c = PixelCanvas(64, 64, 4)
    body = M['dragonfire']
    o = M['shadow'][0]
    flame = M['gem_fire']
    # HEAD (y=5-20)
    head_pixels = [
        # snout
        *[(x, 5) for x in range(30, 35)],
        *[(x, 6) for x in range(29, 36)],
        *[(x, 7) for x in range(28, 37)],
        *[(x, 8) for x in range(27, 38)],
        *[(x, 9) for x in range(26, 39)],
        *[(x, 10) for x in range(25, 40)],
        *[(x, 11) for x in range(24, 41)],
        *[(x, 12) for x in range(24, 41)],
        *[(x, 13) for x in range(25, 40)],
        *[(x, 14) for x in range(26, 39)],
        *[(x, 15) for x in range(28, 37)],
        *[(x, 16) for x in range(30, 35)],
        # neck
        *[(x, 17) for x in range(30, 35)],
        *[(x, 18) for x in range(30, 35)],
        *[(x, 19) for x in range(30, 35)],
        *[(x, 20) for x in range(30, 35)],
    ]
    for x, y in head_pixels:
        if y < 9: tone = body[5]
        elif y < 14: tone = body[3]
        else: tone = body[2]
        c.px(x, y, tone)
    # Head outline
    head_outline = [
        (30, 4), (31, 4), (32, 4), (33, 4), (34, 4),
        (29, 5), (35, 5), (28, 6), (36, 6), (27, 7), (37, 7), (26, 8), (38, 8),
        (25, 9), (39, 9), (24, 10), (40, 10), (23, 11), (41, 11), (23, 12), (41, 12),
        (24, 13), (40, 13), (25, 14), (39, 14), (26, 15), (38, 15), (28, 16), (36, 16),
        # Jaw
        (29, 17), (35, 17), (30, 18), (34, 18), (31, 19), (33, 19), (32, 20),
    ]
    for x, y in head_outline:
        c.px(x, y, o)
    # Eyes
    c.px(27, 9, flame[5]); c.px(28, 9, flame[5])
    c.px(36, 9, flame[5]); c.px(37, 9, flame[5])
    c.px(27, 10, o); c.px(36, 10, o)
    # Snout detail
    c.px(31, 7, body[6]); c.px(32, 7, body[6])
    # BODY (y=20-40)
    body_pixels = []
    for y in range(20, 41):
        if y < 24: rx = (y - 20) * 3 + 8
        elif y < 36: rx = 14
        else: rx = max(0, 14 - (y - 36) * 3)
        for x in range(32 - rx, 32 + rx + 1):
            body_pixels.append((x, y))
    for x, y in body_pixels:
        if 0 <= x < 64 and 0 <= y < 64:
            if y < 26: tone = body[4]
            elif y < 34: tone = body[3]
            else: tone = body[2]
            c.px(x, y, tone)
    # Body outline
    for y in range(20, 41):
        c.px(32 - 14, y, o); c.px(32 + 14, y, o)
    # WINGS (y=22-45)
    # Left wing
    for y in range(22, 46):
        for x in range(2, 22):
            if 0 <= x < 64 and 0 <= y < 64:
                # Wing shape: triangular
                if y < 30 and x > 5: c.px(x, y, body[2])
                elif y < 40: c.px(x, y, body[3])
                else: c.px(x, y, body[2])
    # Right wing
    for y in range(22, 46):
        for x in range(42, 62):
            if 0 <= x < 64 and 0 <= y < 64:
                if y < 30 and x < 58: c.px(x, y, body[2])
                elif y < 40: c.px(x, y, body[3])
                else: c.px(x, y, body[2])
    # Wing membranes
    c.line_diag(20, 30, 4, 25, body[1])
    c.line_diag(20, 30, 2, 35, body[1])
    c.line_diag(20, 30, 4, 42, body[1])
    c.line_diag(20, 30, 10, 45, body[1])
    c.line_diag(44, 30, 60, 25, body[1])
    c.line_diag(44, 30, 62, 35, body[1])
    c.line_diag(44, 30, 60, 42, body[1])
    c.line_diag(44, 30, 54, 45, body[1])
    # Wing outlines
    wing_l_outline = [(20, 30), (15, 25), (5, 23), (2, 30), (3, 38), (8, 42), (15, 45), (20, 38)]
    for i in range(len(wing_l_outline) - 1):
        x1, y1 = wing_l_outline[i]; x2, y2 = wing_l_outline[i+1]
        c.line_diag(x1, y1, x2, y2, o)
    wing_r_outline = [(44, 30), (49, 25), (59, 23), (62, 30), (61, 38), (56, 42), (49, 45), (44, 38)]
    for i in range(len(wing_r_outline) - 1):
        x1, y1 = wing_r_outline[i]; x2, y2 = wing_r_outline[i+1]
        c.line_diag(x1, y1, x2, y2, o)

    # LEGS (y=40-55)
    for leg_x in [24, 30, 34, 40]:
        for y in range(40, 55):
            c.px(leg_x, y, body[2])
            c.px(leg_x + 1, y, body[2])
        for y in [40, 54]:
            c.px(leg_x - 1, y, o); c.px(leg_x + 2, y, o)
        for y in range(40, 55):
            c.px(leg_x - 1, y, o); c.px(leg_x + 2, y, o)
    # Foot claws
    for leg_x in [24, 30, 34, 40]:
        c.px(leg_x - 1, 55, o); c.px(leg_x, 55, o); c.px(leg_x + 1, 55, o); c.px(leg_x + 2, 55, o)

    # TAIL (y=40-60)
    tail = [(45, 42), (48, 45), (50, 48), (52, 51), (54, 54), (55, 56)]
    for x, y in tail:
        c.px(x, y, body[3])
        c.px(x - 1, y, body[2])
    # Flame tip
    c.px(56, 56, flame[5]); c.px(57, 57, flame[6]); c.px(58, 58, flame[5])
    c.px(57, 58, hex_c('#FFFFE0'))

    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# ELF WARRIOR — 64x64
# ═══════════════════════════════════════════════════════════════════

def draw_elf_warrior():
    c = PixelCanvas(64, 64, 4)
    skin = M['skin_elf']
    armor = M['gem_nature']  # green
    armor_hi = M['gem_nature']  # we'll mix
    o = M['shadow'][0]
    gold = M['gold']
    # HEAD (y=4-18, with hair, pointed ears)
    # Hair (yellow-blond)
    hair = '#D8B868'
    hair_d = '#8A7038'
    for y in range(4, 14):
        for x in range(24, 40):
            c.px(x, y, hex_c(hair))
    # Hair outline
    c.line_diag(24, 4, 24, 13, hex_c(hair_d))
    c.line_diag(40, 4, 40, 13, hex_c(hair_d))
    # Face
    for y in range(13, 20):
        for x in range(25, 39):
            c.px(x, y, skin[3])
    # Pointed ears
    c.line_diag(24, 14, 19, 15, skin[3])
    c.line_diag(19, 15, 19, 18, skin[3])
    c.line_diag(19, 18, 24, 18, skin[3])
    c.line_diag(24, 18, 24, 14, skin[3])
    c.line_diag(40, 14, 45, 15, skin[3])
    c.line_diag(45, 15, 45, 18, skin[3])
    c.line_diag(45, 18, 40, 18, skin[3])
    # Eyes
    c.px(28, 16, hex_c('#202020')); c.px(28, 17, hex_c('#202020'))
    c.px(35, 16, hex_c('#202020')); c.px(35, 17, hex_c('#202020'))
    # Eye glints
    c.px(28, 16, hex_c('#80C0FF')); c.px(35, 16, hex_c('#80C0FF'))
    # Mouth
    c.px(31, 19, hex_c('#A06060'))
    # Head outline
    for y in range(4, 20):
        c.px(24, y, o); c.px(40, y, o)
    for x in range(24, 41):
        c.px(x, 4, o); c.px(x, 19, o)
    # Ear outlines
    c.px(19, 16, o); c.px(19, 17, o); c.px(45, 16, o); c.px(45, 17, o)
    # Hair detail
    c.px(28, 6, hex_c(hair_d)); c.px(35, 6, hex_c(hair_d))
    c.px(30, 4, hex_c(hair_d)); c.px(33, 4, hex_c(hair_d))

    # BODY (y=20-44)
    for y in range(20, 45):
        for x in range(24, 40):
            # Shoulder pads
            if y == 20: c.px(x, y, armor[4])
            elif y == 21: c.px(x, y, armor[3])
            elif y == 44: c.px(x, y, armor[1])
            else:
                if x == 24: c.px(x, y, armor[4])
                elif x == 39: c.px(x, y, armor[1])
                else: c.px(x, y, armor[2])
    # Gold trim (collar)
    for x in range(26, 38):
        c.px(x, 22, gold[3])
    # Chest emblem (gold leaf)
    c.px(31, 28, gold[5]); c.px(32, 28, gold[5])
    c.px(30, 29, gold[4]); c.px(31, 29, gold[4]); c.px(32, 29, gold[4]); c.px(33, 29, gold[4])
    c.px(31, 30, gold[4]); c.px(32, 30, gold[4])
    # Belt
    for x in range(24, 40):
        c.px(x, 38, hex_c('#1A0A00'))
    c.px(30, 38, gold[4]); c.px(33, 38, gold[4])
    # Body outline
    for y in [20, 21, 44]:
        for x in range(24, 41):
            c.px(x, y, o)
    for x in [23, 40]:
        for y in range(20, 45):
            c.px(x, y, o)
    # Arms
    for y in range(22, 40):
        c.px(20, y, armor[2])
        c.px(19, y, armor[2])
        c.px(43, y, armor[2])
        c.px(44, y, armor[2])
    # Hand (skin)
    c.px(20, 40, skin[3]); c.px(20, 41, skin[3])
    c.px(43, 40, skin[3]); c.px(43, 41, skin[3])
    # Hand outline
    c.px(19, 40, o); c.px(19, 41, o); c.px(20, 42, o); c.px(19, 42, o)
    c.px(44, 40, o); c.px(44, 41, o); c.px(43, 42, o); c.px(44, 42, o)

    # LEGS (y=45-58)
    for y in range(45, 58):
        for x in [28, 29, 34, 35]:
            c.px(x, y, armor[2])
        c.px(27, y, armor[1])
        c.px(36, y, armor[1])
    # Leg outlines
    for y in [45, 57]:
        for x in [27, 28, 29, 34, 35, 36]:
            c.px(x, y, o)
    for x in [27, 36]:
        for y in range(45, 58):
            c.px(x, y, o)

    # BOOTS (y=58-62)
    for x in [26, 27, 28, 29, 34, 35, 36, 37]:
        c.px(x, 58, hex_c('#3A2010'))
        c.px(x, 59, hex_c('#3A2010'))
    # Sole
    for x in [26, 27, 28, 29, 34, 35, 36, 37]:
        c.px(x, 60, hex_c('#1A0A00'))
    # Outline
    for x in [25, 38]:
        for y in range(58, 61):
            c.px(x, y, o)
    for x in range(25, 39):
        c.px(x, 60, o)

    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# TROLL BRUTE — 64x64
# ═══════════════════════════════════════════════════════════════════

def draw_troll_brute():
    c = PixelCanvas(64, 64, 4)
    skin = M['skin_orc']  # green
    leather = M['leather']
    o = M['shadow'][0]
    tusk = '#F0E0B0'
    # HEAD (y=4-18, large)
    # Hair (dark shaggy)
    hair = '#3A2818'
    for y in range(2, 9):
        for x in range(22, 42):
            c.px(x, y, hex_c(hair))
    # Head shape
    for y in range(8, 20):
        for x in range(22, 42):
            if x == 22 or x == 41: c.px(x, y, skin[1])  # shadow
            elif y == 8: c.px(x, y, skin[3])  # top
            elif y == 19: c.px(x, y, skin[1])  # bottom
            else: c.px(x, y, skin[2])
    # Eyes (orange)
    c.px(27, 14, hex_c('#FF6020')); c.px(28, 14, hex_c('#FF6020'))
    c.px(35, 14, hex_c('#FF6020')); c.px(36, 14, hex_c('#FF6020'))
    c.px(28, 14, hex_c('#000000')); c.px(36, 14, hex_c('#000000'))
    # Tusks
    c.px(28, 18, hex_c(tusk)); c.px(29, 18, hex_c(tusk))
    c.px(34, 18, hex_c(tusk)); c.px(35, 18, hex_c(tusk))
    # Head outline
    for y in range(2, 20):
        c.px(22, y, o); c.px(42, y, o)
    for x in range(22, 43):
        c.px(x, 2, o); c.px(x, 19, o)
    # Body (y=20-46, WIDE shoulders)
    for y in range(20, 47):
        for x in range(18, 46):
            if y == 20: c.px(x, y, skin[3])
            elif y == 46: c.px(x, y, skin[1])
            elif x == 18 or x == 45: c.px(x, y, skin[3])
            elif x == 19 or x == 44: c.px(x, y, skin[2])
            else: c.px(x, y, skin[2])
    # Leather harness (chest straps)
    for y in range(22, 26):
        for x in range(18, 46):
            c.px(x, y, leather[3])
    c.line_diag(18, 22, 46, 38, leather[1])  # diagonal strap
    c.line_diag(46, 22, 18, 38, leather[1])
    # Body outline
    for y in [20, 21, 46]:
        for x in [17, 18, 19, 20, 43, 44, 45, 46]:
            c.px(x, y, o)
    for x in [17, 46]:
        for y in range(20, 47):
            c.px(x, y, o)
    # Arms (very thick)
    for y in range(22, 44):
        for x in [12, 13, 14, 15, 48, 49, 50, 51]:
            if x in [12, 51]: c.px(x, y, skin[1])
            elif x in [13, 50]: c.px(x, y, skin[2])
            else: c.px(x, y, skin[3])
    # Wrist bands
    for x in [12, 13, 14, 15, 48, 49, 50, 51]:
        c.px(x, 42, leather[1])
        c.px(x, 43, leather[1])
    # Fists
    for x in [11, 12, 13, 14, 15, 16, 47, 48, 49, 50, 51, 52]:
        c.px(x, 44, skin[1])
        c.px(x, 45, skin[1])
    # Legs (thick, y=46-60)
    for y in range(46, 60):
        for x in [22, 23, 24, 25, 38, 39, 40, 41]:
            if x in [22, 41]: c.px(x, y, skin[1])
            elif x in [23, 40]: c.px(x, y, skin[2])
            else: c.px(x, y, skin[3])
    # Boots
    for x in [21, 22, 23, 24, 25, 26, 37, 38, 39, 40, 41, 42]:
        c.px(x, 60, leather[1])
        c.px(x, 61, leather[0])
    # Outline
    for x in [21, 42]:
        for y in range(60, 62):
            c.px(x, y, o)
    for x in range(21, 43):
        c.px(x, 61, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# GIANT COLOSSUS — 64x64
# ═══════════════════════════════════════════════════════════════════

def draw_giant_colossus():
    c = PixelCanvas(64, 64, 4)
    stone = M['stone']
    moss = M['gem_nature']
    o = M['shadow'][0]
    # HEAD (small, y=2-12)
    for y in range(2, 13):
        for x in range(24, 40):
            if y == 2: c.px(x, y, stone[5])
            elif y == 12: c.px(x, y, stone[1])
            elif x == 24: c.px(x, y, stone[4])
            elif x == 39: c.px(x, y, stone[2])
            else: c.px(x, y, stone[3])
    # Eyes (orange)
    c.px(28, 7, hex_c('#FF6020')); c.px(29, 7, hex_c('#FF6020'))
    c.px(35, 7, hex_c('#FF6020')); c.px(36, 7, hex_c('#FF6020'))
    c.px(28, 7, hex_c('#000000')); c.px(35, 7, hex_c('#000000'))
    # Brow (dark)
    for x in [26, 27, 28, 29, 35, 36, 37, 38]:
        c.px(x, 5, o)
    # Mouth (carved)
    for x in range(28, 36):
        c.px(x, 11, o)
    # Head outline
    for y in range(2, 13):
        c.px(24, y, o); c.px(40, y, o)
    for x in range(24, 41):
        c.px(x, 2, o); c.px(x, 12, o)

    # BODY (y=12-44, MASSIVE)
    for y in range(12, 45):
        for x in range(12, 52):
            if y == 12: c.px(x, y, stone[4])
            elif y == 44: c.px(x, y, stone[1])
            elif x < 16: c.px(x, y, stone[4])
            elif x > 47: c.px(x, y, stone[1])
            else: c.px(x, y, stone[2])
    # Body outline
    for y in [12, 44]:
        for x in [11, 12, 51, 52]:
            c.px(x, y, o)
    for x in [11, 52]:
        for y in range(12, 45):
            c.px(x, y, o)
    # Cracks
    c.line_diag(15, 18, 20, 24, stone[0])
    c.line_diag(38, 16, 44, 22, stone[0])
    c.line_diag(25, 30, 32, 38, stone[0])
    # Moss patches
    for x, y in [(18, 28), (20, 30), (40, 35), (42, 38), (16, 38), (45, 40)]:
        c.px(x, y, moss[3])
        c.px(x + 1, y, moss[2])

    # Arms (very thick)
    for y in range(14, 42):
        for x in [4, 5, 6, 7, 8, 56, 57, 58, 59, 60]:
            if x in [4, 60]: c.px(x, y, stone[2])
            elif x in [5, 59]: c.px(x, y, stone[2])
            else: c.px(x, y, stone[3])
    # Fists
    for y in range(40, 48):
        for x in range(2, 12):
            c.px(x, y, stone[2])
        for x in range(52, 62):
            c.px(x, y, stone[2])
    for x in [2, 11, 52, 61]:
        for y in range(40, 48):
            c.px(x, y, o)
    for y in [47]:
        for x in range(2, 62):
            c.px(x, y, o)
    # Legs (thick, y=44-62)
    for y in range(44, 62):
        for x in [18, 19, 20, 21, 22, 42, 43, 44, 45, 46]:
            if x in [18, 46]: c.px(x, y, stone[1])
            else: c.px(x, y, stone[2])
    # Leg outlines
    for x in [18, 46]:
        for y in range(44, 62):
            c.px(x, y, o)
    # Boots
    for y in [60, 61]:
        for x in [16, 17, 18, 19, 20, 21, 22, 23, 41, 42, 43, 44, 45, 46, 47, 48]:
            c.px(x, y, stone[1])
    for y in [62]:
        for x in [16, 23, 41, 48]:
            c.px(x, y, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# GENERATE
# ═══════════════════════════════════════════════════════════════════

def main():
    draw_dragon_fire().save(f'{ENT}/dragon_fire.png')
    draw_dragon_frost().save(f'{ENT}/dragon_frost.png')
    draw_dragon_whelp().save(f'{ENT}/dragon_whelp.png')
    draw_elf_warrior().save(f'{ENT}/elf_warrior.png')
    draw_troll_brute().save(f'{ENT}/troll_brute.png')
    draw_giant_colossus().save(f'{ENT}/giant_colossus.png')
    print(f"✅ Generated 6 entity textures")

if __name__ == '__main__':
    main()
