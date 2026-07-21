#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""fetch_icons.py — vendoriza os SVGs da Lucide (lib oficial de ícones da casa).

Baixa o pacote npm `lucide-static` (tarball direto do registry, sem npm) e extrai
apenas os SVGs para assets/icones/lucide/. Rodar uma vez — depois disso o repo é
autossuficiente (icon.py e o layer "icon" do compose.py só leem do disco).

Uso:
    uv run tools/fetch_icons.py [--version X.Y.Z]
"""

import argparse
import io
import json
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "icones" / "lucide"
REGISTRY = "https://registry.npmjs.org/lucide-static"


def main():
    ap = argparse.ArgumentParser(description="Vendoriza SVGs da Lucide no repo.")
    ap.add_argument("--version", default="latest", help="versão npm (default: latest)")
    args = ap.parse_args()

    meta = json.load(urllib.request.urlopen(f"{REGISTRY}/{args.version}"))
    version, url = meta["version"], meta["dist"]["tarball"]
    print(f"[..] lucide-static {version}")
    data = urllib.request.urlopen(url).read()

    DEST.mkdir(parents=True, exist_ok=True)
    count = 0
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.name.startswith("package/icons/") and member.name.endswith(".svg"):
                (DEST / Path(member.name).name).write_bytes(tar.extractfile(member).read())
                count += 1
    (DEST / "VERSION").write_text(version + "\n", encoding="utf-8")
    print(f"[ok] {count} ícones em {DEST.relative_to(ROOT)} (v{version})")


if __name__ == "__main__":
    main()
