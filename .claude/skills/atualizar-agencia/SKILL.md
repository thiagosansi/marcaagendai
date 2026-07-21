---
name: atualizar-agencia
description: Puxa as atualizações de maquinário da matriz para esta filial - fetch + merge git com a marca blindada (merge=ours em brand/, data/, outputs/, assets/, anexos/, referencias/ e .env), remoção do maquinário exclusivo da matriz e resumo do que entrou. Uso - /atualizar-agencia. Filial antiga sem história compartilhada usa --allow-unrelated-histories uma única vez.
---

# Atualizar a agência — puxar maquinário novo da matriz

Objetivo: trazer para esta filial as melhorias de maquinário publicadas na matriz
(remote `matriz`) por um merge git normal — com histórico, diff e possibilidade de
revert — sem NUNCA atropelar conteúdo da marca.

## Passos

1. **Guard — isto é uma filial assinada?**
   ```bash
   git remote get-url matriz
   ```
   Sem remote `matriz` → este repo não é uma filial assinada (pode ser a própria
   matriz). Explicar ao usuário; se ele quiser assinar este repo, configurar:
   ```bash
   git remote add matriz https://github.com/afialho/agentica-engine.git
   ```

2. **Working tree limpo.** `git status` sujo → commitar antes (ou orientar o
   usuário). Nunca mergear por cima de trabalho não salvo.

3. **Blindagem ativa.** O `.gitattributes` da matriz marca `brand/`, `data/`,
   `outputs/`, `assets/`, `anexos/`, `referencias/` e `.env*` com `merge=ours`:
   conflito nesses caminhos resolve SEMPRE para o lado da filial. O driver
   precisa estar habilitado no repo que faz o merge (idempotente):
   ```bash
   git config merge.ours.driver true
   ```

4. **Buscar e inspecionar o que vem:**
   ```bash
   git fetch matriz
   git rev-list --count HEAD..matriz/main   # 0 = já em dia: avisar e encerrar
   git log --oneline HEAD..matriz/main      # o que vem
   git diff --stat HEAD...matriz/main       # onde mexe
   ```

5. **Merge:**
   ```bash
   git merge matriz/main --no-edit
   ```
   Filial antiga que nunca uniu histórias (erro `refusing to merge unrelated
   histories`) → uma única vez: `git merge matriz/main --allow-unrelated-histories`.
   Desse merge em diante, a rotina volta a ser o comando normal.

6. **Conflitos restantes** (fora dos caminhos blindados — raros):
   - Maquinário puro (`agents/`, `tools/`, `templates/`, `.claude/skills/`):
     lado da MATRIZ.
   - Arquivo com toque da marca (título do `CLAUDE.md`, `.claude/agents/*` com o
     nome da agência): manter o toque da filial e aplicar por cima a mudança
     estrutural da matriz.
   - `.claude/settings.json`: mesclar à mão (união de permissões + hooks).
   Nunca resolver às cegas — olhar o diff dos dois lados antes de escolher.

7. **Maquinário exclusivo da matriz não fica na filial.** Abrir filial é
   operação reservada à matriz (ver `LICENSE`): a skill `/abrir-filial` e o
   motor de export não pertencem a nenhuma filial. Filial antiga ainda os tem,
   e o merge pode trazê-los de volta (arquivo só de um lado entra sem conflito,
   fora do alcance do merge=ours). Depois do merge, remover se existirem:
   ```bash
   git rm -r -q --ignore-unmatch .claude/skills/abrir-filial \
     tools/reset_project.py tools/reset_manifest.json
   git diff --cached --quiet || git commit -m "Remove maquinário exclusivo da matriz"
   ```
   O `LICENSE` é o caso oposto: chega da matriz pelo próprio merge e deve
   permanecer intacto na raiz — nunca remover nem editar.

8. **Fechar e resumir.** Limpar o aviso pendente da barra de status (a barra
   também se limpa sozinha ao detectar o merge — isto só antecipa), fazer backup
   no remoto da filial e resumir ao usuário o que entrou, por área (agents,
   tools, templates, skills), 1 linha por novidade:
   ```bash
   rm -f "$(git rev-parse --git-dir)/matriz-pendente"
   git push origin main
   ```

## Notas

- O hook `.claude/hooks/sinalizar-matriz.sh` (SessionStart) é quem avisa que
  existe atualização pendente — aviso VISÍVEL na abertura da sessão
  (`systemMessage`) + contexto para o Claude; checagem com throttle de 6h,
  silenciosa offline. Entre checagens, o aviso fica FIXO na barra de status
  (`.claude/hooks/statusline-agencia.sh` lê `.git/matriz-pendente`, sem rede).
  Esta skill é o passo manual que o aviso sugere; nada é aplicado sem o usuário pedir.
- Reverter uma atualização que desagradou: `git revert -m 1 <merge-commit>`.
