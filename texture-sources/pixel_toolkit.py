"""
Pixel art toolkit for "AAA" Minecraft texture quality.

This is the high-fidelity version that supersamples at 4x and snaps to pixels.
Key techniques:
- Draw at 4x resolution with sub-pixel coordinates
- Multi-tone color ramps (5-7 tones per material)
- Anti-aliased edges via PIL.Image.resize LANCZOS
- Proper silhouette design with interior detail
- Consistent art direction across all assets

Drawing workflow:
1. Create canvas at SUPER × TARGET size (4x for items, 8x for entities)
2. Draw with PIL ImageDraw using float coordinates
3. Optionally pre-blur for soft edges (e.g., glow particles)
4. Downsample to TARGET size with NEAREST (preserves pixel art look)
5. Apply final touches (specular highlights, etc.) at target size
"""

from PIL import Image, ImageDraw, ImageFilter
import math, os

# ═══════════════════════════════════════════════════════════════════
# CORE TOOLKIT
# ═══════════════════════════════════════════════════════════════════

def new_canvas(w, h, bg=(0, 0, 0, 0)):
    return Image.new('RGBA', (w, h), bg)

def new_super(target_w, target_h, super_=4, bg=(0, 0, 0, 0)):
    """Create a supersampled canvas 4x larger than the target."""
    return Image.new('RGBA', (target_w * super_, target_h * super_), bg)

def snap(image, target_w, target_h, super_=4, resample=Image.NEAREST):
    """Downsample a supersampled image to target size with pixel-art snap."""
    return image.resize((target_w, target_h), resample)

def hex_to_rgba(h, a=255):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, a)

# ═══════════════════════════════════════════════════════════════════
# COLOR RAMP UTILITIES
# ═══════════════════════════════════════════════════════════════════

def make_ramp(colors):
    """Convert a list of hex colors to a list of (r,g,b) tuples."""
    return [hex_to_rgba(c) for c in colors]

def lerp(c1, c2, t):
    """Linear interpolation between two RGBA tuples."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (c1[3] if len(c1) > 3 else 255,)

def ramp_from_2(light, dark, steps=5):
    """Make a 2-stop gradient."""
    c1, c2 = hex_to_rgba(light), hex_to_rgba(dark)
    return [lerp(c1, c2, i / (steps - 1)) for i in range(steps)]

def ramp_from_3(dark, mid, light, steps=7):
    """Make a 3-stop gradient with dark->mid->light."""
    c1, c2, c3 = hex_to_rgba(dark), hex_to_rgba(mid), hex_to_rgba(light)
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        if t < 0.5:
            out.append(lerp(c1, c2, t * 2))
        else:
            out.append(lerp(c2, c3, (t - 0.5) * 2))
    return out

def shift_hue(rgba, dh):
    """Shift a color's hue by dh (-180 to 180)."""
    r, g, b = rgba[:3]
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0: return rgba
    h = 0
    if mx == r: h = ((g - b) / d) % 6
    elif mx == g: h = (b - r) / d + 2
    else: h = (r - g) / d + 4
    h = (h * 60 + dh) % 360 / 60
    if 0 <= h < 1: nr, ng, nb = mx, mn + d * h, mn
    elif 1 <= h < 2: nr, ng, nb = mx - d * (h - 1), mx, mn
    elif 2 <= h < 3: nr, ng, nb = mn, mx, mn + d * (h - 2)
    elif 3 <= h < 4: nr, ng, nb = mn, mx - d * (h - 3), mx
    elif 4 <= h < 5: nr, ng, nb = mn + d * (h - 4), mn, mx
    else: nr, ng, nb = mx, mn, mx - d * (h - 5)
    return (int(nr), int(ng), int(nb), rgba[3] if len(rgba) > 3 else 255)

def darken(rgba, amount=0.5):
    """Darken a color by amount (0-1)."""
    r, g, b = rgba[:3]
    return (int(r * (1 - amount)), int(g * (1 - amount)), int(b * (1 - amount)), rgba[3] if len(rgba) > 3 else 255)

