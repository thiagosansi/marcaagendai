# agentica-engine

Uma agência de marketing completa para a SUA marca, operando inteiramente dentro do **Claude Code**.

Não é um app. Não tem telas, comandos nem dashboard. Você abre o Claude Code nesta pasta,
escreve um pedido em linguagem natural e a agência pensa, decide, executa, gera as peças
finais (incluindo imagens), organiza tudo em pastas e melhora com o tempo.

```text
Você:   Crie uma sequência de stories para abrir caixinha de perguntas
        sobre um tema do seu nicho.

Agência: entende → consulta memória e marca → decide formato e quantidade →
         escreve copy → compõe as artes finais → revisa (marca, ética, qualidade) →
         entrega em outputs/99999-2026-07-12-1030-stories-caixinha/ + resumo.
```

## Como pedir

Escreva como escreveria para uma agência real. Exemplos que funcionam:

- *Crie um carrossel premium sobre andador infantil.*
- *Crie uma campanha para divulgar o produto principal da marca.*
- *Crie 10 roteiros UGC para Reels.*
- *Crie um certificado premium para as alunas do curso.*
- *Crie uma capa de Reels para um vídeo sobre lavagem nasal.*
- *Pesquise vídeos virais do seu nicho e monte uma biblioteca.*
- *Crie um roteiro para a porta-voz da marca gravar em primeira pessoa.*
- *Não gostei do fundo roxo, deixa mais clean.* ← feedback também é pedido (vira memória)

Você **não** precisa dizer quantidade de slides, formato ou se usa foto das pessoas da marca —
a agência decide e justifica. Se você disser uma quantidade, ela é respeitada à risca.

## Como a agência funciona

O arquivo [`CLAUDE.md`](CLAUDE.md) é o manual de operação que o Claude Code carrega em toda
sessão. Ele define o pipeline: **entender → consultar → decidir → produzir → revisar →
entregar → aprender**.

O "time" está em [`agents/`](agents/): 21 papéis (atendimento, estratégia, branding,
produto, pesquisa, social media, viral, copy, direção criativa, design, logo, web design,
web dev, produção visual, vídeo, música, offline, brand guardian, revisor ético, revisor
de qualidade, arquivista). Para jobs grandes
(campanhas, lotes), papéis rodam como subagents paralelos definidos em `.claude/agents/`.

## Estrutura do repositório

| Pasta | O que é |
|---|---|
| `brand/` | Identidade: marca, público, tom de voz, visual, tipografia, cores, formatos, ética |
| `data/` | **Memória da agência**: padrões aprovados/rejeitados, aprendizados, histórico, índice de assets |
| `agents/` | Os papéis do time (expertise de cada profissional) |
| `templates/` | Formulários que padronizam briefs, carrosséis, roteiros, checklists |
| `assets/` | Fotos, logos, fontes e referências da marca (veja `assets/README.md`) |
| `referencias/` | Biblioteca de pesquisa: virais, inspiração visual, concorrentes |
| `outputs/` | Um job = uma pasta datada com brief, decisões, copy, imagens e finais |
| `tools/` | Scripts mínimos: gerar imagem (OpenAI), compor arte final, indexar assets |

## Memória — como a agência aprende

- `data/padroes-aprovados.md` / `data/padroes-rejeitados.md` — o gosto da casa.
- `data/memoria-copy.md`, `memoria-visual.md`, `memoria-criativa.md`, `memoria-assets.md` —
  aprendizados por disciplina.
- `data/historico-de-trabalhos.md` — uma linha por job entregue.
- `data/insights-de-audiencia.md` — o que a audiência responde bem (alimente com resultados!).

Diga **"aprovado"**, **"não gostei de X"** ou **"faz mais assim"** e a agência registra na
memória antes de qualquer outra coisa. Quanto mais feedback, melhor ela fica.

## Assets — onde colocar seus arquivos

Passe fotos e materiais à agência (anexo ou caminho) — ela cria as subpastas de
`assets/` do SEU contexto (pessoas da marca, produtos, bastidores, logos,
referencias-aprovadas, referencias-rejeitadas) e organiza tudo. Depois peça: *"indexe os assets"* — ou rode:

