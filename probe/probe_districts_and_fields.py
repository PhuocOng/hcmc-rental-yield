"""Probe 4: lay danh sach quan cua TP.HCM + xac minh truong nao la met vuong.

Xuat: data/output/hcm_districts.json
"""

import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
CTX = ssl.create_default_context()
BASE = "https://gateway.chotot.com/v1/public/ad-listing"
HCM = 13000
CATS = {1010: "Căn hộ/Chung cư", 1020: "Nhà ở", 1030: "Văn phòng/MBKD", 1040: "Đất", 1050: "Phòng trọ"}


def listing(**params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))


# ============================================ A) truong nao la met vuong?
print("=" * 70)
print("[A] Xac minh: `size` hay `area` moi la met vuong?")
print("    Kiem tra: price / price_million_per_m2 phai bang dien tich that\n")
ok_size = ok_area = tested = 0
for a in listing(cg=1020, st="s", limit=40, o=0, region_v2=HCM).get("ads", []):
    p, ppm2 = a.get("price"), a.get("price_million_per_m2")
    if not p or not ppm2:
        continue
    implied = p / 1e6 / ppm2          # dien tich suy ra tu chinh so lieu cua ho
    tested += 1
    if a.get("size") and abs(implied - a["size"]) < 0.6:
        ok_size += 1
    if a.get("area") and abs(implied - a["area"]) < 0.6:
        ok_area += 1
    if tested <= 5:
        print(f"    gia={p/1e9:>6.2f} ty  ppm2={ppm2:>7.2f}  =>  dien tich suy ra={implied:>7.1f}"
              f"   | size={a.get('size')}  area={a.get('area')} ({a.get('area_name')})")
print(f"\n    Tren {tested} tin:  khop voi `size` = {ok_size}   |   khop voi `area` = {ok_area}")
print("    => DUNG TRUONG `size` LAM MET VUONG." if ok_size > ok_area else "    => xem lai!")

# ============================================ B) danh sach quan cua TP.HCM
print("=" * 70)
print("[B] Gom danh sach quan (ma `area` + ten)")
districts, wards = {}, {}
for cg in CATS:
    for st in ("s", "u"):
        for o in (0, 50, 100, 150):
            try:
                r = listing(cg=cg, st=st, limit=50, o=o, region_v2=HCM)
            except Exception:
                break
            for a in r.get("ads", []):
                if a.get("area") and a.get("area_name"):
                    districts[a["area"]] = a["area_name"]
                if a.get("ward") and a.get("ward_name"):
                    wards[a["ward"]] = a["ward_name"]
            time.sleep(0.3)
print(f"    Tim duoc {len(districts)} quan/huyen, {len(wards)} phuong/xa\n")
for code, name in sorted(districts.items()):
    print(f"      area={code:<5} area_v2={13000 + code:<7} {name}")

# ============================ C) dem tin theo quan de biet quy mo phai cao
print("=" * 70)
print("[C] Dem so tin moi quan (can ho + nha o) de uoc luong khoi luong")
totals, grand = {}, Counter()
for code, name in sorted(districts.items()):
    row = {}
    for cg in (1010, 1020):
        for st in ("s", "u"):
            try:
                n = listing(cg=cg, st=st, limit=1, o=0, region_v2=HCM,
                            area_v2=13000 + code).get("total", 0)
            except Exception:
                n = None
            row[f"{cg}_{st}"] = n
            if n:
                grand[f"{cg}_{st}"] += n
            time.sleep(0.25)
    totals[code] = {"name": name, **row}
    print(f"    {name:<28} can-ho ban={str(row['1010_s']):>6} thue={str(row['1010_u']):>6}"
          f"  |  nha-o ban={str(row['1020_s']):>6} thue={str(row['1020_u']):>6}")

print(f"\n    TONG CONG: {dict(grand)}")
print(f"    Uoc tinh tong so tin phai tai: ~{sum(grand.values()):,}")

with open("data/output/hcm_districts.json", "w", encoding="utf-8") as f:
    json.dump({"districts": districts, "counts": totals, "wards_sample": wards},
              f, ensure_ascii=False, indent=2)
print("\n    Da ghi data/output/hcm_districts.json")
