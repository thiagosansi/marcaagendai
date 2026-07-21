#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.4", "resvg-py"]
# ///
"""
compose.py — compositor de peças finais do harness.

Monta a arte final (canvas + fundo + camadas) a partir de um spec JSON, usando as
fontes da marca (assets/fontes/, papéis display/corpo/kicker). É o caminho para todo
texto importante: a IA gera fundo/ilustração, o compose aplica a tipografia.

Os defaults visuais da MARCA (cor de texto, fundo da pill, anatomia do balão, sombras,
presets de fundo) vêm de brand/tema-visual.json — criado na /imersao-na-marca. Sem o
tema, valem defaults neutros do harness.

Uso:
    uv run tools/compose.py spec.json --out saida.png [--pdf] [--canvas 1080x1350] [--strict]

Verificações automáticas (o PIL corta/sobrepõe em silêncio): tinta de texto (text/badge/
bubble) fora do canvas, palavra mais larga que o max_width, texto nas zonas de UI do
story (topo 250px / base 420px em canvas 9:16 — ou "safe_margins" declaradas no canvas),
texto sobre "subject_zones" de imagens, colisão de tinta entre linhas (fonte de marca com
métricas maiores que os defaults) e peso ignorado em fonte sem eixo wght. Cada violação
vira "[aviso] ..." no stderr + sidecar <saida>.warnings.json ao lado do PNG (sem avisos,
sidecar antigo é removido). --strict: qualquer aviso encerra com exit 3.

Spec (JSON):
{
  "canvas": {"preset": "feed-4x5"} | {"w": 1080, "h": 1350} | "1080x1920",
            (aceita "safe_margins": {"top": N, "bottom": N, "left": N, "right": N} —
             zonas onde texto dispara aviso; em story 9:16 vale o default 250/420)
  "background":
      {"color": "#F8FAFC"}
    | {"preset": "casa"}                                  ← preset nomeado do tema
    | {"gradient": {"from": "#DBEAFE", "to": "#EDE9FE", "direction": "vertical"}}
    | {"radial": {"inner": "#DBEAFE", "mid": "#FFFFFF", "outer": "#EDE9FE",
       "center": [0.5, 0.0], "radius": [1.25, 0.88], "mid_stop": 0.47}}
    | {"image": "caminho.png", "fit": "cover",
       "scrim": {"color": "#0F172A", "opacity": 0.45, "area": "bottom"}},
  "layers": [
    {"type": "rect",   "x": 80, "y": 900, "w": 920, "h": 300, "radius": 40,
     "color": "#FFFFFF", "opacity": 0.92, "shadow": true},         ← "shadow": true usa a
                                                                     sombra default do tema
    {"type": "text",   "spans": [                                  ← rich text POR PALAVRA
       {"text": "Destaque ", "weight": 700},                         (negrito de palavra-chave,
       {"text": "no meio da frase, "},                               frase colorida; aceita
       {"text": "com cor.", "color": "#7C3AED", "weight": 700}],     spans tb. em lines)
     "font": "corpo", "size": 38, "x": 120, "y": 940, "max_width": 840},
    {"type": "image",  "path": "assets/grafismos/selo.png",
     "x": "center", "y": 1240, "w": 244, "tint": "#7C3AED"},       ← tint recolore selo/glifo
    {"type": "circle", "cx": 1000, "cy": 120, "r": 60, "color": "#2563EB", "opacity": 0.15},
    {"type": "image",  "path": "assets/logos/logo.png", "x": "center",
     "y": 1220, "w": 220, "radius": 0, "opacity": 1.0,
     "subject_zones": [{"x": 300, "y": 400, "w": 360, "h": 320,
                        "label": "rosto do bebê"}]},                ← zonas (coords do CANVAS)
                                                                     que texto não pode cobrir —
                                                                     a direção de arte marca
                                                                     depois de ver a imagem
    {"type": "text",   "text": "Título da peça", "font": "display", "weight": 700,
     "size": 84, "color": {"from": "#1D4ED8", "to": "#7C3AED"},   ← gradiente em texto
     "x": 80, "y": 200, "max_width": 920, "align": "left",
     "line_height": 1.12, "letter_spacing": 0, "uppercase": false},
    {"type": "text",   "lines": [                                 ← headline multicolorida
       {"text": "Linha de cima", "color": "#1D4ED8"},                (cor/peso/size por linha;
       {"text": "Linha do meio", "color": "#7C3AED", "size": 64},     sizes MISTOS → vão ótico
       {"text": "Linha de baixo", "color": "#047857"}],               uniforme, "gap" px opcional)
     "font": "display", "weight": 700, "size": 88, "x": 80, "y": 300, "line_height": 1.1},
    {"type": "blob",   "cx": 990, "cy": 90, "r": 210, "color": "#EDE9FE", "opacity": 0.9,
     "seed": 7, "variance": 0.2, "stretch_x": 1.15},              ← forma orgânica de canto
    {"type": "dots",   "x": 880, "y": 260, "rows": 4, "cols": 5, "gap": 34, "r": 5,
     "color": "#2563EB", "opacity": 0.35},                        ← dot grid decorativo
    {"type": "badge",  "text": "Kicker da peça", "x": 80, "y": 170, "font": "corpo",
     "weight": 600, "size": 34, "color": "#FFFFFF",
     "icon": "send"},                                             ← pill; sem "bg" usa a cor do
                                                                     tema (+ ícone Lucide p/ CTA:
                                                                     send=enviar; "→" só avançar)
    {"type": "bubble", "x": 110, "y": 850, "w": 400, "h": 240,
     "color": "#FFFFFF"},                                         ← balão de fala; anatomia
                                                                     (raios, canto-quina, sombra)
                                                                     vem do tema — qualquer campo
                                                                     pode ser sobreposto no spec
    {"type": "icon",   "name": "star", "size": 56, "color": "#7C3AED", "cx": 160,
     "cy": 720, "circle_bg": "#EDE9FE", "circle_r": 56}           ← Lucide (assets/icones/lucide)
  ]
}

Fontes: papéis "display" / "corpo" / "kicker" (mapeados em assets/fontes/mapa-fontes.json);
os aliases históricos "baloo" / "dm" / "albert" continuam aceitos como sinônimos. No mapa,
cada papel aceita "Arquivo.ttf" direto OU {"file": "Arquivo.ttf", "line_height":
{"large": 1.1, "small": 1.3, "threshold": 56}} — calibração da entrelinha default para
fonte de marca com métricas diferentes das fontes da casa (line_height do spec segue
vencendo tudo; sem calibração valem os defaults 1.1/1.3).

Presets de canvas: feed-4x5, feed-1x1, story, capa-reels, thumb-yt, linkedin,
banner-16x9, certificado-a4, capa-a4, cracha, flyer-a5, cartaz-a3 (impressos já
incluem sangria 3mm @300dpi — ver brand/formatos.md).
"""

