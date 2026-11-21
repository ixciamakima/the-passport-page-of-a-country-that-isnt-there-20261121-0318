#!/usr/bin/env python3
"""Render entry.png for the-passport-page-of-a-countr-2-20261121-0318.

Invented passport spread: Republic of Valdoria (mountain republic).
Data page (left) + visa/stamp page (right), canvas exactly 1024x1024.
Run in-session only; the graded entry program (main.py) is a stdlib byte copy.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

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
MONO_B = lambda s: font(f"{FD}/DejaVuSansMono-Bold.ttf", s)
STAMP_F = lambda s: font(f"{FL}/LiberationSerif-Bold.ttf", s)
STAMP = lambda s: font(f"{FL}/LiberationSerif-Regular.ttf", s)

# Palette
GREEN = (29, 58, 42)        # passport green
GREEN_L = (47, 84, 62)
GOLD = (176, 141, 58)
GOLD_L = (201, 168, 92)
PAPER = (247, 243, 232)
PAPER_D = (238, 231, 214)
INK = (32, 32, 34)
INK_SOFT = (74, 74, 78)
RULE = (120, 110, 88)
BLUE_INK = (28, 62, 128)
RED_INK = (158, 32, 32)
PURPLE_INK = (96, 48, 120)
TEAL_INK = (18, 96, 88)

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


# ---------------------------------------------------------------- helpers
def text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def center(draw, cx, y, s, f, fill=INK):
    draw.text((cx, y), s, font=f, fill=fill, anchor="ma")


def coat_of_arms(draw, cx, cy, scale=1.0):
    """Three peaks + star, gold on green."""
    w = 46 * scale
    h = 34 * scale
    pts = [(cx - w, cy + h * 0.55), (cx - w * 0.45, cy - h * 0.55),
           (cx - w * 0.1, cy + h * 0.15), (cx + w * 0.2, cy - h * 0.8),
           (cx + w * 0.55, cy + h * 0.15), (cx + w, cy + h * 0.55)]
    draw.line(pts, fill=GOLD_L, width=max(2, int(3 * scale)), joint="curve")
    draw.line([(cx - w, cy + h * 0.55), (cx + w, cy + h * 0.55)],
              fill=GOLD_L, width=max(2, int(3 * scale)))
    # star above middle peak
    sx, sy, r = cx + w * 0.2, cy - h * 1.05, 7 * scale
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=GOLD_L)


def guilloche(draw, box, color, step=9):
    """Faint wavy security lines inside box."""
    x0, y0, x1, y1 = box
    for yy in range(y0, y1, step):
        pts = []
        for xx in range(x0, x1 + 1, 12):
            pts.append((xx, yy + 2.5 * math.sin(xx / 46.0 + yy / 30.0)))
        draw.line(pts, fill=color, width=1)


def portrait(draw, box):
    """Flat-vector portrait: woman, dark hair, teal jacket, mountain backdrop."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # sky gradient
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((196, 214, 226), (232, 236, 238)))
        draw.line([(x0, y0 + yy), (x1, y0 + yy)], fill=c)
    # distant mountains
    draw.polygon([(x0, y1 - 52), (x0 + w * 0.30, y1 - 118),
                  (x0 + w * 0.52, y1 - 62), (x0 + w * 0.78, y1 - 126),
                  (x1, y1 - 58), (x1, y1), (x0, y1)],
                 fill=(168, 186, 196))
    draw.polygon([(x0, y1 - 30), (x0 + w * 0.35, y1 - 78),
                  (x0 + w * 0.62, y1 - 34), (x1, y1 - 66),
                  (x1, y1), (x0, y1)], fill=(148, 168, 180))
    cx = x0 + w // 2
    # shoulders / jacket
    draw.polygon([(cx - 78, y1), (cx - 66, y1 - 58), (cx - 30, y1 - 78),
                  (cx + 30, y1 - 78), (cx + 66, y1 - 58), (cx + 78, y1)],
                 fill=(36, 74, 84))
    # shirt V
    draw.polygon([(cx - 16, y1 - 76), (cx + 16, y1 - 76), (cx, y1 - 44)],
                 fill=(240, 238, 230))
    # jacket lapels
    draw.polygon([(cx - 30, y1 - 78), (cx - 8, y1 - 70), (cx - 4, y1 - 44),
                  (cx - 18, y1 - 52)], fill=(24, 56, 64))
    draw.polygon([(cx + 30, y1 - 78), (cx + 8, y1 - 70), (cx + 4, y1 - 44),
                  (cx + 18, y1 - 52)], fill=(24, 56, 64))
    # neck
    draw.rectangle([cx - 13, y1 - 108, cx + 13, y1 - 74], fill=(214, 164, 124))
    # face
    draw.ellipse([cx - 34, y1 - 196, cx + 34, y1 - 106], fill=(232, 185, 138))
    # hair: cap + side sweep
    draw.pieslice([cx - 38, y1 - 202, cx + 38, y1 - 118], 180, 360,
                  fill=(58, 38, 26))
    draw.polygon([(cx - 38, y1 - 160), (cx - 30, y1 - 196), (cx - 6, y1 - 202),
                  (cx - 30, y1 - 168)], fill=(58, 38, 26))
    draw.polygon([(cx + 38, y1 - 160), (cx + 30, y1 - 196), (cx + 8, y1 - 202),
                  (cx + 30, y1 - 168)], fill=(58, 38, 26))
    # hair fall right side
    draw.polygon([(cx + 30, y1 - 190), (cx + 40, y1 - 150), (cx + 34, y1 - 112),
                  (cx + 24, y1 - 150)], fill=(58, 38, 26))
    # eyebrows + eyes
    draw.arc([cx - 24, y1 - 168, cx - 8, y1 - 156], 200, 340,
             fill=(58, 38, 26), width=2)
    draw.arc([cx + 8, y1 - 168, cx + 24, y1 - 156], 200, 340,
             fill=(58, 38, 26), width=2)
    draw.ellipse([cx - 19, y1 - 158, cx - 13, y1 - 152], fill=(40, 28, 20))
    draw.ellipse([cx + 13, y1 - 158, cx + 19, y1 - 152], fill=(40, 28, 20))
    # nose + lips
    draw.line([(cx, y1 - 152), (cx - 2, y1 - 136), (cx + 3, y1 - 134)],
              fill=(198, 148, 108), width=2)
    draw.arc([cx - 9, y1 - 130, cx + 9, y1 - 120], 10, 170,
             fill=(168, 92, 84), width=2)
    # laminate diagonal sheen (drawn in photo-box coordinates)
    draw.polygon([(x0 + w * 0.55, y0), (x0 + w * 0.75, y0),
                  (x0 + w * 0.2, y1), (x0, y1)],
                 fill=(255, 255, 255, 26))


