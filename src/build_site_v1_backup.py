"""Buoc 4 — Dung website tinh, mot file HTML tu chua tat ca.

Vi sao mot file: khong build step, khong phu thuoc thu vien ngoai, mo bang
file:// cung chay, deploy len GitHub Pages/Vercel chi can keo tha. Du an hoc
sinh phai con chay duoc sau 2 nam nua, nen it phu thuoc bao nhieu tot bay nhieu.

Chay: python src/build_site.py   ->  web/index.html
"""

from __future__ import annotations

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
WEB = ROOT / "web"

fin = json.loads((OUT / "financial_summary.json").read_text(encoding="utf-8"))
cells = json.loads((OUT / "yield_by_district_size.json").read_text(encoding="utf-8"))
wards = json.loads((OUT / "yield_by_ward.json").read_text(encoding="utf-8"))
clean = json.loads((OUT / "clean_report.json").read_text(encoding="utf-8"))
mapgeo = json.loads((OUT / "hcm_geo.json").read_text(encoding="utf-8"))
mapbounds = json.loads((OUT / "hcm_bounds.json").read_text(encoding="utf-8"))

GD = fin["gia_dinh"]
LTS = fin["lai_tiet_kiem_pct"]

# ------------------------------------------------------- xep hang quan
byd = defaultdict(lambda: {"rong": [], "gop": [], "n": 0})
for c in cells:
    byd[c["district_name"]]["rong"].append(c["ti_suat_rong"])
    byd[c["district_name"]]["gop"].append(c["ti_suat_gop"])
    byd[c["district_name"]]["n"] += c["n_ban"] + c["n_thue"]
districts = sorted(
    ({"ten": k, "rong": st.median(v["rong"]), "gop": st.median(v["gop"]), "n": v["n"]}
     for k, v in byd.items()),
    key=lambda d: -d["rong"])

# vi du can ho 60-80 m² de dien san vao may tinh
apt = [c for c in cells if c["category_name"].startswith("Căn hộ") and c["size_bucket"] == "60-80"]
GIA_M2 = st.median([c["gia_ban_m2"] for c in apt])
THUE_M2 = st.median([c["gia_thue_m2"] for c in apt])

ward_rows = sorted(wards, key=lambda w: -w["ti_suat_rong"])

DATA = {
    "gd": GD, "lts": LTS,
    "districts": districts,
    "wards": [{"p": w["ward_name"], "q": w["district_name"], "c": w["category_name"],
               "gop": round(w["ti_suat_gop"], 2), "rong": round(w["ti_suat_rong"], 2),
               "ban": round(w["gia_ban_m2"] / 1e6, 1), "thue": round(w["gia_thue_m2"] / 1e3),
               "nb": w["n_ban"], "nt": w["n_thue"]} for w in ward_rows],
    # lam tron cho de doc — day la vi du dien san, khong phai ket qua tinh toan
    "vd": {"gia": round(GIA_M2 * 70 / 1e8) * int(1e8),
           "thue": round(THUE_M2 * 70 / 1e5) * int(1e5), "m2": 70},
    "geo": mapgeo, "bounds": mapbounds,
}

# HTML la raw string vi ben trong co regex JS nhu \D va \s+ — neu khong,
# Python hieu nham la escape sequence va se hong o cac ban Python moi.
HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tỉ suất cho thuê bất động sản TP.HCM</title>
<meta name="description" content="Phân tích 45.084 tin rao bán và cho thuê tại TP.HCM: mua nhà cho thuê sinh lời 1,51%/năm, thua xa gửi tiết kiệm.">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>
<style>
:root{
  --bg:#fbfaf8; --fg:#1a1a1a; --muted:#6b6b6b; --line:#e2ded8;
  --card:#fff; --accent:#b3261e; --good:#1f6f43; --bar:#c9c2b6; --shadow:0 1px 2px rgba(0,0,0,.05);
}
@media (prefers-color-scheme:dark){
  :root{--bg:#14140f;--fg:#ece8e1;--muted:#9a948a;--line:#2e2d27;--card:#1c1c17;
        --accent:#ef6b5f;--good:#5fc48b;--bar:#3d3b33;--shadow:none}
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
h1{font-size:clamp(28px,5vw,44px);line-height:1.15;letter-spacing:-.02em;margin:0 0 16px}
h2{font-size:clamp(20px,3vw,27px);letter-spacing:-.01em;margin:56px 0 6px}
h3{font-size:17px;margin:28px 0 8px}
p{margin:0 0 14px} .muted{color:var(--muted)}
.sub{font-size:18px;color:var(--muted);max-width:60ch}
hr{border:0;border-top:1px solid var(--line);margin:48px 0}
header{padding:64px 0 8px;border-bottom:1px solid var(--line)}
.meta{font-size:13px;color:var(--muted);margin-top:28px;padding-bottom:28px}

/* --- so lieu lon --- */
.hero{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:36px 0 8px;
  border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--card)}
.hero>div{padding:26px 24px}
.hero>div+div{border-left:1px solid var(--line)}
.big{font-size:clamp(38px,7vw,58px);font-weight:600;line-height:1;letter-spacing:-.03em;
  font-variant-numeric:tabular-nums}
.lab{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:10px}
.red{color:var(--accent)} .green{color:var(--good)}
.note{font-size:14px;color:var(--muted);margin-top:8px}
@media(max-width:640px){.hero{grid-template-columns:1fr}.hero>div+div{border-left:0;border-top:1px solid var(--line)}}

/* --- may tinh --- */
.calc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:24px;
  box-shadow:var(--shadow)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
label{display:block;font-size:13px;color:var(--muted);margin:14px 0 5px}
input[type=text],input[type=number]{width:100%;padding:9px 11px;font-size:15px;font-family:inherit;
  border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);
  font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--accent);margin:2px 0}
