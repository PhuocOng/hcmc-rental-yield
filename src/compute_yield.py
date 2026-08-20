"""Buoc 2 — Tinh ti suat cho thue theo O.

Nguyen tac (xem PLAN.md): KHONG duoc lay gia ban trung binh chia cho gia thue
trung binh cua ca quan — nhu vay la dem gia biet thu chia cho tien thue phong tro.
Phai ghep trong tung O co cung loai hinh va cung tam dien tich.

Tinh o HAI muc do de tu kiem tra lan nhau:
  A. phuong x danh muc                  -> min hon ve dia ly, dung cho ban do
  B. quan x danh muc x nhom dien tich   -> khop hon ve loai tai san, dung cho so tong

Neu A va B lech nhau nhieu => co hieu ung khac biet dien tich giua tin ban va tin
thue, va phai bao cao dieu do chu khong duoc giau.

Chay: python src/compute_yield.py
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "interim" / "clean_hcm.jsonl"
OUTDIR = ROOT / "data" / "output"

MIN_N = 10          # so tin toi thieu MOI BEN thi o moi duoc tinh
SIZE_BUCKETS = [(0, 40), (40, 60), (60, 80), (80, 120), (120, 200), (200, 10_000)]


def bucket(size: float) -> str:
    for lo, hi in SIZE_BUCKETS:
        if lo <= size < hi:
            return f"{lo}-{hi if hi < 10_000 else '+'}"
    return "?"


def yields(cells: dict) -> dict:
    """Tu {khoa: {ban: [ppm2...], thue: [ppm2...]}} -> ti suat moi o."""
    out = {}
    for key, v in cells.items():
        if len(v["ban"]) < MIN_N or len(v["thue"]) < MIN_N:
            continue
        sale = st.median(v["ban"])            # dong/m²
        rent = st.median(v["thue"])           # dong/m²/thang
        out[key] = {
            "n_ban": len(v["ban"]), "n_thue": len(v["thue"]),
            "gia_ban_m2": sale, "gia_thue_m2": rent,
            "ti_suat_pct": rent * 12 / sale * 100,
        }
    return out


rows = [json.loads(l) for l in SRC.open(encoding="utf-8")]
print(f"Doc {len(rows):,} tin da lam sach\n")

# ------------------------------------------------------- A) phuong x danh muc
cells_a = defaultdict(lambda: {"ban": [], "thue": [], "meta": None})
for r in rows:
    c = cells_a[(r["ward"], r["category"])]
    c[r["deal"]].append(r["price_per_m2"])
    c["meta"] = (r["ward_name"], r["district_name"], r["category_name"])

ya = {}
for key, v in cells_a.items():
    if len(v["ban"]) >= MIN_N and len(v["thue"]) >= MIN_N:
        sale, rent = st.median(v["ban"]), st.median(v["thue"])
        ward_name, dist_name, cat_name = v["meta"]
        ya[key] = {
            "ward": key[0], "ward_name": ward_name, "district_name": dist_name,
            "category_name": cat_name, "n_ban": len(v["ban"]), "n_thue": len(v["thue"]),
            "gia_ban_m2": sale, "gia_thue_m2": rent,
            "ti_suat_pct": rent * 12 / sale * 100,
        }

# ------------------------------- B) quan x danh muc x nhom dien tich
cells_b = defaultdict(lambda: {"ban": [], "thue": [], "meta": None})
for r in rows:
    c = cells_b[(r["district"], r["category"], bucket(r["size_m2"]))]
    c[r["deal"]].append(r["price_per_m2"])
    c["meta"] = (r["district_name"], r["category_name"])

yb = {}
for key, v in cells_b.items():
    if len(v["ban"]) >= MIN_N and len(v["thue"]) >= MIN_N:
        sale, rent = st.median(v["ban"]), st.median(v["thue"])
        dist_name, cat_name = v["meta"]
        yb[key] = {
            "district": key[0], "district_name": dist_name, "category_name": cat_name,
            "size_bucket": key[2], "n_ban": len(v["ban"]), "n_thue": len(v["thue"]),
            "gia_ban_m2": sale, "gia_thue_m2": rent,
            "ti_suat_pct": rent * 12 / sale * 100,
        }

print("=" * 72)
print("SO O DU DIEU KIEN (>= 10 tin moi ben)")
print(f"  A. phuong x danh muc                {len(ya):>5} / {len(cells_a)}")
print(f"  B. quan x danh muc x dien tich      {len(yb):>5} / {len(cells_b)}")

for label, y in (("A (phuong)", ya), ("B (quan x dien tich)", yb)):
    v = [x["ti_suat_pct"] for x in y.values()]
    n = sum(x["n_ban"] + x["n_thue"] for x in y.values())
    print("=" * 72)
    print(f"KET QUA — muc {label}   [{len(y)} o, {n:,} tin]")
    print(f"  Trung vi ti suat cac o : {st.median(v):.2f} %/nam")
    print(f"  Trung binh             : {st.mean(v):.2f} %/nam")
    q = st.quantiles(v, n=10)
    print(f"  p10 {q[0]:.2f}%   p50 {st.median(v):.2f}%   p90 {q[8]:.2f}%")
    print(f"  thap nhat {min(v):.2f}%   cao nhat {max(v):.2f}%")

# --------------------------------------------------- theo danh muc
print("=" * 72)
print("THEO DANH MUC (muc B)")
for cat in ("Căn hộ/Chung cư", "Nhà ở"):
    v = [x["ti_suat_pct"] for x in yb.values() if x["category_name"] == cat]
    if v:
        print(f"  {cat:<18} {len(v):>3} o   trung vi {st.median(v):.2f} %/nam")

# --------------------------------------------------- xep hang quan
print("=" * 72)
print("XEP HANG QUAN (muc B, gop moi danh muc/dien tich cua quan)")
byd = defaultdict(list)
for x in yb.values():
    byd[x["district_name"]].append(x["ti_suat_pct"])
rank = sorted(((st.median(v), k, len(v)) for k, v in byd.items()), reverse=True)
for med, name, n in rank:
    print(f"  {name:<26} {med:>5.2f} %/nam   ({n} o)")

OUTDIR.mkdir(parents=True, exist_ok=True)
(OUTDIR / "yield_by_ward.json").write_text(
    json.dumps(list(ya.values()), ensure_ascii=False, indent=2), encoding="utf-8")
(OUTDIR / "yield_by_district_size.json").write_text(
    json.dumps(list(yb.values()), ensure_ascii=False, indent=2), encoding="utf-8")
print("=" * 72)
print("Da ghi data/output/yield_by_ward.json va yield_by_district_size.json")
