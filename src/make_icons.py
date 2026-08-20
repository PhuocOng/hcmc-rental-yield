"""Sinh favicon va anh chia se cho website.

Bieu tuong = chinh luan diem cua du an thu gon lai: HAI THANH, mot ngan mot dai.
Thanh dat nung ngan = ti suat cho thue, thanh xanh muc dai = lai tiet kiem. O co
16px van doc duoc "mot cai ngan hon han cai kia", va no khong giong bat ky bieu
tuong ngoi nha / bieu do cot chung chung nao.

Xuat ra docs/: favicon.svg · favicon.ico · icon-192.png · apple-touch-icon.png · og.png

Chay: python src/make_icons.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "docs"      # GitHub Pages chi phuc vu tu / hoac /docs
WEB.mkdir(parents=True, exist_ok=True)

BG = (26, 23, 20)          # #1A1714 den am
RUST = (204, 98, 66)       # #CC6242 dat nung
TEAL = (78, 156, 147)      # #4E9C93 xanh muc
INK = (235, 231, 225)
INK2 = (162, 154, 144)

FONTS = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    return ImageFont.truetype(str(FONTS / name), size)


# ------------------------------------------------------------------ favicon SVG
# Ty le that la 1,51/6,00 = 0,25. O co 16px thanh ngan se chi con ~2px va bien mat,
# nen keo len 0,36 — van doc ro la "ngan hon han" ma khong bi mat hut.
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="6" fill="#1A1714"/>
<rect x="5" y="8"  width="8"  height="6" rx="1.5" fill="#CC6242"/>
<rect x="5" y="19" width="22" height="6" rx="1.5" fill="#4E9C93"/>
</svg>'''
(WEB / "favicon.svg").write_text(SVG, encoding="utf-8")


def draw_mark(size: int, radius_ratio: float = 0.1875) -> Image.Image:
    """Ve bieu tuong o kich thuoc bat ky. Ve lon roi thu nho cho canh muot."""
    S = size * 8
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = S / 32
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius_ratio * S, fill=BG)
    d.rounded_rectangle([5 * u, 8 * u, 13 * u, 14 * u], radius=1.5 * u, fill=RUST)
    d.rounded_rectangle([5 * u, 19 * u, 27 * u, 25 * u], radius=1.5 * u, fill=TEAL)
    return img.resize((size, size), Image.LANCZOS)


# ICO nhieu kich thuoc — Windows va trinh duyet cu chon size phu hop
ico_sizes = [16, 24, 32, 48, 64]
draw_mark(64).save(WEB / "favicon.ico", format="ICO",
                   sizes=[(s, s) for s in ico_sizes])
draw_mark(192).save(WEB / "icon-192.png")
# apple-touch-icon khong duoc bo goc trong suot — iOS tu bo goc
apple = Image.new("RGB", (180, 180), BG)
apple.paste(draw_mark(180, radius_ratio=0), (0, 0), draw_mark(180, radius_ratio=0))
apple.save(WEB / "apple-touch-icon.png")

# ------------------------------------------------------------------ anh chia se
W, H = 1200, 630
og = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(og)

f_ttl = font("segoeuib.ttf", 60)
f_num = font("consolab.ttf", 76)
f_unit = font("segoeui.ttf", 26)
f_lab = font("segoeui.ttf", 27)
f_meta = font("segoeui.ttf", 22)
f_kick = font("segoeuib.ttf", 20)

M = 78
d.text((M, 62), "HCMC RENTAL YIELD", font=f_kick, fill=(140, 132, 122))
d.text((M, 100), "Buying to let earns less", font=f_ttl, fill=INK)
d.text((M, 168), "than leaving the money in a bank", font=f_ttl, fill=INK)

# hai thanh so sanh — dung ty le THAT
BAR_X, BAR_W, BAR_H = M + 268, 620, 40
rows = [(1.51, RUST, "letting, after all costs", 300),
        (6.00, TEAL, "12-month bank deposit", 382)]
mx = max(r[0] for r in rows)
for val, col, lab, y in rows:
    txt = f"{val:.2f}"
    tw = d.textlength(txt, font=f_num)
    d.text((BAR_X - 22 - tw - 46, y - 8), txt, font=f_num, fill=col)
    d.text((BAR_X - 22 - 42, y + 30), "%/yr", font=f_unit, fill=INK2)
    d.rounded_rectangle([BAR_X, y, BAR_X + BAR_W, y + BAR_H], radius=5,
                        fill=(42, 38, 34))
    d.rounded_rectangle([BAR_X, y, BAR_X + BAR_W * val / mx, y + BAR_H], radius=5,
                        fill=col)
    d.text((BAR_X + 14, y + BAR_H + 8), lab, font=f_meta, fill=INK2)

d.line([M, 500, W - M, 500], fill=(52, 47, 42), width=1)
d.text((M, 522), "A deposit pays 4.0× more — a gap of 4.49 pp every year.",
       font=f_lab, fill=INK)
d.text((M, 562), "45,084 listings · 20 districts · Chợ Tốt, 15 Aug 2026",
       font=f_meta, fill=INK2)

# vach mau ben trai cho co dau nhan
d.rectangle([0, 0, 7, H], fill=RUST)
og.save(WEB / "og.png", optimize=True)

for f in ("favicon.svg", "favicon.ico", "icon-192.png", "apple-touch-icon.png", "og.png"):
    print(f"  {f:<22} {(WEB / f).stat().st_size / 1024:6.1f} KB")
