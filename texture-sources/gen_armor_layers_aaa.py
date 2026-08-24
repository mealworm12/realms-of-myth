"""
Worn-layer armor textures (humanoid layout, 64x32) for Realms of Myth.

7 sets x (main + optional leggings layer):
  mythril, dragonscale, mage_master, ranger_master,
  berserker_master, paladin_master, druid_master

Output: realms_of_myth_RP/textures/armor/<set>_humanoid.png
        realms_of_myth_RP/textures/armor/<set>_humanoid_leggings.png

Vanilla humanoid armor UV layout (64x32), per layer:
  - Helmet:   head box  (32,0)-(47,15) front face at (40,8)-(47,15)
  - Body:     body box  (16,16)-(39,31) front at (20,20)-(27,27)
  - Right arm (40,16)-(55,31); mirrored to left arm by the engine
  - Right leg (0,16)-(15,31) on MAIN; leggings layer uses same slots
  - Boots overlay right/left leg region on main layer too.

House style: deliberate pixel placement, 5-7 tone ramps, dark outlines,
palettes inherited from gen_armor_aaa.ARMOR_SETS.
Deterministic: no randomness.
"""

import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "realms_of_myth_RP", "textures", "armor")
os.makedirs(OUT, exist_ok=True)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def lighten(c, f=0.35):
    return tuple(max(0, min(255, int(v + (255 - v) * f))) for v in c)


class Ramp:
    """7-tone material ramp from a base hex: outline..highlight."""
    def __init__(self, base_hex, out_hex=None, accent_hex=None):
        b = hx(base_hex)
        self.out = hx(out_hex) if out_hex else shade(b, 0.25)
        self.lo = shade(b, 0.6)
        self.base = b
        self.mid = lighten(b, 0.12)
        self.hi = lighten(b, 0.3)
        self.spec = lighten(b, 0.55)
        self.accent = hx(accent_hex) if accent_hex else self.spec


ARMOR_SETS = {
    # name: (base, out, accent, style)
    "mythril":          ("#6A7A88", "#1A2A38", "#D4AF37", "plate"),
    "dragonscale":      ("#6A1A1A", "#1A0000", "#D4AF37", "scale"),
    "mage_master":      ("#3A1068", "#0A0020", "#E0A0FF", "robe"),
    "ranger_master":    ("#5A4020", "#1A0A00", "#80E040", "leather"),
    "berserker_master": ("#8A2A2A", "#2A0000", "#FF8040", "plate"),
    "paladin_master":   ("#B09030", "#2A1000", "#FFF080", "plate"),
    "druid_master":     ("#2A5A4A", "#001A10", "#80FFC0", "robe"),
}

W, H = 64, 32
T = (0, 0, 0, 0)  # transparent


class Layer:
    def __init__(self):
        self.px = [[T] * W for _ in range(H)]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def image(self):
        img = Image.new("RGBA", (W, H), T)
        data = []
        for y in range(H):
            for x in range(W):
                data.append(self.px[y][x])
        img.putdata(data)
        return img


def dither(ramp, x, y):
    """Deliberate 4-step vertical shading within a box face."""
    return ramp


def face(img, x0, y0, x1, y1, ramp, style="plate"):
    """Fill a box face with vertical shading + top highlight + bottom shadow."""
    h = y1 - y0 + 1
    tones = [ramp.hi, ramp.base, ramp.base, ramp.lo]
    for y in range(y0, y1 + 1):
        t = tones[min(3, int((y - y0) / max(1, h) * 4))]
        for x in range(x0, x1 + 1):
            if style == "scale" and (x + y) % 3 == 0:
                img.set(x, y, ramp.lo)
            elif style == "robe":
                img.set(x, y, ramp.base if (y - y0) % 4 else ramp.mid)
            elif style == "leather" and (x - y) % 4 == 0:
                img.set(x, y, ramp.lo)
            else:
                img.set(x, y, t)
    # top highlight / bottom shadow rows
    for x in range(x0, x1 + 1):
        img.set(x, y0, ramp.hi)
        img.set(x, y1, ramp.lo)


def outline_box(img, x0, y0, x1, y1, ramp):
    for x in range(x0, x1 + 1):
        img.set(x, y0, ramp.out)
        img.set(x, y1, ramp.out)
    for y in range(y0, y1 + 1):
        img.set(x0, y, ramp.out)
        img.set(x1, y, ramp.out)


