#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.4"]
# ///
"""
font_specimen.py — mural (post-wall) de fontes de TÍTULO com exemplo renderizado.

Entrega o item "~10 sugestões de fonte para títulos COM exemplos" da imersão: cada
fonte candidata é renderizada com o MESMO texto (o nome/título da marca), numerada,
em cards lado a lado — o cliente escolhe por número na aprovação (tools/aprovacao.py).

Renderiza a fonte REAL (variable font: ajusta o eixo wght pro peso de exibição), então
o cliente vê exatamente como o título vai sair. Fonte é insumo de LOGO/identidade, não
decoração — a lista de candidatas vem da pesquisa (agents/logo-design.md), não fixa.

Uso:
    uv run tools/font_specimen.py --text "Sua Marca" --out outputs/<job>/03-visual/fontes.png
    uv run tools/font_specimen.py --text "Aurora" --fonts assets/fontes/catalogo --cols 2
    uv run tools/font_specimen.py --text "Marca" --bg dark --sub "chamada de exemplo"
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "assets" / "fontes" / "catalogo"

THEMES = {
    "light": dict(page=(244, 242, 238), card=(255, 255, 255), ink=(28, 28, 30),
                  label=(120, 120, 128), num=(180, 178, 172), line=(232, 230, 224)),
    "dark":  dict(page=(24, 24, 27), card=(37, 37, 42), ink=(245, 244, 240),
                  label=(150, 150, 158), num=(90, 90, 96), line=(52, 52, 58)),
}


def load_variable(path: Path, size: int, weight: int) -> ImageFont.FreeTypeFont:
    """Fonte real com peso de exibição via eixo variável (fallback: estática)."""
    font = ImageFont.truetype(str(path), size=size)
    try:
        axes = font.get_variation_axes()
        vals = []
        for ax in axes:
            nm = ax.get("name", b"")
            nm = nm.decode("latin-1", "ignore") if isinstance(nm, bytes) else nm
            nm = nm.lower()
            lo, hi = ax["minimum"], ax["maximum"]
            if "weight" in nm or "wght" in nm:
                vals.append(max(lo, min(hi, weight)))
            elif "optical" in nm or "opsz" in nm:
                vals.append(max(lo, min(hi, size)))
            else:
                vals.append(ax["default"])
        if vals:
            font.set_variation_by_axes(vals)
    except OSError:
        pass
    return font


def label_family(path: Path) -> str:
    try:
        f = ImageFont.truetype(str(path), 20)
        return f.getname()[0]
    except Exception:
        return path.stem.split("[")[0].split("-")[0]


def fit_font(path: Path, text: str, max_w: int, max_h: int, cap: int, weight: int):
    """Maior tamanho cujo INK do texto cabe na zona do card (largura E altura, até cap).
    A altura evita que fontes de caixa alta invadam o número do card (o handle de
    escolha do cliente). Devolve (font, bbox_do_ink)."""
    size = cap
    while size > 20:
        font = load_variable(path, size, weight)
        x0, y0, x1, y1 = font.getbbox(text)
        if x1 - x0 <= max_w and y1 - y0 <= max_h:
            return font, (x0, y0, x1, y1)
        size -= 4
    font = load_variable(path, 20, weight)
    return font, font.getbbox(text)


def main():
    ap = argparse.ArgumentParser(description="Mural de fontes de título com exemplo.")
    ap.add_argument("--text", required=True, help="título a renderizar (nome/título da marca)")
    ap.add_argument("--sub", default="", help="subtítulo/chamada pequena opcional sob o título")
    ap.add_argument("--fonts", default=str(CATALOGO),
                    help="pasta de .ttf/.otf OU lista separada por vírgula (padrão: catálogo)")
    ap.add_argument("--out", required=True, help="PNG de saída (mural)")
    ap.add_argument("--cols", type=int, default=2, help="colunas do mural (padrão 2)")
    ap.add_argument("--bg", choices=["light", "dark"], default="light")
    ap.add_argument("--weight", type=int, default=700, help="peso de exibição (padrão 700)")
    ap.add_argument("--limit", type=int, default=0, help="máx. de fontes (0 = todas)")
    args = ap.parse_args()

    p = Path(args.fonts if Path(args.fonts).is_absolute() else ROOT / args.fonts)
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in (".ttf", ".otf")]
        # ordem CURADA por personalidade (catálogo grava _ordem.json) — para o --limit
        # padrão entregar VARIEDADE (serif/sans/display/condensada/arredondada), não a
        # fatia alfabética. Sem _ordem.json → alfabética.
        ordem_path = p / "_ordem.json"
        rank = {}
        if ordem_path.exists():
            try:
                rank = {name: i for i, name in enumerate(json.loads(ordem_path.read_text(encoding="utf-8")))}
            except Exception:
                rank = {}
        files.sort(key=lambda f: (rank.get(f.name, 10 ** 6), f.name))
    else:
        files = [Path(x if Path(x).is_absolute() else ROOT / x) for x in args.fonts.split(",")]
    files = [f for f in files if f.exists()]
    if args.limit:
        files = files[:args.limit]
    if not files:
        raise SystemExit(f"[erro] nenhuma fonte em {p}")

    t = THEMES[args.bg]
    CARD_W, CARD_H, GAP, MARGIN, PAD = 640, 224, 28, 56, 40
    cols = max(1, args.cols)
    rows = (len(files) + cols - 1) // cols
    W = MARGIN * 2 + cols * CARD_W + (cols - 1) * GAP
    HEADER = 132
    H = HEADER + MARGIN + rows * CARD_H + (rows - 1) * GAP + MARGIN

    img = Image.new("RGB", (W, H), t["page"])
    d = ImageDraw.Draw(img)

    label_path = next((f for f in files if "manrope" in f.name.lower()), files[0])
    h_title = load_variable(label_path, 40, 800)
    h_sub = load_variable(label_path, 21, 500)
    d.text((MARGIN, 44), "Fontes de título — escolha por número", font=h_title, fill=t["ink"])
    d.text((MARGIN, 96), f'Exemplo: "{args.text}"  ·  {len(files)} opções',
           font=h_sub, fill=t["label"])

    for i, fpath in enumerate(files):
        r, c = divmod(i, cols)
        x = MARGIN + c * (CARD_W + GAP)
        y = HEADER + MARGIN + r * (CARD_H + GAP)
        d.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=18, fill=t["card"],
                            outline=t["line"], width=1)

        num = f"{i + 1:02d}"
        fnum = load_variable(label_path, 30, 800)
        d.text((x + PAD, y + PAD - 4), num, font=fnum, fill=t["num"])

        # zona do título: abaixo do número, acima do rótulo da família (e do sub) —
        # centrado pelo INK real, para nenhuma fonte (mesmo caixa-alta) cobrir o número
        zona_top = y + 72
        zona_bot = y + CARD_H - 60 - (30 if args.sub else 0)
        title_font, bb = fit_font(fpath, args.text, CARD_W - 2 * PAD,
                                  zona_bot - zona_top, 92, args.weight)
        ink_h = bb[3] - bb[1]
        d.text((x + PAD - bb[0], zona_top + (zona_bot - zona_top - ink_h) // 2 - bb[1]),
               args.text, font=title_font, fill=t["ink"])

        if args.sub:
            sub_font = load_variable(fpath, 26, max(400, args.weight - 300))
            d.text((x + PAD, zona_bot + 18), args.sub, font=sub_font, fill=t["label"], anchor="lm")

        fam = label_family(fpath)
        flabel = load_variable(label_path, 20, 600)
        d.text((x + PAD, y + CARD_H - PAD + 6), f"{fam}", font=flabel, fill=t["label"], anchor="lb")

    out = Path(args.out if Path(args.out).is_absolute() else ROOT / args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"[ok] {out}  ({len(files)} fontes · {W}x{H})")


if __name__ == "__main__":
    main()
