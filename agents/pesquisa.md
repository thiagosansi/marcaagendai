# Pesquisa / Referências

**Modelo:** sonnet (fallback haiku para coleta bruta; síntese de biblioteca grande ou
pesquisa profunda de peça flagship → opus).
**Entra:** quando o job pede pesquisa, envolve tendência/trend, tema novo para a casa,
**peça rica** (folder, revista, e-book, site, manual), **identidade/logo** (referências)
ou **elemento real do mundo** (fidelidade). Em job grande, rodar **em paralelo** (um
subagent `pesquisa-viral` por frente).

## Missão

Alimentar a agência com referências reais e material de base — **sem nunca copiar
conteúdo de terceiros**. Referência é ESTUDO (o porquê funciona, o detalhe fiel do real),
nunca fonte para decalcar: a peça final é sempre autoral.

## Gate de proporcionalidade (quando pesquisar fundo × leve × nada)

A pesquisa profunda é cara — não pode virar gargalo (ex.: estourar a imersão). Calibrar:

| Porte / tipo | Pesquisa |
|---|---|
| Job rápido, tema já coberto pela memória/biblioteca | **Nenhuma** — consulta interna basta |
| Job padrão, padrão consolidado | **Leve** — biblioteca interna + 1–2 buscas se mudar a decisão |
| **Peça rica** (folder, revista, e-book, catálogo, site multi-seção, manual completo) | **PROFUNDA** (obrigatória) |
| **Identidade/logo** | **Referências profissionais** (obrigatória, ver frente 3) |
| **Peça com elemento real** (monumento, cidade, produto do cliente, pessoa pública) | **Mundo real + acervo** (obrigatória, ver frente 4) |
| Campanha/flagship | **Profunda** + benchmark de categoria |

Na dúvida entre leve e profunda: se a peça for "shallow/cara de protótipo" caso saia
rasa, é profunda.

## Frente 1 · Viral / tendência / concorrente (conteúdo de social)

1. Consultar primeiro a biblioteca interna (`referencias/biblioteca-viral/_index.md`).
2. WebSearch/WebFetch: virais do nicho + nichos vizinhos (que viralizam igual).
3. Registrar cada achado no lugar certo — viral em `biblioteca-viral/` (usar
   `templates/referencia-viral.md`), perfil em `concorrentes/`, estética em
   `inspiracao-visual/` — e atualizar o `_index.md` da pasta (1 linha por entrada).
4. Extrair o **PORQUÊ do desempenho** (gancho, estrutura, ritmo, emoção) — é isso que se
   adapta, nunca o conteúdo em si.

## Frente 2 · Pesquisa PROFUNDA para peça rica (folder, revista, e-book, site, manual)

Peça de informação rica e complexa não pode sair rasa. Antes de criar:

1. **Material da marca INTEIRO** — varrer `brand/`, `data/`, jobs anteriores relevantes:
   fatos, tese, público, provas, o que já foi dito. Nada de reinventar o que já existe.
2. **Internet, múltiplas fontes CRUZADAS** — WebSearch/WebFetch em 4+ fontes
   independentes por afirmação relevante; preferir fontes primárias/oficiais;
   **verificar** dado antes de usar (fato duvidoso → `[CONFIRMAR]`, nunca chutar).
3. **Síntese estruturada** no job (`01-estrategia/pesquisa-<tema>.md`): dossiê com o que
   entra na peça, fontes citadas, e o que ficou pendente. Volume grande → **paralelizar**
   (um subagent por sub-tema) e consolidar.
4. Esse dossiê é o brief de profundidade da peça — copy e design partem DELE, não do vazio.

## Frente 3 · Referências de identidade / LOGO (insumo do `agents/logo-design.md`)

Causa-raiz do logo amador é gerar sem referência. Antes do board de logo:

- WebSearch/WebFetch de **logos profissionais** do setor + categorias vizinhas + o
  estilo desejado (Behance, Dribbble, Brand New, Fonts In Use, Logobook, foundries).
- Salvar o board em `referencias/inspiracao-visual/` (e no job em
  `03-visual/referencias-logo/_index.md`), registrando **o que faz cada uma funcionar**:
  construção/grid, peso, espaço negativo, terminais, sistema de cor, mecanismo.
- Também as candidatas de **fonte de título** (quais famílias servem à categoria/tom) —
  alimentam o `tools/font_specimen.py`.
- Direitos autorais: estudo, **nunca cópia** — a marca final é autoral.

## Frente 4 · Mundo real / acervo de referência (fidelidade — insumo de produção visual)

Quando a peça exige **elemento real** (monumento, cidade, ponto turístico, produto do
cliente, pessoa pública), a fidelidade nos mínimos detalhes é obrigatória — realidade
distorcida (Estátua da Liberdade sem tocha, torre Eiffel prateada, fisionomia errada)
destrói a credibilidade da marca.

1. **Estudar cada detalhe** — pesquisar em múltiplas fontes; para o produto do cliente,
   estudar o material que ele passou (embalagem, rótulo, cor, forma reais).
2. **Montar/atualizar o acervo** em `assets/referencias-reais/` (ver
   `assets/referencias-reais/_index.md`): por elemento, registrar as **características
   fiéis** e **o que NUNCA distorcer** (os detalhes-assinatura). Rodar
   `uv run tools/index_assets.py` para o `--ref` encontrar.
3. **Direitos autorais (regra dura):** a referência baixada é ESTUDO e material de
   `--ref` tratado — **nunca publicada na íntegra**. A imagem final é sempre gerada/
   composta pela agência.
4. Entregar o dossiê de fidelidade (o que conferir no gate) para a produção visual
   (`agents/producao-visual.md`, gate de fidelidade ao real).

## Registro por referência (campos mínimos)

Link · plataforma/fonte · autor · tema/nicho · data de coleta · **o porquê** (desempenho,
construção, ou detalhe fiel do real conforme a frente) · **como adaptar sem copiar** · tags.

## Entregável

Arquivos na biblioteca/acervo + síntese para o job (viral: 5–10 linhas; peça rica/logo/
mundo real: dossiê estruturado com fontes).

## Anti-padrões

- Copiar roteiro/arte/logo/imagem de terceiros (inspiração/estudo ≠ cópia).
- Colecionar referência sem extrair o porquê / o detalhe fiel.
- Citar métricas ou dados sem checar (estimativa vira "~aprox."; fato duvidoso → `[CONFIRMAR]`).
- Entregar peça rica rasa por ter pulado a pesquisa profunda.
- Distorcer elemento real por não ter estudado a referência.
- Acionar pesquisa profunda em job que não precisa (respeitar o gate de proporcionalidade).
