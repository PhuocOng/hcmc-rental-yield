"""Buoc 4 — Dung website.

v3: song ngu Anh/Viet (Anh mac dinh), bo chu Inter + IBM Plex Mono, bo cuc bang
dieu khien du lieu, bieu do SVG co truc va thanh sai so bootstrap.

Chay: python src/build_site.py   ->  docs/index.html
"""

from __future__ import annotations

import json
import statistics as st
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
WEB = ROOT / "docs"      # GitHub Pages chi phuc vu tu / hoac /docs

fin = json.loads((OUT / "financial_summary.json").read_text(encoding="utf-8"))
cells = json.loads((OUT / "yield_by_district_size.json").read_text(encoding="utf-8"))
wards = json.loads((OUT / "yield_by_ward.json").read_text(encoding="utf-8"))
clean = json.loads((OUT / "clean_report.json").read_text(encoding="utf-8"))
dists = json.loads((OUT / "district_ci.json").read_text(encoding="utf-8"))
den = json.loads((OUT / "district_en.json").read_text(encoding="utf-8"))
mapgeo = json.loads((OUT / "hcm_geo.json").read_text(encoding="utf-8"))
mapbounds = json.loads((OUT / "hcm_bounds.json").read_text(encoding="utf-8"))

den.setdefault("Huyện Củ Chi", "Cu Chi")
den.setdefault("Huyện Cần Giờ", "Can Gio")

GD, LTS = fin["gia_dinh"], fin["lai_tiet_kiem_pct"]
CI_W = st.median([d["rong_hi"] - d["rong_lo"] for d in dists])


def r2(x):
    return round(x, 2)


DATA = {
    "gd": GD, "lts": LTS, "den": den,
    "dist": [{"ten": d["ten"], "rong": r2(d["rong"]), "gop": r2(d["gop"]),
              "lo": r2(d["rong_lo"]), "hi": r2(d["rong_hi"]), "n": d["n"]} for d in dists],
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
            "nam": round(fin["so_nam_thu_hoi_von"]), "chenh": r2(fin["chenh_lech_diem"])},
    "n": {"raw": clean["tong_dong_vao"], "clean": clean["giu_lai"],
          "pct": clean["ty_le_giu"], "wards": len(wards), "ciw": r2(CI_W)},
    "rej": clean["loai_bo"],
}

# ---------------------------------------------------------------- HTML + CSS
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HCMC Rental Yield</title>
<meta name="description" content="45,084 for-sale and for-rent listings in Ho Chi Minh City: net rental yield 1.51%/yr against a 6.0% bank deposit.">

<!-- Bieu tuong = hai thanh so sanh, chinh la luan diem cua trang thu gon lai.
     SVG cho trinh duyet moi, .ico cho ban cu va cho Windows. -->
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#1A1714">

<!-- og:image PHAI la duong dan tuyet doi: Facebook va Twitter khong doc duoc
     duong dan tuong doi. Doi cho nay neu ten mien thay doi. -->
<meta property="og:type" content="website">
<meta property="og:title" content="Buying to let in HCMC earns less than a bank deposit">
<meta property="og:description" content="45,084 listings across 20 districts. Net rental yield 1.51%/yr against 6.00% on a 12-month deposit — a gap of 4.49 points, before the property has appreciated at all.">
<meta property="og:image" content="https://rental-yield.bannguyenxanh.com/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>
<style>
:root{
  /* Bang mau co chu dinh, KHONG dung do-xanh la:
     - dat nung  = dai luong dang do (ti suat cho thue)
     - xanh muc  = moc so sanh (lai tiet kiem)
     - hoang tho = nhom thu hai (nha o)
     Nen la trang am, khong phai xam lanh, de bot cam giac "mau mac dinh". */
  --acc:#A8432A; --acc2:#B07C2B; --ref:#1F5E5B;
  --page:#F5F2ED; --panel:#FFFDFA; --line:#DDD6CC; --line2:#EDE8E0;
  --ink:#1A1714; --ink2:#5C554C; --ink3:#7A7268;
  --pos:#1F5E5B; --neg:#A8432A;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{--page:#131211;--panel:#1B1917;--line:#2E2B27;--line2:#252220;
        --ink:#EBE7E1;--ink2:#A29A90;--ink3:#8A8279;
        --acc:#CC6242; --acc2:#C99A46; --ref:#4E9C93;
        --pos:#4E9C93; --neg:#CC6242}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);
  font:400 13.5px/1.55 var(--sans);-webkit-font-smoothing:antialiased;
  font-feature-settings:"cv05" 1,"cv11" 1,"ss01" 1;font-variant-numeric:tabular-nums}
h1,h2,h3{margin:0;font-weight:600;letter-spacing:-.011em}
p{margin:0 0 9px}

.app{max-width:1340px;margin:0 auto;padding:0 16px 56px}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:11px}
.c12{grid-column:span 12}.c7{grid-column:span 7}.c6{grid-column:span 6}.c5{grid-column:span 5}
@media(max-width:1020px){.c7,.c6,.c5{grid-column:span 12}}

.top{position:sticky;top:0;z-index:900;background:var(--panel);
  border-bottom:1px solid var(--line);margin-bottom:11px}
.top .in{max-width:1340px;margin:0 auto;padding:0 16px;height:46px;display:flex;
  align-items:center;gap:12px}
.top h1{font-size:14px;white-space:nowrap}
.top .home{color:var(--ink3);text-decoration:none;font-size:16px;line-height:1;
  padding:2px 6px;border:1px solid var(--line);border-radius:3px}
.top .home:hover{color:var(--ink);border-color:var(--ink3)}
.top .tag{font:500 10px/1 var(--mono);letter-spacing:.05em;color:var(--ink3);
  border:1px solid var(--line);border-radius:2px;padding:4px 6px;white-space:nowrap}
