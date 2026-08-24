"""
Armor item icons v2 (16x16) for Realms of Myth.

Replaces the flat 6-tone icons from gen_armor_aaa.py with richer
7-tone material ramps + per-piece detail (rivets, scales, runes).

Output: realms_of_myth_RP/textures/items/<set>_<piece>.png
Deterministic; palettes inherited from gen_armor_aaa.ARMOR_SETS.
"""

import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "realms_of_myth_RP", "textures", "items")
os.makedirs(OUT, exist_ok=True)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def lighten(c, f=0.35):
    return tuple(max(0, min(255, int(v + (255 - v) * f))) for v in c)


class Ramp:
    """7 tones: out, lo2, lo, base, mid, hi, spec."""
    def __init__(self, base_hex, out_hex=None, accent_hex=None):
        b = hx(base_hex)
        self.out = hx(out_hex) if out_hex else shade(b, 0.22)
        self.lo2 = shade(b, 0.42)
        self.lo = shade(b, 0.62)
        self.base = b
        self.mid = lighten(b, 0.10)
        self.hi = lighten(b, 0.28)
        self.spec = lighten(b, 0.52)
        self.accent = hx(accent_hex) if accent_hex else self.spec


ARMOR_SETS = {
    "mythril":          ("#6A7A88", "#1A2A38", "#D4AF37"),
    "dragonscale":      ("#6A1A1A", "#1A0000", "#D4AF37"),
    "mage_master":      ("#3A1068", "#0A0020", "#E0A0FF"),
    "ranger_master":    ("#5A4020", "#1A0A00", "#80E040"),
    "berserker_master": ("#8A2A2A", "#2A0000", "#FF8040"),
    "paladin_master":   ("#B09030", "#2A1000", "#FFF080"),
    "druid_master":     ("#2A5A4A", "#001A10", "#80FFC0"),
}

T = (0, 0, 0, 0)


def alpha(c):
    return c + (255,) if len(c) == 3 else c


