---
name: imersao-na-marca
description: Onboarding guiado da marca num harness recém-exportado (filial) - pipeline de 6 estágios com gates de parada (setup técnico com OPENAI_API_KEY, materiais ask-first, entrevista + briefing de marca obrigatórios, identidade & manual da marca entregue como página web com aprovação do cliente, 30 peças-exemplo de Instagram variadas aprovadas na página, liberação). Estágios 3-4 fecham com aprovação formal via tools/aprovacao.py (loop até status aprovado; formato da página segue o artefato - mural para peças, carrossel real com voto por slide, documento para artefatos de marca). Estado persistente em brand/onboarding-status.md - a skill retoma do estágio pendente; estágio pendente bloqueia produção. Rodar quando o status tiver estágio pendente ou brand/ contiver [PREENCHER].
---

# Imersão na marca — onboarding em estágios com gates

Objetivo: sair de um harness em branco para uma agência configurada, calibrada e
liberada para o primeiro job. Fonte de tudo: **o usuário**. Materiais que ele apontar
ajudam, mas não decidem.

## Regras duras (valem em todos os estágios)

1. **Persistir antes de avançar**: cada estágio grava seus resultados nos arquivos do
   repo (`brand/`, `data/`, `assets/`, `.env`) ANTES de passar ao próximo. Decisão que
   ficou só na conversa = decisão perdida — a falha clássica de filial foi decidir sem
   gravar nada.
2. **Estado em `brand/onboarding-status.md`**: ao iniciar, LER o status e retomar do
   primeiro estágio pendente (nunca refazer os concluídos). Ao fechar um estágio,
   marcar `[x]` com data e observação de 1 linha. Arquivo não existe? Criar com os 6
   estágios em `[ ]` (modelo em `templates/marca-nova/brand/onboarding-status.md`).
3. **Gate = STOP de verdade**: onde o estágio manda parar, PARE — apresente, pergunte
   e **aguarde a resposta do usuário** antes de qualquer próximo passo.
4. **Nunca inventar fato de marca** — o que faltar fica `[PREENCHER]` e vira pendência.
5. **Onboarding incompleto bloqueia produção** (regra do CLAUDE.md): pedido de peça
   com estágio pendente vira continuação desta imersão.
6. **Ask-first para materiais**: o harness NUNCA varre a máquina nem o repo em busca
   de materiais por conta própria — **nem com permissão**. Material entra no fluxo
   porque o usuário apontou o caminho; a skill só lê exatamente o que foi apontado.
   Vale em todos os estágios, não só no 1.
7. **Voz de AGÊNCIA com o cliente**: falar sempre como agência — "nós", "aqui na
   agência", "o que **fizemos**". NUNCA expor "a IA", o harness, a skill, um nome de
   script ou "a ferramenta" como sujeito ao cliente. "A IA vai gerar" → "**vamos
   produzir**"; "o que a IA fez" → "**o que fizemos**". A key da API se explica como
   "o que **nos permite produzir** as imagens das peças", sem citar o script.
8. **A AGÊNCIA organiza o material — o cliente só passa**: o material chega pelo
   terminal (o cliente anexa OU cola o caminho/URL de referência); **a agência lê o
   apontado e salva/organiza sozinha** nas pastas de `assets/`. **NUNCA pedir que o
   cliente "coloque o arquivo na pasta X"** — arrumar é trabalho nosso.
9. **Numeração CONTÍNUA das perguntas** (estágio 2): numerar de forma contínua e
   sequencial na ordem de envio, do começo ao fim do estágio. **Uma pergunta enviada
   via `AskUserQuestion` CONSOME seu número normalmente** — nunca reiniciar a contagem
   nem pular número por causa da ferramenta ou da quebra em blocos (a falha clássica:
   pular da 5 para a 7, ou da 5 para a 8, quando a múltipla escolha sai no tool).
