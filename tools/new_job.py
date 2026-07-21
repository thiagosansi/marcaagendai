#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
new_job.py — cria a pasta de um novo job em outputs/ com o naming da casa.

Uso:
    uv run tools/new_job.py "stories caixinha respiratória" [--pedido "texto literal do pedido"]

Cria: outputs/NNNNN-AAAA-MM-DD-HHMM-stories-caixinha-respiratoria/00-brief/brief.md
NNNNN é um contador DECRESCENTE de 5 dígitos (99999, 99998, …): em qualquer listagem
A→Z (Finder, VS Code, ls) o job mais novo aparece SEMPRE no topo — pedido do fundador.
Fôlego de ~100 mil jobs (décadas). A data+hora seguem no nome para leitura. As demais
subpastas (01-estrategia, 02-conteudo, …) são criadas conforme o job usa.
"""

import argparse
import datetime as dt
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slugify(text):
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-")
    return "-".join(slug.split("-")[:6])  # slug curto


def main():
    ap = argparse.ArgumentParser(description="Cria pasta de job em outputs/.")
    ap.add_argument("titulo", help="título/slug do job")
    ap.add_argument("--pedido", default="", help="pedido literal do usuário")
    args = ap.parse_args()

    now = dt.datetime.now()
    today = now.date().isoformat()
    stamp = now.strftime("%Y-%m-%d-%H%M")
    outputs = ROOT / "outputs"
    prefixes = [int(m.group(1)) for p in outputs.iterdir()
                if p.is_dir() and (m := re.match(r"^(\d{5})-", p.name))]
    seq = (min(prefixes) - 1) if prefixes else 99999
    if seq < 0:
        import sys
        sys.exit("[erro] contador de jobs esgotado — re-baselinar os prefixos de outputs/ "
                 "(renumerar a partir de 99999) antes de criar novos jobs.")
    job = outputs / f"{seq:05d}-{stamp}-{slugify(args.titulo)}"
    if job.exists():
        print(f"[aviso] já existe: {job}")
        return
    (job / "00-brief").mkdir(parents=True)

    template = ROOT / "templates" / "brief.md"
    brief = template.read_text(encoding="utf-8") if template.exists() else "# Brief\n"
    brief = brief.replace("<título do job>", args.titulo)
    brief = brief.replace("AAAA-MM-DD", today)
    if args.pedido:
        brief = brief.replace("<como o usuário escreveu>", args.pedido)
    (job / "00-brief" / "brief.md").write_text(brief, encoding="utf-8")

    print(f"[ok] {job}")


if __name__ == "__main__":
    main()
