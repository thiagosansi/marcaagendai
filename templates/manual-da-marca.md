# Manual da marca (branding book) — estrutura canônica

> **O que é:** o entregável clássico de agência que consolida a identidade num
> documento apresentável — para o dono, a equipe, fornecedores e futuros criativos.
> **Quem usa:** o job "manual da marca" (tipo de job orquestrado pelos papéis
> existentes — estratégia, copywriter, direção criativa + design, offline e/ou time
> web, gates; conteúdo dirigido pelo `agents/branding.md`, dono do que o manual DIZ —
> os demais executam a forma) e a `/imersao-na-marca` (estágio 3: boards
> aprovados consolidam no nível SIMPLIFICADO).
> **Regra de ouro:** o manual APRESENTA o que `brand/*.md` define — NUNCA inventa.
> Conteúdo novo não nasce aqui: nasce em `brand/`, o manual espelha. Fato ausente =
> `[CONFIRMAR: …]` na página e pendência no registro.

## Dois níveis

| Nível | Seções | Quando |
|---|---|---|
| **Simplificado** | 0–7 | padrão do onboarding (estágio 3 da imersão) e da maioria dos pedidos — o essencial para qualquer pessoa aplicar a marca |
| **Completo** | 0–14 | marca com produção rodada — ideal DEPOIS das peças-exemplo aprovadas (estágio 4): os exemplos de aplicação nascem no gosto já calibrado |

## Nível SIMPLIFICADO (essencial)

### 0 · Capa + sumário

Capa com logo, nome ("Manual da marca — <Marca>"), nível e versão + sumário das
seções. A capa já é peça da marca: fundo, tipografia e grafismos do sistema.

### 1 · A marca

Essência, posicionamento e a definição em UMA frase.
Fonte: `brand/plataforma-de-marca.md` (a tese — fonte primária desta seção, dirigida
pelo `agents/branding.md`) + `brand/identidade.md` + `brand/briefing-de-marca.md`
(negócio-em-uma-frase) + `brand/publico.md` (para quem a marca existe).

### 2 · Logo

Versões e quando usar cada uma, clear space, tamanhos mínimos (digital px / impresso
mm), comportamento sobre fundo claro/escuro e o que NUNCA fazer com o logo.
Fonte: `brand/logo.md` (mini-manual) + kit em `assets/logos/`.

### 3 · Cores

Paleta com hex, papel e proporção de uso de cada cor (primárias/secundárias/acentos/
neutros), combinações aprovadas e combinações VETADAS.
Fonte: `brand/cores.md`.

### 4 · Tipografia

Famílias (com licença), papéis display/corpo/kicker e hierarquia com exemplos
renderizados (título, subtítulo, corpo, rótulo).
Fonte: `brand/tipografia.md` + `assets/fontes/mapa-fontes.json`.

### 5 · Tom de voz

Personalidade em adjetivos, como a marca fala / como NUNCA fala e 3–5 frases-exemplo
reais (certo × errado quando ajudar).
Fonte: `brand/tom-de-voz.md`.

### 6 · Estilo visual em ~5 regras

As regras que fazem uma peça "parecer a marca": fotografia (o que entra, o que não
entra), ilustração, grafismos próprios, composição e respiro.
Fonte: `brand/design-language.md` + `brand/identidade-visual.md`.

### 7 · Do's & Don'ts

Tabela dupla (FAÇA × NUNCA FAÇA) cobrindo logo, cor, tipografia, tom e composição —
visual quando possível (miniaturas certo × errado).
Fonte: seções anteriores + `data/padroes-aprovados.md` / `data/padroes-rejeitados.md`.

## Nível COMPLETO (tudo do simplificado +)

### 8 · Exemplos de aplicação (peças REAIS)

Post de feed · capa + 1 slide de carrossel · story · capa de Reels · foto de perfil ·
assinatura de e-mail · papelaria básica (cartão de visita, timbrado).
**Geradas pelo pipeline da agência (compose/generate) como peças de verdade — nunca
mockup desenhado à mão.** Peças aprovadas existentes
(`assets/referencias-aprovadas/`) podem entrar como exemplos.

### 9 · Grid e layout

Margens e áreas seguras por formato, respiro, lockups (arranjos travados de
título/logo/selo). Fonte: `brand/formatos.md` + `brand/design-language.md`.

### 10 · Iconografia e grafismos