def draw_main_layer(set_name, ramp, style):
    m = Layer()

    # ---- HELMET (head wrap): UV (32,0)-(47,15). Draw a full helmet hood:
    # top cap row 8-9, sides columns 32/47, front band across 40-47 rows 8-11
    face(m, 32, 8, 39, 15, ramp, style)   # head sides/back/top wrap
    face(m, 40, 8, 47, 15, ramp, style)   # head front
    outline_box(m, 32, 8, 47, 15, ramp)
    # visor slit on the front face
    for x in range(42, 47):
        m.set(x, 11, ramp.out)
        m.set(x, 12, ramp.out)
    m.set(43, 12, ramp.accent)
    m.set(46, 12, ramp.accent)
    # crest strip along top
    for x in range(36, 44):
        m.set(x, 8, ramp.accent if x % 2 == 0 else ramp.hi)

    # ---- BODY (chest): UV (16,16)-(39,31): back (16,16)-(19,31)? Actually
    # vanilla: torso front (20,20)-(27,27), torso back (28,20)-(35,27),
    # sides (16,20)-(19,27)... we fill the whole 16-39 x 20-27 band plus
    # shoulder caps at rows 16-19.
    face(m, 16, 16, 39, 19, ramp, style)              # shoulders band
    face(m, 16, 20, 39, 27, ramp, style)              # torso wrap faces
    outline_box(m, 16, 16, 39, 19, ramp)
    outline_box(m, 16, 20, 39, 27, ramp)
    # chest emblem on front face center
    m.rect(23, 21, 24, 22, ramp.accent)
    m.set(22, 22, ramp.accent)
    m.set(25, 22, ramp.accent)
    m.set(23, 23, ramp.accent)
    m.set(24, 23, ramp.accent)
    # belt line
    for x in range(17, 39):
        m.set(x, 26, ramp.lo if x % 2 else ramp.out)

    # ---- RIGHT ARM: UV (40,16)-(55,31), arm faces occupy (44,20)-(51,27)
    face(m, 40, 20, 43, 27, ramp, style)
    face(m, 44, 20, 51, 27, ramp, style)
    face(m, 52, 20, 55, 27, ramp, style)
    outline_box(m, 40, 20, 55, 27, ramp)
    # pauldron cap
    for x in range(40, 56):
        m.set(x, 20, ramp.accent if x % 3 == 0 else ramp.hi)

    # ---- RIGHT LEG / BOOT: UV (0,16)-(15,31), leg faces (4,20)-(11,31)
    face(m, 0, 20, 3, 31, ramp, style)
    face(m, 4, 20, 11, 31, ramp, style)
    face(m, 12, 20, 15, 31, ramp, style)
    outline_box(m, 0, 20, 15, 31, ramp)
    # boot cuff
    for x in range(0, 16):
        m.set(x, 20, ramp.accent if x % 2 == 0 else ramp.hi)
    # sole
    for x in range(0, 16):
        m.set(x, 31, ramp.out)

    return m.image()


def draw_leggings_layer(set_name, ramp, style):
    """Second layer texture used for *_humanoid_leggings.png (leggings outer)."""
    m = Layer()
    # hips/body lower wrap
    face(m, 16, 20, 39, 27, ramp, style)
    outline_box(m, 16, 20, 39, 27, ramp)
    for x in range(17, 39):
        m.set(x, 26, ramp.lo)
    # legs full length
    for x0 in (0, 12):
        pass
    face(m, 0, 20, 15, 31, ramp, style)
    outline_box(m, 0, 20, 15, 31, ramp)
    for x in range(0, 16):
        m.set(x, 31, ramp.out)
    return m.image()


def main():
    count = 0
    for name, (base, out, accent, style) in ARMOR_SETS.items():
        ramp = Ramp(base, out, accent)
        draw_main_layer(name, ramp, style).save(
            os.path.join(OUT, f"{name}_humanoid.png"))
        draw_leggings_layer(name, ramp, style).save(
            os.path.join(OUT, f"{name}_humanoid_leggings.png"))
        count += 2
    print(f"[armor-layers] wrote {count} worn-layer textures -> {OUT}")


if __name__ == "__main__":
    main()
