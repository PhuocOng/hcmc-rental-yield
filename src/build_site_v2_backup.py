"""Buoc 4 — Dung website.

v2: bo bo cuc kieu bai bao, chuyen sang bo cuc BANG DIEU KHIEN du lieu:
thanh chi so o dau, cac panel xep theo luoi, bieu do SVG co truc va thanh sai so,
bang du lieu day. Bang mau lay theo Tableau 10.

Chay: python src/build_site.py   ->  web/index.html
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
WEB = ROOT / "web"

fin = json.loads((OUT / "financial_summary.json").read_text(encoding="utf-8"))
cells = json.loads((OUT / "yield_by_district_size.json").read_text(encoding="utf-8"))
wards = json.loads((OUT / "yield_by_ward.json").read_text(encoding="utf-8"))
clean = json.loads((OUT / "clean_report.json").read_text(encoding="utf-8"))
dists = json.loads((OUT / "district_ci.json").read_text(encoding="utf-8"))
mapgeo = json.loads((OUT / "hcm_geo.json").read_text(encoding="utf-8"))
mapbounds = json.loads((OUT / "hcm_bounds.json").read_text(encoding="utf-8"))

GD, LTS = fin["gia_dinh"], fin["lai_tiet_kiem_pct"]
NGAY = "15/08/2026"

r2 = lambda x: round(x, 2)
DATA = {
    "gd": GD, "lts": LTS,
    "dist": [{"ten": d["ten"], "rong": r2(d["rong"]), "gop": r2(d["gop"]),
              "lo": r2(d["rong_lo"]), "hi": r2(d["rong_hi"]), "n": d["n"], "no": d["n_o"]}
             for d in dists],
    # o quan x loai hinh x dien tich — dung cho bieu do phan tan va bo chon cua may tinh
    "cells": [{"q": c["district_name"], "c": c["category_name"], "d": c["size_bucket"],
               "ban": round(c["gia_ban_m2"]), "thue": round(c["gia_thue_m2"]),
               "gop": r2(c["ti_suat_gop"]), "rong": r2(c["ti_suat_rong"]),
               "lo": r2(c.get("rong_lo", c["ti_suat_rong"])),
               "hi": r2(c.get("rong_hi", c["ti_suat_rong"])),
               "nb": c["n_ban"], "nt": c["n_thue"]} for c in cells],
    "wards": [{"p": w["ward_name"], "q": w["district_name"], "c": w["category_name"],
               "ban": round(w["gia_ban_m2"] / 1e6, 1), "thue": round(w["gia_thue_m2"] / 1e3),
               "gop": r2(w["ti_suat_gop"]), "rong": r2(w["ti_suat_rong"]),
               "lo": r2(w.get("rong_lo", w["ti_suat_rong"])),
               "hi": r2(w.get("rong_hi", w["ti_suat_rong"])),
               "nb": w["n_ban"], "nt": w["n_thue"]}
              for w in sorted(wards, key=lambda x: -x["ti_suat_rong"])],
    "geo": mapgeo, "bounds": mapbounds,
    "kpi": {"rong": r2(fin["ti_suat_rong_trung_vi"]), "gop": r2(fin["ti_suat_gop_trung_vi"]),
            "nam": round(fin["so_nam_thu_hoi_von"]), "chenh": r2(fin["chenh_lech_diem"]),
            "tang": r2(fin["tang_gia_can_thiet"]["vay_bang_tiet_kiem"])},
    "n": {"raw": clean["tong_dong_vao"], "clean": clean["giu_lai"], "pct": clean["ty_le_giu"]},
}

# do rong khoang tin cay dien hinh — dung trong phan Phuong phap
CI_W = st.median([d["rong_hi"] - d["rong_lo"] for d in dists])

HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tỉ suất cho thuê bất động sản TP.HCM</title>
<meta name="description" content="Bảng phân tích 45.084 tin rao bán và cho thuê tại TP.HCM: tỉ suất cho thuê ròng 1,51%/năm so với lãi tiết kiệm 6,0%.">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>
<style>
:root{
  /* bang mau Tableau 10 */
  --t-blue:#4E79A7; --t-orange:#F28E2B; --t-red:#E15759; --t-teal:#76B7B2;
  --t-green:#59A14F; --t-grey:#BAB0AC;
  --page:#F2F2F2; --panel:#FFF; --line:#DCDCDC; --line2:#EDEDED;
  --ink:#1B1B1B; --ink2:#5A5A5A; --ink3:#8C8C8C;
  --pos:#59A14F; --neg:#E15759;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{--page:#131417;--panel:#1A1C20;--line:#2C2F35;--line2:#24262B;
        --ink:#E8E8EA;--ink2:#A0A4AB;--ink3:#71767E;
        --t-blue:#6E9BC9; --t-orange:#F2A44F; --t-red:#E8756F; --t-green:#6DB863;
        --pos:#6DB863;--neg:#E8756F}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);
  font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
h1,h2,h3{margin:0;font-weight:600;letter-spacing:-.01em}
p{margin:0 0 10px}
a{color:var(--t-blue)}
.num{font-variant-numeric:tabular-nums}

/* ---------- khung ---------- */
.app{max-width:1320px;margin:0 auto;padding:0 16px 60px}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:12px}
.c12{grid-column:span 12}.c8{grid-column:span 8}.c6{grid-column:span 6}
.c5{grid-column:span 5}.c4{grid-column:span 4}.c7{grid-column:span 7}
@media(max-width:1000px){.c8,.c6,.c5,.c4,.c7{grid-column:span 12}}

/* ---------- thanh tren ---------- */
.top{position:sticky;top:0;z-index:900;background:var(--panel);
  border-bottom:1px solid var(--line);margin-bottom:12px}
.top .in{max-width:1320px;margin:0 auto;padding:11px 16px;display:flex;
  align-items:baseline;gap:14px;flex-wrap:wrap}
.top h1{font-size:15px}
.top .tag{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3);
  border:1px solid var(--line);border-radius:2px;padding:2px 6px}
.top .sp{margin-left:auto;font-size:11.5px;color:var(--ink3);display:flex;gap:16px;flex-wrap:wrap}
.top .sp b{color:var(--ink2);font-weight:600}

/* ---------- panel ---------- */
.p{background:var(--panel);border:1px solid var(--line);border-radius:3px;
  display:flex;flex-direction:column;min-width:0}
.ph{padding:9px 13px;border-bottom:1px solid var(--line2);display:flex;
  align-items:baseline;gap:9px;flex-wrap:wrap}
.ph h2{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink2)}
.ph .hint{font-size:11.5px;color:var(--ink3);margin-left:auto}
.pb{padding:13px;flex:1;min-width:0}
.pb.tight{padding:0}

/* ---------- the chi so ---------- */
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:12px}
@media(max-width:1000px){.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.kpis{grid-template-columns:1fr}}
.k{background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:12px 14px}
.k .lb{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);
  margin-bottom:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.k .v{font-size:29px;font-weight:600;line-height:1.05;letter-spacing:-.02em}
.k .v small{font-size:14px;font-weight:500;color:var(--ink2);margin-left:2px}
.k .ci{font-size:11px;color:var(--ink3);margin-top:5px;font-family:var(--mono)}
.k.acc{border-left:3px solid var(--t-red)}
.k.acc2{border-left:3px solid var(--t-green)}

/* ---------- bieu do ---------- */
svg.chart{display:block;width:100%;overflow:visible}
.ax{stroke:var(--line);stroke-width:1}
.gl{stroke:var(--line2);stroke-width:1;shape-rendering:crispEdges}
.tk{fill:var(--ink3);font-size:10.5px}
.lbl{fill:var(--ink2);font-size:11.5px}
.val{fill:var(--ink);font-size:11.5px;font-weight:600}
.refl{stroke:var(--t-green);stroke-width:1.5;stroke-dasharray:5 3}
.reft{fill:var(--t-green);font-size:10.5px;font-weight:600}
.whisk{stroke:var(--ink3);stroke-width:1.2;opacity:.85}
.barr{fill:var(--t-blue)}
.barr:hover{fill:var(--t-orange)}
.dot{stroke:var(--panel);stroke-width:.8;cursor:pointer}
.dot:hover{stroke:var(--ink);stroke-width:1.6}

/* ---------- chu thich / bo loc ---------- */
.lg{display:flex;gap:14px;align-items:center;font-size:11.5px;color:var(--ink2);flex-wrap:wrap}
.lg i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;
  vertical-align:0}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.seg button{font:inherit;font-size:11.5px;padding:3px 10px;border:0;cursor:pointer;
  background:var(--panel);color:var(--ink2);border-right:1px solid var(--line)}
.seg button:last-child{border-right:0}
.seg button[aria-pressed=true]{background:var(--t-blue);color:#fff}

/* ---------- bang ---------- */
.tw{overflow:auto;max-height:400px}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:12.5px}
thead th{position:sticky;top:0;background:var(--panel);z-index:1;text-align:left;
  padding:8px 10px;border-bottom:1px solid var(--line);font-size:10.5px;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);font-weight:600;
  cursor:pointer;white-space:nowrap;user-select:none}
thead th:hover{color:var(--ink)}
thead th .ar{opacity:.45;font-size:9px}
tbody td{padding:6px 10px;border-bottom:1px solid var(--line2);white-space:nowrap}
tbody tr:hover td{background:color-mix(in srgb,var(--t-blue) 7%,transparent)}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.cimini{display:inline-block;width:52px;height:5px;background:var(--line2);border-radius:2px;
  position:relative;vertical-align:middle;margin-left:6px}
.cimini i{position:absolute;top:0;bottom:0;background:var(--t-blue);opacity:.55;border-radius:2px}
.thin{color:var(--ink3)}

/* ---------- may tinh ---------- */
.cf{display:grid;grid-template-columns:repeat(4,1fr);gap:11px 16px}
@media(max-width:860px){.cf{grid-template-columns:repeat(2,1fr)}}
label{display:block;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:4px}
label .rv{float:right;text-transform:none;letter-spacing:0;font-size:11.5px;color:var(--ink);
  font-family:var(--mono)}
input[type=text],select{width:100%;padding:6px 8px;font:inherit;font-size:13px;
  border:1px solid var(--line);border-radius:3px;background:var(--panel);color:var(--ink)}
input[type=range]{width:100%;accent-color:var(--t-blue);margin:5px 0 0}
.res{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:14px;
  border:1px solid var(--line);border-radius:3px;overflow:hidden}
@media(max-width:860px){.res{grid-template-columns:1fr 1fr}}
.res div{padding:10px 12px;border-right:1px solid var(--line2);border-bottom:1px solid var(--line2)}
.res .rl{font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink3);
  margin-bottom:5px}
.res .rv2{font-size:19px;font-weight:600}
.vd{margin-top:12px;padding:11px 13px;border-radius:3px;font-size:13px;line-height:1.6;
  background:color-mix(in srgb,var(--t-red) 8%,transparent);
  border:1px solid color-mix(in srgb,var(--t-red) 25%,transparent)}

/* ---------- ban do ---------- */
#map{width:100%;height:430px;background:#0d1117}
.leaflet-container{font:inherit;background:#0d1117}
.leaflet-control-attribution{font-size:9.5px!important;background:rgba(0,0,0,.5)!important;color:#bbb!important}
.leaflet-control-attribution a{color:#9ec5ff!important}
.mwrap{position:relative}
.mbtn{position:absolute;left:9px;top:9px;z-index:500;display:flex;gap:5px}
.mbtn button{font:inherit;font-size:11.5px;padding:4px 9px;border-radius:3px;cursor:pointer;
  border:1px solid rgba(255,255,255,.25);background:rgba(15,15,15,.8);color:#eee}
.mbtn button:hover{background:rgba(45,45,45,.9)}
.mlg{position:absolute;left:9px;bottom:20px;z-index:500;background:rgba(15,15,15,.8);
  border:1px solid rgba(255,255,255,.16);border-radius:3px;padding:7px 9px;color:#eee;font-size:10.5px}
.mlg .b{display:block;height:7px;width:150px;border-radius:2px;margin:4px 0 3px;
  background:linear-gradient(90deg,#7d1d16,#F28E2B,#EDC948)}
.mlg .r{display:flex;justify-content:space-between;font-family:var(--mono)}
.dtip{background:#16181c;color:#f0f0f0;border:1px solid rgba(255,255,255,.2);border-radius:3px;
  padding:7px 9px;font-size:12px;line-height:1.5}
.ping{width:13px;height:13px;border-radius:50%;background:#EDC948;
  box-shadow:0 0 0 2px rgba(255,255,255,.9);position:relative}
.ping::after{content:"";position:absolute;inset:-5px;border:2px solid #EDC948;border-radius:50%;
  animation:pl 1.7s ease-out infinite}
@keyframes pl{0%{transform:scale(.55);opacity:1}100%{transform:scale(2.6);opacity:0}}
.pinglbl{position:absolute;left:19px;top:-3px;white-space:nowrap;color:#fff;font-size:12px;
  font-weight:600;text-shadow:0 1px 4px #000}

/* ---------- van ban ---------- */
.prose{font-size:13px;line-height:1.7;color:var(--ink2);max-width:74ch}
.prose b,.prose strong{color:var(--ink)}
.prose h3{font-size:12.5px;color:var(--ink);margin:16px 0 5px}
.prose h3:first-child{margin-top:0}
.prose ul{margin:0 0 10px;padding-left:18px}
.prose li{margin-bottom:4px}
details{border-top:1px solid var(--line2);padding:9px 0}
details:first-of-type{border-top:0}
summary{cursor:pointer;font-size:12.5px;font-weight:600;color:var(--ink)}
details p{margin:7px 0 0;font-size:12.5px;line-height:1.65;color:var(--ink2)}
.kv{width:100%;font-size:12.5px}
.kv td{padding:4px 0;border-bottom:1px solid var(--line2)}
.kv td:last-child{text-align:right;font-family:var(--mono);color:var(--ink)}
code{font-family:var(--mono);font-size:11.5px;background:var(--page);padding:1px 4px;
  border-radius:2px;border:1px solid var(--line2)}
footer{margin-top:16px;padding:14px 2px;font-size:11.5px;color:var(--ink3);
  border-top:1px solid var(--line)}
</style>
</head>
<body>

<div class="top"><div class="in">
  <h1>Tỉ suất cho thuê bất động sản TP.HCM</h1>
  <span class="tag">Chợ Tốt · __NGAY__</span>
  <div class="sp">
    <span><b>__NCLEAN__</b> tin sau lọc</span>
    <span><b>__NRAW__</b> tin thô</span>
    <span><b>20</b> quận · <b>__NW__</b> ô phường</span>
  </div>
</div></div>

<div class="app">

  <div class="kpis">
    <div class="k acc">
      <div class="lb">Tỉ suất ròng</div>
      <div class="v" id="k1">—<small>%/năm</small></div>
      <div class="ci" id="k1c"></div>
    </div>
    <div class="k">
      <div class="lb">Tỉ suất gộp</div>
      <div class="v" id="k2">—<small>%/năm</small></div>
      <div class="ci">trước thuế, phí, bỏ trống</div>
    </div>
    <div class="k acc2">
      <div class="lb">Gửi tiết kiệm 12 tháng</div>
      <div class="v" id="k3">—<small>%/năm</small></div>
      <div class="ci">Big4 tại quầy, 08/2026</div>
    </div>
    <div class="k">
      <div class="lb">Chênh lệch</div>
      <div class="v" id="k4">—<small>điểm %</small></div>
      <div class="ci">gửi ngân hàng hơn</div>
    </div>
    <div class="k">
      <div class="lb">Số năm hoàn vốn</div>
      <div class="v" id="k5">—<small>năm</small></div>
      <div class="ci">chỉ tính tiền thuê</div>
    </div>
  </div>

  <div class="grid">

    <div class="p c7">
      <div class="ph"><h2>Bản đồ tỉ suất ròng theo quận</h2>
        <span class="hint">kéo · lăn để phóng · bấm để nhảy tới</span></div>
      <div class="pb tight mwrap">
        <div id="map"></div>
        <div class="mbtn"><button id="b_vn">Toàn Việt Nam</button><button id="b_hcm">Về TP.HCM</button></div>
        <div class="mlg"><div>Tỉ suất ròng %/năm</div><span class="b"></span>
          <div class="r"><span id="lg_lo"></span><span id="lg_hi"></span></div></div>
      </div>
    </div>

    <div class="p c5">
      <div class="ph"><h2>Xếp hạng quận</h2>
        <span class="hint">thanh ngang = khoảng tin cậy 95%</span></div>
      <div class="pb"><svg id="ch_rank" class="chart"></svg></div>
    </div>

    <div class="p c7">
      <div class="ph"><h2>Giá bán và tỉ suất</h2>
        <div class="seg" id="segcat">
          <button data-c="all" aria-pressed="true">Tất cả</button>
          <button data-c="Căn hộ/Chung cư" aria-pressed="false">Căn hộ</button>
          <button data-c="Nhà ở" aria-pressed="false">Nhà ở</button>
        </div>
        <span class="hint">mỗi điểm = một ô quận×diện tích</span></div>
      <div class="pb"><svg id="ch_scat" class="chart"></svg>
        <div class="lg" style="margin-top:8px">
          <span><i style="background:var(--t-blue)"></i>Căn hộ/Chung cư</span>
          <span><i style="background:var(--t-orange)"></i>Nhà ở</span>
          <span class="thin">kích thước điểm ∝ số tin</span>
        </div>
      </div>
    </div>

    <div class="p c5">
      <div class="ph"><h2>Phân bố tỉ suất theo phường</h2>
        <span class="hint">__NW__ ô</span></div>
      <div class="pb"><svg id="ch_hist" class="chart"></svg></div>
    </div>

    <div class="p c12">
      <div class="ph"><h2>Máy tính đầu tư</h2>
        <span class="hint">chọn một ô thị trường hoặc tự nhập — mọi giả định đều chỉnh được</span></div>
      <div class="pb">
        <div class="cf">
          <div><label>Chọn ô thị trường</label><select id="sel"></select></div>
          <div><label>Giá mua</label><input type="text" id="gia" inputmode="numeric"></div>
          <div><label>Tiền thuê mỗi tháng</label><input type="text" id="thue" inputmode="numeric"></div>
          <div><label>Vay <span class="rv" id="vv"></span></label><input type="range" id="vay" min="0" max="90" step="5"></div>
          <div><label>Lãi suất vay <span class="rv" id="lvv"></span></label><input type="range" id="lv" min="6" max="18" step="0.5"></div>
          <div><label>Lãi tiết kiệm <span class="rv" id="ltv"></span></label><input type="range" id="lt" min="3" max="10" step="0.1"></div>
          <div><label>Bỏ trống <span class="rv" id="btv"></span></label><input type="range" id="bt" min="0" max="4" step="0.5"></div>
          <div><label>Phí quản lý + bảo trì <span class="rv" id="bhv"></span></label><input type="range" id="bh" min="0" max="4" step="0.1"></div>
        </div>
        <div class="res">
          <div><div class="rl">Tỉ suất gộp</div><div class="rv2" id="o_gop"></div></div>
          <div><div class="rl">Tỉ suất ròng</div><div class="rv2" id="o_rong"></div></div>
          <div><div class="rl">Số năm hoàn vốn</div><div class="rv2" id="o_nam"></div></div>
          <div><div class="rl">Dòng tiền mỗi tháng khi vay</div><div class="rv2" id="o_dt"></div></div>
          <div><div class="rl">Nếu gửi ngân hàng</div><div class="rv2" id="o_nh"></div></div>
          <div><div class="rl">Giá phải tăng mỗi năm để hòa vốn</div><div class="rv2" id="o_tang"></div></div>
        </div>
        <div class="vd" id="verdict"></div>
      </div>
    </div>

    <div class="p c12">
      <div class="ph"><h2>Dữ liệu theo phường</h2>
        <span class="hint">bấm tiêu đề cột để sắp xếp · ô ít tin được làm mờ</span></div>
      <div class="pb tight"><div class="tw"><table id="wt">
        <thead><tr>
          <th data-k="p">Phường</th><th data-k="q">Quận</th><th data-k="c">Loại hình</th>
          <th data-k="ban" class="n">Giá bán<br><span class="thin">tr/m²</span></th>
          <th data-k="thue" class="n">Giá thuê<br><span class="thin">ngh/m²/th</span></th>
          <th data-k="gop" class="n">Gộp<br><span class="thin">%/năm</span></th>
          <th data-k="rong" class="n">Ròng<br><span class="thin">%/năm</span></th>
          <th data-k="lo" class="n">Khoảng tin cậy 95%</th>
          <th data-k="nb" class="n">Tin<br><span class="thin">bán/thuê</span></th>
        </tr></thead><tbody></tbody>
      </table></div></div>
    </div>

    <div class="p c6">
      <div class="ph"><h2>Phương pháp</h2></div>
      <div class="pb prose">
        <h3>Ghép theo ô, không lấy trung bình cả quận</h3>
        <p>Lấy giá bán trung bình một quận chia cho tiền thuê trung bình quận đó là sai: tin rao bán
        nghiêng về nhà phố lớn, tin cho thuê nghiêng về căn hộ nhỏ. Mọi so sánh ở đây chỉ thực hiện
        <b>trong cùng một ô</b> — cùng phường (hoặc quận), cùng loại hình, cùng tầm diện tích — và
        dùng <b>trung vị giá trên mỗi m²</b> của từng bên.</p>

        <h3>Khoảng tin cậy</h3>
        <p>Mỗi ô chỉ có vài chục tin, nên tỉ suất tính ra <b>có sai số</b>. Khoảng tin cậy 95% được
        ước lượng bằng <b>bootstrap</b>: lấy mẫu có hoàn lại từ chính danh sách tin của ô, tính lại
        tỉ suất, lặp 600 lần. Ở cấp quận, khoảng tin cậy rộng trung vị <b>__CIW__ điểm %</b>.
        Vì vậy <b>thứ hạng giữa các quận ở nhóm giữa không tách bạch</b> — chỉ hai đầu bảng là
        phân biệt được có ý nghĩa.</p>

        <h3>Tự kiểm tra chéo</h3>
        <p>Tỉ suất gộp tính độc lập theo hai cách: theo <i>phường × loại hình</i> ra 2,57%/năm, theo
        <i>quận × loại hình × nhóm diện tích</i> ra 2,61%/năm. Hai con số gần trùng nhau, nghĩa là
        kết quả không đến từ chênh lệch cơ cấu diện tích giữa hai phía.</p>

        <h3>Làm sạch</h3>
        <p>Từ __NRAW__ tin thô còn __NCLEAN__ tin (__PCT__%). Bị loại:</p>
        <table class="kv"><tbody>__REJECTS__</tbody></table>

        <h3>Giả định mặc định</h3>
        <table class="kv"><tbody>
        <tr><td>Lãi tiết kiệm 12 tháng</td><td>6,0%/năm</td></tr>
        <tr><td>Lãi vay thả nổi</td><td>12,0%/năm</td></tr>
        <tr><td>Tỉ lệ vay</td><td>70%</td></tr>
        <tr><td>Bỏ trống</td><td>1 tháng/năm</td></tr>
        <tr><td>Thuế cho thuê</td><td>10% doanh thu</td></tr>
        <tr><td>Phí quản lý chung cư</td><td>15.000 đ/m²/tháng</td></tr>
        <tr><td>Bảo trì</td><td>0,5% giá trị/năm</td></tr>
        </tbody></table>
      </div>
    </div>

    <div class="p c6">
      <div class="ph"><h2>Giới hạn</h2><span class="hint">đọc trước khi trích dẫn</span></div>
      <div class="pb prose">
        <details open><summary>Đây là giá rao, không phải giá giao dịch</summary>
        <p>Người bán thường hét cao hơn giá chốt 5–15%, giá thuê ít mặc cả hơn, nên tỉ suất thật
        <b>cao hơn</b> con số ở đây. Nhưng để tỉ suất gộp chạm mức tiết kiệm 6%, giá rao phải cao
        hơn giá bán thật tới <b>53%</b> — không thị trường nào mặc cả ở mức đó.</p></details>

        <details><summary>Chưa tính chi phí giao dịch</summary>
        <p>Lệ phí trước bạ, công chứng, môi giới và thuế chuyển nhượng 2% cộng lại khoảng 5–7% cho
        một vòng mua–bán. Với kỳ nắm giữ 5 năm đó là ~1,2%/năm chưa được trừ, nên mức
        <b>tăng giá cần thiết đang bị tính thấp</b>.</p></details>

        <details><summary>So sánh một kỳ, chưa phải IRR</summary>
        <p>Đây là so sánh tĩnh một năm. Khung đúng của ngành là IRR trên kỳ nắm giữ 5–10 năm, có
        trả gốc dần, chi phí mua vào, và bán ra ở cuối kỳ. Ngoài ra lãi tiết kiệm là mốc dễ dãi —
        tài sản kém thanh khoản, có đòn bẩy, không phân tán thì mốc yêu cầu phải cao hơn.</p></details>

        <details><summary>Một nguồn, và chỉ là tin mới đăng</summary>
        <p>Toàn bộ từ Chợ Tốt. Tuổi tin trung vị chỉ <b>6 ngày</b> — API trả về tin mới đăng, không
        phải toàn bộ hàng đang chào bán, nên hàng ế nằm lâu (thường bị hét giá cao nhất) có thể
        thiếu đại diện. Con số căn hộ 3,4%/năm thấp hơn mức 4–5% mà CBRE và Savills công bố; phần
        chênh này chưa được giải thích đầy đủ.</p></details>

        <details><summary>Chưa kiểm tra hai phía có cùng loại tài sản</summary>
        <p>Trong cùng một ô, tin bán có thể nghiêng về căn hộ mới bàn giao còn tin thuê nghiêng về
        chung cư cũ. Nếu vậy thì đang lấy giá nhà mới chia cho tiền thuê nhà cũ, và tỉ suất bị kéo
        xuống một cách hệ thống.</p></details>

        <details><summary>Tên phường loạn vì sáp nhập</summary>
        <p>Nhiều phường có đuôi "(Quận 2 cũ)", 17 tên ứng với nhiều hơn một mã. Mọi tính toán dùng
        <b>mã phường</b> làm khóa, tên chỉ để hiển thị.</p></details>

        <details><summary>Một lát cắt, không phải chuỗi thời gian</summary>
        <p>Dữ liệu chụp ngày __NGAY__. Câu hỏi "giá nhà có thật sự tăng đủ để người mua hòa vốn
        không" <b>không</b> trả lời được bằng bộ dữ liệu này.</p></details>
      </div>
    </div>

  </div>

  <footer>
    Dự án học sinh · dữ liệu Chợ Tốt thu thập __NGAY__ · chỉ công bố số liệu đã tổng hợp theo phường,
    không đăng lại nội dung tin gốc · bản đồ nền Esri và CARTO · <b>không phải lời khuyên đầu tư</b>.
  </footer>
</div>

<script>
const D=__DATA__;
const $=id=>document.getElementById(id);
const nf=new Intl.NumberFormat('vi-VN');
const pc=(v,d=2)=>v.toFixed(d).replace('.',',')+'%';
const money=v=>v>=1e9?(v/1e9).toFixed(2).replace('.',',')+' tỷ'
  :v>=1e6?(v/1e6).toFixed(1).replace('.',',')+' tr':nf.format(Math.round(v))+' đ';
const cssv=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const SVGNS='http://www.w3.org/2000/svg';
/* Do be ngang tu O CHUA chu khong tu chinh svg: luc ve lan dau svg co the chua co
   kich thuoc, doc nham se lam viewBox sai ty le va chieu cao bi phong len gap may lan. */
function wOf(svg,min){const b=svg.parentElement.getBoundingClientRect().width-26;
  return Math.max(min, Math.round(b||min));}
function el(t,a={},kids=[]){const e=document.createElementNS(SVGNS,t);
  for(const k in a)e.setAttribute(k,a[k]); kids.forEach(c=>e.appendChild(c)); return e;}
function txt(s,a={}){const e=el('text',a); e.textContent=s; return e;}

/* ===================== 1. the chi so ===================== */
const K=D.kpi;
$('k1').innerHTML=pc(K.rong)+'<small>%/năm</small>'.replace('%/năm','/năm');
$('k1').innerHTML=K.rong.toFixed(2).replace('.',',')+'<small>%/năm</small>';
$('k2').innerHTML=K.gop.toFixed(2).replace('.',',')+'<small>%/năm</small>';
$('k3').innerHTML=D.lts.toFixed(1).replace('.',',')+'<small>%/năm</small>';
$('k4').innerHTML=K.chenh.toFixed(2).replace('.',',')+'<small>điểm %</small>';
$('k5').innerHTML=K.nam+'<small>năm</small>';
{const lo=Math.min(...D.dist.map(d=>d.lo)), hi=Math.max(...D.dist.map(d=>d.hi));
 $('k1c').textContent='quận thấp nhất '+pc(D.dist[D.dist.length-1].rong)
   +' · cao nhất '+pc(D.dist[0].rong);}

/* ===================== 2. bieu do xep hang ===================== */
function drawRank(){
  const s=$('ch_rank'); s.innerHTML='';
  const rows=D.dist, W=wOf(s,340), RH=19, mT=22, mB=26, mL=112, mR=40;
  const H=mT+rows.length*RH+mB;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`); s.style.height=H+'px';
  const xmax=Math.max(D.lts*1.06, ...rows.map(r=>r.hi));
  const X=v=>mL+v/xmax*(W-mL-mR);

  for(let t=0;t<=Math.floor(xmax);t++){
    s.appendChild(el('line',{class:'gl',x1:X(t),x2:X(t),y1:mT-6,y2:H-mB}));
    s.appendChild(txt(t+'%',{class:'tk',x:X(t),y:H-mB+13,'text-anchor':'middle'}));
  }
  s.appendChild(el('line',{class:'refl',x1:X(D.lts),x2:X(D.lts),y1:mT-12,y2:H-mB}));
  s.appendChild(txt('Gửi tiết kiệm '+pc(D.lts,1),
    {class:'reft',x:X(D.lts),y:mT-16,'text-anchor':'end'}));

  rows.forEach((r,i)=>{
    const y=mT+i*RH, cy=y+RH/2;
    s.appendChild(txt(r.ten.replace('Thành phố ','TP. ').replace('Huyện ','H. ').replace('Quận ','Q. '),
      {class:'lbl',x:mL-8,y:cy+4,'text-anchor':'end'}));
    const b=el('rect',{class:'barr',x:mL,y:y+4,width:Math.max(1,X(r.rong)-mL),height:RH-9,rx:1});
    b.appendChild(el('title',{},[])); b.querySelector('title').textContent=
      `${r.ten}\nRòng ${pc(r.rong)}  (KTC 95%: ${pc(r.lo)} – ${pc(r.hi)})\nGộp ${pc(r.gop)} · ${nf.format(r.n)} tin`;
    s.appendChild(b);
    s.appendChild(el('line',{class:'whisk',x1:X(r.lo),x2:X(r.hi),y1:cy,y2:cy}));
    [r.lo,r.hi].forEach(v=>s.appendChild(el('line',{class:'whisk',x1:X(v),x2:X(v),y1:cy-4,y2:cy+4})));
    s.appendChild(txt(pc(r.rong),{class:'val',x:X(r.hi)+6,y:cy+4}));
  });
}

/* ===================== 3. bieu do phan tan ===================== */
let catFilter='all';
function drawScat(){
  const s=$('ch_scat'); s.innerHTML='';
  const W=wOf(s,420), H=300, mT=14, mB=38, mL=44, mR=14;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`); s.style.height=H+'px';
  const pts=D.cells.filter(c=>catFilter==='all'||c.c===catFilter);
  const xs=pts.map(p=>p.ban/1e6), ys=pts.map(p=>p.rong);
  const x0=0, x1=Math.max(...xs)*1.05, y0=0, y1=Math.max(D.lts*1.05,...ys);
  const X=v=>mL+(v-x0)/(x1-x0)*(W-mL-mR), Y=v=>H-mB-(v-y0)/(y1-y0)*(H-mT-mB);

  for(let t=0;t<=y1;t++){
    s.appendChild(el('line',{class:'gl',x1:mL,x2:W-mR,y1:Y(t),y2:Y(t)}));
    s.appendChild(txt(t+'%',{class:'tk',x:mL-7,y:Y(t)+3.5,'text-anchor':'end'}));
  }
  const step=x1>200?50:20;
  for(let t=0;t<=x1;t+=step){
    s.appendChild(txt(t,{class:'tk',x:X(t),y:H-mB+14,'text-anchor':'middle'}));
  }
  s.appendChild(el('line',{class:'ax',x1:mL,x2:W-mR,y1:H-mB,y2:H-mB}));
  s.appendChild(el('line',{class:'refl',x1:mL,x2:W-mR,y1:Y(D.lts),y2:Y(D.lts)}));
  s.appendChild(txt('Gửi tiết kiệm '+pc(D.lts,1),{class:'reft',x:W-mR,y:Y(D.lts)-5,'text-anchor':'end'}));
  s.appendChild(txt('Giá bán, triệu đồng/m²',{class:'lbl',x:(mL+W-mR)/2,y:H-6,'text-anchor':'middle'}));
  s.appendChild(txt('Tỉ suất ròng',{class:'lbl',x:mL-34,y:mT+4,transform:`rotate(-90 ${mL-34} ${mT+4})`,'text-anchor':'end'}));

  const nmax=Math.max(...pts.map(p=>p.nb+p.nt));
  pts.forEach(p=>{
    const c=el('circle',{class:'dot',cx:X(p.ban/1e6),cy:Y(p.rong),
      r:3+Math.sqrt((p.nb+p.nt)/nmax)*7,
      fill:p.c.startsWith('Căn hộ')?cssv('--t-blue'):cssv('--t-orange'),
      'fill-opacity':.62});
    const t=el('title'); t.textContent=
      `${p.q} · ${p.c} · ${p.d} m²\nRòng ${pc(p.rong)} (KTC ${pc(p.lo)}–${pc(p.hi)})\n`+
      `Bán ${(p.ban/1e6).toFixed(1)} tr/m² · Thuê ${nf.format(Math.round(p.thue/1e3))} ngh/m²/th\n`+
      `${p.nb} tin bán · ${p.nt} tin thuê`;
    c.appendChild(t); s.appendChild(c);
  });
}
$('segcat').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b)return;
  catFilter=b.dataset.c;
  [...$('segcat').children].forEach(x=>x.setAttribute('aria-pressed',x===b));
  drawScat();
});

/* ===================== 4. bieu do phan bo ===================== */
function drawHist(){
  const s=$('ch_hist'); s.innerHTML='';
  const W=wOf(s,320), H=300, mT=14, mB=38, mL=32, mR=12;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`); s.style.height=H+'px';
  const vals=D.wards.map(w=>w.rong), lo=0, hi=Math.max(D.lts*1.05,...vals), NB=22;
  const bins=new Array(NB).fill(0);
  vals.forEach(v=>bins[Math.min(NB-1,Math.floor((v-lo)/(hi-lo)*NB))]++);
  const ymax=Math.max(...bins);
  const X=v=>mL+(v-lo)/(hi-lo)*(W-mL-mR), Y=v=>H-mB-v/ymax*(H-mT-mB);
  const bw=(W-mL-mR)/NB;

  for(let t=0;t<=ymax;t+=Math.ceil(ymax/4)){
    s.appendChild(el('line',{class:'gl',x1:mL,x2:W-mR,y1:Y(t),y2:Y(t)}));
    s.appendChild(txt(t,{class:'tk',x:mL-6,y:Y(t)+3.5,'text-anchor':'end'}));
  }
  bins.forEach((n,i)=>{
    if(!n)return;
    const r=el('rect',{x:mL+i*bw+.8,y:Y(n),width:bw-1.6,height:H-mB-Y(n),
      fill:cssv('--t-blue'),'fill-opacity':.78,rx:1});
    const t=el('title'); t.textContent=
      `${pc(lo+(hi-lo)*i/NB,1)} – ${pc(lo+(hi-lo)*(i+1)/NB,1)}: ${n} ô`;
    r.appendChild(t); s.appendChild(r);
  });
  s.appendChild(el('line',{class:'ax',x1:mL,x2:W-mR,y1:H-mB,y2:H-mB}));
  for(let t=0;t<=hi;t++){
    s.appendChild(txt(t+'%',{class:'tk',x:X(t),y:H-mB+14,'text-anchor':'middle'}));
  }
  s.appendChild(el('line',{class:'refl',x1:X(D.lts),x2:X(D.lts),y1:mT-4,y2:H-mB}));
  s.appendChild(txt('Gửi tiết kiệm',{class:'reft',x:X(D.lts)-5,y:mT+6,'text-anchor':'end'}));
  s.appendChild(txt('Tỉ suất ròng của ô phường',{class:'lbl',x:(mL+W-mR)/2,y:H-6,'text-anchor':'middle'}));
  s.appendChild(txt('Số ô',{class:'lbl',x:mL-24,y:mT+2,transform:`rotate(-90 ${mL-24} ${mT+2})`,'text-anchor':'end'}));
}

/* ===================== 5. may tinh ===================== */
const sel=$('sel');
const SZ=['0-40','40-60','60-80','80-120','120-200','200-+'];
const ord=D.cells.map((c,i)=>i).sort((a,b)=>{
  const A=D.cells[a],B=D.cells[b];
  return A.q.localeCompare(B.q,'vi') || A.c.localeCompare(B.c,'vi')
      || SZ.indexOf(A.d)-SZ.indexOf(B.d);});
sel.innerHTML='<option value="-1">— tự nhập —</option>'+
  ord.map(i=>{const c=D.cells[i];
    return `<option value="${i}">${c.q} · ${c.c.replace('Căn hộ/Chung cư','Căn hộ')} · ${c.d} m² — ròng ${pc(c.rong)} (${c.nb+c.nt} tin)</option>`;
  }).join('');
const parseN=s=>+String(s).replace(/\D/g,'')||0;
const setN=(id,v)=>$(id).value=nf.format(Math.round(v));

function calc(){
  const gia=parseN($('gia').value), thue=parseN($('thue').value);
  const vay=+$('vay').value/100, lv=+$('lv').value/100, lt=+$('lt').value/100;
  const bt=+$('bt').value, bh=+$('bh').value/100;
  $('vv').textContent=(vay*100)+'%'; $('lvv').textContent=(lv*100).toFixed(1)+'%';
  $('ltv').textContent=(lt*100).toFixed(1)+'%'; $('btv').textContent=bt+' tháng';
  $('bhv').textContent=(bh*100).toFixed(1)+'%';
  if(!gia)return;

  const gop=thue*12/gia*100;
  const thuc=thue*12*(1-bt/12);
  const rongVND=thuc-thuc*D.gd.thue_cho_thue-gia*bh;
  const rong=rongVND/gia*100;
  const dt=(rongVND-gia*vay*lv)/12, nh=gia*lt/12;
  const nam=rong>0?100/rong:Infinity;
  const tang=vay*lv*100+(1-vay)*lt*100-rong;

  $('o_gop').textContent=pc(gop);
  $('o_rong').textContent=pc(rong);
  $('o_rong').style.color=rong<lt*100?'var(--neg)':'var(--pos)';
  $('o_nam').textContent=isFinite(nam)?Math.round(nam)+' năm':'không bao giờ';
  $('o_dt').textContent=(dt>=0?'+':'−')+money(Math.abs(dt));
  $('o_dt').style.color=dt>=0?'var(--pos)':'var(--neg)';
  $('o_nh').textContent='+'+money(nh);
  $('o_nh').style.color='var(--pos)';
  $('o_tang').textContent=pc(tang);

  $('verdict').innerHTML=rong<lt*100
    ? `Gửi ngân hàng hơn <b>${pc(lt*100-rong)}</b> mỗi năm. Chênh lệch dòng tiền giữa hai lựa chọn là
       <b>${money(nh-dt)} mỗi tháng</b>. Để mua nhà có lợi hơn, giá nhà phải tăng đều
       <b>${pc(tang)} mỗi năm</b>, năm này qua năm khác.`
    : `Với các giả định này, cho thuê nhỉnh hơn gửi tiết kiệm <b>${pc(rong-lt*100)}</b> mỗi năm.`;
}
['gia','thue'].forEach(id=>$(id).addEventListener('input',()=>{sel.value='-1';calc();}));
['vay','lv','lt','bt','bh'].forEach(id=>$(id).addEventListener('input',calc));
sel.addEventListener('change',()=>{
  const c=D.cells[+sel.value]; if(!c)return;
  const m2=({'0-40':32,'40-60':52,'60-80':70,'80-120':95,'120-200':150,'200-+':260})[c.d]||70;
  setN('gia',c.ban*m2); setN('thue',c.thue*m2); calc();
});
$('vay').value=D.gd.ty_le_vay*100; $('lv').value=D.gd.lai_vay_tha_noi*100;
$('lt').value=D.lts; $('bt').value=D.gd.bo_trong_thang; $('bh').value=1.0;
{const ung=D.cells.map((c,i)=>[c,i]).filter(([c])=>c.c.startsWith('Căn hộ')&&c.d==='60-80');
 ung.sort((a,b)=>(b[0].nb+b[0].nt)-(a[0].nb+a[0].nt));
 sel.value=String(ung.length?ung[0][1]:0);}
sel.dispatchEvent(new Event('change'));

/* ===================== 6. bang ===================== */
let sortK='rong',sortD=false;
function drawTable(){
  const rows=D.wards.slice().sort((a,b)=>{
    const x=a[sortK],y=b[sortK];
    return (sortD?1:-1)*(typeof x==='string'?String(y).localeCompare(String(x),'vi'):y-x);
  });
  const wmax=Math.max(...rows.map(r=>r.hi-r.lo));
  document.querySelector('#wt tbody').innerHTML=rows.map(r=>{
    const mo=r.nb<15||r.nt<15;
    return `<tr${mo?' class="thin"':''}>
      <td>${r.p}</td><td>${r.q.replace('Thành phố ','TP. ')}</td>
      <td>${r.c.replace('Căn hộ/Chung cư','Căn hộ')}</td>
      <td class="n">${String(r.ban).replace('.',',')}</td>
      <td class="n">${nf.format(r.thue)}</td>
      <td class="n">${pc(r.gop)}</td>
      <td class="n" style="color:${r.rong<D.lts?'var(--neg)':'var(--pos)'};font-weight:600">${pc(r.rong)}</td>
      <td class="n"><span class="thin">${pc(r.lo)}–${pc(r.hi)}</span>
        <span class="cimini"><i style="left:${(r.lo/ (r.lo+ (r.hi-r.lo)+1e-9))*0}%;width:${Math.min(100,(r.hi-r.lo)/wmax*100)}%"></i></span></td>
      <td class="n thin">${r.nb}/${r.nt}</td></tr>`;
  }).join('');
}
document.querySelectorAll('#wt th').forEach(th=>th.addEventListener('click',()=>{
  const k=th.dataset.k; sortD=(k===sortK)?!sortD:false; sortK=k; drawTable();
}));
drawTable();

/* ===================== 7. ban do ===================== */
window.addEventListener('DOMContentLoaded',function(){
  if(typeof L==='undefined'){
    $('map').innerHTML='<div style="padding:22px;color:#bbb;font-size:13px">Bản đồ cần kết nối mạng '
      +'để tải ảnh nền. Các bảng và biểu đồ khác vẫn dùng được.</div>'; return;
  }
  const kh=s=>s.toLocaleUpperCase('vi').replace(/\s+/g,' ').trim();
  const byName={}; D.dist.forEach(d=>byName[kh(d.ten)]=d);
  const vals=D.dist.map(d=>d.rong), lo=Math.min(...vals), hi=Math.max(...vals);
  const C0=[125,29,22],C1=[237,201,72];
  const color=v=>`rgb(${C0.map((c,i)=>Math.round(c+(C1[i]-c)*((v-lo)/(hi-lo||1)))).join(',')})`;

  const HCM=L.latLngBounds(D.bounds), VN=L.latLngBounds([[8.2,102.1],[23.5,109.6]]);
  const map=L.map('map',{zoomControl:false,scrollWheelZoom:true,zoomSnap:.25});
  map.fitBounds(VN);   /* phai dat khung nhin TRUOC khi them lop, neu khong Leaflet nem loi */
  L.control.zoom({position:'bottomright'}).addTo(map);
  window._map=map;

  const bases={
    'Vệ tinh':L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {maxZoom:18,attribution:'Ảnh vệ tinh &copy; Esri, Maxar'}),
    'Bản đồ':L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      {maxZoom:19,attribution:'&copy; OpenStreetMap &copy; CARTO'}),
    'Nền tối':L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {maxZoom:19,attribution:'&copy; OpenStreetMap &copy; CARTO'}),
  };
  bases['Vệ tinh'].addTo(map);
  L.control.layers(bases,null,{position:'topright'}).addTo(map);

  const layer=L.geoJSON(D.geo,{
    style:f=>{const r=byName[kh(f.properties.ten)];
      return r?{color:'#fff',weight:1,opacity:.85,fillColor:color(r.rong),fillOpacity:.7}
              :{color:'#fff',weight:1,opacity:.4,fillColor:'#8a8a8a',fillOpacity:.4};},
    onEachFeature:(f,l)=>{
      const ten=f.properties.ten, r=byName[kh(ten)];
      l.bindTooltip(r?`<b>${ten}</b><br>Ròng ${pc(r.rong)} <span style="opacity:.6">(${pc(r.lo)}–${pc(r.hi)})</span>`
                     +`<br>Gộp ${pc(r.gop)} · ${nf.format(r.n)} tin`
                    :`<b>${ten}</b><br><span style="opacity:.6">không đủ dữ liệu</span>`,
        {sticky:true,className:'dtip',opacity:1});
      l.on('mouseover',()=>l.setStyle({weight:2.5,fillOpacity:.85}));
      l.on('mouseout',()=>layer.resetStyle(l));
      l.on('click',()=>map.flyToBounds(l.getBounds(),{padding:[20,20],duration:.7}));
    }}).addTo(map);

  /* khung mac dinh khop theo cac quan CO du lieu — Can Gio va Cu Chi rat rong va deu
     trong, khop ca chung se lam loi do thi teo lai o giua */
  const LOI=L.latLngBounds([]);
  layer.eachLayer(l=>{if(byName[kh(l.feature.properties.ten)])LOI.extend(l.getBounds());});

  const ping=L.marker(HCM.getCenter(),{interactive:false,icon:L.divIcon({className:'',
    html:'<div class="ping"><span class="pinglbl">TP.HCM</span></div>',iconSize:[13,13],iconAnchor:[6,6]})});
  const PAD={padding:[22,22]};
  let view='vn';
  const toVN=()=>{view='vn';map.flyToBounds(VN,{duration:1.1});ping.addTo(map);};
  const toHCM=()=>{view='hcm';map.flyToBounds(LOI,{...PAD,duration:1.3});map.removeLayer(ping);};
  $('b_vn').onclick=toVN; $('b_hcm').onclick=toHCM;

  /* chi goi khi khung THAT SU doi kich thuoc — goi vo to va se lam dut hoat anh bay */
  const mel=$('map'); let last='';
  const fit=()=>{const k=mel.clientWidth+'x'+mel.clientHeight; if(k===last)return; last=k;
    map.invalidateSize({animate:false}); map.fitBounds(view==='vn'?VN:LOI,view==='vn'?{}:PAD);};
  new ResizeObserver(fit).observe(mel);
  requestAnimationFrame(fit);
  ping.addTo(map); setTimeout(toHCM,1500);

  $('lg_lo').textContent=pc(lo); $('lg_hi').textContent=pc(hi);
});

/* ===================== ve lai khi doi kich thuoc ===================== */
function drawAll(){drawRank();drawScat();drawHist();}
/* Ve NGAY, dong bo. Khong dung requestAnimationFrame lam lan ve dau: trinh duyet
   tam dung rAF khi tab dang an, va bieu do se trong tron cho toi khi nguoi dung
   chuyen sang tab do. Sau khi trang load xong thi ve lai de lay be ngang chinh xac. */
drawAll();
addEventListener('load',drawAll);
let rt; new ResizeObserver(()=>{clearTimeout(rt);rt=setTimeout(drawAll,120);})
  .observe(document.querySelector('.app'));
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',drawAll);
</script>
</body>
</html>
"""