def make_stamp(lines, color, size=(168, 196), rotate=0, oval=False,
               sub=None):
    """One border-control stamp on its own transparent layer."""
    w, h = size
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 20, 20
    if oval:
        d.ellipse([ox, oy, ox + w, oy + h], outline=color, width=3)
        d.ellipse([ox + 7, oy + 7, ox + w - 7, oy + h - 7], outline=color,
                  width=1)
    else:
        d.rounded_rectangle([ox, oy, ox + w, oy + h], radius=10,
                            outline=color, width=3)
        d.rounded_rectangle([ox + 6, oy + 6, ox + w - 6, oy + h - 6],
                            radius=7, outline=color, width=1)
    y = oy + 16
    for i, (s, f) in enumerate(lines):
        d.text((ox + w // 2, y), s, font=f, fill=color, anchor="ma")
        y += 24 if i == 0 else 21
    if sub:
        d.text((ox + w // 2, oy + h - 30), sub, font=STAMP(15), fill=color,
               anchor="ma")
    if rotate:
        layer = layer.rotate(rotate, resample=Image.BICUBIC, expand=False)
    return layer


# ---------------------------------------------------------------- build
def main():
    img = Image.new("RGB", (W, H), (18, 26, 22))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- two pages
    d.rounded_rectangle([14, 14, 506, 1010], radius=6, fill=PAPER)
    d.rounded_rectangle([518, 14, 1010, 1010], radius=6, fill=PAPER)
    # centre gutter shadow
    d.rectangle([506, 14, 518, 1010], fill=(60, 52, 40))
    d.line([512, 14, 512, 1010], fill=(30, 26, 20), width=2)

    # ================= LEFT PAGE: data page =================
    # header band
    d.rectangle([14, 14, 506, 118], fill=GREEN)
    d.rectangle([14, 118, 506, 122], fill=GOLD)
    coat_of_arms(d, 260, 52, scale=0.9)
    center(d, 260, 84, "REPUBLIC OF VALDORIA", SERIF_B(25), GOLD_L)
    center(d, 260, 132, "REPUBLIKA VALDORIJA  ·  PASSPORT / PUTOVNICA",
           SANS(14), INK_SOFT)

    # faint guilloche strip under header
    guilloche(d, (30, 160, 490, 178), (196, 186, 160))

    # ---- portrait (left) + fields (right)
    px0, py0, px1, py1 = 34, 188, 216, 428
    d.rectangle([px0 - 3, py0 - 3, px1 + 3, py1 + 3], outline=RULE, width=2)
    portrait(d, (px0, py0, px1, py1))
    center(d, 125, 436, "PHOTOGRAPH", SANS(13), INK_SOFT)

    # field block right of portrait
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
    # last row ends ~186+9*47=609; tighten: fields end at 609, ok

    # issue / expiry row, authority on its own line below
    y = 636
    d.line([34, y - 12, 486, y - 12], fill=RULE, width=1)
    text(d, (34, y), "DATE OF ISSUE / IZDANO", SANS(12), INK_SOFT)
    text(d, (34, y + 14), "14 FEB 2024", SANS_B(16))
    text(d, (250, y), "DATE OF EXPIRY / VRIJEDI DO", SANS(12), INK_SOFT)
    text(d, (250, y + 14), "13 FEB 2034", SANS_B(16))
    text(d, (34, y + 50), "AUTHORITY / TIJELO", SANS(12), INK_SOFT)
    text(d, (34, y + 64), "MINISTRY OF THE INTERIOR — ZLATEN", SANS_B(16))

    # signature
    y = 752
    d.line([34, y, 250, y], fill=INK, width=1)
    text(d, (34, y + 6), "HOLDER'S SIGNATURE / POTPIS", SANS(12), INK_SOFT)
    d.text((40, y - 26), "Mara Ilsen", font=font(f"{FD}/DejaVuSerif.ttf", 22),
           fill=(52, 52, 90))

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

    # ---- MRZ
    line1, line2 = build_mrz()
    d.rectangle([14, 906, 506, 1010], fill=(232, 228, 216))
    d.text((34, 922), line1, font=MONO(17), fill=INK)
    d.text((34, 950), line2, font=MONO(17), fill=INK)
    text(d, (34, 982), "P<VALILSEN<<MARA<ELENA  ·  VD482916  ·  VALDORIA",
         SANS(12), INK_SOFT)

    # ================= RIGHT PAGE: visa / stamps =================
    center(d, 764, 34, "VISAS", SERIF_B(26), GREEN)
    center(d, 764, 66, "VIZE  ·  PAGE 7 / STRANICA 7", SANS(14), INK_SOFT)
    d.line([548, 96, 980, 96], fill=RULE, width=1)
    # faint watermark mountains
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.polygon([(560, 940), (660, 700), (740, 880), (830, 640), (930, 900),
                (980, 980), (560, 980)], outline=(120, 130, 110, 60), width=3)
    img.paste(Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)), wm), (0, 0), wm)
    d = ImageDraw.Draw(img, "RGBA")

    # stamps: (country, kind, date, place, color, rotate, oval)
    stamps = [
        ("VALDORIA", "DEPARTURE", "03 MAR 2024", "ZLATEN AIRPORT", GREEN, -4, False),
        ("DRAVNIA", "ARRIVAL", "03 MAR 2024", "BREZNO", BLUE_INK, 5, False),
        ("DRAVNIA", "DEPARTURE", "10 MAR 2024", "BREZNO", BLUE_INK, -6, False),
        ("VALDORIA", "ARRIVAL", "10 MAR 2024", "ZLATEN AIRPORT", GREEN, 3, False),
        ("VALDORIA", "DEPARTURE", "22 JUN 2024", "ZLATEN AIRPORT", GREEN, -3, False),
        ("KESSAR", "ARRIVAL", "22 JUN 2024", "PORT KESSAR", PURPLE_INK, 6, True),
        ("KESSAR", "DEPARTURE", "05 JUL 2024", "PORT KESSAR", PURPLE_INK, -5, True),
        ("VALDORIA", "ARRIVAL", "05 JUL 2024", "ZLATEN AIRPORT", GREEN, 4, False),
        ("VALDORIA", "DEPARTURE", "18 OCT 2025", "ZLATEN AIRPORT", GREEN, -5, False),
        ("TARNOVIA", "ARRIVAL", "18 OCT 2025", "VESK", TEAL_INK, 4, False),
        ("TARNOVIA", "DEPARTURE", "02 NOV 2025", "VESK", TEAL_INK, -4, False),
        ("VALDORIA", "ARRIVAL", "02 NOV 2025", "ZLATEN AIRPORT", GREEN, 5, False),
    ]
    xs = [540, 700, 860]
    ys = [112, 300, 488, 676]
    for i, (country, kind, date, place, color, rot, oval) in enumerate(stamps):
        cx, cy = xs[i % 3], ys[i // 3]
        lines = [(country, STAMP_F(17)), (kind, STAMP_F(16)),
                 (date, STAMP(16)), (place, STAMP(15))]
        stamp = make_stamp(lines, color, size=(140, 160), rotate=rot,
                           oval=oval)
        img.paste(stamp, (cx - 20, cy - 20), stamp)

    # Kessar visa-condition stamp (the paperwork detail, bottom centre)
    cond = make_stamp(
        [("KESSAR", STAMP_F(16)), ("ENTRY 90 DAYS", STAMP_F(15)),
         ("NO EMPLOYMENT", STAMP(15)), ("FEE PAID 40 VLD", STAMP(15))],
        RED_INK, size=(200, 140), rotate=-2, oval=False)
    img.paste(cond, (770, 856), cond)

    # small caption bottom-left of right page
    text(d, (548, 890), "STAMPS IN ORDER OF TRAVEL", SANS(13), INK_SOFT)
    text(d, (548, 910), "ALL DATES AFTER 14 FEB 2024", SANS(13), INK_SOFT)

    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
