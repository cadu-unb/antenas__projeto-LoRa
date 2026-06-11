# 07 — UI CP-4 Standalone e Campo `feasible`

## Problema

A UI standalone futura precisa filtrar rapidamente enlaces viáveis/inviáveis, mas hoje essa decisão exige recalcular ou interpretar margem e risco.

## Escopo

Plano prospectivo para CP-4. Não exige criar UI agora.

## Campo Central

`LinkBatchResult.feasible`

Regra:

```python
feasible = link_margin_db > 0.0
```

## Uso na UI

Filtros:

- mostrar todos
- mostrar apenas viáveis
- mostrar apenas inviáveis

Visual:

- `feasible=True` e `LOW`: verde
- `feasible=True` e `MEDIUM`: amarelo/laranja
- `feasible=False`: vermelho

## Parâmetros Standalone

- frequência fixa/default dentro de `915-928 MHz`
- potência TX
- ganho TX
- ganho RX
- perdas extras
- distância
- sensibilidade RX
- SF

## Validação

- A UI não calcula Friis diretamente.
- A UI chama funções de domínio.
- A UI não importa `gis/` para simulação ponto a ponto.
