"""
AAA-quality armor textures for Realms of Myth.

7 armor sets × 4 pieces = 28 textures:
- mythril (silver-blue)
- dragonscale (red dragon leather)
- mage_master (purple arcane)
- ranger_master (forest green)
- berserker_master (blood red)
- paladin_master (gold)
- druid_master (deep green)

Each piece (helmet, chestplate, leggings, boots):
- 16x16 target, 8x supersampled
- Multi-tone shading (5-7 tones)
- Distinct silhouette per piece
- Detail (rivets, plates, fabric folds)
- Outlines for definition
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
import os

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
ITEMS = f'{RP}/textures/items'

# ═══════════════════════════════════════════════════════════════════
# ARMOR PIECE DRAWERS
# ═══════════════════════════════════════════════════════════════════

def draw_helmet(base_color, hi_color, lo_color, out_color, accent_color, has_horn=False, has_visor=True):
    """16x16 knight-style helmet with visor slit + crest + horn studs."""
    c = PixelCanvas(16, 16, 8)
    # Dome (rows 2-9, cols 3-12)
    for y in range(2, 10):
        for x in range(3, 13):
            if y == 2: c.px(x, y, hi_color)  # top highlight
            elif y == 9: c.px(x, y, lo_color)  # bottom shadow
            else:
                if x == 3: c.px(x, y, hi_color)  # left highlight
                elif x == 12: c.px(x, y, lo_color)  # right shadow
                else: c.px(x, y, base_color)  # main
    # Visor slit
    for x in range(5, 11):
        c.px(x, 6, out_color)
        c.px(x, 7, out_color)
    # Eye glints
    c.px(6, 7, accent_color); c.px(9, 7, accent_color)
    # Decoration band
    for x in range(4, 12):
        c.px(x, 4, accent_color)
    c.px(4, 4, hi_color); c.px(11, 4, hi_color)
    # Crest (top center, rows 0-1)
    c.px(7, 0, accent_color); c.px(8, 0, accent_color)
    c.px(7, 1, accent_color); c.px(8, 1, hi_color)
    if has_horn:
        c.px(4, 1, lo_color); c.px(4, 2, lo_color)
        c.px(11, 1, lo_color); c.px(11, 2, lo_color)
    # Outline
    for y in [1, 10]:
        for x in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]: c.px(x, y, out_color)
    for x in [2, 13]:
        for y in range(2, 10): c.px(x, y, out_color)
    # Cheek plates
    c.px(2, 9, base_color); c.px(13, 9, base_color)
    c.px(2, 10, lo_color); c.px(13, 10, lo_color)
    c.px(1, 10, out_color); c.px(14, 10, out_color)
    return c.finish()

def draw_chestplate(base_color, hi_color, lo_color, out_color, accent_color, has_emblem=True, style='plate', variant='standard'):
    """16x16 chestplate with shoulders, body, belt, and center seam.
    variant options: standard, spiked (berserker), rune (mage), leaf (druid), sun (paladin)
    """
    c = PixelCanvas(16, 16, 8)
    if style == 'plate':
        # Shoulders (rows 3-4, cols 1-14)
        for y in [3, 4]:
            for x in range(1, 15):
                if y == 3: c.px(x, y, hi_color)
                else: c.px(x, y, base_color)
        # Pauldrons (round shoulder caps)
        c.px(1, 5, base_color); c.px(14, 5, base_color)
        c.px(2, 5, hi_color); c.px(13, 5, hi_color)
        # Body (rows 5-13, cols 3-12)
        for y in range(5, 14):
            for x in range(3, 13):
                if x == 3: c.px(x, y, hi_color)
                elif x == 12: c.px(x, y, lo_color)
                else: c.px(x, y, base_color)
        # Center seam
        for y in range(5, 13):
            c.px(7, y, lo_color); c.px(8, y, lo_color)
        # Belt (row 11-12)
        for x in range(3, 13):
            c.px(x, 11, lo_color)
            c.px(x, 12, out_color)
        c.px(7, 11, accent_color); c.px(8, 11, accent_color)  # buckle
        # Outline
        for y in [2, 13]:
            for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]: c.px(x, y, out_color)
        for x in [0, 1, 14, 15]:
            for y in range(3, 14): c.px(x, y, out_color)
        # Arms (sides, rows 6-12)
        c.px(2, 6, base_color); c.px(2, 7, base_color); c.px(2, 8, base_color); c.px(2, 9, base_color); c.px(2, 10, base_color)
        c.px(2, 11, base_color); c.px(2, 12, base_color)
        c.px(13, 6, base_color); c.px(13, 7, base_color); c.px(13, 8, base_color); c.px(13, 9, base_color); c.px(13, 10, base_color)
        c.px(13, 11, base_color); c.px(13, 12, base_color)
        # Variant-specific details
        if variant == 'spiked':
            # Spikes on shoulders (rows 2-3)
            c.px(2, 2, out_color); c.px(2, 3, out_color)
            c.px(13, 2, out_color); c.px(13, 3, out_color)
            c.px(5, 2, out_color); c.px(10, 2, out_color)
            # Banded plate (rows 7-8)
            c.px(3, 7, lo_color); c.px(4, 7, lo_color); c.px(5, 7, lo_color); c.px(6, 7, lo_color)
            c.px(9, 7, lo_color); c.px(10, 7, lo_color); c.px(11, 7, lo_color); c.px(12, 7, lo_color)
        elif variant == 'rune':
            # Glowing runes on body
            c.px(6, 7, accent_color); c.px(9, 7, accent_color)
            c.px(7, 8, accent_color); c.px(8, 8, accent_color)
            c.px(6, 9, accent_color); c.px(9, 9, accent_color)
        elif variant == 'leaf':
            # Vine/leaf pattern
            c.px(5, 6, accent_color); c.px(10, 6, accent_color)
            c.px(5, 9, accent_color); c.px(10, 9, accent_color)
            c.px(4, 8, accent_color); c.px(11, 8, accent_color)
        elif variant == 'sun':
            # Sun emblem with rays
            c.px(7, 6, accent_color); c.px(8, 6, accent_color)
            c.px(6, 7, accent_color); c.px(7, 7, hi_color); c.px(8, 7, hi_color); c.px(9, 7, accent_color)
            c.px(7, 8, accent_color); c.px(8, 8, accent_color)
            c.px(5, 7, accent_color); c.px(10, 7, accent_color)
        elif variant == 'forest':
            # Leaf cluster
            c.px(7, 6, accent_color); c.px(8, 6, accent_color); c.px(7, 7, accent_color); c.px(8, 7, accent_color)
        if has_emblem:
            # Center emblem
            c.px(7, 8, accent_color); c.px(8, 8, accent_color)
    elif style == 'robe':
        # Robe style (wider at bottom)
        # Shoulders (rows 3-4, cols 2-13)
        for y in [3, 4]:
            for x in range(2, 14):
                if y == 3: c.px(x, y, hi_color)
                else: c.px(x, y, base_color)
        # Body widens
        for y in range(5, 14):
            width = (y - 5) // 2 + 1
            for x in range(3 - width//2, 13 + width//2):
                if 0 <= x <= 15:
                    if x < 7: c.px(x, y, hi_color)
                    elif x > 8: c.px(x, y, lo_color)
                    else: c.px(x, y, base_color)
        # Belt
        for x in range(3, 13):
            c.px(x, 10, out_color)
        c.px(7, 10, accent_color); c.px(8, 10, accent_color)
        # Outline
        for y in [2, 13]:
            for x in range(1, 15): c.px(x, y, out_color)
    return c.finish()

def draw_leggings(base_color, hi_color, lo_color, out_color, accent_color):
    """16x16 leggings — pants shape with belt + knee details."""
    c = PixelCanvas(16, 16, 8)
    # Waist (rows 2-4, cols 3-12)
    for y in range(2, 5):
        for x in range(3, 13):
            if y == 2: c.px(x, y, hi_color)
            elif y == 4: c.px(x, y, lo_color)
            else: c.px(x, y, base_color)
    # Legs (rows 5-13, two columns)
    # Left leg
    for y in range(5, 14):
        for x in [3, 4, 5, 6]:
            if x == 3: c.px(x, y, hi_color)
            elif x == 6: c.px(x, y, lo_color)
            else: c.px(x, y, base_color)
    # Right leg
    for y in range(5, 14):
        for x in [9, 10, 11, 12]:
            if x == 9: c.px(x, y, hi_color)
            elif x == 12: c.px(x, y, lo_color)
            else: c.px(x, y, base_color)
    # Center gap (rows 5-13)
    for y in range(5, 14): c.px(7, y, out_color); c.px(8, y, out_color)
    # Belt (row 4)
    for x in range(3, 13): c.px(x, 4, out_color)
    c.px(7, 4, accent_color); c.px(8, 4, accent_color)  # buckle
    c.px(3, 4, lo_color); c.px(12, 4, lo_color)  # belt ends
    # Knee pads (rows 8-9)
    c.rect(4, 8, 2, 2, accent_color)  # left knee
    c.px(4, 8, hi_color); c.px(5, 9, lo_color)
    c.rect(10, 8, 2, 2, accent_color)  # right knee
    c.px(10, 8, hi_color); c.px(11, 9, lo_color)
    # Boot tops (rows 13-14)
    for y in [13]:
        for x in [3, 4, 5, 6]: c.px(x, y, lo_color)
        for x in [9, 10, 11, 12]: c.px(x, y, lo_color)
    # Outline
    for y in [1, 5]:
        for x in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]: c.px(x, y, out_color)
    for x in [2, 13]:
        for y in range(2, 14): c.px(x, y, out_color)
    for y in [13]:
        for x in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]: c.px(x, y, out_color)
    return c.finish()

def draw_boots(base_color, hi_color, lo_color, out_color, accent_color):
    """16x16 boots — pair with cuff + sole + accent."""
    c = PixelCanvas(16, 16, 8)
    # Left boot
    for y in range(5, 13):
        for x in [2, 3, 4, 5, 6]:
            if x == 2: c.px(x, y, hi_color)
            elif x == 6: c.px(x, y, lo_color)
            else: c.px(x, y, base_color)
    # Right boot
    for y in range(5, 13):
        for x in [9, 10, 11, 12, 13]:
            if x == 9: c.px(x, y, hi_color)
            elif x == 13: c.px(x, y, lo_color)
            else: c.px(x, y, base_color)
    # Cuffs (row 5)
    for x in [2, 3, 4, 5, 6]: c.px(x, 5, lo_color)
    for x in [9, 10, 11, 12, 13]: c.px(x, 5, lo_color)
    # Soles (row 13-14)
    for x in range(2, 8): c.px(x, 13, out_color); c.px(x, 14, out_color)
    for x in range(8, 14): c.px(x, 13, out_color); c.px(x, 14, out_color)
    # Sole detail
    c.px(2, 14, accent_color); c.px(13, 14, accent_color)
    c.px(7, 14, accent_color); c.px(8, 14, accent_color)
    # Buckle (row 7)
    c.px(4, 7, accent_color); c.px(11, 7, accent_color)
    c.px(4, 8, accent_color); c.px(11, 8, accent_color)
    # Outline
    for y in [4, 12]:
        for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]: c.px(x, y, out_color)
    for x in [1, 14]:
        for y in range(5, 13): c.px(x, y, out_color)
    for y in [14]:
        for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]: c.px(x, y, out_color)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# ARMOR SET DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

ARMOR_SETS = {
    'mythril': dict(
        base='#6A7A88', hi='#9AB0C0', lo='#4A5A68', out='#1A2A38', accent='#D4AF37',
    ),
    'dragonscale': dict(
        base='#6A1A1A', hi='#A04030', lo='#3A0A0A', out='#1A0000', accent='#D4AF37',
    ),
    'mage_master': dict(
        base='#3A1068', hi='#7A40B0', lo='#1A0040', out='#0A0020', accent='#E0A0FF',
    ),
    'ranger_master': dict(
        base='#5A4020', hi='#9A7840', lo='#3A2810', out='#1A0A00', accent='#80E040',  # BROWN/LEATHER
    ),
    'berserker_master': dict(
        base='#8A2A2A', hi='#D04040', lo='#4A0A0A', out='#2A0000', accent='#FF8040',
    ),
    'paladin_master': dict(
        base='#B09030', hi='#FFD700', lo='#604010', out='#2A1000', accent='#FFF080',
    ),
    'druid_master': dict(
        base='#2A5A4A', hi='#5AA08A', lo='#0A2A1A', out='#001A10', accent='#80FFC0',  # teal/forest
    ),
}

# ═══════════════════════════════════════════════════════════════════
# GENERATE
# ═══════════════════════════════════════════════════════════════════

def hex_c(h):
    return hex_to_rgba(h)

def make_armor():
    count = 0
    variants = {
        'mythril': ('plate', 'standard'),
        'dragonscale': ('plate', 'spiked'),
        'mage_master': ('robe', 'rune'),
        'ranger_master': ('plate', 'forest'),
        'berserker_master': ('plate', 'spiked'),
        'paladin_master': ('plate', 'sun'),
        'druid_master': ('robe', 'leaf'),
    }
    for set_name, pal in ARMOR_SETS.items():
        base = hex_c(pal['base']); hi = hex_c(pal['hi']); lo = hex_c(pal['lo']); out = hex_c(pal['out']); accent = hex_c(pal['accent'])
        # Helmet
        img = draw_helmet(base, hi, lo, out, accent, has_horn=(set_name in ['paladin_master', 'berserker_master']))
        img.save(f'{ITEMS}/{set_name}_helmet.png')
        # Chestplate
        style, variant = variants[set_name]
        img = draw_chestplate(base, hi, lo, out, accent, has_emblem=True, style=style, variant=variant)
        img.save(f'{ITEMS}/{set_name}_chestplate.png')
        # Leggings
        img = draw_leggings(base, hi, lo, out, accent)
        img.save(f'{ITEMS}/{set_name}_leggings.png')
        # Boots
        img = draw_boots(base, hi, lo, out, accent)
        img.save(f'{ITEMS}/{set_name}_boots.png')
        count += 4
    print(f"✅ Generated {count} armor pieces with variants")

if __name__ == '__main__':
    make_armor()
