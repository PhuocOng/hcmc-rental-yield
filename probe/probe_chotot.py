"""Do cau truc API cong khai cua Cho Tot (nhatot.com).

Muc dich: KHONG doan ma vung / ma danh muc, ma suy ra tu chinh du lieu tra ve.
Chay: python probe/probe_chotot.py
Ket qua chi tiet ghi ra data/probe_report.json (UTF-8).
"""

import json
import ssl
import sys
import time
import urllib.error
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


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))


def listing(**params):
    return get(BASE + "?" + urllib.parse.urlencode(params))


report = {}

# ---------------------------------------------------------------- 1) mot tin mau
print("=" * 68)
print("[1] Mot tin mau -> xem co nhung truong gi")
sample = listing(cg=1000, limit=1, o=0)
ad = (sample.get("ads") or [{}])[0]
report["sample_ad"] = ad
print(f"    tong tin trong cg=1000: {sample.get('total')}")
print(f"    so truong moi tin: {len(ad)}")
interesting = [
    "ad_id", "subject", "price", "price_string", "area", "size", "rooms",
    "category", "category_name", "region", "region_name", "area_name",
    "ward", "ward_name", "list_time", "type", "price_million_per_m2",
]
for k in interesting:
    if k in ad:
        print(f"      {k:<24} = {str(ad[k])[:58]}")

# ------------------------------------------------- 2) tim ma vung Ha Noi / TP.HCM
print("=" * 68)
print("[2] Do ma vung (region_v2)")
regions_found = {}
for code in (12000, 13000, 11000, 1, 2):
    try:
        r = listing(cg=1000, limit=1, o=0, region_v2=code)
        ads = r.get("ads") or []
        if ads:
            nm = ads[0].get("region_name", "?")
            regions_found[code] = {"region_name": nm, "total": r.get("total")}
            print(f"    region_v2={code:<6} -> {nm:<22} total={r.get('total')}")
    except Exception as e:
        print(f"    region_v2={code:<6} -> loi: {type(e).__name__}")
    time.sleep(0.4)
report["regions"] = regions_found

# --------------------------------------- 3) suy ra taxonomy danh muc tu du lieu
print("=" * 68)
print("[3] Cac danh muc con trong nhom bat dong san (cg=1000)")
cats = Counter()
names = {}
for offset in range(0, 400, 50):
    try:
        r = listing(cg=1000, limit=50, o=offset)
        for a in r.get("ads") or []:
            c = a.get("category")
            if c is not None:
                cats[c] += 1
                names.setdefault(c, a.get("category_name", "?"))
    except Exception as e:
        print(f"    offset={offset} loi: {type(e).__name__}")
        break
    time.sleep(0.4)

for c, n in sorted(cats.items()):
    print(f"    cg={c:<6} n={n:<4} {names.get(c)}")
report["categories"] = {str(c): {"name": names.get(c), "seen": n} for c, n in cats.items()}

with open("data/probe_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("=" * 68)
print("Da ghi data/probe_report.json")
