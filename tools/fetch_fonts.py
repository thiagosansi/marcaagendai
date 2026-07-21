#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
fetch_fonts.py — (re)baixa as fontes default do harness (OFL) para assets/fontes/.

As fontes já vêm no repositório (licença OFL incluída); este script existe para
reparo/atualização a partir do repositório oficial google/fonts. Fontes próprias
da marca (fora deste default) são vendorizadas manualmente em assets/fontes/ e
mapeadas em mapa-fontes.json — não passam por aqui.

Uso:
    uv run tools/fetch_fonts.py
"""

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "fontes"

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FILES = [
    (f"{BASE}/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf", "DMSans-VariableFont_opsz,wght.ttf"),
    (f"{BASE}/dmsans/OFL.txt", "OFL-DMSans.txt"),
    (f"{BASE}/albertsans/AlbertSans%5Bwght%5D.ttf", "AlbertSans-VariableFont_wght.ttf"),
    (f"{BASE}/albertsans/OFL.txt", "OFL-AlbertSans.txt"),
    (f"{BASE}/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf",
     "Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf"),
    (f"{BASE}/fraunces/OFL.txt", "OFL-Fraunces.txt"),
]


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for url, name in FILES:
        dest = DEST / name
        req = urllib.request.Request(url, headers={"User-Agent": "mkt-agency-fonts/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        print(f"[ok] {dest} ({round(dest.stat().st_size / 1024)} KB)")


if __name__ == "__main__":
    main()
