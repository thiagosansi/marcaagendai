#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.4"]
# ///
"""warp_cover.py — compõe uma capa/arte REAL sobre a face de um livro/placa numa foto,
com warp de perspectiva. v2: detecção automática do quad + QA embutido.

Lição da v1 (reprova do fundador, story-04 upsell): cantos lidos "a olho" numa grade
saíram errados (capa-adesivo cobrindo 70% do livro) e a máscara de dedos por threshold
de pele serrilhou as bordas. Regras da v2:
  - O quad é DETECTADO (flood fill na face lisa do livro) ou dado manualmente; sempre
    conferir o --debug overlay antes de aceitar.
  - Dedos/oclusores voltam por cima via máscara por componentes (distância de cor ao
    creme do livro + morfologia + feather) — nunca threshold pixel-a-pixel cru.
  - NUNCA aprovar sem olhar o contact sheet de QA (--qa): bordas/cantos em zoom 2x.

Uso:
  uv run tools/warp_cover.py --base foto.png --cover capa.png --out saida.png \
      --auto-quad "x0,y0,x1,y1"          # ROI grosseiro em volta do livro (recomendado)
  ... ou --corners "x,y x,y x,y x,y"     # TL TR BR BL manuais (fallback)
  [--bleed 3] [--occ-threshold 70] [--no-protect] [--no-cover-crop] [--shadow]
  [--debug debug.png] [--qa qa-sheet.png]
"""
import argparse
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter


# ---------- geometria ----------

