"""Trang chu (web/index.html) — gioi thieu du an, dan vao dashboard.html.

Cung he thong thiet ke voi bang dieu khien (Inter + IBM Plex Mono, dat nung /
xanh muc / hoang tho, nen trang am) nhung bo cuc kieu TRANG BAO, khong phai luoi
bang dieu khien: co cot chu doc duoc, khoang tho rong hon, mot hinh chu dao.

Chay: python src/build_home.py   ->  web/index.html
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
WEB = ROOT / "web"

fin = json.loads((OUT / "financial_summary.json").read_text(encoding="utf-8"))
clean = json.loads((OUT / "clean_report.json").read_text(encoding="utf-8"))
dists = json.loads((OUT / "district_ci.json").read_text(encoding="utf-8"))

D = {
    "rent": round(fin["ti_suat_rong_trung_vi"], 2),
    "dep": fin["lai_tiet_kiem_pct"],
    "gross": round(fin["ti_suat_gop_trung_vi"], 2),
    "gap": round(fin["chenh_lech_diem"], 2),
    "nd": len(dists),
    "clean": clean["giu_lai"], "raw": clean["tong_dong_vao"],
}

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HCMC Rental Yield</title>
<meta name="description" content="45,084 for-sale and for-rent listings in Ho Chi Minh City: net rental yield 1.51%/yr against a 6.0% bank deposit.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico" sizes="16x16 32x32 48x48">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#1A1714">
<meta property="og:type" content="website">
<meta property="og:title" content="Buying to let in HCMC earns less than a bank deposit">
<meta property="og:description" content="45,084 listings across 20 districts. Net rental yield 1.51%/yr against 6.00% on a 12-month deposit.">
<meta property="og:image" content="og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --acc:#A8432A; --acc2:#B07C2B; --ref:#1F5E5B;
  --page:#F5F2ED; --panel:#FFFDFA; --line:#DDD6CC; --line2:#EDE8E0;
  --ink:#1A1714; --ink2:#5C554C; --ink3:#7A7268;
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root{--page:#131211;--panel:#1B1917;--line:#2E2B27;--line2:#252220;
        --ink:#EBE7E1;--ink2:#A29A90;--ink3:#8A8279;
        --acc:#CC6242; --acc2:#C99A46; --ref:#4E9C93}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);
  font:400 15px/1.65 var(--sans);-webkit-font-smoothing:antialiased;
  font-feature-settings:"cv05" 1,"cv11" 1,"ss01" 1}
h1,h2,h3{margin:0;font-weight:600;letter-spacing:-.018em}
p{margin:0 0 12px}
a{color:inherit}
.wrap{max-width:980px;margin:0 auto;padding:0 22px}

/* ---------- thanh dieu huong ---------- */
.nav{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--page) 88%,transparent);
  backdrop-filter:saturate(150%) blur(9px);border-bottom:1px solid var(--line)}
.nav .in{max-width:980px;margin:0 auto;padding:0 22px;height:52px;display:flex;
  align-items:center;gap:13px}
.mk{display:flex;flex-direction:column;gap:2.5px;width:19px}
.mk i{height:4px;border-radius:1px;display:block}
.mk i:first-child{width:7px;background:var(--acc)}
.mk i:last-child{width:19px;background:var(--ref)}
.nav b{font-size:14px;font-weight:600;letter-spacing:-.01em}
.nav .sp{margin-left:auto;display:flex;align-items:center;gap:16px}
.nav a.lk{font-size:13px;color:var(--ink2);text-decoration:none}
.nav a.lk:hover{color:var(--ink)}
@media(max-width:620px){.nav a.lk{display:none}}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.lang button{font:500 11px/1 var(--sans);letter-spacing:.04em;padding:6px 9px;border:0;
  cursor:pointer;background:transparent;color:var(--ink3)}
.lang button+button{border-left:1px solid var(--line)}
.lang button[aria-pressed=true]{background:var(--ink);color:var(--page)}

/* ---------- hero ---------- */
.hero{padding:76px 0 60px;border-bottom:1px solid var(--line)}
.kick{font:500 11px/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:20px}
h1{font-size:clamp(31px,5.4vw,52px);line-height:1.1;max-width:16ch}
/* dong dau mau muc, dong sau mau nhan — cau co cho ngoat, khong phai
   ca khoi cung mot mau */
h1 span{display:block}
h1 span+span{color:var(--acc)}
.lede{margin:22px 0 34px;font-size:17px;line-height:1.65;color:var(--ink2);max-width:62ch}
.cmp{display:grid;grid-template-columns:max-content 1fr max-content;
  column-gap:14px;row-gap:11px;align-items:center;max-width:660px}
.cn{font:600 30px/1 var(--mono);letter-spacing:-.03em;text-align:right;white-space:nowrap}
.cn small{font:500 12px/1 var(--sans);color:var(--ink3);margin-left:2px}
.cn.a{color:var(--acc)} .cn.b{color:var(--ref)}
.cb{height:15px;background:var(--line2);border-radius:2px;position:relative;overflow:hidden}
.cb i{position:absolute;left:0;top:0;bottom:0;border-radius:2px;display:block;
  animation:grow .9s cubic-bezier(.22,1,.36,1) both}
@keyframes grow{from{width:0!important}}
.cc{font-size:12px;color:var(--ink3);white-space:nowrap}
@media(max-width:640px){.cmp{grid-template-columns:max-content 1fr}.cc{display:none}}
.gap{margin:20px 0 30px;font-size:15px;color:var(--ink2);max-width:62ch}
.gap b{font-family:var(--mono);font-weight:600;color:var(--ink)}
.cta{display:flex;gap:11px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;font:500 14px/1 var(--sans);
  padding:12px 18px;border-radius:3px;text-decoration:none;border:1px solid transparent}
.btn.p{background:var(--acc);color:#fff}
.btn.p:hover{filter:brightness(1.08)}
.btn.s{border-color:var(--line);color:var(--ink2)}
.btn.s:hover{border-color:var(--ink3);color:var(--ink)}

/* ---------- muc ---------- */
section{padding:56px 0;border-bottom:1px solid var(--line)}
.st{font:500 11px/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:9px}
h2{font-size:clamp(22px,3vw,30px);line-height:1.2;margin-bottom:10px}
.sub{color:var(--ink2);max-width:62ch;margin-bottom:30px}

.f3{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
@media(max-width:820px){.f3{grid-template-columns:1fr;gap:24px}}
.f3 .n{font:600 42px/1 var(--mono);letter-spacing:-.035em;color:var(--acc)}
.f3 .n small{font:500 13px/1 var(--sans);color:var(--ink3);margin-left:4px;letter-spacing:0}
.f3 h3{font-size:14px;margin:11px 0 6px}
.f3 p{font-size:13.5px;line-height:1.65;color:var(--ink2);margin:0}

.steps{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:3px;overflow:hidden}
@media(max-width:760px){.steps{grid-template-columns:1fr}}
.steps>div{background:var(--panel);padding:20px 22px}
.steps .no{font:500 11px/1 var(--mono);color:var(--acc);margin-bottom:9px}
.steps h3{font-size:15px;margin-bottom:7px}
.steps p{font-size:13.5px;line-height:1.65;color:var(--ink2);margin:0}

.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}
@media(max-width:820px){.cards{grid-template-columns:1fr}}
.cards a{background:var(--panel);border:1px solid var(--line);border-radius:3px;
  padding:18px 19px;text-decoration:none;display:block;transition:border-color .15s}
.cards a:hover{border-color:var(--acc)}
.cards h3{font-size:14.5px;margin-bottom:6px}
.cards p{font-size:13px;line-height:1.6;color:var(--ink2);margin:0}
.cards .go{font:500 12px var(--mono);color:var(--acc);margin-top:11px;display:block}

.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--acc2);
  border-radius:3px;padding:20px 22px;max-width:70ch}
.note p{font-size:14px;line-height:1.7;color:var(--ink2);margin:0 0 12px}
.note a{font:500 13px var(--sans);color:var(--acc);text-decoration:none}
.note a:hover{text-decoration:underline}

.files{display:flex;flex-wrap:wrap;gap:8px}
.files a{font:400 12.5px var(--mono);padding:7px 11px;border:1px solid var(--line);
  border-radius:3px;text-decoration:none;color:var(--ink2);background:var(--panel)}
.files a:hover{border-color:var(--ink3);color:var(--ink)}
footer{padding:26px 0 60px;font-size:12.5px;color:var(--ink3)}
footer b{color:var(--ink2)}
</style>
</head>
<body>

<div class="nav"><div class="in">
  <span class="mk"><i></i><i></i></span>
  <b>HCMC Rental Yield</b>
  <div class="sp">
    <a class="lk" href="dashboard.html" data-h="nav_dash"></a>
    <a class="lk" href="#how" data-h="nav_meth"></a>
    <a class="lk" href="#data" data-h="nav_data"></a>
    <div class="lang">
      <button data-l="en" aria-pressed="true">EN</button>
      <button data-l="vi" aria-pressed="false">VI</button>
    </div>
  </div>
</div></div>

<div class="wrap">

  <div class="hero">
    <div class="kick" data-h="kick"></div>
    <h1><span data-h="h1a"></span><span data-h="h1b"></span></h1>
    <p class="lede" data-h="lede"></p>

    <div class="cmp">
      <span class="cn a" id="n_rent"></span>
      <span class="cb"><i id="b_rent" style="background:var(--acc)"></i></span>
      <span class="cc" data-h="bar_rent"></span>
      <span class="cn b" id="n_dep"></span>
      <span class="cb"><i id="b_dep" style="background:var(--ref)"></i></span>
      <span class="cc" data-h="bar_dep"></span>
    </div>

    <p class="gap" id="gap"></p>
    <div class="cta">
      <a class="btn p" href="dashboard.html"><span data-h="cta"></span> →</a>
      <a class="btn s" href="#how" data-h="cta2"></a>
    </div>
  </div>

  <section>
    <div class="st">01</div><h2 data-h="f_title"></h2>
    <div class="f3" style="margin-top:26px">
      <div><div class="n"><span data-h="f1n"></span><small data-h="f1u"></small></div>
        <h3 data-h="f1"></h3><p data-h="f1t"></p></div>
      <div><div class="n"><span data-h="f2n"></span><small data-h="f2u"></small></div>
        <h3 data-h="f2"></h3><p data-h="f2t"></p></div>
      <div><div class="n"><span data-h="f3n"></span><small data-h="f3u"></small></div>
        <h3 data-h="f3"></h3><p data-h="f3t"></p></div>
    </div>
  </section>

  <section id="how">
    <div class="st">02</div><h2 data-h="h_title"></h2>
    <p class="sub" data-h="h_sub"></p>
    <div class="steps">
      <div><div class="no">01</div><h3 data-h="h1"></h3><p data-h="h1t"></p></div>
      <div><div class="no">02</div><h3 data-h="h2"></h3><p data-h="h2t"></p></div>
      <div><div class="no">03</div><h3 data-h="h3"></h3><p data-h="h3t"></p></div>
      <div><div class="no">04</div><h3 data-h="h4"></h3><p data-h="h4t"></p></div>
    </div>
  </section>

  <section>
    <div class="st">03</div><h2 data-h="w_title"></h2>
    <div class="cards" style="margin-top:26px">
      <a href="dashboard.html"><h3 data-h="w1"></h3><p data-h="w1t"></p><span class="go">→</span></a>
      <a href="dashboard.html"><h3 data-h="w2"></h3><p data-h="w2t"></p><span class="go">→</span></a>
      <a href="dashboard.html"><h3 data-h="w3"></h3><p data-h="w3t"></p><span class="go">→</span></a>
    </div>
  </section>

  <section>
    <div class="st">04</div><h2 data-h="l_title"></h2>
    <div class="note" style="margin-top:22px">
      <p data-h="l_t"></p>
      <a href="dashboard.html" data-h="l_link"></a>
    </div>
  </section>

  <section id="data" style="border-bottom:0">
    <div class="st">05</div><h2 data-h="d_title"></h2>
    <p class="sub" data-h="d_t"></p>
    <div class="files">
      <a href="yield_by_ward.json"><span data-h="d1"></span> · json</a>
      <a href="yield_by_district_size.json"><span data-h="d2"></span> · json</a>
      <a href="district_ci.json"><span data-h="d3"></span> · json</a>
      <a href="financial_summary.json"><span data-h="d4"></span> · json</a>
      <a href="clean_report.json"><span data-h="d5"></span> · json</a>
    </div>
  </section>

  <footer data-hh="foot"></footer>
</div>

<script>
const D=__DATA__;
__I18N__
let L=localStorage.getItem('ry_lang')||'en';
const dec=(v,d=2)=>L==='en'?v.toFixed(d):v.toFixed(d).replace('.',',');
function setLang(l){
  L=l;localStorage.setItem('ry_lang',l);
  document.documentElement.lang=l;document.title=H[l].title;
  document.querySelectorAll('[data-h]').forEach(e=>e.textContent=H[l][e.dataset.h]);
  document.querySelectorAll('[data-hh]').forEach(e=>e.innerHTML=H[l][e.dataset.hh]);
  document.querySelectorAll('.lang button').forEach(b=>
    b.setAttribute('aria-pressed',b.dataset.l===l));
  const u=l==='en'?'%/yr':'%/năm';
  document.getElementById('n_rent').innerHTML=dec(D.rent)+'<small>'+u+'</small>';
  document.getElementById('n_dep').innerHTML=dec(D.dep)+'<small>'+u+'</small>';
  document.getElementById('gap').innerHTML=l==='en'
    ? 'A deposit pays <b>'+dec(D.dep/D.rent,1)+'×</b> more — a gap of <b>'+dec(D.gap)
      +' points</b> every year, before the property has appreciated a single dong.'
    : 'Gửi ngân hàng lời gấp <b>'+dec(D.dep/D.rent,1)+' lần</b> — chênh <b>'+dec(D.gap)
      +' điểm</b> mỗi năm, khi giá nhà còn chưa tăng đồng nào.';
}
document.querySelectorAll('.lang button').forEach(b=>
  b.addEventListener('click',()=>setLang(b.dataset.l)));
setLang(L);
/* dat be rong thanh sau khi da dat chu, de hoat anh chay tu 0 */
const mx=Math.max(D.rent,D.dep);
document.getElementById('b_rent').style.width=(D.rent/mx*100)+'%';
document.getElementById('b_dep').style.width=(D.dep/mx*100)+'%';
</script>
</body>
</html>
"""

html = (PAGE
        .replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":")))
        .replace("__I18N__", (ROOT / "src" / "i18n_home.js").read_text(encoding="utf-8")))
WEB.mkdir(parents=True, exist_ok=True)
(WEB / "index.html").write_text(html, encoding="utf-8")
print(f"web/index.html  ({(WEB / 'index.html').stat().st_size / 1024:.0f} KB)")