10. **Paralelizar a PRODUÇÃO por porte** (velocidade sem perder qualidade): onde o
    estágio produz em lote — board de logo, seções do manual, build web, as 30
    peças-exemplo + os 3 gates — rodar via subagents em paralelo (`produtor-visual`,
    `produtor-web`, `revisor`), conforme a proporcionalidade do `CLAUDE.md`. Só os
    loops de aprovação (espera do cliente) são inerentemente seriais — a produção não.

## Página de aprovação do cliente (protocolo dos estágios 3 e 4)

`tools/aprovacao.py` sobe uma página web local (127.0.0.1) onde o CLIENTE revisa,
vota 👍/👎 e comenta por seção/peça (👎 exige comentário). **O FORMATO da página
segue o ARTEFATO** (o docstring do tool é o contrato):

- **Peças produzidas** (posts, stories, capas) → spec com `"layout": "mural"`
  (post-wall): grade com imagem grande; clique amplia em **lightbox** (a imagem ocupa
  a tela, swipe/setas navegam entre as peças, legenda/detalhes sob a imagem).
- **Carrossel** → item `"tipo": "carrossel"` com os slides: vira carrossel DE VERDADE
  na página (passa pro lado e pro outro) e o voto continua **POR SLIDE** — o widget
  acompanha o slide ativo, os dots mostram o estado.
- **Artefatos de MARCA** (board de direções de logo, specimen de fontes, paleta,
  blocos de manual) → spec com `"layout": "documento"`: coluna única, imagem grande,
  leitura de board. **Post-wall NÃO serve para esses artefatos.**
- **Manual da marca web** → `--html` com `data-aprovacao` por seção (widgets
  injetados na própria página).