import argparse
import io
import json
import math
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fontes"
LUCIDE_DIR = ROOT / "assets" / "icones" / "lucide"

# (largura, altura, dpi) — impressos com sangria 3mm @300dpi
CANVAS_PRESETS = {
    "feed-4x5": (1080, 1350, None),
    "feed-1x1": (1080, 1080, None),
    "story": (1080, 1920, None),
    "capa-reels": (1080, 1920, None),
    "thumb-yt": (1280, 720, None),
    "linkedin": (1200, 1350, None),
    "banner-16x9": (1920, 1080, None),
    "certificado-a4": (3579, 2551, 300),
    "capa-a4": (2551, 3579, 300),
    "cracha": (1252, 1725, 300),
    "flyer-a5": (1819, 2551, 300),
    "cartaz-a3": (3579, 5031, 300),
}

# Fontes por PAPEL. Os defaults do harness (OFL, embutidas no repo) valem quando a marca
# não tem fonte própria; marca com fontes oficiais troca os arquivos em
# assets/fontes/mapa-fontes.json (a skill /imersao-na-marca pergunta e configura).
DEFAULT_FONT_FILES = {
    "display": "DMSans-VariableFont_opsz,wght.ttf",
    "corpo": "DMSans-VariableFont_opsz,wght.ttf",
    "kicker": "AlbertSans-VariableFont_wght.ttf",
}
# Aliases históricos usados nos specs — apontam para os papéis acima.
FONT_ROLES = {"baloo": "display", "dm": "corpo", "albert": "kicker"}


def _load_font_files():
    """mapa-fontes.json: papel → "Arquivo.ttf" OU {"file": "...", "line_height": {...}}."""
    files = dict(DEFAULT_FONT_FILES)
    heights = {}
    mapa = FONT_DIR / "mapa-fontes.json"
    if mapa.exists():
        data = json.loads(mapa.read_text(encoding="utf-8"))
        for k, v in data.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                if v.get("file"):
                    files[k] = v["file"]
                if v.get("line_height"):
                    heights[k] = v["line_height"]
            else:
                files[k] = v
    return files, heights


FONT_FILES, FONT_LINE_HEIGHTS = _load_font_files()


def default_line_height(family, size):
    """Entrelinha default por papel: calibrável via "line_height" no mapa-fontes
    (fonte de marca com métricas maiores); ausente = constantes da casa 1.1/1.3."""
    cfg = FONT_LINE_HEIGHTS.get(family) or FONT_LINE_HEIGHTS.get(FONT_ROLES.get(family, family))
    if cfg:
        large = size >= int(cfg.get("threshold", 56))
        return float(cfg.get("large", 1.1)) if large else float(cfg.get("small", 1.3))
    return 1.1 if size >= 56 else 1.3

# Defaults visuais NEUTROS do harness — a identidade da marca NÃO vive no código.
# brand/tema-visual.json (criado na /imersao-na-marca) sobrepõe estes valores.
NEUTRAL_THEME = {
    "text": {"color": "#111827"},
    "icon": {"color": "#111827"},
    "badge": {"bg": "#2563EB"},
    "bubble": {"radius": 24, "tail_radius": 24, "tail_corner": "br",
               "shadow": {"dx": 0, "dy": 6, "opacity": 0.15, "color": "#000000", "blur": 12}},
    "rect": {"shadow": {"dx": 0, "dy": 6, "opacity": 0.15, "color": "#000000", "blur": 12}},
    "background_presets": {},
}

_theme_cache = None


