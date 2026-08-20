"""Trang chu (docs/index.html) — video chay sau TOAN BO trang, cuon toi dau tua toi do.

v3: video khong con la mot hero rieng nua ma nam CO DINH sau ca trang. Tien do
cuon cua toan tai lieu (0 -> 1) anh xa thang sang thoi diem video (0 -> 26,5s),
nen keo den dau cung co chuyen dong. Noi dung noi ben tren tren nhung tam kinh toi.

Video: 6 chang flycam THAT ghep lien tuc, xem `src/make_journey.py`.

Bon diem ky thuat cua co che tua, thieu cai nao cung hong:
  1. Tai CA file thanh Blob truoc. De trinh duyet tu xin tung doan qua HTTP Range
     thi tua qua tua lai se kep.
  2. Noi suy thoi gian trong vong lap rAF, khong gan thang.
  3. Chan lenh tua chong nhau, kem han thoi gian de khong ket vinh vien.
  4. Chi ghi vao DOM khi gia tri THAT SU doi.

Chay: python src/build_home.py   ->  docs/index.html
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
WEB = ROOT / "docs"      # GitHub Pages chi phuc vu tu / hoac /docs

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
<meta name="theme-color" content="#0E0D0C">
<meta property="og:type" content="website">
<meta property="og:title" content="Buying to let in HCMC earns less than a bank deposit">
<meta property="og:description" content="45,084 listings across 20 districts. Net rental yield 1.51%/yr against 6.00% on a 12-month deposit.">
<meta property="og:image" content="https://peter208.com/hcmc-rental-yield/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" as="image" href="assets/hero-poster.jpg" fetchpriority="high">
<!-- KHONG dung <link rel="preload" as="video">: "video" khong phai gia tri hop le
     cua thuoc tinh as, trinh duyet tai rieng mot ban va KHONG ghep duoc voi request
     cua the <video> — thanh ra tai hai lan, ton gap doi bang thong. The <video> voi
     preload="auto" va src dat san la du: metadata nam dau file (+faststart) nen tua
     duoc sau khoang 200ms. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
/* Trang nay LUON toi: co video nam sau tat ca, khong the co ban nen sang. */
:root{
  --acc:#CC6242; --acc2:#C99A46; --ref:#4E9C93;
  --void:#0E0D0C;
  --ink:#F0ECE6; --ink2:#A9A197; --ink3:#7C756C;
  --glass:rgba(19,17,16,.90); --line:rgba(255,255,255,.13); --line2:rgba(255,255,255,.07);
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--void);color:var(--ink);
  font:400 15px/1.65 var(--sans);-webkit-font-smoothing:antialiased;
  font-feature-settings:"cv05" 1,"cv11" 1,"ss01" 1}
h1,h2,h3{margin:0;font-weight:600;letter-spacing:-.018em}
p{margin:0 0 12px}
a{color:inherit}
.wrap{max-width:1000px;margin:0 auto;padding:0 22px}

/* ============ VIDEO NEN, CO DINH SAU TAT CA ============ */
.bg{position:fixed;inset:0;z-index:0;overflow:hidden;background:var(--void);
  will-change:transform}
.bg img,.bg video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
/* will-change phai nam o .bg — transform ap len chinh no. Dat o con thi trinh duyet
   tach them hai lop khong can thiet. */
.bg video{opacity:0;transition:opacity .8s ease}
.bg video.ready{opacity:1}
/* Video da san thi anh nen khong con viec gi — an di de bot mot lop phai gop */
.bg.live img{display:none}
.bg img{opacity:.8}
/* Man loc: giu chu doc duoc, va keo footage lui ve lam ket cau nen */
/* Man loc phu ca khung, doi xung va muot nen doc ra nhu anh sang tu nhien chu
   khong phai mot mang toi. Do net cua footage den tu do phan giai, muc nen va
   bao hoa mau — KHONG den tu viec nhat man loc di, nen cho phep no du toi de
   giu chu doc duoc. */
.bg .veil{position:absolute;inset:0;
  background:radial-gradient(130% 100% at 50% 40%,rgba(14,13,12,.36) 0%,rgba(14,13,12,.62) 58%,
    rgba(14,13,12,.85) 100%)}
main{position:relative;z-index:10}

/* ============ thanh dieu huong ============ */
.nav{position:fixed;top:0;left:0;right:0;z-index:60;height:54px;
  border-bottom:1px solid transparent;transition:background .35s,border-color .35s}
/* Khong dung backdrop-filter o day: nen phia sau la video dang tua nen no phai
   lam mo lai vung do MOI KHUNG HINH. Tren nen toi san, mot lop dac 92% nhin
   gan nhu y het ma gan nhu khong ton gi. */
.nav.on{background:rgba(12,11,10,.92);
  border-bottom-color:var(--line)}
.nav .in{max-width:1000px;margin:0 auto;padding:0 22px;height:54px;display:flex;
  align-items:center;gap:13px}
.mk{display:flex;flex-direction:column;gap:2.5px;width:19px}
.mk i{height:4px;border-radius:1px;display:block}
.mk i:first-child{width:7px;background:var(--acc)}
.mk i:last-child{width:19px;background:var(--ref)}
.nav b{font-size:14px;white-space:nowrap}
.nav .sp{margin-left:auto;display:flex;align-items:center;gap:16px}
/* Nut duy nhat tren nav. Chi con MOT loi keu goi nen no duoc phep noi bat. */
.navcta{display:inline-flex;align-items:center;gap:8px;text-decoration:none;
  background:var(--acc);color:#fff;font:600 12.5px/1 var(--sans);letter-spacing:-.005em;
  padding:10px 15px;border-radius:4px;white-space:nowrap;
  box-shadow:0 2px 14px rgba(204,98,66,.30);
  transition:box-shadow .25s,transform .25s,filter .25s}
.navcta:hover{filter:brightness(1.1);box-shadow:0 5px 22px rgba(204,98,66,.48);
  transform:translateY(-1px)}
.navcta i{font-style:normal;transition:transform .25s}
.navcta:hover i{transform:translateX(3px)}
/* cham nhip nho, bao rang ben trong co thu dang song */
.navcta .dot{width:6px;height:6px;border-radius:50%;background:#fff;opacity:.9;
  animation:beat 2.4s ease-in-out infinite}
@keyframes beat{0%,100%{opacity:.35;transform:scale(.8)}50%{opacity:1;transform:scale(1)}}
/* Man hep: an DONG TIEU DE chu khong an nhan cua nut. Bieu tuong ben trai van
   du de nhan ra trang, con nut ma mat chu thi khong ai biet no dan di dau. */
@media(max-width:560px){.nav b{display:none}.navcta{padding:10px 13px}}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.lang button{font:500 11px/1 var(--sans);letter-spacing:.04em;padding:6px 9px;border:0;
  cursor:pointer;background:transparent;color:var(--ink3)}
.lang button+button{border-left:1px solid var(--line)}
.lang button[aria-pressed=true]{background:var(--ink);color:var(--void)}

/* ============ cac man mo dau ============ */
.beat{min-height:100vh;display:grid;place-items:center;padding:80px 24px;text-align:center}
.beat>div{max-width:840px;width:100%;position:relative;
  opacity:0;transform:translateY(26px);transition:opacity .9s cubic-bezier(.22,1,.36,1),
  transform .9s cubic-bezier(.22,1,.36,1)}
/* KHONG dat mang toi sau chu: no hien thanh mot vet bau duc lu lu tren may.
   Chi dung do bong nhieu lop — bong om sat net chu nen tach duoc chu khoi nen
   ma khong tao ra hinh khoi nao nhin thay duoc. */
.beat.seen>div{opacity:1;transform:none}
/* Tren footage sang, mau chu phu cua giao dien qua chim — dung mau sang rieng */
.beat .kick{font:600 11px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;
  color:rgba(255,255,255,.82);margin-bottom:22px;
  text-shadow:0 1px 2px rgba(0,0,0,.95),0 1px 8px rgba(0,0,0,.85)}
.beat h1{font-size:clamp(32px,6.2vw,64px);line-height:1.06;
  text-shadow:0 1px 2px rgba(0,0,0,.92),0 2px 10px rgba(0,0,0,.78),0 6px 34px rgba(0,0,0,.6)}
/* Dat nung goc lan vao may hoang hon vi cung tong am — sang len va vien toi de tach */
.beat h1 em{font-style:normal;color:#F79E77;
  text-shadow:0 1px 2px rgba(0,0,0,.92),0 2px 10px rgba(0,0,0,.78),0 6px 34px rgba(0,0,0,.6)}
.beat .lede{margin:22px auto 0;font-size:17px;line-height:1.7;max-width:56ch;
  color:rgba(255,255,255,.93);text-shadow:0 1px 2px rgba(0,0,0,.95),0 1px 8px rgba(0,0,0,.85)}
.beat .big{font:600 clamp(50px,10vw,116px)/1 var(--mono);letter-spacing:-.045em;
  text-shadow:0 1px 2px rgba(0,0,0,.92),0 2px 10px rgba(0,0,0,.78),0 6px 34px rgba(0,0,0,.6)}
.beat .sm{margin-top:16px;font-size:16px;max-width:52ch;margin-left:auto;margin-right:auto;
  color:rgba(255,255,255,.92);text-shadow:0 1px 2px rgba(0,0,0,.95),0 1px 8px rgba(0,0,0,.85)}

.cmp{display:grid;grid-template-columns:max-content 1fr max-content;
  column-gap:14px;row-gap:12px;align-items:center;max-width:620px;margin:0 auto;text-align:left}
.cn{font:600 32px/1 var(--mono);letter-spacing:-.03em;text-align:right;white-space:nowrap}
.cn small{font:500 12px/1 var(--sans);color:var(--ink3);margin-left:2px}
.cn.a{color:var(--acc)} .cn.b{color:var(--ref)}
.cb{height:15px;background:rgba(255,255,255,.12);border-radius:2px;position:relative;
  overflow:hidden}
.cb i{position:absolute;left:0;top:0;bottom:0;border-radius:2px;display:block;width:0;
  transition:width 1.1s cubic-bezier(.22,1,.36,1)}
.cc{font-size:12px;color:rgba(255,255,255,.70);white-space:nowrap;
  text-shadow:0 1px 2px rgba(0,0,0,.95),0 1px 8px rgba(0,0,0,.85)}
@media(max-width:640px){.cmp{grid-template-columns:max-content 1fr}.cc{display:none}}
.cta{display:flex;gap:11px;flex-wrap:wrap;justify-content:center;margin-top:30px}
.btn{display:inline-flex;align-items:center;gap:8px;font:500 14px/1 var(--sans);
  padding:14px 21px;border-radius:3px;text-decoration:none;border:1px solid transparent}
.btn.p{background:var(--acc);color:#fff;box-shadow:0 3px 20px rgba(204,98,66,.32)}
.btn.p:hover{filter:brightness(1.12);box-shadow:0 6px 30px rgba(204,98,66,.5);
  transform:translateY(-2px)}
.btn{transition:box-shadow .25s,transform .25s,filter .25s,border-color .25s,color .25s}
.btn.big{font-size:15.5px;font-weight:600;padding:17px 28px}
.btn i{font-style:normal;transition:transform .25s}
.btn:hover i{transform:translateX(4px)}
.ctasub{margin:16px 0 0;font:400 12.5px/1.5 var(--sans);
  color:rgba(255,255,255,.78);text-shadow:0 1px 2px rgba(0,0,0,.95),0 1px 8px rgba(0,0,0,.85)}
.btn.s{border-color:var(--line);color:var(--ink2)}
.btn.s:hover{border-color:var(--ink2);color:var(--ink)}

/* ============ cac muc noi dung, tren tam kinh toi ============ */
section.panel{content-visibility:auto;contain-intrinsic-size:auto 420px;
  background:var(--glass);
  border:1px solid var(--line);border-radius:4px;padding:38px 34px;margin-bottom:14px;
  opacity:0;transform:translateY(30px);
  transition:opacity .8s cubic-bezier(.22,1,.36,1),transform .8s cubic-bezier(.22,1,.36,1)}
section.panel.seen{opacity:1;transform:none}
@media(max-width:640px){section.panel{padding:26px 20px}}
.st{font:600 11px/1 var(--mono);letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink3);margin-bottom:9px}
h2{font-size:clamp(22px,3vw,31px);line-height:1.2;margin-bottom:10px}
.sub{color:var(--ink2);max-width:62ch;margin-bottom:30px}
.f3{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
@media(max-width:820px){.f3{grid-template-columns:1fr;gap:24px}}
.f3 .n{font:600 44px/1 var(--mono);letter-spacing:-.035em;color:var(--acc)}
.f3 .n small{font:500 13px/1 var(--sans);color:var(--ink3);margin-left:4px;letter-spacing:0}
.f3 h3{font-size:14px;margin:11px 0 6px}
.f3 p{font-size:13.5px;line-height:1.65;color:var(--ink2);margin:0}
.steps{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line2);
  border:1px solid var(--line2);border-radius:3px;overflow:hidden}
@media(max-width:760px){.steps{grid-template-columns:1fr}}
.steps>div{background:rgba(255,255,255,.028);padding:20px 22px}
.steps .no{font:600 11px/1 var(--mono);color:var(--acc);margin-bottom:9px}
.steps h3{font-size:15px;margin-bottom:7px}
.steps p{font-size:13.5px;line-height:1.65;color:var(--ink2);margin:0}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}
@media(max-width:820px){.cards{grid-template-columns:1fr}}
.cards a{background:rgba(255,255,255,.035);border:1px solid var(--line2);border-radius:3px;
  padding:18px 19px;text-decoration:none;display:block;transition:border-color .18s,background .18s}
.cards a:hover{border-color:var(--acc);background:rgba(255,255,255,.06)}
.cards h3{font-size:14.5px;margin-bottom:6px}
.cards p{font-size:13px;line-height:1.6;color:var(--ink2);margin:0}
.cards .go{font:600 12px var(--mono);color:var(--acc);margin-top:11px;display:block}
.note{border-left:3px solid var(--acc2);padding:4px 0 4px 20px;max-width:70ch}
.note p{font-size:14px;line-height:1.75;color:var(--ink2);margin:0 0 12px}
.note a{font:500 13px var(--sans);color:var(--acc);text-decoration:none}
.note a:hover{text-decoration:underline}
.files{display:flex;flex-wrap:wrap;gap:8px}
.files a{font:400 12.5px var(--mono);padding:8px 12px;border:1px solid var(--line2);
  border-radius:3px;text-decoration:none;color:var(--ink2);background:rgba(255,255,255,.035)}
.files a:hover{border-color:var(--ink3);color:var(--ink)}
footer{padding:30px 22px 70px;max-width:1000px;margin:0 auto;font-size:12.5px;color:var(--ink3)}

/* ============ vong tron tai + goi y cuon ============ */
.ring{position:fixed;left:50%;bottom:46px;transform:translateX(-50%);z-index:40;
  display:flex;align-items:center;gap:10px;color:var(--ink3);
  font:600 10.5px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;
  transition:opacity .45s}
.ring svg{width:17px;height:17px;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:2}
.ring .bgc{stroke:rgba(255,255,255,.15)}
.ring .fg{stroke:var(--acc);stroke-dasharray:44;stroke-dashoffset:44;
  transition:stroke-dashoffset .2s linear}
.hint{position:fixed;left:50%;bottom:44px;transform:translateX(-50%);z-index:40;
  color:var(--ink3);font:600 10.5px/1 var(--mono);letter-spacing:.16em;
  text-transform:uppercase;opacity:0;transition:opacity .5s;pointer-events:none}
.hint::after{content:"";display:block;width:1px;height:22px;margin:10px auto 0;
  background:linear-gradient(180deg,rgba(255,255,255,.4),transparent)}

@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .beat{min-height:auto;padding:56px 24px}
  .beat>div,section.panel{opacity:1;transform:none;transition:none}
  .bg video{display:none}
  .hint,.ring{display:none}
}
</style>
</head>
<body>

<div class="bg">
  <img src="assets/hero-poster.jpg" alt="" fetchpriority="high" decoding="sync">
  <video id="hv" muted playsinline preload="auto" disablepictureinpicture></video>
  <div class="veil"></div>
</div>

<div class="nav" id="nav"><div class="in">
  <span class="mk"><i></i><i></i></span>
  <b>HCMC Rental Yield</b>
  <div class="sp">
    <a class="navcta" href="dashboard.html" id="navcta">
      <span class="dot"></span><span data-h="nav_dash"></span><i>&#8594;</i></a>
    <div class="lang">
      <button data-l="en" aria-pressed="true">EN</button>
      <button data-l="vi" aria-pressed="false">VI</button>
    </div>
  </div>
</div></div>

<main>
  <section class="beat"><div>
    <div class="kick" data-h="kick"></div>
    <h1><span data-h="h1a"></span> <em data-h="h1b"></em></h1>
    <p class="lede" data-h="lede"></p>
    <div class="cta">
      <a class="btn p big" href="dashboard.html">
        <span data-h="cta"></span><i>&#8594;</i></a>
    </div>
  </div></section>

  <section class="beat"><div>
    <div class="big" data-h="sc1"></div>
    <h1 style="font-size:clamp(24px,3.6vw,40px);margin-top:14px" data-h="sc1b"></h1>
  </div></section>

  <section class="beat"><div>
    <h1 style="font-size:clamp(26px,4.6vw,48px)" data-h="sc2"></h1>
    <p class="sm" data-h="sc2b"></p>
  </div></section>

  <section class="beat" id="cmpbeat"><div>
    <h1 style="font-size:clamp(22px,3.4vw,36px);margin-bottom:28px" data-h="sc3"></h1>
    <div class="cmp">
      <span class="cn a" id="n_rent"></span>
      <span class="cb"><i id="b_rent" style="background:var(--acc)"></i></span>
      <span class="cc" data-h="bar_rent"></span>
      <span class="cn b" id="n_dep"></span>
      <span class="cb"><i id="b_dep" style="background:var(--ref)"></i></span>
      <span class="cc" data-h="bar_dep"></span>
    </div>
    <p class="sm" id="gap" style="margin-top:24px"></p>
    <div class="cta">
      <a class="btn p big" href="dashboard.html">
        <span data-h="cta"></span><i>&#8594;</i></a>
      <a class="btn s" href="#how" data-h="cta2"></a>
    </div>
    <p class="ctasub" data-h="cta_sub"></p>
  </div></section>

  <div class="wrap">
    <section class="panel">
      <div class="st">01</div><h2 data-h="f_title"></h2>
      <div class="f3" style="margin-top:28px">
        <div><div class="n"><span data-h="f1n"></span><small data-h="f1u"></small></div>
          <h3 data-h="f1"></h3><p data-h="f1t"></p></div>
        <div><div class="n"><span data-h="f2n"></span><small data-h="f2u"></small></div>
          <h3 data-h="f2"></h3><p data-h="f2t"></p></div>
        <div><div class="n"><span data-h="f3n"></span><small data-h="f3u"></small></div>
          <h3 data-h="f3"></h3><p data-h="f3t"></p></div>
      </div>
    </section>

    <section class="panel" id="how">
      <div class="st">02</div><h2 data-h="h_title"></h2>
      <p class="sub" data-h="h_sub"></p>
      <div class="steps">
        <div><div class="no">01</div><h3 data-h="h1"></h3><p data-h="h1t"></p></div>
        <div><div class="no">02</div><h3 data-h="h2"></h3><p data-h="h2t"></p></div>
        <div><div class="no">03</div><h3 data-h="h3"></h3><p data-h="h3t"></p></div>
        <div><div class="no">04</div><h3 data-h="h4"></h3><p data-h="h4t"></p></div>
      </div>
    </section>

    <section class="panel">
      <div class="st">03</div><h2 data-h="w_title"></h2>
      <div class="cards" style="margin-top:26px">
        <a href="dashboard.html"><h3 data-h="w1"></h3><p data-h="w1t"></p><span class="go">→</span></a>
        <a href="dashboard.html"><h3 data-h="w2"></h3><p data-h="w2t"></p><span class="go">→</span></a>
        <a href="dashboard.html"><h3 data-h="w3"></h3><p data-h="w3t"></p><span class="go">→</span></a>
      </div>
    </section>

    <section class="panel">
      <div class="st">04</div><h2 data-h="l_title"></h2>
      <div class="note" style="margin-top:22px">
        <p data-h="l_t"></p><a href="dashboard.html" data-h="l_link"></a>
      </div>
    </section>

    <section class="panel" id="data">
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
  </div>

  <footer data-hh="foot"></footer>
</main>

<div class="ring" id="ring">
  <svg viewBox="0 0 16 16"><circle class="bgc" cx="8" cy="8" r="7"></circle>
    <circle class="fg" id="rfg" cx="8" cy="8" r="7"></circle></svg>
  <span data-h="loading"></span>
</div>
<div class="hint" id="hint" data-h="scroll"></div>

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
  $('navcta').setAttribute('aria-label',H[l].nav_dash);
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

/* ================= hien dan khi cuon toi =================
   Lam trong chinh ham cuon chu KHONG dung IntersectionObserver: neu IO khong
   chay (tab an, trinh duyet cu) thi noi dung se ket o opacity 0 vinh vien.
   Chin phan tu, moi lan cuon quet mot luot — chi phi khong dang ke. */
const REVEAL=[...document.querySelectorAll('.beat,section.panel')];
function reveal(){
  for(const e of REVEAL){
    if(e.classList.contains('seen')) continue;
    const r=e.getBoundingClientRect();
    if(r.top < innerHeight*0.86 && r.bottom > 0){
      e.classList.add('seen');
      if(e.id==='cmpbeat') setBars();
    }
  }
}

function setBars(){
  const mx=Math.max(D.rent,D.dep);
  $('b_rent').style.width=(D.rent/mx*100)+'%';
  $('b_dep').style.width=(D.dep/mx*100)+'%';
}

/* ================= VIDEO NEN, TUA THEO CUON CA TRANG ================= */
(function(){
  const SRC='assets/hero-scrub.mp4';
  const v=$('hv'), ring=$('ring'), hint=$('hint'), nav=$('nav'), bg=document.querySelector('.bg');
  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;

  function giveUp(){
    ring.style.display='none'; hint.style.display='none';
    REVEAL.forEach(e=>e.classList.add('seen'));
    setBars();
  }

  /* Truoc day tai TRON 5 MB thanh Blob roi moi cho tua. Trong ~1,5-2 giay do
     `v.duration` chua co nen vong tua khong chay: nguoi dung cuon ma hinh khong
     doi khung. Do chinh la 2 giay "lag" khi vua vao.

     Gio phat truc tiep. Nho `-movflags +faststart`, phan metadata nam o dau file
     nen `loadedmetadata` ve sau vai tram ms — tua duoc gan nhu ngay lap tuc, va
     chi tai MOT lan thay vi hai. */
  function load(){
    v.preload='auto';
    v.src=SRC;
    v.addEventListener('loadedmetadata',()=>{
      v.classList.add('ready');
      setTimeout(()=>document.querySelector('.bg').classList.add('live'),900);
      if(scrollY<60) hint.style.opacity=1;
      start();
    },{once:true});
    v.addEventListener('error',giveUp,{once:true});
    setTimeout(()=>{ if(!v.duration) giveUp(); },20000);
    /* Vong tron bao phan da tai duoc, doc tu chinh bo dem cua video */
    const iv=setInterval(()=>{
      if(!v.duration) return;
      const b=v.buffered.length?v.buffered.end(v.buffered.length-1):0;
      const f=Math.min(1,b/v.duration);
      $('rfg').style.strokeDashoffset=44*(1-f);
      if(f>0.995){ clearInterval(iv); ring.style.opacity=0;
        setTimeout(()=>ring.style.display='none',450); }
    },180);
  }

  let shown=0,target=0,running=false,seeking=false,seekAt=0,navOn=false;
  v.addEventListener('seeked',()=>{seeking=false;});
  /* Moi lenh tua bat decoder giai ma lai tu keyframe gan nhat (o day la toi 8
     khung). Goi tua moi nhip rAF = doi decoder lam 60 lan/giay o do phan giai
     1600x900 — no khong theo kip va sinh ra giat. Chan o ~30 lan/giay: mat
     thuong khong phan biet duoc, ma decoder tho duoc. */
  /* Video 24 khung/giay. Tua toi mot thoi diem nam GIUA hai khung se hien ra
     dung khung do — tuc la mot lenh giai ma day du cho ket qua y het khung dang
     hien. Truoc day nguong la 0.004 giay = MOT PHAN MUOI khung: phan lon lenh tua
     la vo ich, chi ton decoder chu khong doi gi tren man hinh.
     Gio lam tron ve bien khung: khong bao gio tua neu khung hien ra khong doi. */
  const FPS=24, FRAME=1/FPS, SEEK_MIN_MS=38;
  let lastSeek=0, shownFrame=-1;
  function seek(force){
    const now=performance.now();
    if(seeking) return;
    const f=Math.round(shown/FRAME);
    if(!force && f===shownFrame) return;              /* khung khong doi -> bo qua */
    if(!force && now-lastSeek<SEEK_MIN_MS) return;    /* san toc do khi cuon rat nhanh */
    const t=f*FRAME;
    /* Gan currentTime bang dung gia tri hien tai thi KHONG co su kien 'seeked',
       ma co 'seeking' lai da bat -> ket vinh vien, moi lenh tua sau deu bi chan. */
    if(Math.abs(v.currentTime-t)<1e-4){ shownFrame=f; return; }
    lastSeek=now; shownFrame=f; seeking=true; seekAt=now;
    try{ v.currentTime=t; }catch(e){ seeking=false; }
  }
  /* He so noi suy quyet dinh do "bam" cua video vao vi tri cuon.
     0.16 can ~220ms de duoi kip 90% khoang cach — doc ra thanh cam giac tre.
     0.26 con ~130ms, van muot ma theo sat tay hon nhieu.
     Va khi nguoi dung keo thanh cuon nhay mot phat (khoang cach > 2,5s) thi
     dung noi suy nua, nhay thang toi noi, neu khong se thay video "boi" theo. */
  function tick(){
    if(seeking && performance.now()-seekAt>400) seeking=false;   /* chong ket vinh vien */
    const d=target-shown;
    if(Math.abs(d)<FRAME*0.5){ shown=target; running=false; seek(true); return; }
    shown += Math.abs(d)>2.5 ? d*0.75 : d*0.26;
    seek();
    requestAnimationFrame(tick);
  }

  let lastP=-1;
  /* scrollHeight ep trinh duyet TINH LAI BO CUC ngay tai cho. Goi no trong ham
     cuon la ep tinh bo cuc dong bo hang chuc lan moi giay — day la thu nang nhat
     trong ca vong cuon. Do mot lan, chi do lai khi kich thuoc that su doi. */
  let maxScroll=1;
  function measure(){ maxScroll=Math.max(1,document.documentElement.scrollHeight-innerHeight); }

  let lastScale=-1;
  function onScroll(){
    const p=clamp(scrollY/maxScroll,0,1);
    if(v.duration){
      target=p*v.duration*0.999;
      /* KHONG duoc kep target vao phan da tai. Video dang TAM DUNG thi trinh
         duyet chi tai truoc mot doan ngan (do duoc: 2,5 giay = 9%) roi ngung han
         — kep vao do la ghim nen dung yen o 9% hanh trinh du nguoi dung cuon het
         trang. Cu de no tua toi dau can: trinh duyet se tu xin doan con thieu,
         cho mot nhip ngan van hon la khong bao gio nhuc nhich. */
      if(!running){ running=true; requestAnimationFrame(tick); }
    }
    reveal();
    /* Lam tron ty le phong to thanh 40 nac. Truoc day de 4 chu so thap phan nen
       gan nhu moi lan cuon deu ra mot gia tri moi, ep gop lai ca lop video 1600px.
       40 nac cho ca trang van muot mat ma so lan gop giam han. */
    const sc=Math.round(p*40);
    if(sc!==lastScale){
      lastScale=sc;
      bg.style.transform='scale('+(1+sc/40*0.035).toFixed(3)+')';
    }
    const on=scrollY>50;
    if(on!==navOn){ navOn=on; nav.classList.toggle('on',on); }
    if(scrollY>60 && hint.style.opacity!=='0') hint.style.opacity=0;
  }
  function start(){
    measure();
    addEventListener('scroll',onScroll,{passive:true});
    addEventListener('resize',()=>{measure();onScroll();});
    /* bo cuc con doi khi anh/font ve xong, do lai vai lan dau */
    [300,1200,3000].forEach(t=>setTimeout(()=>{measure();onScroll();},t));
    onScroll();
  }
  window._hero={onScroll,giveUp,state:()=>({shown,target,running,seeking})};

  if(reduce) giveUp(); else load();
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
vid = WEB / "assets" / "hero-scrub.mp4"
print(f"docs/index.html  ({(WEB / 'index.html').stat().st_size / 1024:.0f} KB)")
print(f"  video nen: {vid.stat().st_size / 1e6:.2f} MB" if vid.exists() else "  ! chua co video")
