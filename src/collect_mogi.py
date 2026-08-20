"""Thu thap tin rao BAN va CHO THUE tu mogi.vn — TP.HCM. Nguon DOI CHUNG.

Vi sao co gioi han trang: mogi chi 15-16 tin/trang, cao het se mat nhieu gio va
lam phien server ho. Day la nguon DOI CHUNG — chi can du de so trung vi theo quan
voi Cho Tot, khong can toan bo. Mac dinh 25 trang/quan/loai (~400 tin), va so
trang bi bo qua duoc GHI LAI trong file .meta.json de bao cao trung thuc.

Chay:
    python src/collect_mogi.py                 # thu 2 quan, 3 trang — kiem tra truoc
    python src/collect_mogi.py --full          # chay that
    python src/collect_mogi.py --full --pages 40
"""

from __future__ import annotations

import argparse
import html as H
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ROOT = Path(__file__).resolve().parent.parent
DELAY = 1.0     # cham hon Cho Tot vi day la HTML thuong, khong phai API

# slug quan cua mogi <-> ten quan cua Cho Tot (de sau nay ghep hai nguon)
DISTRICTS = {
    "quan-1": "Quận 1", "quan-3": "Quận 3", "quan-4": "Quận 4", "quan-5": "Quận 5",
    "quan-6": "Quận 6", "quan-7": "Quận 7", "quan-8": "Quận 8", "quan-10": "Quận 10",
    "quan-11": "Quận 11", "quan-12": "Quận 12",
    "quan-binh-tan": "Quận Bình Tân", "quan-binh-thanh": "Quận Bình Thạnh",
    "quan-go-vap": "Quận Gò Vấp", "quan-phu-nhuan": "Quận Phú Nhuận",
    "quan-tan-binh": "Quận Tân Bình", "quan-tan-phu": "Quận Tân Phú",
    "huyen-binh-chanh": "Huyện Bình Chánh", "huyen-cu-chi": "Huyện Củ Chi",
    "huyen-hoc-mon": "Huyện Hóc Môn", "huyen-nha-be": "Huyện Nhà Bè",
    "huyen-can-gio": "Huyện Cần Giờ", "thanh-pho-thu-duc": "Thành phố Thủ Đức",
}

DEALS = {"mua": "ban", "thue": "thue"}

LINK = re.compile(
    r'href="(?:https://mogi\.vn)?(/([a-z0-9\-]+)/(mua|thue)-([a-z0-9\-]+)/[a-z0-9\-]*?-id(\d+))"'
)
UNITS = {"tỷ": 1_000_000_000, "triệu": 1_000_000, "nghìn": 1_000, "ngàn": 1_000}


def parse_price(text: str | None) -> int | None:
    """'2 tỷ 650 triệu' -> 2650000000 ; '8 triệu 500 nghìn' -> 8500000."""
    if not text:
        return None
    total, found = 0, False
    for num, unit in re.findall(r"([\d.,]+)\s*(tỷ|triệu|nghìn|ngàn)", text):
        try:
            total += float(num.replace(".", "").replace(",", ".")) * UNITS[unit]
        except ValueError:
            continue
        found = True
    return int(total) if found else None


def fetch(url: str, tries: int = 3) -> str | None:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept-Language": "vi-VN,vi;q=0.9"})
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return None


def parse_page(html: str) -> list[dict]:
    rows, parts = [], LINK.split(html)
    for i in range(1, len(parts), 6):
        href, district, deal, ptype, pid = parts[i:i + 5]
        tail = parts[i + 5] if i + 5 < len(parts) else ""
        area = re.search(r"([\d.,]+)\s*m<sup>2</sup>", tail)
        beds = re.search(r"<li>\s*(\d+)\s*PN\s*</li>", tail)
        price_txt = re.search(r'price[^>]*>\s*([^<]{1,40}?)\s*<', tail)
        ptxt = H.unescape(price_txt.group(1)).strip() if price_txt else None
        rows.append({
            "id": pid,
            "deal": DEALS[deal],
            "district_slug": district,
            "district": DISTRICTS.get(district),
            "ptype": ptype,
            "area_m2": float(area.group(1).replace(",", ".")) if area else None,
            "beds": int(beds.group(1)) if beds else None,
            "price_text": ptxt,
            "price_vnd": parse_price(ptxt),
            "url": "https://mogi.vn" + href,
        })
    return rows


def crawl(slug: str, deal: str, max_pages: int) -> tuple[list[dict], bool]:
    """Tra ve (danh sach tin, co bi cham tran trang khong)."""
    out, seen = [], set()
    hit_cap = False
    for cp in range(1, max_pages + 1):
        url = f"https://mogi.vn/{slug}/{deal}-nha-dat" + (f"?cp={cp}" if cp > 1 else "")
        html = fetch(url)
        if not html:
            break
        fresh = [r for r in parse_page(html) if r["id"] not in seen]
        if not fresh:
            break
        seen.update(r["id"] for r in fresh)
        out.extend(fresh)
        if cp == max_pages:
            hit_cap = True     # con tin nhung minh tu dung -> phai ghi lai
        time.sleep(DELAY)
    return out, hit_cap


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="chay het 22 quan")
    ap.add_argument("--pages", type=int, default=25, help="tran so trang moi quan/loai")
    args = ap.parse_args()

    districts = DISTRICTS if args.full else dict(list(DISTRICTS.items())[:2])
    pages = args.pages if args.full else 3

    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d")
    outdir = ROOT / "data" / "raw"
    outdir.mkdir(parents=True, exist_ok=True)
    tag = "hcm" if args.full else "hcm_test"
    outfile = outdir / f"mogi_{tag}_{stamp}.jsonl"

    print(f"mogi.vn | {len(districts)} quan | toi da {pages} trang/quan/loai")
    print(f"Ghi ra: {outfile}\n")

    total, capped, bad_slugs = 0, [], []
    started = time.time()

    with outfile.open("w", encoding="utf-8") as f:
        for slug, name in districts.items():
            for deal in ("mua", "thue"):
                rows, hit = crawl(slug, deal, pages)
                if not rows:
                    bad_slugs.append(f"{slug}/{deal}")
                if hit:
                    capped.append(f"{slug}/{deal}")
                now = datetime.now(timezone.utc).isoformat()
                for r in rows:
                    r["_collected_at"] = now
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                total += len(rows)
                ok = sum(1 for r in rows if r["price_vnd"] and r["area_m2"])
                print(f"  {name or slug:<22} {DEALS[deal]:<5} {len(rows):>5} tin "
                      f"({ok} du gia+m²){'  [cham tran]' if hit else ''}", flush=True)

    meta = {
        "source": "mogi.vn", "region": "TP.HCM", "collected": stamp,
        "page_cap_per_cell": pages, "total_rows": total,
        "cells_hit_cap": capped,          # nhung o CON TIN nhung minh da dung
        "cells_empty": bad_slugs,         # slug sai hoac that su khong co tin
    }
    (outfile.with_suffix(".meta.json")).write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nXONG — {total:,} tin trong {(time.time()-started)/60:.1f} phut")
    if capped:
        print(f"  ! {len(capped)} o cham tran {pages} trang (con tin chua lay): {capped[:6]}")
    if bad_slugs:
        print(f"  ! {len(bad_slugs)} o rong — kiem tra slug: {bad_slugs[:6]}")
    print(f"  File: {outfile}")


if __name__ == "__main__":
    main()
