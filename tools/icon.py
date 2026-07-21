#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.4", "resvg-py"]
# ///
"""icon.py — rasteriza um ícone Lucide (lib oficial de ícones) recolorido em PNG.

Os SVGs vivem em assets/icones/lucide/ (vendorizar com: uv run tools/fetch_icons.py).
Para peças, prefira o layer {"type": "icon", ...} direto no spec do compose.py; este
tool serve para gerar PNG avulso (mockups, testes, materiais fora do compose).

Uso:
    uv run tools/icon.py --name baby --color "#2563EB" --size 96 --out baby.png
    uv run tools/icon.py --name star --color "#1D4ED8" --size 56 \
        --circle-bg "#DBEAFE" --circle-r 56 --out icone.png   # com círculo de fundo

Catálogo de nomes: https://lucide.dev/icons (kebab-case).
"""

import argparse
import io
import re
import sys
from pathlib import Path

import resvg_py
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
LUCIDE_DIR = ROOT / "assets" / "icones" / "lucide"


def parse_color(value, default_alpha=255):
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    a = int(s[6:8], 16) if len(s) >= 8 else default_alpha
    return (r, g, b, a)


def rasterize_lucide(name, size, color, stroke_width=None):
    """Lê o SVG da Lucide, recolore o stroke e rasteriza em `size`×`size` (RGBA)."""
    path = LUCIDE_DIR / f"{name}.svg"
    if not path.exists():
        sys.exit(f"[erro] ícone '{name}' não existe em {LUCIDE_DIR} — confira o nome em "
                 f"https://lucide.dev/icons ou rode: uv run tools/fetch_icons.py")
    svg = path.read_text(encoding="utf-8")
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    if stroke_width is not None:
        svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg)
    png = resvg_py.svg_to_bytes(svg_string=svg, width=int(size), height=int(size))
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def main():
    ap = argparse.ArgumentParser(description="Rasteriza ícone Lucide em PNG.")
    ap.add_argument("--name", required=True, help="nome kebab-case (ex.: baby, stethoscope)")
    ap.add_argument("--color", default="#111827", help="cor do traço (hex)")
    ap.add_argument("--size", type=int, default=96, help="lado do ícone em px")
    ap.add_argument("--stroke", type=float, default=None, help="stroke-width (default: 2 do SVG)")
    ap.add_argument("--circle-bg", default=None, help="cor do círculo de fundo (hex), opcional")
    ap.add_argument("--circle-r", type=int, default=None, help="raio do círculo (default: size*0.95)")
    ap.add_argument("--out", required=True, help="arquivo .png de saída")
    args = ap.parse_args()

    icon = rasterize_lucide(args.name, args.size, args.color, args.stroke)

    if args.circle_bg:
        r = args.circle_r or round(args.size * 0.95)
        canvas = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
        d = ImageDraw.Draw(canvas)
        d.ellipse([0, 0, 2 * r, 2 * r], fill=parse_color(args.circle_bg))
        canvas.alpha_composite(icon, ((2 * r - icon.width) // 2, (2 * r - icon.height) // 2))
        icon = canvas

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    icon.save(out)
    print(f"[ok] {out}  ({icon.width}x{icon.height})")


if __name__ == "__main__":
    main()