def solve8(A, b):
    """Resolve sistema 8x8 por eliminação de Gauss (sem numpy)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        pivval = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= pivval
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def find_coeffs(dst, src):
    """Coeficientes p/ Image.transform(PERSPECTIVE): mapeia dst<-src (4 pts TL,TR,BR,BL)."""
    A, b = [], []
    for (dx, dy), (sx, sy) in zip(dst, src):
        A.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy]); b.append(sx)
        A.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy]); b.append(sy)
    return solve8(A, b)


def dist2(a, b):
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return dr * dr + dg * dg + db * db


# ---------- detecção do quad ----------

def theil_sen(points):
    """Ajuste robusto v = a*k + b (mediana de slopes de pares) — aguenta as 'mordidas'
    dos dedos nas bordas. points: lista de (k, v)."""
    pts = sorted(points)
    n = len(pts)
    if n < 8:
        sys.exit("[erro] pontos insuficientes para ajustar a borda do livro")
    half = n // 2
    slopes = []
    for i in range(half):
        k1, v1 = pts[i]
        k2, v2 = pts[i + half]
        if k2 != k1:
            slopes.append((v2 - v1) / (k2 - k1))
    slopes.sort()
    a = slopes[len(slopes) // 2]
    inters = sorted(v - a * k for k, v in pts)
    b = inters[len(inters) // 2]
    return a, b


def detect_quad(rgb, roi, seed_tol=85.0, warmth_band=18.0, flat_tol=14.0):
    """Detecta a face do livro dentro do ROI. Estratégia estável p/ livro FRONTAL:
    1) máscara 'papel': pixel plano localmente (flat_tol), perto da cor-semente
       (seed_tol) e com a MESMA warmth (R−B ± banda — separa o papel creme de
       tecido branco, parede e pele);
    2) platôs: bordas L/R = run contíguo de colunas com contagem ≥ 55% do pico;
       topo/base idem por linhas (dedos só 'mordem' o run, não o derrubam);
    3) inclinação: refina topo/base/laterais com Theil–Sen DENTRO do retângulo,
       aceitando só tilt pequeno (livro frontal) — senão mantém o retângulo.
    Retorna (corners TL TR BR BL, cor base)."""
    x0, y0, x1, y1 = roi
    px = rgb.load()
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    samples = [px[xx, yy] for yy in range(cy - 15, cy + 16) for xx in range(cx - 15, cx + 16)]
    med = tuple(sorted(s[i] for s in samples)[len(samples) // 2] for i in range(3))
    wmed = med[0] - med[2]
    wlo, whi = wmed - warmth_band, wmed + warmth_band
    s2, f2 = seed_tol * seed_tol, flat_tol * flat_tol

    W, H = x1 - x0, y1 - y0
    mask = bytearray(W * H)
    colcnt = [0] * W
    rowcnt = [0] * H
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            w = c[0] - c[2]
            if not (wlo <= w <= whi) or dist2(c, med) > s2:
                continue
            cr = px[min(x + 2, x1 - 1), y]
            cd = px[x, min(y + 2, y1 - 1)]
            if dist2(c, cr) > f2 or dist2(c, cd) > f2:
                continue
            mask[(y - y0) * W + (x - x0)] = 1
            colcnt[x - x0] += 1
            rowcnt[y - y0] += 1

    def plateau(counts, frac=0.55):
        peak = max(counts)
        if peak < 30:
            sys.exit("[erro] face do livro não encontrada no ROI (máscara vazia)")
        thr = peak * frac
        best, cur = None, None
        for i, v in enumerate(counts):
            if v >= thr:
                cur = [i, i] if cur is None else [cur[0], i]
            else:
                if cur and (best is None or cur[1] - cur[0] > best[1] - best[0]):
                    best = cur
                cur = None
        if cur and (best is None or cur[1] - cur[0] > best[1] - best[0]):
            best = cur
        return best

    lx, rx = plateau(colcnt)
    ty, by = plateau(rowcnt, frac=0.30)  # mãos mordem até ~60% de uma linha do livro
    L, R = x0 + lx, x0 + rx
    T, B = y0 + ty, y0 + by
    if (R - L) < 60 or (B - T) < 60:
        sys.exit(f"[erro] face detectada pequena demais ({R-L}x{B-T}) — confira o ROI")

    # refinamento de tilt (bordas quase retas de livro frontal; rejeita ajuste maluco)
    inset = max(8, (R - L) // 12)

    def edge_line(scan_range, fixed_range, horizontal, edge0):
        pts = []
        for k in fixed_range:
            found = None
            for v in scan_range:
                xx, yy = (k, v) if horizontal else (v, k)
                if not (x0 <= xx < x1 and y0 <= yy < y1):
                    continue
                if mask[(yy - y0) * W + (xx - x0)]:
                    found = v
                    break
            # outlier = coluna/linha coberta por dedo (borda "encontrada" longe do platô)
            if found is not None and abs(found - edge0) <= 14:
                pts.append((k, found))
        if len(pts) < 20:
            return None
        a, b = theil_sen(pts)
        return (a, b) if abs(a) <= 0.08 else None

    xs = range(L + inset, R - inset)
    ys = range(T + inset, B - inset)
    top = edge_line(range(T - 6, T + 40), xs, True, T)
    bot = edge_line(range(B + 6, B - 40, -1), xs, True, B)
    left = edge_line(range(L - 6, L + 40), ys, False, L)
    right = edge_line(range(R + 6, R - 40, -1), ys, False, R)

    def yat(line, fallback, x):
        return line[0] * x + line[1] if line else fallback

    def xat(line, fallback, y):
        return line[0] * y + line[1] if line else fallback

    tl = (xat(left, L, T), yat(top, T, L))
    tr = (xat(right, R, T), yat(top, T, R))
    br = (xat(right, R, B), yat(bot, B, R))
    bl = (xat(left, L, B), yat(bot, B, L))

    # sanidade: cantos dentro do ROI com folga
    for (x, y) in (tl, tr, br, bl):
        if x <= x0 + 2 or x >= x1 - 2 or y <= y0 + 2 or y >= y1 - 2:
            sys.exit(f"[erro] canto ({x:.0f},{y:.0f}) encostou no ROI — confira o ROI")
    return [tl, tr, br, bl], med


def expand_quad(corners, bleed):
    """Empurra cada canto para FORA (a partir do centróide) — mata halo de 1-2px."""
    cx = sum(p[0] for p in corners) / 4.0
    cy = sum(p[1] for p in corners) / 4.0
    out = []
    for (x, y) in corners:
        vx, vy = x - cx, y - cy
        n = (vx * vx + vy * vy) ** 0.5 or 1.0
        out.append((x + bleed * vx / n, y + bleed * vy / n))
    return out


# ---------- máscara de oclusores (dedos etc.) ----------

def occluder_mask(rgb, quad_mask, book_color, roi, occ_tol=70.0, min_area=350):
    """Pixels DENTRO do quad cuja cor foge do creme do livro = oclusores (dedos, anéis).
    Componentes pequenos (linhas de borda, ruído, sombra fina) são descartados; o
    resultado volta dilatado + feather para preservar a borda AA dos dedos."""
    x0, y0, x1, y1 = roi
    px = rgb.load()
    qm = quad_mask.load()
    W, H = rgb.size
    raw = Image.new("L", (W, H), 0)
    rp = raw.load()
    t2 = occ_tol * occ_tol
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if qm[x, y] > 128 and dist2(px[x, y], book_color) > t2:
                rp[x, y] = 255
    # abertura morfológica: mata linhas finas e ruído
    opened = raw.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    op = opened.load()
    keep = Image.new("L", (W, H), 0)
    kp = keep.load()
    seen = bytearray(W * H)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if op[x, y] <= 128 or seen[y * W + x]:
                continue
            comp = []
            q = deque([(x, y)])
            seen[y * W + x] = 1
            while q:
                ax, ay = q.popleft()
                comp.append((ax, ay))
                for nx, ny in ((ax + 1, ay), (ax - 1, ay), (ax, ay + 1), (ax, ay - 1)):
                    if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] \
                            and op[nx, ny] > 128:
                        seen[ny * W + nx] = 1
                        q.append((nx, ny))
            if len(comp) >= min_area:
                for (ax, ay) in comp:
                    kp[ax, ay] = 255
    # recupera a franja AA dos dedos e suaviza a transição
    grown = keep.filter(ImageFilter.MaxFilter(7))
    return grown.filter(ImageFilter.GaussianBlur(1.4))


# ---------- QA ----------

def qa_sheet(img, corners, out_path, box=150, scale=2):
    """Contact sheet: 4 cantos + 4 meios-de-borda em zoom 2x, num grid único rotulado."""
    pts = {
        "TL": corners[0], "TR": corners[1], "BR": corners[2], "BL": corners[3],
        "top": ((corners[0][0] + corners[1][0]) / 2, (corners[0][1] + corners[1][1]) / 2),
        "right": ((corners[1][0] + corners[2][0]) / 2, (corners[1][1] + corners[2][1]) / 2),
        "bottom": ((corners[2][0] + corners[3][0]) / 2, (corners[2][1] + corners[3][1]) / 2),
        "left": ((corners[3][0] + corners[0][0]) / 2, (corners[3][1] + corners[0][1]) / 2),
    }
    tile = box * 2 * scale
    sheet = Image.new("RGB", (tile * 4, (tile + 28) * 2), (20, 20, 20))
    dr = ImageDraw.Draw(sheet)
    for i, (name, (cx, cy)) in enumerate(pts.items()):
        gx, gy = (i % 4) * tile, (i // 4) * (tile + 28)
        c = img.crop((int(cx) - box, int(cy) - box, int(cx) + box, int(cy) + box))
        c = c.resize((tile, tile), Image.LANCZOS)
        sheet.paste(c, (gx, gy))
        dr.text((gx + 6, gy + tile + 6), name, fill=(255, 255, 80))
    sheet.save(out_path)


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cover", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--auto-quad", help="ROI 'x0,y0,x1,y1' em volta do livro — detecta cantos")
    ap.add_argument("--corners", help="manual: 'x,y x,y x,y x,y' (TL TR BR BL)")
    ap.add_argument("--bleed", type=float, default=3.0, help="expansão do quad p/ fora (px)")
    ap.add_argument("--grad-tol", type=float, default=14.0)
    ap.add_argument("--seed-tol", type=float, default=85.0)
    ap.add_argument("--occ-threshold", type=float, default=70.0)
    ap.add_argument("--min-area", type=int, default=350)
    ap.add_argument("--no-protect", action="store_true", help="não recolocar dedos/oclusores")
    ap.add_argument("--protect-skin", action="store_true", help=argparse.SUPPRESS)  # alias v1
    ap.add_argument("--no-cover-crop", action="store_true",
                    help="não cropar a capa ao ratio do quad (pode distorcer)")
    ap.add_argument("--shadow", action="store_true",
                    help="sombra deslocada (só p/ capa 'flutuando'; cobrindo a face, NÃO usar)")
    ap.add_argument("--debug", help="salva overlay: quad + capa 55%% (conferir SEMPRE)")
    ap.add_argument("--qa", help="salva contact sheet 2x de bordas/cantos (conferir SEMPRE)")
    args = ap.parse_args()

    base = Image.open(args.base).convert("RGBA")
    rgb = base.convert("RGB")
    cover = Image.open(args.cover).convert("RGBA")
    W, H = base.size

    # 1) quad
    book_color = None
    if args.auto_quad:
        vals = [int(v) for v in args.auto_quad.replace(" ", ",").split(",") if v != ""]
        if len(vals) != 4:
            sys.exit("[erro] --auto-quad espera 'x0,y0,x1,y1'")
        roi = (max(0, vals[0]), max(0, vals[1]), min(W, vals[2]), min(H, vals[3]))
        corners, book_color = detect_quad(rgb, roi, args.grad_tol, args.seed_tol)
        print(f"[auto-quad] TL={corners[0]} TR={corners[1]} BR={corners[2]} BL={corners[3]} "
              f"base={book_color}")
    elif args.corners:
        corners = [tuple(float(v) for v in p.split(",")) for p in args.corners.split()]
        if len(corners) != 4:
            sys.exit("[erro] --corners espera 4 pontos TL TR BR BL")
        roi = (max(0, int(min(p[0] for p in corners)) - 40),
               max(0, int(min(p[1] for p in corners)) - 40),
               min(W, int(max(p[0] for p in corners)) + 40),
               min(H, int(max(p[1] for p in corners)) + 40))
    else:
        sys.exit("[erro] informe --auto-quad (recomendado) ou --corners")

    quad = expand_quad(corners, args.bleed)

    def d(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    qw = (d(quad[0], quad[1]) + d(quad[3], quad[2])) / 2
    qh = (d(quad[0], quad[3]) + d(quad[1], quad[2])) / 2
    ratio = qw / qh
    print(f"[quad] {qw:.0f}x{qh:.0f}px ratio={ratio:.3f}")

    # 2) capa: crop central ao ratio do quad (miolo intacto, sem distorção)
    if not args.no_cover_crop:
        cw, ch = cover.size
        cr = cw / ch
        if abs(cr - ratio) > 0.01:
            if cr > ratio:
                nw = round(ratio * ch)
                xc = (cw - nw) // 2
                cover = cover.crop((xc, 0, xc + nw, ch))
            else:
                nh = round(cw / ratio)
                yc = (ch - nh) // 2
                cover = cover.crop((0, yc, cw, yc + nh))
            print(f"[cover] crop central p/ ratio {ratio:.3f} -> {cover.size}")

    # 3) warp com supersampling 2x (bordas antialiased)
    SS = 2
    cover_big = cover.resize((max(2, int(qw * SS * 1.25)), max(2, int(qh * SS * 1.25))),
                             Image.LANCZOS)
    quad_ss = [(x * SS, y * SS) for (x, y) in quad]
    src = [(0, 0), (cover_big.width, 0), (cover_big.width, cover_big.height),
           (0, cover_big.height)]
    coeffs = find_coeffs(quad_ss, src)
    warped = cover_big.transform((W * SS, H * SS), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    warped = warped.resize((W, H), Image.LANCZOS)

    if args.shadow:
        sil = warped.getchannel("A").point(lambda v: 120 if v > 8 else 0)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.putalpha(sil)
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        off = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        off.paste(sh, (7, 10))
        base = Image.alpha_composite(base, off)

    orig = base.copy()
    comp = Image.alpha_composite(base, warped)

    # 4) dedos/oclusores por cima (máscara por componentes, nunca threshold cru)
    if not args.no_protect:
        if book_color is None:
            ccx = int(sum(p[0] for p in corners) / 4)
            ccy = int(sum(p[1] for p in corners) / 4)
            pxr = rgb.load()
            samples = [pxr[xx, yy] for yy in range(ccy - 10, ccy + 11)
                       for xx in range(ccx - 10, ccx + 11)]
            book_color = tuple(sorted(s[i] for s in samples)[len(samples) // 2]
                               for i in range(3))
        qmask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(qmask).polygon([(p[0], p[1]) for p in quad], fill=255)
        qmask = qmask.filter(ImageFilter.MinFilter(3))
        occ = occluder_mask(rgb, qmask, book_color, roi, args.occ_threshold, args.min_area)
        comp.paste(orig, (0, 0), occ)

    comp.convert("RGB").save(args.out)
    print(f"[ok] {args.out}")

    # 5) QA — obrigatório olhar antes de aprovar
    if args.debug:
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        overlay = Image.blend(overlay, warped, 0.55)
        dbg = Image.alpha_composite(rgb.convert("RGBA"), overlay)
        dd = ImageDraw.Draw(dbg)
        pts = [(p[0], p[1]) for p in quad] + [(quad[0][0], quad[0][1])]
        dd.line(pts, fill=(255, 0, 0, 255), width=3)
        for (x, y) in quad:
            dd.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 0, 0, 255), width=3)
        dbg.convert("RGB").save(args.debug)
        print(f"[debug] {args.debug}")
    if args.qa:
        qa_sheet(comp.convert("RGB"), quad, args.qa)
        print(f"[qa] {args.qa}")


if __name__ == "__main__":
    main()
