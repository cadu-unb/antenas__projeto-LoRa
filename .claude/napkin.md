# Napkin Runbook

## Curation Rules
- Re-prioritize on every read.
- Keep recurring, high-value notes only.
- Max 10 items per category.
- Each item includes date + "Do instead".

## Execution & Validation (Highest Priority)
1. **[2026-06-10] Respeitar gatekeeping por sprint**
   Do instead: antes de avancar de fase, conferir os criterios de aceite e gates definidos em `doc/architecture/parts/main.md`.
2. **[2026-06-10] Preservar escopo de documentacao tecnica**
   Do instead: manter mudancas focadas no roadmap LoRa/antenas e evitar refatoracoes fora do pedido.

## Shell & Command Reliability
1. **[2026-06-10] Preferir comandos nativos do PowerShell**
   Do instead: usar `Get-ChildItem`, `Get-Content` e `rg` no workspace antes de assumir estrutura de arquivos.
2. **[2026-06-10] Nao mexer em permissoes locais sem pedido explicito**
   Do instead: deixar `.claude/settings.local.json` intacto salvo quando o usuario pedir alteracao de permissoes.

## Domain Behavior Guardrails
1. **[2026-06-10] LoRa Brasil deve ficar em 915-928 MHz**
   Do instead: tratar 433 MHz e 868 MHz como fora da faixa ANATEL para este projeto e anotar/remover essas opcoes em documentacao e testes.
2. **[2026-06-10] Projeto e uma plataforma LoRa/antenas**
   Do instead: alinhar novas decisoes ao MVP de sandbox de simulacao, link budget, padroes de radiacao e cobertura no Campus Darcy Ribeiro.
3. **[2026-06-10] Documentacao e bloqueadora no Sprint 0.5**
   Do instead: priorizar formulas, referencias, casos de teste e matriz de acuracia antes de implementar sprints posteriores.

## User Directives
1. **[2026-06-10] Manter `.claude` instanciada com skills do usuario**
   Do instead: citar `napkin` e `caveman` como referencias operacionais do projeto dentro da pasta `.claude`.
2. **[2026-06-10] `napkin` ativo em todas as sessoes**
   Do instead: ler e curar `.claude/napkin.md` no inicio do trabalho, mantendo apenas orientacoes reutilizaveis.
3. **[2026-06-10] `caveman` citado, mas nao instalado neste ambiente**
   Do instead: preservar a referencia como preferencia do usuario e pedir/ler a skill quando ela ficar disponivel.