.rv{float:right;color:var(--fg);font-variant-numeric:tabular-nums}
.out{margin-top:22px;padding-top:20px;border-top:1px solid var(--line)}
.orow{display:flex;justify-content:space-between;align-items:baseline;padding:8px 0;
  border-bottom:1px dotted var(--line);font-variant-numeric:tabular-nums}
.orow:last-child{border-bottom:0}
.orow b{font-size:19px;font-weight:600}
.verdict{margin-top:18px;padding:16px 18px;border-radius:8px;font-size:15px;
  background:color-mix(in srgb,var(--accent) 9%,transparent);
  border:1px solid color-mix(in srgb,var(--accent) 26%,transparent)}

/* --- bang / bieu do --- */
table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);
  font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:var(--fg)}
td.n,th.n{text-align:right}
.barrow{display:grid;grid-template-columns:150px 1fr 62px;gap:12px;align-items:center;
  padding:5px 0;font-size:14px}
.bar{height:17px;background:var(--bar);border-radius:3px;position:relative}
.bar i{position:absolute;inset:0 auto 0 0;background:var(--accent);border-radius:3px;display:block}
.barv{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}
.ref{position:relative;height:1px;background:var(--line);margin:10px 0 4px}
@media(max-width:640px){.barrow{grid-template-columns:110px 1fr 52px;font-size:13px}}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}

/* --- ban do Leaflet --- */
.mapbox{position:relative;margin-top:18px;border:1px solid var(--line);border-radius:10px;
  overflow:hidden}
