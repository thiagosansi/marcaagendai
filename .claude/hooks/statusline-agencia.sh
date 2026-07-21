#!/bin/bash
# Barra de status da agência (statusLine do Claude Code — .claude/settings.json).
# Mostra "modelo · pasta · branch" e, numa FILIAL com maquinário da matriz
# pendente, mantém o aviso 📦 FIXO na barra até a atualização entrar.
#
# Sem rede AQUI, nunca: o estado (.git/matriz-pendente, "<sha> <n>") é escrito
# pelo sinalizar-matriz.sh no SessionStart; esta barra só lê e valida LOCALMENTE
# (merge-base). Assim que o /atualizar-agencia mergear o sha, o aviso some e o
# arquivo de estado é removido daqui mesmo. Fail-open em tudo.
#
# Recebe no stdin o JSON da sessão (model.display_name, workspace.project_dir…).

set -u
entrada="$(cat 2>/dev/null || true)"

campo() {  # campo "a.b.c" → valor string do stdin JSON (python3; sem jq)
  printf '%s' "$entrada" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for parte in sys.argv[1].split("."):
    d = d.get(parte) if isinstance(d, dict) else None
    if d is None:
        sys.exit(0)
if isinstance(d, str):
    print(d)
' "$1" 2>/dev/null
}

modelo="$(campo model.display_name)"
projeto="$(campo workspace.project_dir)"
[ -n "$projeto" ] || projeto="${CLAUDE_PROJECT_DIR:-$PWD}"

linha="" ; sep=""
juntar() { [ -n "$1" ] && { linha="$linha$sep$1"; sep=" · "; }; }
juntar "$modelo"
juntar "$(basename "$projeto")"
juntar "$(git -C "$projeto" branch --show-current 2>/dev/null)"

gitdir="$(git -C "$projeto" rev-parse --git-dir 2>/dev/null)"
if [ -n "$gitdir" ]; then
  case "$gitdir" in /*) ;; *) gitdir="$projeto/$gitdir" ;; esac
  pend="$gitdir/matriz-pendente"
  if [ -f "$pend" ]; then
    sha="$(cut -d' ' -f1 "$pend" 2>/dev/null)"
    n="$(cut -d' ' -f2 "$pend" 2>/dev/null)"
    if [ -n "$sha" ] && git -C "$projeto" merge-base --is-ancestor "$sha" HEAD 2>/dev/null; then
      rm -f "$pend" 2>/dev/null   # atualização entrou — aviso sai da barra sozinho
    elif [ -n "$n" ] && [ "$n" != "?" ]; then
      juntar "📦 matriz: $n atualização(ões) — /atualizar-agencia"
    else
      juntar "📦 matriz: maquinário novo — /atualizar-agencia"
    fi
  fi
fi

printf '%s\n' "$linha"
