#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["vtracer", "pillow", "resvg-py"]
# ///
"""
vectorize.py — vetorização raster→SVG (acabamento de logo/símbolo gerado por IA).

Fecha a lacuna de toolchain do harness: o `compose.py`/`icon.py` só rasterizam
(SVG→PNG); este tool faz o inverso (PNG→SVG) para o caminho ORGÂNICO/ilustrado do
logo, onde não há SVG autoral por código.

Regras da casa (agents/logo-design.md):
- SVG cristalino = wordmark/monograma/geométrico desenhados por CÓDIGO (não é aqui).
- Este tool é ACABAMENTO do símbolo orgânico/ilustrado: auto-trace com curadoria.
  Auto-trace de arte de IA NEM SEMPRE sai limpo — sempre olhar o preview, o
  COMPARATIVO e o nº de nós, e reprovar se ficar pesado/impreciso (o tool imprime
  as métricas do gate).
- `--mode color` (padrão, vtracer spline) para marca com cores chapadas;
  `--mode mono` (binário) para silhueta/positivo-negativo.

Qualidade de CURVAS (a parte que o auto-trace mais erra) — o preparo do raster faz
o trabalho pesado ANTES do trace:
1. **Upscale automático** (LANCZOS) para ~2400px quando a entrada é menor — curva
   traçada em 1024px sai poligonal/ondulada; em alta resolução o ajuste de spline
   converge. Controle: `--upscale auto|none|<fator>` (default auto, teto 4×).
2. **Knockout do fundo chapado** (como antes, agora em operações de imagem — rápido
   mesmo em alta resolução).
3. **Recorte do halo**: pixels de borda que ficaram entre o fundo e a arte (o
   anti-aliasing) criam contorno duplo e serrilhado no vetor — são removidos.
4. **Alpha binarizado** (borda dura) — o vtracer ajusta curvas melhor sem meia-
   transparência.

Gates automáticos na saída:
- **Fidelidade de silhueta (IoU)**: o SVG é re-rasterizado e comparado com o raster
  preparado; abaixo de 98,5% o tool avisa (curvas/formas se afastaram do original).
- **Comparativo lado a lado** `<saida>-compare.png` (original | vetor) — olhar com
  zoom nas curvas é parte do gate do logo-design.
- **Peso**: paths/nós/KB — SVG pesado = trace impreciso.

Sempre gera um preview PNG rasterizado do SVG (mesmo motor resvg do compose).

Uso:
    uv run tools/vectorize.py entrada.png --out logo.svg
    uv run tools/vectorize.py entrada.png --out icone.svg --mode mono
    uv run tools/vectorize.py entrada.png --out logo.svg --detail alto      # mais fiel
    uv run tools/vectorize.py entrada.png --out logo.svg --corner-threshold 80  # curvas mais suaves
"""

import argparse
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Presets de detalhe: quanto MAIOR o filter_speckle, mais limpo (menos nós/ruído).
# color_precision/gradient_step controlam a fidelidade de cor. Ajustados para logo
# (cores chapadas, formas nítidas) — não para foto.
DETAIL_PRESETS = {
    "limpo": dict(filter_speckle=8, color_precision=6, layer_difference=16, corner_threshold=60,
                  length_threshold=4.0, splice_threshold=45, path_precision=3),
    "medio": dict(filter_speckle=4, color_precision=7, layer_difference=12, corner_threshold=60,
                  length_threshold=3.5, splice_threshold=45, path_precision=4),
    "alto":  dict(filter_speckle=2, color_precision=8, layer_difference=8, corner_threshold=45,
                  length_threshold=3.0, splice_threshold=45, path_precision=5),
}

ALVO_UPSCALE = 2400   # lado maior desejado para o trace
TETO_UPSCALE = 4.0
IOU_MINIMO = 0.985


