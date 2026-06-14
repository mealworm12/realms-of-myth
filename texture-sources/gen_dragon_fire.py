"""
Real AAA entity textures for Realms of Myth.

Strategy: draw each entity in a TOP-DOWN view (since the geo model wraps the
texture around the model like a skin). This is how Minecraft entity textures
work — the head is in one area, body in another, limbs in others, and the
renderer maps them onto the 3D shape.

For dragons: head at top, body in middle, 2 wings spread left/right, 4 legs at
bottom, tail trailing down.

I will draw with extreme pixel care — no ellipses, no shortcuts. Each pixel
is a deliberate art choice. This is the only way to achieve a "real"
dragon look at this resolution.
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
from gen_armor_aaa import hex_c
import os, math

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
ENT = f'{RP}/textures/entity'

# ═══════════════════════════════════════════════════════════════════
# SHARED: pixel-by-pixel outline of organic shapes
# ═══════════════════════════════════════════════════════════════════

def smooth_outline(c, points, color):
    """Draw a closed outline through points using line_diag for smooth curves."""
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i+1) % len(points)]
        c.line_diag(x1, y1, x2, y2, color)

# ═══════════════════════════════════════════════════════════════════
# DRAGON FIRE — 128x128, hand-drawn pixel by pixel
# ═══════════════════════════════════════════════════════════════════

def draw_dragon_fire():
    """Hand-pixeled fire dragon in top-down view.

    Anatomy:
    - HEAD at top center (y=10-35): triangular, with snout pointing up
    - NECK (y=35-50): 2px wide connector
    - BODY (y=50-80): wide oval body with belly scales
    - WINGS spread left/right (y=45-95)
    - LEGS at bottom (y=80-105): 4 leg pairs
    - TAIL (y=80-118): curving to lower-right
    """
    c = PixelCanvas(128, 128, 4)
    body = M['dragonfire']  # red palette
    o = M['shadow'][0]
    flame = M['gem_fire']
    out = o

    # ══ HEAD (y=10-35) ══
    # Triangular dragon head pointing up, 18 wide at base, 12 wide at top
    # Skulls curve outward at cheeks, taper to snout
    head_outline = [
        (60, 10),  # tip of snout
        (66, 10),
        (66, 12), (70, 14),
        (74, 17), (78, 22),  # right cheek
        (80, 28),
        (78, 33), (74, 36),  # jaw line
        (70, 38), (66, 39), (60, 40), (54, 39), (50, 38),  # bottom
        (46, 36), (42, 33), (40, 28),
        (42, 22), (46, 17),  # left cheek
        (50, 14), (54, 12),
        (60, 10),
    ]
    # Fill head with body color (will overwrite as we add details)
    # Use a simpler fill: for each y, find left and right outline
    for y in range(10, 41):
        # Find left and right edges at this y
        left, right = None, None
        for x in range(35, 95):
            if y in [p[1] for p in head_outline]:
                # Check if x is inside polygon at this y
                pass
        # Just do scanline: for each y, fill from outline
    # Simpler: for each y, fill between symmetric edges
    head_fill = {
        10: [(60, 66)],  # snout tip
        11: [(58, 68)],
        12: [(58, 70)],
        13: [(56, 72), (60, 60)],  # oops, this isn't right
    }
    # Manual fill using direct pixel placement
    head_pixels = [
        # y=10: snout tip
        (60, 10), (61, 10), (62, 10), (63, 10), (64, 10), (65, 10),
        # y=11: snout widens
        (59, 11), (60, 11), (61, 11), (62, 11), (63, 11), (64, 11), (65, 11), (66, 11),
        # y=12-13: snout fuller
        *[(x, 12) for x in range(58, 68)],
        *[(x, 13) for x in range(56, 70)],
        # y=14-16: head widens
        *[(x, 14) for x in range(54, 72)],
        *[(x, 15) for x in range(52, 74)],
        *[(x, 16) for x in range(50, 76)],
        # y=17-20: cheeks form
        *[(x, 17) for x in range(48, 78)],
        *[(x, 18) for x in range(46, 80)],
        *[(x, 19) for x in range(44, 82)],
        *[(x, 20) for x in range(42, 84)],
        # y=21-25: skull at widest
        *[(x, 21) for x in range(42, 84)],
        *[(x, 22) for x in range(40, 86)],
        *[(x, 23) for x in range(40, 86)],
        *[(x, 24) for x in range(40, 86)],
        *[(x, 25) for x in range(40, 86)],
        # y=26-30: jaw narrows
        *[(x, 26) for x in range(42, 84)],
        *[(x, 27) for x in range(44, 82)],
        *[(x, 28) for x in range(46, 80)],
        *[(x, 29) for x in range(48, 78)],
        *[(x, 30) for x in range(50, 76)],
        # y=31-35: jaw bottom
        *[(x, 31) for x in range(52, 74)],
        *[(x, 32) for x in range(54, 72)],
        *[(x, 33) for x in range(56, 70)],
        *[(x, 34) for x in range(58, 68)],
        *[(x, 35) for x in range(60, 66)],
        # y=36-40: neck connector
        *[(x, 36) for x in range(60, 66)],
        *[(x, 37) for x in range(60, 66)],
        *[(x, 38) for x in range(60, 66)],
        *[(x, 39) for x in range(60, 66)],
        *[(x, 40) for x in range(60, 66)],
    ]
    for x, y in head_pixels:
        # Multi-tone based on y (top bright, bottom dark)
        if y < 18: tone = body[5]  # top highlight
        elif y < 25: tone = body[4]
        elif y < 32: tone = body[3]
        else: tone = body[2]  # jaw shadow
        c.px(x, y, tone)
    # Add some shading variation (left/right)
    for y in range(10, 41):
        for x in range(35, 95):
            if (x, y) in head_pixels:
                if x < 60 and (x + y) % 5 == 0: c.px(x, y, body[5])  # left highlight
                if x > 65 and (x + y) % 5 == 0: c.px(x, y, body[2])  # right shadow
    # Outline head
    head_outline_pixels = [
        (60, 9), (61, 9), (62, 9), (63, 9), (64, 9), (65, 9),  # top of snout
        (59, 10), (60, 10), (65, 10), (66, 10),  # row 10 outline
        (58, 11), (67, 11),
        (57, 12), (68, 12),
        (55, 13), (56, 13), (69, 13), (70, 13),
        (53, 14), (54, 14), (71, 14), (72, 14),
        (51, 15), (52, 15), (73, 15), (74, 15),
        (49, 16), (50, 16), (75, 16), (76, 16),
        (47, 17), (48, 17), (77, 17), (78, 17),
        (45, 18), (46, 18), (79, 18), (80, 18),
        (43, 19), (44, 19), (81, 19), (82, 19),
        (41, 20), (42, 20), (83, 20), (84, 20),
        (39, 21), (40, 21), (85, 21), (86, 21),
        (39, 22), (40, 22), (85, 22), (86, 22),
        (39, 23), (40, 23), (85, 23), (86, 23),
        (39, 24), (40, 24), (85, 24), (86, 24),
        (39, 25), (40, 25), (85, 25), (86, 25),
        (41, 26), (42, 26), (83, 26), (84, 26),
        (43, 27), (44, 27), (81, 27), (82, 27),
        (45, 28), (46, 28), (79, 28), (80, 28),
        (47, 29), (48, 29), (77, 29), (78, 29),
        (49, 30), (50, 30), (75, 30), (76, 30),
        (51, 31), (52, 31), (73, 31), (74, 31),
        (53, 32), (54, 32), (71, 32), (72, 32),
        (55, 33), (56, 33), (69, 33), (70, 33),
        (57, 34), (58, 34), (67, 34), (68, 34),
        (59, 35), (60, 35), (65, 35), (66, 35),
        # Bottom (jaw line)
        (60, 40), (61, 40), (62, 40), (63, 40), (64, 40), (65, 40),
    ]
    for x, y in head_outline_pixels:
        c.px(x, y, out)
    # Snout highlight
    c.px(62, 12, body[6]); c.px(63, 12, body[6])
    c.px(62, 13, body[5]); c.px(63, 13, body[5])
    # Eyes (glowing yellow)
    c.px(54, 19, flame[6])
    c.px(55, 19, flame[5])
    c.px(54, 20, flame[5])
    c.px(70, 19, flame[6])
    c.px(71, 19, flame[5])
    c.px(70, 20, flame[5])
    # Eye pupils
    c.px(54, 20, out); c.px(70, 20, out)
    # Nostrils
    c.px(60, 14, out); c.px(65, 14, out)
    c.px(60, 15, out); c.px(65, 15, out)
    # Horns
    horn_left = [(54, 9), (53, 7), (52, 5), (51, 4)]
    horn_right = [(71, 9), (72, 7), (73, 5), (74, 4)]
    for x, y in horn_left + horn_right:
        c.px(x, y, out)
    c.px(54, 8, body[1]); c.px(53, 6, body[1]); c.px(52, 4, body[1])
    c.px(71, 8, body[1]); c.px(72, 6, body[1]); c.px(73, 4, body[1])
    # Mouth (glowing line)
    c.px(58, 32, out); c.px(59, 32, out); c.px(60, 32, out)
    c.px(61, 32, flame[5]); c.px(62, 32, flame[5]); c.px(63, 32, flame[5])
    c.px(64, 32, flame[5]); c.px(65, 32, flame[5])
    c.px(66, 32, out); c.px(67, 32, out)
    # Teeth
    c.px(60, 33, body[6]); c.px(61, 33, body[6]); c.px(64, 33, body[6]); c.px(65, 33, body[6])

    # ══ NECK (y=36-50) ══
    for y in range(36, 51):
        for x in range(58, 68):
            c.px(x, y, body[3])
            if x == 58: c.px(x, y, body[4])
            if x == 67: c.px(x, y, body[2])
    # Neck outline
    for y in range(36, 51):
        c.px(57, y, out); c.px(68, y, out)
    # Neck spikes
    for y in [40, 44, 48]:
        c.px(60, y, out); c.px(60, y-1, out)

    # ══ BODY (y=50-80) ══
    # Wide oval body, 30 wide at center
    body_pixels = []
    for y in range(50, 81):
        # Symmetric body widening then narrowing
        if y < 55: rx = (y - 50) * 3 + 16  # 16, 19, 22, 25, 28
        elif y < 75: rx = 30  # widest
        else: rx = max(0, 30 - (y - 75) * 3)  # narrowing
        for x in range(64 - rx, 64 + rx + 1):
            body_pixels.append((x, y))
    for x, y in body_pixels:
        if 0 <= x < 128 and 0 <= y < 128:
            # Multi-tone
            if y < 58: tone = body[4]  # top highlight
            elif y < 70: tone = body[3]  # main
            else: tone = body[2]  # bottom shadow
            c.px(x, y, tone)
    # Belly scales (rows 65-78, lighter)
    for y in range(65, 79):
        for x in range(54, 75):
            if (x + y) % 6 == 0: c.px(x, y, body[5])
            elif (x + y) % 4 == 0: c.px(x, y, body[4])
    # Body outline
    for y in range(50, 81):
        for x in [64 - 32, 64 + 32]:
            if 0 <= x < 128:
                c.px(x, y, out)
    # Spikes along back
    for x in range(40, 90, 4):
        c.px(x, 50, out); c.px(x, 49, out)
        c.px(x, 48, body[1])

    # ══ WINGS (y=50-90, left + right) ══
    # Left wing: triangular, extends from body to far left
    # Top edge: from (40, 55) to (10, 50) to (5, 60) to (15, 75) to (40, 70)
    # Bottom edge: from (40, 70) to (35, 85) to (15, 90) to (5, 80)
    wing_left = [
        # Outline
        (40, 55), (35, 50), (25, 48), (15, 50), (5, 55), (2, 65), (5, 75), (10, 80), (5, 85), (15, 88), (25, 90), (35, 88), (40, 75),
    ]
    # Draw outline
    for i in range(len(wing_left) - 1):
        x1, y1 = wing_left[i]; x2, y2 = wing_left[i+1]
        c.line_diag(x1, y1, x2, y2, out)
    # Fill wing interior with body color
    for y in range(48, 91):
        for x in range(2, 42):
            if 0 <= x < 128 and 0 <= y < 128:
                # Inside wing shape (approximate)
                if y < 55 and x > 5:  # top of wing
                    c.px(x, y, body[2])
                elif y < 70:  # middle of wing
                    c.px(x, y, body[3])
                else:  # bottom
                    c.px(x, y, body[2])
    # Wing membrane lines (fingers)
    c.line_diag(40, 55, 35, 50, body[1])
    c.line_diag(40, 70, 35, 50, body[1])
    c.line_diag(40, 75, 25, 48, body[1])
    c.line_diag(40, 75, 15, 50, body[1])
    c.line_diag(40, 75, 5, 55, body[1])
    c.line_diag(40, 75, 2, 65, body[1])
    c.line_diag(40, 75, 5, 75, body[1])
    c.line_diag(40, 75, 10, 80, body[1])
    c.line_diag(40, 75, 5, 85, body[1])
    c.line_diag(40, 75, 15, 88, body[1])
    c.line_diag(40, 75, 25, 90, body[1])
    c.line_diag(40, 75, 35, 88, body[1])
    # Wing claw at top
    c.px(35, 48, out); c.px(36, 48, out); c.px(37, 48, out)
    c.px(36, 47, out); c.px(36, 46, out)

    # Right wing (mirror)
    wing_right = [(88, 55), (93, 50), (103, 48), (113, 50), (123, 55), (126, 65), (123, 75), (118, 80), (123, 85), (113, 88), (103, 90), (93, 88), (88, 75)]
    for i in range(len(wing_right) - 1):
        x1, y1 = wing_right[i]; x2, y2 = wing_right[i+1]
        c.line_diag(x1, y1, x2, y2, out)
    for y in range(48, 91):
        for x in range(86, 128):
            if 0 <= x < 128 and 0 <= y < 128:
                if y < 55 and x > 122: c.px(x, y, body[2])
                elif y < 70: c.px(x, y, body[3])
                else: c.px(x, y, body[2])
    c.line_diag(88, 55, 93, 50, body[1])
    c.line_diag(88, 70, 93, 50, body[1])
    c.line_diag(88, 75, 103, 48, body[1])
    c.line_diag(88, 75, 113, 50, body[1])
    c.line_diag(88, 75, 123, 55, body[1])
    c.line_diag(88, 75, 126, 65, body[1])
    c.line_diag(88, 75, 123, 75, body[1])
    c.line_diag(88, 75, 118, 80, body[1])
    c.line_diag(88, 75, 123, 85, body[1])
    c.line_diag(88, 75, 113, 88, body[1])
    c.line_diag(88, 75, 103, 90, body[1])
    c.line_diag(88, 75, 93, 88, body[1])
    c.px(91, 48, out); c.px(92, 48, out); c.px(93, 48, out)
    c.px(92, 47, out); c.px(92, 46, out)

    # ══ LEGS (y=78-108) ══
    # 4 legs, 2 in front, 2 in back
    for leg_x, leg_y_start, leg_y_end in [
        (50, 80, 105),  # front-left
        (60, 80, 108),  # front-right
        (68, 80, 108),  # back-right
        (78, 80, 105),  # back-left
    ]:
        for y in range(leg_y_start, leg_y_end + 1):
            c.px(leg_x, y, body[2])
            c.px(leg_x + 1, y, body[2])
            if y == leg_y_start: c.px(leg_x, y, body[3]); c.px(leg_x + 1, y, body[3])
        # Outline
        c.px(leg_x - 1, leg_y_start, out); c.px(leg_x + 2, leg_y_start, out)
        for y in range(leg_y_start, leg_y_end + 1):
            c.px(leg_x - 1, y, out); c.px(leg_x + 2, y, out)
        # Foot (claws)
        c.px(leg_x - 1, leg_y_end, out); c.px(leg_x, leg_y_end, out)
        c.px(leg_x + 1, leg_y_end, out); c.px(leg_x + 2, leg_y_end, out)
        for x in range(leg_x - 1, leg_x + 3):
            c.px(x, leg_y_end + 1, out)

    # ══ TAIL (y=85-122) ══
    # Tail curving down-right with flame tip
    tail_pixels = [
        (80, 85), (82, 88), (84, 91), (86, 94), (88, 97), (90, 100),
        (92, 103), (94, 105), (96, 107), (98, 109), (100, 110),
        (102, 111), (104, 112), (106, 113),
    ]
    for i, (x, y) in enumerate(tail_pixels):
        # Width tapers from 2px to 1px
        width = max(1, 2 - i // 5)
        c.px(x, y, body[3])
        if width >= 2:
            c.px(x - 1, y, body[2])
        # Outline
        c.px(x, y - 1, out) if i % 2 == 0 else None
    # Tail spikes
    for x, y in [(82, 90), (88, 96), (94, 103)]:
        c.px(x + 1, y - 1, out)
        c.px(x + 2, y - 1, out)
    # Flame tip (y=110-118, x=106-120)
    flame_pixels = [
        (107, 112, flame[5]), (108, 113, flame[6]), (109, 114, flame[5]),
        (110, 113, flame[5]), (111, 114, flame[6]), (112, 115, flame[5]),
        (113, 114, flame[5]), (114, 113, flame[5]), (115, 112, flame[4]),
        (116, 111, flame[4]), (117, 110, flame[3]),
        (110, 116, flame[4]), (113, 116, flame[4]),
        (108, 111, flame[4]), (114, 110, flame[4]),
    ]
    for x, y, color in flame_pixels:
        c.px(x, y, color)
    # Flame core
    c.px(110, 113, flame[6]); c.px(112, 114, flame[6])
    c.px(111, 114, hex_c('#FFFFE0'))  # brightest center

    return c.finish()

if __name__ == '__main__':
    img = draw_dragon_fire()
    img.save(f'{ENT}/dragon_fire.png')
    print(f"dragon_fire: {img.size}, {os.path.getsize(f'{ENT}/dragon_fire.png')} bytes")