def _merge_theme(base, extra):
    """Merge por chave (dicts em profundidade); chaves _* do tema são doc, ignoradas."""
    out = dict(base)
    for k, v in extra.items():
        if k.startswith("_"):
            continue
        out[k] = _merge_theme(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_theme():
    """Tema visual da marca (brand/tema-visual.json) sobre os defaults neutros."""
    global _theme_cache
    if _theme_cache is None:
        theme = NEUTRAL_THEME
        path = ROOT / "brand" / "tema-visual.json"
        if path.exists():
            theme = _merge_theme(theme, json.loads(path.read_text(encoding="utf-8")))
        _theme_cache = theme
    return _theme_cache


# ── Avisos de composição ────────────────────────────────────────────────────
# O PIL corta e sobrepõe em silêncio — estas verificações tornam violações visíveis.
WARNINGS = []
_CTX = {"size": None, "safe": None, "zones": []}
_static_weight_warned = set()


def warn(tipo, layer_ref, detalhe):
    WARNINGS.append({"tipo": tipo, "layer": layer_ref, "detalhe": detalhe})
    print(f"[aviso] {layer_ref}: {detalhe}", file=sys.stderr)


def _layer_ref(layer):
    """Identificação curta da camada para os avisos: tipo, trecho do texto e posição."""
    txt = layer.get("text")
    if txt is None and "spans" in layer:
        txt = "".join(s.get("text", "") for s in layer["spans"])
    label = ""
    if txt:
        txt = " ".join(txt.split())
        label = f' "{txt[:28]}…"' if len(txt) > 28 else f' "{txt}"'
    return f"{layer.get('type', 'text')}{label} @({layer.get('x', '?')},{layer.get('y', '?')})"


def _check_text_ink(ink, layer_ref, kind="texto"):
    """Checa a tinta de uma camada com texto: canvas, safe margins e subject_zones."""
    if ink is None or not _CTX["size"]:
        return
    W, H = _CTX["size"]
    l, t, r, b = ink
    fora = []
    if l < 0:
        fora.append(f"esquerda ({round(l)}px < 0)")
    if t < 0:
        fora.append(f"topo ({round(t)}px < 0)")
    if r > W:
        fora.append(f"direita ({round(r)}px > {W})")
    if b > H:
        fora.append(f"base ({round(b)}px > {H})")
    if fora:
        warn("texto-fora-do-canvas", layer_ref, f"{kind} fora do canvas: {', '.join(fora)}")
    safe = _CTX["safe"]
    if safe:
        if safe.get("top") and t < safe["top"]:
            warn("safe-margin", layer_ref,
                 f"{kind} na zona de UI do topo (tinta em y={round(t)}, zona até {safe['top']}px)")
        if safe.get("bottom") and b > H - safe["bottom"]:
            warn("safe-margin", layer_ref,
                 f"{kind} na zona de UI da base (tinta até y={round(b)}, zona a partir de {H - safe['bottom']}px)")
        if safe.get("left") and l < safe["left"]:
            warn("safe-margin", layer_ref,
                 f"{kind} na margem segura esquerda (tinta em x={round(l)} < {safe['left']}px)")
        if safe.get("right") and r > W - safe["right"]:
            warn("safe-margin", layer_ref,
                 f"{kind} na margem segura direita (tinta até x={round(r)} > {W - safe['right']}px)")
    for z in _CTX["zones"]:
        if l < z["x"] + z["w"] and r > z["x"] and t < z["y"] + z["h"] and b > z["y"]:
            warn("texto-sobre-zona", layer_ref,
                 f"{kind} sobre {z.get('label', 'zona marcada')} "
                 f"(zona x={z['x']} y={z['y']} {z['w']}x{z['h']})")


def _line_ink(draw, lx, yy, line, font, ls_px=0.0):
    """Bbox absoluto da tinta de uma linha desenhada em (lx, yy); None se sem tinta."""
    bb = draw.textbbox((0, 0), line, font=font)
    if bb[2] <= bb[0]:
        return None
    return (lx + bb[0], yy + bb[1], lx + bb[2] + ls_px * max(0, len(line) - 1), yy + bb[3])


def _finish_text_checks(layer, inks):
    """Fecha um bloco de texto: colisão de tinta entre linhas consecutivas (tolerância
    2px — pega fonte de marca com ascender/descender maiores que a entrelinha default,
    sem confiar nas tabelas de métrica do TTF) + checks de posição no bloco inteiro."""
    vis = [i for i in inks if i]
    if not vis:
        return
    ref = _layer_ref(layer)
    worst = 0
    for a, b in zip(inks, inks[1:]):
        if a and b:
            worst = max(worst, a[3] - b[1])
    if worst > 2:
        fam = layer.get("font", "corpo")
        role = FONT_ROLES.get(fam, fam)
        hint = ("aumentar o line_height do spec" if "line_height" in layer else
                f"calibrar o line_height do papel '{role}' em assets/fontes/mapa-fontes.json")
        warn("colisao-de-tinta", ref,
             f"tinta de linhas consecutivas se sobrepõe ({round(worst)}px) — {hint}")
    union = (min(i[0] for i in vis), min(i[1] for i in vis),
             max(i[2] for i in vis), max(i[3] for i in vis))
    _check_text_ink(union, ref)


def parse_color(value, default_alpha=255):
    """'#RGB' | '#RRGGBB' | '#RRGGBBAA' -> (r, g, b, a)"""
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    a = int(s[6:8], 16) if len(s) >= 8 else default_alpha
    return (r, g, b, a)


def load_font(family, weight, size):
    """Carrega fonte da marca com peso via variable font (fallback: estática)."""
    role = FONT_ROLES.get(family, family)  # baloo/dm/albert → display/corpo/kicker
    name = FONT_FILES.get(family) or FONT_FILES.get(role) or family  # aceita caminho direto
    path = FONT_DIR / name if not Path(name).is_absolute() else Path(name)
    if not path.exists():
        candidates = list(FONT_DIR.glob(f"{family}*.ttf")) + list(FONT_DIR.glob(f"{family.title()}*.ttf"))
        if candidates:
            path = candidates[0]
        else:
            sys.exit(f"[erro] fonte '{family}' não encontrada em {FONT_DIR}")
    font = ImageFont.truetype(str(path), size=size)
    has_wght = False
    try:
        axes = font.get_variation_axes()
        values = []
        for ax in axes:
            axis_name = ax.get("name", b"")
            if isinstance(axis_name, bytes):
                axis_name = axis_name.decode("latin-1", "ignore")
            axis_name = axis_name.lower()
            lo, hi = ax["minimum"], ax["maximum"]
            if "weight" in axis_name or "wght" in axis_name:
                has_wght = True
                values.append(max(lo, min(hi, weight)))
            elif "optical" in axis_name or "opsz" in axis_name:
                values.append(max(lo, min(hi, size)))
            else:
                values.append(ax["default"])
        if values:
            font.set_variation_by_axes(values)
    except OSError:
        pass  # fonte estática — peso vem do arquivo
    if not has_wght:
        _warn_static_weight(family, int(weight), path, font)
    return font


def _warn_static_weight(family, weight, path, font):
    """Sem eixo wght, o PIL ignora o peso pedido em silêncio — avisar quando o peso
    do arquivo (deduzido do nome do estilo) não é o pedido. 1 aviso por combinação."""
    try:
        style = font.getname()[1] or ""
    except Exception:
        style = ""
    s = style.lower().replace(" ", "")
    implied = 400
    for token, w in (("extrablack", 950), ("black", 900), ("heavy", 900),
                     ("extrabold", 800), ("ultrabold", 800), ("semibold", 600),
                     ("demibold", 600), ("bold", 700), ("medium", 500),
                     ("extralight", 200), ("ultralight", 200), ("light", 300),
                     ("thin", 100)):
        if token in s:
            implied = w
            break
    key = (family, weight, path.name)
    if weight != implied and key not in _static_weight_warned:
        _static_weight_warned.add(key)
        warn("peso-estatico-ignorado", f"fonte '{family}'",
             f"peso {weight} pedido, mas {path.name} não tem eixo de peso "
             f"(estilo '{style or '?'}' ≈ {implied}) — o peso do arquivo prevalece")


def linear_gradient(size, c1, c2, direction="vertical"):
    """Gradiente linear RGBA."""
    w, h = size
    grad = Image.linear_gradient("L")  # 256x256, vertical 0->255
    if direction == "horizontal":
        grad = grad.rotate(90, expand=True)
    grad = grad.resize((w, h))
    a = Image.new("RGBA", (w, h), parse_color(c1))
    b = Image.new("RGBA", (w, h), parse_color(c2))
    return Image.composite(b, a, grad)


def radial_background(size, spec):
    """Gradiente radial elíptico de 3 paradas (inner → mid → outer).
    Foco e raios são frações do canvas: center [0.5, 0.0] + radius [1.25, 0.88]
    equivalem ao CSS radial-gradient(125% 88% at 50% 0%). mid_stop = posição da
    parada do meio (0..1)."""
    w, h = size
    small_w, small_h = 240, 240
    inner = parse_color(spec["inner"])[:3]
    mid = parse_color(spec["mid"])[:3]
    outer = parse_color(spec["outer"])[:3]
    center = spec.get("center", [0.5, 0.0])
    radius = spec.get("radius", [1.25, 0.88])
    stop = float(spec.get("mid_stop", 0.47))
    cx, cy = small_w * float(center[0]), small_h * float(center[1])
    rx, ry = small_w * float(radius[0]), small_h * float(radius[1])
    img = Image.new("RGB", (small_w, small_h))
    px = img.load()
    for y in range(small_h):
        for x in range(small_w):
            d = min(1.0, (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) ** 0.5)
            if d < stop:
                t = d / stop
                c = tuple(round(inner[i] + (mid[i] - inner[i]) * t) for i in range(3))
            else:
                t = (d - stop) / (1 - stop)
                c = tuple(round(mid[i] + (outer[i] - mid[i]) * t) for i in range(3))
            px[x, y] = c
    return img.resize((w, h), Image.LANCZOS).convert("RGBA")


def fit_cover(img, target_w, target_h):
    """Redimensiona cobrindo o alvo e corta o excesso pelo centro."""
    scale = max(target_w / img.width, target_h / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - target_w) // 2, (nh - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def apply_scrim(base, scrim):
    """Escurece área da imagem para legibilidade de texto."""
    w, h = base.size
    color = parse_color(scrim.get("color", "#000000"))[:3]
    opacity = float(scrim.get("opacity", 0.4))
    area = scrim.get("area", "bottom")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if area == "full":
        overlay = Image.new("RGBA", (w, h), color + (round(255 * opacity),))
    else:
        mask = Image.linear_gradient("L").resize((w, h))  # 0 topo -> 255 base
        if area == "top":
            mask = mask.rotate(180)
        mask = mask.point(lambda v: round(v * opacity))
        overlay = Image.new("RGBA", (w, h), color + (255,))
        overlay.putalpha(mask)
    return Image.alpha_composite(base, overlay)


def build_background(size, bg, _from_preset=False):
    if bg is None:
        return Image.new("RGBA", size, (255, 255, 255, 255))
    if "preset" in bg:
        if _from_preset:
            sys.exit("[erro] preset de fundo não pode referenciar outro preset (tema-visual.json)")
        presets = load_theme().get("background_presets", {})
        spec = presets.get(bg["preset"])
        if spec is None:
            sys.exit(f"[erro] preset de fundo desconhecido: {bg['preset']} — defina em "
                     f"brand/tema-visual.json (background_presets: {', '.join(sorted(presets)) or 'nenhum'})")
        return build_background(size, spec, _from_preset=True)
    if "radial" in bg:
        return radial_background(size, bg["radial"])
    if "color" in bg:
        return Image.new("RGBA", size, parse_color(bg["color"]))
    if "gradient" in bg:
        g = bg["gradient"]
        return linear_gradient(size, g["from"], g["to"], g.get("direction", "vertical"))
    if "image" in bg:
        path = ROOT / bg["image"] if not Path(bg["image"]).is_absolute() else Path(bg["image"])
        img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
        img = fit_cover(img, *size) if bg.get("fit", "cover") == "cover" else img.resize(size, Image.LANCZOS)
        if "scrim" in bg:
            img = apply_scrim(img, bg["scrim"])
        return img
    sys.exit(f"[erro] fundo inválido: {bg}")


def wrap_text(draw, text, font, max_width, letter_spacing_px, ref=None):
    """Quebra por palavras respeitando max_width (respeita \\n manuais)."""
    def line_width(line):
        base = draw.textlength(line, font=font)
        return base + letter_spacing_px * max(0, len(line) - 1)

    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        if ref is not None:
            for word in words:
                ww = line_width(word)
                if ww > max_width:
                    warn("palavra-maior-que-max-width", ref,
                         f'palavra "{word}" mais larga que o max_width '
                         f"({round(ww)}px > {round(max_width)}px) — vai vazar da caixa")
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if line_width(trial) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_line(target, xy, line, font, fill, letter_spacing_px):
    """Desenha uma linha (com tracking opcional) em um Draw."""
    if letter_spacing_px <= 0:
        target.text(xy, line, font=font, fill=fill)
        return
    x, y = xy
    for ch in line:
        target.text((x, y), ch, font=font, fill=fill)
        x += target.textlength(ch, font=font) + letter_spacing_px


def _span_style(span, layer):
    """Resolve fonte/peso/cor de um span com fallback no bloco (cor default: tema)."""
    return (
        span.get("font", layer.get("font", "corpo")),
        int(span.get("weight", layer.get("weight", 400))),
        span.get("color", layer.get("color", load_theme()["text"]["color"])),
    )


def _spans_words(spans):
    """Converte spans em palavras; cada palavra = lista de (fragmento, span).
    Spans emendados sem espaço continuam a MESMA palavra (ex.: "**Con**fiança");
    "\\n" dentro de um span vira quebra forçada (sentinela None na lista)."""
    words, current = [], []
    for span in spans:
        for pi, paragraph in enumerate(span["text"].split("\n")):
            if pi > 0:
                if current:
                    words.append(current)
                    current = []
                words.append(None)  # quebra de linha forçada
            pieces = paragraph.split(" ")
            for i, piece in enumerate(pieces):
                if i > 0 and current:
                    words.append(current)
                    current = []
                if piece:
                    current.append((piece, span))
    if current:
        words.append(current)
    return words


def _draw_spans_row(base, x, y, words, size, layer, measure_only=False, ink=None):
    """Desenha (ou só mede) UMA linha de palavras estilizadas; retorna a largura.
    Baselines: quando os spans da linha misturam fontes com ascent efetivo diferente
    (>1px, medido na tinta do "H" — as tabelas de métrica do TTF mentem), cada span é
    alinhado pela baseline; bold/regular da mesma família varia <=1px e nada muda."""
    draw = ImageDraw.Draw(base)
    dys = {}
    if not measure_only:
        bases = {}
        for word in words:
            for _, span in word:
                fam, wt, _ = _span_style(span, layer)
                if (fam, wt) not in bases:
                    bases[(fam, wt)] = draw.textbbox((0, 0), "H", font=load_font(fam, wt, size))[3]
        if bases and max(bases.values()) - min(bases.values()) > 1:
            ref_base = max(bases.values())
            dys = {k: ref_base - v for k, v in bases.items()}
    space_w = None
    cx = x
    for wi, word in enumerate(words):
        if wi > 0:
            if space_w is None:
                fam, wt, _ = _span_style(word[0][1], layer)
                space_w = draw.textlength(" ", font=load_font(fam, wt, size))
            cx += space_w
        for frag, span in word:
            fam, wt, color = _span_style(span, layer)
            font = load_font(fam, wt, size)
            if not measure_only:
                fy = y + dys.get((fam, wt), 0)
                draw.text((round(cx), fy), frag, font=font, fill=parse_color(color))
                if ink is not None:
                    bb = draw.textbbox((round(cx), fy), frag, font=font)
                    if bb[2] > bb[0]:
                        ink.append(bb)
            cx += draw.textlength(frag, font=font)
    return cx - x


def render_text_spans(base, layer):
    """Parágrafo/linha rich text: layer["spans"] = [{"text", "weight"?, "color"?, "font"?}].
    Peso e cor variam POR PALAVRA/trecho (negrito de palavras-chave, frase colorida —
    padrão das referências aprovadas); quebra por palavras em max_width."""
    W, _ = base.size
    size = int(layer["size"])
    margin = 80
    x = layer.get("x", margin)
    centered = x == "center"
    max_width = int(layer.get("max_width", (W - 2 * margin) if centered else (W - int(x) - margin)))
    x0 = (W - max_width) // 2 if centered else int(x)
    align = layer.get("align", "center" if centered else "left")
    line_height = float(layer.get("line_height",
                                  default_line_height(layer.get("font", "corpo"), size)))
    step = round(size * line_height)

    draw = ImageDraw.Draw(base)
    words = _spans_words(layer["spans"])
    lines, current, cur_w = [], [], 0
    for word in words:
        if word is None:  # quebra forçada
            lines.append(current)
            current, cur_w = [], 0
            continue
        w_width = _draw_spans_row(base, 0, -10_000, [word], size, layer, measure_only=True)
        if w_width > max_width:
            warn("palavra-maior-que-max-width", _layer_ref(layer),
                 f'palavra "{"".join(f for f, _ in word)}" mais larga que o max_width '
                 f"({round(w_width)}px > {max_width}px) — vai vazar da caixa")
        if not current:
            current, cur_w = [word], w_width
            continue
        fam, wt, _ = _span_style(word[0][1], layer)
        sp = draw.textlength(" ", font=load_font(fam, wt, size))
        if cur_w + sp + w_width > max_width:
            lines.append(current)
            current, cur_w = [word], w_width
        else:
            current.append(word)
            cur_w += sp + w_width
    if current:
        lines.append(current)

    yy = int(layer["y"])
    line_inks = []
    for line in lines:
        lw = _draw_spans_row(base, 0, -10_000, line, size, layer, measure_only=True)
        lx = {"left": x0, "center": x0 + (max_width - lw) / 2,
              "right": x0 + max_width - lw}[align]
        frag_inks = []
        _draw_spans_row(base, round(lx), yy, line, size, layer, ink=frag_inks)
        line_inks.append((min(b[0] for b in frag_inks), min(b[1] for b in frag_inks),
                          max(b[2] for b in frag_inks), max(b[3] for b in frag_inks))
                         if frag_inks else None)
        yy += step
    _finish_text_checks(layer, line_inks)
    return step * len(lines)


def render_text_layer(base, layer):
    if "lines" in layer:
        return render_text_lines(base, layer)
    if "spans" in layer:
        return render_text_spans(base, layer)
    W, H = base.size
    text = layer["text"]
    if layer.get("uppercase"):
        text = text.upper()
    size = int(layer["size"])
    font = load_font(layer.get("font", "corpo"), int(layer.get("weight", 400)), size)
    letter_spacing_px = float(layer.get("letter_spacing", 0)) * size
    margin = 80
    x = layer.get("x", margin)
    centered = x == "center"
    max_width = int(layer.get("max_width", (W - 2 * margin) if centered else (W - int(x) - margin)))
    x0 = (W - max_width) // 2 if centered else int(x)
    y = int(layer["y"])
    align = layer.get("align", "center" if centered else "left")
    # Display (≥56px) sem line_height explícito → ritmo TIGHT 1.1 (regra do fundador:
    # título espaçado = reprova; 1.1 ≈ o vão ótico 0.16×size dos lockups em `lines`).
    # Corpo (<56px) mantém 1.3 para leitura confortável. Fonte de marca com métricas
    # maiores calibra estes defaults via "line_height" no mapa-fontes (por papel).
    line_height = float(layer.get("line_height",
                                  default_line_height(layer.get("font", "corpo"), size)))

    draw = ImageDraw.Draw(base)
    lines = wrap_text(draw, text, font, max_width, letter_spacing_px, _layer_ref(layer))
    step = round(size * line_height)

    color = layer.get("color", load_theme()["text"]["color"])
    gradient = isinstance(color, dict)

    line_inks = []
    if gradient:
        block_h = step * len(lines) + round(size * 0.4)
        mask = Image.new("L", (max_width + 8, block_h), 0)
        mdraw = ImageDraw.Draw(mask)
        yy = 0
        for line in lines:
            lw = mdraw.textlength(line, font=font) + letter_spacing_px * max(0, len(line) - 1)
            lx = {"left": 0, "center": (max_width - lw) / 2, "right": max_width - lw}[align]
            draw_line(mdraw, (round(lx), yy), line, font, 255, letter_spacing_px)
            line_inks.append(_line_ink(draw, x0 + round(lx), y + yy, line, font, letter_spacing_px))
            yy += step
        grad_img = linear_gradient(mask.size, color["from"], color["to"],
                                   color.get("direction", "horizontal"))
        base.paste(grad_img, (x0, y), mask)
    else:
        fill = parse_color(color)
        yy = y
        for line in lines:
            lw = draw.textlength(line, font=font) + letter_spacing_px * max(0, len(line) - 1)
            lx = {"left": x0, "center": x0 + (max_width - lw) / 2, "right": x0 + max_width - lw}[align]
            draw_line(draw, (round(lx), yy), line, font, fill, letter_spacing_px)
            line_inks.append(_line_ink(draw, round(lx), yy, line, font, letter_spacing_px))
            yy += step
    _finish_text_checks(layer, line_inks)
    return step * len(lines)


def render_text_lines(base, layer):
    """Headline multicolorida / lockup: layer["lines"] = [{"text", "color"?, "weight"?, "size"?}, ...].
    Cor, peso e TAMANHO podem variar por linha (ritmo tipográfico); resto vem do bloco.

    LOCKUP DISPLAY (menor size ≥ 56, ou tamanhos MISTOS, ou "gap" explícito): o vão
    entre as linhas é medido no DESENHO REAL (ink box) e mantido UNIFORME e TIGHT —
    avançar por size×line_height produz vãos desiguais (mistos) ou largos demais
    (mesmo tamanho com line_height 1.3 — reprovado 2× pelo fundador). Default:
    0.16 × menor size (≈ ritmo line_height 1.1; 0.40 ficou "separado demais").
    Ajuste fino opcional: "gap" em px; lockup de 3+ linhas com conectivo pequeno pode
    pedir ~0.3 × menor size. Passar "line_height" explícito força o passo clássico
    (uso de corpo de texto multi-linha, ex.: itens de lista em DM Sans < 56)."""
    items = layer["lines"]
    if not items:
        return 0
    sizes = [int(item.get("size", layer.get("size", 0))) for item in items]
    display = min((s for s in sizes if s > 0), default=0) >= 56
    use_ink = ("gap" in layer) or (len(set(sizes)) > 1) or (display and "line_height" not in layer)
    if not use_ink:
        total = 0
        for item in items:
            sub = {k: v for k, v in layer.items() if k not in ("lines", "gap")}
            body = {"spans": item["spans"]} if "spans" in item else {"text": item["text"]}
            sub.pop("text", None)
            sub.pop("spans", None)
            sub.update({**body, "y": int(layer["y"]) + total})
            for k in ("color", "weight", "size"):
                if k in item:
                    sub[k] = item[k]
            total += render_text_layer(base, sub)
        return total

    # Lockup display (mistos OU mesmo tamanho) → gap ótico constante entre ink boxes
    draw = ImageDraw.Draw(base)
    y0 = int(layer["y"])
    gap = layer.get("gap")
    gap = round(0.16 * min(s for s in sizes if s > 0)) if gap is None else int(gap)
    prev_bottom = None
    total = 0
    for item, size in zip(items, sizes):
        plain = ("".join(s["text"] for s in item["spans"]) if "spans" in item
                 else item["text"])
        text = plain.upper() if layer.get("uppercase") else plain
        font = load_font(layer.get("font", "corpo"),
                         int(item.get("weight", layer.get("weight", 400))), size)
        _, ink_top, _, ink_bottom = draw.textbbox((0, 0), text, font=font)
        origin = y0 if prev_bottom is None else prev_bottom + gap - ink_top
        sub = {k: v for k, v in layer.items() if k not in ("lines", "gap")}
        body = {"spans": item["spans"]} if "spans" in item else {"text": item["text"]}
        sub.pop("text", None)
        sub.pop("spans", None)
        sub.update({**body, "y": origin, "size": size})
        for k in ("color", "weight"):
            if k in item:
                sub[k] = item[k]
        render_text_layer(base, sub)
        prev_bottom = origin + ink_bottom
        total = prev_bottom - y0
    return total


def rasterize_lucide(name, size, color, stroke_width=None):
    """Ícone Lucide (assets/icones/lucide) recolorido e rasterizado em RGBA."""
    try:
        import resvg_py
    except ImportError:
        sys.exit("[erro] resvg-py indisponível — rodar via uv (o header declara a dependência)")
    path = LUCIDE_DIR / f"{name}.svg"
    if not path.exists():
        sys.exit(f"[erro] ícone '{name}' não existe — nomes em https://lucide.dev/icons; "
                 f"vendorizar com: uv run tools/fetch_icons.py")
    svg = path.read_text(encoding="utf-8").replace('stroke="currentColor"', f'stroke="{color}"')
    if stroke_width is not None:
        svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg)
    png = resvg_py.svg_to_bytes(svg_string=svg, width=int(size), height=int(size))
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def draw_blob(base, layer):
    """Forma orgânica suave — blob decorativo de canto. Determinístico por seed."""
    cx, cy, r = float(layer["cx"]), float(layer["cy"]), float(layer["r"])
    variance = float(layer.get("variance", 0.22))
    stretch_x = float(layer.get("stretch_x", 1.0))
    stretch_y = float(layer.get("stretch_y", 1.0))
    npts = int(layer.get("points", 8))
    rnd = random.Random(int(layer.get("seed", 7)))
    ctrl = []
    for i in range(npts):
        ang = 2 * math.pi * i / npts
        rr = r * (1 + rnd.uniform(-variance, variance))
        ctrl.append((rr * math.cos(ang) * stretch_x, rr * math.sin(ang) * stretch_y))
    pts = []
    for i in range(npts):  # Catmull-Rom fechada → contorno suave
        p0, p1, p2, p3 = ctrl[i - 1], ctrl[i], ctrl[(i + 1) % npts], ctrl[(i + 2) % npts]
        for j in range(16):
            t = j / 16
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            pts.append((x, y))
    ss = 3  # supersampling local para bordas lisas
    pad = r * (1 + variance) + 4
    bw, bh = int(2 * pad * stretch_x) + 8, int(2 * pad * stretch_y) + 8
    tile = Image.new("RGBA", (bw * ss, bh * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    color = parse_color(layer["color"])
    alpha = round(255 * float(layer.get("opacity", 1.0)) * (color[3] / 255))
    d.polygon([((bw / 2 + x) * ss, (bh / 2 + y) * ss) for x, y in pts], fill=color[:3] + (alpha,))
    tile = tile.resize((bw, bh), Image.LANCZOS)
    base.alpha_composite(tile, (round(cx - bw / 2), round(cy - bh / 2)))


def draw_dots(base, layer):
    """Dot grid decorativo (grade de pontinhos)."""
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    color = parse_color(layer.get("color", "#FFFFFF"))
    alpha = round(255 * float(layer.get("opacity", 1.0)) * (color[3] / 255))
    x0, y0 = int(layer["x"]), int(layer["y"])
    rows, cols = int(layer.get("rows", 4)), int(layer.get("cols", 5))
    gap, r = int(layer.get("gap", 34)), int(layer.get("r", 5))
    for i in range(rows):
        for j in range(cols):
            cx, cy = x0 + j * gap, y0 + i * gap
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color[:3] + (alpha,))
    base.alpha_composite(overlay)


def draw_badge(base, layer):
    """Pill de rótulo curto (kicker, contador, CTA). Sem "bg" no spec, usa a cor do
    tema. Aceita ícone Lucide embutido: "icon": "send" (+ "icon_side": "right"|"left",
    "icon_size", "icon_gap") — cor do ícone segue a cor do texto. Uso canônico: CTA de
    compartilhar = ícone `send`; a seta "→" fica reservada para "arraste/avançar"."""
    W, _ = base.size
    text = layer["text"].upper() if layer.get("uppercase") else layer["text"]
    size = int(layer.get("size", 32))
    font = load_font(layer.get("font", "corpo"), int(layer.get("weight", 600)), size)
    ls_px = float(layer.get("letter_spacing", 0)) * size
    probe = ImageDraw.Draw(base)
    tw = probe.textlength(text, font=font) + ls_px * max(0, len(text) - 1)
    ascent, descent = font.getmetrics()
    th = ascent + descent
    icon_img, icon_gap = None, 0
    if layer.get("icon"):
        icon_size = int(layer.get("icon_size", round(size * 1.05)))
        icon_gap = int(layer.get("icon_gap", round(size * 0.42)))
        icon_img = rasterize_lucide(layer["icon"], icon_size,
                                    layer.get("color", "#FFFFFF"),
                                    layer.get("icon_stroke_width"))
    pad_x = int(layer.get("padding_x", round(size * 0.95)))
    pad_y = int(layer.get("padding_y", round(size * 0.5)))
    content_w = tw + ((icon_img.width + icon_gap) if icon_img else 0)
    w, h = int(content_w + 2 * pad_x), int(th + 2 * pad_y)
    x = layer.get("x", 80)
    x = (W - w) // 2 if x == "center" else int(x)
    y = int(layer["y"])
    bg = parse_color(layer.get("bg", load_theme()["badge"]["bg"]))
    alpha = round(255 * float(layer.get("bg_opacity", 1.0)) * (bg[3] / 255))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        [x, y, x + w, y + h], radius=int(layer.get("radius", h // 2)), fill=bg[:3] + (alpha,))
    base.alpha_composite(overlay)
    text_x = x + pad_x
    if icon_img and layer.get("icon_side", "right") == "left":
        text_x += icon_img.width + icon_gap
    draw_line(ImageDraw.Draw(base), (text_x, y + pad_y), text, font,
              parse_color(layer.get("color", "#FFFFFF")), ls_px)
    if icon_img:
        if layer.get("icon_side", "right") == "left":
            icon_x = x + pad_x
        else:
            icon_x = round(text_x + tw + icon_gap)
        base.alpha_composite(icon_img, (icon_x, y + (h - icon_img.height) // 2))
    _check_text_ink((x, y, x + w, y + h), _layer_ref(layer), "badge")


def draw_bubble(base, layer):
    """Balão de fala: retângulo arredondado onde o canto do FALANTE pode ter raio
    menor — uma quina suave, ainda arredondada, que faz o papel da ponta do balão
    (nada de rabinho triangular). A sombra é a MESMA forma deslocada. A anatomia
    default (raios, canto-quina, sombra) vem do tema (brand/tema-visual.json);
    qualquer campo pode ser sobreposto no spec. Texto vai em camada `text` por cima.
    Spec: {"type":"bubble","x","y","w","h",
           "radius":32,                           ← raio dos cantos normais
           "tail_corner":"br"|"bl"|"tr"|"tl",   ← canto-quina, aponta para o falante
           "tail_radius":10,                      ← raio da quina (menor que radius)
           "color":"#FFFFFF",
           "shadow": true | {"dx","dy","opacity","color","blur"}}"""
    W, _ = base.size
    th = load_theme()["bubble"]
    w, h = int(layer["w"]), int(layer["h"])
    x = layer.get("x", 80)
    x = (W - w) // 2 if x == "center" else int(x)
    y = int(layer["y"])
    R = int(layer.get("radius", th["radius"]))
    r = int(layer.get("tail_radius", th["tail_radius"]))
    corner = str(layer.get("tail_corner", th["tail_corner"])).lower()
    corner = {"r": "br", "l": "bl"}.get(corner, corner)  # compat com specs antigos

    ss = 3  # supersampling para curvas lisas
    big = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1],
                                          radius=R * ss, fill=255)
    small = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(small).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1],
                                            radius=r * ss, fill=255)
    q = R * ss  # quadrante do canto-quina vem da versão de raio menor
    boxes = {"tl": (0, 0, q, q), "tr": (w * ss - q, 0, w * ss, q),
             "bl": (0, h * ss - q, q, h * ss), "br": (w * ss - q, h * ss - q, w * ss, h * ss)}
    box = boxes.get(corner, boxes["br"])
    big.paste(small.crop(box), box[:2])
    mask = big.resize((w, h), Image.LANCZOS)

    if layer.get("shadow", True):
        sh = layer.get("shadow") if isinstance(layer.get("shadow"), dict) else {}
        th_sh = th["shadow"]
        dx, dy = int(sh.get("dx", th_sh["dx"])), int(sh.get("dy", th_sh["dy"]))
        s_op = float(sh.get("opacity", th_sh["opacity"]))
        s_col = parse_color(sh.get("color", th_sh["color"]))[:3]
        blur = int(sh.get("blur", th_sh["blur"]))
        s_mask = mask.filter(ImageFilter.GaussianBlur(blur)) if blur else mask
        s_mask = s_mask.point(lambda v: round(v * s_op))
        shadow_img = Image.new("RGBA", mask.size, s_col + (255,))
        shadow_img.putalpha(s_mask)
        base.alpha_composite(shadow_img, (x + dx, y + dy))

    color = parse_color(layer.get("color", "#FFFFFF"))
    alpha_mask = mask.point(lambda v: round(v * (color[3] / 255) *
                                            float(layer.get("opacity", 1.0))))
    bubble = Image.new("RGBA", mask.size, color[:3] + (255,))
    bubble.putalpha(alpha_mask)
    base.alpha_composite(bubble, (x, y))
    _check_text_ink((x, y, x + w, y + h), _layer_ref(layer), "balão")


def draw_icon(base, layer):
    """Ícone Lucide, opcionalmente sobre círculo pastel (padrão das referências).
    Posição: cx/cy (centro) ou x/y (canto sup-esq do ícone; x aceita "center")."""
    W, _ = base.size
    size = int(layer.get("size", 56))
    icon = rasterize_lucide(layer["name"], size, layer.get("color", load_theme()["icon"]["color"]),
                            layer.get("stroke_width"))
    opacity = float(layer.get("opacity", 1.0))
    if opacity < 1.0:
        a = icon.getchannel("A").point(lambda v: round(v * opacity))
        icon.putalpha(a)
    if "cx" in layer:
        cx, cy = int(layer["cx"]), int(layer["cy"])
    else:
        x = layer.get("x", 80)
        x = (W - size) // 2 if x == "center" else int(x)
        cx, cy = x + size // 2, int(layer["y"]) + size // 2
    if layer.get("circle_bg"):
        r = int(layer.get("circle_r", round(size * 0.95)))
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        bg = parse_color(layer["circle_bg"])
        alpha = round(255 * float(layer.get("circle_opacity", 1.0)) * (bg[3] / 255))
        ImageDraw.Draw(overlay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg[:3] + (alpha,))
        base.alpha_composite(overlay)
    base.alpha_composite(icon, (cx - icon.width // 2, cy - icon.height // 2))


def render_layer(base, layer):
    W, H = base.size
    ltype = layer["type"]

    if ltype == "text":
        render_text_layer(base, layer)
        return

    if ltype == "rect":
        color = parse_color(layer["color"])
        alpha = round(255 * float(layer.get("opacity", 1.0)) * (color[3] / 255))
        x = layer.get("x", 0)
        x = (W - int(layer["w"])) // 2 if x == "center" else int(x)
        y, w, h = int(layer["y"]), int(layer["w"]), int(layer["h"])
        radius = int(layer.get("radius", 0))
        if layer.get("shadow"):
            # sombra default vem do tema (brand/tema-visual.json); o spec sobrepõe campos
            sh = layer.get("shadow") if isinstance(layer.get("shadow"), dict) else {}
            th_sh = load_theme()["rect"]["shadow"]
            blur = int(sh.get("blur", th_sh["blur"]))
            dx, dy = int(sh.get("dx", th_sh["dx"])), int(sh.get("dy", th_sh["dy"]))
            s_op = float(sh.get("opacity", th_sh["opacity"]))
            s_col = parse_color(sh.get("color", th_sh["color"]))[:3]
            pad = blur * 2 + max(abs(dx), abs(dy))
            mask = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                [pad, pad, pad + w, pad + h], radius=radius, fill=255)
            shadow_mask = mask.filter(ImageFilter.GaussianBlur(blur)).point(
                lambda v: round(v * s_op))
            shadow_img = Image.new("RGBA", mask.size, s_col + (255,))
            shadow_img.putalpha(shadow_mask)
            base.alpha_composite(shadow_img, (x - pad + dx, y - pad + dy))
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rounded_rectangle(
            [x, y, x + w, y + h], radius=radius, fill=color[:3] + (alpha,))
        base.alpha_composite(overlay)
        return

    if ltype == "circle":
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        color = parse_color(layer["color"])
        alpha = round(255 * float(layer.get("opacity", 1.0)) * (color[3] / 255))
        cx, cy, r = int(layer["cx"]), int(layer["cy"]), int(layer["r"])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color[:3] + (alpha,))
        base.alpha_composite(overlay)
        return

    if ltype == "blob":
        draw_blob(base, layer)
        return

    if ltype == "dots":
        draw_dots(base, layer)
        return

    if ltype == "badge":
        draw_badge(base, layer)
        return

    if ltype == "bubble":
        draw_bubble(base, layer)
        return

    if ltype == "icon":
        draw_icon(base, layer)
        return

    if ltype == "image":
        path = ROOT / layer["path"] if not Path(layer["path"]).is_absolute() else Path(layer["path"])
        img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
        if layer.get("tint"):
            # recolorir glifo/selo monocromático (ex.: selos brancos de assets/grafismos)
            tint = parse_color(layer["tint"])[:3]
            tinted = Image.new("RGBA", img.size, tint + (0,))
            tinted.putalpha(img.getchannel("A"))
            img = tinted
        if "w" in layer and "h" in layer:
            img = fit_cover(img, int(layer["w"]), int(layer["h"]))
        elif "w" in layer:
            ratio = int(layer["w"]) / img.width
            img = img.resize((int(layer["w"]), round(img.height * ratio)), Image.LANCZOS)
        elif "h" in layer:
            ratio = int(layer["h"]) / img.height
            img = img.resize((round(img.width * ratio), int(layer["h"])), Image.LANCZOS)
        if layer.get("circle"):
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).ellipse([0, 0, img.width, img.height], fill=255)
            img.putalpha(mask)
        elif layer.get("radius"):
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width, img.height],
                                                   radius=int(layer["radius"]), fill=255)
            img.putalpha(mask)
        opacity = float(layer.get("opacity", 1.0))
        if opacity < 1.0:
            alpha = img.getchannel("A").point(lambda v: round(v * opacity))
            img.putalpha(alpha)
        x = layer.get("x", 0)
        x = (W - img.width) // 2 if x == "center" else int(x)
        base.alpha_composite(img, (x, int(layer["y"])))
        return

    sys.exit(f"[erro] camada de tipo desconhecido: {ltype}")