```bash
uv run tools/index_assets.py
```

Detalhes, convenções de nome e a política de git para fotos: `assets/README.md`.

## Geração de imagens (OpenAI)

1. Copie `.env.example` para `.env` e preencha `OPENAI_API_KEY`.
2. O modelo é configurável em `OPENAI_IMAGE_MODEL` (padrão atual: `gpt-image-2`).
   Nada é hardcodado — quando sair um modelo melhor, troque uma linha no `.env`.
3. Sem chave configurada a agência continua funcionando: entrega copy, roteiros e
   composições tipográficas (que não usam IA) e deixa os prompts prontos.

Texto importante nunca é confiado à IA de imagem: a agência gera o fundo/ilustração e
compõe o texto com as fontes reais da marca (`tools/compose.py` + papéis de
`brand/tipografia.md`, resolvidos em `assets/fontes/mapa-fontes.json`).

## Revisar e aprovar peças

Toda entrega passa por 3 gates antes de chegar a você (marca, ética em saúde, qualidade) —
o checklist fica em `outputs/<job>/06-revisao/`. E toda entrega fecha com uma página
**`entrega.html`** na pasta do job: abra no navegador para ver as peças em mural ou
carrossel, ampliar cada imagem, copiar textos e baixar arquivos. Ao receber:

- **Aprovou** → diga "aprovado" (vira padrão aprovado + candidata a referência).
- **Quer mudar** → diga o quê ("menos caixas", "título maior") — a agência gera `v02` na
  mesma pasta e registra o aprendizado.

## Evoluindo a agência

- Novas regras de marca → edite `brand/*.md` (ou peça: *"atualiza o style guide: …"*).
- Novos papéis → crie `agents/<papel>.md` seguindo o formato dos existentes.
- Referências → peça pesquisa (*"pesquise virais de X"*) e a biblioteca cresce em
  `referencias/biblioteca-viral/`.
- Fatos do curso (preço, datas, módulos) → mantenha `brand/identidade.md` atualizado;
  a agência nunca inventa fatos, ela marca `[CONFIRMAR]`.

## Levar a agência para outra marca — `/abrir-filial` e `/imersao-na-marca`

Pense neste repositório como **uma agência que tem um cliente dentro dela**.
A agência (agentes, ferramentas, pipeline, templates) é reaproveitável para
qualquer marca; o cliente (a marca: identidade, fotos, memórias, trabalhos) não é.
Duas skills separam uma coisa da outra:

### `/abrir-filial <pasta-destino>` — uma cópia da agência, sem levar o cliente junto

**Comando exclusivo da matriz** (este repositório): a skill não viaja para as
filiais, e a licença (`LICENSE`) reserva à matriz a comercialização e a
redistribuição do harness — filial não abre filial.

Você diz **onde criar a cópia** (esse é o único parâmetro — se não disser, a
agência pergunta). Exemplo:

```text
Você:    /abrir-filial ~/agencias/clinica-sorriso
Agência: cria a pasta, copia só o maquinário, limpa qualquer menção à marca,
         verifica, testa e avisa: "filial pronta".
```

O que acontece na prática:

| | Vai para a cópia? |
|---|---|
| Agentes, tools, CLAUDE.md, templates, ícones, fontes | ✅ como estão |
| `brand/` e `data/` (marca e memórias) | 🔄 substituídos por **fichas em branco** — mesmos arquivos, mesma estrutura, campos `[PREENCHER: …]` |
| `outputs/`, fotos, logos, referências, `.env` (chaves) | ❌ ficam de fora |
| Histórico do git | ❌ a cópia nasce com git novo (o histórico do repo-mãe guarda tudo da marca de origem) |

