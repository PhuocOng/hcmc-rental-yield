"""Probe 3 (cuoi): tach ban/thue, kiem tra phan trang that, va tham so chia nho."""

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


def listing(**params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        return json.loads(r.read().decode("utf-8"))


HCM = 13000

# -------------------------------- A) ty le tin ban vs thue trong cg=1010
print("=" * 68)
print("[A] Phan bo truong `type` cua tin trong cg=1010 (200 tin dau)")
types = Counter()
for o in range(0, 200, 50):
    r = listing(cg=1010, limit=50, o=o, region_v2=HCM)
    for a in r.get("ads") or []:
        types[a.get("type")] += 1
    time.sleep(0.35)
print(f"    {dict(types)}")
print("    -> s = ban, u = cho thue (kiem chung bang price_string ben duoi)")
r = listing(cg=1010, limit=50, o=0, region_v2=HCM)
for a in (r.get("ads") or [])[:6]:
    print(f"      type={a.get('type')}  {str(a.get('price_string')):<16} {str(a.get('subject'))[:42]}")

# --------------------- B) tim tham so loc ban/thue phia server
print("=" * 68)
print("[B] Thu cac tham so loc ban/thue")
for pname in ("st", "ad_type", "listing_type", "sp", "pty"):
    for pval in ("s", "u"):
        try:
            r = listing(**{"cg": 1010, "limit": 50, "o": 0, "region_v2": HCM, pname: pval})
            c = Counter(a.get("type") for a in r.get("ads") or [])
            print(f"    {pname}={pval!r:<4} total={str(r.get('total')):<7} phan bo type: {dict(c)}")
        except Exception as e:
            print(f"    {pname}={pval!r:<4} loi {type(e).__name__}")
        time.sleep(0.35)

# ------------------- C) offset sau co tra ve tin THAT SU khac nhau khong
print("=" * 68)
print("[C] Kiem tra phan trang: ad_id o cac offset khac nhau co trung nhau khong")
seen = {}
for o in (0, 2000, 5000, 9000, 9980, 12000, 20000):
    try:
        r = listing(cg=1020, limit=20, o=o, region_v2=HCM)
        ids = [a.get("ad_id") for a in r.get("ads") or []]
        seen[o] = ids
        print(f"    o={o:<7} -> {len(ids)} tin | ad_id dau = {ids[0] if ids else None}")
    except Exception as e:
        print(f"    o={o:<7} -> loi {type(e).__name__}")
    time.sleep(0.35)
allids = [i for v in seen.values() for i in v]
print(f"    Tong cong {len(allids)} tin, trong do {len(set(allids))} ad_id KHAC NHAU")
if len(set(allids)) < len(allids):
    print("    !! CO TRUNG -> offset sau khong dang tin, phai chia nho truy van")

# ------------------------------ D) tham so chia nho theo quan / phuong
print("=" * 68)
print("[D] Thu tham so chia nho theo dia ban")
for pname, pval in (("area_v2", 13096), ("area", 13096), ("ward", 9245), ("w", 9245)):
    try:
        r = listing(**{"cg": 1020, "limit": 5, "o": 0, "region_v2": HCM, pname: pval})
        ads = r.get("ads") or []
        nms = {a.get("area_name") for a in ads} or {"-"}
        wds = {a.get("ward_name") for a in ads} or {"-"}
        print(f"    {pname}={pval:<7} total={str(r.get('total')):<7} quan={list(nms)[:2]} phuong={list(wds)[:2]}")
    except Exception as e:
        print(f"    {pname}={pval:<7} loi {type(e).__name__}")
    time.sleep(0.35)
