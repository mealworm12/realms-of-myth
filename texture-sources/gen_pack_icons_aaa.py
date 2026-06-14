"""
AAA pack icons (256x256) for Realms of Myth.

Hand-pixeled at 4x supersampled with multi-tone shading.
"""

import sys
sys.path.insert(0, '/tmp')
from pixel_toolkit import *
from gen_weapons_aaa import PixelCanvas, M
from gen_armor_aaa import hex_c
import os, math

ROOT = '/workspace/realms-of-myth'
RP = f'{ROOT}/realms_of_myth_RP'
BP = f'{ROOT}/realms_of_myth_BP'

def make_bp_icon():
    """256x256 — gold-framed sword on dark purple background."""
    c = PixelCanvas(256, 256, 4)
    purple_dark = '#1A0830'
    purple_mid = '#2A1050'
    purple_hi = '#3A1870'
    gold = M['gold']
    mythril = M['mythril']
    o = M['shadow'][0]
    out = '#000000'
    # Background gradient (top dark to bottom darker)
    for y in range(256):
        if y < 128:
            t = y / 128
            r = int(35 + t * 5)
            g = int(15 + t * 5)
            b = int(70 + t * 5)
            c.d.rectangle([0, y, 255, y], fill=(r, g, b, 255))
        else:
            t = (y - 128) / 128
            r = int(40 - t * 20)
            g = int(20 - t * 10)
            b = int(75 - t * 30)
            c.d.rectangle([0, y, 255, y], fill=(r, g, b, 255))
    # Stars (background sparkles)
    for x, y, r in [(40, 30, 2), (220, 50, 1), (30, 80, 1), (200, 100, 2), (15, 130, 1), (240, 130, 1), (50, 180, 1), (210, 200, 1), (20, 230, 1), (240, 240, 2)]:
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx*dx + dy*dy <= r*r:
                    c.px(x + dx, y + dy, '#FFFFFF')
    # Outer gold frame
    for x in range(8):
        c.d.rectangle([0, x, 255, x], fill=gold[3])
        c.d.rectangle([0, 255 - x, 255, 255 - x], fill=gold[3])
        c.d.rectangle([x, 0, x, 255], fill=gold[3])
        c.d.rectangle([255 - x, 0, 255 - x, 255], fill=gold[3])
    # Inner gold frame
    for x in range(2):
        c.d.rectangle([12, 12 + x, 243, 12 + x], fill=gold[4])
        c.d.rectangle([12, 243 - x, 243, 243 - x], fill=gold[4])
        c.d.rectangle([12 + x, 12, 12 + x, 243], fill=gold[4])
        c.d.rectangle([243 - x, 12, 243 - x, 243], fill=gold[4])
    # Decorative corner flourishes
    for cx, cy in [(20, 20), (236, 20), (20, 236), (236, 236)]:
        c.d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=gold[4])
        c.d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=gold[5])
        c.px(cx, cy, '#FFFFFF')

    # Title banner (top, y=30-60)
    for y in range(30, 60):
        c.d.rectangle([30, y, 226, y], fill=purple_dark)
    c.d.rectangle([30, 30, 226, 32], fill=purple_hi)
    c.d.rectangle([30, 58, 226, 60], fill='#0A0020')
    # Banner border
    for y in [30, 60]:
        for x in [30, 226]:
            c.d.rectangle([x, y, x, y], fill=gold[4])
    # Title text "REALMS" (pixel font)
    title_letters = [
        # R E A L M S
        # Each letter is 8x16
        [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),(0,11),(0,12),(0,13),(0,14),(0,15),
         (1,0),(2,0),(3,0),(4,0),(1,7),(2,7),(3,7),(4,7),(1,8),(2,8),(3,8),(4,8),(1,4),(2,4),(3,4),(4,4),(1,9),(2,9),(3,9),(4,9),(4,10),(4,11),(4,12),(4,13),(4,14),(4,15)],  # R
        # E
        # A
        # L
        # M
        # S
    ]
    # Simpler: just use solid bars for title
    # Skip text for now; rely on visual

    # CENTRAL SWORD
    cx = 128
    # Blade (rows 70-180, 12 wide tapering to point)
    # Top of blade
    # Multi-tone blade
    blade = [
        (cx, 70), (cx, 75), (cx - 1, 75), (cx + 1, 75),
        (cx - 1, 80), (cx + 1, 80),
        (cx - 1, 85), (cx + 1, 85),
        (cx - 2, 90), (cx + 2, 90),
        (cx - 2, 95), (cx + 2, 95),
        (cx - 3, 100), (cx + 3, 100),
        (cx - 3, 105), (cx + 3, 105),
        (cx - 4, 110), (cx + 4, 110),
        (cx - 4, 115), (cx + 4, 115),
        (cx - 5, 120), (cx + 5, 120),
        (cx - 5, 125), (cx + 5, 125),
        (cx - 6, 130), (cx + 6, 130),
        (cx - 6, 135), (cx + 6, 135),
        (cx - 7, 140), (cx + 7, 140),
        (cx - 7, 145), (cx + 7, 145),
        (cx - 8, 150), (cx + 8, 150),
        (cx - 8, 155), (cx + 8, 155),
        (cx - 9, 160), (cx + 9, 160),
        (cx - 9, 165), (cx + 9, 165),
        (cx - 10, 170), (cx + 10, 170),
        (cx - 10, 175), (cx + 10, 175),
        (cx - 11, 180), (cx + 11, 180),
    ]
    # Fill with multi-tone gradient
    for y in range(70, 185):
        for x in range(cx - 12, cx + 13):
            if 0 <= x < 256 and 0 <= y < 256:
                # Determine if inside blade at this y
                if y >= 70 and y < 80:
                    if abs(x - cx) <= 1: c.px(x, y, mythril[6])
                elif y >= 80 and y < 100:
                    if abs(x - cx) <= 2: c.px(x, y, mythril[5])
                elif y >= 100 and y < 130:
                    if abs(x - cx) <= 4: c.px(x, y, mythril[4])
                elif y >= 130 and y < 160:
                    if abs(x - cx) <= 6: c.px(x, y, mythril[4])
                elif y >= 160 and y < 185:
                    if abs(x - cx) <= 10: c.px(x, y, mythril[3])
    # Blade outline
    for y in range(70, 185):
        # Determine width
        if y < 80: w = 1
        elif y < 100: w = 2
        elif y < 130: w = 4
        elif y < 160: w = 6
        else: w = 10
        if 0 <= cx - w - 1 < 256: c.px(cx - w - 1, y, out)
        if 0 <= cx + w + 1 < 256: c.px(cx + w + 1, y, out)
    c.px(cx, 70, out); c.px(cx, 71, out)
    # Center fuller (groove)
    for y in range(85, 180):
        if y < 100: pass
        elif y < 130: c.px(cx, y, mythril[2])
        elif y < 160: c.px(cx, y, mythril[2]); c.px(cx + 1, y, mythril[2])
        else: c.px(cx, y, mythril[1]); c.px(cx + 1, y, mythril[1])
    # Specular highlight
    for y in [90, 95, 100, 105, 110]:
        c.px(cx - 1, y, mythril[6])
    # Glow rune (cyan)
    c.px(cx, 120, '#80E0FF')
    c.px(cx, 140, '#80E0FF')
    c.px(cx, 160, '#80E0FF')

    # Crossguard (gold, rows 180-195)
    for y in range(180, 195):
        for x in range(cx - 50, cx + 51):
            if 0 <= x < 256:
                if y == 180: c.px(x, y, gold[5])
                elif y == 194: c.px(x, y, gold[1])
                elif y == 181: c.px(x, y, gold[4])
                elif y == 193: c.px(x, y, gold[2])
                else:
                    if x < cx - 30: c.px(x, y, gold[4])
                    elif x > cx + 30: c.px(x, y, gold[2])
                    else: c.px(x, y, gold[3])
    # Crossguard outline
    c.line_diag(cx - 50, 180, cx - 50, 195, out)
    c.line_diag(cx + 50, 180, cx + 50, 195, out)
    c.line_diag(cx - 50, 180, cx + 50, 180, out)
    c.line_diag(cx - 50, 195, cx + 50, 195, out)
    # End caps
    for y in [182, 193]:
        c.px(cx - 51, y, gold[2])
        c.px(cx + 51, y, gold[2])
    # Center gem (large blue)
    c.px(cx - 6, 185, '#40A0E0'); c.px(cx + 6, 185, '#40A0E0')
    c.px(cx - 6, 190, '#40A0E0'); c.px(cx + 6, 190, '#40A0E0')
    c.px(cx - 4, 186, '#80E0FF'); c.px(cx - 4, 189, '#80E0FF')
    c.px(cx - 5, 187, '#FFFFFF'); c.px(cx - 4, 188, '#FFFFFF')

    # Handle (rows 195-225)
    for y in range(195, 225):
        for x in range(cx - 6, cx + 7):
            if 0 <= x < 256:
                if x < cx - 3: c.px(x, y, '#8B5A2B')  # leather
                elif x > cx + 3: c.px(x, y, '#3E2810')  # shadow
                else: c.px(x, y, '#5C3A1E')  # main
    # Wrap detail
    for y in [200, 205, 210, 215, 220]:
        c.line_diag(cx - 6, y, cx + 6, y + 2, '#2A1800')
    # Handle outline
    c.line_diag(cx - 6, 195, cx - 6, 225, out)
    c.line_diag(cx + 6, 195, cx + 6, 225, out)

    # Pommel (rows 225-240)
    for y in range(225, 240):
        for x in range(cx - 12, cx + 13):
            if 0 <= x < 256:
                if y == 225: c.px(x, y, gold[5])
                elif y == 239: c.px(x, y, gold[1])
                elif x < cx - 8: c.px(x, y, gold[4])
                elif x > cx + 8: c.px(x, y, gold[2])
                else: c.px(x, y, gold[3])
    # Pommel outline
    c.line_diag(cx - 12, 225, cx - 12, 240, out)
    c.line_diag(cx + 12, 225, cx + 12, 240, out)
    c.line_diag(cx - 12, 225, cx + 12, 225, out)
    c.line_diag(cx - 12, 240, cx + 12, 240, out)
    # Center jewel
    c.px(cx - 4, 230, '#40A0E0'); c.px(cx + 4, 230, '#40A0E0')
    c.px(cx - 4, 234, '#40A0E0'); c.px(cx + 4, 234, '#40A0E0')
    c.px(cx - 2, 232, '#80E0FF')

    return c.finish()