Segurança embutida: um **leak-scan** varre a cópia procurando termos da marca
(nomes, produtos, cidades — lista em `tools/reset_manifest.json`), a agência
reescreve o que for apontado, re-escaneia até ficar limpo e roda um smoke test
(gera uma arte de teste) para provar que nada quebrou.
**Este repositório não é alterado em nada** — é uma cópia; a marca-mãe continua
intacta aqui. (Existe um modo destrutivo `--in-place` que zera ESTE repo, mas ele
só roda com pedido explícito seu e tripla confirmação.)

### `/imersao-na-marca` — o onboarding da marca nova, em estágios com gates

É o outro lado: roda **na pasta exportada**, por quem recebeu a agência.
A pessoa abre o Claude Code lá e diz `/imersao-na-marca`. A agência conduz
**6 estágios com gates de parada** (progresso em `brand/onboarding-status.md`;
a produção só libera quando a imersão fecha):

1. **Setup técnico** — chave de imagem no `.env`, fontes e ícones conferidos;
2. **Materiais (ask-first)** — você aponta o que existe (logo, manual, fotos,
   peças antigas); a agência lê SÓ o apontado, confirma item a item e organiza;
3. **Entrevista + briefing** — perguntas numeradas em blocos digestíveis
   (fatos objetivos + perfil subjetivo da marca);
4. **Identidade & manual** — traduzir o que existe OU criar do zero (plataforma
   de marca, boards A/B/C, logo profissional, manual simplificado **entregue como
   página web**), com **aprovação formal do cliente na página web local**
   (`tools/aprovacao.py`);
5. **Peças-exemplo reais** — **30 peças variadas** (feeds, stories e carrosséis;
   com e sem pessoas, foto real e cena por IA, fundo chapado, claro e escuro)
   aprovadas peça a peça na página — carrossel roda como carrossel de verdade,
   com voto por slide: a agência nasce com o gosto calibrado em arquivo;
6. **Liberação** — checklist final e agência pronta para pedidos em linguagem
   natural.

### O fluxo completo, do início ao fim

```text
1. você:            /abrir-filial ~/agencias/clinica-sorriso
2. você entrega:    a pasta (zip, repositório novo, como preferir)
3. quem recebeu:    abre o Claude Code na pasta → /imersao-na-marca
4. quem recebeu:    responde a entrevista, envia logo/manual/fotos
5. pronto:          a mesma agência daqui, trabalhando para a marca deles
```

### Manter as filiais atualizadas — `/atualizar-agencia`

A filial nasce **assinada**: um remote `matriz` aponta de volta para este
repositório. Quando o maquinário evolui aqui (agente novo, tool melhorada,
regra nova), cada filial puxa as novidades quando quiser:

```text
1. ao abrir a sessão, um aviso 📦 aparece NA HORA se a matriz tem novidades —
   e fica fixo na barra de status até você atualizar
   (checagem automática, no máximo a cada 6h, silenciosa sem internet)
2. você:     /atualizar-agencia
3. agência:  busca, mostra o que vem, faz o merge e resume o que entrou
   (o aviso some da barra sozinho)
```

O conteúdo da marca é **blindado**: em `brand/`, `data/`, `outputs/`, `assets/`,
`anexos/` e `referencias/`, qualquer disputa no merge resolve sempre para o lado
da filial (`.gitattributes` + merge=ours). E como é git, tudo tem histórico —
uma atualização que desagradar se desfaz com um revert.

Bônus para runtimes OpenAI: o `AGENTS.md` na raiz adapta o harness para rodar
também no Codex/GPT (aditivo — não muda nada no Claude Code).

## Requisitos

- [Claude Code](https://claude.com/claude-code) — a agência roda dentro dele.
- [uv](https://docs.astral.sh/uv/) — roda os scripts de `tools/` sem setup de ambiente.
- Chave da OpenAI (opcional, só para geração de imagem por IA).

## Licença

Uso **não comercial** — ver [`LICENSE`](LICENSE). Em resumo: quem recebe uma
filial pode usar e modificar o harness à vontade no próprio negócio, e **tudo
que produzir com ele é seu** (inclusive para vender); mas o harness em si só
pode ser comercializado ou redistribuído pela **matriz** — nenhuma filial pode
vender o produto nem exportar novas cópias.
