#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
aprovacao.py — página local de aprovação: o cliente revisa, vota 👍/👎, comenta e conclui.

Sobe um servidor HTTP local (SEMPRE 127.0.0.1), abre a página no navegador e espera o
CLIENTE humano revisar as entregas. Cada item/seção ganha um widget "👍 Aprovar /
👎 Ajustar" + campo de comentários; regra dura: 👎 exige comentário não-vazio. Ao fim da
página há um campo de COMENTÁRIO GERAL (opcional — observações transversais que não são
de uma peça; não trava a conclusão). O botão final "✅ Pronto — tudo revisado" (rodapé
fixo, com contador "X de N revisados") só libera quando TODOS os itens foram votados E
todo 👎 tem comentário. Ao concluir, o servidor grava o feedback em JSON (--out),
imprime um resumo legível no stdout e encerra com exit 0 — devolvendo o controle à
agência, que aplica os ajustes e reabre nova rodada. Loop até aprovar.

O FORMATO da página segue o ARTEFATO (escolher certo é obrigação da agência):

- **layout "mural"** (default) — post-wall para PEÇAS PRODUZIDAS (posts, stories,
  capas): grade de cards com imagem grande; clique amplia em LIGHTBOX ocupando a tela
  (respiro nas bordas), com swipe/setas navegando entre as peças e os textos da peça
  (legenda, identificação, características) sob a imagem.
- **item tipo "carrossel"** — carrossel DE VERDADE dentro da página (um slide por vez,
  passa pro lado e pro outro, dots + contador); a aprovação continua POR SLIDE: o
  widget de voto acompanha o slide ativo e os dots mostram o estado (verde/âmbar).
- **layout "documento"** — coluna única com imagem/bloco em tamanho grande, para
  ARTEFATOS DE MARCA (direções de logo, specimen de tipografia, paleta, blocos de
  manual). Post-wall NÃO serve para esses artefatos — usar documento.
- **--html** — injeta os widgets numa página existente (ex.: manual da marca web
  marcado com data-aprovacao) — o formato do artefato é a própria página.

Modos (exatamente um):

1) --spec review.json — a ferramenta monta a página a partir de um spec:

       {
         "titulo": "Peças de Instagram — rodada 1",
         "layout": "mural",                       # mural (default) | documento
         "itens": [
           {"id": "feed-01", "tipo": "imagem", "titulo": "Feed 01 — Sinais de alerta",
            "arquivo": "outputs/.../05-finais/feed-01.png",
            "descricao": "opcional — aparece no card",
            "legenda": "opcional — aparece no lightbox (default: descricao)",
            "detalhes": "opcional — características, no lightbox (ex.: feed 4:5 · foto real)"},
           {"id": "carrossel-mitos", "tipo": "carrossel", "titulo": "Carrossel — Mitos",
            "descricao": "opcional",
            "slides": [
              {"arquivo": ".../carrossel-capa.png", "titulo": "Capa", "legenda": "..."},
              {"arquivo": ".../carrossel-02.png"},          # titulo default: "Slide N"
              {"arquivo": ".../carrossel-03.png", "id": "opcional"}
            ]},
           {"id": "legenda", "tipo": "texto", "titulo": "Legenda do post",
            "conteudo": "Primeiro parágrafo...\\n\\nSegundo parágrafo..."},
           {"id": "bloco", "tipo": "html", "titulo": "Bloco do manual", "arquivo": "trecho.html"}
         ]
       }

   tipo "imagem":    exige "arquivo" (servida via GET /asset/<id>).
   tipo "carrossel": exige "slides" (≥2, cada um com "arquivo"); cada slide é UM item
                     de aprovação (id default "<id>-NN", título "<título> — Slide N").
   tipo "html":      fragmento embutido num container — por "conteudo" ou "arquivo".
   tipo "texto":     parágrafos — por "conteudo" ou "arquivo".
   Caminhos de "arquivo": absolutos, relativos ao cwd OU relativos ao diretório do
   próprio spec (tentados nessa ordem). "id" duplicado no spec = erro na subida.

2) --html pagina.html — serve a página dada (e os assets relativos ao diretório dela)
   injetando o widget de aprovação logo após a abertura de cada elemento marcado:

       <section data-aprovacao="capitulo-logo" data-titulo="Logo"> ... </section>

   Título do widget = atributo data-titulo (senão o próprio id). O rodapé fixo e o JS
   são injetados automaticamente. Página sem nenhum data-aprovacao = erro na subida.

Exemplos:

    uv run tools/aprovacao.py --spec review.json --out feedback.json
    uv run tools/aprovacao.py --html manual-da-marca/index.html --out fb.json --porta 9000
    uv run tools/aprovacao.py --spec review.json --out fb.json --no-open   # só imprime a URL

Feedback gravado no --out (UTF-8) — slides de carrossel entram como itens normais:

    {"status": "aprovado" | "com-ajustes",       # aprovado = zero reprovados
     "concluido_em": "<ISO>",
     "titulo": "...",
     "itens": [{"id": "...", "titulo": "...",
                "voto": "aprovado" | "reprovado", "comentario": "..."}],
     "comentario_geral": "..."}               # observações transversais (pode ser "")

Rotas: GET / (página) · GET/POST /estado (estado vivo do formulário — reload da página
restaura) · POST /concluir (valida a regra dura; pendência = 400 com a lista e o
servidor segue vivo; ok = grava o --out, responde página de encerramento com tentativa
de window.close(), imprime o resumo e encerra com exit 0) · GET /asset/<id> (modo spec)
· demais paths = arquivos estáticos do diretório da página (modo --html).

