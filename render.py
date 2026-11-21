#!/usr/bin/env python3
"""Render entry.png v2 for the-passport-page-of-a-countr-2-20261121-0318.

Same document as v1 (Republic of Valdoria, Mara Elena Ilsen, same dates and
stamp history) but rendered to read as a scan/photo of a physical passport:
textured paper, guilloche fields, microprint strips, a shaded portrait with
soft edges, ink-eroded stamps with uneven opacity, a foil hologram, a centre
fold shadow and a scan-lighting gradient with fine grain over everything.

Run in-session only; the graded entry program (main.py) is a stdlib byte copy.
"""
import math
import os
import random

from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont)

random.seed(20261121)

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: font(f"{FD}/DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font(f"{FD}/DejaVuSerif.ttf", s)
SANS = lambda s: font(f"{FD}/DejaVuSans.ttf", s)
SANS_B = lambda s: font(f"{FD}/DejaVuSans-Bold.ttf", s)
MONO = lambda s: font(f"{FD}/DejaVuSansMono.ttf", s)
STAMP_F = lambda s: font(f"{FL}/LiberationSerif-Bold.ttf", s)
STAMP = lambda s: font(f"{FL}/LiberationSerif-Regular.ttf", s)
SIG_F = lambda s: font(f"{FL}/LiberationSerif-Italic.ttf", s)

# Palette
GREEN = (29, 58, 42)        # passport green
GOLD = (176, 141, 58)
GOLD_L = (201, 168, 92)
PAPER = (246, 240, 228)
INK = (34, 34, 36)
INK_SOFT = (84, 80, 72)
RULE = (128, 118, 94)
BLUE_INK = (30, 62, 128)
RED_INK = (156, 34, 32)
PURPLE_INK = (98, 50, 118)
TEAL_INK = (18, 94, 86)
STAMP_INKS = {"GREEN": (34, 84, 54), "BLUE": BLUE_INK, "PURPLE": PURPLE_INK,
              "TEAL": TEAL_INK, "RED": RED_INK}

# ---------------------------------------------------------------- MRZ
WEIGHTS = [7, 3, 1]


def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55
        total += v * WEIGHTS[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<VALILSEN<<MARA<ELENA"
    line1 = line1 + "<" * (44 - len(line1))
    doc9 = "VD482916<"  # document number field is 9 chars, '<'-padded
    dob = "880312"
    exp = "340213"
    personal = "<" * 14
    body = (doc9 + mrz_check(doc9) + "VAL" + dob + mrz_check(dob) + "F"
            + exp + mrz_check(exp) + personal + mrz_check(personal))
    line2 = body + mrz_check(body)  # composite check digit
    assert len(line1) == 44, len(line1)
    assert len(line2) == 44, len(line2)
    return line1, line2


# ---------------------------------------------------------------- texture
def noise_layer(w, h, lo, hi):
    """Greyscale noise image with values in [lo, hi]."""
    raw = os.urandom(w * h)
    lut = [lo + (b * (hi - lo)) // 255 for b in range(256)]
    return Image.frombytes("L", (w, h), raw).point(lut)


def paper_texture(img, box):
    """Multiply a soft blurred noise into the paper so it is not flat."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    n = noise_layer(w // 2, h // 2, 238, 255)
    n = n.filter(ImageFilter.GaussianBlur(1.2)).resize((w, h), Image.BICUBIC)
    n = n.convert("RGB")
    region = img.crop(box)
    img.paste(ImageChops.multiply(region, n), (x0, y0))
    # sparse fibres / specks
    sp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    for _ in range(260):
        x, y = random.uniform(0, w), random.uniform(0, h)
        ln = random.uniform(2, 7)
        tone = random.choice([(120, 105, 80), (255, 255, 250)])
        sd.line([(x, y), (x + ln, y + random.uniform(-1, 1))],
                fill=tone + (26,), width=1)
    img.paste(Image.alpha_composite(region.convert("RGBA"), sp).convert("RGB"),
              (x0, y0))


def guilloche_field(img, box, tint_a, tint_b, alpha=30):
    """Two families of fine sine waves clipped to box, on an overlay."""
    x0, y0, x1, y1 = box
    ov = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w, h = x1 - x0, y1 - y0
    for yy in range(-10, h + 10, 9):
        pts = [(xx, yy + 3.2 * math.sin(xx / 52.0 + yy / 26.0))
               for xx in range(0, w + 1, 8)]
        d.line(pts, fill=tint_a + (alpha,), width=1)
    for yy in range(-10, h + 10, 14):
        pts = [(xx, yy + 5.0 * math.sin(xx / 88.0 - yy / 40.0 + 1.7))
               for xx in range(0, w + 1, 8)]
        d.line(pts, fill=tint_b + (alpha - 8,), width=1)
    # one rosette: wavy concentric circles
    cx, cy = w * 0.78, h * 0.30
    for r in range(16, 120, 13):
        pts = []
        for a in range(0, 361, 6):
            rr = r + 4.5 * math.sin(math.radians(a) * 5 + r)
            pts.append((cx + rr * math.cos(math.radians(a)),
                        cy + rr * math.sin(math.radians(a))))
        d.line(pts, fill=tint_a + (alpha + 6,), width=1)
    base = img.crop(box).convert("RGBA")
    img.paste(Image.alpha_composite(base, ov).convert("RGB"), (x0, y0))


def microprint(img, x, y, width, fill):
    """A repeated tiny-print line, clipped to the page width it sits on."""
    unit = "REPUBLIKA VALDORIJA · VALDORIA · "
    layer = Image.new("RGBA", (width, 18), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f = SANS(13)
    uw = ld.textlength(unit, font=f)
    s = unit * (int(width // uw) + 1)
    ld.text((0, 1), s, font=f, fill=fill + (255,))
    base = img.crop((x, y, x + width, y + 18)).convert("RGBA")
    img.paste(Image.alpha_composite(base, layer).convert("RGB"), (x, y))


# ---------------------------------------------------------------- helpers
def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def center(draw, cx, y, s, f, fill=INK):
    draw.text((cx, y), s, font=f, fill=fill, anchor="ma")


def coat_of_arms(draw, cx, cy, scale=1.0, alpha=255):
    """Three peaks + star, gold."""
    col = GOLD_L + (alpha,) if alpha < 255 else GOLD_L
    w = 46 * scale
    h = 34 * scale
    pts = [(cx - w, cy + h * 0.55), (cx - w * 0.45, cy - h * 0.55),
           (cx - w * 0.1, cy + h * 0.15), (cx + w * 0.2, cy - h * 0.8),
           (cx + w * 0.55, cy + h * 0.15), (cx + w, cy + h * 0.55)]
    draw.line(pts, fill=col, width=max(2, int(3 * scale)), joint="curve")
    draw.line([(cx - w, cy + h * 0.55), (cx + w, cy + h * 0.55)],
              fill=col, width=max(2, int(3 * scale)))
    sx, sy, r = cx + w * 0.2, cy - h * 1.05, 7 * scale
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=col)


# ---------------------------------------------------------------- portrait
def portrait(box):
    """Shaded portrait rendered at 2x and downscaled: soft, photo-like.

    Woman with dark hair and a teal jacket against a studio backdrop; the
    shading is built from blurred shadow/highlight layers, not flat fills.
    """
    x0, y0, x1, y1 = box
    w, h = (x1 - x0) * 2, (y1 - y0) * 2
    img = Image.new("RGB", (w, h), (206, 216, 222))
    d = ImageDraw.Draw(img, "RGBA")

    # studio backdrop: vertical gradient, lighter behind the head
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(a + (b - a) * t)
                  for a, b in zip((214, 224, 230), (188, 198, 206)))
        d.line([(0, yy), (w, yy)], fill=c)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.16, h * 0.02, w * 0.84, h * 0.62],
               fill=(255, 255, 255, 46))
    img = Image.alpha_composite(img.convert("RGBA"),
                                glow.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(img, "RGBA")

    cx = w // 2
    skin = (228, 178, 132)
    skin_sh = (204, 152, 106)
    skin_dp = (176, 122, 82)
    skin_hi = (248, 212, 172)
    hair_c = (56, 36, 24)
    jacket = (33, 70, 80)
    jacket_sh = (22, 50, 58)

    # shoulders / jacket with a soft vertical gradient
    for yy in range(int(h * 0.78), h):
        t = (yy - h * 0.78) / (h * 0.22)
        c = tuple(int(a + (b - a) * t) for a, b in zip(jacket, jacket_sh))
        d.line([(0, yy), (w, yy)], fill=c)
    d.polygon([(cx - w * 0.46, h), (cx - w * 0.40, h * 0.80),
               (cx - w * 0.17, h * 0.735), (cx + w * 0.17, h * 0.735),
               (cx + w * 0.40, h * 0.80), (cx + w * 0.46, h)], fill=jacket)
    # shirt V + its shadow
    d.polygon([(cx - w * 0.085, h * 0.745), (cx + w * 0.085, h * 0.745),
               (cx, h * 0.90)], fill=(238, 235, 226))
    d.polygon([(cx - w * 0.085, h * 0.745), (cx, h * 0.90),
               (cx - w * 0.028, h * 0.745)], fill=(214, 210, 198))
    # lapels
    d.polygon([(cx - w * 0.17, h * 0.735), (cx - w * 0.045, h * 0.775),
               (cx - w * 0.02, h * 0.90), (cx - w * 0.10, h * 0.80)],
              fill=jacket_sh)
    d.polygon([(cx + w * 0.17, h * 0.735), (cx + w * 0.045, h * 0.775),
               (cx + w * 0.02, h * 0.90), (cx + w * 0.10, h * 0.80)],
              fill=jacket_sh)
    # neck + shadow cast by the chin
    d.rectangle([cx - w * 0.075, h * 0.60, cx + w * 0.075, h * 0.755],
                fill=(216, 166, 124))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [cx - w * 0.075, h * 0.585, cx + w * 0.075, h * 0.665],
        fill=skin_dp + (120,))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img, "RGBA")

    # ears + face base
    d.ellipse([cx - w * 0.205, h * 0.335, cx - w * 0.155, h * 0.435],
              fill=skin_sh)
    d.ellipse([cx + w * 0.155, h * 0.335, cx + w * 0.205, h * 0.435],
              fill=skin_sh)
    face = [cx - w * 0.185, h * 0.085, cx + w * 0.185, h * 0.635]
    d.ellipse(face, fill=skin)
    # face shading: blurred shadow at the sides, highlight down the centre
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([cx - w * 0.20, h * 0.10, cx - w * 0.06, h * 0.60],
               fill=skin_sh + (105,))
    sd.ellipse([cx + w * 0.06, h * 0.10, cx + w * 0.20, h * 0.60],
               fill=skin_sh + (105,))
    sd.ellipse([cx - w * 0.10, h * 0.47, cx + w * 0.10, h * 0.66],
               fill=skin_sh + (70,))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(13)))
    hi = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    hd.ellipse([cx - w * 0.075, h * 0.13, cx + w * 0.075, h * 0.42],
               fill=skin_hi + (80,))
    hd.ellipse([cx - w * 0.028, h * 0.36, cx + w * 0.028, h * 0.52],
               fill=skin_hi + (65,))
    img = Image.alpha_composite(img, hi.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img, "RGBA")

    # hair: mass, then strands in varied browns
    d.pieslice([cx - w * 0.215, h * 0.045, cx + w * 0.215, h * 0.46],
               180, 360, fill=hair_c)
    d.polygon([(cx - w * 0.215, h * 0.26), (cx - w * 0.19, h * 0.52),
               (cx - w * 0.135, h * 0.30), (cx - w * 0.155, h * 0.13)],
              fill=hair_c)
    d.polygon([(cx + w * 0.215, h * 0.26), (cx + w * 0.185, h * 0.56),
               (cx + w * 0.13, h * 0.32), (cx + w * 0.155, h * 0.13)],
              fill=hair_c)
    for _ in range(70):
        side = random.choice([-1, 1])
        sx = cx + side * random.uniform(w * 0.10, w * 0.205)
        sy = h * random.uniform(0.05, 0.13)
        ln = random.uniform(h * 0.08, h * 0.20)
        tone = random.choice([(74, 50, 32), (44, 28, 18), (96, 66, 40),
                              (64, 42, 26)])
        d.line([(sx, sy), (sx + side * random.uniform(2, 9), sy + ln)],
               fill=tone + (110,), width=2)
    # hairline sweep
    d.arc([cx - w * 0.20, h * 0.05, cx + w * 0.20, h * 0.34], 185, 330,
          fill=(44, 28, 18), width=5)

    # eyebrows (soft) + eyes
    brow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(brow)
    bd.arc([cx - w * 0.145, h * 0.295, cx - w * 0.045, h * 0.345], 195, 345,
           fill=(52, 34, 22, 220), width=6)
    bd.arc([cx + w * 0.045, h * 0.295, cx + w * 0.145, h * 0.345], 195, 345,
           fill=(52, 34, 22, 220), width=6)
    img = Image.alpha_composite(img, brow.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(img, "RGBA")
    for sgn in (-1, 1):
        ex = cx + sgn * w * 0.092
        ey = h * 0.375
        d.ellipse([ex - w * 0.036, ey - h * 0.016, ex + w * 0.036,
                   ey + h * 0.016], fill=(243, 240, 234))
        d.ellipse([ex - w * 0.017, ey - h * 0.015, ex + w * 0.017,
                   ey + h * 0.015], fill=(84, 56, 34))
        d.ellipse([ex - w * 0.008, ey - h * 0.008, ex + w * 0.008,
                   ey + h * 0.008], fill=(20, 14, 10))
        d.ellipse([ex - w * 0.004, ey - h * 0.011, ex + w * 0.003,
                   ey - h * 0.004], fill=(255, 255, 255))
        d.arc([ex - w * 0.038, ey - h * 0.024, ex + w * 0.038,
               ey + h * 0.010], 180, 360, fill=(60, 40, 26), width=3)
    # nose: soft shadow strokes
    nose = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nose)
    nd.line([(cx + w * 0.012, h * 0.40), (cx + w * 0.026, h * 0.475),
             (cx + w * 0.006, h * 0.49)], fill=skin_dp + (130,), width=4)
    nd.ellipse([cx - w * 0.032, h * 0.478, cx - w * 0.008, h * 0.50],
               fill=skin_dp + (110,))
    nd.ellipse([cx + w * 0.008, h * 0.478, cx + w * 0.032, h * 0.50],
               fill=skin_dp + (110,))
    img = Image.alpha_composite(img, nose.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(img, "RGBA")
    # lips
    d.ellipse([cx - w * 0.052, h * 0.532, cx + w * 0.052, h * 0.572],
              fill=(178, 104, 94))
    d.ellipse([cx - w * 0.046, h * 0.548, cx + w * 0.046, h * 0.578],
              fill=(192, 118, 106))
    d.line([(cx - w * 0.048, h * 0.556), (cx + w * 0.048, h * 0.556)],
           fill=(140, 74, 66), width=3)
    d.line([(cx - w * 0.026, h * 0.570), (cx + w * 0.010, h * 0.570)],
           fill=(226, 160, 148), width=3)

    # soften the whole portrait, then downscale into place
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    return img.resize((x1 - x0, y1 - y0), Image.LANCZOS).convert("RGBA")


# ---------------------------------------------------------------- stamps
def erode_ink(layer, opacity):
    """Make a stamp look physically stamped: noisy alpha, soft edge."""
    a = layer.split()[3]
    nw, nh = max(2, layer.width // 2), max(2, layer.height // 2)
    n = noise_layer(nw, nh, 0, 255).resize(layer.size, Image.BICUBIC)
    # most of the ink stays; random specks drop out, edges fray
    lut = []
    for v in range(256):
        if v < 46:
            lut.append(70)
        elif v < 110:
            lut.append(165)
        else:
            lut.append(215 + (v - 110) * 40 // 145)
    mask = n.point(lut)
    a = ImageChops.multiply(a, mask)
    a = a.filter(ImageFilter.GaussianBlur(0.7))
    if opacity < 1.0:
        a = a.point(lambda v: int(v * opacity))
    layer.putalpha(a)
    return layer


def make_stamp(lines, color, size=(140, 160), rotate=0, oval=False,
               opacity=0.9):
    """Border-control stamp: drawn at 2x, ink-eroded, downscaled."""
    w, h = size
    S = 2
    lw, lh = (w + 40) * S, (h + 40) * S
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 20 * S, 20 * S
    ink = color + (255,)
    if oval:
        d.ellipse([ox, oy, ox + w * S, oy + h * S], outline=ink, width=3 * S)
        d.ellipse([ox + 7 * S, oy + 7 * S, ox + (w - 7) * S,
                   oy + (h - 7) * S], outline=ink, width=S)
    else:
        d.rounded_rectangle([ox, oy, ox + w * S, oy + h * S], radius=10 * S,
                            outline=ink, width=3 * S)
        d.rounded_rectangle([ox + 6 * S, oy + 6 * S, ox + (w - 6) * S,
                             oy + (h - 6) * S], radius=7 * S, outline=ink,
                            width=S)
    y = oy + 15 * S
    for i, (s, f) in enumerate(lines):
        # fonts arrive pre-scaled 2x from stamp_lines()
        d.text((ox + w * S // 2, y), s, font=f, fill=ink, anchor="ma")
        y += (25 if i == 0 else 22) * S
    layer = erode_ink(layer, opacity)
    if rotate:
        layer = layer.rotate(rotate, resample=Image.BICUBIC, expand=False)
    return layer.resize((w + 40, h + 40), Image.LANCZOS)


def stamp_lines(country, kind, date, place):
    return [(country, STAMP_F(34)), (kind, STAMP_F(32)),
            (date, STAMP(32)), (place, STAMP(30))]


# ---------------------------------------------------------------- hologram
def hologram(size=118):
    """Foil seal: pastel concentric rings + star, translucent."""
    S = 2
    layer = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = size * S // 2
    pastel = [(255, 170, 205), (170, 235, 215), (180, 195, 255),
              (255, 238, 170), (215, 180, 255)]
    for i, r in enumerate(range(size * S // 2 - 4, 8, -11)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=pastel[i % len(pastel)] + (88,), width=5)
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = (size * S // 4) if i % 2 == 0 else (size * S // 9)
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(star, outline=(255, 244, 200, 130), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    return layer.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- build
def main():
    # dark surface the open passport lies on, with its own grain + vignette
    img = Image.new("RGB", (W, H), (26, 30, 27))
    surf = noise_layer(W // 2, H // 2, 230, 255)
    surf = surf.filter(ImageFilter.GaussianBlur(1.2)).resize((W, H),
                                                             Image.BICUBIC)
    img = ImageChops.multiply(img, surf.convert("RGB"))
    d = ImageDraw.Draw(img, "RGBA")

    # page shadows first (soft, offset) so the book sits on the surface
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(shadow)
    sdd.rounded_rectangle([24, 26, 1014, 1018], radius=8, fill=(0, 0, 0, 150))
    img.paste(Image.alpha_composite(img.convert("RGBA"),
                                    shadow.filter(ImageFilter.GaussianBlur(9)))
              .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- the two pages
    for box in ([16, 16, 504, 1008], [520, 16, 1008, 1008]):
        d.rounded_rectangle(box, radius=6, fill=PAPER)
    for box in ([16, 16, 504, 1008], [520, 16, 1008, 1008]):
        paper_texture(img, tuple(box))
    d = ImageDraw.Draw(img, "RGBA")

    # security print on both pages
    guilloche_field(img, (24, 130, 496, 896), (150, 168, 138), (196, 178, 128),
                    alpha=26)
    guilloche_field(img, (528, 108, 1000, 1000), (150, 168, 138),
                    (196, 178, 128), alpha=22)
    d = ImageDraw.Draw(img, "RGBA")

    # large faint coat-of-arms watermark behind the data fields
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    coat_of_arms(ImageDraw.Draw(wm), 356, 520, scale=3.4, alpha=22)
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ================= LEFT PAGE: data page =================
    d.rectangle([16, 16, 504, 116], fill=GREEN)
    d.rectangle([16, 116, 504, 120], fill=GOLD)
    # guilloche shimmer over the header band
    ov = Image.new("RGBA", (488, 100), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for yy in range(2, 100, 6):
        pts = [(xx, yy + 2.4 * math.sin(xx / 40.0 + yy / 22.0))
               for xx in range(0, 489, 8)]
        od.line(pts, fill=(255, 246, 200, 26), width=1)
    hdr = img.crop((16, 16, 504, 116)).convert("RGBA")
    img.paste(Image.alpha_composite(hdr, ov).convert("RGB"), (16, 16))
    d = ImageDraw.Draw(img, "RGBA")
    coat_of_arms(d, 260, 50, scale=0.9)
    center(d, 260, 82, "REPUBLIC OF VALDORIA", SERIF_B(25), GOLD_L)
    center(d, 260, 130, "REPUBLIKA VALDORIJA  ·  PASSPORT / PUTOVNICA",
           SANS(14), INK_SOFT)
    microprint(img, 34, 158, 452, (168, 158, 128))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- portrait: frame shadow, photo, border, laminate sheen
    px0, py0, px1, py1 = 34, 190, 216, 430
    ph_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ph_shadow).rounded_rectangle(
        [px0 + 2, py0 + 4, px1 + 5, py1 + 6], radius=3, fill=(0, 0, 0, 110))
    img.paste(Image.alpha_composite(
        img.convert("RGBA"),
        ph_shadow.filter(ImageFilter.GaussianBlur(4))).convert("RGB"), (0, 0))
    photo = portrait((px0, py0, px1, py1))
    img.paste(photo, (px0, py0), photo)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([px0 - 2, py0 - 2, px1 + 2, py1 + 2], outline=(105, 96, 74),
                width=2)
    sheen = Image.new("RGBA", (px1 - px0, py1 - py0), (0, 0, 0, 0))
    ImageDraw.Draw(sheen).polygon(
        [(118, 0), (168, 0), (60, 240), (10, 240)], fill=(255, 255, 255, 20))
    img.paste(Image.alpha_composite(img.crop((px0, py0, px1, py1))
                                    .convert("RGBA"), sheen).convert("RGB"),
              (px0, py0))
    d = ImageDraw.Draw(img, "RGBA")
    center(d, 125, 438, "PHOTOGRAPH", SANS(13), INK_SOFT)

    # field block right of portrait (same data as v1)
    fx = 238
    fields = [
        ("TYPE / VRSTA", "P"),
        ("COUNTRY CODE / DRŽAVA", "VAL"),
        ("PASSPORT No. / BROJ", "VD 482 916"),
        ("SURNAME / PREZIME", "ILSEN"),
        ("GIVEN NAMES / IME", "MARA ELENA"),
        ("NATIONALITY / DRŽAVLJANSTVO", "VALDORIAN"),
        ("DATE OF BIRTH / ROĐENJE", "12 MAR 1988"),
        ("PLACE OF BIRTH / MJESTO", "ZLATEN"),
        ("SEX / SPOL", "F"),
    ]
    y = 186
    for label, value in fields:
        text(d, (fx, y), label, SANS(13), INK_SOFT)
        text(d, (fx, y + 15), value, SANS_B(19))
        y += 47

    y = 636
    d.line([34, y - 12, 486, y - 12], fill=RULE, width=1)
    text(d, (34, y), "DATE OF ISSUE / IZDANO", SANS(13), INK_SOFT)
    text(d, (34, y + 14), "14 FEB 2024", SANS_B(16))
    text(d, (250, y), "DATE OF EXPIRY / VRIJEDI DO", SANS(13), INK_SOFT)
    text(d, (250, y + 14), "13 FEB 2034", SANS_B(16))
    text(d, (34, y + 50), "AUTHORITY / TIJELO", SANS(13), INK_SOFT)
    text(d, (34, y + 64), "MINISTRY OF THE INTERIOR — ZLATEN", SANS_B(16))

    # signature: italic hand on a slightly rotated, softened layer
    sig = Image.new("RGBA", (240, 56), (0, 0, 0, 0))
    ImageDraw.Draw(sig).text((8, 6), "Mara Ilsen", font=SIG_F(30),
                             fill=(44, 46, 96, 235))
    sig = sig.rotate(2.5, resample=Image.BICUBIC, expand=False)
    sig = sig.filter(ImageFilter.GaussianBlur(0.4))
    img.paste(Image.alpha_composite(
        img.crop((30, 706, 270, 762)).convert("RGBA"), sig).convert("RGB"),
        (30, 706))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([34, 752, 250, 752], fill=INK, width=1)
    text(d, (34, 758), "HOLDER'S SIGNATURE / POTPIS", SANS(13), INK_SOFT)

    # ---- endorsement box: the telling paperwork detail
    y = 792
    d.rounded_rectangle([34, y, 486, y + 84], radius=4, outline=RED_INK,
                        width=2)
    d.rectangle([34, y, 486, y + 26], fill=RED_INK)
    center(d, 260, y + 4, "ENDORSEMENT / NAPOMENA", SANS_B(15), (255, 255, 255))
    text(d, (46, y + 34),
         "HIGH-ALTITUDE TRAVEL ABOVE 2,500 M ONLY WITH", SANS_B(15), RED_INK)
    text(d, (46, y + 54), "A REGISTERED MOUNTAIN GUIDE.  ·  VISAS: SEE P. 7",
         SANS_B(15), RED_INK)

    # security thread: thin metallic dashes down the data page
    for yy in range(140, 890, 26):
        d.line([(492, yy), (492, yy + 13)], fill=(150, 148, 138), width=2)

    # ---- MRZ
    line1, line2 = build_mrz()
    d.rectangle([16, 904, 504, 1008], fill=(233, 228, 214))
    microprint(img, 34, 884, 452, (172, 162, 132))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((32, 922), line1, font=MONO(16), fill=INK)
    d.text((32, 951), line2, font=MONO(16), fill=INK)
    text(d, (34, 982), "P<VALILSEN<<MARA<ELENA  ·  VD482916  ·  VALDORIA",
         SANS(13), INK_SOFT)

    # foil hologram overlapping the portrait's lower-right corner
    holo = hologram(118)
    img.paste(holo, (168, 372), holo)
    d = ImageDraw.Draw(img, "RGBA")

    # ================= RIGHT PAGE: visa / stamps =================
    center(d, 764, 34, "VISAS", SERIF_B(26), GREEN)
    center(d, 764, 66, "VIZE  ·  PAGE 7 / STRANICA 7", SANS(14), INK_SOFT)
    d.line([548, 96, 980, 96], fill=RULE, width=1)
    # faint watermark mountains
    wm2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm2)
    wd.polygon([(560, 940), (660, 700), (740, 880), (830, 640), (930, 900),
                (980, 980), (560, 980)], outline=(118, 128, 108, 66), width=3)
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm2).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # the same twelve stamps, same order and dates as v1
    G = STAMP_INKS["GREEN"]
    stamps = [
        ("VALDORIA", "DEPARTURE", "03 MAR 2024", "ZLATEN AIRPORT", G, -4, False, 0.93),
        ("DRAVNIA", "ARRIVAL", "03 MAR 2024", "BREZNO", BLUE_INK, 5, False, 0.88),
        ("DRAVNIA", "DEPARTURE", "10 MAR 2024", "BREZNO", BLUE_INK, -6, False, 0.95),
        ("VALDORIA", "ARRIVAL", "10 MAR 2024", "ZLATEN AIRPORT", G, 3, False, 0.85),
        ("VALDORIA", "DEPARTURE", "22 JUN 2024", "ZLATEN AIRPORT", G, -3, False, 0.92),
        ("KESSAR", "ARRIVAL", "22 JUN 2024", "PORT KESSAR", PURPLE_INK, 6, True, 0.90),
        ("KESSAR", "DEPARTURE", "05 JUL 2024", "PORT KESSAR", PURPLE_INK, -5, True, 0.86),
        ("VALDORIA", "ARRIVAL", "05 JUL 2024", "ZLATEN AIRPORT", G, 4, False, 0.94),
        ("VALDORIA", "DEPARTURE", "18 OCT 2025", "ZLATEN AIRPORT", G, -5, False, 0.89),
        ("TARNOVIA", "ARRIVAL", "18 OCT 2025", "VESK", TEAL_INK, 4, False, 0.93),
        ("TARNOVIA", "DEPARTURE", "02 NOV 2025", "VESK", TEAL_INK, -4, False, 0.87),
        ("VALDORIA", "ARRIVAL", "02 NOV 2025", "ZLATEN AIRPORT", G, 5, False, 0.91),
    ]
    xs = [540, 700, 860]
    ys = [116, 304, 492, 680]
    for i, (country, kind, date, place, color, rot, oval, op) in enumerate(stamps):
        cx, cy = xs[i % 3], ys[i // 3]
        jx = cx + random.randint(-3, 3)
        jy = cy + random.randint(-3, 3)
        stamp = make_stamp(stamp_lines(country, kind, date, place), color,
                           size=(140, 160), rotate=rot, oval=oval, opacity=op)
        img.paste(stamp, (jx - 20, jy - 20), stamp)

    # Kessar visa-condition stamp (the paperwork detail on the visa page)
    cond = make_stamp(
        [("KESSAR", STAMP_F(32)), ("ENTRY 90 DAYS", STAMP_F(30)),
         ("NO EMPLOYMENT", STAMP(30)), ("FEE PAID 40 VLD", STAMP(30))],
        RED_INK, size=(200, 140), rotate=-2, opacity=0.9)
    img.paste(cond, (596, 838), cond)
    d = ImageDraw.Draw(img, "RGBA")

    # ================= physical finish =================
    # centre fold: feathered shadow band + a highlight on the right leaf
    fold = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fold)
    for i in range(30):
        a = int(105 * math.sin(math.pi * i / 29) ** 1.5)
        fd.line([(497 + i, 10), (497 + i, 1014)], fill=(24, 20, 14, a),
                width=1)
    for i in range(10):
        a = int(26 * (1 - i / 10))
        fd.line([(528 + i, 10), (528 + i, 1014)], fill=(255, 252, 240, a),
                width=1)
    img = Image.alpha_composite(img.convert("RGBA"), fold).convert("RGB")

    # scan lighting: gentle radial falloff, brighter upper-left
    light = Image.new("L", (256, 256), 0)
    ld = ImageDraw.Draw(light)
    for r in range(255, 0, -4):
        v = int(196 + 59 * (1 - r / 255) ** 1.6)
        ld.ellipse([108 - r, 92 - r, 108 + r, 92 + r], fill=v)
    light = light.resize((W, H), Image.BICUBIC).convert("RGB")
    img = ImageChops.multiply(img, light)
    img = ImageEnhance.Color(img).enhance(0.985)

    # kill the vector crispness, then lay fine grain over everything
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    grain = noise_layer(W // 2, H // 2, 250, 255)
    grain = grain.filter(ImageFilter.GaussianBlur(0.8)).resize((W, H),
                                                              Image.BICUBIC)
    img = ImageChops.multiply(img, grain.convert("RGB"))

    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
