"""Probe 2: tim danh muc CHO THUE va do tran phan trang cua API Cho Tot."""

import json
import ssl
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
CTX = ssl.create_default_context()
BASE = "https://gateway.chotot.com/v1/public/ad-listing"


def listing(**params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))


out = {}

# ------------------------------------------------ 1) quet toan bo ma danh muc BDS
print("=" * 68)
print("[1] Quet ma danh muc 1000-1099 (giu lai cai tra ve dung cg minh hoi)")
cats = {}
for cg in range(1000, 1100):
    try:
        r = listing(cg=cg, limit=1, o=0, region_v2=13000)
        ads = r.get("ads") or []
        if ads and ads[0].get("category") == cg:
            nm = ads[0].get("category_name", "?")
            typ = ads[0].get("type")
            cats[cg] = {"name": nm, "type": typ, "total": r.get("total")}
            print(f"    cg={cg:<6} type={str(typ):<3} total={str(r.get('total')):<7} {nm}")
    except Exception:
        pass
    time.sleep(0.25)
out["categories"] = cats

# --------------------------------------------------------- 2) thu tham so `type`
print("=" * 68)
print("[2] Thu tham so type tren cg=1010 (Can ho/Chung cu)")
for t in ("s", "u", "b", "r"):
    try:
        r = listing(cg=1010, limit=1, o=0, region_v2=13000, type=t)
        ads = r.get("ads") or []
        if ads:
            a = ads[0]
            print(f"    type={t!r:<5} total={str(r.get('total')):<7} "
                  f"cat={a.get('category_name')} | gia={a.get('price_string')} "
                  f"| {str(a.get('subject'))[:40]}")
        else:
            print(f"    type={t!r:<5} total={r.get('total')} (khong co tin)")
    except Exception as e:
        print(f"    type={t!r:<5} loi {type(e).__name__}")
    time.sleep(0.4)

# ------------------------------------------------------- 3) do tran phan trang
print("=" * 68)
print("[3] Do tran phan trang (offset o) tren cg=1020 region=13000")
for o in (0, 5000, 9000, 9950, 10000, 12000):
    try:
        r = listing(cg=1020, limit=20, o=o, region_v2=13000)
        n = len(r.get("ads") or [])
        print(f"    o={o:<7} -> tra ve {n} tin (total bao {r.get('total')})")
    except Exception as e:
        print(f"    o={o:<7} -> loi {type(e).__name__}: {e}")
    time.sleep(0.4)

with open("data/probe_report2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("=" * 68)
print("Da ghi data/probe_report2.json")