.top .sp{margin-left:auto;display:flex;gap:15px;font-size:11px;color:var(--ink3);white-space:nowrap}
.top .sp b{font-family:var(--mono);font-weight:500;color:var(--ink2)}
@media(max-width:840px){.top .sp{display:none}}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.lang button{font:500 11px/1 var(--sans);letter-spacing:.04em;padding:5px 9px;border:0;
  cursor:pointer;background:var(--panel);color:var(--ink3)}
.lang button+button{border-left:1px solid var(--line)}
.lang button[aria-pressed=true]{background:var(--ink);color:var(--panel)}

.p{background:var(--panel);border:1px solid var(--line);border-radius:3px;
  display:flex;flex-direction:column;min-width:0}
.ph{padding:8px 12px;border-bottom:1px solid var(--line2);display:flex;
  align-items:center;gap:9px;flex-wrap:wrap;min-height:35px}
.ph h2{font:600 10.5px/1.3 var(--sans);letter-spacing:.085em;text-transform:uppercase;color:var(--ink2)}
.ph .hint{font-size:11px;color:var(--ink3);margin-left:auto}
.pb{padding:12px;flex:1;min-width:0}
.pb.tight{padding:0}

.hero{display:grid;grid-template-columns:1.18fr 1fr;gap:0;margin-bottom:11px;
  background:var(--panel);border:1px solid var(--line);border-radius:3px;overflow:hidden}
@media(max-width:900px){.hero{grid-template-columns:1fr}}
.cmp{padding:15px 18px;border-right:1px solid var(--line2);min-width:0}
@media(max-width:900px){.cmp{border-right:0;border-bottom:1px solid var(--line2)}}
.cl{font:500 9.5px/1.3 var(--sans);letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:13px}
/* MOT luoi chung cho ca hai hang, khong phai hai luoi rieng: co the cot dau
   la max-content nen tu co theo do dai chu ("%/yr" vs "%/năm") ma hai hang van
   thang cot nhau tuyet doi. Truoc day cot dau khoa cung 86px -> tieng Viet tran
   de len thanh. */
.cgrid{display:grid;grid-template-columns:max-content 1fr max-content;
  column-gap:12px;row-gap:9px;align-items:center}
.cn{font:600 30px/1 var(--mono);letter-spacing:-.03em;text-align:right;white-space:nowrap}
.cn small{font:500 12px/1 var(--sans);color:var(--ink3);margin-left:1px}
.cn.neg{color:var(--neg)} .cn.pos{color:var(--pos)}
.cb{height:15px;background:var(--line2);border-radius:2px;position:relative;overflow:hidden}
.cb i{position:absolute;left:0;top:0;bottom:0;display:block;border-radius:2px;
  transition:width .5s cubic-bezier(.22,1,.36,1)}
.cb i.r{background:var(--neg)} .cb i.g{background:var(--ref)}
.cc{font-size:11px;color:var(--ink3);white-space:nowrap}
@media(max-width:620px){.cgrid{grid-template-columns:max-content 1fr}.cc{display:none}}
.cg{margin-top:11px;padding-top:10px;border-top:1px solid var(--line2);
  font-size:12.5px;color:var(--ink2)}
.cg b{font-family:var(--mono);font-weight:600;color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(3,1fr)}
.stats>div{padding:15px 12px;border-right:1px solid var(--line2);min-width:0}
.stats>div:last-child{border-right:0}
@media(max-width:520px){.stats{grid-template-columns:1fr}
  .stats>div{border-right:0;border-top:1px solid var(--line2)}}
.stats .lb{font:500 9.5px/1.3 var(--sans);letter-spacing:.075em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:7px;white-space:nowrap}
.stats .v{font:600 19px/1.15 var(--mono);letter-spacing:-.025em;white-space:nowrap}
.stats .v.sm{font-size:16.5px}   /* o khoang gia tri dai hon nen phai nho hon */
.stats .v small{font:500 11px/1 var(--sans);color:var(--ink3);margin-left:2px;letter-spacing:0}
.stats .ci{font-size:10.5px;color:var(--ink3);margin-top:6px;line-height:1.4}

svg.chart{display:block;width:100%;overflow:visible}
.ax{stroke:var(--line)}
.gl{stroke:var(--line2);shape-rendering:crispEdges}
.tk{fill:var(--ink3);font:400 10px var(--mono)}
.lbl{fill:var(--ink2);font:400 11px var(--sans)}
.dlb{fill:var(--ink2);font:400 11px var(--sans)}
.val{fill:var(--ink);font:500 11px var(--mono)}
.refl{stroke:var(--ref);stroke-width:1.4;stroke-dasharray:4 3}
.reft{fill:var(--ref);font:500 10px var(--sans)}
.whisk{stroke:var(--ink3);stroke-width:1.1;opacity:.8}
.barr{fill:var(--acc)}
.barr:hover{fill:var(--acc2)}
.dot{stroke:var(--panel);stroke-width:.7;cursor:pointer}
.dot:hover{stroke:var(--ink);stroke-width:1.5}

.lg{display:flex;gap:13px;align-items:center;font-size:10.5px;color:var(--ink2);
  flex-wrap:wrap;margin-top:7px}
.lg i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.seg button{font:500 10.5px/1 var(--sans);padding:5px 9px;border:0;cursor:pointer;
  background:var(--panel);color:var(--ink3)}
.seg button+button{border-left:1px solid var(--line)}
.seg button[aria-pressed=true]{background:var(--acc);color:#fff}

.tw{overflow:auto;max-height:390px}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:12px}
thead th{position:sticky;top:0;background:var(--panel);z-index:1;text-align:left;
  padding:7px 9px;border-bottom:1px solid var(--line);
  font:600 9.5px/1.35 var(--sans);letter-spacing:.07em;text-transform:uppercase;
  color:var(--ink3);cursor:pointer;white-space:nowrap;user-select:none}
thead th:hover{color:var(--ink)}
thead th span{font:400 9.5px var(--sans);letter-spacing:.03em;text-transform:none;
  opacity:.75;display:block}
