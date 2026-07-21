# tools — ferramentas mínimas de produção

Scripts autossuficientes (PEP 723): rodar com `uv run tools/<script>.py` — o uv resolve
as dependências sozinho, sem venv. Alternativa: `pip install -r tools/requirements.txt`.

| Script | Faz | Uso típico |
|---|---|---|
| `compose.py` | Compõe a peça final: canvas + fundo + camadas — texto com as fontes reais (inclui headline multicolorida por linha), fotos, `rect`/`circle`, `blob` (forma orgânica de canto), `dots` (dot grid), `badge` (pill), `bubble` (balão de fala), `icon` (Lucide, com círculo de fundo opcional). Defaults visuais da marca em `brand/tema-visual.json`. Presets de todos os formatos, incluindo impressos 300dpi. | `uv run tools/compose.py spec.json --out final.png [--pdf]` |
| `generate_image.py` | Gera imagens na OpenAI (modelo configurável via `.env`, padrão `gpt-image-2`). Salva sidecar `.prompt.json`. Suporta referências (`--ref`) e fundo transparente. | `uv run tools/generate_image.py --prompt "..." --out 04-imagens/ --name conceito -n 2` |
| `entrega.py` | **Página de entrega do job** (TODA entrega fecha com ela): HTML estático que se molda ao artefato — imagens = post-wall + lightbox, carrossel = carrossel real, texto = página formatada + copiar, PDF = preview + download, vídeo/áudio = player, site = card com link. Botões Lucide outlined. | `uv run tools/entrega.py outputs/<job>/entrega.json` |
| `aprovacao.py` | Página local de aprovação do cliente (👍/👎 + comentário por item, servidor 127.0.0.1, feedback em JSON). Formato segue o artefato: `layout mural` (peças, com lightbox), item `carrossel` (voto por slide), `layout documento` (artefatos de marca), `--html` (manual web). | `uv run tools/aprovacao.py --spec review.json --out feedback.json` |
| `vectorize.py` | Vetoriza PNG→SVG (acabamento de logo orgânico): upscale automático, cores achatadas, halo aparado; gate de fidelidade de silhueta (IoU) + `-compare.png` para curadoria das curvas. | `uv run tools/vectorize.py logo.png --out logo.svg` |
| `font_specimen.py` | Mural numerado de fontes de título com o nome da marca renderizado (o cliente escolhe por número na aprovação). | `uv run tools/font_specimen.py --text "Marca" --out fontes.png --limit 10` |
| `fetch_font_catalog.py` | Vendoriza o catálogo de ~16 famílias de título OFL em `assets/fontes/catalogo/` (insumo do specimen). | `uv run tools/fetch_font_catalog.py` |
| `warp_cover.py` | Aplica capa/arte real sobre a face de um livro/placa numa foto, com warp de perspectiva + QA embutido. | `uv run tools/warp_cover.py --base foto.png --cover capa.png --out saida.png` |
| `index_assets.py` | Indexa `assets/` em `data/asset-index.json` (categoria, dimensões, tags). Pula `assets/icones/` (catálogo próprio). | `uv run tools/index_assets.py` |
| `new_job.py` | Cria a pasta datada do job em `outputs/` com brief pré-preenchido. | `uv run tools/new_job.py "carrossel andador" --pedido "..."` |
| `fetch_fonts.py` | Re-baixa as fontes da marca (já vêm no repo). | `uv run tools/fetch_fonts.py` |
| `fetch_icons.py` | Vendoriza os SVGs da **Lucide** (lib oficial de ícones) em `assets/icones/lucide/`. | `uv run tools/fetch_icons.py` |
| `icon.py` | Rasteriza um ícone Lucide recolorido em PNG avulso (com círculo de fundo opcional). Em peças, preferir o layer `icon` do compose. | `uv run tools/icon.py --name baby --color "#2563EB" --size 96 --out baby.png` |
| `reset_project.py` | Motor do `/abrir-filial`: exporta o maquinário limpo (ver `reset_manifest.json`). **Exclusivo da matriz** — não viaja para filiais (`LICENSE`). | via skill `/abrir-filial` |

`_pagina_web.py` é módulo compartilhado (não é CLI): casca neutra, lightbox, carrossel,
ícones Lucide embutidos e mini-Markdown usados por `aprovacao.py` e `entrega.py` — as
duas páginas falam a mesma língua visual.

O schema completo do spec de composição está documentado no docstring de `compose.py`;
um exemplo pronto em `tools/examples/compose-exemplo.json` (renderizado em
`tools/examples/exemplo-feed-4x5.png`). Os specs de entrega e aprovação estão nos
docstrings de `entrega.py` e `aprovacao.py`.

Princípio: **nenhum orquestrador em código** — quem pensa é o Claude; os scripts só fazem
o que LLM não faz bem (pixels, índice, API).
