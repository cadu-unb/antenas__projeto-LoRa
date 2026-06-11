# 04 — Executor Puro `propagation/batch`

## Problema

O cálculo batch de Friis + SIR está dentro de `gis/multi_link.py`. A matemática RF deve ficar no Bloco 1 e receber apenas escalares.

## Arquivo Alvo

Novo:

- `src/lora_antenna/propagation/batch/executor.py`

## Solução

Criar `execute_link_batch(request, scalar_inputs)`:

1. Recebe `LinkBatchRequest`.
2. Recebe `list[ScalarLinkInput]`.
3. Calcula FSPL.
4. Calcula potência recebida.
5. Calcula margem.
6. Classifica `LinkRisk`.
7. Calcula `feasible`.
8. Calcula SIR considerando links com mesmo destino como interferentes.
9. Retorna `list[LinkBatchResult]`.

## Fronteira

O executor não sabe:

- latitude
- longitude
- KML
- prédio
- Shapely
- SRTM
- mapa
- Streamlit

Ele sabe apenas:

- distância
- frequência
- potência
- ganhos
- perdas
- sensibilidade
- spreading factor

## Validação

- Rodar batch com pares sintéticos sem nenhum import de `gis/`.
- Confirmar que `sir_decodable` é preenchido quando há interferentes.
- Confirmar que `feasible` é `True` somente para margem positiva.
