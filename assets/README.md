# assets — o acervo da marca

Coloque os arquivos nas pastas por contexto e peça à agência para indexar
(`uv run tools/index_assets.py` → `data/asset-index.json`).

| Pasta | O que vai aqui |
|---|---|
| `quiches/` | 156 fotos do produto principal (quiches inteiras, fatias, em caixa da marca) |
| `produtos/` | tartelettes, torta de limão, doces, embalagem |
| `equipe/` | fotos de ação de rua/degustação — **funcionária uniformizada** (uso do rosto pendente de autorização de imagem) |
| `fundadora-priscila/` | fotos da fundadora Priscila — **a enviar** (não estavam no acervo inicial) |
| `bastidores/` | preparo, cozinha, montagem |
| `loja/` | espaço físico / ambiente (vazio por ora) |
| `institucional/` | prova social — placa do prêmio "Salvador 2020 — Os Melhores da Gastronomia" |
| `referencias-antigas/` | peças prontas antigas da marca (anúncio Copa, ilustrações IA, post junino) — referência histórica, não material bruto |
| `videos/` | vídeo(s) da marca (a revisar) |
| `logos/` | logo da marca e variações (kit + mini-manual em `brand/logo.md`) |
| `fontes/` | DM Sans, Albert Sans e Fraunces variáveis (já incluídas, licenças OFL) — fontes próprias da marca entram aqui com licença conferida, papéis em `mapa-fontes.json` |
| `icones/` | Lucide vendorizado (`uv run tools/fetch_icons.py`) — a lib oficial do harness |
| `grafismos/` | selos e dispositivos-assinatura da marca (recoloríveis via `"tint"` do compose) |
| `referencias-aprovadas/` | artes NOSSAS que representam o padrão da casa |
| `referencias-rejeitadas/` | artes NOSSAS reprovadas (anti-referência — estudar o porquê) |

Fotos com crianças ou pessoas identificáveis: **somente com termo de autorização de
imagem confirmado** (regras do domínio em `brand/etica-e-saude.md`).

## Convenções de nome

Nomes descritivos em kebab-case, sem acento — viram **tags de busca** no índice:
`pessoa-contexto-cena.jpg` > `IMG_4032.jpg`.

## Importando o acervo

O acervo entra na imersão (`/imersao-na-marca`, estágio 1 — ask-first: você aponta o
que existe e a agência organiza, renomeia e indexa). Para novos lotes depois, peça:
*"importe e organize as fotos de X"*.

## Nota sobre git (decidido)

Fotos **não são versionadas** (adicionar os diretórios de foto ao `.gitignore` —
acervos pesados não cabem num repo saudável). O que o git versiona: índice de
metadados (`data/asset-index.json`), logos e fontes. Num computador novo, re-importe
dos masters e rode `uv run tools/index_assets.py`.
