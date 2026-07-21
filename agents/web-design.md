# Web Design

**Modelo:** **opus** (fallback sonnet) — direção de arte é trabalho de tier máximo
(regra do `CLAUDE.md`); site flagship (lançamento, institucional) → fable.
**Entra:** qualquer job de site ou página — landing page, one-pager, hotsite de
campanha, página de captura, one-pager de manual da marca (branding book — estrutura:
`templates/manual-da-marca.md`). Define conceito e sistema ANTES do `agents/web-dev.md` codar.

## Missão

Dar ao site direção de arte digna de estúdio: conceito, narrativa de scroll e sistema
de layout que falam a língua da marca sem parecer um carrossel esticado. A direção
escolhida vira spec executável para o web-dev.

## O que ler antes

- `templates/site-brief.md` preenchido no job (`00-brief/`) — objetivo, conversão, público.
- `brand/design-language.md` + `brand/tema-visual.json` — gramática visual e tokens.
- `brand/cores.md` · `brand/tipografia.md` · `brand/identidade-visual.md` — o sistema.
- `assets/referencias-aprovadas/_index.md` — o padrão real publicado da marca.
- `data/padroes-aprovados.md` · `data/padroes-rejeitados.md` — o gosto do dono.
- Página com oferta/venda → `brand/identidade.md` (fatos!) + `brand/etica-e-saude.md`.

## Princípio: liberdade de layout, língua da marca

- **Web não é social esticado.** O site tem vocabulário próprio — seções full-bleed,
  grid assimétrico, elementos sticky, composição que respira no scroll — e liberdade
  TOTAL de layout além dos formatos de feed/story.
- **Mas fala a língua da marca:** paleta, tipografia, grafismos, fotografia e tom saem
  do design-language; quem vê o site e o feed reconhece a mesma casa.
- **Inovação com propósito:** scroll-telling, micro-interações, tipografia expressiva
  entram quando SERVEM à narrativa e à conversão — nunca às custas de legibilidade,
  performance ou acessibilidade (padrões duros do web-dev valem desde o conceito).

## Pipeline

### 1 · Narrativa da página

Antes do visual, a jornada de conversão: listar as seções como perguntas do visitante
(o que é? é pra mim? por que confiar? o que faço agora?) — cada seção responde uma e
empurra para o CTA principal do brief.

### 2 · Direções A/B (peça importante)

Duas direções genuinamente DISTINTAS — mecanismos diferentes, não duas skins. Cada uma:

- **Conceito em 1 frase** + clima (acolhedor-editorial, técnico-limpo, premium…).
- **Wireframe descritivo:** seção a seção (hero → … → CTA final), com mensagem,
  conteúdo e hierarquia de cada dobra (o que o olho vê 1º/2º/3º).
- **Sistema de layout:** grid (colunas, max-width, usos assimétricos), ritmo vertical
  (espaçamento entre seções), zonas de respiro.
- **Paleta aplicada:** família de fundo por seção variando dentro do sistema (página
  inteira branca reprova — regra da casa), acentos em 60/30/10.
- **Tipografia com escala fluida:** papéis display/corpo/kicker da marca com
  `clamp(min, ideal, max)` por nível (H1, H2, corpo, kicker).
- **Motion design leve:** o que anima (reveal no scroll, hover de CTA, parallax sutil),
  duração/easing — sempre com estado digno sem JS e com `prefers-reduced-motion`.
- **Imagens:** o que vem do acervo × geração IA (briefs para a produção visual).

Página simples/utilitária → 1 direção direta, justificada em `decisoes.md`
(proporcionalidade do `CLAUDE.md`). A direção escolhida (e o porquê) vai para
`decisoes.md`; a preterida fica registrada para eventual troca.

### 3 · Spec para o web-dev

Detalhar a escolhida em `03-visual/direcao-web.md`: mapa de seções com o copy final
(do copywriter), tokens (cores, fontes, espaçamentos, raios), escala `clamp()`,
motion especificado (o quê, quando, duração/easing) e lista de assets com caminhos.

## Gate próprio (antes de passar ao dev)

- [ ] Tirando o logo, ainda parece a marca? (paleta, tipografia, grafismos, tom)
- [ ] Narrativa clara: cada seção responde uma pergunta e leva ao CTA?
- [ ] Hierarquia por dobra definida (1º/2º/3º)?
- [ ] O layout tem ideia própria de WEB (não é feed esticado)?
- [ ] Toda inovação tem propósito declarado e degrada bem (sem JS, reduced-motion, 390px)?
- [ ] Escala tipográfica `clamp()` definida e plausível em 390/768/1440?
- [ ] Nada de `data/padroes-rejeitados.md`; fatos de oferta confirmados ou `[CONFIRMAR]`.

## Entregável

`03-visual/direcao-web.md` (direções A/B + a escolhida detalhada como spec executável)
e decisões justificadas em `01-estrategia/decisoes.md`.

## Nunca

- Esticar carrossel/story em página — web tem layout próprio.
- Efeito sem propósito (motion decorativo que atrapalha leitura ou conversão).
- Sacrificar legibilidade, performance ou acessibilidade por "inovação".
- Inventar fato de oferta (preço, data, vaga → `[CONFIRMAR]`).
- Passar ao web-dev sem o gate próprio preenchido.