Biblioteca oficial de ícones (estilo, peso, quando usar) e grafismos próprios da
marca (anatomia e regras de aplicação). Fonte: `brand/design-language.md` +
`assets/icones/` + `assets/grafismos/`.

### 11 · Aplicação em vídeo

Capas, lower thirds e legendas/telas de texto: fontes, tamanhos e posições seguras.
Fonte: `brand/formatos.md` (vídeo) + `brand/design-language.md`.

### 12 · Acessibilidade

Contrastes mínimos (texto×fundo ≥ 4.5:1; títulos grandes ≥ 3:1), tamanhos mínimos de
texto por meio (digital/impresso) e regras de legibilidade da casa.

### 13 · Galeria do que NUNCA fazer

Contraexemplos VISUAIS: logo esticado, cor fora da paleta, fonte errada, texto
espremido… Gerar as peças-erro deliberadamente pelo pipeline (rápido no compose) —
ver o erro ensina mais que ler a proibição. Fonte: seção 7 +
`data/padroes-rejeitados.md`.

### 14 · Versão, vigência e contato

Versão (v01, v02…), data de vigência, o que mudou desde a anterior, responsável pela
marca e canal para dúvidas `[CONFIRMAR: contato]`.

## Regras de produção

- **Fonte da verdade = `brand/*.md`.** Cada fato do manual (hex, fonte, frase, regra)
  é conferido contra o arquivo de origem; divergência = erro do manual, nunca "versão
  nova" — identidade muda em `brand/` primeiro, o manual acompanha.
- **Formatos de entrega** (os dois podem coexistir):
  - **PADRÃO: site estático one-pager** — time web (`agents/web-design.md` +
    `agents/web-dev.md`), navegação por âncoras, 100% autocontido. O manual
    profissional É uma página web compartilhável com o cliente (abre por `file://`,
    viaja por zip/link) — é também a página usada na aprovação (`--html` +
    `data-aprovacao` por seção);
  - **PDF A4 paginado** — pipeline offline/compose (300dpi, specs em
    `agents/offline.md`), páginas compostas com as fontes reais da marca — quando o
    cliente pedir material impresso/arquivável.
  - Na imersão (estágio 3), o manual simplificado nasce em markdown estruturado
    (este arquivo como esqueleto — a fonte) e é entregue na versão WEB; o PDF vira
    etapa seguinte ou pendência registrada.
- **Exemplos de aplicação = peças reais do pipeline** (compose/generate), com specs e
  prompts arquivados no job. Mockup ilustrativo desenhado à mão não representa o
  sistema — não entra.
- **Porte** (proporcionalidade do `CLAUDE.md`): simplificado = job Padrão · completo
  = job Grande (paralelizar as peças de aplicação com subagents).
- **Aprovação do cliente antes de fechar:** no build web, marcar cada seção com
  `data-aprovacao="<id>"` + `data-titulo="<nome da seção>"` e abrir
  `uv run tools/aprovacao.py --html <site>/index.html --out
  <job>/06-revisao/feedback-manual-r<N>.json` (Bash em background; aguardar o
  término e ler o JSON); seção 👎 volta para ajuste com o comentário do cliente
  como brief; LOOP até `status: "aprovado"` — só então o manual vira vigente e é
  registrado.
- **Registro e vigência:** finais do manual vigente copiados para `brand/manual/`
  (kebab-case com nível e versão — ex.: `manual-simplificado-v01.md` + o site
  autocontido `site-manual-v01/`, `manual-completo-v01-a4.pdf` se houver PDF)
  + registro atualizado em `brand/manual-da-marca.md`
  (versão, data, nível, formato, caminho, pendências). Identidade mudou depois →
  `brand/*.md` E manual atualizados JUNTOS (sincronia via `agents/arquivista.md`).

## Gates (antes de entregar)

Os 3 da casa (marca, ética, qualidade — `templates/checklist-revisao.md`) MAIS a
conferência específica do manual:

- [ ] Fato a fato contra `brand/` — hex a hex, fonte a fonte, frase a frase (a fonte
      da verdade vence o manual)
- [ ] Nenhum conteúdo inventado — o que não está em `brand/` está `[CONFIRMAR]`
- [ ] Exemplos de aplicação são peças reais do pipeline (specs/prompts no job)
- [ ] O manual passa no próprio teste: cada página respeita as regras que ela ensina
- [ ] Versão/vigência preenchida + registro `brand/manual-da-marca.md` atualizado
