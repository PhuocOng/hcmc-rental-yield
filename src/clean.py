"""Buoc 1 — Lam sach du lieu tho.

Ap 7 luat da chot, va GHI LAI moi luat loai bao nhieu tin. Nhat ky loai bo la
thu se dua thang vao trang Phuong phap cua website — loc ma khong ghi lai thi
nguoi doc khong co cach nao kiem tra.

Vao : data/raw/chotot_hcm_<ngay>.jsonl
Ra  : data/interim/clean_hcm.jsonl  +  data/output/clean_report.json

Chay: python src/clean.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw" / "chotot_hcm_20260815.jsonl"
OUT = ROOT / "data" / "interim" / "clean_hcm.jsonl"
REPORT = ROOT / "data" / "output" / "clean_report.json"

# ------------------------------------------------------------------ nguong loc
SIZE_MIN, SIZE_MAX = 10, 1_000                     # m²
PRICE_SALE = (100_000_000, 500_000_000_000)        # 100 trieu .. 500 ty
PRICE_RENT = (500_000, 500_000_000)                # 500 nghin .. 500 trieu/thang
PPM2_SALE = (5_000_000, 500_000_000)               # 5 .. 500 trieu/m²
PPM2_RENT = (20_000, 2_000_000)                    # 20 nghin .. 2 trieu/m²/thang


def main() -> None:
    rejects: Counter[str] = Counter()
    kept: list[dict] = []
    seen_soft: set[tuple] = set()
    total = 0

    with SRC.open(encoding="utf-8") as f:
        for line in f:
            total += 1
            a = json.loads(line)
            st = (a.get("_query") or {}).get("st")

            price, size = a.get("price"), a.get("size")
            ward, cat = a.get("ward"), a.get("category")

            # --- 1. truong bat buoc
            if not price or not size or not ward or not cat or st not in ("s", "u"):
                rejects["1_thieu_truong_bat_buoc"] += 1
                continue

            # --- 2. dien tich hop ly
            if not (SIZE_MIN <= size <= SIZE_MAX):
                rejects["2_dien_tich_vo_ly"] += 1
                continue

            # --- 3. gia hop ly theo loai giao dich
            lo, hi = PRICE_SALE if st == "s" else PRICE_RENT
            if not (lo <= price <= hi):
                rejects["3_gia_vo_ly"] += 1
                continue

            # --- 4. gia tren m² hop ly  (bat tin lech muc: tin ban dang vao muc thue)
            ppm2 = price / size
            lo, hi = PPM2_SALE if st == "s" else PPM2_RENT
            if not (lo <= ppm2 <= hi):
                rejects["4_gia_tren_m2_vo_ly"] += 1
                continue

            # --- 5. trung mem: cung nguoi dang + m² + gia + loai
            key = (a.get("account_oid"), size, price, st, cat)
            if a.get("account_oid") and key in seen_soft:
                rejects["5_trung_mem"] += 1
                continue
            seen_soft.add(key)

            kept.append({
                "ad_id": a["ad_id"],
                "account_oid": a.get("account_oid"),
                "deal": "ban" if st == "s" else "thue",
                "price": price,
                "size_m2": size,
                "price_per_m2": ppm2,
                "rooms": a.get("rooms"),
                "category": cat,
                "category_name": a.get("category_name"),
                # ma phuong/quan la KHOA — ten chi de hien thi, vi ten bi loan do sap nhap
                "ward": ward,
                "ward_name": a.get("ward_name"),
                "district": a.get("area"),
                "district_name": a.get("area_name"),
                "list_time": a.get("list_time"),
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_deal = Counter(r["deal"] for r in kept)
    by_cat = Counter(r["category_name"] for r in kept)
    report = {
        "nguon": SRC.name,
        "tong_dong_vao": total,
        "giu_lai": len(kept),
        "ty_le_giu": round(len(kept) / total * 100, 2),
        "loai_bo": dict(rejects),
        "loai_bo_tong": sum(rejects.values()),
        "con_lai_theo_giao_dich": dict(by_deal),
        "con_lai_theo_danh_muc": dict(by_cat),
        "nguong": {
            "dien_tich_m2": [SIZE_MIN, SIZE_MAX],
            "gia_ban": PRICE_SALE, "gia_thue": PRICE_RENT,
            "gia_m2_ban": PPM2_SALE, "gia_m2_thue": PPM2_RENT,
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Vao : {total:,} tin")
    print(f"Giu : {len(kept):,} tin  ({report['ty_le_giu']}%)\n")
    print("Loai bo theo tung luat:")
    for k in sorted(rejects):
        print(f"   {k:<28} {rejects[k]:>7,}  ({rejects[k]/total*100:.2f}%)")
    print(f"\nCon lai: {dict(by_deal)}")
    for k, v in by_cat.items():
        print(f"   {k:<20} {v:>7,}")
    print(f"\nRa: {OUT}")


if __name__ == "__main__":
    main()
