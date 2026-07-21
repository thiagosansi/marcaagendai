# referencias — biblioteca de pesquisa

Inteligência externa da agência (o acervo próprio fica em `assets/`).

| Pasta | O que é | Índice |
|---|---|---|
| `biblioteca-viral/` | Conteúdos que performaram: anatomia do gancho, estrutura, ritmo e **como adaptar sem copiar** (formato `templates/referencia-viral.md`) | `_index.md` |
| `concorrentes/` | Perfis do nicho e nichos irmãos: posicionamento, formatos, cadência, o que fazem bem, o que evitar | `_index.md` |
| `inspiracao-visual/` | Referências estéticas externas (direção de arte, tipografia, composição) com nota do que aproveitar | `_index.md` |

## Como as pastas são preenchidas

**1 · Sob demanda** — você pede e o agente de pesquisa (subagent `pesquisa-viral`, com
WebSearch/WebFetch) coleta, analisa e registra:

- *"Pesquise vídeos virais de <nicho da marca>"* → `biblioteca-viral/`
- *"Mapeie os concorrentes de <produto/segmento da marca>"* → `concorrentes/`
- *"Busque referências visuais de carrossel editorial de saúde premium"* → `inspiracao-visual/`

**2 · Por gatilho do pipeline** — sem você pedir, a pesquisa entra quando:

- o job depende de trend (áudio/formato do momento) e a biblioteca não tem nada recente;
- é campanha grande (benchmark antes de criar);
- o tema é novo para a casa e não há referência interna.

**3 · Por captura** — viu um Reels/perfil/arte boa por aí? Cole o link no chat com
*"guarda essa referência"* e a agência analisa e arquiva no lugar certo.

Toda entrada atualiza o `_index.md` da pasta (1 linha) — os índices são o que a agência
consulta primeiro em jobs futuros; os arquivos completos, só quando o tema é relevante.

## Formato das entradas

- **biblioteca-viral/**: usar `templates/referencia-viral.md` (link, gancho transcrito,
  estrutura, ritmo, áudio, por que funcionou, como adaptar, tags).
- **concorrentes/**: 1 arquivo por perfil — quem é, posicionamento, formatos e cadência,
  3 pontos fortes, 3 fraquezas/oportunidades para nós, o que **não** copiar, exemplos
  (links). Revisitar a cada ~3 meses (anotar data).
- **inspiracao-visual/**: 1 arquivo por referência ou coleção — link/print, o que
  exatamente aproveitar (grid? paleta? hierarquia?), onde se aplicaria na sua marca.
  Prints salvos na própria pasta.

Regra de ouro: referência é para roubar ESTRUTURA (gancho, ritmo, mecânica, grid),
nunca conteúdo. E concorrente é régua de diferenciação, não molde.