class C:
    def __init__(self):
        self.g = [[T] * 16 for _ in range(16)]

    def px(self, x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            self.g[y][x] = alpha(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def save(self, path):
        img = Image.new("RGBA", (16, 16))
        img.putdata([self.g[y][x] for y in range(16) for x in range(16)])
        img.save(path)


def dome(c, r, cx=8, top=3, w=9, h=7):
    """Rounded helmet dome with vertical shading."""
    x0, x1 = cx - w // 2, cx + w // 2
    for i, y in enumerate(range(top, top + h)):
        t = [r.spec, r.hi, r.mid, r.base, r.base, r.lo, r.lo2][i]
        # taper the bottom rows inward slightly at corners
        inset = 1 if y >= top + h - 1 else 0
        for x in range(x0 + inset, x1 - inset + 1):
            c.px(x, y, t)
    # specular glint upper-left
    c.px(cx - 2, top + 1, r.spec)
    c.px(cx - 1, top + 1, r.hi)
    c.px(cx - 2, top + 2, r.hi)


def outline(c, pts, r):
    for x, y in pts:
        c.px(x, y, r.out)


def helmet(r, set_name):
    c = C()
    dome(c, r)
    # visor slit rows 7-8
    c.rect(4, 7, 11, 8, r.out)
    c.px(5, 8, r.accent)
    c.px(10, 8, r.accent)
    # brow band
    c.rect(4, 5, 11, 5, r.hi)
    c.px(4, 5, r.spec); c.px(11, 5, r.lo2)
    # crest
    c.rect(7, 0, 8, 2, r.accent)
    c.px(7, 2, r.hi); c.px(8, 2, r.hi)
    # cheek guards
    c.px(3, 9, r.lo); c.px(12, 9, r.lo)
    c.px(3, 10, r.lo2); c.px(12, 10, r.lo2)
    # rivets
    c.px(4, 6, r.out); c.px(11, 6, r.out)
    outline(c, [(3, 3), (12, 3), (2, 4), (13, 4), (2, 8), (13, 8),
                (3, 10), (12, 10), (4, 11), (11, 11)], r)
    if set_name == "mage_master":       # pointed wizard helm tip
        c.px(7, 0, r.accent); c.px(8, 0, r.hi); c.px(8, 1, r.spec)
    if set_name in ("paladin_master", "berserker_master"):  # horns
        c.px(2, 2, r.accent); c.px(1, 1, r.accent)
        c.px(13, 2, r.accent); c.px(14, 1, r.accent)
    return c


def chestplate(r, set_name):
    c = C()
    # shoulders row 2-4
    c.rect(1, 2, 4, 5, r.hi)
    c.rect(11, 2, 14, 5, r.lo)
    c.rect(2, 2, 3, 4, r.spec)
    c.px(12, 3, r.mid); c.px(13, 4, r.lo2)
    # torso rows 3-12
    c.rect(4, 3, 11, 12, r.base)
    c.rect(4, 3, 5, 11, r.hi)      # left light edge
    c.rect(10, 4, 11, 12, r.lo)    # right shadow edge
    c.rect(4, 12, 11, 12, r.lo2)   # bottom shadow
    # collar
    c.rect(6, 2, 9, 2, r.lo)
    # center seam + emblem
    c.rect(7, 4, 8, 11, r.mid)
    emblem = {
        "mage_master": lambda: (c.rect(7, 5, 8, 6, r.accent),
                                c.px(6, 6, r.accent), c.px(9, 6, r.accent)),
        "ranger_master": lambda: (c.px(6, 5, r.accent), c.px(9, 5, r.accent),
                                  c.px(7, 4, r.accent), c.px(8, 4, r.accent),
                                  c.px(7, 7, r.accent), c.px(8, 7, r.accent)),
        "berserker_master": lambda: (c.rect(6, 5, 7, 7, r.accent),
                                     c.rect(8, 5, 9, 7, r.accent)),
        "paladin_master": lambda: (c.rect(7, 4, 8, 7, r.accent),
                                   c.px(6, 5, r.accent), c.px(9, 5, r.accent)),
        "druid_master": lambda: (c.px(7, 5, r.accent), c.px(8, 5, r.accent),
                                 c.px(6, 6, r.accent), c.px(9, 6, r.accent),
                                 c.px(7, 7, r.accent), c.px(8, 7, r.accent)),
        "mythril": lambda: (c.px(7, 5, r.accent), c.px(8, 5, r.accent),
                            c.rect(6, 6, 9, 6, r.accent)),
        "dragonscale": lambda: (c.px(6, 5, r.accent), c.px(9, 6, r.accent),
                                c.px(7, 7, r.accent), c.px(8, 5, r.accent)),
    }
    emblem[set_name]()
    # belt
    c.rect(4, 11, 11, 11, r.lo2)
    c.rect(7, 11, 8, 11, r.accent)
    # rivets on shoulders
    c.px(2, 5, r.out); c.px(13, 5, r.out)
    outline(c, [(1, 1), (2, 1), (13, 1), (14, 1), (1, 5), (14, 5), (1, 6),
                (14, 6), (4, 2), (11, 2), (4, 13), (11, 13), (5, 13), (10, 13)], r)
    return c


def leggings(r, set_name):
    c = C()
    # waistband rows 1-3
    c.rect(3, 1, 12, 3, r.hi)
    c.rect(3, 1, 12, 1, r.spec)
    c.rect(3, 3, 12, 3, r.lo)
    c.px(7, 2, r.accent); c.px(8, 2, r.accent)
    # legs rows 4-14
    c.rect(4, 4, 7, 14, r.base)
    c.rect(8, 4, 11, 14, r.base)
    c.rect(4, 4, 4, 13, r.hi)
    c.rect(11, 4, 11, 13, r.lo)
    c.rect(8, 4, 8, 13, r.mid)
    # knee plates
    c.rect(5, 7, 6, 8, r.hi)
    c.rect(9, 7, 10, 8, r.hi)
    c.px(5, 8, r.base); c.px(9, 8, r.base)
    # bottom shading
    c.rect(4, 14, 11, 14, r.lo2)
    outline(c, [(3, 1), (12, 1), (2, 2), (13, 2), (3, 4), (12, 4),
                (4, 15), (7, 15), (8, 15), (11, 15)], r)
    return c


def boots(r, set_name):
    c = C()
    # boot shafts rows 2-8
    c.rect(3, 2, 6, 8, r.base)
    c.rect(9, 2, 12, 8, r.base)
    c.rect(3, 2, 3, 7, r.hi)
    c.rect(9, 2, 9, 7, r.hi)
    c.rect(6, 3, 6, 8, r.lo)
    c.rect(12, 3, 12, 8, r.lo)
    # cuffs
    c.rect(3, 2, 6, 2, r.hi)
    c.rect(9, 2, 12, 2, r.hi)
    c.px(3, 3, r.accent); c.px(12, 3, r.accent)
    # feet rows 9-12, toes point outward
    c.rect(1, 9, 6, 11, r.base)
    c.rect(9, 9, 14, 11, r.base)
    c.rect(1, 9, 1, 10, r.hi)
    c.rect(14, 9, 14, 10, r.lo)
    # toe caps + heel shading for extra depth
    c.rect(1, 9, 2, 10, r.spec)
    c.rect(13, 9, 14, 10, r.lo2)
    c.rect(3, 10, 5, 11, r.lo)
    c.rect(10, 10, 12, 11, r.lo2)
    # soles
    c.rect(1, 12, 6, 12, r.out)
    c.rect(9, 12, 14, 12, r.out)
    outline(c, [(3, 1), (6, 1), (9, 1), (12, 1), (2, 2), (13, 2),
                (0, 10), (0, 11), (15, 10), (15, 11), (1, 13), (14, 13)], r)
    return c


DRAWERS = {"helmet": helmet, "chestplate": chestplate,
           "leggings": leggings, "boots": boots}


def main():
    n = 0
    for name, (base, out, accent) in ARMOR_SETS.items():
        ramp = Ramp(base, out, accent)
        for slot, fn in DRAWERS.items():
            fn(ramp, name).save(os.path.join(OUT, f"{name}_{slot}.png"))
            n += 1
    print(f"[armor-icons-v2] wrote {n} icons -> {OUT}")


if __name__ == "__main__":
    main()
