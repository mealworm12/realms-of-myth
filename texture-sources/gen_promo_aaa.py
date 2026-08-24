"""
Promo art generator — release v1.0.0 "Ascension".
House pipeline (PIL, deterministic, no RNG). Generates:
  docs/screenshots/banner.png       (1280x480 texture collage + title)
  docs/screenshots/grid_items.png   (texture showcase grid)
  docs/screenshots/grid_armor.png   (texture showcase grid)
  docs/screenshots/grid_entities.png(texture showcase grid)

These are TEXTURE SHOWCASES, not in-game photography.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, 'realms_of_myth_RP', 'textures')
OUT = os.path.join(ROOT, 'docs', 'screenshots')
os.makedirs(OUT, exist_ok=True)

INK = (16, 12, 24)
GOLD = (255, 208, 96)
PARCH = (232, 220, 196)


def load(path):
    p = os.path.join(RP, path)
    if not os.path.exists(p):
        return None
    return Image.open(p).convert('RGBA')


def find_item(*names):
    for n in names:
        img = load(os.path.join('items', n + '.png'))
        if img:
            return img
    return None


def find_entity(*names):
    for n in names:
        img = load(os.path.join('entity', n + '.png'))
        if img:
            return img
    return None


def font(size):
    for cand in ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'):
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)  # Pillow >= 10.1 scalable
    except Exception:
        return ImageFont.load_default()


def upscale(img, cell):
    # nearest-neighbor pixel upscale to fit cell
    w, h = img.size
    s = max(1, min(cell // max(w, 1), cell // max(h, 1)))
    return img.resize((w * s, h * s), Image.NEAREST)


def draw_grid(names, finder, cols, cell, title, subtitle):
    rows = (len(names) + cols - 1) // cols
    header = 110
    W = cols * cell + (cols + 1) * 18
    H = header + rows * cell + (rows + 1) * 18 + 50
    canvas = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(canvas)
    f_t, f_s, f_l = font(44), font(20), font(15)
    d.text((24, 22), title, fill=GOLD, font=f_t)
    d.text((26, 74), subtitle, fill=PARCH, font=f_s)
    for i, name in enumerate(names):
        r, c = divmod(i, cols)
        x = 18 + c * (cell + 18)
        y = header + r * (cell + 18)
        d.rounded_rectangle([x, y, x + cell, y + cell], radius=8,
                            fill=(28, 24, 40), outline=(70, 60, 90), width=2)
        img = finder(name)
        if img:
            up = upscale(img, cell - 28)
            ux = x + (cell - up.width) // 2
            uy = y + (cell - up.height) // 2
            canvas.paste(up, (ux, uy), up)
        label = name.replace('_', ' ')
        tw = d.textlength(label, font=f_l)
        if tw < cell - 8:
            d.text((x + (cell - tw) / 2, y + cell - 2), label,
                   fill=(150, 140, 165), font=f_l)
    return canvas


def make_banner():
    W, H = 1280, 480
    canvas = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(canvas)

    # subtle vignette bands
    for i, a in enumerate(range(6)):
        shade = 24 + i * 4
        d.rectangle([0, H - (i + 1) * 14, W, H - i * 14], fill=(shade + 10, shade, shade + 18))

    heroes = [
        ('items/dawnbreaker.png', 60, 300),
        ('items/stormcaller_hammer.png', 190, 290),
        ('entity/dragon_fire.png', 330, 250),
        ('armor/mythril_humanoid.png', 900, 260),
        ('items/void_reaver.png', 1080, 300),
        ('blocks/ancient_altar.png', 560, 330),
    ]
    for path, x, y in heroes:
        img = load(path)
        if not img:
            continue
        up = upscale(img, 150)
        canvas.paste(up, (x + (150 - up.width) // 2, y + (150 - up.height) // 2), up)

    f_title, f_sub, f_tag = font(72), font(30), font(19)
    title = "REALMS OF MYTH"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2 + 3, 63), title, fill=(0, 0, 0), font=f_title)
    d.text(((W - tw) / 2, 60), title, fill=GOLD, font=f_title)
    sub = "ASCENSION  ·  v1.0.0"
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 160), sub, fill=PARCH, font=f_sub)
    tag = "A fantasy RPG add-on: races, classes, dragons, mythic gear & rituals"
    tgw = d.textlength(tag, font=f_tag)
    d.text(((W - tgw) / 2, H - 42), tag, fill=(170, 158, 180), font=f_tag)

    d.text((24, H - 68), "Texture showcase (procedural art pipeline)",
           fill=(120, 112, 132), font=f_tag)
    return canvas


def main():
    items = ['dawnbreaker', 'stormcaller_hammer', 'void_reaver', 'mythril_sword',
             'mythril_bow', 'dragon_bone_greatsword', 'dragonslayer_spear',
             'elven_dagger', 'enchanted_bow', 'shadowfang_dagger', 'giant_club',
             'troll_warhammer', 'magic_staff', 'dragon_heart', 'dragon_scale',
             'dragon_egg', 'fire_essence', 'frost_essence']
    armor = ['mythril_helmet', 'mythril_chestplate', 'mythril_leggings', 'mythril_boots',
             'mage_master_helmet', 'mage_master_chestplate', 'mage_master_leggings',
             'mage_master_boots', 'paladin_master_helmet', 'paladin_master_chestplate',
             'ranger_master_helmet', 'ranger_master_chestplate', 'druid_master_helmet',
             'druid_master_chestplate', 'berserker_master_helmet',
             'berserker_master_chestplate', 'class_token_mage', 'class_token_paladin']
    entities = ['dragon_fire', 'dragon_frost', 'dragon_whelp', 'elf_warrior',
                'troll_brute', 'giant_colossus']

    def fi(n):
        return load(os.path.join('items', n + '.png'))

    def fa(n):
        return load(os.path.join('items', n + '.png'))

    def fe(n):
        return load(os.path.join('entity', n + '.png'))

    make_banner().save(os.path.join(OUT, 'banner.png'))
    draw_grid(items, fi, 6, 128, 'ITEMS & MYTHIC GEAR',
              'Texture showcase — procedural art pipeline').save(
        os.path.join(OUT, 'grid_items.png'))
    draw_grid(armor, fa, 6, 128, 'ARMOR & CLASS REGALIA',
              'Texture showcase — procedural art pipeline').save(
        os.path.join(OUT, 'grid_armor.png'))
    draw_grid(entities, fe, 6, 160, 'DRAGONS & CREATURES',
              'Texture showcase — procedural art pipeline').save(
        os.path.join(OUT, 'grid_entities.png'))
    print('promo art written to', OUT)


if __name__ == '__main__':
    main()
