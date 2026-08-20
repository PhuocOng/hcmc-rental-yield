"""Chuan bi ban do: GeoJSON ranh gioi 22 quan/huyen TP.HCM cho Leaflet.

Ban truoc tu chieu toa do sang duong SVG de trang tu chua het. Ban nay dung
Leaflet + anh ve tinh -> phai la GeoJSON that, va da chap nhan phu thuoc mang.

Viec chinh o day la GIAN LUOC: file goc 232 KB qua nang de nhung thang vao HTML.
Dung thuat toan Douglas-Peucker (giu lai cac diem lam nen hinh dang, bo cac diem
nam gan nhu tren duong thang) thay vi bo bua theo khoang cach.

Nguon: github.com/nguyencaonhan271201/tphcm_district_boundaries

Chay: python src/prep_map.py  ->  data/output/hcm_geo.json
"""

from __future__ import annotations

import json
import ssl
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "output"
GEO = OUT / "hcm_districts.geojson"
URL = ("https://raw.githubusercontent.com/nguyencaonhan271201/"
       "tphcm_district_boundaries/main/hcm.geojson")

EPS = 0.00012      # ~13 m — du min o muc zoom thanh pho
NDIGITS = 5        # ~1 m


def load_geo() -> dict:
    if not GEO.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as r:
            GEO.write_text(r.read().decode("utf-8"), encoding="utf-8")
    return json.loads(GEO.read_text(encoding="utf-8"))


def perp_dist(p, a, b) -> float:
    """Khoang cach tu p toi doan thang ab."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5


def douglas_peucker(pts: list, eps: float) -> list:
    """Giu lai diem xa duong noi hai dau nhat, de quy hai nua. Vong lap thay de quy
    de khong tran stack voi ring nhieu diem."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        dmax, idx = 0.0, i
        for k in range(i + 1, j):
            d = perp_dist(pts[k], pts[i], pts[j])
            if d > dmax:
                dmax, idx = d, k
        if dmax > eps:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [p for p, k in zip(pts, keep) if k]


def rings(geom: dict):
    t = geom.get("type")
    if t == "Polygon":
        yield from geom["coordinates"]
    elif t == "MultiPolygon":
        for poly in geom["coordinates"]:
            yield from poly
    elif t == "GeometryCollection":
        for g in geom.get("geometries", []):
            yield from rings(g)


def title_vi(s: str) -> str:
    """'QUẬN GÒ VẤP' -> 'Quận Gò Vấp' (khop voi ten trong du lieu Cho Tot)."""
    return " ".join(w.capitalize() for w in s.strip().split())


geo = load_geo()
feats, n_in, n_out = [], 0, 0
lons, lats = [], []

for f in geo["features"]:
    polys = []
    for ring in rings(f["geometry"]):
        pts = [(lon, lat) for lon, lat, *_ in ring]
        n_in += len(pts)
        simp = douglas_peucker(pts, EPS)
        if len(simp) < 4:
            continue
        if simp[0] != simp[-1]:
            simp.append(simp[0])          # GeoJSON: ring phai khep kin
        n_out += len(simp)
        lons += [p[0] for p in simp]
        lats += [p[1] for p in simp]
        polys.append([[round(x, NDIGITS), round(y, NDIGITS)] for x, y in simp])

    feats.append({
        "type": "Feature",
        "properties": {"ten": title_vi(f["properties"]["name"])},
        "geometry": {"type": "MultiPolygon", "coordinates": [[p] for p in polys]},
    })

fc = {"type": "FeatureCollection", "features": feats}
(OUT / "hcm_geo.json").write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")),
                                  encoding="utf-8")

bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
(OUT / "hcm_bounds.json").write_text(json.dumps(bounds), encoding="utf-8")

kb = (OUT / "hcm_geo.json").stat().st_size / 1024
print(f"{len(feats)} quan/huyen")
print(f"diem: {n_in:,} -> {n_out:,}  (gian luoc {100 - n_out / n_in * 100:.0f}%)")
print(f"khung bao: {bounds[0][0]:.3f},{bounds[0][1]:.3f} .. {bounds[1][0]:.3f},{bounds[1][1]:.3f}")
print(f"Da ghi data/output/hcm_geo.json  ({kb:.0f} KB)")
print("\nTen sau chuan hoa:")
for f in feats[:5]:
    print("  ", f["properties"]["ten"])