def lighten(rgba, amount=0.3):
    """Lighten a color by amount (0-1)."""
    r, g, b = rgba[:3]
    return (int(r + (255 - r) * amount), int(g + (255 - g) * amount), int(b + (255 - b) * amount), rgba[3] if len(rgba) > 3 else 255)

# ═══════════════════════════════════════════════════════════════════
# ADVANCED DRAWING PRIMITIVES
# ═══════════════════════════════════════════════════════════════════

def aa_line(draw, x1, y1, x2, y2, color, width=1.0):
    """Anti-aliased line. PIL ImageDraw.line has width; we approximate AA via width."""
    if width == 1:
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    else:
        # Use ellipse endpoints for AA
        draw.line([(x1, y1), (x2, y2)], fill=color, width=int(width))
        if int(width) >= 1:
            r = int(width) // 2
            draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color)
            draw.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=color)

def gradient_rect(draw, x, y, w, h, color_top, color_bottom):
    """Vertical gradient rectangle."""
    c1 = hex_to_rgba(color_top) if isinstance(color_top, str) else color_top
    c2 = hex_to_rgba(color_bottom) if isinstance(color_bottom, str) else color_bottom
    for i in range(int(h)):
        t = i / max(1, int(h) - 1)
        c = lerp(c1, c2, t)
        draw.line([(int(x), int(y) + i), (int(x) + int(w) - 1, int(y) + i)], fill=c)

def radial_gradient(img, cx, cy, r_inner, r_outer, color_center, color_edge):
    """Place a radial gradient into an image. Used for orbs, glows."""
    c1 = hex_to_rgba(color_center) if isinstance(color_center, str) else color_center
    c2 = hex_to_rgba(color_edge) if isinstance(color_edge, str) else color_edge
    px = img.load()
    w, h = img.size
    for y in range(int(cy - r_outer), int(cy + r_outer) + 1):
        for x in range(int(cx - r_outer), int(cx + r_outer) + 1):
            d = math.hypot(x - cx, y - cy)
            if d > r_outer: continue
            if d < r_inner:
                color = c1
            else:
                t = (d - r_inner) / max(1, (r_outer - r_inner))
                color = lerp(c1, c2, t)
            if 0 <= x < w and 0 <= y < h:
                # alpha blend with existing
                existing = px[x, y]
                a = color[3] / 255
                r = int(existing[0] * (1 - a) + color[0] * a)
                g = int(existing[1] * (1 - a) + color[1] * a)
                b = int(existing[2] * (1 - a) + color[2] * a)
                px[x, y] = (r, g, b, max(existing[3], color[3]))

def noise_texture(img, intensity=10, seed=42):
    """Add subtle noise to a texture for organic feel."""
    import random
    random.seed(seed)
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0: continue
            n = (random.random() - 0.5) * intensity * 2
            px[x, y] = (
                max(0, min(255, int(r + n))),
                max(0, min(255, int(g + n))),
                max(0, min(255, int(b + n))),
                a
            )

# ═══════════════════════════════════════════════════════════════════
# HIGH-LEVEL: DRAW A 16x16 ITEM AT 4X, SNAP TO 16
# ═══════════════════════════════════════════════════════════════════

def draw_at_target(target_w, target_h, super_=8, draw_fn=None, save_path=None):
    """Generic: create super-canvas, call draw_fn(canvas, draw, super_), then snap."""
    img = new_super(target_w, target_h, super_)
    d = ImageDraw.Draw(img)
    if draw_fn:
        draw_fn(img, d, super_)
    result = snap(img, target_w, target_h, super_)
    if save_path:
        result.save(save_path)
    return result

# ═══════════════════════════════════════════════════════════════════
# TEST: Simple sword at 4x supersampled
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Quick sanity test
    def test(img, d, s):
        d.rectangle([0, 0, 16*s, 16*s], fill=(0, 0, 0, 0))
        d.rectangle([6*s, 1*s, 9*s, 12*s], fill='#80B0D8', outline='#FFFFFF')
        d.rectangle([6*s, 1*s, 7*s, 12*s], fill='#C0E0F8')

    out = draw_at_target(16, 16, 4, test)
    out.save('/tmp/test.png')
    print(f"Test image: {out.size}")
