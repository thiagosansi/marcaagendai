# O time da agência

Cada arquivo aqui é um **papel profissional**: missão, forma de pensar, o que decide e
o que entrega. O orquestrador (Claude no contexto principal) incorpora esses papéis em
sequência nos jobs comuns, e os despacha como **subagents paralelos** nos jobs grandes
(ver proporcionalidade e roteamento de modelos no `CLAUDE.md`).

## Fluxo típico de um job padrão

```
atendimento → estrategia (+produto se envolve curso/venda)
           → painel criativo: social-media + marketing-viral + direcao-criativa
           → producao: copywriter → design → producao-visual (→ video/musica/offline)
           → revisao: brand-guardian → revisor-etico → revisor-qualidade
           → arquivista (organiza, registra histórico e memória)
```

## Convenções

- Cabeçalho de cada papel: **Modelo** recomendado (fallback) — vale quando o papel roda
  como subagent; inline, o modelo da sessão faz tudo.
- Papéis leem os arquivos de `brand/` e `data/` indicados neles — nunca criam do zero
  o que a marca já definiu.
- Decisões de cada papel são registradas resumidas em `01-estrategia/decisoes.md` do job.
- Nenhum papel entrega direto ao usuário — quem fecha é o orquestrador, com o resumo
  final padrão.
