#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
fetch_font_catalog.py — vendoriza um CATÁLOGO curado de fontes de TÍTULO (OFL) em
assets/fontes/catalogo/, para o gerador de specimens (tools/font_specimen.py).

Diferente de fetch_fonts.py (que só repõe as 3 fontes DEFAULT do harness em uso),
este baixa um leque de ~15 famílias de título cobrindo o espectro de personalidade
(serifadas editoriais, sans geométricas, humanistas, display com caráter, condensadas,
arredondadas). O catálogo alimenta as "~10 sugestões de fonte com exemplo" da imersão
sem download em runtime — a escolha da marca continua sendo curada pela pesquisa.

O catálogo é MAQUINÁRIO (fontes genéricas, não é conteúdo de marca) → segue no export.
Adicionar/remover famílias: editar CATALOGO abaixo. Cada OFL.txt acompanha a fonte.

Uso:
    uv run tools/fetch_font_catalog.py
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "fontes" / "catalogo"
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"

# (slug no google/fonts, arquivo dentro de ofl/<slug>/, rótulo humano da família)
# ORDEM CURADA por personalidade: as 10 PRIMEIRAS cobrem o espectro (serif editorial →
# geométrica → contemporânea → display → condensada → arredondada), então o `--limit 10`
# padrão do specimen entrega VARIEDADE, não a fatia alfabética. As 6 seguintes são extras
# (aparecem com --limit maior ou --fonts curado pela pesquisa). Variáveis quando possível.
# NÃO inclui a fonte-identidade da marca-matriz (essa fica só na matriz): a filial não
# herda identidade de marca como candidata; a personalidade "arredondada" fica com Fredoka.
CATALOGO = [
    ("playfairdisplay", "PlayfairDisplay[wght].ttf", "Playfair Display"),  # serifada editorial clássica
    ("dmserifdisplay", "DMSerifDisplay-Regular.ttf", "DM Serif Display"),  # serifada display alto contraste
    ("fraunces", "Fraunces[SOFT,WONK,opsz,wght].ttf", "Fraunces"),         # serifada moderna macia
    ("montserrat", "Montserrat[wght].ttf", "Montserrat"),                  # geométrica versátil
    ("manrope", "Manrope[wght].ttf", "Manrope"),                           # humanista limpa
    ("spacegrotesk", "SpaceGrotesk[wght].ttf", "Space Grotesk"),           # geométrica com caráter tech
    ("bricolagegrotesque", "BricolageGrotesque[opsz,wdth,wght].ttf", "Bricolage Grotesque"),  # contemporânea
    ("unbounded", "Unbounded[wght].ttf", "Unbounded"),                     # display bold distinta
    ("bebasneue", "BebasNeue-Regular.ttf", "Bebas Neue"),                  # condensada caixa-alta
    ("fredoka", "Fredoka[wdth,wght].ttf", "Fredoka"),                      # arredondada amigável
    ("cormorant", "Cormorant[wght].ttf", "Cormorant"),                     # serifada fina refinada (extra)
    ("instrumentserif", "InstrumentSerif-Regular.ttf", "Instrument Serif"),  # serifada display delicada (extra)
    ("poppins", "Poppins-SemiBold.ttf", "Poppins"),                        # geométrica arredondada (extra)
    ("archivo", "Archivo[wdth,wght].ttf", "Archivo"),                      # grotesca forte (extra)
    ("sora", "Sora[wght].ttf", "Sora"),                                    # geométrica moderna (extra)
    ("outfit", "Outfit[wght].ttf", "Outfit"),                              # minimal geométrica (extra)
]


def fetch(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mkt-agency-fonts/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        return True
    except Exception as e:  # 404/rede — não derruba o lote
        print(f"[skip] {url.rsplit('/', 1)[-1]} — {e}")
        return False


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    ok, ordem = 0, []
    for slug, fname, label in CATALOGO:
        enc = urllib.parse.quote(fname, safe=".")  # []/, → %5B%5D%2C
        if fetch(f"{BASE}/{slug}/{enc}", DEST / fname):
            print(f"[ok] {label:22s} → {fname} ({round((DEST / fname).stat().st_size / 1024)} KB)")
            fetch(f"{BASE}/{slug}/OFL.txt", DEST / f"OFL-{slug}.txt")
            ordem.append(fname)
            ok += 1
    # ordem curada de exibição — o font_specimen respeita para o --limit entregar variedade
    (DEST / "_ordem.json").write_text(json.dumps(ordem, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"\n[fim] {ok}/{len(CATALOGO)} famílias em {DEST.relative_to(ROOT)} (+ _ordem.json)")


if __name__ == "__main__":
    main()
