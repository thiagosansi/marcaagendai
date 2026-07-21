#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
entrega.py — a página de entrega do job: um HTML estático que exibe o resultado.

TODA entrega da agência fecha com uma página destas (regra do CLAUDE.md): o arquivo
`entrega.html` nasce na pasta do job, abre por file:// (zero servidor, zero rede) e
SE MOLDA ao tipo de artefato para dar a melhor visualização:

- **imagens** (posts, stories, capas) → post-wall (grade) com imagem grande; clique
  amplia em LIGHTBOX ocupando o espaço da tela (respiro nas bordas), swipe/setas
  navegam entre as peças, textos da peça (legenda/identificação/características)
  sob a imagem;
- **carrossel** → carrossel DE VERDADE (um slide por vez, passa pro lado e pro
  outro, dots + contador), com download por slide;
- **texto** (legenda, roteiro, copy, resumo) → página formatada (Markdown básico)
  com botão COPIAR (e baixar, quando veio de arquivo);
- **pdf** → preview embutido + abrir em nova aba + baixar;
- **video / audio** → player nativo + baixar;
- **site** → card com screenshot (se houver) e botão "Abrir o site";
- **arquivo** (qualquer outro) → nome + tamanho + baixar.

Botões com ícones Lucide outlined, simples, sem firulas. A página referencia os
arquivos por caminho RELATIVO — mover a pasta do job inteira não quebra nada.

Uso:

    uv run tools/entrega.py outputs/<job>/entrega.json                  # → entrega.html ao lado
    uv run tools/entrega.py spec.json --out outputs/<job>/entrega.html
    uv run tools/entrega.py spec.json --open                            # abre no navegador

Spec (JSON):

    {
      "titulo": "Stories — caixinha de perguntas",
      "subtitulo": "3 stories + legenda — prontos para publicar",   # opcional
      "data": "2026-07-13",                                          # opcional
      "itens": [
        {"tipo": "imagem", "arquivo": "05-finais/story-01.png", "titulo": "Story 01",
         "legenda": "texto que acompanha a peça (aparece no lightbox)",
         "detalhes": "story 9:16 · foto real"},                      # opcional
        {"tipo": "carrossel", "titulo": "Carrossel — Mitos", "legenda": "opcional",
         "slides": [{"arquivo": ".../capa.png", "titulo": "Capa", "legenda": "..."},
                    {"arquivo": ".../slide-02.png"}]},
        {"tipo": "texto", "titulo": "Legenda do post",
         "arquivo": "02-conteudo/legenda.md"},                       # ou "conteudo": "..."
                                                                     # "formato": "markdown"|"puro"
        {"tipo": "pdf", "arquivo": "05-finais/certificado-a4.pdf", "titulo": "Certificado A4"},
        {"tipo": "video", "arquivo": "05-finais/reels-01.mp4"},
        {"tipo": "audio", "arquivo": "02-conteudo/trilha.mp3"},
        {"tipo": "site", "caminho": "site/index.html", "titulo": "Landing page",
         "screenshot": "06-revisao/desktop-1440.png"},
        {"tipo": "arquivo", "arquivo": "05-finais/fonte-editavel.zip"}
      ]
    }

Regras de montagem: itens "imagem" consecutivos viram UM mural; itens "arquivo"
consecutivos viram UMA lista de downloads; os demais ganham bloco próprio, na ordem
do spec. Caminhos: absolutos, relativos ao cwd OU relativos ao diretório do spec.
Arquivo inexistente = erro na geração (a página nunca nasce com link quebrado).
"""

import argparse
import html
import json
import os
import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _pagina_web as ui

TIPOS = ("imagem", "carrossel", "texto", "pdf", "video", "audio", "site", "arquivo")

CSS_ENTREGA = ui.CSS_BASE + ui.CSS_LIGHTBOX + ui.CSS_CARROSSEL + ui.CSS_PROSA + """
body{padding-bottom:60px}
main{max-width:1240px;margin:0 auto;padding:16px 20px 30px;display:flex;
  flex-direction:column;gap:22px}
.ent-wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));
  gap:20px;align-items:start}
.ent-card{margin:0;background:#fff;border:1px solid #e6e9ee;border-radius:16px;
  padding:14px;box-shadow:0 1px 3px rgba(15,23,42,.05);display:flex;
  flex-direction:column;gap:10px}
