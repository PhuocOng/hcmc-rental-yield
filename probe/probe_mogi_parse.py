"""Kiem chung: co boc duoc day du truong tu mot trang danh sach mogi.vn khong?

Chay tren file da luu (data/output/mogi-ban.html, mogi-thue.html).
"""

import html as H
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent

# href dang: /<quan>/<mua|thue>-<loai-hinh>/<slug>-id<so>
# Tin TOP dung link tuong doi, danh sach chinh dung link tuyet doi -> nhan ca hai.
LINK = re.compile(
    r'href="(?:https://mogi\.vn)?(/([a-z0-9\-]+)/(mua|thue)-([a-z0-9\-]+)/[a-z0-9\-]*?-id(\d+))"'
)


def parse(html: str) -> list[dict]:
    out, seen = [], set()
    # cat trang thanh tung doan bat dau bang mot link tin
    parts = LINK.split(html)
    # split voi 5 nhom -> moi tin chiem 6 phan tu
    for i in range(1, len(parts), 6):
        href, district, deal, ptype, pid = parts[i:i + 5]
        tail = parts[i + 5] if i + 5 < len(parts) else ""
        if pid in seen:
            continue
        seen.add(pid)

        title = re.search(r">([^<]{10,200})</a>", tail)
        area = re.search(r"([\d.,]+)\s*m<sup>2</sup>", tail)
        beds = re.search(r"<li>\s*(\d+)\s*PN\s*</li>", tail)
        wcs = re.search(r"<li>\s*(\d+)\s*WC\s*</li>", tail)
        price = re.search(r'price[^>]*>\s*([^<]{1,40}?)\s*<', tail)
        addr = re.search(r'prop-addr[^>]*>\s*([^<]{5,120}?)\s*<', tail)

        out.append({
            "id": pid,
            "deal": "ban" if deal == "mua" else "thue",
            "district": district,
            "ptype": ptype,
            "title": H.unescape(title.group(1)).strip() if title else None,
            "area_m2": float(area.group(1).replace(",", ".")) if area else None,
            "beds": int(beds.group(1)) if beds else None,
            "wc": int(wcs.group(1)) if wcs else None,
            "price_text": H.unescape(price.group(1)).strip() if price else None,
            "addr": H.unescape(addr.group(1)).strip() if addr else None,
            "url": "https://mogi.vn" + href,
        })
    return out


for fname in ("mogi-ban.html", "mogi-thue.html"):
    p = ROOT / "data" / "output" / fname
    if not p.exists():
        print(f"thieu {p}")
        continue
    rows = parse(p.read_text(encoding="utf-8"))
    full = [r for r in rows if r["price_text"] and r["area_m2"]]
    print("=" * 70)
    print(f"{fname}: {len(rows)} tin | co DU ca gia va dien tich: {len(full)}")
    for r in full[:4]:
        print(f"  [{r['deal']}] {r['price_text']:<14} {str(r['area_m2']):>7} m²  "
              f"{str(r['beds']) + 'PN' if r['beds'] else '   ':<5} "
              f"{r['district']:<16} {r['ptype'][:22]}")
        print(f"        {r['title'][:78] if r['title'] else ''}")
