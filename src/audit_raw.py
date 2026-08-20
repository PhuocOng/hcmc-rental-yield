"""Soi chat luong du lieu tho truoc khi lam sach.

Muc dich KHONG phai lam sach, ma la BIET no ban o dau de dat luat loc cho dung.
Doc theo dong (file 268 MB) va chi giu lai truong can dung.

Chay: python src/audit_raw.py
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "chotot_hcm_20260815.jsonl"

KEEP = ("ad_id", "account_oid", "price", "size", "area", "area_name", "ward",
        "ward_name", "category", "category_name", "type", "rooms",
        "price_million_per_m2", "list_time", "subject")


def pct(n: int, total: int) -> str:
    return f"{n:>7,} ({n / total * 100:5.1f}%)"


rows = []
with SRC.open(encoding="utf-8") as f:
    for line in f:
        a = json.loads(line)
        r = {k: a.get(k) for k in KEEP}
        r["st"] = (a.get("_query") or {}).get("st")
        rows.append(r)

N = len(rows)
print(f"Tong so dong: {N:,}\n")

# ---------------------------------------------------------- 1) trung lap
print("=" * 68)
print("[1] TRUNG LAP")
ids = Counter(r["ad_id"] for r in rows)
dup_id = sum(v - 1 for v in ids.values() if v > 1)
print(f"  ad_id duy nhat            {len(ids):>7,}")
print(f"  dong bi lap lai ad_id     {pct(dup_id, N)}")

# cung nguoi dang + cung dien tich + cung gia -> gan nhu chac la mot tin dang lai
key = Counter((r["account_oid"], r["size"], r["price"], r["st"]) for r in rows
              if r["account_oid"] and r["size"] and r["price"])
soft = sum(v - 1 for v in key.values() if v > 1)
print(f"  nghi trung (nguoi+m²+gia) {pct(soft, N)}")
print(f"  so tai khoan dang tin     {len({r['account_oid'] for r in rows}):>7,}")
top = Counter(r["account_oid"] for r in rows).most_common(3)
print(f"  tai khoan dang nhieu nhat: {[v for _, v in top]} tin")

# ------------------------------------------------------- 2) thieu du lieu
print("=" * 68)
print("[2] THIEU DU LIEU")
for field in ("price", "size", "ward", "ward_name", "area_name", "rooms"):
    miss = sum(1 for r in rows if not r.get(field))
    print(f"  thieu {field:<14} {pct(miss, N)}")

# ------------------------------------- 3) st co khop truong type khong
print("=" * 68)
print("[3] KIEM TRA BO LOC BAN/THUE (st truyen di vs type tra ve)")
mism = Counter((r["st"], r["type"]) for r in rows)
for (s, t), n in sorted(mism.items()):
    flag = "" if s == t else "   <-- LECH"
    print(f"  st={s} -> type={t}: {n:>7,}{flag}")

# ------------------------------------------------------ 4) gia bat thuong
print("=" * 68)
print("[4] GIA BAT THUONG")
for stt, label in (("s", "BAN"), ("u", "THUE")):
    p = sorted(r["price"] for r in rows if r["st"] == stt and r["price"])
    if not p:
        continue
    q = st.quantiles(p, n=100)
    print(f"  {label} (n={len(p):,})")
    print(f"     p1 {q[0]:>18,.0f}   trung vi {st.median(p):>18,.0f}   p99 {q[98]:>18,.0f}")
    print(f"     min {min(p):>17,.0f}   max      {max(p):>18,.0f}")
    absurd_lo = sum(1 for x in p if x < (1e8 if stt == "s" else 5e5))
    absurd_hi = sum(1 for x in p if x > (5e11 if stt == "s" else 5e8))
    print(f"     qua thap: {absurd_lo:,}    qua cao: {absurd_hi:,}")

# ---------------------------------------------------- 5) dien tich bat thuong
print("=" * 68)
print("[5] DIEN TICH (truong `size`)")
s = sorted(r["size"] for r in rows if r["size"])
q = st.quantiles(s, n=100)
print(f"  n={len(s):,}  min={min(s):,.0f}  p1={q[0]:,.0f}  trung vi={st.median(s):,.0f}  "
      f"p99={q[98]:,.0f}  max={max(s):,.0f}")
print(f"  duoi 10 m²: {sum(1 for x in s if x < 10):,}   tren 1000 m²: {sum(1 for x in s if x > 1000):,}")

# ------------------------------------------------- 6) ten phuong co bi loan
print("=" * 68)
print("[6] TEN PHUONG (van de sap nhap hanh chinh)")
wards = {r["ward"]: r["ward_name"] for r in rows if r["ward"]}
old = [w for w in wards.values() if w and "cũ" in w]
print(f"  so phuong duy nhat        {len(wards):>7,}")
print(f"  ten co chua chu 'cũ'      {len(old):>7,}  vd: {old[:2]}")
names = Counter(r["ward_name"] for r in rows if r["ward_name"])
multi = {n: c for n, c in names.items() if sum(1 for w, v in wards.items() if v == n) > 1}
print(f"  ten phuong ung voi >1 ma  {len(multi):>7,}")

# --------------------------------- 7) o co du ca ban va thue khong
print("=" * 68)
print("[7] DO PHU: o (phuong x danh muc) co du CA ban VA thue?")
cell = defaultdict(lambda: {"s": 0, "u": 0})
for r in rows:
    if r["ward"] and r["size"] and r["price"]:
        cell[(r["ward"], r["category"])][r["st"]] += 1
both10 = sum(1 for v in cell.values() if v["s"] >= 10 and v["u"] >= 10)
both1 = sum(1 for v in cell.values() if v["s"] >= 1 and v["u"] >= 1)
print(f"  tong so o                     {len(cell):>6,}")
print(f"  o co ca ban va thue (>=1)     {both1:>6,}")
print(f"  o DU DIEU KIEN (>=10 moi ben) {both10:>6,}   <-- so o se len ban do")
