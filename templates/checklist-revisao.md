# Revisão — <job>

Data: AAAA-MM-DD · Revisor: <inline / subagent revisor (modelo)>

## Universal (qualquer marca) — itens DUROS

Valem para toda peça visual, em qualquer marca que rode este harness. Falhou um item
duro → corrigir ANTES de avaliar os gates.

- [ ] Peças finais ABERTAS e inspecionadas (Read) uma a uma — nunca aprovar às cegas
- [ ] Texto sobre rosto/cabeça de pessoa = **reprova**
- [ ] Rosto/cabeça cortado por crop (fit_cover, card, full-bleed) = **reprova** — conferir CADA pessoa em CADA peça
- [ ] Nenhuma sobreposição texto×elemento não intencional (texto invadindo foto, ícone, grafismo ou outro texto)
- [ ] Sidecar `<peça>.warnings.json` do compose conferido: ausente/vazio, OU cada aviso justificado em `01-estrategia/decisoes.md` (aviso não justificado = reprova)
- [ ] Margens e áreas seguras respeitadas (story: topo 250px / base 420px; margens do formato em `brand/formatos.md`)
- [ ] Contraste texto×fundo ≥ 4.5:1 (títulos grandes ≥ 3:1)
- [ ] Composição digital (colagem, recorte, warp): zoom em bordas, costuras e mãos — sem serrilhado nem desalinhamento
- [ ] Métrica de fonte ok — sem colisão de tinta entre linhas/blocos (ascendentes×descendentes), peso realmente renderizado

## Gate 1 · Marca (brand-guardian) — [APROVADO / AJUSTAR / REPROVADO]

Itens específicos da marca vêm de `brand/` — a régua é `brand/design-language.md`.

- [ ] Premium/editorial (não template, não cara de IA)
- [ ] Gramática visual da marca respeitada (`brand/design-language.md`: grafismos, balões, selos, fundos, detalhes-assinatura)
- [ ] Fontes da marca nos papéis certos (`brand/tipografia.md`) · paleta e proporções (`brand/cores.md`)
- [ ] Pessoa INTEGRADA à composição conforme a política da marca (`brand/design-language.md` + `data/memoria-visual.md`)
- [ ] Figurinos/fundos harmonizados entre pessoas na mesma peça
- [ ] Listas, ícones e frases no padrão da casa (`brand/design-language.md`) · frase nunca solta na peça
- [ ] Respiro + hierarquia (máx. 3 níveis; texto nunca espremido em coluna estreita)
- [ ] Logo/selo na regra da marca (`brand/identidade-visual.md` + `brand/logo.md`) e sem distorção
- [ ] Nada de `data/padroes-rejeitados.md` presente
- [ ] Série consistente (se carrossel/sequência)

Itens: …

## Gate 2 · Ética (revisor-etico · `brand/etica-e-saude.md`) — [APROVADO / AJUSTAR / VETADO]

- [ ] Zero cura/garantia/absolutos · [ ] zero conduta individualizada
- [ ] Medo calibrado · [ ] antes/depois ok · [ ] números com fonte
- [ ] Pessoa vulnerável (criança etc.): dignidade + autorização (se foto real)
- [ ] Fatos de oferta confirmados ou [CONFIRMAR] · [ ] urgência real
- [ ] URL/selo de fechamento é do PRODUTO anunciado (mapa produto→URL em `brand/identidade.md`)

Itens: …

## Gate 3 · Qualidade (revisor-qualidade) — [APROVADO / AJUSTAR]

- [ ] Gate de identidade em toda recomposição (lado a lado com a foto real)
- [ ] Legível no celular (mín. 32px em canvas 1080)
- [ ] Português impecável (inclusive dentro das imagens; acentos renderizados)
- [ ] Nomes próprios da marca corretos (`brand/identidade.md`) · [ ] CTA executável
- [ ] Arquivos organizados + resumo.md + histórico registrado

Itens: …

## Conclusão

<pode entregar? o que foi corrigido nesta revisão?>