Há um **campo de comentário geral** no fim (para observações que não são de uma peça
específica; opcional, não trava a conclusão). O botão final "✅ Pronto — tudo
revisado" grava o feedback no `--out` (`{status: "aprovado"|"com-ajustes", itens:
[{id, titulo, voto, comentario}], comentario_geral}` — slides de carrossel entram
como itens), encerra o processo e devolve o controle à agência. **Ler o
`comentario_geral` também** — nele costumam vir pedidos transversais (paleta, tom,
direção) que valem para todas as peças.

- **Rodar via Bash com `run_in_background: true` e AGUARDAR a notificação de término
  do processo** (o servidor vive, sem timeout, até o cliente concluir). Terminou →
  ler o JSON do `--out`; cada 👎 volta para ajuste com o comentário do cliente como
  brief; reabrir nova rodada (`r1`, `r2`…) — LOOP até `status: "aprovado"`, com os
  aprovados acumulando num placar no job.
- Resiliência: cliente fechou a aba sem concluir → o servidor segue vivo, basta
  reabrir a URL impressa no stdout; sem navegador (SSH/headless) → a ferramenta
  imprime a URL (`--no-open`), passar ao cliente para abrir manualmente; Ctrl+C
  cancela a rodada sem gravar nada (exit 130).

## Estágio 0 — Setup técnico

- Conferir `.env`: existe? `OPENAI_API_KEY` preenchida? Se faltar: **PARE e PEÇA a key
  ao usuário** — explicar (voz de agência) que ela é **o que nos permite produzir as
  imagens das peças**; sem ela, algumas peças ficam limitadas. Apontar o `.env.example`
  como modelo. Com a resposta: gravar o `.env` e validar com uma geração mínima
  (`uv run tools/generate_image.py --prompt "um círculo azul sobre fundo branco" -n 1
  --quality low --out /tmp --name teste-api`).
- **Prosseguir sem key SÓ com consentimento explícito do usuário**, registrado na
  observação do estágio ("sem geração de imagem por ora — aprovado pelo usuário"),
  deixando claro o que fica indisponível (peças dependentes de imagem gerada).
- Conferir também: `uv` roda; fontes do harness em `assets/fontes/` +
  `assets/fontes/mapa-fontes.json` presentes; ícones em `assets/icones/lucide/`
  (vazio → `uv run tools/fetch_icons.py`).
- ⛔ Gate: `.env` resolvido (gravado e testado, OU consentimento sem-key registrado no
  status) — persistir o status e só então avançar.

## Estágio 1 — Materiais (ask-first)

- **O harness NUNCA varre a máquina nem o repo em busca de materiais por conta
  própria — nem com permissão.** Nada de listar pastas, `find`, `glob` ou "deixa eu
  ver o que você tem por aqui": material só entra no fluxo porque o usuário apontou.
- PERGUNTAR ao usuário quais assets existem, em lista clara:
  - logo? (em quais formatos — vetor, PNG?)
  - manual da marca / style guide? (PDF, link?)
  - fotos? (de quê — produto, equipe, espaço, bastidores — e quantas?)
  - peças antigas aprovadas? (posts, materiais que representam bem a marca)
  - fontes próprias? (`.ttf`/`.otf`, com licença confirmada)
  - paleta documentada? (hex oficiais, manual de cores)
- **O cliente PASSA o material pelo terminal — a agência organiza.** Ele **anexa** os
  arquivos na conversa OU **cola o caminho/URL** de onde estão. NUNCA pedir que ele
  "coloque em `assets/logos/`" ou arrume pasta: arrumar é trabalho nosso. Frasear como
  agência: "manda aqui que a gente organiza", não "salve na pasta X".
- **SÓ DEPOIS** de recebido/apontado: ler exatamente o que veio (nada além) e confirmar
  a interpretação **item a item** — "recebemos X e entendemos Y — confere?".
- **Materiais são HIPÓTESES até o usuário confirmar — NUNCA trate material, mesmo
  passado por ele, como decisão de marca.**
- ⛔ Gate: cada item recebido com interpretação confirmada (é oficial? está atual?
  entra ou descarta?). "Não tenho nada" é resposta válida — registrar e seguir: o
  estágio 3 cria tudo do zero.
- Persistir: **a agência salva e organiza** o confirmado em `assets/` sozinha — logos em
  `assets/logos/`, fontes em `assets/fontes/`, referências aprovadas em
  `assets/referencias-aprovadas/`, fotos em pastas kebab-case novas (ex.:
  `assets/produtos/`, `assets/equipe/`), tudo mapeado na tabela do `assets/README.md`;
  descartes e itens sem veredito anotados na observação do status.

## Estágio 2 — Entrevista + briefing de marca (SEMPRE, mesmo com material farto)

**Condução: `agents/branding.md`** (inline no porte normal; subagent em porte grande,
conforme a proporcionalidade do `CLAUDE.md`) — entrevista e briefing são a
matéria-prima da plataforma de marca do estágio 3.

Duas frentes, aplicadas em **blocos digestíveis** (nunca as ~19 perguntas de uma vez),
com **numeração ÚNICA e contínua P1→P19** — os blocos são só rótulos; a contagem corre
reto (regra dura 9). **Pergunta enviada via `AskUserQuestion` mantém seu número na
sequência** — não reiniciar nem pular por causa da ferramenta.

**Bloco A · Fatos objetivos (P1–P10)** — mensagem única e organizada:
  P1. Identidade e fatos: nome exato da marca, o que faz/vende, diferenciais;
  P2. Site oficial; P3. Instagram e demais redes (handles);
  P4. Segmento e concorrentes/referências (quem admira, de quem quer distância);
  P5. Público: perfis, dores, desejos; P6. Tom de voz: como fala e como NUNCA fala;
  P7. Do's & don'ts de comunicação;
  P8. Produtos/ofertas com fatos: preço, formato, datas, URL por produto;
  P9. Setor regulado? Regras éticas/legais do domínio (o que nunca prometer);
  P10. Rostos da marca: quem aparece, fotos-fonte e **autorização de imagem**.

**Bloco B · Perfil da marca (P11–P19)** (`templates/briefing-de-marca.md`, questões 1–9
renumeradas em sequência): P11 negócio, P12 negócio em uma frase, P13 público-alvo,
P14 primeira impressão desejada, P15 cores de preferência e **vetadas**, P16
características que refletem o negócio (**múltipla escolha**), P17 referências
admiradas / de quem fugir, P18 palavras-chave, P19 o que a marca NUNCA deve parecer.
  A múltipla escolha (**P16**) sai via **AskUserQuestion** quando disponível (opções
  marcáveis > lista para transcrever) **mantendo o número P16**; as abertas seguem em
  texto. As de leque fechado (P15 cores, P17 referências) também podem usar o tool sem
  perder seu número.

- **"PARE e aguarde as respostas do usuário. NUNCA responda a entrevista ou o briefing
  por conta própria com material apontado — material só serve para PRÉ-PREENCHER
  um resumo que o usuário confirma."**
- Usuário enviou manual da marca (PDF/imagens)? Extrair, montar o resumo do que foi
  entendido e CONFIRMAR com ele antes de gravar.
- ⛔ Gate: respostas recebidas (ou pendência explícita por item não respondido) E
  briefing PERSISTIDO em `brand/briefing-de-marca.md` — sem isso não avança.
- Persistir: `brand/briefing-de-marca.md` (questionário respondido, grafia fiel) +
  `brand/identidade.md`, `brand/publico.md`, `brand/tom-de-voz.md`,
  `brand/etica-e-saude.md` + sementes de `data/` (insights de audiência). Grafia exata.
- O estágio 3 deriva paleta/tipografia/estilo/logo **do briefing** — capricho aqui
  poupa rodadas de board.

## Estágio 3 — Identidade & manual da marca: traduzir OU criar

Dois caminhos — escolher pelo que o estágio 2 revelou. Nos dois, o destino é o mesmo:
identidade documentada em `brand/*.md` (fonte da verdade) e consolidada num **manual
da marca (branding book)** nível SIMPLIFICADO (`templates/manual-da-marca.md`,
seções 0–7), aprovado pelo cliente na página de aprovação.

**Condução: `agents/branding.md`** — primeiro ato do estágio, nos dois caminhos:
transformar entrevista + briefing na **plataforma de marca**
(`brand/plataforma-de-marca.md`; estrutura do gêmeo em `templates/marca-nova/brand/`),
validada com o usuário. Ela é o brief de tudo abaixo (tese antes do pixel):
logo-design, direção criativa e copywriter executam contra ela, e a seção "A marca"
do manual nasce dela.

Primeiro passo do estágio (se ainda não existir): criar o job da imersão —
`uv run tools/new_job.py "onboarding-imersao"` — boards, drafts do manual, versão
web, peças-exemplo do estágio 4 e feedbacks do cliente vivem nele (é o `<job>` das
instruções abaixo).

**(a) Marca COM identidade definida** — traduzir e validar:
- O manual/style guide que o usuário apontou no estágio 1 é TRADUZIDO para os
  arquivos da agência: paleta, tipografia e estilo em `brand/cores.md`,
  `brand/tipografia.md`, `brand/identidade-visual.md` e `brand/design-language.md`;
  validar o resumo com o usuário antes de dar por fechado.
- Fontes próprias → `.ttf`/`.otf` em `assets/fontes/` + papéis (display/corpo/kicker)
  em `assets/fontes/mapa-fontes.json` + render de calibração no estágio 4. Sem fonte
  própria → os OFL do harness seguem como fallback licenciado (registrar como decisão
  consciente do usuário, não omissão).
- Manual recebido defasado, incompleto ou inexistente como documento? **OFERECER**
  atualizar/gerar um manual novo (simplificado já; completo pós-calibração) — opção
  do dono, NUNCA imposição. Registrar a decisão em `brand/manual-da-marca.md`.

**(b) Marca SEM identidade (ou incompleta) — cliente-do-zero: a agência cria TUDO.**
Marca sem nada NÃO é impedimento — é o caso em que a agência MAIS agrega. Tudo nasce
do briefing (`brand/briefing-de-marca.md` + entrevista) e é apresentado como **boards
de direções A/B/C** para o usuário aprovar/recusar/mesclar, iterando até aprovação:

1. **Identidade verbal**: personalidade da voz, regras de linguagem, mensagens-chave
   e o que a marca NUNCA parece (pergunta 9 do briefing) → preencher
   `brand/tom-de-voz.md` e `brand/identidade.md`;
2. **Identidade visual completa**:
   - Paleta: 2–3 rotas com hex e **racional por cor** amarrado ao briefing (primeira
     impressão desejada, características marcadas, cores de preferência — vetadas
     respeitadas sem exceção);
   - Tipografia: apresentar **~10 fontes de título com EXEMPLO renderizado** — mural
     numerado via `uv run tools/font_specimen.py --text "<Nome da Marca>" --out
     <job>/03-visual/fontes.png --limit 10` (candidatas do catálogo
     `assets/fontes/catalogo/` + pesquisa; `--bg dark` quando fizer sentido). O cliente
     **escolhe por número** na aprovação; a escolhida vira a fonte de título + os pares
     corpo/kicker (papéis display/corpo/kicker), licença OFL conferida;
   - Estilo visual: moodboard descritivo + referências;
   - Grafismos próprios da marca (ver bloco abaixo);
   - LOGO: acionar o papel `agents/logo-design.md` — **pesquisa de referências
     profissionais → board de 5 direções (por mecanismo) + specimen de fontes →
     refino → vetorização SVG → kit em `assets/logos/` + mini-manual `brand/logo.md`**.
     Board apresentado ao cliente em layout **documento** na aprovação (uma direção
     por seção, imagem grande + racional — artefato de marca não vai em post-wall);
3. **Gramática visual fechada**: `brand/design-language.md` + `brand/tema-visual.json`
   preenchidos e COERENTES entre si e com o resto (mesma paleta, mesmos papéis de
   fonte, mesma anatomia de grafismos — nada decidido num arquivo e esquecido no outro);
4. **Consolidar no MANUAL SIMPLIFICADO**: boards aprovados → montar o manual da marca
   (seções 0–7 de `templates/manual-da-marca.md`), SEMPRE em markdown estruturado,
   como draft no job da imersão — a cópia para `brand/manual/` só acontece DEPOIS
   do loop de aprovação abaixo.

**Grafismos próprios da marca** (dispositivos de assinatura, selos, texturas): são
DECIDIDOS COM O USUÁRIO a partir da identidade DELA. **PROIBIDO replicar
dispositivos de outra marca ou "da casa anterior"** — a filial nasce com assinatura
própria, não com a fantasia de outra marca.

**Aprovação do cliente — loop na página web** (todo manual consolidado neste
estágio, inclusive no caminho (a) quando o dono aceitar a oferta):

1. **Versão web do manual**: one-pager autocontido em `<job>/site-manual/`
   (seguir `agents/web-design.md` + `agents/web-dev.md`; fontes reais da marca via
   `@font-face`) — **a página web É o entregável do manual** (compartilhável com o
   cliente), não só o veículo de aprovação — com **cada seção do manual marcada com
   `data-aprovacao="<id>"` e `data-titulo="<nome da seção>"`** — a marcação é
   requisito do build do manual web.
2. **Abrir para o cliente**: `uv run tools/aprovacao.py --html
   <job>/site-manual/index.html --out <job>/06-revisao/feedback-manual-r<N>.json`
   — protocolo background acima; aguardar o término do processo e ler o JSON.
3. **Iterar**: seção 👎 volta para ajuste com o comentário do cliente como brief
   (identidade muda em `brand/*.md` primeiro, o manual acompanha); regenerar e
   REABRIR a página **só com as seções ajustadas em destaque** — na rodada nova,
   apenas elas levam `data-aprovacao` (novo voto); as aprovadas ficam como contexto
   e ACUMULAM no placar `<job>/06-revisao/placar-manual.md`. LOOP até uma rodada
   fechar com `status: "aprovado"` (zero 👎).
4. **Só então — identidade selada**: manual vigente copiado para `brand/manual/`
   — o markdown (`manual-simplificado-v01.md`) E a versão web autocontida
   (`site-manual-v01/`, sem as marcações de aprovação ativas) + registro em
   `brand/manual-da-marca.md`; PDF A4 só se o cliente pedir material impresso
   (etapa posterior ou pendência registrada).

- ⛔ Gate: caminho (a) — resumo validado pelo usuário + oferta de manual respondida;
  caminho (b) — manual SIMPLIFICADO **aprovado pelo cliente NA PÁGINA**
  (`status: "aprovado"` no feedback JSON da última rodada) — aprovação só verbal
  não fecha o gate.
- Persistir: `brand/plataforma-de-marca.md` (a tese) + `brand/*.md` do caminho
  percorrido + `brand/tema-visual.json` (cores
  default de texto/ícone/badge, anatomia de balão, sombras, presets de fundo) +
  manual simplificado em `brand/manual/` (md + site web) com registro em
  `brand/manual-da-marca.md`
  (no caminho (a), quando o dono aceitar a oferta) + feedbacks e placar arquivados
  no job (`06-revisao/`).
- **Manual COMPLETO** (exemplos de aplicação reais, grid, vídeo, acessibilidade) é
  job posterior — ideal DEPOIS do estágio 4: o gosto sai calibrado e as
  peças-exemplo aprovadas são candidatas naturais a exemplos de aplicação. O resumo
  final da imersão (estágio 5) oferece.

## Estágio 4 — Peças-exemplo de Instagram (aprovação do cliente)

Com a identidade selada, produzir o primeiro set REAL da marca e aprovar peça a
peça na página — a calibração de gosto acontece sobre material de verdade
(moodboard vira apoio opcional de processo, não entrega).

**Condução: `agents/branding.md`**, com a direção criativa: cada peça precisa
EXPRESSAR a plataforma (posicionamento, personalidade, mensagens-chave), não só
obedecer à gramática visual.

- Produzir EXATAMENTE **30 peças** — mix de referência: **14 posts de feed + 14
  stories + 2 carrosséis (capa + 4–5 slides cada)**; o painel pode rebalancear os
  formatos conforme a marca, mantendo o TOTAL de 30 (mínimos: 8 feeds, 8 stories,
  2 carrosséis). Peças reais do pipeline (`generate_image`/`compose`), no mesmo job
  da imersão. Cada peça EXPRESSA a plataforma; nenhuma é preenchimento.
- **VARIEDADE é requisito, não desejo** — o conjunto varre o alcance do sistema, não
  30 variações da mesma ideia. Mínimos no conjunto (os eixos se sobrepõem; adaptar o
  que não fizer sentido para a marca, registrando o porquê em `decisoes.md`):
  - **cenas e fotos REAIS** do acervo (quando existirem e autorizadas) e/ou pessoas
    reais da marca recompostas via `--ref` — ≥ 4;
  - **cenas realistas por IA** com pessoas genéricas do universo da marca — ≥ 5;
  - **sem pessoas** (cenário, detalhe, objeto/produto) — ≥ 5;
  - **fundo chapado** tipográfico — ≥ 5;
  - **grafismos/elementos visuais da marca** em destaque — ≥ 5;
  - **tom claro E tom escuro** conforme a paleta — ≥ 8 de cada, se a marca tiver os
    dois lados;
  - **hierarquia tipográfica VARIADA entre as peças** — tamanho, peso e cor por linha
    nos títulos (lockup do compose) e textos secundários variando quando fizer
    sentido; atravessa o conjunto INTEIRO (dentro de uma peça segue valendo máx.
    3 níveis — `agents/design.md`).
- **Produzir em PARALELO** (regra dura 10): as 30 peças via subagents `produtor-visual`
  simultâneos em lotes coesos (5–6 peças por sistema visual/lote), com batch das
  gerações de imagem — corta a maior parte do tempo do estágio sem tocar na qualidade.
- Calibração técnica embutida: os renders testam as fontes reais da marca; o compose
  avisou colisão de tinta entre linhas → ajustar o `line_height` do papel em
  `assets/fontes/mapa-fontes.json` e re-renderizar até limpar.
- **3 gates internos da casa ANTES do cliente** (marca, ética, qualidade): o
  cliente nunca vê peça que os gates da casa reprovariam.
- Montar `<job>/06-revisao/review-pecas-r<N>.json` (modo `--spec`, layout mural):
  **1 item por peça avulsa** (`feed-01..`, `story-01..` — com `legenda` e `detalhes`
  preenchidos: aparecem no lightbox) + **cada carrossel como item
  `"tipo": "carrossel"`** com os slides listados — na página ele roda como carrossel
  de verdade e o voto é **POR SLIDE**. Slide 👎 é refeito com o comentário como
  brief; se o comentário apontar problema de SISTEMA (paleta, conceito, tipografia),
  o carrossel INTEIRO revisita a direção.
- Abrir: `uv run tools/aprovacao.py --spec <job>/06-revisao/review-pecas-r<N>.json
  --out <job>/06-revisao/feedback-pecas-r<N>.json` — protocolo background acima.
  LOOP: peça 👎 é refeita com o comentário do cliente como brief e volta na rodada
  seguinte; aprovadas acumulam no placar `<job>/06-revisao/placar-pecas.md`; até
  `status: "aprovado"`.
- Persistir a CADA rodada: aprovação/reprovação + comentário viram entrada datada em
  `data/padroes-aprovados.md` / `data/padroes-rejeitados.md`, aprendizados em
  `data/memoria-visual.md`; os feedback JSONs ficam arquivados no job — a filial
  nasce com o gosto calibrado em arquivo.
- ⛔ Gate: **todas as 30 peças aprovadas na página** — toda peça avulsa e todo slide
  de carrossel (rodada com `status: "aprovado"`).

## Estágio 5 — Liberação

- Checklist final (tudo precisa passar):
  - `grep -rn "PREENCHER" brand/` sem pendência crítica (restos viram lista de pendências);
  - `.env` ok (ou consentimento sem-key registrado no status);
  - `brand/tema-visual.json` preenchido com as decisões do estágio 3;
  - memórias semeadas (padrões aprovados/rejeitados + memória visual com entradas datadas);
  - `uv run tools/index_assets.py` rodado (`data/asset-index.json` atualizado);
  - **página de entrega do job da imersão gerada** (`uv run tools/entrega.py
    <job>/entrega.json`): as 30 peças aprovadas em mural + carrosséis reais + item
    `site` apontando o manual web — toda entrega da casa fecha com `entrega.html`.
- ⛔ Gate: item reprovado → voltar ao estágio dono do item e corrigir; NÃO marcar completo.
- Persistir: marcar o estágio 5 `[x]` em `brand/onboarding-status.md` (produção
  liberada) e entregar o resumo final — o que foi configurado, decisões-chave,
  pendências `[PREENCHER]` restantes, a OFERTA do manual da marca COMPLETO (com
  exemplos de aplicação reais — as peças-exemplo aprovadas no estágio 4 já são
  candidatas e o gosto está calibrado: é o momento ideal) e que a agência está
  pronta para pedidos em linguagem natural.