.ent-card img{display:block;width:100%;height:auto;border-radius:12px;
  border:1px solid #e6e9ee}
.ent-card figcaption{display:flex;flex-direction:column;gap:2px}
.ent-nome{font-size:15px;font-weight:700;color:#25303e}
.ent-meta{font-size:12.5px;color:#6b7583}
.ent-meta code{background:#eef1f5;border-radius:6px;padding:1px 6px;font-size:.95em}
.ent-bloco{background:#fff;border:1px solid #e6e9ee;border-radius:16px;
  padding:clamp(16px,2.6vw,24px);box-shadow:0 1px 3px rgba(15,23,42,.05)}
.ent-bloco h2{margin:0;font-size:19px;letter-spacing:-.01em}
.ent-cabeca{display:flex;align-items:center;justify-content:space-between;gap:12px;
  flex-wrap:wrap;margin-bottom:14px}
.ent-desc{margin:-8px 0 14px;color:#5c6675;font-size:14.5px}
.ent-acoes{display:flex;gap:8px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:9px 14px;border:1px solid #d4d9e0;
  border-radius:10px;background:#fff;color:#39424e;font-family:inherit;font-size:14px;
  font-weight:600;line-height:1;cursor:pointer;text-decoration:none;
  transition:border-color .12s ease,color .12s ease}
.btn:hover{border-color:#9aa4b1}
.btn svg{width:17px;height:17px;flex:0 0 auto}
.btn-ok{border-color:#18914f;color:#0d5c31}
.btn [hidden]{display:none}
.ent-slide-rodape{display:flex;align-items:center;gap:12px;justify-content:center;
  flex-wrap:wrap}
.ent-slide-titulo{font-size:13.5px;font-weight:600;color:#5c6675}
.ent-prosa{max-width:76ch}
.ent-pdf iframe{display:block;width:100%;height:min(74vh,860px);border:1px solid #e6e9ee;
  border-radius:12px;background:#fff}
.ent-media{display:block;width:100%;max-height:74vh;border-radius:12px;background:#000}
audio.ent-media{max-height:none;background:none}
.ent-site-shot{display:block;width:100%;height:auto;border-radius:12px;
  border:1px solid #e6e9ee;margin-bottom:12px}
.ent-arquivos{display:flex;flex-direction:column;gap:10px}
.ent-arq{display:flex;align-items:center;gap:14px;padding:12px 14px;
  border:1px solid #e6e9ee;border-radius:12px}
.ent-arq > svg{width:26px;height:26px;color:#6b7583;flex:0 0 auto}
.ent-arq-info{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:1px}
.ent-arq-info .ent-nome{overflow-wrap:anywhere}
"""

JS_ENTREGA = """
(function () {
  "use strict";
  var dataEl = document.getElementById("ent-textos");
  var TEXTOS = dataEl ? JSON.parse(dataEl.textContent || "{}") : {};

  function copiar(txt) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(txt);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = txt;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) {}
      document.body.removeChild(ta);
      ok ? resolve() : reject();
    });
  }

  function sinalizar(btn, texto) {
    var rotulo = btn.querySelector(".btn-rotulo");
    var icPadrao = btn.querySelector(".btn-ic");
    var icOk = btn.querySelector(".btn-ic-ok");
    var antes = rotulo.textContent;
    rotulo.textContent = texto;
    btn.classList.add("btn-ok");
    if (icPadrao && icOk) { icPadrao.hidden = true; icOk.hidden = false; }
    setTimeout(function () {
      rotulo.textContent = antes;
      btn.classList.remove("btn-ok");
      if (icPadrao && icOk) { icPadrao.hidden = false; icOk.hidden = true; }
    }, 1600);
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-copiar]");
    if (!btn) return;
    var txt = TEXTOS[btn.getAttribute("data-copiar")];
    if (typeof txt !== "string") return;
    copiar(txt).then(function () { sinalizar(btn, "Copiado"); })
      .catch(function () { sinalizar(btn, "Falhou — selecione e copie"); });
  });
})();
"""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def humano(nbytes):
    for unidade in ("B", "KB", "MB", "GB"):
        if nbytes < 1024 or unidade == "GB":
            if unidade == "B":
                return f"{nbytes} {unidade}"
            return f"{nbytes:.1f}".replace(".", ",") + f" {unidade}"
        nbytes /= 1024


def btn_baixar(href, rotulo="Baixar"):
    return (f'<a class="btn" href="{href}" download>{ui.icone("download")}'
            f'<span class="btn-rotulo">{html.escape(rotulo)}</span></a>')


def btn_abrir(href, rotulo="Abrir em nova aba"):
    return (f'<a class="btn" href="{href}" target="_blank" rel="noopener">'
            f'{ui.icone("external-link")}<span class="btn-rotulo">{html.escape(rotulo)}</span></a>')


def btn_copiar(iid, rotulo="Copiar"):
    return (f'<button type="button" class="btn" data-copiar="{html.escape(iid)}">'
            f'{ui.icone("copy", "ic btn-ic")}'
            f'{ui.icone("check", "ic btn-ic-ok", extra="hidden")}'
            f'<span class="btn-rotulo">{html.escape(rotulo)}</span></button>')


# ---------------------------------------------------------------------------
# spec
# ---------------------------------------------------------------------------

def carregar_spec(caminho):
    if not caminho.exists():
        sys.exit(f"[erro] spec não encontrado: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.exit(f"[erro] spec inválido (JSON): {e}")
    if not isinstance(dados, dict) or not isinstance(dados.get("itens"), list) or not dados["itens"]:
        sys.exit('[erro] spec precisa de {"itens": [...]} com pelo menos 1 item.')
    return dados


def _campo(bruto, chave):
    valor = bruto.get(chave)
    return str(valor) if valor else ""


def normalizar_itens(dados, spec_dir):
    """Valida cada item, resolve caminhos e devolve a lista normalizada."""
    itens = []
    for i, bruto in enumerate(dados["itens"], 1):
        if not isinstance(bruto, dict):
            sys.exit(f"[erro] item #{i} do spec não é um objeto JSON.")
        tipo = str(bruto.get("tipo") or "").strip().lower()
        if tipo not in TIPOS:
            sys.exit(f"[erro] item #{i}: tipo \"{tipo}\" inválido (use {' | '.join(TIPOS)}).")

        item = {
            "tipo": tipo,
            "id": str(bruto.get("id") or f"item-{i:02d}"),
            "titulo": _campo(bruto, "titulo"),
            "legenda": _campo(bruto, "legenda"),
            "detalhes": _campo(bruto, "detalhes"),
        }

        def resolver(chave, obrigatorio=True, de=bruto, contexto=f"item #{i}"):
            valor = de.get(chave)
            if not valor:
                if obrigatorio:
                    sys.exit(f"[erro] {contexto} ({tipo}) exige \"{chave}\".")
                return None
            alvo = ui.resolver_caminho(valor, spec_dir)
            if alvo is None:
                sys.exit(f"[erro] {contexto}: arquivo não encontrado: {valor} "
                         f"(tentei absoluto, cwd e {spec_dir}).")
            return alvo

        if tipo == "carrossel":
            slides_brutos = bruto.get("slides")
            if not isinstance(slides_brutos, list) or len(slides_brutos) < 2:
                sys.exit(f"[erro] item #{i} (carrossel) exige \"slides\" com pelo menos 2 slides.")
            slides = []
            for j, sb in enumerate(slides_brutos, 1):
                if not isinstance(sb, dict):
                    sys.exit(f"[erro] item #{i}: slide #{j} não é um objeto JSON.")
                alvo = resolver("arquivo", de=sb, contexto=f"item #{i}, slide #{j}")
                slides.append({
                    "arquivo": alvo,
                    "titulo": str(sb.get("titulo") or f"Slide {j}"),
                    "legenda": _campo(sb, "legenda"),
                    "detalhes": _campo(sb, "detalhes"),
                })
            item["slides"] = slides
            item["titulo"] = item["titulo"] or "Carrossel"

        elif tipo == "texto":
            conteudo = bruto.get("conteudo")
            if conteudo is None:
                alvo = resolver("arquivo")
                conteudo = alvo.read_text(encoding="utf-8")
                item["arquivo"] = alvo
            item["conteudo"] = str(conteudo)
            item["formato"] = str(bruto.get("formato") or "markdown").lower()
            item["titulo"] = item["titulo"] or "Texto"

        elif tipo == "site":
            valor = bruto.get("caminho") or bruto.get("arquivo")
            if not valor:
                sys.exit(f"[erro] item #{i} (site) exige \"caminho\" (o index.html do site).")
            alvo = ui.resolver_caminho(valor, spec_dir)
            if alvo is None:
                sys.exit(f"[erro] item #{i}: site não encontrado: {valor}.")
            item["arquivo"] = alvo
            shot = bruto.get("screenshot")
            if shot:
                item["screenshot"] = resolver("screenshot", obrigatorio=False)
            item["titulo"] = item["titulo"] or "Site"

        else:  # imagem | pdf | video | audio | arquivo
            item["arquivo"] = resolver("arquivo")
            item["titulo"] = item["titulo"] or item["arquivo"].stem

        itens.append(item)
    return itens


# ---------------------------------------------------------------------------
# página
# ---------------------------------------------------------------------------

def montar_pagina(dados, itens, out_path, titulo_cli=None):
    e = html.escape
    out_dir = out_path.resolve().parent
    lb_grupos, textos_copiaveis, blocos = {}, {}, []

    def href(caminho):
        rel = Path(os.path.relpath(caminho, out_dir)).as_posix()
        return quote(rel, safe="/.-_~")

    def card_imagem(item, gid, idx):
        legenda = f'<div class="ent-meta">{e(item["detalhes"])}</div>' if item["detalhes"] else ""
        return (
            '<figure class="ent-card">'
            f'<img src="{href(item["arquivo"])}" alt="{e(item["titulo"])}" '
            f'data-lb-grupo="{e(gid)}" data-lb-i="{idx}" loading="lazy">'
            f'<figcaption><div class="ent-nome">{e(item["titulo"])}</div>{legenda}</figcaption>'
            f'<div class="ent-acoes">{btn_baixar(href(item["arquivo"]))}</div>'
            '</figure>'
        )

    def bloco_cabeca(item, acoes=""):
        acoes_html = f'<div class="ent-acoes">{acoes}</div>' if acoes else ""
        cab = f'<div class="ent-cabeca"><h2>{e(item["titulo"])}</h2>{acoes_html}</div>'
        desc = f'<p class="ent-desc">{e(item["legenda"])}</p>' if item["legenda"] else ""
        return cab + desc

    i = 0
    while i < len(itens):
        item = itens[i]

        if item["tipo"] == "imagem":  # sequência de imagens = um mural
            gid = f"mural-{len(lb_grupos)}"
            lb_grupos[gid] = []
            cards = []
            while i < len(itens) and itens[i]["tipo"] == "imagem":
                atual = itens[i]
                lb_grupos[gid].append({
                    "src": href(atual["arquivo"]),
                    "titulo": atual["titulo"],
                    "legenda": atual["legenda"],
                    "detalhes": atual["detalhes"],
                })
                cards.append(card_imagem(atual, gid, len(lb_grupos[gid]) - 1))
                i += 1
            blocos.append(f'<section class="ent-wall">{"".join(cards)}</section>')
            continue

        if item["tipo"] == "arquivo":  # sequência de arquivos = uma lista
            linhas = []
            while i < len(itens) and itens[i]["tipo"] == "arquivo":
                atual = itens[i]
                arq = atual["arquivo"]
                meta = f"{arq.name} · {humano(arq.stat().st_size)}"
                linhas.append(
                    f'<div class="ent-arq">{ui.icone("file")}'
                    f'<div class="ent-arq-info"><div class="ent-nome">{e(atual["titulo"])}</div>'
                    f'<div class="ent-meta">{e(meta)}</div></div>'
                    f'{btn_baixar(href(arq))}</div>'
                )
                i += 1
            blocos.append(f'<section class="ent-bloco ent-arquivos">{"".join(linhas)}</section>')
            continue

        if item["tipo"] == "carrossel":
            gid = f"car-{item['id']}"
            dom_id = ui.dom_id_seguro(item["id"], "car")
            lb_grupos[gid] = []
            slides_html, rotulos = [], []
            for j, slide in enumerate(item["slides"]):
                titulo_slide = f'{item["titulo"]} — {slide["titulo"]}'
                lb_grupos[gid].append({
                    "src": href(slide["arquivo"]),
                    "titulo": titulo_slide,
                    "legenda": slide["legenda"],
                    "detalhes": slide["detalhes"],
                })
                slides_html.append(
                    f'<img src="{href(slide["arquivo"])}" alt="{e(titulo_slide)}" '
                    f'data-lb-grupo="{e(gid)}" data-lb-i="{j}" loading="lazy">'
                    f'<div class="ent-slide-rodape"><span class="ent-slide-titulo">{e(slide["titulo"])}</span>'
                    f'{btn_baixar(href(slide["arquivo"]), "Baixar slide")}</div>'
                )
                rotulos.append(slide["titulo"])
            blocos.append(
                f'<section class="ent-bloco">{bloco_cabeca(item)}'
                f'{ui.montar_carrossel(dom_id, slides_html, rotulos)}</section>'
            )

        elif item["tipo"] == "texto":
            textos_copiaveis[item["id"]] = item["conteudo"]
            acoes = btn_copiar(item["id"])
            if item.get("arquivo"):
                acoes += btn_baixar(href(item["arquivo"]))
            corpo = (ui.markdown_para_html(item["conteudo"]) if item["formato"] == "markdown"
                     else ui.texto_para_html(item["conteudo"]))
            blocos.append(
                f'<section class="ent-bloco">{bloco_cabeca(item, acoes)}'
                f'<div class="ent-prosa prosa">{corpo}</div></section>'
            )

        elif item["tipo"] == "pdf":
            arq = item["arquivo"]
            acoes = btn_abrir(href(arq)) + btn_baixar(href(arq))
            meta = f'<p class="ent-meta">{e(arq.name)} · {e(humano(arq.stat().st_size))}</p>'
            blocos.append(
                f'<section class="ent-bloco">{bloco_cabeca(item, acoes)}'
                f'<div class="ent-pdf"><iframe src="{href(arq)}" title="{e(item["titulo"])}" '
                f'loading="lazy"></iframe></div>{meta}</section>'
            )

        elif item["tipo"] in ("video", "audio"):
            arq = item["arquivo"]
            tag = ("<video" if item["tipo"] == "video" else "<audio")
            player = (f'{tag} class="ent-media" controls preload="metadata" '
                      f'src="{href(arq)}"></{tag[1:]}>')
            blocos.append(
                f'<section class="ent-bloco">{bloco_cabeca(item, btn_baixar(href(arq)))}'
                f'{player}</section>'
            )

        elif item["tipo"] == "site":
            arq = item["arquivo"]
            shot = ""
            if item.get("screenshot"):
                shot = (f'<a href="{href(arq)}" target="_blank" rel="noopener">'
                        f'<img class="ent-site-shot" src="{href(item["screenshot"])}" '
                        f'alt="Prévia — {e(item["titulo"])}" loading="lazy"></a>')
            rel_legivel = Path(os.path.relpath(arq, out_dir)).as_posix()
            meta = f'<p class="ent-meta">abre por file:// — <code>{e(rel_legivel)}</code></p>'
            blocos.append(
                f'<section class="ent-bloco">{bloco_cabeca(item, btn_abrir(href(arq), "Abrir o site"))}'
                f'{shot}{meta}</section>'
            )

        i += 1

    titulo = titulo_cli or _campo(dados, "titulo") or "Entrega"
    sub = " · ".join(x for x in (_campo(dados, "subtitulo"), _campo(dados, "data")) if x)
    sub_html = f"<p>{e(sub)}</p>" if sub else ""
    textos_json = json.dumps(textos_copiaveis, ensure_ascii=False).replace("</", "<\\/")

    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{e(titulo)}</title>'
        f'<style>{CSS_ENTREGA}</style></head><body>'
        f'<header class="pw-topo"><h1>{e(titulo)}</h1>{sub_html}</header>'
        f'<main>{"".join(blocos)}</main>'
        f'{ui.montar_lightbox({k: v for k, v in lb_grupos.items() if v})}'
        f'<script>{ui.JS_CARROSSEL}</script>'
        f'<script id="ent-textos" type="application/json">{textos_json}</script>'
        f'<script>{JS_ENTREGA}</script>'
        '</body></html>'
    )


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="Gera a página de entrega (entrega.html) do job — HTML estático que "
                    "se molda ao tipo de artefato, com lightbox, carrossel e botões de "
                    "copiar/baixar.")
    ap.add_argument("spec", type=Path, help="entrega.json com os itens da entrega")
    ap.add_argument("--out", type=Path,
                    help="HTML de saída (default: entrega.html ao lado do spec)")
    ap.add_argument("--titulo", help="título da página (default: do spec)")
    ap.add_argument("--open", action="store_true", help="abrir a página no navegador ao fim")
    args = ap.parse_args()

    dados = carregar_spec(args.spec)
    spec_dir = args.spec.resolve().parent
    out = args.out or (spec_dir / "entrega.html")
    itens = normalizar_itens(dados, spec_dir)
    pagina = montar_pagina(dados, itens, out, args.titulo)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pagina, encoding="utf-8")

    contagem = {}
    for it in itens:
        contagem[it["tipo"]] = contagem.get(it["tipo"], 0) + 1
    resumo = " · ".join(f"{v} {k}" for k, v in contagem.items())
    print(f"[entrega] {out}  ({resumo})", flush=True)
    print(f"[entrega] abrir no navegador: file://{out.resolve()}", flush=True)
    if args.open:
        webbrowser.open(f"file://{out.resolve()}")


if __name__ == "__main__":
    main()
