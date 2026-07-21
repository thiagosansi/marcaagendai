#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.4"]
# ///
"""
index_assets.py — indexa o acervo de assets/ em data/asset-index.json.

O índice permite à agência consultar o acervo sem varrer pastas: categoria (pasta de
1º nível), dimensões, tamanho e tags derivadas do nome do arquivo. Rodar sempre que
assets forem adicionados/organizados.

Curadoria manual (opcional): se data/asset-tags.json existir, suas tags são mescladas
no campo `curadoria` de cada entrada correspondente (chave = campo `arquivo` do índice).
Formato: {"assets/…/foto.jpg": {"figurino": "<vocabulário da marca — ex.: uniforme|casual|social|esporte|outro>",
"figurino_cores": ["…"], "cenario": "estudio-claro|consultorio|externa|outro",
"pose": "em-pe|sentada|apoiada|movimento|closeup",
"enquadramento": "corpo-inteiro|meio-corpo|rosto", "qualidade": "boa|media|ruim"}}.
Sem o arquivo, o índice sai idêntico ao de sempre; arquivo inválido → aviso e segue.

Uso:
    uv run tools/index_assets.py
"""

import datetime as dt
import json
import unicodedata
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ROOT / "data" / "asset-index.json"
TAGS = ROOT / "data" / "asset-tags.json"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tiff", ".bmp"}
SKIP_NAMES = {".gitkeep", ".DS_Store", "README.md", "_ordem.json"}
SKIP_DIRS = {"icones"}  # SVGs da Lucide têm catálogo próprio (lucide.dev) — não poluir o índice


def tags_from_name(stem):
    norm = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    parts = norm.replace("_", "-").replace(" ", "-").lower().split("-")
    return sorted({p for p in parts if len(p) > 2 and not p.isdigit()})


def load_curadoria():
    """Tags de curadoria manual (data/asset-tags.json) — separadas das tags de nome.

    Arquivo ausente → {} (comportamento idêntico ao índice sem curadoria).
    JSON inválido ou estrutura inesperada → aviso e {} (nunca trava a indexação).
    """
    if not TAGS.exists():
        return {}
    try:
        data = json.loads(TAGS.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
            raise ValueError("esperado objeto {\"<arquivo>\": {tags...}}")
        return data
    except Exception as e:
        print(f"[aviso] {TAGS.relative_to(ROOT)} ignorado ({e}) — índice segue sem curadoria")
        return {}


def main():
    curadoria = load_curadoria()
    aplicadas = set()
    items = []
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file() or path.name in SKIP_NAMES or path.name.startswith("."):
            continue
        rel = path.relative_to(ROOT)
        rel_assets = path.relative_to(ASSETS)
        if rel_assets.parts[0] in SKIP_DIRS:
            continue
        categoria = rel_assets.parts[0]
        ext = path.suffix.lower()
        item = {
            "categoria": categoria,
            "arquivo": str(rel),
            "nome": path.stem,
            "tipo": "imagem" if ext in IMG_EXT else ("fonte" if ext in (".ttf", ".otf") else "outro"),
            "kb": round(path.stat().st_size / 1024),
            "tags": tags_from_name(path.stem),
        }
        if item["tipo"] == "imagem":
            try:
                with Image.open(path) as im:
                    w, h = im.size
                    orientation = im.getexif().get(0x0112)
                    if orientation in (5, 6, 7, 8):  # EXIF rotacionada 90°
                        w, h = h, w
                    item["largura"], item["altura"] = w, h
            except Exception:
                item["tipo"] = "outro"
        cur = curadoria.get(item["arquivo"])
        if cur:
            item["curadoria"] = cur
            aplicadas.add(item["arquivo"])
        items.append(item)

    categorias = {}
    for it in items:
        categorias[it["categoria"]] = categorias.get(it["categoria"], 0) + 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "total": len(items),
        "categorias": dict(sorted(categorias.items())),
        "itens": items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] {OUT} — {len(items)} itens")
    for cat, n in sorted(categorias.items()):
        print(f"     {cat}: {n}")
    if curadoria:
        print(f"     curadoria: {len(aplicadas)}/{len(curadoria)} entradas de {TAGS.name} mescladas")
        orfas = sorted(set(curadoria) - aplicadas)
        for o in orfas[:5]:
            print(f"     [aviso] curadoria sem asset no índice: {o}")
        if len(orfas) > 5:
            print(f"     [aviso] … e mais {len(orfas) - 5} entradas órfãs")


if __name__ == "__main__":
    main()
