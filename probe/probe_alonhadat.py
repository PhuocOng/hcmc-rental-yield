"""Do cau truc HTML cua alonhadat.com.vn truoc khi viet scraper.

Can biet: khoi tin nam trong the nao, co dien tich khong, dia chi chi tiet toi
cap nao (quan hay phuong), URL trang cho thue, va cach phan trang.
"""

import re
import ssl
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ROOT = Path(__file__).resolve().parent.parent


def grab(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "vi-VN,vi;q=0.9"})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        raw = r.read()
    for enc in ("utf-8", "windows-1258", "latin-1"):
        try:
            return r.status, raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return r.status, raw.decode("utf-8", errors="replace")


URLS = {
    "ban":  "https://alonhadat.com.vn/nha-dat/can-ban/tp-hcm.html",
    "thue": "https://alonhadat.com.vn/nha-dat/cho-thue/tp-hcm.html",
    "ban_trang2": "https://alonhadat.com.vn/nha-dat/can-ban/tp-hcm/2/trang--2.html",
}

for label, url in URLS.items():
    print("=" * 72)
    print(f"[{label}] {url}")
    try:
        status, html = grab(url)
    except Exception as e:
        print(f"   ✗ {type(e).__name__}: {e}")
        continue
    print(f"   HTTP {status}, {len(html)/1000:.0f} KB")
    (ROOT / "data" / "output" / f"alonhadat_{label}.html").write_text(html, encoding="utf-8")

    # cac class hay dung -> doan khoi chua tin
    classes = Counter(re.findall(r'class="([a-z0-9_\- ]{3,40})"', html, re.I))
    top = [c for c, n in classes.most_common(18) if n >= 3]
    print(f"   class lap nhieu: {top[:12]}")

    # dem cac dau hieu du lieu
    print(f"   gia (tỷ/triệu) : {len(re.findall(r'\\d+[.,]?\\d*\\s*(?:tỷ|triệu)', html))}")
    print(f"   dien tich m2   : {len(re.findall(r'\\d+[.,]?\\d*\\s*m(?:²|2)', html, re.I))}")
    print(f"   link chi tiet  : {len(set(re.findall(r'href=\"(/[^\"]*?\\.html)\"', html)))}")

    # dia chi chi tiet toi dau?
    print(f"   nhac 'Phường'  : {len(re.findall(r'Phường|Phuong', html))}")
    print(f"   nhac 'Quận'    : {len(re.findall(r'Quận|Quan ', html))}")

print("=" * 72)
print("[chi tiet] Boc thu MOT khoi tin tu trang ban")
_, html = grab(URLS["ban"])
m = re.search(r'<div class="content-item".{0,2500}?</div>\s*</div>', html, re.S)
if not m:
    m = re.search(r'(<div class="[^"]*item[^"]*".{500,2500}?)</div>\s*</div>', html, re.S)
if m:
    block = re.sub(r"\s+", " ", m.group(0))
    print(block[:1400])
else:
    idx = html.find("tỷ")
    print("   Khong khop mau quen — doan quanh chu 'tỷ':")
    print(re.sub(r"\s+", " ", html[max(0, idx - 900):idx + 500]))

print("=" * 72)
print("Da luu HTML vao data/output/alonhadat_*.html de xem tay neu can")