def resolve_canvas(spec_canvas, override):
    raw = override or spec_canvas
    if raw is None:
        sys.exit("[erro] spec sem 'canvas' e sem --canvas")
    if isinstance(raw, str):
        if raw in CANVAS_PRESETS:
            return CANVAS_PRESETS[raw]
        w, h = raw.lower().split("x")
        return (int(w), int(h), None)
    if "preset" in raw:
        if raw["preset"] not in CANVAS_PRESETS:
            sys.exit(f"[erro] preset desconhecido: {raw['preset']} (opções: {', '.join(CANVAS_PRESETS)})")
        return CANVAS_PRESETS[raw["preset"]]
    return (int(raw["w"]), int(raw["h"]), raw.get("dpi"))


def main():
    ap = argparse.ArgumentParser(description="Compõe peça final a partir de spec JSON.")
    ap.add_argument("spec", help="arquivo JSON do spec")
    ap.add_argument("--out", required=True, help="arquivo de saída (.png ou .jpg)")
    ap.add_argument("--pdf", action="store_true", help="salvar também PDF (impressos)")
    ap.add_argument("--canvas", help="override do canvas: preset ou WxH")
    ap.add_argument("--strict", action="store_true",
                    help="exit 3 se houver qualquer [aviso] de composição")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    w, h, dpi = resolve_canvas(spec.get("canvas"), args.canvas)

    # Contexto das verificações: canvas, safe margins e zonas proibidas (subject_zones)
    _CTX["size"] = (w, h)
    declared = spec.get("canvas", {}).get("safe_margins") if isinstance(spec.get("canvas"), dict) else None
    if declared:
        _CTX["safe"] = {s: int(declared.get(s, 0)) for s in ("top", "bottom", "left", "right")}
    elif abs(w / h - 9 / 16) < 0.01:
        # story 9:16 → zonas de UI do Instagram (universais): topo 250px, base 420px
        _CTX["safe"] = {"top": 250, "bottom": 420, "left": 0, "right": 0}
    _CTX["zones"] = [z for l in spec.get("layers", []) if l.get("type") == "image"
                     for z in l.get("subject_zones", [])]

    base = build_background((w, h), spec.get("background"))
    for layer in spec.get("layers", []):
        render_layer(base, layer)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        base.convert("RGB").save(out, quality=92)
    else:
        base.save(out)
    print(f"[ok] {out}  ({w}x{h})")

    warn_path = out.with_suffix(".warnings.json")
    if WARNINGS:
        warn_path.write_text(json.dumps(WARNINGS, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
        print(f"[aviso] {len(WARNINGS)} aviso(s) de composição — {warn_path.name}",
              file=sys.stderr)
    elif warn_path.exists():
        warn_path.unlink()

    if args.pdf:
        pdf_path = out.with_suffix(".pdf")
        base.convert("RGB").save(pdf_path, "PDF", resolution=dpi or 300)
        print(f"[ok] {pdf_path}  ({dpi or 300}dpi)")

    if args.strict and WARNINGS:
        sys.exit(3)


if __name__ == "__main__":
    main()