def _corner_bg(im):
    """Cor de fundo estimada pela mediana dos 4 cantos (logo em fundo chapado)."""
    w, h = im.size
    pts = [(1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)]
    cs = [im.getpixel(p)[:3] for p in pts]
    med = tuple(sorted(c[i] for c in cs)[len(cs) // 2] for i in range(3))
    return med


def _fator_upscale(size, modo):
    if modo == "none":
        return 1.0
    if modo != "auto":
        try:
            return max(1.0, min(TETO_UPSCALE, float(modo)))
        except ValueError:
            sys.exit(f"[erro] --upscale inválido: {modo} (use auto | none | um fator, ex. 2.5)")
    maior = max(size)
    if maior >= 1800:
        return 1.0
    return min(TETO_UPSCALE, ALVO_UPSCALE / maior)


def _dist_para_cor(im_rgb, cor):
    """Distância Chebyshev (maior canal) de cada pixel até `cor`, como imagem L."""
    from PIL import Image, ImageChops
    solida = Image.new("RGB", im_rgb.size, cor)
    diff = ImageChops.difference(im_rgb, solida)
    r, g, b = diff.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b)


def _achatar_cores(im, n, minimo=0.008):
    """Achata a arte nas cores DOMINANTES: mede a população (mediancut 64), mantém
    as cores que cobrem ≥ `minimo` do canvas (até n) e faz snap de TODO pixel para
    a dominante mais próxima. O degradê de anti-aliasing da borda — que o trace
    transforma em dezenas de camadas finas e contorno duplo — colapsa nas cores
    reais do logo. n=0 desliga."""
    from PIL import Image

    if not n:
        return im
    rgb = im.convert("RGB")
    amostra = rgb.quantize(colors=64, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    contagens = sorted(amostra.getcolors(maxcolors=64) or [], reverse=True)
    if not contagens:
        return im
    total = sum(c for c, _ in contagens)
    pal = amostra.getpalette()
    cores = [tuple(pal[i * 3:i * 3 + 3]) for c, i in contagens if c / total >= minimo][:n]
    if len(cores) < 2:  # arte quase monocromática: garante fundo + arte
        cores = [tuple(pal[i * 3:i * 3 + 3]) for c, i in contagens[:2]]

    pal_img = Image.new("P", (1, 1))
    paleta = [canal for cor in cores for canal in cor]
    paleta += list(cores[0]) * (256 - len(cores))  # padding repete a 1ª (nunca vence sozinho)
    pal_img.putpalette(paleta)
    achatada = rgb.quantize(palette=pal_img, dither=Image.Dither.NONE).convert("RGB").convert("RGBA")
    achatada.putalpha(im.getchannel("A"))
    return achatada


def _aparar_halo(im, cor_bg, tol, passes=2):
    """Remove o halo de anti-aliasing: pixel ainda opaco, com cor PRÓXIMA do fundo e
    ENCOSTADO em área transparente, vira transparente. Poucas passadas bastam."""
    from PIL import ImageChops, ImageFilter

    tol_halo = min(int(tol * 2), 96)
    perto_do_bg = _dist_para_cor(im.convert("RGB"), cor_bg).point(
        lambda v: 255 if v <= tol_halo else 0)
    for _ in range(passes):
        alfa = im.getchannel("A")
        transparente = alfa.point(lambda v: 255 if v == 0 else 0)
        vizinho = transparente.filter(ImageFilter.MaxFilter(3))  # dilata 1px
        opaco = alfa.point(lambda v: 255 if v > 0 else 0)
        halo = ImageChops.multiply(ImageChops.multiply(perto_do_bg, vizinho), opaco)
        manter = halo.point(lambda v: 0 if v else 255)
        im.putalpha(ImageChops.multiply(alfa, manter))
    return im


def prep_raster(png_path: Path, knockout: str, tol: int, upscale: str, max_cores: int):
    """Prepara o raster para o trace: upscale (curvas precisam de resolução),
    posterização (cores chapadas), knockout do fundo chapado para transparente,
    recorte do halo de borda, alpha binarizado (borda dura) e autocrop.
    Devolve (caminho_prep, resumo_str)."""
    from PIL import Image, ImageChops

    im = Image.open(png_path).convert("RGBA")
    passos = []

    fator = _fator_upscale(im.size, upscale)
    if fator > 1.001:
        im = im.resize((round(im.width * fator), round(im.height * fator)), Image.LANCZOS)
        passos.append(f"upscale {fator:.1f}× → {im.width}×{im.height}")

    if max_cores:
        im = _achatar_cores(im, max_cores)
        passos.append(f"cores achatadas (≤{max_cores})")

    target = None
    if knockout and knockout != "none":
        if knockout == "auto":
            target = _corner_bg(im)
        else:
            s = knockout.lstrip("#")
            target = tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

    if target is not None:
        fundo = _dist_para_cor(im.convert("RGB"), target).point(
            lambda v: 0 if v <= tol else 255)          # 0 = é fundo
        im.putalpha(ImageChops.multiply(im.getchannel("A"), fundo))
        passos.append("knockout #%02X%02X%02X" % target)
        im = _aparar_halo(im, target, tol, passes=max(2, round(2 * fator)))
        passos.append("halo aparado")

    # borda dura: meia-transparência confunde o ajuste de curvas do trace
    im.putalpha(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0))

    bbox = im.split()[-1].getbbox()  # bbox do conteúdo (não-transparente)
    if bbox:
        pad = max(4, round(4 * fator))
        x0, y0, x1, y1 = bbox
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
        im = im.crop((x0, y0, x1, y1))

    out = png_path.with_name(png_path.stem + "-prep.png")
    im.save(out)
    return out, (" · ".join(passos) or "sem preparo extra"), fator


def tidy_svg(svg: str) -> str:
    """Garante viewBox (escala nítida em qualquer tamanho) e remove comentário do gerador."""
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.DOTALL)
    if "viewBox" not in svg:
        m = re.search(r'<svg\b[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', svg)
        if m:
            w, h = m.group(1), m.group(2)
            svg = re.sub(r"<svg\b", f'<svg viewBox="0 0 {w} {h}"', svg, count=1)
    return re.sub(r"\n{2,}", "\n", svg).strip() + "\n"


