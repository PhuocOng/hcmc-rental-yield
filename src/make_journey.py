r"""Ghep 6 clip flycam thanh MOT hanh trinh lien tuc lam nen cho ca trang chu.

Hanh trinh: may -> rung ngap man -> cho noi mien Tay -> TP.HCM -> giua cao oc
-> duong pho. Tat ca la footage THAT tu Pexels, khong sinh bang AI.

Hai viec bat buoc, thieu cai nao cung thanh trinh chieu anh chu khong phai mot
cu bay:
  1. Chinh CUNG MOT tong cho ca sau clip. Chung lech mau rat xa: ba clip dau
     nang gat va ruc, ba clip sau am va mo.
  2. Hoa tan giua cac chang, khong cat thang.

Vi day la NEN nam sau chu, ha bao hoa manh tay la dung: no phai lui ve lam ket
cau, khong tranh cho voi noi dung.

Chay: python src/make_journey.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:/Users/onggi/AppData/Local/Temp/claude"
    r"/C--Users-onggi-OneDrive-Desktop-old-FacebookReels"
    r"/ecb42b94-4374-482a-8df2-f76c108e8627/scratchpad/journey")
ASSETS = ROOT / "docs" / "assets"
OUT = ASSETS / "hero-scrub.mp4"
POSTER = ASSETS / "hero-poster.jpg"

W, FPS, SEG, FADE = 1152, 30, 5.5, 1.1      # be ngang, fps, giay moi chang, giay hoa tan

# (file, giay bat dau) — chon doan dep nhat cua tung clip
STAGES = [
    # Bo chang may thuan (chi co may, khong co gi de nhin). Chang AI "ven may lo ra
    # song" len lam mo dau: no vua co may vua co mat dat, vao de hon.
    ("2_ha-xuong.mp4", 0),          # AI  — ven may, song va dong bang hien ra
    ("3_dong-bang.mp4", 5),         # that — cho noi mien Tay
    ("4_tphcm.mp4", 30),            # that — TP.HCM nhin rong
    ("7_tphcm-hoang-hon.mp4", 31),  # that — cao oc luc hoang hon (chang moi them)
    ("5_giua-cao-oc.mp4", 6),       # that — luon giua cao oc
    ("6_duong-pho.mp4", 4),         # that — vong xoay nhin thang xuong
]

# Tong chung: ha bao hoa manh, toi di, hoi am. Bien no thanh ket cau nen.
GRADE = "eq=saturation=0.42:brightness=-0.10:contrast=1.12,colorbalance=rs=.04:bs=-.03"

SCRUB_FLAGS = ["-c:v", "libx264", "-crf", "31", "-preset", "slow",
               "-g", "8", "-keyint_min", "8", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", "-an"]


def run(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    missing = [f for f, _ in STAGES if not (SRC / f).exists()]
    if missing:
        sys.exit(f"Thieu clip nguon trong {SRC}:\n  " + "\n  ".join(missing))

    ins: list[str] = []
    for f, ss in STAGES:
        ins += ["-ss", str(ss), "-t", str(SEG), "-i", str(SRC / f)]

    # Chuan hoa tung chang ve cung kich thuoc, cung fps, cung tong mau
    # force_original_aspect_ratio=increase: phong de PHU KIN khung roi moi cat.
    # Cac clip nguon khong cung ty le (co cai 2048x1080), thu thang ve be ngang
    # roi cat se thieu chieu cao va ffmpeg do.
    H = int(W * 9 / 16)
    parts = [f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
             f"crop={W}:{H},fps={FPS},{GRADE},setpts=PTS-STARTPTS[v{i}]"
             for i in range(len(STAGES))]

    # Noi bang xfade. Moc thoi gian phai TRU DON phan da hoa tan cua cac chang truoc,
    # neu khong cac chang sau se bi cat cut.
    chain, prev, t = [], "v0", 0.0
    for i in range(1, len(STAGES)):
        t += SEG - FADE
        lab = f"x{i}"
        chain.append(f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={t:.2f}[{lab}]")
        prev = lab

    fc = ";".join(parts + chain)
    run(ins + ["-filter_complex", fc, "-map", f"[{prev}]"] + SCRUB_FLAGS + [str(OUT)])
    run(["-ss", "0.2", "-i", str(OUT), "-frames:v", "1", "-q:v", "3", str(POSTER)])

    dur = len(STAGES) * SEG - (len(STAGES) - 1) * FADE
    mb = OUT.stat().st_size / 1e6
    print(f"  {len(STAGES)} chang, {dur:.1f} giay, {W}px")
    print(f"  {OUT.relative_to(ROOT)}   {mb:.2f} MB")
    print(f"  {POSTER.relative_to(ROOT)}   {POSTER.stat().st_size / 1024:.0f} KB")
    if mb > 12:
        print(f"  ! {mb:.1f} MB nang cho nen di dong. Tang -crf hoac ha W.")


if __name__ == "__main__":
    main()