tbody td{padding:5px 9px;border-bottom:1px solid var(--line2);white-space:nowrap}
tbody tr:hover td{background:color-mix(in srgb,var(--acc) 7%,transparent)}
td.n,th.n{text-align:right}
td.n{font-family:var(--mono);font-size:11.5px}
tr.low td{opacity:.48}
.ci2{color:var(--ink3);font-size:10.5px}

.cf{display:grid;grid-template-columns:repeat(4,1fr);gap:10px 15px}
@media(max-width:880px){.cf{grid-template-columns:repeat(2,1fr)}}
label{display:block;font:500 9.5px/1.3 var(--sans);letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:4px}
label .rv{float:right;font:500 11px var(--mono);letter-spacing:0;text-transform:none;color:var(--ink)}
input[type=text],select{width:100%;padding:6px 8px;font:400 12.5px var(--sans);
  border:1px solid var(--line);border-radius:3px;background:var(--panel);color:var(--ink)}
input[type=text]{font-family:var(--mono)}
input[type=range]{width:100%;accent-color:var(--acc);margin:6px 0 0}
.res{display:grid;grid-template-columns:repeat(3,1fr);margin-top:13px;
  border:1px solid var(--line);border-radius:3px;overflow:hidden}
@media(max-width:880px){.res{grid-template-columns:1fr 1fr}}
.res div{padding:9px 11px;border-right:1px solid var(--line2);border-bottom:1px solid var(--line2)}
.res .rl{font:500 9.5px/1.3 var(--sans);letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:5px}
.res .rv2{font:600 18px/1.1 var(--mono);letter-spacing:-.02em}
.vd{margin-top:11px;padding:10px 12px;border-radius:3px;font-size:12.5px;line-height:1.6;
  background:color-mix(in srgb,var(--neg) 8%,transparent);
  border:1px solid color-mix(in srgb,var(--neg) 22%,transparent)}
.vd b{font-family:var(--mono);font-weight:600}

