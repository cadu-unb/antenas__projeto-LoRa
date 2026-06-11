# 06 — Refatoração de `gis/multi_link.py`

## Problema

`gis/multi_link.py` acumula duas responsabilidades:

1. Orquestração geográfica.
2. Contratos e execução matemática batch.

Isso torna a UI dependente de GIS mesmo quando só precisa de batch RF.

## Arquivo Alvo

Modificado:

- `src/lora_antenna/gis/multi_link.py`

## Solução

Após criar `propagation/batch/`, `gis/multi_link.py` deve:

1. Receber `KMLDocument`.
2. Calcular ou receber `DistanceMatrix`.
3. Resolver pontos por label.
4. Calcular distância 3D.
5. Executar ray tracing 2D.
6. Montar `ScalarLinkInput`.
7. Montar `LinkBatchRequest`.
8. Chamar `execute_link_batch()`.
9. Retornar `list[LinkBatchResult]`.

## O Que Deve Sair de `gis/multi_link.py`

- Definições de `LinkPair`.
- Definições de `LinkBatchRequest`.
- Definições de `LinkBatchResult`.
- Lógica pura de Friis/SIR.

## O Que Deve Permanecer

- Conversão KML → escalares.
- Seleção de prédios/obstáculos.
- Cálculo de perdas por ray tracing.
- Construção de entradas batch.

## Validação

- `gis/multi_link.py` pode importar `propagation.batch`.
- `propagation.batch` não pode importar `gis`.
- Batch com KML real continua gerando resultados.
