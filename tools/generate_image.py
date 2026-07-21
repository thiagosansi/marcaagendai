#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.60"]
# ///
"""
generate_image.py — geração de imagens via OpenAI Images API.

Modelo 100% configurável: OPENAI_IMAGE_MODEL no .env (padrão gpt-image-2) ou --model.
Salva as imagens + sidecar .prompt.json com todos os parâmetros (documentação do job).

Uso:
    uv run tools/generate_image.py --prompt "..." --out outputs/<job>/04-imagens/ --name conceito -n 2
    uv run tools/generate_image.py --prompt-file prompt.txt --ref assets/equipe/foto.jpg ...
    uv run tools/generate_image.py --prompt "..." --size 1024x1536 --quality high --transparent

Regras da casa (data/memoria-visual.md):
- Texto dentro da imagem: apenas rótulos educativos, SEMPRE entre aspas no prompt.
- Rosto de pessoa real nunca inventado do zero — composição/retoque fiel via --ref com
  gate de identidade obrigatório depois. (O tool tenta input_fidelity=high; modelos que
  não aceitam o parâmetro — ex.: gpt-image-2 — caem no fallback automático.)
- Elemento REAL do mundo (produto do cliente, monumento, cidade, pessoa pública): gerar
  com --ref da referência real (acervo assets/referencias-reais/), NUNCA de cabeça e
  NUNCA distorcendo o real (tocha, cor, proporção, rótulo, fisionomia). Referência da
  internet é estudo/insumo de --ref — nunca publicada na íntegra (direitos autorais).
- Bebês/crianças genéricos hiper-realistas: permitidos no educativo (contexto digno).
"""

import argparse
import base64
import datetime as dt
import json
import mimetypes
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    load_env()
    ap = argparse.ArgumentParser(description="Gera imagens via OpenAI Images API.")
    ap.add_argument("--prompt", help="prompt de geração")
    ap.add_argument("--prompt-file", help="arquivo com o prompt")
    ap.add_argument("--model", default=os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2"),
                    help="modelo (padrão: $OPENAI_IMAGE_MODEL ou gpt-image-2)")
    ap.add_argument("--size", default=os.environ.get("OPENAI_IMAGE_SIZE", "auto"),
                    help="ex.: 1024x1024, 1024x1536, 1536x1024, auto")
    ap.add_argument("--quality", default=os.environ.get("OPENAI_IMAGE_QUALITY", "auto"),
                    help="low | medium | high | auto")
    ap.add_argument("-n", type=int, default=1, help="número de variações")
    ap.add_argument("--out", default=".", help="pasta de saída")
    ap.add_argument("--name", default="imagem", help="nome-base dos arquivos")
    ap.add_argument("--ref", action="append", default=[],
                    help="imagem de referência (repetir para várias) — usa endpoint de edição")
    ap.add_argument("--input-fidelity", choices=["high", "low", "off"], default="high",
                    help="fidelidade a rostos/detalhes da referência em edições (padrão: high; "
                         "'off' não envia o parâmetro)")
    ap.add_argument("--transparent", action="store_true", help="fundo transparente (se o modelo suportar)")
    args = ap.parse_args()

    prompt = args.prompt or (Path(args.prompt_file).read_text(encoding="utf-8").strip()
                             if args.prompt_file else None)
    if not prompt:
        sys.exit("[erro] informe --prompt ou --prompt-file")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("[erro] OPENAI_API_KEY ausente — copie .env.example para .env e preencha. "
                 "Enquanto isso, salve o prompt em 03-visual/prompts.md e siga o job.")

    try:
        from openai import OpenAI, BadRequestError
    except ImportError:
        sys.exit("[erro] pacote openai não instalado — rode via `uv run tools/generate_image.py ...`")

    client = OpenAI()
    kwargs = {"model": args.model, "prompt": prompt, "n": args.n}
    if args.size and args.size != "auto":
        kwargs["size"] = args.size
    if args.quality and args.quality != "auto":
        kwargs["quality"] = args.quality
    if args.transparent:
        kwargs["background"] = "transparent"
    if args.ref and args.input_fidelity != "off":
        kwargs["input_fidelity"] = args.input_fidelity  # preserva rosto/figurino da referência

    def call(k):
        if args.ref:
            files = [open(ROOT / r if not Path(r).is_absolute() else r, "rb") for r in args.ref]
            try:
                return client.images.edit(image=files if len(files) > 1 else files[0], **k)
            finally:
                for f in files:
                    f.close()
        return client.images.generate(**k)

    try:
        result = call(kwargs)
    except BadRequestError as e:
        # parâmetro opcional não suportado pelo modelo -> tenta sem os opcionais
        slim = {k: v for k, v in kwargs.items() if k in ("model", "prompt", "n", "size")}
        if slim != kwargs:
            print(f"[aviso] modelo recusou parâmetros opcionais ({e.message if hasattr(e, 'message') else e}); "
                  f"tentando sem quality/background…")
            result = call(slim)
            kwargs = slim
        else:
            sys.exit(f"[erro] API recusou a chamada: {e}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, item in enumerate(result.data, start=1):
        raw = None
        if getattr(item, "b64_json", None):
            raw = base64.b64decode(item.b64_json)
        elif getattr(item, "url", None):
            with urllib.request.urlopen(item.url) as resp:
                raw = resp.read()
        if raw is None:
            print(f"[aviso] item {i} sem dados de imagem — pulando")
            continue
        path = out_dir / f"{args.name}-{i:02d}.png"
        path.write_bytes(raw)
        saved.append(str(path))
        print(f"[ok] {path}")

    sidecar = out_dir / f"{args.name}.prompt.json"
    sidecar.write_text(json.dumps({
        "prompt": prompt,
        "model": kwargs.get("model"),
        "size": kwargs.get("size", "auto"),
        "quality": kwargs.get("quality", "auto"),
        "background": kwargs.get("background"),
        "input_fidelity": kwargs.get("input_fidelity"),
        "n": args.n,
        "refs": args.ref,
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "arquivos": saved,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] {sidecar}")


if __name__ == "__main__":
    main()
