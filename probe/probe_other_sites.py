"""Khao sat cac trang BDS khac: co cao duoc khong, robots.txt noi gi.

Moi trang chi goi 2 request (robots.txt + 1 trang danh sach) — do khao sat, khong phai cao.
Xuat: data/output/site_survey.json
"""

import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ROOT = Path(__file__).resolve().parent.parent

SITES = {
    "batdongsan.com.vn": "https://batdongsan.com.vn/nha-dat-ban-tp-hcm",
    "mogi.vn":           "https://mogi.vn/ho-chi-minh/mua-nha-dat",
    "alonhadat.com.vn":  "https://alonhadat.com.vn/nha-dat/can-ban/tp-hcm.html",
    "guland.vn":         "https://guland.vn/mua-ban-nha-dat-ho-chi-minh",
    "nhadat24h.net":     "https://nhadat24h.net/nha-dat-ban-tp-ho-chi-minh",
    "homedy.com":        "https://homedy.com/ban-nha-dat-ho-chi-minh",
    "bds123.vn":         "https://bds123.vn/nha-dat-ban-tp-ho-chi-minh.html",
    "muaban.net":        "https://muaban.net/bat-dong-san-tp-ho-chi-minh-l1",
}


def grab(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "vi-VN,vi;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        raw = r.read()
        enc = r.headers.get_content_charset() or "utf-8"
        return r.status, dict(r.headers), raw.decode(enc, errors="replace")


def check_robots(host):
    try:
        _, _, txt = grab(f"https://{host}/robots.txt", timeout=15)
    except Exception as e:
        return {"ok": False, "note": f"{type(e).__name__}"}
    lines = [l.strip() for l in txt.splitlines()]
    star, cur = [], None
    for l in lines:
        low = l.lower()
        if low.startswith("user-agent:"):
            cur = low.split(":", 1)[1].strip()
        elif low.startswith("disallow:") and cur == "*":
            star.append(l.split(":", 1)[1].strip())
    return {"ok": True, "disallow_all_agents": star[:14], "n_rules": len(star),
            "blocks_root": "/" in star}


def analyse(name, url):
    print("=" * 72)
    print(f"{name}")
    res = {"url": url}

    res["robots"] = check_robots(name)
    r = res["robots"]
    if r.get("ok"):
        flag = "CHAN TOAN BO" if r["blocks_root"] else f"{r['n_rules']} luat cam"
        print(f"  robots.txt : {flag}")
        if r["disallow_all_agents"]:
            print(f"               vd: {', '.join(r['disallow_all_agents'][:6])}")
    else:
        print(f"  robots.txt : khong doc duoc ({r.get('note')})")

    try:
        status, headers, html = grab(url)
    except urllib.error.HTTPError as e:
        srv = e.headers.get("server", "?") if e.headers else "?"
        res["fetch"] = {"status": e.code, "server": srv}
        verdict = "BI CHAN (Cloudflare)" if e.code in (403, 503) else f"HTTP {e.code}"
        print(f"  tai trang  : ✗ {verdict}  [server: {srv}]")
        return res
    except Exception as e:
        res["fetch"] = {"error": type(e).__name__}
        print(f"  tai trang  : ✗ {type(e).__name__}")
        return res

    server = headers.get("server", "?")
    res["fetch"] = {"status": status, "server": server, "bytes": len(html)}
    print(f"  tai trang  : ✓ HTTP {status}, {len(html)/1000:.0f} KB  [server: {server}]")

    # JSON nhung san trong HTML -> boc rat de
    embeds = [k for k, pat in {
        "__NEXT_DATA__": r"__NEXT_DATA__",
        "__NUXT__": r"__NUXT__",
        "INITIAL_STATE": r"__INITIAL_STATE__|window\.__initial",
        "ld+json": r'application/ld\+json',
    }.items() if re.search(pat, html, re.I)]
    res["embedded_json"] = embeds

    # HTML co san gia/dien tich khong (server-rendered) hay phai chay JS
    prices = len(re.findall(r"\d+[.,]?\d*\s*(?:tỷ|triệu)(?:/tháng)?", html))
    m2 = len(re.findall(r"\d+[.,]?\d*\s*m²|\d+\s*m2", html, re.I))
    res["price_hits"], res["m2_hits"] = prices, m2
    print(f"  trong HTML : {prices} chuoi gia, {m2} chuoi m²", end="")
    print(f"   | JSON nhung: {', '.join(embeds) if embeds else 'khong'}")

    if prices >= 15 and m2 >= 10:
        v = "DE — HTML co san gia va dien tich"
    elif embeds:
        v = "DUOC — phai boc JSON nhung trong trang"
    elif prices > 0:
        v = "KHO — co gia nhung thua thot"
    else:
        v = "KHONG — trang rong, phai chay JavaScript"
    res["verdict"] = v
    print(f"  ket luan   : {v}")
    return res


def main():
    out = {}
    for name, url in SITES.items():
        try:
            out[name] = analyse(name, url)
        except Exception as e:
            out[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"  !! {type(e).__name__}")
        time.sleep(1.2)

    p = ROOT / "data" / "output" / "site_survey.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=" * 72)
    print(f"Da ghi {p}")


if __name__ == "__main__":
    main()
