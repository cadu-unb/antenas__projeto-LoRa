# 10 — Critérios de Aceite e Governança

## Critérios Técnicos

- `core/constants.py` contém constantes físicas e sensibilidade RX correta.
- `propagation/batch/` existe e não importa `gis/`.
- `LinkBatchResult` contém `feasible`.
- `gis/multi_link.py` delega execução RF para `propagation/batch/executor.py`.
- `DistanceMatrix` é modelo rastreável, não apenas `dict`.
- Tabela P1-P8 existe em `gis/reference_tables.py`.
- Validação ANATEL `915-928 MHz` permanece ativa.

## Critérios de Fronteira

Comando esperado:

```powershell
rg -n "from lora_antenna\.gis|import lora_antenna\.gis|from lora_antenna\.network|import lora_antenna\.network" src/lora_antenna/propagation src/lora_antenna/core src/lora_antenna/antenna
```

Resultado esperado: nenhuma ocorrência.

## Critérios de Validação Funcional

- Batch sintético sem KML funciona.
- Batch GIS com KML funciona.
- SIR é calculado quando há interferentes.
- `feasible` independe de `sir_decodable`.
- Channel plan reduz ou mantém colisões, nunca aumenta por erro de algoritmo.

## Governança `_plan` vs `_report`

- `_doc/_report/` registra auditorias e estado real observado.
- `_doc/_plan/` registra planos de execução derivados dessas auditorias.
- `_doc/_plan/_etapas/` contém fatiamento operacional para implementação incremental.

## Gate de Saída

O conjunto de etapas é considerado completo quando cada arquivo tiver sido transformado em alteração real ou explicitamente marcado como adiado com justificativa técnica.
