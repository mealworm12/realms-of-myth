"""
Complete AAA weapon generator — all 10 weapons using the proven pixel-by-pixel
methodology from draw_mythril_sword.

Each weapon:
- 16x16 target size, 8x supersampled
- Tapered blade with proper proportions
- Multi-tone shading (3-5 tones per material)
- Center detail (fuller, rune, gem)
- Outlined for definition
- Distinctive shape per weapon type
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
from PIL import Image, ImageDraw
import os

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
ITEMS = f'{RP}/textures/items'

# ═══════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════

def fill_rect(c, x1, y1, x2, y2, color, fn=None):
    """Fill rectangle from (x1,y1) to (x2,y2) inclusive. fn=function(x,y)->color."""
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            if fn: c.px(x, y, fn(x, y))
            else: c.px(x, y, color)

def fill_triangle(c, points, color, fn=None):
    """Fill triangle with vertices at (x,y) points."""
    # Simple scanline triangle
    pts = sorted(points, key=lambda p: p[1])
    if len(pts) < 3: return
    x1, y1 = pts[0]
    x2, y2 = pts[1]
    x3, y3 = pts[2]
    for y in range(min(y1, y2, y3), max(y1, y2, y3) + 1):
        # Find x range at this y
        xs = []
        for (xa, ya), (xb, yb) in [(pts[0], pts[1]), (pts[1], pts[2]), (pts[0], pts[2])]:
            if ya == yb: continue
            if min(ya, yb) <= y <= max(ya, yb):
                t = (y - ya) / (yb - ya)
                xs.append(xa + t * (xb - xa))
        if len(xs) >= 2:
            xs.sort()
            for x in range(int(min(xs)), int(max(xs)) + 1):
                if 0 <= x <= 15 and 0 <= y <= 15:
                    if fn: c.px(x, y, fn(x, y))
                    else: c.px(x, y, color)

# ═══════════════════════════════════════════════════════════════════
# SWORDS — mythril, dragonbone, shadowfang
# ═══════════════════════════════════════════════════════════════════

def draw_mythril_sword():
    c = PixelCanvas(16, 16, 8)
    m, g, l, o = M['mythril'], M['gold'], M['leather'], M['shadow'][0]
    # Blade rows 0-9, taper to point
    blade = [(0,8,8),(1,7,8),(2,7,8),(3,6,9),(4,6,9),(5,6,9),(6,6,9),(7,6,9),(8,6,9),(9,6,9)]
    for y, x1, x2 in blade:
        for x in range(x1, x2+1):
            if x < 7: c.px(x, y, m[4])
            elif x == 7: c.px(x, y, m[5])
            elif x == 8: c.px(x, y, m[3])
            else: c.px(x, y, m[1])
    for y, x1, x2 in blade:
        c.px(x1, y, o); 
        if x1 != x2: c.px(x2, y, o)
    for y in range(2, 10): c.px(7, y, m[2])  # fuller
    c.px(7, 3, m[6]); c.px(7, 4, m[5])  # specular
    # Crossguard rows 9-10
    for x in range(2, 14):
        c.px(x, 9, g[4]); c.px(x, 10, g[2])
    c.px(7, 9, g[5]); c.px(6, 9, g[4]); c.px(8, 9, g[3])
    for y in [9, 10]:
        for x in [1, 14]: c.px(x, y, g[0])
    for x in [2, 13]: c.px(x, 9, g[5]); c.px(x, 10, g[1])  # end caps
    c.rect(7, 9, 1, 1, hex_to_rgba('#40A0E0'))  # gem
    c.px(6, 9, hex_to_rgba('#80E0FF')); c.px(8, 9, hex_to_rgba('#2080A0'))
    # Grip rows 11-13
    for y in range(11, 14):
        for x in [6, 7, 8, 9]:
            if x == 6: c.px(x, y, l[5])
            elif x == 9: c.px(x, y, l[2])
            else: c.px(x, y, l[3])
    c.line_diag(6, 13, 9, 11, l[1])
    c.line_diag(6, 11, 9, 9, l[1])  # not needed
    for y in [10, 14]:
        for x in [5, 6, 7, 8, 9, 10]: c.px(x, y, o)
    for x in [5, 10]:
        for y in [11, 12, 13]: c.px(x, y, o)
    # Pommel rows 14-15
    for y in [14, 15]:
        for x in [5, 6, 7, 8, 9, 10]: c.px(x, y, g[3])
    c.px(5, 14, g[5]); c.px(6, 14, g[5])
    c.px(10, 14, g[1]); c.px(10, 15, g[1])
    c.px(7, 14, hex_to_rgba('#40A0E0')); c.px(8, 14, hex_to_rgba('#40A0E0'))
    for x in [4, 11]:
        for y in [14, 15]: c.px(x, y, o)
    c.px(5, 13, o); c.px(10, 13, o)
    return c.finish()

def draw_dragon_bone_greatsword():
    c = PixelCanvas(16, 16, 8)
    bone, o, ember, l = M['bone'], M['shadow'][0], M['gem_fire'], M['leather']
    # Bigger blade (greatsword = 1px wider, longer)
    blade = [(0,8,8),(1,7,8),(2,6,9),(3,6,9),(4,6,9),(5,6,9),(6,5,10),(7,5,10),(8,5,10),(9,5,10),(10,5,10)]
    for y, x1, x2 in blade:
        for x in range(x1, x2+1):
            # Shade by horizontal position
            mid = (x1 + x2) / 2
            if x < mid: c.px(x, y, bone[5])  # hi
            elif x == int(mid): c.px(x, y, bone[4])
            elif x == int(mid)+1: c.px(x, y, bone[3])
            else: c.px(x, y, bone[2])  # shadow
    for y, x1, x2 in blade:
        c.px(x1, y, o)
        if x1 != x2: c.px(x2, y, o)
    # Center fuller (dark line)
    for y in range(3, 11): c.px(7, y, bone[2])
    # Ember runes (glowing dots on blade)
    c.px(7, 4, ember[5])
    c.px(7, 6, ember[4])
    c.px(7, 8, ember[5])
    # Crossguard (dark bone, rows 10-11)
    for x in range(2, 14):
        c.px(x, 10, bone[3]); c.px(x, 11, bone[1])
    c.px(7, 10, bone[4]); c.px(6, 10, bone[3]); c.px(8, 10, bone[2])
    for y in [10, 11]:
        for x in [1, 14]: c.px(x, y, o)
    c.px(2, 10, bone[4]); c.px(13, 10, bone[4])
    # Wrap-wrapped handle (rows 12-13)
    for y in range(12, 14):
        for x in [6, 7, 8, 9]:
            if x == 6: c.px(x, y, l[5])
            elif x == 9: c.px(x, y, l[2])
            else: c.px(x, y, l[3])
    c.line_diag(6, 13, 9, 11, l[1])
    for y in [11, 14]:
        for x in [5, 6, 7, 8, 9, 10]: c.px(x, y, o)
    for x in [5, 10]:
        for y in [12, 13]: c.px(x, y, o)
    # Bone pommel (rows 15)
    for x in [5, 6, 7, 8, 9, 10]: c.px(x, 15, bone[3])
    c.px(5, 15, bone[4]); c.px(10, 15, bone[1])
    c.rect(7, 15, 2, 1, ember[3])  # ember in pommel
    c.px(5, 14, o); c.px(10, 14, o); c.px(4, 15, o); c.px(11, 15, o)
    return c.finish()

def draw_shadowfang_dagger():
    c = PixelCanvas(16, 16, 8)
    s, o, gem = M['shadow'], M['shadow'][0], M['gem_shadow']
    # Curved dagger (longer blade with a slight curve)
    blade = [
        (0, 8, 8),  # tip
        (1, 7, 8),
        (2, 7, 9),  # slight curve right
        (3, 7, 9),
        (4, 7, 9),
        (5, 6, 9),  # widen
        (6, 6, 9),
        (7, 6, 9),
        (8, 6, 9),
        (9, 6, 9),  # base
    ]
    for y, x1, x2 in blade:
        for x in range(x1, x2+1):
            mid = (x1 + x2) / 2
            if x < mid: c.px(x, y, s[5])
            elif x <= mid + 0.5: c.px(x, y, s[4])
            else: c.px(x, y, s[2])
    for y, x1, x2 in blade:
        c.px(x1, y, o)
        if x1 != x2: c.px(x2, y, o)
    for y in range(2, 10): c.px(7, y, s[1])  # dark fuller
    # Purple gem on blade
    c.px(7, 4, gem[5])
    c.px(7, 6, gem[4])
    # Crossguard (dark, narrow, rows 9-10)
    for x in range(3, 13):
        c.px(x, 9, s[2]); c.px(x, 10, s[0])
    c.px(7, 9, s[3])
    for y in [9, 10]:
        for x in [2, 13]: c.px(x, y, o)
    c.px(3, 9, s[3]); c.px(12, 9, s[3])
    # Wraith handle (rows 11-13, dark with purple wrapping)
    for y in range(11, 14):
        for x in [6, 7, 8, 9]:
            if x == 6: c.px(x, y, s[4])
            elif x == 9: c.px(x, y, s[1])
            else: c.px(x, y, s[2])
    # Purple wrap
    c.px(7, 12, gem[4])
    c.line_diag(6, 13, 9, 11, s[0])
    for y in [10, 14]:
        for x in [5, 6, 7, 8, 9, 10]: c.px(x, y, o)
    for x in [5, 10]:
        for y in [11, 12, 13]: c.px(x, y, o)
    # Wraith pommel
    for x in [5, 6, 7, 8, 9, 10]: c.px(x, 15, s[2])
    c.px(5, 15, s[3]); c.px(10, 15, s[1])
    c.rect(7, 15, 2, 1, gem[3])  # purple gem
    c.px(5, 14, o); c.px(10, 14, o); c.px(4, 15, o); c.px(11, 15, o)
    return c.finish()

def draw_elven_dagger():
    c = PixelCanvas(16, 16, 8)
    s, o, gem = M['silver'], M['shadow'][0], M['gem_nature']
    # Slim curved elven blade
    blade = [
        (1, 7, 8),
        (2, 7, 8),
        (3, 6, 9),
        (4, 6, 9),
        (5, 6, 9),
        (6, 6, 9),
        (7, 6, 9),
        (8, 6, 9),
    ]
    for y, x1, x2 in blade:
        for x in range(x1, x2+1):
            if x == 6: c.px(x, y, s[5])
            elif x == 7: c.px(x, y, s[4])
            elif x == 8: c.px(x, y, s[3])
            else: c.px(x, y, s[2])
    # Tip
    c.px(7, 0, s[4]); c.px(8, 0, s[4])
    c.px(7, 1, s[5])
    for y, x1, x2 in blade:
        c.px(x1, y, o)
        if x1 != x2: c.px(x2, y, o)
    # Nature gem embedded
    c.px(7, 3, gem[5])
    c.px(7, 5, gem[4])
    # Wrap-style guard
    for x in range(4, 12):
        c.px(x, 9, s[2]); c.px(x, 10, s[0])
    c.px(7, 9, s[4])
    for y in [9, 10]:
        for x in [3, 12]: c.px(x, y, o)
    # Wood/leather handle
    wood = M['wood']
    for y in range(11, 13):
        for x in [6, 7, 8, 9]:
            if x == 6: c.px(x, y, wood[5])
            elif x == 9: c.px(x, y, wood[2])
            else: c.px(x, y, wood[3])
    c.line_diag(6, 12, 9, 10, wood[1])
    for y in [10, 13]:
        for x in [5, 6, 7, 8, 9, 10]: c.px(x, y, o)
    for x in [5, 10]:
        for y in [11, 12]: c.px(x, y, o)
    # Leaf pommel
    for x in [5, 6, 7, 8, 9, 10]: c.px(x, 13, gem[3])
    c.px(5, 13, gem[4]); c.px(6, 13, gem[4])
    c.px(10, 13, gem[2])
    c.px(4, 13, o); c.px(11, 13, o); c.px(5, 12, o); c.px(10, 12, o)
    # Wrap at 14-15
    for x in [6, 7, 8, 9]: c.px(x, 14, wood[2])
    c.px(6, 14, wood[3]); c.px(9, 14, wood[1])
    c.px(5, 14, o); c.px(10, 14, o); c.px(7, 14, o); c.px(8, 14, o)
    c.px(6, 15, o); c.px(7, 15, o); c.px(8, 15, o); c.px(9, 15, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# HEAVY WEAPONS — hammer, club, greatsword (already done above)
# ═══════════════════════════════════════════════════════════════════

def draw_troll_warhammer():
    c = PixelCanvas(16, 16, 8)
    s, o, l, dark = M['stone'], M['shadow'][0], M['leather'], M['steel']
    # Big blocky head (rows 0-7, cols 1-14)
    for y in range(0, 8):
        for x in range(1, 15):
            if x < 3 or (x < 4 and y < 3): c.px(x, y, s[5])  # top-left highlight
            elif x > 12 or (x > 11 and y > 4): c.px(x, y, s[1])  # bottom-right shadow
            else: c.px(x, y, s[3])  # main
    # 4 corner rivets
    for cx, cy in [(2, 2), (13, 2), (2, 6), (13, 6)]:
        c.px(cx, cy, dark[5])
        c.px(cx - 1 if cx < 8 else cx + 1, cy, dark[3])
    # Center gem
    c.px(7, 3, hex_to_rgba('#A04020')); c.px(8, 3, hex_to_rgba('#A04020'))
    c.px(7, 4, hex_to_rgba('#D06030')); c.px(8, 4, hex_to_rgba('#D06030'))
    # Outline
    for x in [0, 15]:
        for y in range(0, 8): c.px(x, y, o)
    for y in [-1, 8]:  # 0 and 8
        for x in range(0, 16): c.px(x, y, o)
    # Binding rows 7-8 (metal band)
    for x in range(3, 13):
        c.px(x, 7, dark[3]); c.px(x, 8, dark[1])
    c.px(7, 7, dark[4]); c.px(8, 7, dark[4])
    for y in [7, 8]:
        for x in [2, 13]: c.px(x, y, o)
    # Handle rows 9-14
    for y in range(9, 15):
        for x in [7, 8]:
            if x == 7: c.px(x, y, l[4])
            else: c.px(x, y, l[1])
    # Wrap detail
    c.px(7, 11, l[5]); c.px(8, 11, l[5])
    c.px(7, 13, l[2]); c.px(8, 13, l[2])
    for y in [9, 14]:
        for x in [6, 7, 8, 9]: c.px(x, y, o)
    for x in [6, 9]:
        for y in [9, 10, 11, 12, 13, 14]: c.px(x, y, o)
    # Pommel
    for x in [6, 7, 8, 9]: c.px(x, 15, dark[3])
    c.px(6, 15, dark[4]); c.px(9, 15, dark[1])
    c.px(5, 15, o); c.px(10, 15, o); c.px(6, 14, o); c.px(9, 14, o)
    return c.finish()

def draw_giant_club():
    c = PixelCanvas(16, 16, 8)
    wood, o, dark = M['wood'], M['shadow'][0], M['steel']
    # Big wooden head (rows 0-8) with steel bands
    for y in range(0, 9):
        for x in range(1, 15):
            if x < 3: c.px(x, y, wood[5])
            elif x > 12: c.px(x, y, wood[1])
            else: c.px(x, y, wood[3])
    # Wood grain
    c.px(4, 2, wood[1]); c.px(7, 3, wood[1]); c.px(10, 4, wood[1])
    c.px(5, 5, wood[1]); c.px(8, 6, wood[1]); c.px(11, 7, wood[1])
    # Spikes on top
    c.px(2, 0, dark[3]); c.px(5, 0, dark[3]); c.px(8, 0, dark[3]); c.px(11, 0, dark[3]); c.px(13, 0, dark[3])
    # Steel bands (rows 1 and 7)
    for x in range(1, 15):
        c.px(x, 1, dark[4]); c.px(x, 7, dark[4])
        c.px(x, 0, dark[3]) if x not in [2, 5, 8, 11, 13] else None
    # Rivets in bands
    c.px(3, 1, dark[6]); c.px(12, 1, dark[6])
    c.px(3, 7, dark[6]); c.px(12, 7, dark[6])
    # Outline
    for y in range(0, 9):
        c.px(0, y, o); c.px(15, y, o)
    # Handle rows 9-15
    for y in range(9, 16):
        for x in [7, 8]:
            if x == 7: c.px(x, y, wood[5])
            else: c.px(x, y, wood[2])
    # Wrap
    c.px(7, 11, wood[6]); c.px(8, 11, wood[1])
    c.px(7, 13, wood[2]); c.px(8, 13, wood[6])
    for y in [9, 15]:
        for x in [6, 7, 8, 9]: c.px(x, y, o)
    for x in [6, 9]:
        for y in [9, 10, 11, 12, 13, 14, 15]: c.px(x, y, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# BOWS — curved with arrow
# ═══════════════════════════════════════════════════════════════════

def draw_mythril_bow():
    c = PixelCanvas(16, 16, 8)
    wood, o, arrow, m, g = M['wood'], M['shadow'][0], M['wood'], M['mythril'], M['gold']
    # Bow limb (curved C shape on left, 2px wide)
    bow_pixels = [
        # (x, y)
        # Upper limb
        (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5), (1, 6),
        # Grip
        (2, 7), (2, 8), (2, 9), (2, 10),
        # Lower limb
        (1, 10), (1, 11), (1, 12), (2, 12), (2, 13), (2, 14),
    ]
    for x, y in bow_pixels:
        if x == 1: c.px(x, y, wood[2])  # outer shadow
        else: c.px(x, y, wood[4])  # main
    # Bow grip wrap (center)
    for y in [7, 8, 9]:
        c.px(2, y, hex_to_rgba('#5A3015'))  # dark wrap
    # String (vertical white line at x=3)
    for y in range(2, 14):
        c.px(3, y, hex_to_rgba('#F0F0F0'))
    # Bow tips
    c.px(1, 0, m[4]); c.px(1, 14, m[4])
    # Outline
    for x, y in bow_pixels: c.px(x, y, o) if (x, y) in [(1, 3), (1, 12), (2, 1), (2, 14)] else None
    # Arrow nocked (right side, horizontal)
    # Shaft
    for x in range(3, 14):
        c.px(x, 7, wood[4])
        c.px(x, 8, wood[2])
    c.px(3, 6, wood[3]); c.px(3, 9, wood[3])  # nock end
    # Arrowhead (cols 14-15)
    c.px(14, 6, m[4]); c.px(14, 7, m[5]); c.px(14, 8, m[5]); c.px(14, 9, m[4])
    c.px(15, 6, m[3]); c.px(15, 7, m[5]); c.px(15, 8, m[5]); c.px(15, 9, m[3])
    # Fletching
    c.px(3, 6, hex_to_rgba('#E04030')); c.px(4, 6, hex_to_rgba('#E04030'))
    c.px(3, 9, hex_to_rgba('#E04030')); c.px(4, 9, hex_to_rgba('#E04030'))
    return c.finish()

def draw_enchanted_bow():
    c = PixelCanvas(16, 16, 8)
    o, m, g, gem = M['shadow'][0], M['arcane'], M['gold'], M['gem_arcane']
    # Bow limb (purple arcane)
    bow_pixels = [
        (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5), (1, 6),
        (2, 7), (2, 8), (2, 9), (2, 10),
        (1, 10), (1, 11), (1, 12), (2, 12), (2, 13), (2, 14),
    ]
    for x, y in bow_pixels:
        if x == 1: c.px(x, y, m[1])  # outer shadow
        else: c.px(x, y, m[3])  # main
    # Gold grip
    for y in [7, 8, 9]:
        c.px(2, y, g[3])
    # String
    for y in range(2, 14):
        c.px(3, y, hex_to_rgba('#F0F0F0'))
    # Bow tips
    c.px(1, 0, gem[5]); c.px(1, 14, gem[5])
    # Arrow (purple shaft)
    for x in range(3, 14):
        c.px(x, 7, m[3])
        c.px(x, 8, m[1])
    c.px(3, 6, m[2]); c.px(3, 9, m[2])
    # Arrowhead
    c.px(14, 6, gem[5]); c.px(14, 7, gem[6]); c.px(14, 8, gem[6]); c.px(14, 9, gem[5])
    c.px(15, 6, gem[4]); c.px(15, 7, gem[6]); c.px(15, 8, gem[6]); c.px(15, 9, gem[4])
    # Fletching (purple)
    c.px(3, 6, gem[4]); c.px(4, 6, gem[3])
    c.px(3, 9, gem[4]); c.px(4, 9, gem[3])
    # Glow particles
    c.px(2, 0, gem[6]); c.px(0, 7, gem[5]); c.px(2, 14, gem[6])
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# STAFF & SPEAR
# ═══════════════════════════════════════════════════════════════════

def draw_magic_staff():
    c = PixelCanvas(16, 16, 8)
    wood, o, g, gem = M['wood'], M['shadow'][0], M['gold'], M['gem_arcane']
    # Crystal head (top, rows 0-4, diamond shape)
    crystal_pixels = [
        (7, 0), (8, 0),  # tip
        (6, 1), (7, 1), (8, 1), (9, 1),
        (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),  # widest
        (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
        (6, 4), (7, 4), (8, 4), (9, 4),  # narrows
    ]
    for x, y in crystal_pixels:
        # Shade by position relative to center
        dx = abs(x - 7.5)
        if dx < 1: c.px(x, y, gem[6])  # center highlight
        elif dx < 1.5: c.px(x, y, gem[4])
        else: c.px(x, y, gem[2])  # outer shadow
    # Outline
    c.px(7, -1, o); c.px(8, -1, o)  # none, out of bounds
    c.px(5, 2, o); c.px(10, 2, o)
    c.px(5, 3, o); c.px(10, 3, o)
    c.px(6, 4, o); c.px(9, 4, o)
    c.px(7, 0, o); c.px(8, 0, o)
    # Inner facet highlight
    c.px(7, 2, hex_to_rgba('#FFFFFF'))
    c.px(8, 1, hex_to_rgba('#E8C0FF'))
    # Crystal collar (gold, row 5)
    for x in range(4, 12): c.px(x, 5, g[3])
    c.px(4, 5, g[4]); c.px(11, 5, g[4])
    c.px(7, 5, g[5]); c.px(8, 5, g[5])
    for x in [3, 12]: c.px(x, 5, o)
    # Shaft (rows 6-15)
    for y in range(6, 16):
        c.px(7, y, wood[4])
        c.px(8, y, wood[2])
    # Wrap detail
    c.px(7, 9, wood[5]); c.px(8, 9, wood[1])
    c.px(7, 12, wood[5]); c.px(8, 12, wood[1])
    # Outline
    for y in [6, 15]:
        for x in [6, 7, 8, 9]: c.px(x, y, o)
    for x in [6, 9]:
        for y in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]: c.px(x, y, o)
    # Pommel
    c.px(6, 15, g[3]); c.px(7, 15, g[3]); c.px(8, 15, g[3]); c.px(9, 15, g[3])
    c.px(6, 15, g[4]); c.px(9, 15, g[1])
    c.px(5, 15, o); c.px(10, 15, o); c.px(6, 14, o); c.px(9, 14, o)
    return c.finish()

def draw_dragonslayer_spear():
    c = PixelCanvas(16, 16, 8)
    o, m, l = M['shadow'][0], M['silver'], M['leather']
    # Spear tip (rows 0-4, triangular)
    tip_pixels = [
        (7, 0), (8, 0),  # point
        (6, 1), (7, 1), (8, 1), (9, 1),
        (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),
        (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
        (6, 4), (7, 4), (8, 4), (9, 4),  # narrows
    ]
    for x, y in tip_pixels:
        dx = abs(x - 7.5)
        if dx < 1: c.px(x, y, m[6])
        elif dx < 2: c.px(x, y, m[5])
        else: c.px(x, y, m[3])
    # Red gem in center
    c.px(7, 2, hex_to_rgba('#E02020')); c.px(8, 2, hex_to_rgba('#E02020'))
    c.px(7, 1, hex_to_rgba('#FF6040'))
    # Outline
    c.px(7, -1, o); c.px(8, -1, o)
    c.px(5, 2, o); c.px(10, 2, o)
    c.px(5, 3, o); c.px(10, 3, o)
    c.px(6, 4, o); c.px(9, 4, o)
    # Binding (row 5)
    for x in range(5, 11): c.px(x, 5, m[3])
    c.px(5, 5, m[4]); c.px(10, 5, m[4])
    c.px(7, 5, m[5]); c.px(8, 5, m[5])
    for x in [4, 11]: c.px(x, 5, o)
    # Shaft (rows 6-15)
    for y in range(6, 16):
        c.px(7, y, l[3])
        c.px(8, y, l[1])
    # Wrap detail
    c.px(7, 9, l[4]); c.px(8, 9, l[0])
    c.px(7, 12, l[4]); c.px(8, 12, l[0])
    # Outline
    for y in [6, 15]:
        for x in [6, 7, 8, 9]: c.px(x, y, o)
    for x in [6, 9]:
        for y in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]: c.px(x, y, o)
    # Pommel
    c.px(6, 15, m[3]); c.px(7, 15, m[3]); c.px(8, 15, m[3]); c.px(9, 15, m[3])
    c.px(6, 15, m[4]); c.px(9, 15, m[1])
    c.px(5, 15, o); c.px(10, 15, o); c.px(6, 14, o); c.px(9, 14, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# MATERIALS
# ═══════════════════════════════════════════════════════════════════

def draw_mythril_ingot():
    c = PixelCanvas(16, 16, 8)
    m, o = M['mythril'], M['shadow'][0]
    # Bar shape: rows 5-11, cols 2-13
    for y in range(5, 12):
        for x in range(2, 14):
            if y == 5: c.px(x, y, m[5])  # top highlight
            elif y == 11: c.px(x, y, m[2])  # bottom shadow
            else:
                # Left hi, right shadow
                if x == 2: c.px(x, y, m[4])
                elif x == 13: c.px(x, y, m[2])
                else: c.px(x, y, m[3])
    # Inset detail
    for y in [7, 8, 9]:
        for x in range(4, 12):
            c.px(x, y, m[2])
    c.px(4, 7, m[3]); c.px(11, 7, m[3])
    c.px(4, 9, m[1]); c.px(11, 9, m[1])
    # Outline
    for x in [1, 14]:
        for y in range(5, 12): c.px(x, y, o)
    for y in [4, 12]:
        for x in range(2, 14): c.px(x, y, o)
    # Gleam highlight
    c.px(3, 6, m[6])
    c.px(7, 5, m[6])
    return c.finish()

def draw_dragon_scale():
    c = PixelCanvas(16, 16, 8)
    o, red = M['shadow'][0], M['dragonfire']
    # Diamond shape
    pixels = [
        (7, 1), (8, 1),  # top
        (6, 2), (7, 2), (8, 2), (9, 2),
        (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
        (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4),
        (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5),
        (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6),
        (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7),
        (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (12, 8),
        (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (12, 9),
        (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10),
        (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11),
        (6, 12), (7, 12), (8, 12), (9, 12),
        (7, 13), (8, 13),  # bottom point
    ]
    for x, y in pixels:
        # Quadrant shading: top-left highlight, bottom-right shadow
        if x + y < 12: c.px(x, y, red[4])  # top-left hi
        elif x + y < 16: c.px(x, y, red[3])  # mid
        else: c.px(x, y, red[2])  # bottom-right shadow
    # Outline (just outer edge)
    outline_pixels = [(7, 0), (8, 0), (5, 1), (9, 1), (4, 2), (10, 2), (3, 3), (11, 3), (2, 4), (12, 4), (2, 5), (12, 5), (2, 6), (12, 6), (2, 7), (12, 7), (2, 8), (12, 8), (2, 9), (12, 9), (3, 10), (11, 10), (4, 11), (10, 11), (5, 12), (9, 12), (6, 13), (8, 13), (7, 14), (8, 14)]
    for x, y in outline_pixels:
        if 0 <= x <= 15 and 0 <= y <= 15:
            c.px(x, y, o)
    # Shine spot
    c.px(6, 4, red[5])
    c.px(7, 3, red[5])
    return c.finish()

def draw_dragon_heart():
    c = PixelCanvas(16, 16, 8)
    o, red = M['shadow'][0], M['gem_blood']
    # Heart shape (two bumps + point)
    heart_pixels = [
        # Top bumps
        (2, 3), (3, 3), (4, 3), (5, 3),
        (10, 3), (11, 3), (12, 3), (13, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
        (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4),
        (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5),
        (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (13, 5), (14, 5),
        (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6),
        (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (12, 7), (13, 7), (14, 7),
        (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8),
        (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9), (12, 9), (13, 9),
        (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (12, 10),
        (4, 11), (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11),
        (5, 12), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12),
        (6, 13), (7, 13), (8, 13), (9, 13),
        (7, 14), (8, 14),
    ]
    for x, y in heart_pixels:
        # Shade: top-left bright, bottom-right dark
        if x < 7 and y < 7: c.px(x, y, red[4])  # hi
        elif x > 8 and y > 7: c.px(x, y, red[1])  # lo
        else: c.px(x, y, red[3])  # main
    # Outline (heart silhouette)
    outline_pixels = [
        (2, 2), (3, 2), (4, 2), (5, 2), (10, 2), (11, 2), (12, 2), (13, 2),  # top of bumps
        (0, 3), (1, 3), (6, 3), (7, 3), (8, 3), (9, 3), (14, 3), (15, 3),
        (0, 4), (15, 4),
        (0, 5), (15, 5),
        (0, 6), (15, 6),
        (0, 7), (15, 7),
        (1, 8), (14, 8),
        (1, 9), (14, 9),
        (2, 10), (13, 10),
        (3, 11), (12, 11),
        (4, 12), (11, 12),
        (5, 13), (10, 13),
        (6, 14), (9, 14),
        (7, 15), (8, 15),  # bottom point
    ]
    for x, y in outline_pixels:
        if 0 <= x <= 15 and 0 <= y <= 15:
            c.px(x, y, o)
    # Highlight
    c.px(3, 5, red[5])
    c.px(11, 5, red[5])
    c.px(4, 4, red[6])
    return c.finish()

def draw_essence(fire=True):
    c = PixelCanvas(16, 16, 8)
    o = M['shadow'][0]
    if fire: gem = M['gem_fire']; sparkle = '#FFEF60'
    else: gem = M['gem_frost']; sparkle = '#FFFFFF'
    # Round orb (concentric)
    pixels = [
        (7, 3), (8, 3),
        (6, 4), (7, 4), (8, 4), (9, 4),
        (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5),
        (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6),
        (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7),
        (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8),
        (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9), (11, 9),
        (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10),
        (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11),
        (6, 12), (7, 12), (8, 12), (9, 12),
        (7, 13), (8, 13),
    ]
    for x, y in pixels:
        # Distance from center (7.5, 8) determines color
        dx = x - 7.5
        dy = y - 8
        d = (dx*dx + dy*dy) ** 0.5
        if d < 1.5: c.px(x, y, gem[6])  # center brightest
        elif d < 2.5: c.px(x, y, gem[5])
        elif d < 3.5: c.px(x, y, gem[3])
        elif d < 4.5: c.px(x, y, gem[2])
        else: c.px(x, y, gem[1])  # outer
    # Outline
    outline_pixels = [
        (6, 2), (7, 2), (8, 2), (9, 2),
        (4, 3), (5, 3), (10, 3), (11, 3),
        (3, 4), (12, 4),
        (3, 5), (12, 5),
        (3, 6), (12, 6),
        (3, 7), (12, 7),
        (3, 8), (12, 8),
        (3, 9), (12, 9),
        (3, 10), (12, 10),
        (3, 11), (12, 11),
        (4, 12), (11, 12),
        (5, 13), (10, 13),
        (6, 14), (7, 14), (8, 14), (9, 14),
    ]
    for x, y in outline_pixels:
        c.px(x, y, o)
    # Sparkles
    c.px(2, 3, sparkle); c.px(13, 4, sparkle); c.px(1, 8, sparkle); c.px(14, 8, sparkle)
    c.px(3, 13, sparkle); c.px(12, 12, sparkle)
    return c.finish()

def draw_class_token(theme='mage'):
    c = PixelCanvas(16, 16, 8)
    o = M['shadow'][0]
    if theme == 'mage': g = M['arcane']; gem = M['gem_arcane']; icon = '#E0C0FF'
    elif theme == 'ranger': g = M['gem_nature']; gem = M['gem_nature']; icon = '#A0FFC0'
    elif theme == 'berserker': g = M['gem_blood']; gem = M['gem_blood']; icon = '#FFA0A0'
    elif theme == 'paladin': g = M['gold']; gem = M['gold']; icon = '#FFF080'
    else: g = M['gem_nature']; gem = M['gem_nature']; icon = '#C0FF80'
    # Octagonal medallion
    # Outer star
    star = [
        (7, 1), (8, 1),
        (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2),
        (3, 3), (4, 3), (5, 3), (10, 3), (11, 3), (12, 3),
        (2, 4), (3, 4), (12, 4), (13, 4),
        (1, 5), (2, 5), (13, 5), (14, 5),
        (1, 6), (14, 6),
        (1, 7), (14, 7),
        (1, 8), (14, 8),
        (1, 9), (14, 9),
        (1, 10), (14, 10),
        (2, 11), (3, 11), (12, 11), (13, 11),
        (3, 12), (4, 12), (11, 12), (12, 12),
        (5, 13), (6, 13), (7, 13), (8, 13), (9, 13), (10, 13),
        (7, 14), (8, 14),
    ]
    for x, y in star:
        # Distance from center
        dx = abs(x - 7.5); dy = abs(y - 7.5)
        if dx + dy > 6.5: c.px(x, y, g[2])  # outer shadow
        else: c.px(x, y, g[3])
    # Inner octagon
    inner = [
        (6, 3), (7, 3), (8, 3), (9, 3),
        (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4),
        (3, 5), (4, 5), (5, 5), (10, 5), (11, 5), (12, 5),
        (3, 6), (12, 6),
        (3, 7), (12, 7),
        (3, 8), (12, 8),
        (3, 9), (12, 9),
        (3, 10), (12, 10),
        (4, 11), (5, 11), (10, 11), (11, 11),
        (6, 12), (7, 12), (8, 12), (9, 12),
    ]
    for x, y in inner:
        c.px(x, y, g[4])
    # Center circle (gem)
    center = [
        (7, 6), (8, 6),
        (6, 7), (7, 7), (8, 7), (9, 7),
        (6, 8), (7, 8), (8, 8), (9, 8),
        (6, 9), (7, 9), (8, 9), (9, 9),
        (7, 10), (8, 10),
    ]
    for x, y in center:
        dx = abs(x - 7.5); dy = abs(y - 7.5)
        d = (dx*dx + dy*dy) ** 0.5
        if d < 0.5: c.px(x, y, gem[6])
        elif d < 1.5: c.px(x, y, gem[5])
        else: c.px(x, y, gem[4])
    # Cross icon
    c.px(7, 7, icon); c.px(8, 7, icon)
    c.px(7, 8, icon); c.px(8, 8, icon)
    c.px(7, 9, icon); c.px(8, 9, icon)
    c.px(6, 8, icon); c.px(9, 8, icon)
    # Outline
    c.px(6, 2, o); c.px(9, 2, o)
    c.px(2, 4, o); c.px(13, 4, o)
    c.px(1, 5, o); c.px(14, 5, o)
    c.px(0, 6, o); c.px(15, 6, o)
    c.px(0, 7, o); c.px(15, 7, o)
    c.px(0, 8, o); c.px(15, 8, o)
    c.px(0, 9, o); c.px(15, 9, o)
    c.px(1, 10, o); c.px(14, 10, o)
    c.px(2, 11, o); c.px(13, 11, o)
    c.px(6, 13, o); c.px(9, 13, o)
    return c.finish()

# ═══════════════════════════════════════════════════════════════════
# GENERATE ALL
# ═══════════════════════════════════════════════════════════════════

def main():
    items = {
        'mythril_sword': draw_mythril_sword,
        'dragon_bone_greatsword': draw_dragon_bone_greatsword,
        'shadowfang_dagger': draw_shadowfang_dagger,
        'elven_dagger': draw_elven_dagger,
        'troll_warhammer': draw_troll_warhammer,
        'giant_club': draw_giant_club,
        'mythril_bow': draw_mythril_bow,
        'enchanted_bow': draw_enchanted_bow,
        'magic_staff': draw_magic_staff,
        'dragonslayer_spear': draw_dragonslayer_spear,
        'mythril_ingot': draw_mythril_ingot,
        'dragon_scale': draw_dragon_scale,
        'dragon_heart': draw_dragon_heart,
        'fire_essence': lambda: draw_essence(True),
        'frost_essence': lambda: draw_essence(False),
        'class_token_mage': lambda: draw_class_token('mage'),
        'class_token_ranger': lambda: draw_class_token('ranger'),
        'class_token_berserker': lambda: draw_class_token('berserker'),
        'class_token_paladin': lambda: draw_class_token('paladin'),
        'class_token_druid': lambda: draw_class_token('druid'),
    }
    for name, fn in items.items():
        path = f'{ITEMS}/{name}.png'
        img = fn()
        img.save(path)
    print(f"✅ Generated {len(items)} items")

if __name__ == '__main__':
    main()
