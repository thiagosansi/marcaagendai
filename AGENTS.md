# agentica-engine — runtime OpenAI (Codex CLI / GPT)

> Este arquivo adapta a agência para runtimes da OpenAI (Codex CLI, GPT).
> **Se você é o Claude Code, ignore este arquivo** — seu manual é o `CLAUDE.md`
> (este arquivo é puramente aditivo e não muda nada no comportamento de lá).

## Manual de operação

Leia e siga **`CLAUDE.md` na íntegra** — ele é o manual completo da agência
(regra zero, pipeline de 7 passos, consulta obrigatória à marca/memória, produção
visual, 3 gates de revisão, formato do resumo final, memória obrigatória).
Tudo vale neste runtime, com as adaptações abaixo.

## Adaptações para este runtime

1. **Blocos de tooling pessoal no `CLAUDE.md`** (imports `@.claude/<tooling>/...`
   no fim do arquivo, quando existirem): ignorar por completo — tooling que não
   existe aqui; não tente ler esses arquivos nem aplicar esses comportamentos.
2. **Sem subagents nem Skill tool**: os papéis de `agents/` e os subagents de
   `.claude/agents/` rodam **inline, em sequência, por você mesmo**. As skills viram
   roteiros manuais: `/imersao-na-marca` = seguir
   `.claude/skills/imersao-na-marca/SKILL.md`; `/atualizar-agencia` = seguir
   `.claude/skills/atualizar-agencia/SKILL.md`. Na MATRIZ (e só nela — ver
   `LICENSE`): `/abrir-filial` = seguir `.claude/skills/abrir-filial/SKILL.md`
   executando `uv run tools/reset_project.py`; essa skill e o motor de export não
   existem nas filiais.
3. **Roteamento de modelos** (tabela haiku/sonnet/opus do `CLAUDE.md`): não se
   aplica — use o modelo da sessão para tudo. A regra que permanece: direção de
   arte, formulação da marca (branding), copy importante e revisão ética são o
   trabalho mais exigente da casa.
4. **Ferramentas**: idênticas — `uv run tools/...` (new_job, generate_image, compose,
   icon, index_assets, fetch_icons, fetch_fonts, entrega, aprovacao, vectorize,
   font_specimen). `.env` igual (`OPENAI_API_KEY`,
   `OPENAI_IMAGE_MODEL`). **Config do Codex**: a sandbox padrão bloqueia rede —
   habilite acesso à rede (ex.: `network_access = true` na config da sessão/projeto)
   para `generate_image.py`, `fetch_*` e pesquisa funcionarem.
5. **`.claude/settings.json`**: config específica do Claude Code (permissões,
   hooks, barra de status) — ignorar.

## Manutenção

Mudou algo estrutural no `CLAUDE.md` (pipeline, skills, tooling)? Revisar se estas
5 adaptações continuam verdadeiras — este arquivo não pode divergir do manual.
