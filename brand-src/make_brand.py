"""Render RME wordmark SVG into HA brand PNGs (light + dark variants)."""

import os
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image

svg_path, out_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
# Any Chromium-based browser works; defaults to Edge's standard Windows location.
edge = os.environ.get(
    "BROWSER_BIN", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)
out_dir.mkdir(parents=True, exist_ok=True)
svg = svg_path.read_text(encoding="utf-8")
svg = re.sub(r'\swidth="150" height="27"', "", svg, count=1)

W, H = 2800, 500  # render big, downscale later


def render(color: str) -> Image.Image:
    colored = svg.replace("#FFFFFF", color)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "logo.svg").write_text(colored, encoding="utf-8")
        (tmp / "page.html").write_text(
            "<html><body style='margin:0;background:transparent'>"
            f"<img src='logo.svg' style='width:{W}px;height:{H}px;object-fit:contain'>"
            "</body></html>",
            encoding="utf-8",
        )
        png = tmp / "shot.png"
        subprocess.run(
            [edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--default-background-color=00000000", f"--window-size={W},{H}",
             f"--user-data-dir={tmp / 'profile'}",
             f"--screenshot={png}", (tmp / "page.html").as_uri()],
            check=True, capture_output=True, timeout=60,
        )
        img = Image.open(png).convert("RGBA")
        img.load()
    return img.crop(img.getbbox())  # trim transparent edges


def fit_height(img: Image.Image, h: int) -> Image.Image:
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)


def square(img: Image.Image, size: int, pad: float = 0.06) -> Image.Image:
    inner = round(size * (1 - 2 * pad))
    scale = inner / max(img.width, img.height)
    small = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(small, ((size - small.width) // 2, (size - small.height) // 2), small)
    return canvas


for prefix, color in (("", "#1A1A1A"), ("dark_", "#FFFFFF")):
    art = render(color)
    fit_height(art, 128).save(out_dir / f"{prefix}logo.png", optimize=True)
    fit_height(art, 256).save(out_dir / f"{prefix}logo@2x.png", optimize=True)
    square(art, 256).save(out_dir / f"{prefix}icon.png", optimize=True)
    square(art, 512).save(out_dir / f"{prefix}icon@2x.png", optimize=True)

for p in sorted(out_dir.iterdir()):
    print(p.name, Image.open(p).size)
