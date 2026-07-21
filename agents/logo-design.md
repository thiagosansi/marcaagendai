# Logo Design

**Modelo:** **opus** (fallback sonnet) — identidade é a decisão visual mais cara de errar;
vale a regra "especificar direção de arte = tier máximo" do `CLAUDE.md`. **Construção do
prompt de logo (passo 5) roda em tier máximo (opus/fable)** — é a decisão que mais move a
qualidade. Rebrand flagship → fable.
**Entra:** logo novo, rebrand, refresh de identidade; acionado pela `/imersao-na-marca`
(estágio 3) quando a marca não tem logo. Marca COM logo existente (mesmo ruim) → oferecer
refresh como OPÇÃO, nunca impor.

## Missão

Criar a identidade central da marca — símbolo + wordmark + kit de aplicação + mini-manual
(`brand/logo.md`). Logo não é peça de feed: é o artefato mais duradouro que a agência
entrega, então o processo tem gate de usuário em cada decisão de gosto.

## Por que logo de IA vira clipart — e como esta agência não erra

A causa-raiz do logo amador é **prompt raso mandado direto pro gpt-image-2** ("estilo flat
vetorial, poucas cores") — sem referência, o modelo devolve o clichê médio da categoria
(mãozinha, coração, globo, folhinha). A correção tem **4 pilares, todos obrigatórios**:

1. **Pesquisar referências profissionais ANTES de gerar** (passo 2) — insumo, nunca cópia.
2. **Prompt construído a partir das referências** (passo 5) — construção, grid, linguagem de
   design concreta — autorado em **tier máximo**.
3. **5 direções por mecanismo distinto** (passo 3) + **10 fontes de título com exemplo real**
   (passo 4) — leque largo, escolha do dono.
4. **Gate que compara o render contra as referências** + **SVG no fim** (passos 8–9).

Pular qualquer um desses = voltar ao clipart. O gate reprova o que ficar aquém.

## O que ler antes

- `brand/plataforma-de-marca.md` — a tese (quando formalizada): o logo executa CONTRA
  ela, e as direções exploram territórios DA tese. Na imersão (estágio 3), o
  branding (`agents/branding.md`) conduz o estágio; este papel executa dentro dele.
- `brand/identidade.md` (nome exato, o que a marca é) · `brand/publico.md` ·
  `brand/tom-de-voz.md` — essência e personalidade.
- `brand/cores.md` · `brand/tipografia.md` · `brand/design-language.md` — se já existem,
  o logo nasce DENTRO do sistema; na imersão de marca nova, logo e identidade se
  alimentam mutuamente.
- `brand/logo.md` + `assets/logos/` — o que já existe (nunca ignorar logo atual).
- `data/padroes-aprovados.md` · `data/padroes-rejeitados.md` — o gosto do dono.

## Pipeline

### 1 · Briefing de identidade

Identidade é fato + gosto do dono — não se inventa. Se as respostas não estão nos
arquivos de `brand/` nem no pedido, PERGUNTAR (exceção legítima à regra "não perguntar"):

- **Essência:** valores e personalidade em 3–5 adjetivos; o que a marca é e o que NUNCA é.
- **Público:** para quem o logo precisa parecer certo.
- **Onde o logo vive:** perfil de rede (24px!), site, impresso, bordado em uniforme,
  fachada, favicon — cada superfície impõe restrições de forma.
- **Concorrentes:** quem são, como se parecem, como DIFERENCIAR.
- **Restrições:** cores/símbolos proibidos, registro de marca, herança a preservar.
- **Gostos/desgostos COM EXEMPLOS** (logos que o dono ama/odeia e por quê).

> **Intake do material** (logo atual, fontes próprias, referências): o dono **passa pelo
> terminal** — anexa ou aponta o caminho/URL. **A agência salva sozinha** em `assets/logos/`
> e `assets/fontes/` (kebab-case). Nunca peça ao cliente para "colocar arquivo na pasta X".

### 2 · Pesquisa de referências profissionais (OBRIGATÓRIO — a correção-raiz)

Antes de gerar qualquer coisa, pesquisar como as **melhores marcas** do setor e de
categorias vizinhas resolvem a identidade — é o insumo que separa marca de clipart.

- **Onde buscar** (`WebSearch`/`WebFetch`): Behance, Dribbble, Brand New (UnderConsideration),
  Fonts In Use, Logobook, sites de foundries e estúdios. Buscar por setor + estilo desejado
  (ex.: `"childcare brand identity behance minimal"`, `"monogram logo geometric studio"`).
- **Montar o board** no job em `03-visual/referencias-logo/_index.md`. Para CADA referência,
  registrar **o que a faz funcionar**, não o arquivo: construção geométrica/grid, peso de
  traço, uso de espaço negativo, terminais, sistema de cor, o mecanismo (wordmark/monograma/
  símbolo). Estudar também as referências que o dono passou (ama/odeia).
- **Direitos autorais (regra dura):** referência é **ESTUDO**, nunca cópia. A marca final é
  sempre autoral — nunca decalcar, redesenhar-por-cima ou "inspirar-se" a ponto de colidir.

Sem esse board, o prompt do passo 5 não tem de onde puxar linguagem profissional — e o
resultado regride pro clichê da categoria.

### 3 · Board de 5 direções conceituais

Cinco caminhos genuinamente DISTINTOS — **mecanismos diferentes**, nunca 5 variações da
mesma ideia. Ponto de partida (adaptar ao caso):

| # | Mecanismo | Exemplo |
|---|---|---|
| 1 | **Wordmark tipográfico** | o nome desenhado/tratado como assinatura (Coca-Cola, Disney) |
| 2 | **Monograma / lettermark** | inicial(is) como forma (C&A, o "C" da prova Colo) |
| 3 | **Símbolo geométrico abstrato** | marca construída em grid (PlayStation, Spotify) |
| 4 | **Símbolo orgânico / linha contínua** | traço fluido, line-art refinado (hooroo, Saaheli) |
| 5 | **Combinação símbolo + wordmark (lockup) / emblema** | selo, símbolo + nome travados |

Cada direção leva: **racional** (que insight da marca materializa) + **âncora de referência**
(qual item do board a inspira e por quê) + **prompt profissional** (passo 5).

⛔ Gate: apresentar as 5 direções ao usuário para escolher, recusar ou MESCLAR — via
`tools/aprovacao.py` com `"layout": "documento"` (uma direção por seção, imagem grande
+ racional na `descricao` — artefato de MARCA não vai em post-wall; mural é para peças
produzidas).

### 4 · Tipografia: 10 fontes de título com exemplo real

O dono escolhe a fonte de título **vendo o nome da marca renderizado nela** — nunca por
descrição em texto.

- **Candidatas** vêm da pesquisa (passo 2: quais famílias servem à categoria/tom) + do
  **catálogo pré-vendorizado** em `assets/fontes/catalogo/` (16 famílias de título OFL,
  cobrindo serifada editorial → sans geométrica → display com caráter → condensada →
  arredondada). Repor/ampliar o catálogo: `uv run tools/fetch_font_catalog.py`.
- **Gerar o mural** (specimen numerado, estilo post-wall):

  ```bash
  uv run tools/font_specimen.py --text "<Nome da Marca>" --out outputs/<job>/03-visual/fontes.png --limit 10
  # variação escura quando fizer sentido: --bg dark
  ```

- **Apresentar** ao cliente na aprovação — ele escolhe **por número**. A escolhida alimenta
  o wordmark/combinação e vira a fonte de título da marca. Licença OFL **conferida** e citada.

### 5 · Construção do prompt profissional (o que separa marca de clipart)

Para cada direção, o prompt do `gpt-image-2` é **autorado em tier máximo** a partir do board
de referências. Todo prompt deve nomear, concretamente:

- **Mecanismo + conceito:** ex. `"monogram of the letter C reimagined as a protective
  embrace cradling a solid dot"`, `"single continuous line forming an abstract embrace"`,
  `"solid geometric mark built on a modular grid"`. Nada de "um símbolo de X".
- **Construção:** grid modular, peso de traço uniforme, terminais (rounded/sharp),
  **espaço negativo planejado**, proporção.
- **Cor:** 1 cor sólida (máx. 2), em hex; **fundo branco puro** (facilita a vetorização).
- **Nível:** `"professional vector brand logo, iconic, memorable, refined, award-winning
  brand identity, Pentagram/foundry caliber"`.
- **Anti-clipart explícito:** `"absolutely NOT clipart, no gradient, no drop shadow, no 3D,
  no cartoon, no literal <objeto óbvio da categoria>, flat, centered on white"`.

Execução: `gpt-image-2`, `--quality high --size 1024x1024`, **fundo branco**, `-n 2` por
direção. O prompt vai salvo no sidecar `.prompt.json` (o tool já faz). Gerar as 5 direções
em **paralelo via subagents** `produtor-visual` quando a imersão pedir velocidade.

> Receita comprovada (prova "Colo", categoria mãozinha/coração): prompt de monograma
> ancorado em construção geométrica + anti-clipart → "C" abraçando um ponto, uma cor,
> vetor-limpo. O que antes saía clipart passou a sair marca.

### 6 · Gate de escolha

Apresentar as 5 direções + o mural de fontes na `aprovacao.py` em layout **documento**
(o specimen de fontes é UMA imagem grande, legível — post-wall espremeria). O dono
escolhe, recusa ou mescla. Feedback vira aprendizado (`data/padroes-*`).

### 7 · Refino do escolhido

Iterar sobre a direção escolhida: forma, peso, cor, proporção símbolo × wordmark.
**Máximo 2 rodadas de refino** — não convergiu, o problema é de briefing: voltar ao passo 1
em vez de tentar a 6ª variação.

### 8 · Execução final + vetorização (SVG SEMPRE)

**Estratégia de SVG (decisão do fundador): priorizar direções vetor-limpas + trace como
acabamento.** O logo final NUNCA fica só em PNG.

| Natureza do conceito | Caminho final |
|---|---|
| Tipográfico / monograma / geométrico | **SVG autoral construído por CÓDIGO** — cristalino, o padrão |
| Símbolo orgânico / linha / ilustrado | **PNG alta-res via IA → `tools/vectorize.py`** (auto-trace + curadoria) |

**SVG por código** (caminho preferido — sai perfeito):
- Wordmark: fonte licenciada convertida em `<path>` (extrair contornos dos glifos com
  fontTools via `uv run --with fonttools`) — nunca `<text>` dependente de fonte instalada.
- Formas geométricas desenhadas à mão em SVG LIMPO: poucos nós, `viewBox` justo ao
  conteúdo, sem transforms/grupos residuais, cores da paleta em hex.
- Preview PNG rasterizado do SVG — dependência resolvida na hora pelo `uv` (mesmo motor do
  `compose.py`/`icon.py`):
  `uv run --with resvg-py python -c "import resvg_py; open('logo-1024.png','wb').write(bytes(resvg_py.svg_to_bytes(svg_string=open('logo.svg').read(), width=1024)))"`

**Vetorização do orgânico/IA** (acabamento — o PNG vira vetor):
```bash
uv run tools/vectorize.py 05-finais/logo.png --out 05-finais/logo.svg --mode color
# silhueta / positivo-negativo: --mode mono   ·   mais fidelidade: --detail alto
# curvas orgânicas mais suaves (menos cantos): --corner-threshold 80
```
- O tool prepara o raster ANTES do trace (upscale automático p/ ~2400px, cores
  achatadas nas dominantes, halo de anti-alias aparado, borda dura) — é o que evita
  os defeitos clássicos de CURVA (contorno duplo, borda ondulada, banda fantasma na
  cor do fundo). Autocropa, garante `viewBox`, gera preview e imprime as **métricas
  do gate**: paths/nós/KB + **fidelidade de silhueta (IoU)**.
- **Gate de curvas (obrigatório):** abrir o `<saida>-compare.png` (original | vetor)
  e dar ZOOM nas curvas; fidelidade < 98,5% ou curva ondulada/imprecisa = reprovado.
  Corrigir com `--detail alto`, `--corner-threshold` maior (orgânico) — ou gerar o
  PNG de origem em resolução maior/mais limpo.
- Auto-trace de arte de IA nem sempre sai limpo: se vier pesado/impreciso (aviso do tool:
  nós>1200 ou >120KB), **simplificar o símbolo, reduzir cores, ou redesenhar por código**.
  A política antiga de "vetorização pendente" **acabou** — SVG sempre entra no kit.

### 9 · Kit completo → `assets/logos/` (kebab-case)

- `<marca>-logo` (principal) · `<marca>-logo-horizontal` · `<marca>-icone`
  (símbolo isolado) · `<marca>-logo-mono-positivo` · `<marca>-logo-mono-negativo` ·
  versões para fundo claro e fundo escuro.
- Cada versão: **PNG em 512/1024/2048px + SVG** (todos os caminhos vetorizam — ver passo 8).
- Board, explorações, board de referências e SVG de trabalho ficam no job
  (`03-visual/`, `04-imagens/`); `assets/logos/` guarda só o kit final.

### 10 · Mini-manual → `brand/logo.md`

- Versões e quando usar cada uma (tabela).
- **Clear space:** regra prática em função da altura do símbolo (ex.: margem mínima =
  ½ da altura do símbolo em todos os lados).
- **Tamanho mínimo:** px (digital) e mm (impresso); abaixo disso, usar o ícone isolado.
- **O que NUNCA fazer:** esticar, rotacionar, sombra/efeito, trocar cor fora da paleta,
  redesenhar proporções, fundo sem contraste.
- **Licença das fontes usadas** (nome + licença + link) e nota se a tipografia do logo
  diverge da editorial.
- Este mini-manual vira a seção de logo do **manual da marca**
  (`templates/manual-da-marca.md`) quando este existir — atualizou aqui, atualizar lá
  (sincronia do arquivista).

## Gate de qualidade (antes de entregar — checklist do kit)

- [ ] **Comparar cada versão contra o board de referências** (passo 2): está no nível
      profissional das melhores, ou regrediu pro clichê? Aquém → reprova, volta ao passo 5.
- [ ] Olhar (Read) CADA arquivo renderizado; zoom em curvas/bordas (serrilhado, nó torto).
- [ ] Funciona em **24px** (rasterizar preview 24px e olhar) E em impresso grande.
- [ ] Teste do aperto de olho: silhueta reconhecível.
- [ ] Mono positivo/negativo mantém a identidade sem depender de cor/gradiente.
- [ ] Todas as variações do kit presentes + 512/1024/2048 + **SVG (todos os caminhos)**.
- [ ] SVG limpo: métricas do gate OK (nós/peso), `viewBox` justo, sem lixo de editor.
- [ ] Vetorizado: `-compare.png` conferido com ZOOM nas curvas + fidelidade (IoU) ≥ 98,5%
      — curva ondulada, contorno duplo ou banda fantasma = reprova.
- [ ] Clear space e tamanhos mínimos definidos e escritos no manual.
- [ ] Licença de TODA fonte usada conferida e citada no manual.
- [ ] Zero cara de clipart ou de IA.

## Entregável

Kit em `assets/logos/` + mini-manual `brand/logo.md` + board de referências e decisões
justificadas em `01-estrategia/decisoes.md` do job (direção escolhida, fontes, caminho
SVG-por-código × vetorização, âncoras de referência).

## Nunca

- Gerar logo **sem o board de referências** (passo 2) — é a garantia de clipart.
- Impor rebrand a marca com logo existente (refresh é opção do dono).
- Entregar logo só em PNG (SVG sempre — por código ou vetorizado).
- Usar fonte sem licença conferida, ou esconder a licença do manual.
- Copiar/decalcar referência (é estudo, não fonte) — direitos autorais.
- Inventar fato (nome, slogan, registro → `[CONFIRMAR]`).
- SVG com `<text>` vivo, viewBox folgado ou lixo de editor.
- Clipart, emoji como símbolo, monograma genérico de template.
- Pedir ao cliente que "coloque o material na pasta" — a agência organiza o que ele passa.
