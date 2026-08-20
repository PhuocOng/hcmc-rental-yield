"""Buoc 3b — Khoang tin cay bang bootstrap cho moi o va moi quan.

Vi sao can: ti suat cua mot o = trung vi gia thue chia trung vi gia ban, tinh tren
it khi chi 10-15 tin moi ben. Con so do CO SAI SO, va truoc day trang web khong he
the hien dieu do — hien "2,57%" toi hai chu so thap phan nhu the la su that.

Cach lam: lay mau co hoan lai tu chinh danh sach tin cua o, tinh lai ti suat, lap
600 lan, roi lay phan vi 2,5% va 97,5%.

Chay: python src/bootstrap_ci.py
"""
from __future__ import annotations
import json, random, statistics as st, sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
N_BOOT = 600
random.seed(20260815)

fin = json.loads((OUT / "financial_summary.json").read_text(encoding="utf-8"))
GD = fin["gia_dinh"]

def net_pct(sale_m2: float, rent_m2: float, chung_cu: bool) -> float:
    """Giong het cong thuc trong financial_layer.py — giu dong bo."""
    thuc = rent_m2 * 12 * (1 - GD["bo_trong_thang"] / 12)
    ql = GD["phi_quan_ly_m2_thang"] * 12 if chung_cu else 0.0
    rong = thuc - thuc * GD["thue_cho_thue"] - thuc * GD["moi_gioi_cho_thue"] \
           - ql - sale_m2 * GD["bao_tri_nam"]
    return rong / sale_m2 * 100

def boot(ban: list, thue: list, chung_cu: bool) -> tuple:
    gop, rong = [], []
    for _ in range(N_BOOT):
        s = st.median(random.choices(ban, k=len(ban)))
        t = st.median(random.choices(thue, k=len(thue)))
        gop.append(t * 12 / s * 100)
        rong.append(net_pct(s, t, chung_cu))
    gop.sort(); rong.sort()
    i, j = int(N_BOOT * .025), int(N_BOOT * .975) - 1
    return gop[i], gop[j], rong[i], rong[j]

rows = [json.loads(l) for l in (ROOT / "data/interim/clean_hcm.jsonl").open(encoding="utf-8")]
BUCKETS = [(0,40),(40,60),(60,80),(80,120),(120,200),(200,10**9)]
def bucket(s):
    for lo,hi in BUCKETS:
        if lo <= s < hi: return f"{lo}-{hi if hi<10**9 else '+'}"
    return "?"

# ---------------------------------------------------- o phuong x danh muc
cw = defaultdict(lambda: {"ban": [], "thue": []})
for r in rows:
    cw[(r["ward"], r["category"])][r["deal"]].append(r["price_per_m2"])

wards = json.loads((OUT / "yield_by_ward.json").read_text(encoding="utf-8"))
for w in wards:
    v = cw[(w["ward"], 1010 if w["category_name"].startswith("Căn hộ") else 1020)]
    if len(v["ban"]) < 10 or len(v["thue"]) < 10:
        continue
    g0,g1,r0,r1 = boot(v["ban"], v["thue"], w["category_name"].startswith("Căn hộ"))
    w.update(gop_lo=g0, gop_hi=g1, rong_lo=r0, rong_hi=r1,
             ci_rong=r1-r0, n_yeu=min(len(v["ban"]), len(v["thue"])))
(OUT / "yield_by_ward.json").write_text(json.dumps(wards, ensure_ascii=False, indent=1),
                                        encoding="utf-8")

# ------------------------------------- o quan x danh muc x nhom dien tich
cd = defaultdict(lambda: {"ban": [], "thue": []})
for r in rows:
    cd[(r["district"], r["category"], bucket(r["size_m2"]))][r["deal"]].append(r["price_per_m2"])

cells = json.loads((OUT / "yield_by_district_size.json").read_text(encoding="utf-8"))
keyed = {}
for c in cells:
    cat = 1010 if c["category_name"].startswith("Căn hộ") else 1020
    k = (c["district"], cat, c["size_bucket"])
    keyed[k] = c
    v = cd[k]
    g0,g1,r0,r1 = boot(v["ban"], v["thue"], cat == 1010)
    c.update(gop_lo=g0, gop_hi=g1, rong_lo=r0, rong_hi=r1, ci_rong=r1-r0)
(OUT / "yield_by_district_size.json").write_text(json.dumps(cells, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")

# ------------------------------------------------ quan: bootstrap hai tang
bydist = defaultdict(list)
for k, c in keyed.items():
    bydist[c["district_name"]].append((k, c["category_name"].startswith("Căn hộ")))

out = []
for name, keys in bydist.items():
    gs, rs = [], []
    for _ in range(N_BOOT):
        g, r = [], []
        for k, cc in keys:
            v = cd[k]
            s = st.median(random.choices(v["ban"], k=len(v["ban"])))
            t = st.median(random.choices(v["thue"], k=len(v["thue"])))
            g.append(t * 12 / s * 100); r.append(net_pct(s, t, cc))
        gs.append(st.median(g)); rs.append(st.median(r))
    gs.sort(); rs.sort()
    i, j = int(N_BOOT*.025), int(N_BOOT*.975)-1
    out.append({"ten": name, "n_o": len(keys),
                "gop": st.median([keyed[k]["ti_suat_gop"] for k,_ in keys]),
                "rong": st.median([keyed[k]["ti_suat_rong"] for k,_ in keys]),
                "gop_lo": gs[i], "gop_hi": gs[j], "rong_lo": rs[i], "rong_hi": rs[j],
                "n": sum(keyed[k]["n_ban"] + keyed[k]["n_thue"] for k,_ in keys)})
out.sort(key=lambda d: -d["rong"])
(OUT / "district_ci.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                      encoding="utf-8")

print(f"{len(wards)} o phuong · {len(cells)} o quan-dien-tich · {len(out)} quan\n")
w = [x["rong_hi"] - x["rong_lo"] for x in out]
print(f"Do rong KTC cap QUAN: trung vi {st.median(w):.2f} diem  "
      f"(min {min(w):.2f}, max {max(w):.2f})")
print("\nXep hang quan kem khoang tin cay (ti suat RONG):")
for d in out:
    print(f"  {d['ten']:<24} {d['rong']:5.2f}%  [{d['rong_lo']:4.2f} – {d['rong_hi']:4.2f}]  ({d['n_o']} o)")

top, bot = out[0], out[-1]
print(f"\nQuan cao nhat vs thap nhat co tach nhau khong? "
      f"{'CO' if top['rong_lo'] > bot['rong_hi'] else 'KHONG'}")