def svg_metrics(svg: str) -> dict:
    paths = re.findall(r"<path\b", svg)
    # nº aproximado de nós = comandos de desenho nos atributos d="..."
    nodes = len(re.findall(r"[MmLlCcSsQqTtAaHhVvZz]", " ".join(re.findall(r'\bd="([^"]*)"', svg))))
    return {"paths": len(paths), "nodes": nodes, "bytes": len(svg.encode("utf-8"))}


def _mascara_bin(im):
    return im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)


def _pixels_marcados(mask):
    return sum(mask.histogram()[1:])


def fidelidade_silhueta(svg: str, prep_path: Path):
    """Re-rasteriza o SVG no tamanho do raster preparado e mede o IoU das silhuetas
    (cobertura de tinta). Devolve (iou, prep_img, render_img)."""
    import resvg_py
    from PIL import Image, ImageChops

    prep = Image.open(prep_path).convert("RGBA")
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=prep.width))
    render = Image.open(io.BytesIO(png)).convert("RGBA")
    if render.size != prep.size:
        render = render.resize(prep.size, Image.LANCZOS)

    m1, m2 = _mascara_bin(prep), _mascara_bin(render)
    inter = _pixels_marcados(ImageChops.multiply(m1, m2))
    uniao = _pixels_marcados(ImageChops.lighter(m1, m2))
    iou = (inter / uniao) if uniao else 1.0
    return iou, prep, render


def salvar_compare(prep, render, out_path: Path):
    """Comparativo lado a lado (original preparado | vetor re-rasterizado), fundo
    branco — é nele que a curadoria dá zoom nas curvas."""
    from PIL import Image

    alvo_h = min(900, prep.height)

    def achatar(im):
        fator = alvo_h / im.height
        im = im.resize((max(1, round(im.width * fator)), alvo_h), Image.LANCZOS)
        base = Image.new("RGB", im.size, (255, 255, 255))
        base.paste(im, (0, 0), im)
        return base

    a, b = achatar(prep), achatar(render)
    gap = 24
    canvas = Image.new("RGB", (a.width + b.width + gap, alvo_h), (231, 235, 240))
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width + gap, 0))
    canvas.save(out_path)


