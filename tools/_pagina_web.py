#!/usr/bin/env python3
"""
_pagina_web.py — blocos COMPARTILHADOS das páginas web locais do harness.

Não é CLI: é módulo importado pelos tools vizinhos (`aprovacao.py`, `entrega.py`)
para as duas páginas terem a MESMA linguagem de interface — casca neutra, lightbox
de imagem (ampliar/zoom com navegação lateral), carrossel real (swipe/setas/dots),
ícones Lucide outlined embutidos e um renderizador mínimo de Markdown.

Import (os tools já fazem isso):

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _pagina_web as ui

Tudo aqui é neutro do HARNESS — nenhuma identidade de marca vive neste código.

Componentes:
- CSS_BASE / FONTES ............ reset + corpo + topo (.pw-topo)
- icone(nome) .................. SVG Lucide inline (outlined, currentColor)
- CSS_LIGHTBOX / JS_LIGHTBOX ... overlay de ampliação: imagem ocupa o espaço da
  tela (com respiro nas bordas), swipe/setas/teclado navegam entre as peças do
  grupo, textos da peça (título, legenda, detalhes) aparecem sob a imagem.
  Uso: elementos com data-lb-grupo="<gid>" + data-lb-i="<n>" abrem o grupo;
  os dados vêm de <script id="lb-data" type="application/json">{gid: [{src,
  titulo, legenda, detalhes}]}</script> (montar_lightbox faz tudo).
- CSS_CARROSSEL / JS_CARROSSEL . carrossel de verdade (um slide por vez, passa
  pro lado e pro outro): botões, dots, contador, swipe, teclado. API global
  window.__car[id].irPara(i) + evento "car:mudou" (bubbles) para a página
  sincronizar o que quiser (ex.: widget de aprovação por slide).
- montar_carrossel(...) ........ markup do carrossel a partir dos slides prontos
- markdown_para_html(md) ....... subconjunto de Markdown (títulos, listas, tabela
  simples, negrito/itálico/código, links, citação, hr) para exibir textos
- texto_para_html(txt) ......... texto puro → parágrafos
- resolver_caminho(bruto, dir) . absoluto | relativo ao cwd | relativo à base
"""

import html
import json
import re
from pathlib import Path

FONTES = ('-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif')

# ---------------------------------------------------------------------------
# Ícones Lucide (lucide.dev, ISC) — geometria idêntica à vendorizada em
# assets/icones/lucide/, embutida para a página ser 100% autocontida.
# ---------------------------------------------------------------------------

_ICONES = {
    "copy": '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>'
            '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "download": '<path d="M12 15V3"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
                '<path d="m7 10 5 5 5-5"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/>'
                     '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "file": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706'
            'l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/>'
            '<path d="M14 2v5a1 1 0 0 0 1 1h5"/>',
    "file-text": '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706'
                 'l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/>'
                 '<path d="M14 2v5a1 1 0 0 0 1 1h5"/>'
                 '<path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
}


def icone(nome, classe="ic", extra=""):
    """SVG Lucide inline, outlined, herdando a cor do texto (currentColor).
    `extra`: atributos adicionais na tag (ex.: "hidden")."""
    corpo = _ICONES[nome]
    extra = f" {extra.strip()}" if extra.strip() else ""
    return (f'<svg class="{classe}"{extra} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{corpo}</svg>')


# ---------------------------------------------------------------------------
# Casca base
# ---------------------------------------------------------------------------

CSS_BASE = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#f2f4f7;color:#1e2836;font-family:""" + FONTES + """;
  -webkit-font-smoothing:antialiased}
.pw-topo{max-width:1240px;margin:0 auto;padding:34px 20px 6px}
.pw-topo h1{font-size:clamp(22px,4vw,30px);margin:0 0 6px;letter-spacing:-.02em}
.pw-topo p{margin:0;color:#5c6675;font-size:15px}
img{max-width:100%}
"""

# ---------------------------------------------------------------------------
# Lightbox — ampliar imagem no espaço disponível da tela, com navegação lateral
# ---------------------------------------------------------------------------

CSS_LIGHTBOX = """
.lb-trava{overflow:hidden}
#lb{position:fixed;inset:0;z-index:2147483200;display:none;flex-direction:column;
  background:rgba(9,13,19,.93);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
#lb.lb-aberta{display:flex}
#lb-stage{flex:1 1 auto;min-height:0;display:flex;align-items:center;justify-content:center;
  padding:clamp(18px,3.5vw,44px)}
#lb-img{max-width:100%;max-height:100%;object-fit:contain;border-radius:10px;
  box-shadow:0 12px 48px rgba(0,0,0,.5)}
