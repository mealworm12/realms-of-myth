"""
Mythic weapon texture generator — extends the gen_weapons_aaa.py house pipeline
style into gen_mythic_aaa.py. Generates:
  RP/textures/items/dawnbreaker.png          (16x16 item icon)
  RP/textures/items/void_reaver.png
  RP/textures/items/stormcaller_hammer.png

Deterministic (no RNG) — re-runnable byte-stable. Uses pixel-level placement
with 7-tone ramps, matching the established AAA look of existing weapons.
"""

import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'realms_of_myth_RP', 'textures', 'items')

# 7-tone ramps (darkest -> lightest), consistent with house palettes
R = {
    'holy':   ['#5A4000', '#7A5800', '#C09020', '#E0B040', '#FFD060', '#FFF0A0', '#FFFFE0'],
    'gold':   ['#5A4000', '#7A5800', '#9A7000', '#C09020', '#E0B040', '#FFD060', '#FFF080'],
    'void':   ['#000000', '#0A0A1A', '#1A1A2E', '#2A2A44', '#3A3A5C', '#5A4A8A', '#9A6AAA'],
    'shadow': ['#000000', '#0A0A1A', '#1A1A2A', '#2A2A3A', '#3A3A4A', '#4A4A5A', '#5A5A6A'],
    'storm':  ['#0A2A3A', '#10405A', '#20608A', '#4080B0', '#60A0D0', '#A0D0F0', '#E0F6FF'],
    'wood':   ['#2A1A0A', '#4A2A1A', '#6A4A2A', '#8A6040', '#AA8050', '#D0A070', '#F0C890'],
}


def ramp(name, t):
    """Sample a ramp at t in [0,1]."""
    r = R[name]
    idx = min(len(r) - 1, max(0, int(t * len(r))))
    return r[idx]


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def new_canvas():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


def put(px, img, x, y, color):
    if isinstance(color, str):
        color = hex2rgb(color)
    img.putpixel((x, y), (*color, 255))


# ── Dawnbreaker: golden greatsword, diagonal blade with radiant core ──
def gen_dawnbreaker():
    img = new_canvas()
    # Blade: diagonal from (12,1) down-left to (6,7); wide greatsword
    for i in range(9):
        x, y = 12 - i, 1 + i
        t = i / 8.0
        put(None, img, x, y, ramp('holy', 0.85 - 0.35 * abs(t - 0.4)))       # core bright
        put(None, img, x - 1, y, ramp('gold', 0.55))                          # left bevel dark
        put(None, img, x + 1, y, ramp('gold', 0.75))                          # right bevel light
        put(None, img, x - 2, y, ramp('gold', 0.25))                          # edge outline
        # Radiant glints along the blade tip side
        if i % 3 == 1:
            put(None, img, x + 1, y - 1, '#FFFFE0')
    # Guard: perpendicular gold bar at (5,8)-(9,10)
    for gx in range(4, 9):
        put(None, img, gx, 8 + (9 - gx) // 2, ramp('gold', 0.85))
        put(None, img, gx, 9 + (9 - gx) // 2, ramp('gold', 0.45))
    # Handle: down-left diagonal
    for i in range(5):
        x, y = 5 - i, 9 + i
        put(None, img, x, y, ramp('wood', 0.5))
        put(None, img, x - 1, y, ramp('wood', 0.25))
    # Pommel gem
    put(None, img, 1, 13, '#FFF0A0')
    put(None, img, 0, 14, '#FFD060')
    return img


# ── Void Reaver: short black-purple dagger with violet glow ───────────
def gen_void_reaver():
    img = new_canvas()
    # Blade: short diagonal from (11,2) to (8,5)
    for i in range(5):
        x, y = 11 - i, 2 + i
        t = i / 4.0
        put(None, img, x, y, ramp('void', 0.75 - 0.25 * t))     # purple-lit spine
        put(None, img, x - 1, y, ramp('shadow', 0.55))           # dark bevel
        put(None, img, x + 1, y, ramp('shadow', 0.30))           # black edge
    # Violet glow tip
    put(None, img, 11, 2, '#9A6AAA')
    put(None, img, 10, 2, '#5A4A8A')
    # Guard
    put(None, img, 6, 6, '#3A3A5C')
    put(None, img, 7, 6, '#2A2A44')
    put(None, img, 6, 7, '#1A1A2E')
    # Handle
    for i in range(5):
        x, y = 5 - i, 8 + i
        put(None, img, x, y, ramp('shadow', 0.45))
        put(None, img, x - 1, y, ramp('shadow', 0.20))
    # Void gem pommel
    put(None, img, 0, 12, '#9A6AAA')
    put(None, img, 1, 13, '#5A4A8A')
    return img


# ── Stormcaller Hammer: heavy blue steel head on wood shaft ───────────
def gen_stormcaller_hammer():
    img = new_canvas()
    # Head block: rows 1-6, cols 4-12
    for y in range(1, 7):
        for x in range(4, 13):
            # Horizontal shading: darker at edges, lightning-bright center band
            edge = min(x - 4, 12 - x)
            base = 0.25 + 0.09 * edge
            if 7 <= x <= 8:
                put(None, img, x, y, ramp('storm', min(0.95, base + 0.35)))
            else:
                put(None, img, x, y, ramp('storm', base))
            if y == 1 or y == 6:
                # top/bottom rim darker
                c = img.getpixel((x, y))
                img.putpixel((x, y), (c[0] // 2, c[1] // 2, int(c[2] * 0.6), 255))
    # Lightning bolt glyph on the head face
    bolt = [(8, 2), (7, 3), (8, 3), (6, 4), (7, 4), (5, 5), (6, 5)]
    for bx, by in bolt:
        put(None, img, bx, by, '#E0F6FF')
    # Shaft: vertical from (7-8, 7) to (7-8, 14)
    for y in range(7, 15):
        put(None, img, 7, y, ramp('wood', 0.55))
        put(None, img, 8, y, ramp('wood', 0.35))
        put(None, img, 6, y, ramp('wood', 0.22))
    # Wrap detail
    for wy in (8, 12):
        put(None, img, 7, wy, ramp('storm', 0.5))
        put(None, img, 8, wy, ramp('storm', 0.4))
    return img


GENERATORS = {
    'dawnbreaker': gen_dawnbreaker,
    'void_reaver': gen_void_reaver,
    'stormcaller_hammer': gen_stormcaller_hammer,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in GENERATORS.items():
        path = os.path.join(OUT, f'{name}.png')
        fn().save(path)
        print(f'wrote {path}')


if __name__ == '__main__':
    main()