def main():
    ap = argparse.ArgumentParser(description="Vetoriza PNG→SVG (acabamento de logo orgânico).")
    ap.add_argument("input", help="PNG de entrada (marca finalizada em alta-res)")
    ap.add_argument("--out", required=True, help="SVG de saída")
    ap.add_argument("--mode", choices=["color", "mono"], default="color",
                    help="color (cores chapadas) | mono (silhueta binária)")
    ap.add_argument("--detail", choices=list(DETAIL_PRESETS), default="limpo",
                    help="limpo (menos nós, padrão) | medio | alto (mais fiel, mais pesado)")
    ap.add_argument("--knockout", default="auto",
                    help="derrubar fundo chapado p/ transparente: auto | none | #hex (padrão auto)")
    ap.add_argument("--tol", type=int, default=22, help="tolerância de cor do knockout (0-255)")
    ap.add_argument("--upscale", default="auto",
                    help=f"ampliar antes do trace (curvas melhores): auto (até ~{ALVO_UPSCALE}px, "
                         f"padrão) | none | fator (ex. 2.5; teto {TETO_UPSCALE:g}×)")
    ap.add_argument("--max-cores", type=int, default=16,
                    help="posterizar para ≤N cores chapadas antes do trace (mata o degradê "
                         "de anti-alias que vira contorno duplo); 0 desliga (padrão 16)")
    ap.add_argument("--corner-threshold", type=int, default=None,
                    help="sobrepõe o corner_threshold do preset (graus; MAIOR = curvas mais "
                         "suaves/menos cantos — bom p/ orgânico; menor preserva cantos vivos)")
    ap.add_argument("--preview-size", type=int, default=1024,
                    help="lado do PNG de preview rasterizado do SVG (0 = não gerar)")
    args = ap.parse_args()

    inp = Path(args.input if Path(args.input).is_absolute() else ROOT / args.input)
    if not inp.exists():
        sys.exit(f"[erro] entrada não encontrada: {inp}")
    out = Path(args.out if Path(args.out).is_absolute() else ROOT / args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    max_cores = 0 if args.mode == "mono" else args.max_cores
    src, resumo_prep, fator = prep_raster(inp, args.knockout, args.tol, args.upscale, max_cores)
    print(f"[prep] {resumo_prep}")

    try:
        import vtracer
    except ImportError:
        sys.exit("[erro] rode via `uv run tools/vectorize.py ...` (resolve vtracer sozinho)")

    preset = dict(DETAIL_PRESETS[args.detail])
    # parâmetros em PIXELS acompanham o upscale — o preset se comporta como na escala original
    preset["filter_speckle"] = max(1, round(preset["filter_speckle"] * fator))
    preset["length_threshold"] = preset["length_threshold"] * fator
    if args.corner_threshold is not None:
        preset["corner_threshold"] = args.corner_threshold
    kwargs = dict(
        colormode="binary" if args.mode == "mono" else "color",
        mode="spline",
        hierarchical="stacked",
        **preset,
    )
    tmp_svg = out.with_suffix(".raw.svg")
    vtracer.convert_image_to_svg_py(str(src), str(tmp_svg), **kwargs)

    svg = tidy_svg(tmp_svg.read_text(encoding="utf-8"))
    out.write_text(svg, encoding="utf-8")
    tmp_svg.unlink(missing_ok=True)
    print(f"[ok] {out}")

    m = svg_metrics(svg)
    print(f"[gate] paths={m['paths']} · nós≈{m['nodes']} · {round(m['bytes']/1024,1)} KB")
    if m["nodes"] > 1200 or m["bytes"] > 120_000:
        print("[aviso] SVG pesado — auto-trace de IA impreciso. Considere --detail limpo, "
              "simplificar o símbolo, ou redesenhar por código. Curadoria obrigatória.")

    iou, prep_img, render_img = fidelidade_silhueta(svg, src)
    compare = out.with_name(out.stem + "-compare.png")
    salvar_compare(prep_img, render_img, compare)
    print(f"[gate] fidelidade de silhueta (IoU) = {iou:.1%}")
    print(f"[ok] {compare}  (original | vetor — dar ZOOM nas curvas antes de aprovar)")
    if iou < IOU_MINIMO:
        print(f"[aviso] fidelidade abaixo de {IOU_MINIMO:.1%} — curvas/formas se afastaram do "
              "original. Tentar --detail alto, --corner-threshold maior (orgânico) ou "
              "redesenhar por código. NÃO aprovar sem curadoria do comparativo.")

    if src != inp:
        src.unlink(missing_ok=True)

    if args.preview_size:
        import resvg_py
        prev = out.with_name(out.stem + f"-preview-{args.preview_size}.png")
        prev.write_bytes(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=args.preview_size)))
        print(f"[ok] {prev}  (conferir lado a lado com o raster original)")


if __name__ == "__main__":
    main()