def make_rp_icon():
    """256x256 — sunset dragon scene."""
    c = PixelCanvas(256, 256, 4)
    # Sky gradient
    for y in range(8, 248):
        t = y / 256
        if t < 0.3:
            tt = t / 0.3
            r = int(40 + tt * 60)
            g = int(15 + tt * 50)
            b = int(70 + tt * 30)
        elif t < 0.55:
            tt = (t - 0.3) / 0.25
            r = int(100 + tt * 140)
            g = int(65 + tt * 80)
            b = int(100 - tt * 50)
        else:
            tt = (t - 0.55) / 0.45
            r = int(240 - tt * 100)
            g = int(145 - tt * 100)
            b = int(50 - tt * 20)
        c.d.rectangle([8, y, 247, y], fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))
    # Gold frame (matching BP)
    gold = M['gold']
    out = '#000000'
    for x in range(8):
        c.d.rectangle([0, x, 255, x], fill=gold[3])
        c.d.rectangle([0, 255 - x, 255, 255 - x], fill=gold[3])
        c.d.rectangle([x, 0, x, 255], fill=gold[3])
        c.d.rectangle([255 - x, 0, 255 - x, 255], fill=gold[3])
    for x in range(2):
        c.d.rectangle([12, 12 + x, 243, 12 + x], fill=gold[4])
        c.d.rectangle([12, 243 - x, 243, 243 - x], fill=gold[4])
        c.d.rectangle([12 + x, 12, 12 + x, 243], fill=gold[4])
        c.d.rectangle([243 - x, 12, 243 - x, 243], fill=gold[4])
    # Corner flourishes
    for cx, cy in [(20, 20), (236, 20), (20, 236), (236, 236)]:
        c.d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=gold[4])
        c.d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=gold[5])
        c.px(cx, cy, '#FFFFFF')

    # Sun (large, behind mountains)
    sun_cx, sun_cy = 128, 180
    for r in [40, 35, 30, 25, 20, 15, 10]:
        if r >= 35: c.d.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r], fill=hex_c('#FFAA40'))
        elif r >= 25: c.d.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r], fill=hex_c('#FFD060'))
        else: c.d.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r], fill=hex_c('#FFE890'))
    # Sun core (white-hot)
    c.d.ellipse([sun_cx - 8, sun_cy - 8, sun_cx + 8, sun_cy + 8], fill=hex_c('#FFF8C0'))

    # Distant mountains (purple silhouette)
    mountain_distant = [(8, 220), (40, 180), (70, 200), (110, 165), (150, 195), (190, 175), (220, 195), (247, 185), (247, 247), (8, 247)]
    c.d.polygon(mountain_distant, fill=hex_c('#3A1050'))
    # Snow caps
    snow_d = [(35, 185), (40, 180), (45, 185)]
    snow_d += [(105, 170), (110, 165), (115, 170)]
    snow_d += [(185, 180), (190, 175), (195, 180)]
    for i in range(0, len(snow_d), 3):
        c.d.polygon(snow_d[i:i+3], fill=hex_c('#F0E0F0'))

    # Mid mountains
    mountain_mid = [(8, 230), (50, 200), (100, 215), (150, 195), (200, 210), (247, 200), (247, 247), (8, 247)]
    c.d.polygon(mountain_mid, fill=hex_c('#2A0838'))
    # Snow on mid
    for x, y, w in [(48, 204, 4), (148, 200, 4), (198, 215, 3)]:
        c.d.polygon([(x, y), (x + w, y), (x + w//2, y - 3)], fill=hex_c('#D0B0D0'))

    # Foreground mountains
    mountain_fore = [(8, 240), (60, 215), (120, 230), (180, 210), (247, 225), (247, 247), (8, 247)]
    c.d.polygon(mountain_fore, fill=hex_c('#1A0420'))

    # Stars in upper sky
    import random
    random.seed(123)
    for _ in range(15):
        x = random.randint(20, 235)
        y = random.randint(20, 90)
        c.d.ellipse([x, y, x + 1, y + 1], fill=hex_c('#FFFFE0'))
    for _ in range(8):
        x = random.randint(20, 235)
        y = random.randint(20, 90)
        c.d.ellipse([x - 1, y, x + 1, y + 1], fill=hex_c('#FFFFE0'))

    # DRAGON (silhouette in flight, in front of sun)
    dragon_color = '#0A0010'
    dragon_hi = '#1A0828'
    # Body
    c.d.ellipse([100, 90, 160, 130], fill=hex_c(dragon_color))
    # Head
    c.d.ellipse([70, 75, 110, 110], fill=hex_c(dragon_color))
    # Snout
    c.d.polygon([(70, 90), (50, 95), (70, 100)], fill=hex_c(dragon_color))
    # Eye (glowing)
    c.px(80, 88, '#FFD040')
    c.px(81, 88, '#FFE080')
    # Horns
    c.d.polygon([(85, 75), (83, 65), (90, 75)], fill=hex_c(dragon_color))
    c.d.polygon([(95, 75), (97, 65), (100, 75)], fill=hex_c(dragon_color))
    # Neck
    c.d.rectangle([90, 105, 110, 120], fill=hex_c(dragon_color))
    # Wings (extended, large)
    # Left wing
    c.d.polygon([(110, 95), (40, 60), (20, 80), (45, 90), (25, 110), (65, 95)], fill=hex_c(dragon_color))
    # Wing membrane lines
    c.line_diag(110, 95, 40, 60, hex_c(dragon_hi))
    c.line_diag(45, 90, 40, 60, hex_c(dragon_hi))
    c.line_diag(45, 90, 25, 110, hex_c(dragon_hi))
    c.line_diag(65, 95, 25, 110, hex_c(dragon_hi))
    # Right wing
    c.d.polygon([(150, 95), (220, 60), (240, 80), (215, 90), (235, 110), (195, 95)], fill=hex_c(dragon_color))
    c.line_diag(150, 95, 220, 60, hex_c(dragon_hi))
    c.line_diag(215, 90, 220, 60, hex_c(dragon_hi))
    c.line_diag(215, 90, 235, 110, hex_c(dragon_hi))
    c.line_diag(195, 95, 235, 110, hex_c(dragon_hi))
    # Tail
    c.d.polygon([(155, 110), (200, 110), (230, 130), (220, 135), (180, 120)], fill=hex_c(dragon_color))
    # Tail spike
    c.d.polygon([(220, 120), (240, 105), (235, 130)], fill=hex_c(dragon_color))
    # Rim light on dragon (top edge from sun)
    rim_color = '#FF8050'
    for x in range(100, 160):
        c.px(x, 88, hex_c(rim_color))
    c.px(80, 73, hex_c(rim_color))
    c.px(85, 73, hex_c(rim_color))
    c.px(95, 73, hex_c(rim_color))
    c.line_diag(40, 60, 50, 60, hex_c(rim_color))
    c.line_diag(220, 60, 230, 60, hex_c(rim_color))

    # Fire breath from mouth
    c.d.polygon([(50, 95), (25, 85), (10, 90), (15, 100), (30, 102)], fill=hex_c('#FF6020'))
    c.d.polygon([(50, 95), (30, 90), (20, 95), (30, 98)], fill=hex_c('#FFA040'))
    c.d.polygon([(50, 95), (38, 93), (35, 95), (38, 97)], fill=hex_c('#FFE080'))
    c.px(48, 95, hex_c('#FFEF60'))

    return c.finish()

def main():
    make_bp_icon().save(f'{BP}/pack_icon.png')
    make_rp_icon().save(f'{RP}/pack_icon.png')
    print("✅ Pack icons regenerated")

if __name__ == '__main__':
    main()
