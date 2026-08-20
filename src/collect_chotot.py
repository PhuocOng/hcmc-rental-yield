"""Thu thap tin rao BAN va CHO THUE tu Cho Tot — TP.HCM.

Chia truy van theo tung QUAN de khong dinh tran phan trang 10.000 cua API.
Ghi ra data/raw/chotot_<region>_<ngay>.jsonl — moi dong mot tin, giu nguyen ban.

Chay:
    python src/collect_chotot.py                # TP.HCM, can ho + nha o
    python src/collect_chotot.py --region hanoi
    python src/collect_chotot.py --cats 1010 1020 1050
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://gateway.chotot.com/v1/public/ad-listing"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
CTX = ssl.create_default_context()
ROOT = Path(__file__).resolve().parent.parent

PAGE = 50          # so tin moi lan goi
DELAY = 0.45       # nghi giua cac lan goi — cao cham cho lich su
MAX_PAGES = 200    # chan an toan: 200 x 50 = 10.000, dung bang tran cua API

REGIONS = {"hcm": (13000, "TP.HCM"), "hanoi": (12000, "Hà Nội")}

CATS = {
    1010: "Căn hộ/Chung cư",
    1020: "Nhà ở",
    1030: "Văn phòng/MBKD",
    1040: "Đất",
    1050: "Phòng trọ",
}

# st=s -> tin BAN, st=u -> tin CHO THUE. Bat buoc phai loc, vi hai loai
# nam CHUNG mot danh muc (xem README).
STATES = {"s": "ban", "u": "thue"}


def fetch(params: dict, tries: int = 4) -> dict:
    """Goi API, tu thu lai khi loi mang."""
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            wait = 2 ** attempt
            print(f"      ! {type(e).__name__} — thu lai sau {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"That bai sau {tries} lan: {url}")


def load_districts() -> dict[int, str]:
    """Doc danh sach quan da do duoc o probe 4."""
    p = ROOT / "data" / "output" / "hcm_districts.json"
    if not p.exists():
        sys.exit(f"Thieu {p} — chay probe/probe_districts_and_fields.py truoc.")
    d = json.loads(p.read_text(encoding="utf-8"))["districts"]
    return {int(k): v for k, v in d.items()}


def crawl_cell(region_code: int, area_code: int, cg: int, st: str) -> list[dict]:
    """Tai het tin cua mot o (quan x danh muc x ban/thue)."""
    out, seen = [], set()
    for page in range(MAX_PAGES):
        data = fetch({
            "region_v2": region_code, "area_v2": region_code + area_code,
            "cg": cg, "st": st, "limit": PAGE, "o": page * PAGE,
        })
        ads = data.get("ads") or []
        if not ads:
            break
        fresh = 0
        for a in ads:
            aid = a.get("ad_id")
            if aid and aid not in seen:
                seen.add(aid)
                out.append(a)
                fresh += 1
        # het tin moi -> API bat dau lap lai, dung
        if fresh == 0 or len(ads) < PAGE:
            break
        time.sleep(DELAY)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="hcm", choices=list(REGIONS))
    ap.add_argument("--cats", nargs="+", type=int, default=[1010, 1020])
    args = ap.parse_args()

    region_code, region_name = REGIONS[args.region]
    districts = load_districts()

    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d")
    outdir = ROOT / "data" / "raw"
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / f"chotot_{args.region}_{stamp}.jsonl"

    print(f"Thu thap {region_name} | danh muc: {[CATS.get(c, c) for c in args.cats]}")
    print(f"Ghi ra: {outfile}\n")

    total, started = 0, time.time()
    tally: dict[str, int] = {}

    with outfile.open("w", encoding="utf-8") as f:
        for area_code, area_name in sorted(districts.items()):
            for cg in args.cats:
                for st, st_label in STATES.items():
                    ads = crawl_cell(region_code, area_code, cg, st)
                    now = datetime.now(timezone.utc).isoformat()
                    for a in ads:
                        # gan xuat xu vao tung tin de sau nay truy nguoc duoc
                        a["_collected_at"] = now
                        a["_query"] = {
                            "region_v2": region_code, "area_v2": region_code + area_code,
                            "cg": cg, "st": st,
                        }
                        f.write(json.dumps(a, ensure_ascii=False) + "\n")
                    total += len(ads)
                    key = f"{cg}_{st}"
                    tally[key] = tally.get(key, 0) + len(ads)
                    print(f"  {area_name:<26} {CATS.get(cg, cg):<16} {st_label:<5} "
                          f"{len(ads):>5} tin   (tong {total:,})", flush=True)
                    time.sleep(DELAY)

    mins = (time.time() - started) / 60
    print(f"\nXONG — {total:,} tin trong {mins:.1f} phut")
    for key in sorted(tally):
        cg_str, st = key.split("_")
        print(f"   {CATS.get(int(cg_str), cg_str):<18} {STATES[st]:<5} {tally[key]:>7,}")
    print(f"File: {outfile}  ({outfile.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
