r"""Nen video hero cho ky thuat cuon-tua.

Diem sinh tu la `-g 8 -keyint_min 8`: ep keyframe day gap khoang 15 lan binh
thuong. Video thuong dat keyframe moi 2 giay, nen muon nhay toi giay 3,7 thi
trinh duyet phai giai ma tu keyframe gan nhat va tua bi giat. Keyframe moi 8
khung hinh thi tua toi dau cung gan nhu tuc thi.

Chay:
    python src/make_hero_video.py raw.mp4 --ss 31 --t 9    cat doan roi nen
    python src/make_hero_video.py raw.mp4                  nen ca file
    python src/make_hero_video.py --test                   video kiem thu co so khung

Video dang dung tren trang lay tu Pexels id 28896185 (Kasim Luat, flycam TP.HCM
luc hoang hon), cat doan 31s-40s. Lenh tai:
    curl -H "Authorization: <PEXELS_KEY>" -H "User-Agent: Mozilla/5.0"          https://api.pexels.com/videos/videos/28896185
BAT BUOC co User-Agent, thieu no Pexels tra 403 ke ca khi key dung.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
OUT = ASSETS / "hero-scrub.mp4"
POSTER = ASSETS / "hero-poster.jpg"
FONT = r"C\:/Windows/Fonts/consolab.ttf"

# Giu nguyen bo co nay cho MOI lan nen. Chi duoc chinh -crf va do phan giai.
# crf 23: o muc phong 1:1 gan nhu khong phan biet duoc voi crf 20, ma nhe hon 40%.
# Giu nguyen moi co con lai cho MOI lan nen.
SCRUB_FLAGS = ["-c:v", "libx264", "-crf", "23", "-preset", "slow",
               "-g", "8", "-keyint_min", "8", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", "-an"]

TEST_VF = (
    r"drawbox=x='(t/6)*(iw+400)-400':y=ih*0.18:w=380:h=ih*0.64:color=0xA8432A@0.55:t=fill,"
    r"drawbox=x='(t/6)*(iw+700)-700':y=ih*0.30:w=660:h=ih*0.40:color=0x1F5E5B@0.45:t=fill,"
    r"drawtext=fontfile='" + FONT + r"':text='%{eif\:n\:d}':fontcolor=white:fontsize=200"
    r":x=(w-tw)/2:y=(h-th)/2,"
    r"drawtext=fontfile='" + FONT + r"':text='TEST SCRUB':fontcolor=0x8A8279:fontsize=40"
    r":x=(w-tw)/2:y=h*0.74"
)


def run(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    if "--test" in sys.argv:
        # Video kiem thu: in so khung hinh len giua man, de doi chieu vi tri cuon
        # voi frame thuc te dang hien.
        run(["-f", "lavfi", "-i", "color=c=0x131211:s=1920x1080:d=6:r=30",
             "-vf", TEST_VF] + SCRUB_FLAGS + [str(OUT)])
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Nen video that. Ha bao hoa va toi di mot chut de footage lui ve lam NEN,
        # khong tranh cho voi chu de len tren.
        trim = []
        if "--ss" in sys.argv:
            trim += ["-ss", sys.argv[sys.argv.index("--ss") + 1]]
        if "--t" in sys.argv:
            trim += ["-t", sys.argv[sys.argv.index("--t") + 1]]
        run(trim + ["-i", sys.argv[1],
                    "-vf", "scale=1920:-2,eq=brightness=-0.05:saturation=0.82:contrast=1.06"]
            + SCRUB_FLAGS + [str(OUT)])
    else:
        sys.exit(__doc__)

    run(["-i", str(OUT), "-frames:v", "1", "-q:v", "2", str(POSTER)])
    mb = OUT.stat().st_size / 1e6
    print(f"  {OUT.relative_to(ROOT)}   {mb:.2f} MB")
    print(f"  {POSTER.relative_to(ROOT)}   {POSTER.stat().st_size / 1024:.0f} KB")
    if mb > 8:
        print(f"  ! {mb:.1f} MB la nang cho mang di dong."
              f" Tang -crf len 22-25, hoac ha do phan giai xuong 1600px.")


if __name__ == "__main__":
    main()
