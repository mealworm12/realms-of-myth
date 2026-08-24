"""
Realms of Myth — custom particle TEXTURE generator (house PIL pipeline).

Generates soft-alpha VFX sprites under realms_of_myth_RP/textures/particles/.
Style follows pixel_toolkit.py: supersample 4x, draw with sub-pixel coords,
downsample with LANCZOS for smooth glow sprites (particles are glows, not
hard pixel art, so LANCZOS is correct here).

Run from repo root: python3 texture-sources/gen_particles_aaa.py
"""

import os, math
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'realms_of_myth_RP', 'textures', 'particles')
SUPER = 4


def canvas(size):
    return Image.new('RGBA', (size * SUPER, size * SUPER), (0, 0, 0, 0))


def finish(img, size):
    return img.resize((size, size), Image.LANCZOS)


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name))
    print(f'  wrote textures/particles/{name}')


def soft_blob(size, inner, outer, core=0.55):
    """Radial-gradient soft glow blob: inner color center -> outer transparent."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    c = size * SUPER / 2
    steps = 48
    for i in range(steps, -1, -1):
        t = i / steps                      # 0 = edge, 1 = center
        r = t * c * 0.98
        if t > core:
            k = 1 - (t - core) / (1 - core)   # ramp down outside core
        else:
            k = 1.0
        col = tuple(int(inner[j] * k + outer[j] * (1 - k)) for j in range(3))
        a = int(255 * min(1.0, k * 1.1))
        d.ellipse([c - r, c - r, c + r, c + r], fill=col + (a,))
    return finish(img.filter(ImageFilter.GaussianBlur(SUPER)), size)


def shard(size, length_ratio, width_ratio, base, tip):
    """Elongated glowing crystal shard pointing up, centered."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    W = H = size * SUPER
    cx, half_len, half_w = W / 2, H / 2 * length_ratio, W / 2 * width_ratio
    # body: tapered diamond
    pts = [(cx, H / 2 - half_len), (cx + half_w, H / 2),
           (cx, H / 2 + half_len), (cx - half_w, H / 2)]
    d.polygon(pts, fill=base + (230,))
    # bright core line
    d.line([(cx, H / 2 - half_len * 0.7), (cx, H / 2 + half_len * 0.7)],
           fill=tip + (255,), width=max(2, int(half_w * 0.4)))
    img = img.filter(ImageFilter.GaussianBlur(SUPER // 2))
    return finish(img, size)


def sparkle(size, color, arms=4):
    """Cross/star flare with bright core."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    c = S / 2
    L = S * 0.46
    w = S * 0.045
    for i in range(arms):
        ang = i * math.pi / arms
        x2, y2 = c + L * math.cos(ang), c + L * math.sin(ang)
        x3, y3 = c - L * math.cos(ang), c - L * math.sin(ang)
        d.line([(x2, y2), (x3, y3)], fill=color + (235,), width=int(w))
    d.ellipse([c - S*0.09, c - S*0.09, c + S*0.09, c + S*0.09], fill=(255, 255, 255, 255))
    img = img.filter(ImageFilter.GaussianBlur(SUPER // 2))
    return finish(img, size)


def puff(size, tint, density=0.75):
    """Irregular multi-lobe smoke/dust puff."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    rng_lobe = [(0.30, 0.42, 0.38, 0.45), (0.62, 0.35, 0.34, 0.40),
                (0.48, 0.60, 0.36, 0.42), (0.28, 0.62, 0.26, 0.32),
                (0.68, 0.58, 0.28, 0.34)]
    for lx, ly, lr, la in rng_lobe:
        r = S * lr
        col = tint + (int(255 * density * la * 0.7),)
        d.ellipse([S*lx - r, S*ly - r, S*lx + r, S*ly + r], fill=col)
    img = img.filter(ImageFilter.GaussianBlur(SUPER))
    return finish(img, size)


def ring(size, color, thickness=0.10, glow=True):
    """Soft circular shockwave ring."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    steps = 40
    for i in range(steps):
        t = i / steps
        r = S * (0.44 - t * thickness * 1.6)
        a = int(255 * (1 - t) ** 1.5)
        d.ellipse([S/2 - r, S/2 - r, S/2 + r, S/2 + r],
                  outline=color + (a,), width=max(2, int(S * thickness / steps * 2)))
    if glow:
        img = img.filter(ImageFilter.GaussianBlur(SUPER))
    return finish(img, size)


def leaf(size, base, vein):
    """Simple rounded leaf with central vein, tip up-right."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    pts = [(S*0.22, S*0.78), (S*0.18, S*0.42), (S*0.42, S*0.16),
           (S*0.74, S*0.20), (S*0.84, S*0.52), (S*0.62, S*0.82)]
    d.polygon(pts, fill=base + (235,))
    d.line([(S*0.24, S*0.76), (S*0.72, S*0.26)], fill=vein + (255,),
           width=int(S * 0.04))
    img = img.filter(ImageFilter.GaussianBlur(SUPER // 3))
    return finish(img, size)


def bolt_segment(size, color):
    """Jagged electric arc crackle across the frame."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    pts = []
    n = 7
    for i in range(n + 1):
        x = S * (0.08 + 0.84 * i / n)
        y = S * (0.5 + (0.42 if i % 2 == 0 else -0.42) *
                 (0.55 if 0 < i < n else 0.0))
        pts.append((x, y))
    d.line(pts, fill=color + (240,), width=int(S * 0.06))
    d.line(pts, fill=(255, 255, 255, 255), width=int(S * 0.02))
    img = img.filter(ImageFilter.GaussianBlur(SUPER // 2))
    return finish(img, size)


def drip(size, top, bottom):
    """Vertical blood/liquid drip, heavier at bottom."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    d.rounded_rectangle([S*0.40, S*0.12, S*0.60, S*0.66],
                        radius=int(S*0.10), fill=top + (225,))
    d.ellipse([S*0.33, S*0.58, S*0.67, S*0.92], fill=bottom + (245,))
    d.ellipse([S*0.42, S*0.64, S*0.54, S*0.78], fill=(255, 255, 255, 90))
    img = img.filter(ImageFilter.GaussianBlur(SUPER // 3))
    return finish(img, size)


def mote(size, color):
    """Small rune mote: glow dot with tiny diamond core."""
    img = canvas(size)
    d = ImageDraw.Draw(img)
    S = size * SUPER
    c = S / 2
    for i in range(24, 0, -1):
        r = c * i / 24
        a = int(160 * (1 - i / 24))
        d.ellipse([c-r, c-r, c+r, c+r], fill=color + (a,))
    d.polygon([(c, c-S*0.16), (c+S*0.16, c), (c, c+S*0.16), (c-S*0.16, c)],
              fill=(255, 255, 255, 255))
    return finish(img.filter(ImageFilter.GaussianBlur(SUPER // 3)), size)


# ═══════════════════════════════════════════════════════════════════
# TEXTURES
# ═══════════════════════════════════════════════════════════════════

ORANGE   = (255, 168, 64)
CRIMSON  = (220, 48, 24)
ICE      = (140, 210, 255)
WHITE    = (255, 255, 255)
VIOLET   = (186, 110, 255)
GOLD     = (255, 216, 96)
BLOOD    = (170, 16, 24)
DUST     = (148, 130, 108)
GREEN_LF = (86, 176, 72)
GREEN_VN = (150, 214, 120)
ROOT_BR  = (122, 88, 48)
ROOT_GR  = (96, 158, 70)
ELEC     = (150, 200, 255)
RED      = (255, 40, 40)
MIST     = (198, 232, 255)
SMOKE    = (70, 56, 50)


def main():
    print('Generating particle textures...')
    # 1  fireball_trail — hot core ember, orange -> deep red falloff
    save(soft_blob(32, ORANGE, CRIMSON), 'ember.png')
    # 2  frost_nova_ring — elongated ice shard
    save(shard(32, 0.85, 0.16, ICE, WHITE), 'ice_shard.png')
    # 3  arcane_step — violet rune mote
    save(mote(32, VIOLET), 'rune_mote.png')
    # 4  holy_light_beam / 14 class_select_burst — gold star flare
    save(sparkle(32, GOLD), 'sparkle_gold.png')
    # 5  divine_shield_aura — softer wide halo glow
    save(soft_blob(32, (255, 236, 170), GOLD, core=0.35), 'halo_glow.png')
    # 6  rage_blood_motes — drip
    save(drip(32, BLOOD, CRIMSON), 'blood_drip.png')
    # 7  ground_slam_dust — tan dust puff
    save(puff(32, DUST), 'dust_puff.png')
    # 8  nature_blessing_leaves — leaf sprite
    save(leaf(32, GREEN_LF, GREEN_VN), 'leaf.png')
    save(sparkle(16, (228, 255, 180)), 'pollen.png')
    # 9  entangle_roots — earthy wisp
    save(puff(32, ROOT_BR, density=0.55), 'root_wisp.png')
    # 10 spear_lightning — arc segment
    save(bolt_segment(32, ELEC), 'lightning_arc.png')
    # 11 dragon_breath_fire — dark ember smoke blob
    save(puff(32, SMOKE, density=0.85), 'fire_smoke.png')
    save(soft_blob(32, (255, 196, 90), (200, 60, 20)), 'fire_glow.png')
    # 12 dragon_breath_frost — crystalline mist
    save(puff(32, MIST, density=0.65), 'frost_mist.png')
    save(shard(16, 0.9, 0.14, WHITE, ICE), 'frost_chip.png')
    # 13 phase_enrage — red shockwave ring + burst core
    save(ring(64, RED, thickness=0.12), 'shockwave_ring.png')
    save(soft_blob(32, (255, 96, 64), RED), 'enrage_core.png')
    print('Done.')


if __name__ == '__main__':
    main()
