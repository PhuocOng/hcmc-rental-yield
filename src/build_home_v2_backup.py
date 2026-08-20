"""Trang chu (web/index.html) — hero cuon-tua video + gioi thieu du an.

HERO CUON-TUA: mot file MP4 duy nhat, tai ve dang Blob, roi keo `currentTime`
theo vi tri cuon. KHONG dung chuoi anh JPG (nang gap ~3 lan). Video phai duoc
nen voi keyframe day (`-g 8 -keyint_min 8`) thi tua moi tuc thi — xem
`src/make_hero_video.py`.

Bon diem ky thuat, thieu cai nao cung hong:
  1. Tai CA file thanh Blob truoc. De trinh duyet tu xin tung doan qua HTTP Range
     thi tua qua tua lai se kep.
  2. Noi suy thoi gian trong vong lap rAF, khong gan thang. Gan thang thi cuon
     nhanh se nhay coc.
  3. Chan lenh tua chong nhau. Gui lenh tua moi khi lenh cu chua xong -> video
     treo cung. Kem thoi gian cho toi da de khong ket vinh vien.
  4. Chi ghi vao DOM khi gia tri THAT SU doi.

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
<meta name="theme-color" content="#131211">
<meta property="og:type" content="website">
<meta property="og:title" content="Buying to let in HCMC earns less than a bank deposit">
<meta property="og:description" content="45,084 listings across 20 districts. Net rental yield 1.51%/yr against 6.00% on a 12-month deposit.">
<meta property="og:image" content="og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" as="image" href="assets/hero-poster.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --acc:#A8432A; --acc2:#B07C2B; --ref:#1F5E5B;
  --page:#F5F2ED; --panel:#FFFDFA; --line:#DDD6CC; --line2:#EDE8E0;
  --ink:#1A1714; --ink2:#5C554C; --ink3:#7A7268;
  --void:#131211;                 /* nen cua khoi hero, trung mau nen video */
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
.nav{position:fixed;top:0;left:0;right:0;z-index:60;height:52px;
  background:rgba(19,18,17,0);border-bottom:1px solid transparent;
  transition:background .35s ease,border-color .35s ease,backdrop-filter .35s ease}
.nav.on{background:color-mix(in srgb,var(--page) 86%,transparent);
  backdrop-filter:saturate(150%) blur(10px);border-bottom-color:var(--line)}
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
/* Khi con nam tren hero toi, chu nav phai sang de doc duoc */
.nav.dark b,.nav.dark a.lk{color:rgba(255,255,255,.82)}
.nav.dark .lang{border-color:rgba(255,255,255,.22)}
.nav.dark .lang button{color:rgba(255,255,255,.6)}
.nav.dark .lang button[aria-pressed=true]{background:rgba(255,255,255,.92);color:#131211}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden;
  transition:border-color .35s}
.lang button{font:500 11px/1 var(--sans);letter-spacing:.04em;padding:6px 9px;border:0;
  cursor:pointer;background:transparent;color:var(--ink3);transition:color .35s,background .35s}
.lang button+button{border-left:1px solid var(--line)}
.lang button[aria-pressed=true]{background:var(--ink);color:var(--page)}

/* ================= HERO CUON-TUA ================= */
.scrub{position:relative;height:460vh;background:var(--void)}
.stick{position:sticky;top:0;height:100vh;overflow:hidden;background:var(--void)}
#hv{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  opacity:0;transition:opacity .6s ease}
#hv.ready{opacity:1}
.poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.9}
/* Man loc giu chu doc duoc tren footage that, va lam mep video tan vao nen */
.veil{position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(19,18,17,.82) 0%,rgba(19,18,17,.45) 32%,
    rgba(19,18,17,.45) 62%,rgba(19,18,17,.9) 100%)}
.beats{position:absolute;inset:0;display:grid;place-items:center;padding:0 24px}
.beat{grid-area:1/1;max-width:820px;width:100%;text-align:center;
  color:#fff;opacity:0;transform:translateY(18px);will-change:opacity,transform;
  text-shadow:0 1px 24px rgba(0,0,0,.55)}
.beat .kick{font:500 11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:rgba(255,255,255,.55);margin-bottom:20px}
.beat h1{font-size:clamp(32px,6vw,62px);line-height:1.08}
.beat h1 em{font-style:normal;color:var(--acc)}
.beat .lede{margin:20px auto 0;font-size:17px;line-height:1.65;
  color:rgba(255,255,255,.72);max-width:56ch}
.beat .big{font:600 clamp(46px,9vw,104px)/1 var(--mono);letter-spacing:-.04em}
.beat .sm{margin-top:14px;font-size:16px;color:rgba(255,255,255,.66);max-width:52ch;
  margin-left:auto;margin-right:auto}

/* thanh so sanh trong beat cuoi */
.cmp{display:grid;grid-template-columns:max-content 1fr max-content;
  column-gap:14px;row-gap:11px;align-items:center;max-width:620px;margin:0 auto;
  text-align:left}
.cn{font:600 30px/1 var(--mono);letter-spacing:-.03em;text-align:right;white-space:nowrap}
.cn small{font:500 12px/1 var(--sans);color:rgba(255,255,255,.5);margin-left:2px}
.cn.a{color:var(--acc)} .cn.b{color:var(--ref)}
.cb{height:15px;background:rgba(255,255,255,.14);border-radius:2px;position:relative;
  overflow:hidden}
.cb i{position:absolute;left:0;top:0;bottom:0;border-radius:2px;display:block;width:0;
  transition:width .7s cubic-bezier(.22,1,.36,1)}
.cc{font-size:12px;color:rgba(255,255,255,.55);white-space:nowrap}
@media(max-width:640px){.cmp{grid-template-columns:max-content 1fr}.cc{display:none}}
.cta{display:flex;gap:11px;flex-wrap:wrap;justify-content:center;margin-top:28px}
.btn{display:inline-flex;align-items:center;gap:8px;font:500 14px/1 var(--sans);
  padding:13px 20px;border-radius:3px;text-decoration:none;border:1px solid transparent}
.btn.p{background:var(--acc);color:#fff}
.btn.p:hover{filter:brightness(1.1)}
.btn.s{border-color:rgba(255,255,255,.28);color:rgba(255,255,255,.82)}
.btn.s:hover{border-color:#fff;color:#fff}

/* vong tron bao tien do tai video */
.ring{position:absolute;left:50%;bottom:46px;transform:translateX(-50%);
  display:flex;align-items:center;gap:10px;color:rgba(255,255,255,.5);
  font:500 10.5px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;
  transition:opacity .4s}
.ring svg{width:17px;height:17px;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:2}
.ring .bg{stroke:rgba(255,255,255,.16)}
.ring .fg{stroke:var(--acc);stroke-dasharray:44;stroke-dashoffset:44;
  transition:stroke-dashoffset .2s linear}
.hint{position:absolute;left:50%;bottom:44px;transform:translateX(-50%);
  color:rgba(255,255,255,.42);font:500 10.5px/1 var(--mono);letter-spacing:.16em;
  text-transform:uppercase;opacity:0;transition:opacity .5s}
.hint::after{content:"";display:block;width:1px;height:22px;margin:10px auto 0;
  background:linear-gradient(180deg,rgba(255,255,255,.45),transparent)}

/* KHONG CO VIDEO: khoi hero xep thuong, moi beat thanh mot khoi trong luong van */
.scrub.novid{height:auto}
.scrub.novid .stick{position:static;height:auto;padding:104px 0 76px}
.scrub.novid #hv,.scrub.novid .ring,.scrub.novid .hint{display:none}
.scrub.novid .poster{position:absolute;inset:0;height:100%;opacity:.28}
.scrub.novid .beats{position:relative;display:block;max-width:980px;margin:0 auto}
.scrub.novid .beat{opacity:1;transform:none;margin-bottom:64px}
.scrub.novid .beat:last-child{margin-bottom:0}
@media (prefers-reduced-motion:reduce){
  .scrub{height:auto}
  .stick{position:static;height:auto;padding:104px 0 76px}
  #hv,.ring,.hint{display:none}
  .beats{position:relative;display:block;max-width:980px;margin:0 auto}
  .beat{opacity:1;transform:none;margin-bottom:64px}
}

/* ---------- muc ben duoi ---------- */
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

<div class="nav dark" id="nav"><div class="in">
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

<!-- ============ HERO CUON-TUA ============ -->
<div class="scrub" id="scrub">
  <div class="stick">
    <img class="poster" src="assets/hero-poster.jpg" alt="">
    <video id="hv" muted playsinline preload="auto" disablepictureinpicture></video>
    <div class="veil"></div>

    <div class="beats">
      <div class="beat" data-in="0" data-out=".22">
        <div class="kick" data-h="kick"></div>
        <h1><span data-h="h1a"></span> <em data-h="h1b"></em></h1>
        <p class="lede" data-h="lede"></p>
      </div>

      <div class="beat" data-in=".26" data-out=".48">
        <div class="big" data-h="sc1"></div>
        <h1 style="font-size:clamp(24px,3.6vw,38px);margin-top:12px" data-h="sc1b"></h1>
      </div>

      <div class="beat" data-in=".52" data-out=".72">
        <h1 style="font-size:clamp(26px,4.4vw,46px)" data-h="sc2"></h1>
        <p class="sm" data-h="sc2b"></p>
      </div>

      <div class="beat" data-in=".76" data-out="1">
        <h1 style="font-size:clamp(22px,3.4vw,34px);margin-bottom:26px" data-h="sc3"></h1>
        <div class="cmp">
          <span class="cn a" id="n_rent"></span>
          <span class="cb"><i id="b_rent" style="background:var(--acc)"></i></span>
          <span class="cc" data-h="bar_rent"></span>
          <span class="cn b" id="n_dep"></span>
          <span class="cb"><i id="b_dep" style="background:var(--ref)"></i></span>
          <span class="cc" data-h="bar_dep"></span>
        </div>
        <p class="sm" id="gap" style="margin-top:22px"></p>
        <div class="cta">
          <a class="btn p" href="dashboard.html"><span data-h="cta"></span> →</a>
          <a class="btn s" href="#how" data-h="cta2"></a>
        </div>
      </div>
    </div>

    <div class="ring" id="ring">
      <svg viewBox="0 0 16 16"><circle class="bg" cx="8" cy="8" r="7"></circle>
        <circle class="fg" id="rfg" cx="8" cy="8" r="7"></circle></svg>
      <span data-h="loading"></span>
    </div>
    <div class="hint" id="hint" data-h="scroll"></div>
  </div>
</div>

<div class="wrap">
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
      <p data-h="l_t"></p><a href="dashboard.html" data-h="l_link"></a>
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
const $=id=>document.getElementById(id);
const clamp=(v,a,b)=>v<a?a:v>b?b:v;

/* ================= ngon ngu ================= */
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
  $('n_rent').innerHTML=dec(D.rent)+'<small>'+u+'</small>';
  $('n_dep').innerHTML=dec(D.dep)+'<small>'+u+'</small>';
  $('gap').innerHTML=l==='en'
    ? 'A deposit pays <b>'+dec(D.dep/D.rent,1)+'×</b> more, a gap of <b>'+dec(D.gap)
      +' points</b> every year, before the property has appreciated a single dong.'
    : 'Gửi ngân hàng lời gấp <b>'+dec(D.dep/D.rent,1)+' lần</b>, chênh <b>'+dec(D.gap)
      +' điểm</b> mỗi năm, khi giá nhà còn chưa tăng đồng nào.';
}
document.querySelectorAll('.lang button').forEach(b=>
  b.addEventListener('click',()=>setLang(b.dataset.l)));
setLang(L);

/* ================= HERO CUON-TUA ================= */
(function(){
  const SRC='assets/hero-scrub.mp4';
  const scrub=$('scrub'), v=$('hv'), ring=$('ring'), hint=$('hint'), nav=$('nav');
  const beats=[...document.querySelectorAll('.beat')].map(el=>({
    el, a:parseFloat(el.dataset.in), b:parseFloat(el.dataset.out), o:-1, y:-1}));
  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;

  /* Khong co video van phai la mot trang hoan chinh. */
  function giveUp(){ scrub.classList.add('novid'); ring.style.display='none';
    beats.forEach(b=>{b.el.style.opacity=1;b.el.style.transform='none';});
    setBars(1); nav.classList.remove('dark'); }

  function setBars(k){
    const mx=Math.max(D.rent,D.dep);
    $('b_rent').style.width=(D.rent/mx*100*k)+'%';
    $('b_dep').style.width=(D.dep/mx*100*k)+'%';
  }

  /* ---- 1. Tai ca file thanh Blob, co vong tron bao tien do ---- */
  async function load(){
    try{
      const res=await fetch(SRC);
      if(!res.ok) throw new Error(res.status);
      const total=+(res.headers.get('content-length')||0);
      const reader=res.body.getReader(); const chunks=[]; let got=0;
      for(;;){
        const {done,value}=await reader.read();
        if(done) break;
        chunks.push(value); got+=value.length;
        if(total) $('rfg').style.strokeDashoffset=44*(1-got/total);
      }
      v.src=URL.createObjectURL(new Blob(chunks,{type:'video/mp4'}));
      await new Promise((ok,no)=>{
        v.addEventListener('loadedmetadata',ok,{once:true});
        v.addEventListener('error',no,{once:true});
        setTimeout(no,15000);
      });
      v.classList.add('ready');
      ring.style.opacity=0; setTimeout(()=>ring.style.display='none',400);
      hint.style.opacity=1;
      start();
    }catch(e){ giveUp(); }
  }

  /* ---- 2 + 3. Noi suy trong rAF, va chan lenh tua chong nhau ---- */
  let shown=0, target=0, running=false, seeking=false, seekAt=0;
  v.addEventListener('seeked',()=>{seeking=false;});
  function tick(){
    const d=target-shown;
    /* Neu mot lenh tua treo qua 400ms thi bo qua no, khong doi mai */
    if(seeking && performance.now()-seekAt>400) seeking=false;
    if(Math.abs(d)<0.004){ shown=target; running=false;
      if(!seeking){seeking=true;seekAt=performance.now();v.currentTime=shown;} return; }
    shown+=d*0.16;
    if(!seeking){ seeking=true; seekAt=performance.now(); v.currentTime=shown; }
    requestAnimationFrame(tick);
  }

  /* ---- 4. Chi ghi vao DOM khi gia tri THAT SU doi ---- */
  function paint(p){
    for(const b of beats){
      const f=Math.max(0.02,(b.b-b.a)*0.18);
      /* Hai mep phai xu ly rieng: beat DAU (in=0) phai hien san khi vua mo trang,
         beat CUOI (out=1) phai o lai chu khong tan di o day trang. */
      let o;
      if(p<b.a)      o = b.a<=0 ? 1 : 0;
      else if(p>b.b) o = b.b>=1 ? 1 : 0;
      else if(p<b.a+f && b.a>0)  o=(p-b.a)/f;
      else if(p>b.b-f && b.b<1)  o=(b.b-p)/f;
      else o=1;
      o=clamp(o,0,1);
      const y=Math.round((1-o)*18*10)/10, oo=Math.round(o*100)/100;
      if(oo!==b.o){ b.el.style.opacity=oo; b.o=oo; }
      if(y!==b.y){ b.el.style.transform='translateY('+y+'px)'; b.y=y; }
      if(b===beats[beats.length-1]) setBars(oo);
    }
  }

  function onScroll(){
    const r=scrub.getBoundingClientRect();
    const p=clamp(-r.top/(r.height-innerHeight),0,1);
    if(v.duration){ target=p*v.duration*0.999;
      if(!running){ running=true; requestAnimationFrame(tick); } }
    paint(p);
    if(p>0.02) hint.style.opacity=0;
    /* Nav doi mau khi roi khoi vung hero toi */
    const dark=r.bottom>innerHeight*0.6;
    nav.classList.toggle('dark',dark);
    nav.classList.toggle('on',scrollY>40 && !dark);
  }
  function start(){
    addEventListener('scroll',onScroll,{passive:true});
    addEventListener('resize',onScroll);
    onScroll();
  }

  /* cho lo ra de kiem tra tu console (o xem truoc khong phat su kien cuon) */
  window._hero={onScroll,paint,giveUp,state:()=>({shown,target,running,seeking})};

  if(reduce){ giveUp(); }
  else{ load(); paint(0); }
})();
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
vid = WEB / "assets" / "hero-scrub.mp4"
print(f"  video hero: {'co' if vid.exists() else 'CHUA CO'}"
      + (f"  ({vid.stat().st_size / 1024:.0f} KB)" if vid.exists() else ""))
