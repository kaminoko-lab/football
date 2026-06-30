"""
Composites the Kaminoko logo onto a water bottle illustration.
Output: .tmp/kaminoko_water_bottle.png
"""

from PIL import Image, ImageDraw, ImageFilter
import os

LOGO_PATH = "brand_asset/kaminoko-herbal.png"
OUT_PATH  = ".tmp/kaminoko_water_bottle.png"
os.makedirs(".tmp", exist_ok=True)

W, H = 800, 1400

# ── background ─────────────────────────────────────────────────────────────────
bg = Image.new("RGBA", (W, H), (240, 243, 238, 255))
draw = ImageDraw.Draw(bg)

# soft radial gradient feel (light centre)
for r in range(400, 0, -1):
    alpha = int(40 * (1 - r / 400))
    draw.ellipse([W//2 - r, H//2 - r, W//2 + r, H//2 + r],
                 fill=(255, 255, 255, alpha))

# ── bottle dimensions ───────────────────────────────────────────────────────────
cx       = W // 2
body_l   = cx - 160     # left edge of bottle body
body_r   = cx + 160     # right edge
body_top = 280
body_bot = 1220
neck_l   = cx - 55
neck_r   = cx + 55
neck_top = 160
neck_bot = body_top     # shoulder starts here
cap_top  = 95
cap_bot  = neck_top + 8

# colours
C_BOTTLE   = (195, 230, 225, 220)   # frosted teal glass
C_LIGHT    = (230, 250, 248, 180)   # highlight
C_SHADOW   = (150, 195, 188, 200)   # shadow edge
C_EDGE     = (120, 175, 168, 255)   # outline
C_CAP      = (30, 100, 58, 255)
C_CAP_DK   = (15, 65, 35, 255)
C_LABEL_BG = (252, 255, 253, 230)
C_LABEL_BD = (180, 215, 205, 255)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)

# ── bottle body (rounded rect) ──────────────────────────────────────────────────
r = 30   # corner radius
# fill rounded rect for body
d.rounded_rectangle([body_l, body_top, body_r, body_bot], radius=r,
                    fill=C_BOTTLE, outline=C_EDGE, width=3)

# shoulder (trapezoid connecting neck to body)
shoulder_pts = [
    (neck_l, neck_bot),
    (body_l, body_top + 10),
    (body_r, body_top + 10),
    (neck_r, neck_bot),
]
d.polygon(shoulder_pts, fill=C_BOTTLE, outline=C_EDGE)
# clean up shoulder outline artefacts by re-drawing body edges
d.rounded_rectangle([body_l, body_top, body_r, body_bot], radius=r,
                    fill=None, outline=C_EDGE, width=3)

# ── neck ────────────────────────────────────────────────────────────────────────
d.rectangle([neck_l, neck_top, neck_r, neck_bot], fill=C_BOTTLE, outline=C_EDGE, width=2)

# ── cap ─────────────────────────────────────────────────────────────────────────
cap_l = neck_l - 10
cap_r = neck_r + 10
d.rounded_rectangle([cap_l, cap_top, cap_r, cap_bot], radius=8,
                    fill=C_CAP, outline=C_CAP_DK, width=2)
# cap ridges
for y in range(cap_top + 8, cap_bot - 4, 9):
    d.line([(cap_l + 3, y), (cap_r - 3, y)], fill=C_CAP_DK, width=1)

# ── highlight strip (left-centre, simulates cylindrical glass) ─────────────────
hi_l = body_l + 18
hi_r = body_l + 55
d.rounded_rectangle([hi_l, body_top + 30, hi_r, body_bot - 60], radius=18,
                    fill=C_LIGHT)

# ── shadow strip (right edge) ──────────────────────────────────────────────────
sh_l = body_r - 45
sh_r = body_r - 6
d.rounded_rectangle([sh_l, body_top + 20, sh_r, body_bot - 40], radius=15,
                    fill=C_SHADOW)

# ── composite onto bg ──────────────────────────────────────────────────────────
canvas = Image.alpha_composite(bg, layer)

# ── label band ─────────────────────────────────────────────────────────────────
label_pad = 22
label_top = 460
label_bot = 870
label_l   = body_l + label_pad
label_r   = body_r - label_pad

label_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(label_layer)
ld.rounded_rectangle([label_l, label_top, label_r, label_bot], radius=14,
                     fill=C_LABEL_BG, outline=C_LABEL_BD, width=2)
canvas = Image.alpha_composite(canvas, label_layer)

# ── logo ───────────────────────────────────────────────────────────────────────
logo = Image.open(LOGO_PATH).convert("RGBA")
logo_max_w = int((label_r - label_l) * 0.82)
logo_max_h = int((label_bot - label_top) * 0.88)
scale = min(logo_max_w / logo.width, logo_max_h / logo.height)
lw = int(logo.width  * scale)
lh = int(logo.height * scale)
logo = logo.resize((lw, lh), Image.LANCZOS)

lx = (W - lw) // 2
ly = label_top + ((label_bot - label_top) - lh) // 2
canvas.paste(logo, (lx, ly), logo)

# ── drop shadow under bottle ───────────────────────────────────────────────────
shd = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd  = ImageDraw.Draw(shd)
sd.ellipse([body_l + 20, body_bot - 10, body_r - 20, body_bot + 55],
           fill=(0, 0, 0, 55))
shd = shd.filter(ImageFilter.GaussianBlur(22))
canvas = Image.alpha_composite(canvas, shd)

# ── save ───────────────────────────────────────────────────────────────────────
canvas.convert("RGB").save(OUT_PATH, "PNG", quality=95)
print(f"Saved: {OUT_PATH}")
