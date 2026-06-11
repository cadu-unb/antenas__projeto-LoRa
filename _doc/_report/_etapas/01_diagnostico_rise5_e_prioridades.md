# 01 — Diagnóstico Rise 5 e Prioridades

## Problema

A auditoria comparou a arquitetura planejada com a implementação real em `src/lora_antenna/` e encontrou que os gaps principais de interferência foram implementados, mas alguns desvios arquiteturais permanecem.

## Itens Conformes

- Isolamento entre `propagation/` e `gis/` preservado.
- SIR multi-nó implementado em `propagation/interference.py`.
- `LinkRisk` implementado em `propagation/friis.py`.
- `GeographicPosition` com `altitude_srtm_m` implementado.
- Parser KML com suporte a `<Point>` e `<Polygon>`.
- Ray tracing 2D com Shapely implementado.
- Planejamento de canais ANATEL em `network/channel_plan.py`.

## Desvios Priorizados

1. `feasible: bool` ausente em `LinkBatchResult`.
2. Contratos batch ainda localizados em `gis/multi_link.py`.
3. `DistanceMatrix` ainda é alias de `dict`.
4. `DEFAULT_RX_SENSITIVITY_DBM = -110.0` diverge do alvo `-137.0`.
5. Constantes físicas `Z0`, `epsilon_0` e `mu_0` ausentes.

## Priorização

- **Pré-CP-4**: corrigir `feasible`, sensibilidade RX e constantes físicas.
- **Pré-CP-5/6**: criar `propagation/batch/` e mover contratos/executor.
- **Pré-CP-8**: refatorar `DistanceMatrix` e criar tabela de referência P1-P8.

## Critério de Aceite

Esta etapa está resolvida quando cada desvio tiver uma etapa dedicada, com arquivos alvo, plano de alteração e validação esperada.
