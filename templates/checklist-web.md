# Checklist web — <job>

Data: AAAA-MM-DD · Revisor: <inline / subagent (modelo)> · Peça: `outputs/<job>/site/`

> Gate técnico do site — complementa os 3 gates da casa (`templates/checklist-revisao.md`).
> Preencher em `06-revisao/checklist-web.md` ANTES de entregar.

## Funciona

- [ ] Abre por `file://` sem servidor e sem internet — renderiza sem erro
- [ ] Console limpo (zero erro; warning só se justificado)
- [ ] Links e CTAs clicados um a um — destino certo (âncoras, externos, WhatsApp)
- [ ] Site íntegro SEM JS (conteúdo visível, navegação ok — JS só realça)

## Responsivo

- [ ] 390 (mobile): sem overflow horizontal, texto legível, alvos de toque confortáveis
- [ ] 768 (tablet): sem quebra estranha de layout
- [ ] 1440 (desktop): composição da direção respeitada
- [ ] Screenshots salvos no job: `06-revisao/screenshot-desktop-1440.png` + `06-revisao/screenshot-mobile-390.png`

## Acessibilidade

- [ ] Contraste AA nos pares usados (4.5:1 corpo, 3:1 texto grande)
- [ ] Foco visível e navegação completa por teclado
- [ ] Toda imagem de conteúdo com `alt` descritivo (decorativa: `alt=""`)
- [ ] `prefers-reduced-motion` respeitado (animações zeradas/reduzidas, nada some)

## Técnica e SEO

- [ ] Fontes da marca via `@font-face` LOCAIS (copiadas para `site/assets/fonts/`, `font-display: swap`) — zero CDN/fonte remota
- [ ] `lang="pt-BR"` + `title` + `meta description` + OG (title/description/image local) + favicon local
- [ ] Imagens otimizadas (dimensão de uso, `loading="lazy"` abaixo da dobra, `width`/`height` declarados)
- [ ] Peso total da página razoável (indicativo < 2MB sem vídeo)

## Marca

- [ ] `brand/design-language.md` respeitada (paleta, tipografia nos papéis certos, grafismos, tom)
- [ ] Layout com ideia própria de web (não é carrossel esticado) e "parece a marca mesmo sem o logo"

## Conclusão

<pode entregar? o que foi corrigido nesta revisão?>