rej_names = {
    "1_thieu_truong_bat_buoc": "Thiếu giá, diện tích hoặc phường",
    "2_dien_tich_vo_ly": "Diện tích ngoài 10–1.000 m²",
    "3_gia_vo_ly": "Giá ngoài khoảng hợp lý",
    "4_gia_tren_m2_vo_ly": "Giá trên m² vô lý (đăng nhầm mục)",
    "5_trung_mem": "Trùng: cùng người đăng, cùng m², cùng giá",
}
rej_html = "".join(
    f"<tr><td>{rej_names.get(k, k)}</td><td>{v:,}</td></tr>".replace(",", ".")
    for k, v in sorted(clean["loai_bo"].items()))

html = (HTML
        .replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
        .replace("__NGAY__", NGAY)
        .replace("__NRAW__", f"{clean['tong_dong_vao']:,}".replace(",", "."))
        .replace("__NCLEAN__", f"{clean['giu_lai']:,}".replace(",", "."))
        .replace("__PCT__", f"{clean['ty_le_giu']:.1f}".replace(".", ","))
        .replace("__NW__", str(len(wards)))
        .replace("__CIW__", f"{CI_W:.2f}".replace(".", ","))
        .replace("__REJECTS__", rej_html))

WEB.mkdir(parents=True, exist_ok=True)
(WEB / "index.html").write_text(html, encoding="utf-8")
for f in ("yield_by_ward.json", "yield_by_district_size.json", "district_ci.json",
          "financial_summary.json", "clean_report.json"):
    (WEB / f).write_text((OUT / f).read_text(encoding="utf-8"), encoding="utf-8")

print(f"web/index.html  ({(WEB / 'index.html').stat().st_size / 1024:.0f} KB)")
print(f"  {len(dists)} quan · {len(cells)} o quan-dien-tich · {len(wards)} o phuong")
print(f"  KTC cap quan rong trung vi {CI_W:.2f} diem")