#lb-info{flex:0 0 auto;text-align:center;color:#e8edf4;max-height:34vh;overflow:auto;
  padding:0 clamp(18px,5vw,64px) calc(18px + env(safe-area-inset-bottom,0px))}
#lb-titulo{font-weight:700;font-size:15.5px}
#lb-legenda{margin:6px auto 0;font-size:14.5px;line-height:1.55;color:#c3ccd8;
  max-width:72ch;white-space:pre-wrap}
#lb-detalhes{margin:6px auto 0;font-size:12.5px;color:#93a0b0;max-width:72ch}
#lb-contador{margin-top:8px;font-size:12px;letter-spacing:.06em;color:#8a97a8}
.lb-btn{position:absolute;z-index:2;display:flex;align-items:center;justify-content:center;
  width:46px;height:46px;border-radius:50%;border:1px solid rgba(255,255,255,.28);
  background:rgba(15,21,29,.45);color:#fff;cursor:pointer;padding:0;
  transition:background .15s ease}
.lb-btn:hover{background:rgba(15,21,29,.78)}
.lb-btn svg{width:22px;height:22px}
.lb-x{top:max(14px,env(safe-area-inset-top,0px));right:14px}
.lb-prev{left:10px;top:50%;transform:translateY(-50%)}
.lb-next{right:10px;top:50%;transform:translateY(-50%)}
@media (max-width:640px){.lb-prev,.lb-next{display:none}}
[data-lb-grupo]{cursor:zoom-in}
"""

JS_LIGHTBOX = """
(function () {
  "use strict";
  var dataEl = document.getElementById("lb-data");
  var lb = document.getElementById("lb");
  if (!dataEl || !lb) return;
  var GRUPOS = JSON.parse(dataEl.textContent || "{}");
  var img = document.getElementById("lb-img");
  var elTitulo = document.getElementById("lb-titulo");
  var elLegenda = document.getElementById("lb-legenda");
  var elDetalhes = document.getElementById("lb-detalhes");
  var elContador = document.getElementById("lb-contador");
  var btnPrev = lb.querySelector(".lb-prev");
  var btnNext = lb.querySelector(".lb-next");
  var grupo = null, idx = 0;

  function itens() { return GRUPOS[grupo] || []; }
  function preencher(el, txt) { el.textContent = txt || ""; el.hidden = !txt; }

  function mostrar() {
    var lista = itens(), it = lista[idx];
    if (!it) return;
    img.src = it.src;
    img.alt = it.titulo || "";
    preencher(elTitulo, it.titulo);
    preencher(elLegenda, it.legenda);
    preencher(elDetalhes, it.detalhes);
    elContador.textContent = lista.length > 1 ? (idx + 1) + " / " + lista.length : "";
    var nav = lista.length > 1;
    btnPrev.style.visibility = nav ? "visible" : "hidden";
    btnNext.style.visibility = nav ? "visible" : "hidden";
    if (nav) [idx + 1, idx - 1].forEach(function (j) {
      var n = (j + lista.length) % lista.length;
      var pre = new Image(); pre.src = lista[n].src;
    });
  }
  function abrir(gid, i) {
    if (!GRUPOS[gid] || !GRUPOS[gid].length) return;
    grupo = gid; idx = Math.max(0, Math.min(GRUPOS[gid].length - 1, i || 0));
    lb.classList.add("lb-aberta");
    document.documentElement.classList.add("lb-trava");
    mostrar();
    lb.querySelector(".lb-x").focus();
  }
  function fechar() {
    lb.classList.remove("lb-aberta");
    document.documentElement.classList.remove("lb-trava");
    grupo = null;
  }
  function passo(d) {
    var n = itens().length;
    if (!grupo || n < 2) return;
    idx = (idx + d + n) % n;
    mostrar();
  }

  document.addEventListener("click", function (ev) {
    var alvo = ev.target.closest("[data-lb-grupo]");
    if (!alvo) return;
    ev.preventDefault();
    abrir(alvo.getAttribute("data-lb-grupo"), parseInt(alvo.getAttribute("data-lb-i") || "0", 10));
  });
  lb.querySelector(".lb-x").addEventListener("click", fechar);
  btnPrev.addEventListener("click", function () { passo(-1); });
  btnNext.addEventListener("click", function () { passo(1); });
  lb.addEventListener("click", function (ev) {
    if (ev.target === lb || ev.target.id === "lb-stage") fechar();
  });
  document.addEventListener("keydown", function (ev) {
    if (!lb.classList.contains("lb-aberta")) return;
    if (ev.key === "Escape") fechar();
    else if (ev.key === "ArrowLeft") passo(-1);
    else if (ev.key === "ArrowRight") passo(1);
  });
  var t0 = null;
  lb.addEventListener("touchstart", function (ev) {
    if (ev.touches.length === 1) t0 = { x: ev.touches[0].clientX, y: ev.touches[0].clientY };
  }, { passive: true });
  lb.addEventListener("touchend", function (ev) {
    if (!t0) return;
    var dx = ev.changedTouches[0].clientX - t0.x;
    var dy = ev.changedTouches[0].clientY - t0.y;
    t0 = null;
    if (Math.abs(dx) > 48 && Math.abs(dy) < 90) passo(dx < 0 ? 1 : -1);
  }, { passive: true });
})();
"""


def montar_lightbox(grupos):
    """Overlay + dados + JS do lightbox. `grupos`: {gid: [{src, titulo, legenda,
    detalhes}]}. Inserir uma única vez, no fim do <body>."""
    dados = json.dumps(grupos, ensure_ascii=False).replace("</", "<\\/")
    return (
        '<div id="lb" role="dialog" aria-modal="true" aria-label="Visualização ampliada">'
        f'<button type="button" class="lb-btn lb-x" aria-label="Fechar">{icone("x")}</button>'
        f'<button type="button" class="lb-btn lb-prev" aria-label="Anterior">{icone("chevron-left")}</button>'
        f'<button type="button" class="lb-btn lb-next" aria-label="Próxima">{icone("chevron-right")}</button>'
        '<div id="lb-stage"><img id="lb-img" alt=""></div>'
        '<div id="lb-info"><div id="lb-titulo"></div><div id="lb-legenda"></div>'
        '<div id="lb-detalhes"></div><div id="lb-contador"></div></div>'
        '</div>'
        f'<script id="lb-data" type="application/json">{dados}</script>'
        f'<script>{JS_LIGHTBOX}</script>'
    )


# ---------------------------------------------------------------------------
# Carrossel — um slide por vez, passa pro lado e pro outro
# ---------------------------------------------------------------------------

CSS_CARROSSEL = """
.car{position:relative;outline:none}
.car-viewport{overflow:hidden;border-radius:14px}
.car-track{display:flex;transition:transform .3s ease;will-change:transform}
.car-slide{flex:0 0 100%;min-width:100%;display:flex;flex-direction:column;
  align-items:center;gap:10px;padding:0 2px}
