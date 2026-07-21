#!/bin/bash
# Sinalização de atualizações da matriz — roda no SessionStart do Claude Code.
# Numa FILIAL (repo com remote "matriz"), avisa quando a matriz publicou
# maquinário que ainda não entrou aqui. Não toca em nada: só compara e informa.
#
# Saída no formato JSON de hook:
#   - systemMessage ........ aviso VISÍVEL ao usuário na abertura da sessão,
#                            antes de qualquer interação;
#   - additionalContext .... o mesmo aviso no contexto do Claude da filial
#                            (para ele saber e sugerir /atualizar-agencia).
# Estado para a barra de status: .git/matriz-pendente ("<sha> <n>"), lido por
# .claude/hooks/statusline-agencia.sh — mantém o aviso FIXO na barra entre
# checagens; removido quando a filial fica em dia.
#
# Fail-open: qualquer erro (offline, sem remote, fora de repo) sai em silêncio.
# Throttle: no máximo 1 checagem de REDE a cada 6 horas (o arquivo de estado
# segura o aviso na barra de status durante a janela).

set -u
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
# Sem remote "matriz" este repo não é filial (é a própria matriz, ou outro repo).
git remote get-url matriz >/dev/null 2>&1 || exit 0

gitdir="$(git rev-parse --git-dir 2>/dev/null)" || exit 0
stamp="$gitdir/matriz-check-ts"
pendente="$gitdir/matriz-pendente"

now=$(date +%s)
if [ -f "$stamp" ]; then
  last=$(cat "$stamp" 2>/dev/null || echo 0)
  case "$last" in *[!0-9]*) last=0 ;; esac
  [ $((now - last)) -lt 21600 ] && exit 0
fi
echo "$now" > "$stamp" 2>/dev/null

# Uma request só; offline → falha rápida e silenciosa.
remote_sha=$(git ls-remote matriz -h refs/heads/main 2>/dev/null | cut -f1)
[ -n "$remote_sha" ] || exit 0

# Commit remoto já está na nossa história → filial em dia: limpa o estado, silêncio.
if git merge-base --is-ancestor "$remote_sha" HEAD 2>/dev/null; then
  rm -f "$pendente" 2>/dev/null
  exit 0
fi

n=""
if git cat-file -e "$remote_sha" 2>/dev/null; then
  n=$(git rev-list --count "HEAD..$remote_sha" 2>/dev/null || echo "")
fi
if [ -n "$n" ] && [ "$n" != "0" ]; then
  aviso="📦 A matriz da agência tem $n atualização(ões) de maquinário ainda não aplicadas aqui — quando quiser puxar, rode /atualizar-agencia."
else
  aviso="📦 A matriz da agência publicou maquinário novo — quando quiser puxar, rode /atualizar-agencia."
fi

printf '%s %s\n' "$remote_sha" "${n:-?}" > "$pendente" 2>/dev/null

# JSON de hook (texto controlado, sem aspas/backslash — seguro embutir).
printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
  "$aviso" "$aviso"
exit 0