Uso pela agência (Claude Code): rodar via Bash com run_in_background=true e AGUARDAR a
notificação de término do processo — o servidor fica vivo (sem timeout próprio) até o
cliente clicar em "Pronto" (exit 0) ou o processo ser interrompido (Ctrl+C / SIGINT →
mensagem limpa, exit 130, nada gravado). Terminou: ler o JSON do --out, aplicar os
ajustes pedidos e reabrir nova rodada de aprovação com as peças corrigidas.

    uv run tools/aprovacao.py --spec outputs/<job>/06-revisao/review.json \\
        --out outputs/<job>/06-revisao/feedback-r1.json          # run_in_background
"""

import argparse
import datetime as dt
import html
import json
import mimetypes
import re
import signal
import sys
import threading
import webbrowser
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _pagina_web as ui

PORTA_BASE = 8765
FONTES = ui.FONTES

# ---------------------------------------------------------------------------
# CSS / JS (estáticos — sem f-string para não brigar com as chaves)
# ---------------------------------------------------------------------------

CSS_SHELL = ui.CSS_BASE + ui.CSS_LIGHTBOX + ui.CSS_CARROSSEL + """
body{padding:0 0 130px}
main{max-width:1240px;margin:0 auto;padding:14px 20px 40px}
main.apv-mural{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(340px,100%),1fr));
  gap:20px;align-items:start}
main.apv-doc{display:block;max-width:960px}
main.apv-doc .apv-card{margin:0 0 24px}
main.apv-doc .apv-conteudo img{display:block;margin:0 auto;width:auto;max-width:100%;
  max-height:78vh}
.apv-card{background:#fff;border:1px solid #e6e9ee;border-radius:16px;
  padding:clamp(14px,2.4vw,20px);box-shadow:0 1px 3px rgba(15,23,42,.05)}