#map{width:100%;height:412px;background:#0d1117}
.leaflet-container{font-family:var(--sans);background:#0d1117}
.leaflet-control-attribution{font-size:9px!important;background:rgba(0,0,0,.5)!important;color:#bbb!important}
.leaflet-control-attribution a{color:#9ec5ff!important}
.mwrap{position:relative}
.mbtn{position:absolute;left:8px;top:8px;z-index:500;display:flex;gap:5px}
.mbtn button{font:500 10.5px/1 var(--sans);padding:6px 9px;border-radius:3px;cursor:pointer;
  border:1px solid rgba(255,255,255,.22);background:rgba(12,12,12,.78);color:#eee}
.mbtn button:hover{background:rgba(44,44,44,.9)}
.mlg{position:absolute;left:8px;bottom:18px;z-index:500;background:rgba(12,12,12,.78);
  border:1px solid rgba(255,255,255,.14);border-radius:3px;padding:7px 9px;color:#eee;
  font:500 9.5px var(--sans);letter-spacing:.05em;text-transform:uppercase}
.mlg .b{display:block;height:6px;width:142px;border-radius:2px;margin:5px 0 3px;
  background:linear-gradient(90deg,#E0C48F,#C4744B,#7A2E18)}
.mlg .r{display:flex;justify-content:space-between;font:400 10px var(--mono);text-transform:none}
.dtip{background:#14171b;color:#f0f0f0;border:1px solid rgba(255,255,255,.18);border-radius:3px;
  padding:7px 9px;font:400 11.5px/1.55 var(--sans)}
.dtip b{font-size:12.5px}
.ping{width:12px;height:12px;border-radius:50%;background:#EDC948;
  box-shadow:0 0 0 2px rgba(255,255,255,.9);position:relative}
.ping::after{content:"";position:absolute;inset:-5px;border:2px solid #EDC948;border-radius:50%;
  animation:pl 1.7s ease-out infinite}
@keyframes pl{0%{transform:scale(.55);opacity:1}100%{transform:scale(2.6);opacity:0}}
.pinglbl{position:absolute;left:18px;top:-3px;white-space:nowrap;color:#fff;
  font:600 11.5px var(--sans);text-shadow:0 1px 4px #000}

.prose{font-size:12.5px;line-height:1.7;color:var(--ink2);max-width:72ch}
.prose b{color:var(--ink);font-weight:600}
.prose h3{font:600 12px/1.4 var(--sans);color:var(--ink);margin:15px 0 5px}
.prose h3:first-child{margin-top:0}
.kv{width:100%;font-size:12px;margin:3px 0 0;border-collapse:collapse}
.kv td{padding:4px 0;border-bottom:1px solid var(--line2);color:var(--ink2)}
.kv td:last-child{text-align:right;font-family:var(--mono);font-size:11.5px;color:var(--ink)}
details{border-top:1px solid var(--line2);padding:8px 0}
details:first-of-type{border-top:0}
summary{cursor:pointer;font:600 12px var(--sans);color:var(--ink)}
details p{margin:6px 0 0;font-size:12.5px;line-height:1.65;color:var(--ink2)}
footer{margin-top:14px;padding:13px 2px;font-size:11px;color:var(--ink3);
  border-top:1px solid var(--line)}
</style>
</head>
<body>

<div class="top"><div class="in">
  <a class="home" href="index.html" title="Home">←</a>
  <h1 data-t="title"></h1>
  <span class="tag" data-t="src"></span>
  <div class="lang">
    <button data-l="en" aria-pressed="true">EN</button>
    <button data-l="vi" aria-pressed="false">VI</button>
  </div>
  <div class="sp">
    <span><b id="s1"></b> <span data-t="s_clean"></span></span>
    <span><b id="s2"></b> <span data-t="s_raw"></span></span>
    <span><b id="s3"></b> <span data-t="s_cells"></span></span>
  </div>
</div></div>

<div class="app">
  <div class="hero">
    <div class="cmp">
      <div class="cl" data-t="h_cmp"></div>
      <div class="cgrid">
        <span class="cn neg" id="c_rent"></span>
        <span class="cb"><i class="r" id="bar_rent"></i></span>
        <span class="cc" data-t="h_rent"></span>
        <span class="cn pos" id="c_dep"></span>
        <span class="cb"><i class="g" id="bar_dep"></i></span>
        <span class="cc" data-t="h_dep"></span>
      </div>
      <div class="cg" id="c_gap"></div>
    </div>
    <div class="stats">
      <div><div class="lb" data-t="s_gross"></div><div class="v" id="s_gross_v"></div>
        <div class="ci" data-t="s_gross_s"></div></div>
      <div><div class="lb" data-t="s_pay"></div><div class="v" id="s_pay_v"></div>
        <div class="ci" data-t="s_pay_s"></div></div>
      <div><div class="lb" data-t="s_rng"></div><div class="v sm" id="s_rng_v"></div>
        <div class="ci" id="s_rng_s"></div></div>
    </div>
  </div>

  <div class="grid">
    <div class="p c7">
      <div class="ph"><h2 data-t="p_map"></h2><span class="hint" data-t="h_map"></span></div>
      <div class="pb tight mwrap">
        <div id="map"></div>
        <div class="mbtn"><button id="b_vn" data-t="b_vn"></button><button id="b_hcm" data-t="b_hcm"></button></div>
        <div class="mlg"><div data-t="lg_t"></div><span class="b"></span>
          <div class="r"><span id="lg_lo"></span><span id="lg_hi"></span></div></div>
      </div>
    </div>

    <div class="p c5">
      <div class="ph"><h2 data-t="p_rank"></h2><span class="hint" data-t="h_rank"></span></div>
      <div class="pb"><svg id="ch_rank" class="chart"></svg></div>
    </div>

    <div class="p c7">
      <div class="ph"><h2 data-t="p_scat"></h2>
        <div class="seg" id="segcat">
          <button data-c="all" aria-pressed="true" data-t="f_all"></button>
          <button data-c="apt" aria-pressed="false" data-t="f_apt"></button>
          <button data-c="house" aria-pressed="false" data-t="f_house"></button>
        </div>
        <span class="hint" data-t="h_scat"></span></div>
      <div class="pb"><svg id="ch_scat" class="chart"></svg>
        <div class="lg">
          <span><i style="background:var(--acc)"></i><span data-t="f_apt"></span></span>
          <span><i style="background:var(--acc2)"></i><span data-t="f_house"></span></span>
          <span style="color:var(--ink3)" data-t="lg_size"></span>
        </div>
      </div>
    </div>

    <div class="p c5">
      <div class="ph"><h2 data-t="p_hist"></h2><span class="hint" id="h_hist"></span></div>
      <div class="pb"><svg id="ch_hist" class="chart"></svg></div>
    </div>

    <div class="p c12">
      <div class="ph"><h2 data-t="p_calc"></h2><span class="hint" data-t="h_calc"></span></div>
      <div class="pb">
        <div class="cf">
          <div><label data-t="f_cell"></label><select id="sel"></select></div>
          <div><label data-t="f_price"></label><input type="text" id="gia" inputmode="numeric"></div>
          <div><label data-t="f_rent"></label><input type="text" id="thue" inputmode="numeric"></div>
          <div><label><span data-t="f_ltv"></span><span class="rv" id="vv"></span></label><input type="range" id="vay" min="0" max="90" step="5"></div>
          <div><label><span data-t="f_mrate"></span><span class="rv" id="lvv"></span></label><input type="range" id="lv" min="6" max="18" step="0.5"></div>
          <div><label><span data-t="f_drate"></span><span class="rv" id="ltv"></span></label><input type="range" id="lt" min="3" max="10" step="0.1"></div>
          <div><label><span data-t="f_vac"></span><span class="rv" id="btv"></span></label><input type="range" id="bt" min="0" max="4" step="0.5"></div>
          <div><label><span data-t="f_maint"></span><span class="rv" id="bhv"></span></label><input type="range" id="bh" min="0" max="4" step="0.1"></div>
        </div>
        <div class="res">
          <div><div class="rl" data-t="r_gross"></div><div class="rv2" id="o_gop"></div></div>
          <div><div class="rl" data-t="r_net"></div><div class="rv2" id="o_rong"></div></div>
          <div><div class="rl" data-t="r_pay"></div><div class="rv2" id="o_nam"></div></div>
          <div><div class="rl" data-t="r_cf"></div><div class="rv2" id="o_dt"></div></div>
          <div><div class="rl" data-t="r_dep"></div><div class="rv2" id="o_nh"></div></div>
          <div><div class="rl" data-t="r_appr"></div><div class="rv2" id="o_tang"></div></div>
        </div>
        <div class="vd" id="verdict"></div>
      </div>
    </div>

    <div class="p c12">
      <div class="ph"><h2 data-t="p_tbl"></h2><span class="hint" data-t="h_tbl"></span></div>
      <div class="pb tight"><div class="tw"><table id="wt">
        <thead><tr id="thr"></tr></thead><tbody></tbody></table></div></div>
    </div>

    <div class="p c6">
      <div class="ph"><h2 data-t="p_meth"></h2></div>
      <div class="pb prose" id="meth"></div>
    </div>
    <div class="p c6">
      <div class="ph"><h2 data-t="p_lim"></h2><span class="hint" data-t="h_lim"></span></div>
      <div class="pb prose" id="lim"></div>
    </div>
  </div>

  <footer data-th="foot"></footer>
</div>

<script>
const D=__DATA__;
const $=id=>document.getElementById(id);
__I18N__

let L=localStorage.getItem('ry_lang')||'en';
const t=k=>T[L][k];
const LOC=()=>L==='en'?'en-US':'vi-VN';
const nf=n=>new Intl.NumberFormat(LOC()).format(n);
const dec=(v,d=1)=>L==='en'?v.toFixed(d):v.toFixed(d).replace('.',',');
const pc=(v,d=2)=>dec(v,d)+'%';
const money=v=>{const a=Math.abs(v);
  if(L==='en')return a>=1e9?(v/1e9).toFixed(2)+'B':a>=1e6?(v/1e6).toFixed(1)+'M':nf(Math.round(v));
  return a>=1e9?dec(v/1e9,2)+' tỷ':a>=1e6?dec(v/1e6,1)+' tr':nf(Math.round(v))+' đ';};
const DN=n=>L==='en'?(D.den[n]||n):n;
const isApt=c=>c.indexOf('Chung')>=0;
const CN=c=>isApt(c)?t('f_apt'):t('f_house');
const cssv=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function txt(s,a){const e=el('text',a);e.textContent=s;return e;}
function tip(node,s){const x=el('title',{});x.textContent=s;node.appendChild(x);return node;}
/* Do be ngang tu O CHUA: luc ve lan dau svg co the chua co kich thuoc, doc nham
   se lam viewBox sai ty le va chieu cao bi phong len gap may lan. */
const wOf=(s,min)=>Math.max(min,Math.round(s.parentElement.getBoundingClientRect().width-24||min));

/* ---------------- bieu do xep hang ---------------- */
function drawRank(){
  const s=$('ch_rank');s.innerHTML='';
  const rows=D.dist,W=wOf(s,340),RH=19,mT=24,mB=25,mL=98,mR=44,H=mT+rows.length*RH+mB;
  s.setAttribute('viewBox','0 0 '+W+' '+H);s.style.height=H+'px';
  const xm=Math.max(D.lts*1.06,...rows.map(r=>r.hi)),X=v=>mL+v/xm*(W-mL-mR);
  for(let i=0;i<=Math.floor(xm);i++){
    s.appendChild(el('line',{class:'gl',x1:X(i),x2:X(i),y1:mT-6,y2:H-mB}));
    s.appendChild(txt(i+'%',{class:'tk',x:X(i),y:H-mB+13,'text-anchor':'middle'}));}
  s.appendChild(el('line',{class:'refl',x1:X(D.lts),x2:X(D.lts),y1:mT-14,y2:H-mB}));
  s.appendChild(txt(t('dep_short')+' '+pc(D.lts,1),
    {class:'reft',x:X(D.lts)-4,y:mT-17,'text-anchor':'end'}));
  rows.forEach((r,i)=>{
    const y=mT+i*RH,cy=y+RH/2;
    s.appendChild(txt(DN(r.ten),{class:'dlb',x:mL-8,y:cy+4,'text-anchor':'end'}));
    s.appendChild(tip(el('rect',{class:'barr',x:mL,y:y+4,
      width:Math.max(1,X(r.rong)-mL),height:RH-9,rx:1}),
      DN(r.ten)+'\n'+t('r_net')+' '+pc(r.rong)+'   95% CI '+pc(r.lo)+' – '+pc(r.hi)
      +'\n'+t('r_gross')+' '+pc(r.gop)+'  ·  '+nf(r.n)));
    s.appendChild(el('line',{class:'whisk',x1:X(r.lo),x2:X(r.hi),y1:cy,y2:cy}));
    [r.lo,r.hi].forEach(v=>s.appendChild(
      el('line',{class:'whisk',x1:X(v),x2:X(v),y1:cy-4,y2:cy+4})));
    s.appendChild(txt(pc(r.rong),{class:'val',x:X(r.hi)+6,y:cy+4}));});
}

/* ---------------- bieu do phan tan ---------------- */
let catF='all';
function drawScat(){
  const s=$('ch_scat');s.innerHTML='';
  const W=wOf(s,420),H=298,mT=12,mB=36,mL=42,mR=12;
  s.setAttribute('viewBox','0 0 '+W+' '+H);s.style.height=H+'px';
  const pts=D.cells.filter(c=>catF==='all'||(catF==='apt')===isApt(c.c));
  const x1=Math.max(...pts.map(p=>p.ban/1e6))*1.05,
        y1=Math.max(D.lts*1.05,...pts.map(p=>p.rong));
  const X=v=>mL+v/x1*(W-mL-mR),Y=v=>H-mB-v/y1*(H-mT-mB);
  for(let i=0;i<=y1;i++){
    s.appendChild(el('line',{class:'gl',x1:mL,x2:W-mR,y1:Y(i),y2:Y(i)}));
    s.appendChild(txt(i+'%',{class:'tk',x:mL-6,y:Y(i)+3.5,'text-anchor':'end'}));}
  for(let i=0;i<=x1;i+=(x1>200?50:20))
    s.appendChild(txt(i,{class:'tk',x:X(i),y:H-mB+14,'text-anchor':'middle'}));
  s.appendChild(el('line',{class:'ax',x1:mL,x2:W-mR,y1:H-mB,y2:H-mB}));
  s.appendChild(el('line',{class:'refl',x1:mL,x2:W-mR,y1:Y(D.lts),y2:Y(D.lts)}));
  s.appendChild(txt(t('dep_short')+' '+pc(D.lts,1),
    {class:'reft',x:W-mR,y:Y(D.lts)-5,'text-anchor':'end'}));
  s.appendChild(txt(t('ax_price'),{class:'lbl',x:(mL+W-mR)/2,y:H-4,'text-anchor':'middle'}));
  const nm=Math.max(...pts.map(p=>p.nb+p.nt));
  pts.forEach(p=>s.appendChild(tip(el('circle',{class:'dot',
    cx:X(p.ban/1e6),cy:Y(p.rong),r:3+Math.sqrt((p.nb+p.nt)/nm)*7,'fill-opacity':.6,
    fill:isApt(p.c)?cssv('--acc'):cssv('--acc2')}),
    DN(p.q)+' · '+CN(p.c)+' · '+p.d+' m²\n'+t('r_net')+' '+pc(p.rong)
    +'   CI '+pc(p.lo)+'–'+pc(p.hi)+'\n'+dec(p.ban/1e6)+' M/m²  ·  '
    +nf(Math.round(p.thue/1e3))+' k/m²\n'+nf(p.nb)+' / '+nf(p.nt))));
}

/* ---------------- bieu do phan bo ---------------- */
function drawHist(){
  const s=$('ch_hist');s.innerHTML='';
  const W=wOf(s,320),H=298,mT=12,mB=36,mL=30,mR=10,NB=22;
  s.setAttribute('viewBox','0 0 '+W+' '+H);s.style.height=H+'px';
  const v=D.wards.map(w=>w.rong),hi=Math.max(D.lts*1.05,...v),b=new Array(NB).fill(0);
  v.forEach(x=>b[Math.min(NB-1,Math.floor(x/hi*NB))]++);
  const ym=Math.max(...b),X=x=>mL+x/hi*(W-mL-mR),Y=y=>H-mB-y/ym*(H-mT-mB),bw=(W-mL-mR)/NB;
  for(let i=0;i<=ym;i+=Math.ceil(ym/4)){
    s.appendChild(el('line',{class:'gl',x1:mL,x2:W-mR,y1:Y(i),y2:Y(i)}));
    s.appendChild(txt(i,{class:'tk',x:mL-6,y:Y(i)+3.5,'text-anchor':'end'}));}
  b.forEach((n,i)=>{if(n)s.appendChild(tip(el('rect',{x:mL+i*bw+.8,y:Y(n),
    width:bw-1.6,height:H-mB-Y(n),fill:cssv('--acc'),'fill-opacity':.75,rx:1}),
    pc(hi*i/NB,1)+' – '+pc(hi*(i+1)/NB,1)+' : '+n));});
  s.appendChild(el('line',{class:'ax',x1:mL,x2:W-mR,y1:H-mB,y2:H-mB}));
  for(let i=0;i<=hi;i++)
    s.appendChild(txt(i+'%',{class:'tk',x:X(i),y:H-mB+14,'text-anchor':'middle'}));
  s.appendChild(el('line',{class:'refl',x1:X(D.lts),x2:X(D.lts),y1:mT-4,y2:H-mB}));
  s.appendChild(txt(t('ax_ward'),{class:'lbl',x:(mL+W-mR)/2,y:H-4,'text-anchor':'middle'}));
}
$('segcat').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
  catF=b.dataset.c;[...$('segcat').children].forEach(x=>x.setAttribute('aria-pressed',x===b));
  drawScat();});

/* ---------------- may tinh ---------------- */
const SZ=['0-40','40-60','60-80','80-120','120-200','200-+'];
const M2={'0-40':32,'40-60':52,'60-80':70,'80-120':95,'120-200':150,'200-+':260};
function fillSelect(){
  const keep=$('sel').value;
  const ord=D.cells.map((c,i)=>i).sort((a,b)=>{const A=D.cells[a],B=D.cells[b];
    return DN(A.q).localeCompare(DN(B.q),LOC())||CN(A.c).localeCompare(CN(B.c),LOC())
      ||SZ.indexOf(A.d)-SZ.indexOf(B.d);});
  $('sel').innerHTML='<option value="-1">'+t('own')+'</option>'+
    ord.map(i=>{const c=D.cells[i];
      return '<option value="'+i+'">'+DN(c.q)+' · '+CN(c.c)+' · '+c.d+' m² — '
        +pc(c.rong)+' ('+(c.nb+c.nt)+')</option>';}).join('');
  $('sel').value=keep||'-1';
}
const parseN=s=>+String(s).replace(/\D/g,'')||0;
const setN=(id,v)=>$(id).value=nf(Math.round(v));
function calc(){
  const gia=parseN($('gia').value),thue=parseN($('thue').value);
  const vay=+$('vay').value/100,lv=+$('lv').value/100,lt=+$('lt').value/100;
  const bt=+$('bt').value,bh=+$('bh').value/100;
  $('vv').textContent=(vay*100)+'%';$('lvv').textContent=dec(lv*100)+'%';
  $('ltv').textContent=dec(lt*100)+'%';$('btv').textContent=dec(bt,1)+' '+t('mo');
  $('bhv').textContent=dec(bh*100)+'%';
  if(!gia)return;
  const gop=thue*12/gia*100,thuc=thue*12*(1-bt/12);
  const rongV=thuc-thuc*D.gd.thue_cho_thue-gia*bh,rong=rongV/gia*100;
  const dt=(rongV-gia*vay*lv)/12,nh=gia*lt/12,nam=rong>0?100/rong:Infinity;
  const tang=vay*lv*100+(1-vay)*lt*100-rong;
  $('o_gop').textContent=pc(gop);
  $('o_rong').textContent=pc(rong);
  $('o_rong').style.color=rong<lt*100?'var(--neg)':'var(--pos)';
  $('o_nam').textContent=isFinite(nam)?Math.round(nam)+' '+t('yrs'):t('never');
  $('o_dt').textContent=(dt>=0?'+':'−')+money(Math.abs(dt));
  $('o_dt').style.color=dt>=0?'var(--pos)':'var(--neg)';
  $('o_nh').textContent='+'+money(nh);$('o_nh').style.color='var(--pos)';
  $('o_tang').textContent=pc(tang);
  $('verdict').innerHTML=rong<lt*100
    ?t('vd1')(pc(lt*100-rong),money(nh-dt),pc(tang)):t('vd2')(pc(rong-lt*100));
}
['gia','thue'].forEach(id=>$(id).addEventListener('input',()=>{$('sel').value='-1';calc();}));
['vay','lv','lt','bt','bh'].forEach(id=>$(id).addEventListener('input',calc));
$('sel').addEventListener('change',()=>{const c=D.cells[+$('sel').value];if(!c)return;
  const m=M2[c.d]||70;setN('gia',c.ban*m);setN('thue',c.thue*m);calc();});

/* ---------------- bang ---------------- */
let sk='rong',sd=false;
const COLK=['p','q','c','ban','thue','gop','rong','lo','nb'];
function drawTable(){
  $('thr').innerHTML=t('th').map((h,i)=>
    '<th data-k="'+COLK[i]+'"'+(i>2?' class="n"':'')+'>'+h+'</th>').join('');
  $('thr').querySelectorAll('th').forEach(th=>th.addEventListener('click',()=>{
    const k=th.dataset.k;sd=(k===sk)?!sd:false;sk=k;drawTable();}));
  const rows=D.wards.slice().sort((a,b)=>{const x=a[sk],y=b[sk];
    return (sd?1:-1)*(typeof x==='string'?String(y).localeCompare(String(x),LOC()):y-x);});
  document.querySelector('#wt tbody').innerHTML=rows.map(r=>
    '<tr'+(r.nb<15||r.nt<15?' class="low"':'')+'>'
    +'<td>'+r.p+'</td><td>'+DN(r.q)+'</td><td>'+CN(r.c)+'</td>'
    +'<td class="n">'+dec(r.ban)+'</td><td class="n">'+nf(r.thue)+'</td>'
    +'<td class="n">'+pc(r.gop)+'</td>'
    +'<td class="n" style="color:'+(r.rong<D.lts?'var(--neg)':'var(--pos)')
      +';font-weight:600">'+pc(r.rong)+'</td>'
    +'<td class="n ci2">'+pc(r.lo)+' – '+pc(r.hi)+'</td>'
    +'<td class="n" style="color:var(--ink3)">'+r.nb+'/'+r.nt+'</td></tr>').join('');
}

/* ---------------- doi ngon ngu ---------------- */
let mapLayer=null,mapNames=null;
function drawAll(){drawRank();drawScat();drawHist();}
function bindTips(){
  mapLayer.eachLayer(l=>{
    const n=l.feature.properties.ten,
          r=mapNames[n.toLocaleUpperCase('vi').replace(/\s+/g,' ').trim()];
    l.unbindTooltip();
    l.bindTooltip(r
      ?'<b>'+DN(r.ten)+'</b><br>'+t('r_net')+' '+pc(r.rong)
        +' <span style="opacity:.6">('+pc(r.lo)+'–'+pc(r.hi)+')</span><br>'
        +t('r_gross')+' '+pc(r.gop)+' · '+nf(r.n)
      :'<b>'+DN(n)+'</b><br><span style="opacity:.6">'+t('nodata')+'</span>',
      {sticky:true,className:'dtip',opacity:1});});
}
function setLang(l){
  L=l;localStorage.setItem('ry_lang',l);
  document.documentElement.lang=l;document.title=t('title');
  document.querySelectorAll('[data-t]').forEach(e=>e.textContent=t(e.dataset.t));
  document.querySelectorAll('[data-th]').forEach(e=>e.innerHTML=t(e.dataset.th));
  document.querySelectorAll('.lang button').forEach(b=>
    b.setAttribute('aria-pressed',b.dataset.l===l));
  const u=t('unit_yr');
  const rent=D.kpi.rong, dep=D.lts, mx=Math.max(rent,dep);
  $('c_rent').innerHTML=dec(rent,2)+'<small>'+u+'</small>';
  $('c_dep').innerHTML=dec(dep,2)+'<small>'+u+'</small>';
  $('bar_rent').style.width=(rent/mx*100)+'%';
  $('bar_dep').style.width=(dep/mx*100)+'%';
  $('c_gap').innerHTML=t('h_gap')(dec(D.kpi.chenh,2)+' '+t('unit_pp'),dec(dep/rent,1));
  $('s_gross_v').innerHTML=dec(D.kpi.gop,2)+'<small>'+u+'</small>';
  $('s_pay_v').innerHTML=D.kpi.nam+'<small>'+t('unit_years')+'</small>';
  const lo=D.dist[D.dist.length-1],hi=D.dist[0];
  /* bo khoang trang quanh gach ngang cho vua o hep */
  $('s_rng_v').innerHTML=dec(lo.rong,2)+'–'+dec(hi.rong,2)+'<small>%</small>';
  $('s_rng_s').textContent=t('s_rng_s')(D.dist.length);
  $('s1').textContent=nf(D.n.clean);$('s2').textContent=nf(D.n.raw);
  $('s3').textContent=nf(D.n.wards);
  $('h_hist').textContent=nf(D.n.wards)+' '+t('s_cells');
  $('meth').innerHTML=t('meth')(D);$('lim').innerHTML=t('lim');
  $('lg_lo').textContent=pc(Math.min(...D.dist.map(d=>d.rong)));
  $('lg_hi').textContent=pc(Math.max(...D.dist.map(d=>d.rong)));
  /* Dinh dang lai o nhap so theo locale moi: EN dung 1,234,567 con VI dung 1.234.567 */
  {const g=parseN($('gia').value),h=parseN($('thue').value);
   if(g)setN('gia',g); if(h)setN('thue',h);}
  fillSelect();drawTable();drawAll();calc();
  if(mapLayer)bindTips();
}
document.querySelectorAll('.lang button').forEach(b=>
  b.addEventListener('click',()=>setLang(b.dataset.l)));

/* ---------------- ban do ---------------- */
window.addEventListener('DOMContentLoaded',function(){
  const LF=window.L;
  if(!LF||!LF.map){$('map').innerHTML='<div style="padding:20px;color:#bbb;font-size:12.5px">'
    +t('nomap')+'</div>';return;}
  const kh=s=>s.toLocaleUpperCase('vi').replace(/\s+/g,' ').trim();
  mapNames={};D.dist.forEach(d=>mapNames[kh(d.ten)]=d);
  const vals=D.dist.map(d=>d.rong),lo=Math.min(...vals),hi=Math.max(...vals);
  /* Dai BA CHANG lua mi -> dat set -> dat nung dam.
     Mot sac thuan khong du: khoang gia tri chi tu 1,06 den 2,06% nen cac quan
     gan nhu trung mau, va dau nhat gan trang thi phu len anh ve tinh la bay mat.
     Ba chang cho tach bach ro hon ma van nam trong ho mau am, khong thanh cau vong. */
  const RAMP=[[224,196,143],[196,116,75],[122,46,24]];
  const color=v=>{
    const p=Math.max(0,Math.min(1,(v-lo)/(hi-lo||1)))*(RAMP.length-1);
    const i=Math.min(RAMP.length-2,Math.floor(p)),f=p-i;
    return 'rgb('+RAMP[i].map((c,j)=>Math.round(c+(RAMP[i+1][j]-c)*f)).join(',')+')';};
  const HCM=LF.latLngBounds(D.bounds),VN=LF.latLngBounds([[8.2,102.1],[23.5,109.6]]);
  const map=LF.map('map',{zoomControl:false,scrollWheelZoom:true,zoomSnap:.25});
  map.fitBounds(VN);   /* PHAI dat khung nhin truoc khi them bat ky lop nao */
  LF.control.zoom({position:'bottomright'}).addTo(map);window._map=map;
  const bases={};
  bases[t('m_sat')]=LF.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {maxZoom:18,attribution:'Imagery &copy; Esri, Maxar'});
  bases[t('m_str')]=LF.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    {maxZoom:19,attribution:'&copy; OpenStreetMap &copy; CARTO'});
  bases[t('m_dark')]=LF.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    {maxZoom:19,attribution:'&copy; OpenStreetMap &copy; CARTO'});
  bases[t('m_sat')].addTo(map);
  LF.control.layers(bases,null,{position:'topright'}).addTo(map);
  mapLayer=LF.geoJSON(D.geo,{
    style:f=>{const r=mapNames[kh(f.properties.ten)];
      return r?{color:'#fff',weight:1,opacity:.8,fillColor:color(r.rong),fillOpacity:.78}
              :{color:'#fff',weight:1,opacity:.35,fillColor:'#8a8a8a',fillOpacity:.35};},
    onEachFeature:(f,l)=>{
      l.on('mouseover',()=>l.setStyle({weight:2.5,fillOpacity:.92}));
      l.on('mouseout',()=>mapLayer.resetStyle(l));
      l.on('click',()=>map.flyToBounds(l.getBounds(),{padding:[20,20],duration:.7}));}
    }).addTo(map);
  bindTips();
  /* Khung mac dinh khop theo cac quan CO du lieu: Can Gio va Cu Chi rat rong va
     deu trong, khop ca chung se lam loi do thi teo lai o giua. */
  const LOI=LF.latLngBounds([]);
  mapLayer.eachLayer(l=>{if(mapNames[kh(l.feature.properties.ten)])LOI.extend(l.getBounds());});
  const ping=LF.marker(HCM.getCenter(),{interactive:false,icon:LF.divIcon({className:'',
    html:'<div class="ping"><span class="pinglbl">HCMC</span></div>',
    iconSize:[12,12],iconAnchor:[6,6]})});
  const PAD={padding:[22,22]};let view='vn';
  const toVN=()=>{view='vn';map.flyToBounds(VN,{duration:1.1});ping.addTo(map);};
  const toHCM=()=>{view='hcm';map.flyToBounds(LOI,{padding:[22,22],duration:1.3});
    map.removeLayer(ping);};
  $('b_vn').onclick=toVN;$('b_hcm').onclick=toHCM;
  /* Chi goi khi khung THAT SU doi kich thuoc: goi vo to va se lam dut hoat anh bay
     va ban do dung lai o mot muc zoom sai. */
  const me=$('map');let last='';
  const fit=()=>{const k=me.clientWidth+'x'+me.clientHeight;if(k===last)return;last=k;
    map.invalidateSize({animate:false});map.fitBounds(view==='vn'?VN:LOI,view==='vn'?{}:PAD);};
  new ResizeObserver(fit).observe(me);fit();
  ping.addTo(map);setTimeout(toHCM,1500);
});

/* ---------------- khoi dong ---------------- */
$('vay').value=D.gd.ty_le_vay*100;$('lv').value=D.gd.lai_vay_tha_noi*100;
$('lt').value=D.lts;$('bt').value=D.gd.bo_trong_thang;$('bh').value=1.0;
setLang(L);
/* Mac dinh KHONG lay o dau tien khop dieu kien (hoa ra la Quan 1, dat va it dai
   dien) ma lay o NHIEU TIN NHAT. */
{const u=D.cells.map((c,i)=>[c,i]).filter(x=>isApt(x[0].c)&&x[0].d==='60-80');
 u.sort((a,b)=>(b[0].nb+b[0].nt)-(a[0].nb+a[0].nt));
 $('sel').value=String(u.length?u[0][1]:0);$('sel').dispatchEvent(new Event('change'));}
/* Ve dong bo. KHONG dung requestAnimationFrame cho lan ve dau: trinh duyet tam
   dung rAF khi tab dang an, bieu do se trong tron cho toi khi nguoi dung mo tab. */
addEventListener('load',drawAll);
let rt;new ResizeObserver(()=>{clearTimeout(rt);rt=setTimeout(drawAll,120);})
  .observe(document.querySelector('.app'));
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',drawAll);
</script>
</body>
</html>
"""

I18N_PATH = ROOT / "src" / "i18n.js"
html = (PAGE
        .replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
        .replace("__I18N__", I18N_PATH.read_text(encoding="utf-8")))

WEB.mkdir(parents=True, exist_ok=True)
(WEB / "dashboard.html").write_text(html, encoding="utf-8")
for f in ("yield_by_ward.json", "yield_by_district_size.json", "district_ci.json",
          "district_en.json", "financial_summary.json", "clean_report.json"):
    (WEB / f).write_text((OUT / f).read_text(encoding="utf-8"), encoding="utf-8")

print(f"docs/dashboard.html  ({(WEB / 'dashboard.html').stat().st_size / 1024:.0f} KB)")
print(f"  song ngu EN/VI · {len(dists)} quan · {len(cells)} o · {len(wards)} phuong")
print(f"  KTC cap quan rong trung vi {CI_W:.2f} diem")
