"""Buoc 3 — Tang tai chinh.

Bien "ti suat cho thue" thanh mot phan tich dau tu:
  1. ti suat RONG  (tru thue, phi, bo trong, bao tri)
  2. chenh lech so voi gui tiet kiem
  3. kich ban DI VAY -> dong tien moi thang
  4. cau hoi chot: gia nha phai tang bao nhieu %/nam thi nguoi mua moi hoa von?

Moi gia dinh deu nam o GIA_DINH ben duoi va duoc ghi ra file ket qua — nguoi doc
phai thay duoc minh da gia dinh gi, va tu chinh duoc.

Chay: python src/financial_layer.py
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "data" / "output"

# ----------------------------------------------------------------- gia dinh
GD = {
    "lai_tiet_kiem": 0.060,        # 6,0%/nam — Big4 tai quay (moc than trong)
    "lai_vay_tha_noi": 0.120,      # 12,0%/nam — giua khoang 11-15% sau uu dai
    "ty_le_vay": 0.70,             # vay 70% gia tri nha
    "bo_trong_thang": 1.0,         # 1 thang/nam khong co khach thue
    "thue_cho_thue": 0.10,         # 10% doanh thu (ca nhan > 100 trieu/nam)
    "phi_quan_ly_m2_thang": 15_000,  # dong/m²/thang — chi ap cho CHUNG CU
    "bao_tri_nam": 0.005,          # 0,5% gia tri tai san/nam
    "moi_gioi_cho_thue": 0.042,    # ~0,5 thang tien thue moi nam
}


def net_yield(gia_ban_m2: float, gia_thue_m2: float, la_chung_cu: bool) -> dict:
    """Tinh tren 1 m² cho gon — ti suat khong doi theo dien tich."""
    thue_gop_nam = gia_thue_m2 * 12
    thue_thuc = thue_gop_nam * (1 - GD["bo_trong_thang"] / 12)

    tru_thue = thue_thuc * GD["thue_cho_thue"]
    tru_moi_gioi = thue_thuc * GD["moi_gioi_cho_thue"]
    tru_quan_ly = GD["phi_quan_ly_m2_thang"] * 12 if la_chung_cu else 0.0
    tru_bao_tri = gia_ban_m2 * GD["bao_tri_nam"]

    thu_rong = thue_thuc - tru_thue - tru_moi_gioi - tru_quan_ly - tru_bao_tri
    return {
        "ti_suat_gop": thue_gop_nam / gia_ban_m2 * 100,
        "ti_suat_rong": thu_rong / gia_ban_m2 * 100,
        "thu_rong_m2_nam": thu_rong,
        "chi_phi_an_pct": (thue_gop_nam - thu_rong) / thue_gop_nam * 100,
    }


cells = json.loads((OUTDIR / "yield_by_district_size.json").read_text(encoding="utf-8"))
wards = json.loads((OUTDIR / "yield_by_ward.json").read_text(encoding="utf-8"))

for c in cells + wards:
    r = net_yield(c["gia_ban_m2"], c["gia_thue_m2"], c["category_name"].startswith("Căn hộ"))
    c.update(r)

gop = [c["ti_suat_gop"] for c in cells]
rong = [c["ti_suat_rong"] for c in cells]
NY = st.median(rong)          # ti suat rong dai dien
NG = st.median(gop)

print("=" * 74)
print("GIA DINH DANG DUNG")
for k, v in GD.items():
    print(f"   {k:<24} {v}")

print("=" * 74)
print("1) TU TI SUAT GOP SANG TI SUAT RONG")
print(f"   Ti suat GOP  (trung vi) : {NG:6.2f} %/nam")
print(f"   Ti suat RONG (trung vi) : {NY:6.2f} %/nam")
print(f"   Chi phi an nuot mat     : {st.median([c['chi_phi_an_pct'] for c in cells]):6.1f}% tien thue")
print(f"   So nam thu hoi von      : {100 / NY:6.1f} nam  (chi tinh tien thue, khong tinh tang gia)")

print("=" * 74)
print("2) SO VOI GUI TIET KIEM")
lts = GD["lai_tiet_kiem"] * 100
print(f"   Cho thue (rong)         : {NY:6.2f} %/nam")
print(f"   Gui tiet kiem           : {lts:6.2f} %/nam")
print(f"   => Gui ngan hang hon    : {lts - NY:6.2f} diem %/nam  (gap {lts / NY:.1f} lan)")

print("=" * 74)
print("3) KICH BAN DI VAY  (vay {:.0%} gia tri, lai {:.1%})".format(
    GD["ty_le_vay"], GD["lai_vay_tha_noi"]))
chi_phi_vay = GD["ty_le_vay"] * GD["lai_vay_tha_noi"] * 100     # % gia tri nha/nam
dong_tien = NY - chi_phi_vay
print(f"   Thu tu cho thue (rong)  : {NY:+6.2f} % gia tri nha/nam")
print(f"   Tra lai vay             : {-chi_phi_vay:+6.2f} % gia tri nha/nam")
print(f"   => DONG TIEN            : {dong_tien:+6.2f} % gia tri nha/nam")

print("=" * 74)
print("4) GIA PHAI TANG BAO NHIEU %/NAM MOI HOA VON?")
kb_a = lts - NY
kb_b = chi_phi_vay - NY
kb_c = chi_phi_vay + (1 - GD["ty_le_vay"]) * lts - NY
print(f"   A. Mua tien mat, chi can bang gui tiet kiem : {kb_a:5.2f} %/nam")
print(f"   B. Vay {GD['ty_le_vay']:.0%}, chi can khong lo tien            : {kb_b:5.2f} %/nam")
print(f"   C. Vay {GD['ty_le_vay']:.0%}, va bang gui tiet kiem           : {kb_c:5.2f} %/nam")

# ------------------------------------------------- vi du cu the mot can ho
apt = [c for c in cells if c["category_name"].startswith("Căn hộ") and c["size_bucket"] == "60-80"]
if apt:
    m2 = 70
    gia_m2 = st.median([c["gia_ban_m2"] for c in apt])
    thue_m2 = st.median([c["gia_thue_m2"] for c in apt])
    gia = gia_m2 * m2
    r = net_yield(gia_m2, thue_m2, True)
    vay = gia * GD["ty_le_vay"]
    lai_thang = vay * GD["lai_vay_tha_noi"] / 12
    thu_thang = r["thu_rong_m2_nam"] * m2 / 12
    print("=" * 74)
    print(f"VI DU CU THE — can ho {m2} m² (trung vi thi truong)")
    print(f"   Gia mua                 : {gia:>16,.0f} d")
    print(f"   Tien thue gop/thang     : {thue_m2 * m2:>16,.0f} d")
    print(f"   Thu RONG/thang          : {thu_thang:>16,.0f} d")
    print(f"   Vay {GD['ty_le_vay']:.0%} = {vay:,.0f} d, lai {GD['lai_vay_tha_noi']:.0%}")
    print(f"   Tra lai/thang           : {-lai_thang:>16,.0f} d")
    print(f"   => MOI THANG BU LO      : {thu_thang - lai_thang:>16,.0f} d")
    print(f"   Neu gui {gia:,.0f} d vao ngan hang: {gia * GD['lai_tiet_kiem'] / 12:,.0f} d/thang")

print("=" * 74)
print("XEP HANG QUAN — ti suat RONG")
byd = defaultdict(list)
for c in cells:
    byd[c["district_name"]].append(c["ti_suat_rong"])
for med, name in sorted(((st.median(v), k) for k, v in byd.items()), reverse=True):
    thieu = lts - med
    print(f"   {name:<26} {med:5.2f} %/nam   (thua tiet kiem {thieu:4.2f} diem)")

ket_qua = {
    "gia_dinh": GD,
    "ti_suat_gop_trung_vi": round(NG, 3),
    "ti_suat_rong_trung_vi": round(NY, 3),
    "lai_tiet_kiem_pct": lts,
    "chenh_lech_diem": round(lts - NY, 3),
    "so_nam_thu_hoi_von": round(100 / NY, 1),
    "dong_tien_khi_vay_pct": round(dong_tien, 3),
    "tang_gia_can_thiet": {
        "mua_tien_mat_bang_tiet_kiem": round(kb_a, 3),
        "vay_khong_lo": round(kb_b, 3),
        "vay_bang_tiet_kiem": round(kb_c, 3),
    },
}
(OUTDIR / "financial_summary.json").write_text(
    json.dumps(ket_qua, ensure_ascii=False, indent=2), encoding="utf-8")
(OUTDIR / "yield_by_district_size.json").write_text(
    json.dumps(cells, ensure_ascii=False, indent=2), encoding="utf-8")
(OUTDIR / "yield_by_ward.json").write_text(
    json.dumps(wards, ensure_ascii=False, indent=2), encoding="utf-8")
print("=" * 74)
print("Da ghi data/output/financial_summary.json (+ cap nhat 2 file ti suat)")