.apv-card-full{grid-column:1/-1}
.apv-card h2{margin:0 0 4px;font-size:19px;letter-spacing:-.01em}
.apv-desc{margin:0 0 14px;color:#5c6675;font-size:14.5px}
.apv-conteudo img{display:block;max-width:100%;height:auto;border-radius:12px;
  border:1px solid #e6e9ee;box-shadow:0 2px 10px rgba(15,23,42,.07)}
.apv-embed{border:1px solid #e6e9ee;border-radius:12px;padding:8px;overflow:auto;background:#fff}
.apv-texto p{margin:0 0 12px;font-size:15.5px;line-height:1.6;color:#2a3442}
.apv-texto p:last-child{margin-bottom:0}
.apv-slide-painel[hidden]{display:none}
"""

CSS_WIDGET = """
.apv-widget{box-sizing:border-box;margin:14px 0 6px;padding:14px 16px;border:1px solid #e3e6eb;
  border-radius:12px;background:#fafbfc;font-family:""" + FONTES + """;
  font-size:15px;line-height:1.45;color:#25303e;text-align:left}
.apv-widget-head{font-size:13px;color:#6b7583;margin:0 0 10px}
.apv-widget-head strong{color:#25303e}
.apv-botoes{display:flex;gap:8px;flex-wrap:wrap}
.apv-btn{appearance:none;-webkit-appearance:none;border:1.5px solid #d4d9e0;background:#fff;
  border-radius:999px;padding:9px 18px;font-family:inherit;font-size:15px;font-weight:600;
  color:#39424e;cursor:pointer;transition:border-color .12s ease,background .12s ease}
.apv-btn:hover{border-color:#9aa4b1}
.apv-btn-sim.apv-ativo{background:#e5f7ec;border-color:#18914f;color:#0d5c31}
.apv-btn-nao.apv-ativo{background:#fdf0d4;border-color:#c07f18;color:#7a4c07}
.apv-comentario{box-sizing:border-box;display:block;width:100%;margin-top:10px;min-height:64px;
  padding:10px 12px;border:1px solid #d4d9e0;border-radius:10px;font-family:inherit;
  font-size:14.5px;color:#25303e;background:#fff;resize:vertical}
.apv-comentario:focus{outline:2px solid #bcc9f5;border-color:#8298e9}
.apv-falta{display:none;margin-top:8px;font-size:13px;font-weight:600;color:#c62828}
.apv-widget.apv-pendente{border-color:#e05252;box-shadow:0 0 0 3px rgba(224,82,82,.14)}
.apv-widget.apv-pendente .apv-falta{display:block}
#apv-rodape{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;display:flex;
  align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;
  padding:12px clamp(14px,4vw,28px);background:rgba(255,255,255,.94);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-top:1px solid #e3e6eb;
  box-shadow:0 -6px 20px rgba(15,23,42,.06);font-family:""" + FONTES + """}
#apv-info{display:flex;flex-direction:column;gap:2px;min-width:0}
#apv-contador{font-size:14px;font-weight:700;color:#25303e}
#apv-msg{font-size:12.5px;color:#c62828;max-width:64ch}
#apv-concluir{appearance:none;-webkit-appearance:none;border:none;border-radius:999px;
  padding:12px 22px;font-family:inherit;font-size:15px;font-weight:700;cursor:pointer;
  background:#18914f;color:#fff;box-shadow:0 2px 8px rgba(24,145,79,.35);transition:background .15s ease}
#apv-concluir:hover{background:#0f7a40}
#apv-concluir.apv-travado{background:#e4e7ec;color:#98a1ad;box-shadow:none;cursor:not-allowed}
.apv-geral-bloco{max-width:900px;margin:8px auto 0;padding:clamp(16px,3vw,24px) 20px;
  border:1px dashed #cfd5dd;border-radius:14px;background:#fff;text-align:left;
  font-family:""" + FONTES + """}
.apv-geral-titulo{display:block;font-size:16px;font-weight:700;color:#25303e;margin:0 0 4px}
.apv-geral-sub{margin:0 0 10px;font-size:13.5px;color:#6b7583}
.apv-geral-txt{box-sizing:border-box;display:block;width:100%;min-height:80px;padding:10px 12px;
  border:1px solid #d4d9e0;border-radius:10px;font-family:inherit;font-size:14.5px;
  color:#25303e;background:#fff;resize:vertical}
.apv-geral-txt:focus{outline:2px solid #bcc9f5;border-color:#8298e9}
"""

# padding extra para o rodapé fixo não cobrir o fim de páginas alheias (modo --html)
CSS_INJETADO_EXTRA = "\nbody{padding-bottom:130px !important}\n"

JS_APROVACAO = """
(function () {
  "use strict";
  var widgets = Array.prototype.slice.call(document.querySelectorAll(".apv-widget"));
  var total = widgets.length;
  var timer = null;

  function porId(id) {
    for (var i = 0; i < widgets.length; i++)
      if (widgets[i].dataset.apvId === id) return widgets[i];
    return null;
  }
  function estadoAtual() {
    var itens = {};
    widgets.forEach(function (w) {
      itens[w.dataset.apvId] = {
        voto: w.dataset.apvVoto || null,
        comentario: w.querySelector(".apv-comentario").value
      };
    });
    var geral = document.getElementById("apv-geral");
    return { itens: itens, comentario_geral: geral ? geral.value : "" };
  }
  function salvar() {
    clearTimeout(timer);
    fetch("/estado", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(estadoAtual()) }).catch(function () {});
  }
  function salvarDepois() { clearTimeout(timer); timer = setTimeout(salvar, 400); }

  function pendencias() {
    var lista = [];
    widgets.forEach(function (w) {
      var voto = w.dataset.apvVoto || null;
      var coment = w.querySelector(".apv-comentario").value.trim();
      if (!voto) lista.push({ id: w.dataset.apvId, falta: "voto" });
      else if (voto === "reprovado" && !coment) lista.push({ id: w.dataset.apvId, falta: "comentario" });
    });
    return lista;
  }

  function sincronizarDots() {
    widgets.forEach(function (w) {
      if (!w.dataset.apvCar) return;
      var car = document.getElementById(w.dataset.apvCar);
      if (!car) return;
      var dot = car.querySelectorAll(".car-dot")[parseInt(w.dataset.apvSlide, 10)];
      if (!dot) return;
      dot.classList.toggle("car-dot-sim", w.dataset.apvVoto === "aprovado");
      dot.classList.toggle("car-dot-nao", w.dataset.apvVoto === "reprovado");
    });
  }

  function atualizar() {
    var votados = 0;
    widgets.forEach(function (w) { if (w.dataset.apvVoto) votados++; });
    var cont = document.getElementById("apv-contador");
    if (cont) cont.textContent = votados + " de " + total + " revisados";
    var pend = pendencias();
    var btn = document.getElementById("apv-concluir");
    btn.classList.toggle("apv-travado", pend.length > 0);
    btn.setAttribute("aria-disabled", pend.length > 0 ? "true" : "false");
    widgets.forEach(function (w) {
      var aindaPende = pend.some(function (p) { return p.id === w.dataset.apvId; });
      if (!aindaPende) w.classList.remove("apv-pendente");
    });
    if (!pend.length) {
      var m = document.getElementById("apv-msg");
      if (m) m.textContent = "";
    }
    sincronizarDots();
  }

  function revelar(w) {
    // widget de slide de carrossel: ativa o slide antes de rolar até ele
    if (w.dataset.apvCar && window.__car && window.__car[w.dataset.apvCar])
      window.__car[w.dataset.apvCar].irPara(parseInt(w.dataset.apvSlide, 10));
  }

  function apontar(pend) {
    var nomes = [];
    pend.forEach(function (p) {
      var w = porId(p.id);
      if (!w) return;
      w.classList.add("apv-pendente");
      w.querySelector(".apv-falta").textContent = p.falta === "voto"
        ? "Falta votar este item."
        : "O 👎 pede um comentário: o que ajustar?";
      nomes.push(w.dataset.apvTitulo + (p.falta === "comentario" ? " (comentário do 👎)" : ""));
    });
    var m = document.getElementById("apv-msg");
    if (m) m.textContent = "Falta revisar: " + nomes.join(" · ");
    var alvo = pend.length ? porId(pend[0].id) : null;
    if (alvo) {
      revelar(alvo);
      alvo.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  widgets.forEach(function (w) {
    w.querySelectorAll(".apv-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        w.dataset.apvVoto = btn.dataset.voto;
        w.querySelectorAll(".apv-btn").forEach(function (b) {
          var ativo = b === btn;
          b.classList.toggle("apv-ativo", ativo);
          b.setAttribute("aria-pressed", ativo ? "true" : "false");
        });
        atualizar();
        salvar();
      });
    });
    var ta = w.querySelector(".apv-comentario");
    ta.addEventListener("input", function () { atualizar(); salvarDepois(); });
    ta.addEventListener("change", salvar);
  });

  // carrossel: o painel de voto acompanha o slide ativo
  Array.prototype.slice.call(document.querySelectorAll(".apv-car-widgets")).forEach(function (bloco) {
    var car = document.getElementById(bloco.dataset.car);
    if (!car) return;
    var paineis = Array.prototype.slice.call(bloco.querySelectorAll(".apv-slide-painel"));
    car.addEventListener("car:mudou", function (ev) {
      paineis.forEach(function (p, j) { p.hidden = j !== ev.detail.indice; });
    });
  });

  var geralTa = document.getElementById("apv-geral");
  if (geralTa) {
    geralTa.addEventListener("input", salvarDepois);
    geralTa.addEventListener("change", salvar);
  }

  document.getElementById("apv-concluir").addEventListener("click", function () {
    var pend = pendencias();
    if (pend.length) { apontar(pend); return; }
    fetch("/concluir", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(estadoAtual()) })
      .then(function (r) { return r.text().then(function (t) { return { ok: r.ok, texto: t }; }); })
      .then(function (res) {
        if (res.ok) { document.open(); document.write(res.texto); document.close(); return; }
        try {
          var erro = JSON.parse(res.texto);
          if (erro && erro.pendencias) { apontar(erro.pendencias); return; }
        } catch (e) {}
        var m = document.getElementById("apv-msg");
        if (m) m.textContent = "Não foi possível concluir — tente novamente.";
      })
      .catch(function () {
        var m = document.getElementById("apv-msg");
        if (m) m.textContent = "Falha de conexão com o servidor local.";
      });
  });

  fetch("/estado", { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var itens = (data && data.itens) || {};
      widgets.forEach(function (w) {
        var it = itens[w.dataset.apvId];
        if (!it) return;
        if (it.comentario) w.querySelector(".apv-comentario").value = it.comentario;
        if (it.voto === "aprovado" || it.voto === "reprovado") {
          w.dataset.apvVoto = it.voto;
          w.querySelectorAll(".apv-btn").forEach(function (b) {
            var ativo = b.dataset.voto === it.voto;
            b.classList.toggle("apv-ativo", ativo);
            b.setAttribute("aria-pressed", ativo ? "true" : "false");
          });
        }
      });
      var g = document.getElementById("apv-geral");
      if (g && data && typeof data.comentario_geral === "string") g.value = data.comentario_geral;
      atualizar();
    })
    .catch(function () { atualizar(); });
})();
"""

PAGINA_FIM = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revisão concluída</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:#f2f4f7;font-family:""" + FONTES + """}
.fim{text-align:center;background:#fff;border:1px solid #e6e9ee;border-radius:18px;
  padding:44px 48px;margin:20px;box-shadow:0 4px 20px rgba(15,23,42,.08)}
.fim .icone{font-size:44px}
.fim h1{margin:12px 0 6px;font-size:24px;color:#1e2836}
.fim p{margin:0;color:#5c6675;font-size:15px}
</style></head>
<body><div class="fim"><div class="icone">✅</div><h1>Obrigado!</h1>
<p>Feedback registrado. Pode fechar esta aba.</p></div>
<script>setTimeout(function(){try{window.close()}catch(e){}},900);</script>
</body></html>"""


# ---------------------------------------------------------------------------
# HTML dos widgets / rodapé
# ---------------------------------------------------------------------------

def montar_widget(iid, titulo, extras=""):
    e = html.escape
    return (
        f'<div class="apv-widget" data-apv-id="{e(iid)}" data-apv-titulo="{e(titulo)}"{extras}>'
        f'<div class="apv-widget-head">Sua avaliação · <strong>{e(titulo)}</strong></div>'
        '<div class="apv-botoes">'
        '<button type="button" class="apv-btn apv-btn-sim" data-voto="aprovado" aria-pressed="false">👍 Aprovar</button>'
        '<button type="button" class="apv-btn apv-btn-nao" data-voto="reprovado" aria-pressed="false">👎 Ajustar</button>'
        '</div>'
        '<textarea class="apv-comentario" placeholder="Comentários / o que ajustar" '
        'aria-label="Comentários / o que ajustar"></textarea>'
        '<div class="apv-falta"></div>'
        '</div>'
    )


def montar_rodape(n_itens):
    return (
        '<div id="apv-rodape"><div id="apv-info">'
        f'<span id="apv-contador">0 de {n_itens} revisados</span>'
        '<span id="apv-msg"></span></div>'
        '<button id="apv-concluir" class="apv-travado" type="button" aria-disabled="true">'
        '✅ Pronto — tudo revisado</button></div>'
    )


def montar_comentario_geral():
    """Bloco de comentário geral (opcional) no fim da página — observações que não são
    de uma peça específica. NÃO entra na validação (não trava a conclusão)."""
    return (
        '<section class="apv-geral-bloco">'
        '<label class="apv-geral-titulo" for="apv-geral">Comentário geral (opcional)</label>'
        '<p class="apv-geral-sub">Observações que valem para tudo — direção, paleta, tom — '
        'e não são de uma peça específica.</p>'
        '<textarea id="apv-geral" class="apv-geral-txt" '
        'placeholder="Escreva aqui qualquer observação geral…" '
        'aria-label="Comentário geral"></textarea>'
        '</section>'
    )


# ---------------------------------------------------------------------------
# Modo 1 — spec JSON
# ---------------------------------------------------------------------------

def _campo(bruto, chave):
    valor = bruto.get(chave)
    return str(valor) if valor else ""


def carregar_spec(caminho):
    """Valida o spec e devolve (titulo, layout, itens_render, votaveis, assets)."""
    if not caminho.exists():
        sys.exit(f"[erro] spec não encontrado: {caminho}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.exit(f"[erro] spec inválido (JSON): {e}")
    if not isinstance(dados, dict) or not isinstance(dados.get("itens"), list) or not dados["itens"]:
        sys.exit('[erro] spec precisa de {"itens": [...]} com pelo menos 1 item.')

    layout = str(dados.get("layout") or "mural").strip().lower()
    if layout not in ("mural", "documento"):
        sys.exit(f'[erro] layout "{layout}" inválido (use mural | documento).')

    spec_dir = caminho.resolve().parent
    itens_render, votaveis, assets, vistos = [], [], {}, set()

    def registrar_arquivo(iid, bruto_arquivo, contexto):
        alvo = ui.resolver_caminho(bruto_arquivo, spec_dir)
        if alvo is None:
            sys.exit(f"[erro] {contexto}: arquivo não encontrado: {bruto_arquivo} "
                     f"(tentei absoluto, cwd e {spec_dir}).")
        assets[iid] = alvo

    for i, bruto in enumerate(dados["itens"], 1):
        if not isinstance(bruto, dict):
            sys.exit(f"[erro] item #{i} do spec não é um objeto JSON.")
        iid = str(bruto.get("id") or "").strip()
        if not iid:
            sys.exit(f"[erro] item #{i} do spec sem \"id\".")
        if iid in vistos:
            sys.exit(f"[erro] id duplicado no spec: \"{iid}\" — cada item precisa de id único.")
        vistos.add(iid)

        titulo = str(bruto.get("titulo") or iid)
        descricao = _campo(bruto, "descricao")
        tipo = str(bruto.get("tipo") or "").strip().lower()
        if tipo not in ("imagem", "carrossel", "html", "texto"):
            sys.exit(f"[erro] item \"{iid}\": tipo \"{tipo}\" inválido "
                     "(use imagem | carrossel | html | texto).")

        item = {"id": iid, "titulo": titulo, "descricao": descricao, "tipo": tipo}

        if tipo == "imagem":
            arquivo = bruto.get("arquivo")
            if not arquivo:
                sys.exit(f"[erro] item \"{iid}\" (imagem) exige \"arquivo\".")
            registrar_arquivo(iid, arquivo, f'item "{iid}"')
            item["legenda"] = _campo(bruto, "legenda") or descricao
            item["detalhes"] = _campo(bruto, "detalhes")
            votaveis.append({"id": iid, "titulo": titulo})

        elif tipo == "carrossel":
            slides_brutos = bruto.get("slides")
            if not isinstance(slides_brutos, list) or len(slides_brutos) < 2:
                sys.exit(f"[erro] item \"{iid}\" (carrossel) exige \"slides\" com pelo menos 2 slides.")
            slides = []
            for j, sb in enumerate(slides_brutos, 1):
                if not isinstance(sb, dict) or not sb.get("arquivo"):
                    sys.exit(f"[erro] item \"{iid}\": slide #{j} precisa de \"arquivo\".")
                sid = str(sb.get("id") or f"{iid}-{j:02d}").strip()
                if sid in vistos:
                    sys.exit(f"[erro] id duplicado no spec: \"{sid}\" — cada slide precisa de id único.")
                vistos.add(sid)
                stitulo = str(sb.get("titulo") or f"Slide {j}")
                registrar_arquivo(sid, sb["arquivo"], f'item "{iid}", slide #{j}')
                slides.append({
                    "id": sid,
                    "titulo": stitulo,
                    "titulo_completo": f"{titulo} — {stitulo}",
                    "legenda": _campo(sb, "legenda"),
                    "detalhes": _campo(sb, "detalhes"),
                })
                votaveis.append({"id": sid, "titulo": f"{titulo} — {stitulo}"})
            item["slides"] = slides

        else:  # html | texto
            conteudo = bruto.get("conteudo")
            if conteudo is None and bruto.get("arquivo"):
                caminho_txt = ui.resolver_caminho(bruto["arquivo"], spec_dir)
                if caminho_txt is None:
                    sys.exit(f"[erro] item \"{iid}\": arquivo não encontrado: {bruto['arquivo']} "
                             f"(tentei absoluto, cwd e {spec_dir}).")
                conteudo = caminho_txt.read_text(encoding="utf-8")
            if conteudo is None:
                sys.exit(f"[erro] item \"{iid}\" ({tipo}) exige \"conteudo\" ou \"arquivo\".")
            item["conteudo"] = str(conteudo)
            votaveis.append({"id": iid, "titulo": titulo})

        itens_render.append(item)

    return dados.get("titulo"), layout, itens_render, votaveis, assets


def _src_asset(iid):
    return f"/asset/{quote(iid, safe='')}"


def pagina_spec(titulo, layout, itens):
    e = html.escape
    cards = []
    lb_grupos = {}
    grupo_pagina = "pecas"  # imagens avulsas navegam entre si no lightbox
    lb_grupos[grupo_pagina] = []

    for item in itens:
        desc = (f'<p class="apv-desc">{e(item["descricao"])}</p>'
                if item["descricao"] else "")

        if item["tipo"] == "imagem":
            idx = len(lb_grupos[grupo_pagina])
            lb_grupos[grupo_pagina].append({
                "src": _src_asset(item["id"]),
                "titulo": item["titulo"],
                "legenda": item["legenda"],
                "detalhes": item["detalhes"],
            })
            corpo = (f'<img src="{_src_asset(item["id"])}" alt="{e(item["titulo"])}" '
                     f'data-lb-grupo="{grupo_pagina}" data-lb-i="{idx}">')
            classe = "apv-card" if layout == "mural" else "apv-card apv-card-full"
            cards.append(
                f'<section class="{classe}">'
                f'<h2>{e(item["titulo"])}</h2>{desc}'
                f'<div class="apv-conteudo">{corpo}</div>'
                f'{montar_widget(item["id"], item["titulo"])}'
                '</section>'
            )
            continue

        if item["tipo"] == "carrossel":
            dom_id = ui.dom_id_seguro(item["id"], "car")
            gid = f"car:{item['id']}"
            lb_grupos[gid] = []
            slides_html, paineis = [], []
            for j, slide in enumerate(item["slides"]):
                lb_grupos[gid].append({
                    "src": _src_asset(slide["id"]),
                    "titulo": slide["titulo_completo"],
                    "legenda": slide["legenda"],
                    "detalhes": slide["detalhes"],
                })
                slides_html.append(
                    f'<img src="{_src_asset(slide["id"])}" alt="{e(slide["titulo_completo"])}" '
                    f'data-lb-grupo="{e(gid)}" data-lb-i="{j}">'
                )
                extras = f' data-apv-car="{e(dom_id)}" data-apv-slide="{j}"'
                oculto = "" if j == 0 else " hidden"
                paineis.append(
                    f'<div class="apv-slide-painel" data-slide="{j}"{oculto}>'
                    f'{montar_widget(slide["id"], slide["titulo_completo"], extras)}'
                    '</div>'
                )
            rotulos = [s["titulo"] for s in item["slides"]]
            cards.append(
                '<section class="apv-card apv-card-full">'
                f'<h2>{e(item["titulo"])}</h2>{desc}'
                f'{ui.montar_carrossel(dom_id, slides_html, rotulos)}'
                f'<div class="apv-car-widgets" data-car="{e(dom_id)}">{"".join(paineis)}</div>'
                '</section>'
            )
            continue

        if item["tipo"] == "html":
            corpo = f'<div class="apv-embed">{item["conteudo"]}</div>'
        else:
            corpo = f'<div class="apv-texto">{ui.texto_para_html(item["conteudo"])}</div>'
        cards.append(
            '<section class="apv-card apv-card-full">'
            f'<h2>{e(item["titulo"])}</h2>{desc}'
            f'<div class="apv-conteudo">{corpo}</div>'
            f'{montar_widget(item["id"], item["titulo"])}'
            '</section>'
        )

    if not lb_grupos[grupo_pagina]:
        del lb_grupos[grupo_pagina]

    classe_main = "apv-mural" if layout == "mural" else "apv-doc"
    dica_lightbox = " Clique numa imagem para ampliar." if lb_grupos else ""
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{e(titulo)}</title>'
        f'<style>{CSS_SHELL}{CSS_WIDGET}</style></head><body>'
        f'<header class="pw-topo"><h1>{e(titulo)}</h1>'
        '<p>Revise cada item — 👍 para aprovar, 👎 + comentário para pedir ajuste — '
        f'e conclua no rodapé.{dica_lightbox}</p></header>'
        f'<main class="{classe_main}">{"".join(cards)}</main>'
        f'{montar_comentario_geral()}'
        f'{montar_rodape(sum(1 for _ in _iter_votaveis(itens)))}'
        f'{ui.montar_lightbox(lb_grupos)}'
        f'<script>{ui.JS_CARROSSEL}</script>'
        f'<script>{JS_APROVACAO}</script></body></html>'
    )


def _iter_votaveis(itens):
    for item in itens:
        if item["tipo"] == "carrossel":
            yield from item["slides"]
        else:
            yield item


# ---------------------------------------------------------------------------
# Modo 2 — injeção em página HTML existente
# ---------------------------------------------------------------------------

class _LocalizadorMarcacoes(HTMLParser):
    """Encontra o fim da tag de abertura de cada elemento com data-aprovacao."""

    def __init__(self, texto):
        super().__init__(convert_charrefs=True)
        self.texto = texto
        self.line_starts = [0]
        for idx, ch in enumerate(texto):
            if ch == "\n":
                self.line_starts.append(idx + 1)
        self.marcados = []  # (indice_pos_abertura, id, titulo)

    def _indice_absoluto(self):
        linha, coluna = self.getpos()
        return self.line_starts[linha - 1] + coluna

    def _registrar(self, attrs):
        d = dict(attrs)
        if "data-aprovacao" not in d:
            return
        inicio = self._indice_absoluto()
        tag_txt = self.get_starttag_text() or ""
        iid = (d.get("data-aprovacao") or "").strip()
        titulo = (d.get("data-titulo") or iid).strip()
        self.marcados.append((inicio + len(tag_txt), iid, titulo))

    def handle_starttag(self, tag, attrs):
        self._registrar(attrs)

    def handle_startendtag(self, tag, attrs):
        self._registrar(attrs)


def _aplicar_insercoes(texto, insercoes):
    """insercoes: [(indice, trecho)] — sort estável preserva a ordem em índices iguais."""
    partes, ultimo = [], 0
    for indice, trecho in sorted(insercoes, key=lambda par: par[0]):
        partes.append(texto[ultimo:indice])
        partes.append(trecho)
        ultimo = indice
    partes.append(texto[ultimo:])
    return "".join(partes)


def injetar_pagina(caminho):
    """Lê a página, injeta widgets/estilo/rodapé/JS. Devolve (html_final, itens)."""
    if not caminho.exists():
        sys.exit(f"[erro] página não encontrada: {caminho}")
    texto = caminho.read_text(encoding="utf-8")

    loc = _LocalizadorMarcacoes(texto)
    loc.feed(texto)
    loc.close()
    if not loc.marcados:
        sys.exit(f"[erro] {caminho.name} não tem nenhum elemento com data-aprovacao=\"<id>\" — "
                 "marque as seções que o cliente deve aprovar (ex.: "
                 "<section data-aprovacao=\"logo\" data-titulo=\"Logo\">).")

    itens, vistos, insercoes = [], set(), []
    for indice, iid, titulo in loc.marcados:
        if not iid:
            sys.exit("[erro] elemento com data-aprovacao vazio — o atributo precisa de um id.")
        if iid in vistos:
            sys.exit(f"[erro] data-aprovacao duplicado na página: \"{iid}\" — ids devem ser únicos.")
        vistos.add(iid)
        itens.append({"id": iid, "titulo": titulo or iid})
        insercoes.append((indice, montar_widget(iid, titulo or iid)))

    estilo = f"<style>{CSS_WIDGET}{CSS_INJETADO_EXTRA}</style>"
    bloco_fim = (montar_comentario_geral() + montar_rodape(len(itens))
                 + f"<script>{JS_APROVACAO}</script>")

    m_head = re.search(r"</head\s*>", texto, flags=re.I)
    if m_head:
        insercoes.append((m_head.start(), estilo))
    else:
        bloco_fim = estilo + bloco_fim  # sem <head>: estilo vai junto do bloco final

    m_body = re.search(r"</body\s*>", texto, flags=re.I)
    insercoes.append((m_body.start() if m_body else len(texto), bloco_fim))

    return _aplicar_insercoes(texto, insercoes), itens


# ---------------------------------------------------------------------------
# Estado / validação / feedback
# ---------------------------------------------------------------------------

def mesclar_estado(servidor, dados):
    """Aplica um JSON {"itens": {id: {voto, comentario}}, "comentario_geral": "..."}
    no estado em memória."""
    if not isinstance(dados, dict):
        return
    if isinstance(dados.get("comentario_geral"), str):
        servidor.comentario_geral = dados["comentario_geral"]
    itens = dados.get("itens")
    if not isinstance(itens, dict):
        return
    conhecidos = {item["id"] for item in servidor.itens}
    for iid, valor in itens.items():
        if iid not in conhecidos or not isinstance(valor, dict):
            continue
        atual = servidor.estado[iid]
        voto = valor.get("voto", atual["voto"])
        if voto not in ("aprovado", "reprovado", None):
            voto = atual["voto"]
        comentario = valor.get("comentario", atual["comentario"])
        if not isinstance(comentario, str):
            comentario = atual["comentario"]
        servidor.estado[iid] = {"voto": voto, "comentario": comentario}


def calcular_pendencias(servidor):
    pendencias = []
    for item in servidor.itens:
        registro = servidor.estado.get(item["id"], {})
        voto = registro.get("voto")
        comentario = (registro.get("comentario") or "").strip()
        if voto not in ("aprovado", "reprovado"):
            pendencias.append({"id": item["id"], "titulo": item["titulo"], "falta": "voto"})
        elif voto == "reprovado" and not comentario:
            pendencias.append({"id": item["id"], "titulo": item["titulo"], "falta": "comentario"})
    return pendencias


def montar_feedback(servidor):
    itens = []
    for item in servidor.itens:
        registro = servidor.estado[item["id"]]
        itens.append({
            "id": item["id"],
            "titulo": item["titulo"],
            "voto": registro["voto"],
            "comentario": (registro["comentario"] or "").strip(),
        })
    status = "aprovado" if all(i["voto"] == "aprovado" for i in itens) else "com-ajustes"
    return {
        "status": status,
        "concluido_em": dt.datetime.now().isoformat(timespec="seconds"),
        "titulo": servidor.titulo,
        "itens": itens,
        "comentario_geral": (servidor.comentario_geral or "").strip(),
    }


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------

class ServidorAprovacao(ThreadingHTTPServer):
    daemon_threads = True
    # atributos preenchidos no main: modo, titulo, pagina, itens, estado,
    # comentario_geral, assets, base_dir, out_path, lock, resultado


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: ServidorAprovacao

    def log_message(self, *args):  # stdout limpo — só os eventos importantes do main
        pass

    # -- helpers ------------------------------------------------------------
    def _responder(self, codigo, corpo, ctype, fechar=False):
        self.send_response(codigo)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        if fechar:
            self.send_header("Connection", "close")
            self.close_connection = True
        self.end_headers()
        self.wfile.write(corpo)

    def _html(self, codigo, texto, fechar=False):
        self._responder(codigo, texto.encode("utf-8"), "text/html; charset=utf-8", fechar)

    def _json(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self._responder(codigo, corpo, "application/json; charset=utf-8")

    def _ler_corpo_json(self):
        """Devolve (ok, dados|None). Corpo vazio = (True, None); inválido = (False, None)."""
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        if tamanho <= 0:
            return True, None
        bruto = self.rfile.read(tamanho)
        try:
            return True, json.loads(bruto.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False, None

    def _servir_arquivo(self, caminho):
        try:
            corpo = caminho.read_bytes()
        except OSError:
            self._json(404, {"erro": "não encontrado"})
            return
        ctype = mimetypes.guess_type(str(caminho))[0] or "application/octet-stream"
        if ctype.startswith("text/"):
            ctype += "; charset=utf-8"
        self._responder(200, corpo, ctype)

    # -- rotas --------------------------------------------------------------
    def do_GET(self):
        caminho = unquote(urlsplit(self.path).path)
        if caminho == "/":
            self._responder(200, self.server.pagina, "text/html; charset=utf-8")
            return
        if caminho == "/estado":
            with self.server.lock:
                copia = {iid: dict(reg) for iid, reg in self.server.estado.items()}
                geral = self.server.comentario_geral
            self._json(200, {"itens": copia, "comentario_geral": geral})
            return
        if caminho.startswith("/asset/") and self.server.modo == "spec":
            iid = caminho[len("/asset/"):]
            alvo = self.server.assets.get(iid)
            if alvo and alvo.is_file():
                self._servir_arquivo(alvo)
            else:
                self._json(404, {"erro": f"asset desconhecido: {iid}"})
            return
        if self.server.modo == "html":  # estáticos relativos ao diretório da página
            base = self.server.base_dir
            alvo = (base / caminho.lstrip("/")).resolve()
            if alvo.is_file() and alvo.is_relative_to(base):
                self._servir_arquivo(alvo)
            else:
                self._json(404, {"erro": "não encontrado"})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self):
        caminho = urlsplit(self.path).path
        ok, dados = self._ler_corpo_json()
        if not ok:
            self._json(400, {"erro": "json-invalido", "mensagem": "Corpo não é JSON válido."})
            return

        if caminho == "/estado":
            if dados is None:
                self._json(400, {"erro": "corpo-vazio", "mensagem": "Envie o JSON do formulário."})
                return
            with self.server.lock:
                mesclar_estado(self.server, dados)
            self._json(200, {"ok": True})
            return

        if caminho == "/concluir":
            with self.server.lock:
                if dados is not None:
                    mesclar_estado(self.server, dados)
                pendencias = calcular_pendencias(self.server)
                feedback = None if pendencias else montar_feedback(self.server)
            if pendencias:
                self._json(400, {
                    "erro": "pendencias",
                    "mensagem": "Há itens sem voto ou 👎 sem comentário — revise antes de concluir.",
                    "pendencias": pendencias,
                })
                return  # servidor segue vivo
            try:
                self.server.out_path.parent.mkdir(parents=True, exist_ok=True)
                self.server.out_path.write_text(
                    json.dumps(feedback, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            except OSError as e:
                self._json(500, {"erro": "gravacao", "mensagem": f"Falha ao gravar o feedback: {e}"})
                return
            self.server.resultado = feedback
            self._html(200, PAGINA_FIM, fechar=True)
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return

        self._json(404, {"erro": "não encontrado"})


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def criar_servidor(porta_flag):
    if porta_flag:
        try:
            return ServidorAprovacao(("127.0.0.1", porta_flag), Handler)
        except OSError as e:
            sys.exit(f"[erro] porta {porta_flag} indisponível ({e.strerror or e}) — tente outra com --porta.")
    porta = PORTA_BASE
    for _ in range(200):
        try:
            return ServidorAprovacao(("127.0.0.1", porta), Handler)
        except OSError:
            porta += 1
    sys.exit(f"[erro] nenhuma porta livre entre {PORTA_BASE} e {porta}.")


def imprimir_resumo(feedback, out_path):
    aprovados = [i for i in feedback["itens"] if i["voto"] == "aprovado"]
    reprovados = [i for i in feedback["itens"] if i["voto"] == "reprovado"]
    print(f"[aprovacao] revisão concluída — status: {feedback['status']}", flush=True)
    print(f"[aprovacao] 👍 {len(aprovados)} aprovado(s) · 👎 {len(reprovados)} com ajuste(s) "
          f"· total {len(feedback['itens'])}", flush=True)
    for item in reprovados:
        print(f"[aprovacao]   👎 {item['titulo']} — “{item['comentario']}”", flush=True)
    geral = (feedback.get("comentario_geral") or "").strip()
    if geral:
        print(f"[aprovacao] 📝 comentário geral: “{geral}”", flush=True)
    print(f"[aprovacao] feedback gravado em {out_path}", flush=True)


def main():
    # Garante KeyboardInterrupt mesmo quando o processo herda SIGINT ignorado
    # (caso comum ao rodar em background por shell não-interativo).
    signal.signal(signal.SIGINT, signal.default_int_handler)
    for stream in (sys.stdout, sys.stderr):  # acentos/emoji sempre saem
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="Página local de aprovação: cliente vota 👍/👎 por item, comenta e conclui; "
                    "o feedback é gravado em JSON e o processo encerra.")
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--spec", type=Path, help="review.json com os itens a aprovar")
    modo.add_argument("--html", type=Path, help="página HTML com elementos data-aprovacao=\"<id>\"")
    ap.add_argument("--out", type=Path, required=True, help="arquivo JSON de feedback a gravar")
    ap.add_argument("--titulo", help="título da página (default: do spec ou nome do arquivo)")
    ap.add_argument("--porta", type=int, help=f"porta fixa (default: {PORTA_BASE}, incrementando até achar livre)")
    ap.add_argument("--open", action=argparse.BooleanOptionalAction, default=True,
                    help="abrir o navegador automaticamente (--no-open desliga)")
    args = ap.parse_args()

    if args.spec:
        titulo_spec, layout, itens_render, votaveis, assets = carregar_spec(args.spec)
        titulo = args.titulo or titulo_spec or args.spec.stem
        pagina = pagina_spec(titulo, layout, itens_render)
        itens = votaveis
        modo_ativo, base_dir = "spec", None
    else:
        titulo = args.titulo or args.html.name
        pagina, itens = injetar_pagina(args.html)
        assets, modo_ativo = {}, "html"
        base_dir = args.html.resolve().parent

    servidor = criar_servidor(args.porta)
    servidor.modo = modo_ativo
    servidor.titulo = titulo
    servidor.pagina = pagina.encode("utf-8")
    servidor.itens = itens
    servidor.estado = {item["id"]: {"voto": None, "comentario": ""} for item in itens}
    servidor.comentario_geral = ""
    servidor.assets = assets
    servidor.base_dir = base_dir
    servidor.out_path = args.out
    servidor.lock = threading.Lock()
    servidor.resultado = None

    url = f"http://127.0.0.1:{servidor.server_address[1]}"
    print(f"[aprovacao] “{titulo}” — {len(itens)} item(ns) para revisar", flush=True)
    print(f"[aprovacao] servindo em {url} (Ctrl+C cancela sem gravar)", flush=True)

    abriu = False
    if args.open:
        try:
            abriu = webbrowser.open(url)
        except Exception:
            abriu = False
    if not abriu:
        print(f"Abra no navegador: {url}", flush=True)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[aprovacao] interrompido (Ctrl+C) — nenhum feedback foi gravado.", flush=True)
        sys.exit(130)
    finally:
        servidor.server_close()

    if servidor.resultado is not None:
        imprimir_resumo(servidor.resultado, args.out)
    sys.exit(0)


if __name__ == "__main__":
    main()