#map{width:100%;height:min(74vh,620px);background:#0d1117}
.leaflet-container{font:inherit;background:#0d1117}
.leaflet-control-attribution{font-size:10px!important;background:rgba(0,0,0,.55)!important;
  color:#ccc!important}
.leaflet-control-attribution a{color:#9ec5ff!important}
.mapbtns{position:absolute;left:10px;top:10px;z-index:500;display:flex;gap:6px}
.mapbtns button{font:inherit;font-size:12.5px;padding:6px 11px;border-radius:6px;cursor:pointer;
  border:1px solid rgba(255,255,255,.22);background:rgba(18,18,18,.82);color:#f2f2f2;
  backdrop-filter:blur(6px)}
.mapbtns button:hover{background:rgba(40,40,40,.92)}
.maplegend{position:absolute;left:10px;bottom:22px;z-index:500;background:rgba(18,18,18,.82);
  backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.16);border-radius:8px;
  padding:9px 11px;color:#eee;font-size:12px;line-height:1.5;max-width:230px}
.maplegend .lgbar{display:block;height:9px;border-radius:3px;margin:5px 0 3px;
  background:linear-gradient(90deg,#7d1d16,#e0a03a)}
.maplegend .row{display:flex;justify-content:space-between;font-variant-numeric:tabular-nums}
.maplegend .nd{margin-top:7px;padding-top:6px;border-top:1px solid rgba(255,255,255,.15);
  opacity:.8}
.maplegend .nd i{display:inline-block;width:10px;height:10px;border-radius:2px;
  background:#8a8a8a;vertical-align:-1px;margin-right:4px}
.dtip{background:#141414;color:#f0f0f0;border:1px solid rgba(255,255,255,.2);border-radius:7px;
  padding:7px 10px;font-size:13px;line-height:1.5;box-shadow:0 3px 14px rgba(0,0,0,.5)}
.dtip b{font-size:14.5px}
.dtip .mut{opacity:.65}
/* cham nhap nhay danh dau TP.HCM khi dang xem toan Viet Nam */
.ping,.ping::after{border-radius:50%}
.ping{width:15px;height:15px;background:#e0a03a;box-shadow:0 0 0 2px rgba(255,255,255,.85);
  position:relative}
.ping::after{content:"";position:absolute;inset:-5px;border:2px solid #e0a03a;
  animation:pulse 1.7s ease-out infinite}
@keyframes pulse{0%{transform:scale(.55);opacity:1}100%{transform:scale(2.6);opacity:0}}
.pinglbl{position:absolute;left:20px;top:-4px;white-space:nowrap;color:#fff;font-size:13px;
  font-weight:600;text-shadow:0 1px 4px #000}
.tblbox{max-height:460px;overflow-y:auto;border:1px solid var(--line);border-radius:8px}
.tblbox thead th{position:sticky;top:0;background:var(--card);z-index:1}
details{border-top:1px solid var(--line);padding:14px 0}
summary{cursor:pointer;font-weight:600}
code{background:var(--card);border:1px solid var(--line);padding:1px 5px;border-radius:4px;font-size:13px}
footer{margin:64px 0 80px;padding-top:24px;border-top:1px solid var(--line);
  font-size:14px;color:var(--muted)}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Mua nhà cho thuê ở TP.HCM<br>lời ít hơn gửi tiết kiệm</h1>
  <p class="sub">Phân tích __NLIST__ tin rao bán và cho thuê, ghép theo từng phường
  và từng loại hình. Kết quả: không một quận nào trong 20 quận có tỉ suất cho thuê
  đuổi kịp lãi suất ngân hàng.</p>

  <div class="hero">
    <div>
      <div class="lab">Cho thuê, sau chi phí</div>
      <div class="big red">__RONG__<span style="font-size:.45em">%/năm</span></div>
      <div class="note">Tỉ suất gộp __GOP__%, chi phí ẩn nuốt mất 44%</div>
    </div>
    <div>
      <div class="lab">Gửi tiết kiệm 12 tháng</div>
      <div class="big green">__LTS__<span style="font-size:.45em">%/năm</span></div>
      <div class="note">Big4 tại quầy, tháng 8/2026</div>
    </div>
  </div>
  <p class="note" style="margin-top:14px">
    Với tỉ suất __RONG__%, tiền thuê cần <b>__NAM__ năm</b> mới trả hết giá mua căn nhà.</p>

  <div class="meta">
    Nguồn: Chợ Tốt (nhatot.com) · thu thập __NGAY__ · __NRAW__ tin thô →
    __NLIST__ tin sau lọc · 22 quận/huyện TP.HCM
  </div>
</header>

<h2>Nhà của bạn thì sao?</h2>
<p class="sub">Nhập số của chính bạn. Mọi giả định đều chỉnh được — vì chúng là giả định,
không phải sự thật.</p>

<div class="calc">
  <div class="grid2">
    <div>
      <label>Giá mua (đồng)<input type="text" inputmode="numeric" id="gia"></label>
      <label>Tiền thuê thu được mỗi tháng (đồng)<input type="text" inputmode="numeric" id="thue"></label>
      <label>Vay bao nhiêu phần trăm giá trị <span class="rv" id="vv"></span>
        <input type="range" id="vay" min="0" max="90" step="5"></label>
      <label>Lãi suất vay <span class="rv" id="lvv"></span>
        <input type="range" id="lv" min="6" max="18" step="0.5"></label>
    </div>
    <div>
      <label>Lãi suất tiết kiệm để so sánh <span class="rv" id="ltv"></span>
        <input type="range" id="lt" min="3" max="10" step="0.1"></label>
      <label>Số tháng bỏ trống mỗi năm <span class="rv" id="btv"></span>
        <input type="range" id="bt" min="0" max="4" step="0.5"></label>
      <label>Thuế cho thuê <span class="rv" id="thv"></span>
        <input type="range" id="th" min="0" max="20" step="1"></label>
      <label>Phí quản lý + bảo trì mỗi năm <span class="rv" id="bhv"></span>
        <input type="range" id="bh" min="0" max="3" step="0.1"></label>
    </div>
  </div>

  <p class="note" style="margin-top:16px;margin-bottom:0">
    Điền sẵn: căn hộ 70 m² ở mức trung vị thị trường — giá __VDGIA__ và tiền thuê
    __VDTHUE__ mỗi tháng, tính từ chính bộ dữ liệu này. Sửa thành số của bạn.</p>

  <div class="out">
    <div class="orow"><span>Tỉ suất gộp</span><b id="o_gop"></b></div>
    <div class="orow"><span>Tỉ suất ròng, sau mọi chi phí</span><b id="o_rong"></b></div>
    <div class="orow"><span>Dòng tiền mỗi tháng khi có vay</span><b id="o_dt"></b></div>
    <div class="orow"><span>Nếu gửi số tiền đó vào ngân hàng</span><b id="o_nh"></b></div>
    <div class="orow"><span>Số năm tiền thuê trả hết giá mua</span><b id="o_nam"></b></div>
    <div class="orow"><span>Giá nhà phải tăng mỗi năm để hòa vốn</span><b id="o_tang"></b></div>
  </div>
  <div class="verdict" id="verdict"></div>
</div>

<h2>Bản đồ</h2>
<p class="sub">Tỉ suất ròng mỗi năm theo quận, phủ lên ảnh vệ tinh thật.
Kéo để di chuyển, lăn chuột để phóng to, bấm vào một quận để nhảy tới quận đó.</p>

<div class="mapbox">
  <div id="map"></div>
  <div class="mapbtns">
    <button id="b_vn">Toàn Việt Nam</button>
    <button id="b_hcm">Về TP.HCM</button>
  </div>
  <div class="maplegend">
    <div>Tỉ suất ròng %/năm</div>
    <span class="lgbar"></span>
    <div class="row"><span id="lg_lo"></span><span id="lg_hi"></span></div>
    <div class="nd"><i></i> Không đủ dữ liệu</div>
  </div>
</div>
<p class="note" id="mapnote"></p>

<h2>Xếp hạng 20 quận</h2>
<p class="sub">Tỉ suất ròng mỗi năm. Cột xanh dưới cùng là lãi suất tiết kiệm __LTS__%
để đối chiếu — không quận nào chạm tới nó.</p>
<div id="bars"></div>

<h2>Tra theo phường</h2>
<p class="sub">__NW__ ô đủ điều kiện — mỗi ô là một phường và một loại hình có ít nhất
10 tin rao bán và 10 tin cho thuê. Bấm vào tiêu đề cột để sắp xếp.</p>
<div class="tblbox scroll">
<table id="wt">
  <thead><tr>
    <th data-k="p">Phường</th><th data-k="q">Quận</th><th data-k="c">Loại hình</th>
    <th data-k="ban" class="n">Bán<br><span class="muted">tr/m²</span></th>
    <th data-k="thue" class="n">Thuê<br><span class="muted">ngh/m²/th</span></th>
    <th data-k="gop" class="n">Gộp<br><span class="muted">%/năm</span></th>
    <th data-k="rong" class="n">Ròng<br><span class="muted">%/năm</span></th>
    <th data-k="nb" class="n">Số tin</th>
  </tr></thead>
  <tbody></tbody>
</table>
</div>

<h2>Phương pháp</h2>

<h3>Ghép bán với thuê theo ô, không lấy trung bình cả quận</h3>
<p>Lấy giá bán trung bình của một quận chia cho tiền thuê trung bình của quận đó là sai:
tin rao bán nghiêng về nhà phố lớn, tin cho thuê nghiêng về căn hộ nhỏ, nên phép chia đó
đem giá biệt thự so với tiền thuê phòng trọ. Ở đây mọi so sánh chỉ thực hiện
<b>trong cùng một ô</b> — cùng phường, cùng loại hình, cùng tầm diện tích — và dùng
<b>trung vị giá trên mỗi m²</b> của từng bên. Ô nào có dưới 10 tin ở một trong hai phía
thì bị loại, không đoán.</p>

<h3>Tự kiểm tra chéo</h3>
<p>Tỉ suất được tính độc lập theo hai cách: theo <i>phường × loại hình</i> ra 2,57%/năm,
theo <i>quận × loại hình × nhóm diện tích</i> ra 2,61%/năm. Hai con số gần như trùng nhau,
nghĩa là kết quả không đến từ chênh lệch cơ cấu diện tích giữa tin bán và tin thuê.</p>

<h3>Làm sạch dữ liệu</h3>
<p>Từ __NRAW__ tin thô còn __NLIST__ tin (__PCT__%). Số bị loại ở từng bước:</p>
<div class="scroll"><table><thead><tr><th>Luật lọc</th><th class="n">Số tin loại</th></tr></thead>
<tbody>__REJECTS__</tbody></table></div>

<h3>Giả định mặc định</h3>
<div class="scroll"><table><tbody>
<tr><td>Lãi suất tiết kiệm 12 tháng</td><td class="n">6,0%/năm — Big4 tại quầy</td></tr>
<tr><td>Lãi suất vay thả nổi</td><td class="n">12,0%/năm — giữa khoảng 11–15% sau ưu đãi</td></tr>
<tr><td>Tỉ lệ vay</td><td class="n">70% giá trị nhà</td></tr>
<tr><td>Bỏ trống</td><td class="n">1 tháng mỗi năm</td></tr>
<tr><td>Thuế cho thuê</td><td class="n">10% doanh thu</td></tr>
<tr><td>Phí quản lý chung cư</td><td class="n">15.000 đ/m²/tháng</td></tr>
<tr><td>Bảo trì</td><td class="n">0,5% giá trị tài sản mỗi năm</td></tr>
</tbody></table></div>

<h2>Giới hạn</h2>

<details open><summary>Đây là giá rao, không phải giá giao dịch</summary>
<p>Người bán thường hét cao hơn giá chốt 5–15%, còn giá thuê ít mặc cả hơn. Nghĩa là
tỉ suất thật <b>cao hơn</b> con số ở đây. Nhưng để kết luận đảo chiều — tức tỉ suất gộp
chạm mức tiết kiệm 6% — thì giá rao phải cao hơn giá bán thật tới <b>53%</b>. Không thị
trường nào mặc cả ở mức đó, nên kết luận vẫn đứng.</p></details>

<details><summary>Chỉ một nguồn, chỉ phân khúc có rao trên mạng</summary>
<p>Toàn bộ dữ liệu đến từ Chợ Tốt. Nhà bán qua môi giới riêng, qua quen biết, hoặc phân khúc
cao cấp bán qua kênh khác đều không nằm trong đây. Con số căn hộ 3,4%/năm của bộ dữ liệu này
thấp hơn mức 4–5% mà CBRE và Savills thường công bố; phần chênh đó chưa được giải thích
đầy đủ và cần đối chiếu thêm.</p></details>

<details><summary>Một lát cắt, không phải chuỗi thời gian</summary>
<p>Dữ liệu chụp tại một thời điểm (__NGAY__), nên không nói được gì về xu hướng. Câu hỏi
"giá nhà có thật sự tăng 7%/năm không" — điều kiện để người mua hòa vốn — <b>không</b> trả lời
được bằng bộ dữ liệu này.</p></details>

<details><summary>Tỉ suất ròng phụ thuộc giả định</summary>
<p>Tỉ suất gộp chỉ là phép chia hai con số quan sát được, gần như không thể bác. Nhưng tỉ suất
ròng phụ thuộc vào giả định về thuế, phí, bỏ trống và bảo trì — riêng khoản bảo trì 0,5%/năm
đã chiếm phần đáng kể. Vì vậy mọi tham số ở máy tính phía trên đều chỉnh được.</p></details>

<details><summary>Tên phường đang loạn vì sáp nhập</summary>
<p>Nhiều phường có tên kèm đuôi như "(Quận 2 cũ)", và 17 tên phường ứng với nhiều hơn một mã.
Toàn bộ tính toán dùng <b>mã phường</b> làm khóa, tên chỉ để hiển thị.</p></details>

<h2>Dữ liệu</h2>
<p>Chỉ công bố số liệu đã tổng hợp theo phường, không đăng lại nội dung tin rao gốc.</p>
<p><code>yield_by_ward.json</code> · <code>yield_by_district_size.json</code> ·
<code>financial_summary.json</code> · <code>clean_report.json</code></p>

<footer>
  Dự án học sinh · dữ liệu thu thập __NGAY__ từ Chợ Tốt ·
  mã nguồn và phương pháp công khai.<br>
  Không phải lời khuyên đầu tư.
</footer>

</div>
<script>
const D = __DATA__;
const fmt = n => new Intl.NumberFormat('vi-VN').format(Math.round(n));
const pc  = n => n.toFixed(2).replace('.', ',').replace('-', '−') + '%';
const $   = id => document.getElementById(id);

/* ---------- may tinh ---------- */
const F = ['gia','thue','vay','lv','lt','bt','th','bh'];
/* O tien nhap dang chu de hien duoc dau cham ngan cach: doc thi boc lay chu so,
   con dinh dang lai thi lam luc roi con tro — de khong nhay con tro khi dang go. */
const num = id => +($(id).value.replace(/\D/g,'') || 0);
['gia','thue'].forEach(id => $(id).addEventListener('blur', () => {
  const v = num(id); if(v) $(id).value = fmt(v);
}));

function calc(){
  const gia=num('gia'), thue=num('thue');
  const vay=+$('vay').value/100, lv=+$('lv').value/100, lt=+$('lt').value/100;
  const bt=+$('bt').value, th=+$('th').value/100, bh=+$('bh').value/100;

  $('vv').textContent=(vay*100)+'%'; $('lvv').textContent=(lv*100).toFixed(1)+'%';
  $('ltv').textContent=(lt*100).toFixed(1)+'%'; $('btv').textContent=bt+' tháng';
  $('thv').textContent=(th*100)+'%'; $('bhv').textContent=(bh*100).toFixed(1)+'%';

  if(!gia||gia<=0){ return; }
  const gop  = thue*12/gia*100;
  const thuc = thue*12*(1-bt/12);
  const rongVND = thuc - thuc*th - gia*bh;
  const rong = rongVND/gia*100;

  const laiNam = gia*vay*lv;
  const dtThang = (rongVND - laiNam)/12;
  const nhThang = gia*lt/12;
  const nam = rong>0 ? 100/rong : Infinity;
  const tang = vay*lv*100 + (1-vay)*lt*100 - rong;

  $('o_gop').textContent  = pc(gop);
  $('o_rong').textContent = pc(rong);
  $('o_rong').className   = rong < lt*100 ? 'red' : 'green';
  $('o_dt').textContent   = (dtThang>=0?'+':'−') + fmt(Math.abs(dtThang)) + ' đ';
  $('o_dt').className     = dtThang>=0 ? 'green' : 'red';
  $('o_nh').textContent   = '+' + fmt(nhThang) + ' đ';
  $('o_nh').className     = 'green';
  $('o_nam').textContent  = isFinite(nam) ? Math.round(nam) + ' năm' : 'không bao giờ';
  $('o_tang').textContent = pc(tang);

  const chenh = nhThang - dtThang;
  $('verdict').innerHTML = rong < lt*100
    ? `Gửi ngân hàng hơn <b>${pc(lt*100 - rong)}</b> mỗi năm. Chênh lệch dòng tiền giữa
       hai lựa chọn là <b>${fmt(chenh)} đ mỗi tháng</b>. Để mua nhà có lợi hơn, giá nhà
       phải tăng đều <b>${pc(tang)} mỗi năm</b>, năm này qua năm khác.`
    : `Với các giả định này, cho thuê nhỉnh hơn gửi tiết kiệm <b>${pc(rong - lt*100)}</b> mỗi năm.`;
}
F.forEach(id => $(id).addEventListener('input', calc));
$('gia').value=fmt(D.vd.gia); $('thue').value=fmt(D.vd.thue);
$('vay').value=D.gd.ty_le_vay*100; $('lv').value=D.gd.lai_vay_tha_noi*100;
$('lt').value=D.lts; $('bt').value=D.gd.bo_trong_thang;
/* 0,8% = phi quan ly chung cu (15.000 d/m²/thang) + bao tri 0,5%/nam,
   gop lai thanh mot thanh truot cho de hieu — khop voi financial_layer.py */
$('th').value=D.gd.thue_cho_thue*100; $('bh').value=0.8;
calc();

/* ---------- ban do Leaflet ----------
   Leaflet nap bang defer nen chay SAU script noi tuyen nay -> phai doi DOM san sang. */
window.addEventListener('DOMContentLoaded',function(){
  if(typeof L==='undefined'){                       /* mat mang -> bao thang, dung im lang */
    $('map').innerHTML='<div style="padding:26px;color:#bbb;font-size:14px">'
      +'Bản đồ cần kết nối mạng để tải ảnh vệ tinh. Phần xếp hạng và bảng phía dưới '
      +'vẫn dùng được bình thường.</div>';
    return;
  }
  /* Ten hai ben lech hoa/thuong ("Thành phố Thủ Đức" vs "Thành Phố Thủ Đức") ->
     chuan hoa ca hai phia truoc khi ghep, dung so bang chuoi nguyen ban. */
  const kh=s=>s.toLocaleUpperCase('vi').replace(/\s+/g,' ').trim();
  const byName={}; D.districts.forEach(d=>byName[kh(d.ten)]=d);
  const vals=D.districts.map(d=>d.rong), lo=Math.min(...vals), hi=Math.max(...vals);
  const C0=[125,29,22], C1=[224,160,58];            /* do dam (thap) -> ho phach (cao) */
  const color=v=>`rgb(${C0.map((c,i)=>Math.round(c+(C1[i]-c)*((v-lo)/(hi-lo||1)))).join(',')})`;

  const HCM=L.latLngBounds(D.bounds), VN=L.latLngBounds([[8.2,102.1],[23.5,109.6]]);
  /* zoomSnap 0.25: mac dinh la 1, Leaflet lam tron XUONG nen hay zoom xa hon can thiet */
  const map=L.map('map',{zoomControl:false,scrollWheelZoom:true,zoomSnap:.25});
  map.fitBounds(VN);   /* PHAI dat khung nhin truoc khi them bat ky lop nao,
                          neu khong Leaflet nem "Set map center and zoom first" */
  L.control.zoom({position:'bottomright'}).addTo(map);
  window._map=map;   /* de kiem tra muc zoom tu console khi can */

  const bases={
    'Vệ tinh': L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {maxZoom:18,attribution:'Ảnh vệ tinh &copy; Esri, Maxar, Earthstar Geographics'}),
    'Bản đồ': L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
      {maxZoom:19,attribution:'&copy; OpenStreetMap contributors &copy; CARTO'}),
    'Nền tối': L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {maxZoom:19,attribution:'&copy; OpenStreetMap contributors &copy; CARTO'}),
  };
  bases['Vệ tinh'].addTo(map);
  L.control.layers(bases,null,{position:'topright'}).addTo(map);

  const thieu=[];
  const layer=L.geoJSON(D.geo,{
    style: f=>{
      const r=byName[kh(f.properties.ten)];
      return r ? {color:'#fff',weight:1,opacity:.85,fillColor:color(r.rong),fillOpacity:.72}
               : {color:'#fff',weight:1,opacity:.45,fillColor:'#8a8a8a',fillOpacity:.42};
    },
    onEachFeature:(f,l)=>{
      const ten=f.properties.ten, r=byName[kh(ten)];
      if(!r) thieu.push(ten);
      l.bindTooltip(r
        ? `<b>${ten}</b><br>Ròng ${pc(r.rong)} · Gộp ${pc(r.gop)}<br>
           <span class="mut">${fmt(r.n)} tin rao</span>`
        : `<b>${ten}</b><br><span class="mut">không đủ dữ liệu</span>`,
        {sticky:true,className:'dtip',opacity:1});
      l.on('mouseover',()=>l.setStyle({weight:2.5,opacity:1,fillOpacity:.85}));
      l.on('mouseout', ()=>layer.resetStyle(l));
      l.on('click',   ()=>map.flyToBounds(l.getBounds(),{padding:[24,24],duration:.7}));
    }
  }).addTo(map);

  /* cham nhap nhay danh dau Sai Gon khi dang o muc toan quoc */
  const ping=L.marker(HCM.getCenter(),{interactive:false,icon:L.divIcon({
    className:'', html:'<div class="ping"><span class="pinglbl">TP.HCM</span></div>',
    iconSize:[15,15], iconAnchor:[7,7]})});

  /* Khung mac dinh KHONG dung ranh gioi hanh chinh day du: Can Gio va Cu Chi rat rong,
     nam hai dau va deu khong co du lieu, nen khop theo chung se lam loi do thi — phan
     co mau, phan dang xem — teo lai o giua. Khop theo cac quan CO du lieu. */
  const LOI=L.latLngBounds([]);
  layer.eachLayer(l=>{ if(byName[kh(l.feature.properties.ten)]) LOI.extend(l.getBounds()); });

  const PAD={padding:[26,26]};
  let view='vn';                                   /* dang xem toan quoc hay loi do thi */
  const toVN =()=>{view='vn'; map.flyToBounds(VN,{duration:1.1}); ping.addTo(map);};
  const toHCM=()=>{view='hcm'; map.flyToBounds(LOI,{...PAD,duration:1.3}); map.removeLayer(ping);};
  $('b_vn').addEventListener('click',toVN);
  $('b_hcm').addEventListener('click',toHCM);

  /* Leaflet ghi nho kich thuoc khung luc khoi tao. Neu luc do trang chua bo tri xong
     thi no tuong khung be hon that va zoom ra qua xa. Phai bao lai moi khi khung doi
     kich thuoc, va dat lai khung nhin cho dung. */
  const el=$('map');
  let cuoi='';
  const fit=()=>{
    /* Chi lam gi khi khung THAT SU doi kich thuoc. Neu goi vo to va, invalidateSize()
       se bat trung luc ban do dang bay va lam dut hoat anh giua chung -> dung lai o
       mot muc zoom sai. */
    const kt=el.clientWidth+'x'+el.clientHeight;
    if(kt===cuoi) return;
    cuoi=kt;
    map.invalidateSize({animate:false});
    map.fitBounds(view==='vn'?VN:LOI, view==='vn'?{}:PAD);
  };
  new ResizeObserver(fit).observe(el);
  requestAnimationFrame(fit);

  /* mo dau: dat trong khung Viet Nam, ping len, roi bay ve Sai Gon */
  ping.addTo(map);
  setTimeout(toHCM,1500);

  $('lg_lo').textContent=pc(lo); $('lg_hi').textContent=pc(hi);
  $('mapnote').innerHTML=thieu.length
    ? `${thieu.join(' và ')} không có ô nào đủ 10 tin rao bán và 10 tin cho thuê, nên để xám —
       phần lớn giao dịch ở đó là đất nền, vốn không có thị trường cho thuê.`
    : '';
});

/* ---------- bieu do quan ---------- */
const mx = Math.max(D.lts, ...D.districts.map(d=>d.rong)) * 1.05;
$('bars').innerHTML = D.districts.map(d=>`
  <div class="barrow">
    <span>${d.ten.replace('Thành phố ','TP. ')}</span>
    <span class="bar"><i style="width:${d.rong/mx*100}%"></i></span>
    <span class="barv">${pc(d.rong)}</span>
  </div>`).join('')
  + `<div class="barrow" style="margin-top:8px;border-top:1px solid var(--line);padding-top:10px">
       <span class="muted">Gửi tiết kiệm</span>
       <span class="bar"><i style="width:${D.lts/mx*100}%;background:var(--good)"></i></span>
       <span class="barv">${pc(D.lts)}</span>
     </div>`;

/* ---------- bang phuong ---------- */
let dir = {};
function drawTable(k){
  let rows = D.wards.slice();
  if(k){ dir[k] = !dir[k];
    rows.sort((a,b)=> typeof a[k]==='string'
      ? (dir[k]?1:-1)*a[k].localeCompare(b[k],'vi')
      : (dir[k]?1:-1)*(a[k]-b[k])); }
  document.querySelector('#wt tbody').innerHTML = rows.map(w=>`<tr>
    <td>${w.p}</td><td>${w.q.replace('Thành phố ','TP. ')}</td>
    <td>${w.c.replace('Căn hộ/Chung cư','Căn hộ')}</td>
    <td class="n">${w.ban}</td><td class="n">${fmt(w.thue)}</td>
    <td class="n">${pc(w.gop)}</td>
    <td class="n ${w.rong < D.lts ? 'red':'green'}">${pc(w.rong)}</td>
    <td class="n muted">${w.nb}/${w.nt}</td></tr>`).join('');
}
document.querySelectorAll('#wt th').forEach(th =>
  th.addEventListener('click', ()=>drawTable(th.dataset.k)));
drawTable();
</script>
</body>
</html>
"""

rej_names = {
    "1_thieu_truong_bat_buoc": "Thiếu giá, diện tích hoặc phường",
    "2_dien_tich_vo_ly": "Diện tích ngoài khoảng 10–1.000 m²",
    "3_gia_vo_ly": "Giá ngoài khoảng hợp lý",
    "4_gia_tren_m2_vo_ly": "Giá trên m² vô lý (thường là tin đăng nhầm mục)",
    "5_trung_mem": "Trùng lặp: cùng người đăng, cùng diện tích, cùng giá",
}
rej_html = "".join(
    f"<tr><td>{rej_names.get(k, k)}</td><td class='n'>{v:,}</td></tr>".replace(",", ".")
    for k, v in sorted(clean["loai_bo"].items()))

html = (HTML
        .replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
        .replace("__RONG__", f"{fin['ti_suat_rong_trung_vi']:.2f}".replace(".", ","))
        .replace("__GOP__", f"{fin['ti_suat_gop_trung_vi']:.2f}".replace(".", ","))
        .replace("__LTS__", f"{LTS:.1f}".replace(".", ","))
        .replace("__NAM__", str(int(round(fin["so_nam_thu_hoi_von"]))))
        .replace("__NRAW__", f"{clean['tong_dong_vao']:,}".replace(",", "."))
        .replace("__NLIST__", f"{clean['giu_lai']:,}".replace(",", "."))
        .replace("__PCT__", f"{clean['ty_le_giu']:.1f}".replace(".", ","))
        .replace("__NW__", str(len(wards)))
        .replace("__NGAY__", "15/08/2026")
        .replace("__VDGIA__", f"{DATA['vd']['gia'] / 1e9:.2f} tỷ".replace(".", ","))
        .replace("__VDTHUE__", f"{DATA['vd']['thue'] / 1e6:.1f} triệu".replace(".", ","))
        .replace("__REJECTS__", rej_html))

WEB.mkdir(parents=True, exist_ok=True)
(WEB / "index.html").write_text(html, encoding="utf-8")
for f in ("yield_by_ward.json", "yield_by_district_size.json",
          "financial_summary.json", "clean_report.json"):
    (WEB / f).write_text((OUT / f).read_text(encoding="utf-8"), encoding="utf-8")

print(f"Da dung web/index.html  ({(WEB / 'index.html').stat().st_size / 1024:.0f} KB)")
print(f"  {len(districts)} quan · {len(wards)} o phuong · vi du can ho {DATA['vd']['gia']:,} d")