.car-slide img{display:block;max-width:100%;max-height:min(70vh,760px);height:auto;
  object-fit:contain;border-radius:12px}
.car-prev,.car-next{position:absolute;top:50%;transform:translateY(-50%);z-index:2;
  display:flex;align-items:center;justify-content:center;width:42px;height:42px;
  border-radius:50%;border:1px solid #d4d9e0;background:rgba(255,255,255,.94);
  color:#39424e;cursor:pointer;padding:0;box-shadow:0 2px 8px rgba(15,23,42,.12)}
.car-prev{left:10px}
.car-next{right:10px}
.car-prev:disabled,.car-next:disabled{opacity:.35;cursor:default}
.car-prev svg,.car-next svg{width:20px;height:20px}
.car-rodape{display:flex;flex-direction:column;align-items:center;gap:6px;margin-top:12px}
.car-dots{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.car-dot{width:10px;height:10px;border-radius:50%;border:none;padding:0;background:#cdd4dd;
  cursor:pointer;transition:transform .12s ease,background .12s ease}
.car-dot-ativo{outline:2px solid #39424e;outline-offset:2px}
.car-dot-sim{background:#18914f}
.car-dot-nao{background:#c07f18}
.car-contador{font-size:12.5px;color:#6b7583}
"""

JS_CARROSSEL = """
(function () {
  "use strict";
  window.__car = window.__car || {};
  Array.prototype.slice.call(document.querySelectorAll(".car")).forEach(function (car) {
    var track = car.querySelector(".car-track");
    var slides = Array.prototype.slice.call(track.children);
    var dots = Array.prototype.slice.call(car.querySelectorAll(".car-dot"));
    var cont = car.querySelector(".car-contador");
    var btnPrev = car.querySelector(".car-prev");
    var btnNext = car.querySelector(".car-next");
    var idx = 0;

    function irPara(novo) {
      idx = Math.max(0, Math.min(slides.length - 1, novo));
      track.style.transform = "translateX(" + (-idx * 100) + "%)";
      dots.forEach(function (d, i) {
        d.classList.toggle("car-dot-ativo", i === idx);
        d.setAttribute("aria-current", i === idx ? "true" : "false");
      });
      if (cont) cont.textContent = (idx + 1) + " / " + slides.length;
      if (btnPrev) btnPrev.disabled = idx === 0;
      if (btnNext) btnNext.disabled = idx === slides.length - 1;
      car.dispatchEvent(new CustomEvent("car:mudou", {
        detail: { id: car.id, indice: idx }, bubbles: true
      }));
    }

    if (btnPrev) btnPrev.addEventListener("click", function () { irPara(idx - 1); });
    if (btnNext) btnNext.addEventListener("click", function () { irPara(idx + 1); });
    dots.forEach(function (d, i) {
      d.addEventListener("click", function () { irPara(i); });
    });
    var vp = car.querySelector(".car-viewport"), t0 = null;
    vp.addEventListener("touchstart", function (ev) {
      if (ev.touches.length === 1) t0 = { x: ev.touches[0].clientX, y: ev.touches[0].clientY };
    }, { passive: true });
    vp.addEventListener("touchend", function (ev) {
      if (!t0) return;
      var dx = ev.changedTouches[0].clientX - t0.x;
      var dy = ev.changedTouches[0].clientY - t0.y;
      t0 = null;
      if (Math.abs(dx) > 42 && Math.abs(dy) < 80) irPara(idx + (dx < 0 ? 1 : -1));
    }, { passive: true });
    car.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowLeft") { ev.preventDefault(); irPara(idx - 1); }
      else if (ev.key === "ArrowRight") { ev.preventDefault(); irPara(idx + 1); }
    });

    window.__car[car.id] = {
      irPara: irPara,
      indice: function () { return idx; },
      total: slides.length
    };
    irPara(0);
  });
})();
"""


def montar_carrossel(dom_id, slides_html, rotulos=None):
    """Markup do carrossel. `slides_html`: conteúdo pronto de cada slide (a página
    decide o que vai dentro — imagem com data-lb, rótulo, botão…). `rotulos`:
    aria-label de cada dot (default "Slide N")."""
    e = html.escape
    rotulos = rotulos or [None] * len(slides_html)
    dots = "".join(
        f'<button type="button" class="car-dot" aria-label="{e(r or f"Slide {i + 1}")}"></button>'
        for i, r in enumerate(rotulos)
    )
    slides = "".join(f'<div class="car-slide">{s}</div>' for s in slides_html)
    return (
        f'<div class="car" id="{e(dom_id)}" tabindex="0" role="group" '
        'aria-roledescription="carrossel">'
        f'<div class="car-viewport"><div class="car-track">{slides}</div></div>'
        f'<button type="button" class="car-prev" aria-label="Slide anterior">{icone("chevron-left")}</button>'
        f'<button type="button" class="car-next" aria-label="Próximo slide">{icone("chevron-right")}</button>'
        f'<div class="car-rodape"><div class="car-dots">{dots}</div>'
        '<div class="car-contador"></div></div>'
        '</div>'
    )


def dom_id_seguro(bruto, prefixo="el"):
    """Converte um id de spec em id de DOM válido e estável."""
    limpo = re.sub(r"[^A-Za-z0-9_-]+", "-", str(bruto)).strip("-") or "x"
    return f"{prefixo}-{limpo}"


# ---------------------------------------------------------------------------
# Texto → HTML
# ---------------------------------------------------------------------------

def texto_para_html(texto):
    """Texto puro → parágrafos (quebra dupla separa; simples vira <br>)."""
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", texto.strip()) if p.strip()]
    return "".join(
        "<p>" + html.escape(p).replace("\n", "<br>") + "</p>" for p in paragrafos
    )


def _md_inline(s):
    """Regras inline sobre texto JÁ escapado."""
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def markdown_para_html(md):
    """Subconjunto de Markdown suficiente para legendas, roteiros e resumos:
    títulos #–####, listas -/*/1., citação >, tabela simples com |, ``` código,
    ---, negrito/itálico/código/links inline. O que não reconhece vira parágrafo."""
    linhas = md.replace("\r\n", "\n").split("\n")
    saida, i, n = [], 0, len(linhas)

    def flush_para(buf):
        if buf:
            saida.append("<p>" + _md_inline(html.escape(" ".join(buf)))
                         .replace("  ", " ") + "</p>")
            buf.clear()

    buf = []
    while i < n:
        linha = linhas[i]
        crua = linha.strip()

        if crua.startswith("```"):
            flush_para(buf)
            bloco, i = [], i + 1
            while i < n and not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i])
                i += 1
            i += 1  # pula o fecho
            saida.append("<pre><code>" + html.escape("\n".join(bloco)) + "</code></pre>")
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", crua)
        if m:
            flush_para(buf)
            nivel = min(len(m.group(1)) + 1, 5)  # h1 do doc vira h2 na página
            saida.append(f"<h{nivel}>" + _md_inline(html.escape(m.group(2).strip())) + f"</h{nivel}>")
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", crua):
            flush_para(buf)
            saida.append("<hr>")
            i += 1
            continue

        if crua.startswith("|") and crua.endswith("|"):
            flush_para(buf)
            tabela = []
            while i < n and linhas[i].strip().startswith("|"):
                tabela.append([c.strip() for c in linhas[i].strip().strip("|").split("|")])
                i += 1
            corpo = [l for l in tabela if not all(re.fullmatch(r":?-{2,}:?", c or "-") for c in l)]
            tem_cab = len(corpo) < len(tabela)
            partes = ["<table>"]
            for j, l in enumerate(corpo):
                tag = "th" if (tem_cab and j == 0) else "td"
                partes.append("<tr>" + "".join(
                    f"<{tag}>" + _md_inline(html.escape(c)) + f"</{tag}>" for c in l) + "</tr>")
            partes.append("</table>")
            saida.append("".join(partes))
            continue

        if re.match(r"^[-*]\s+", crua):
            flush_para(buf)
            itens = []
            while i < n and re.match(r"^[-*]\s+", linhas[i].strip()):
                itens.append(re.sub(r"^[-*]\s+", "", linhas[i].strip()))
                i += 1
            saida.append("<ul>" + "".join(
                "<li>" + _md_inline(html.escape(it)) + "</li>" for it in itens) + "</ul>")
            continue

        if re.match(r"^\d+[.)]\s+", crua):
            flush_para(buf)
            itens = []
            while i < n and re.match(r"^\d+[.)]\s+", linhas[i].strip()):
                itens.append(re.sub(r"^\d+[.)]\s+", "", linhas[i].strip()))
                i += 1
            saida.append("<ol>" + "".join(
                "<li>" + _md_inline(html.escape(it)) + "</li>" for it in itens) + "</ol>")
            continue

        if crua.startswith(">"):
            flush_para(buf)
            citacao = []
            while i < n and linhas[i].strip().startswith(">"):
                citacao.append(re.sub(r"^>\s?", "", linhas[i].strip()))
                i += 1
            saida.append("<blockquote>" + _md_inline(html.escape(" ".join(citacao))) + "</blockquote>")
            continue

        if not crua:
            flush_para(buf)
            i += 1
            continue

        buf.append(crua)
        i += 1

    flush_para(buf)
    return "".join(saida)


CSS_PROSA = """
.prosa{font-size:15.5px;line-height:1.65;color:#2a3442}
.prosa h2,.prosa h3,.prosa h4,.prosa h5{margin:1.2em 0 .4em;letter-spacing:-.01em;line-height:1.25}
.prosa h2{font-size:21px}
.prosa h3{font-size:18px}
.prosa h4,.prosa h5{font-size:16px}
.prosa p{margin:0 0 12px}
.prosa ul,.prosa ol{margin:0 0 12px;padding-left:22px}
.prosa li{margin:0 0 6px}
.prosa blockquote{margin:0 0 12px;padding:8px 14px;border-left:3px solid #cdd4dd;color:#5c6675}
.prosa code{background:#eef1f5;border-radius:6px;padding:1px 6px;font-size:.92em}
.prosa pre{background:#eef1f5;border-radius:10px;padding:12px 14px;overflow-x:auto}
.prosa pre code{background:none;padding:0}
.prosa hr{border:none;border-top:1px solid #e3e6eb;margin:16px 0}
.prosa table{border-collapse:collapse;margin:0 0 12px;width:100%;font-size:14.5px}
.prosa th,.prosa td{border:1px solid #e3e6eb;padding:7px 10px;text-align:left;vertical-align:top}
.prosa th{background:#f7f8fa}
.prosa a{color:#1d4ed8}
.prosa > :first-child{margin-top:0}
.prosa > :last-child{margin-bottom:0}
"""


# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

def resolver_caminho(bruto, base_dir):
    """Absoluto, relativo ao cwd OU relativo à base (dir do spec) — nessa ordem.
    Devolve Path resolvido ou None se não existir."""
    p = Path(bruto).expanduser()
    if p.is_absolute():
        return p if p.exists() else None
    for base in (Path.cwd(), base_dir):
        candidato = base / p
        if candidato.exists():
            return candidato.resolve()
    return None
