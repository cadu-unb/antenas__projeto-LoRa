# 03 — Contratos `propagation/batch`

## Problema

`LinkPair`, `LinkBatchRequest` e `LinkBatchResult` estão em `gis/multi_link.py`. Isso força qualquer simulação batch standalone a importar `gis/`, quebrando a fronteira do Bloco 1.

## Arquivos Alvo

Novos:

- `src/lora_antenna/propagation/batch/__init__.py`
- `src/lora_antenna/propagation/batch/contracts.py`

Modificado:

- `src/lora_antenna/propagation/__init__.py`

## Solução

Criar contratos puros em `propagation/batch/contracts.py`:

- `LinkPair`
- `ScalarLinkInput`
- `LinkBatchRequest`
- `LinkBatchResult`

`ScalarLinkInput` representa os escalares calculados previamente pelo GIS:

- par lógico
- distância 3D
- perda extra total
- número de prédios cruzados

## Campo Obrigatório

`LinkBatchResult` deve incluir:

```python
feasible: bool
```

Regra:

```python
feasible = link_margin_db > 0.0
```

## Restrições

`contracts.py` pode importar:

- `core/`
- `antenna/base.py`
- `propagation/friis.py`

`contracts.py` não pode importar:

- `gis/`
- `network/`
- `shapely`
- `requests`
- `streamlit`

## Validação

- `from lora_antenna.propagation.batch import LinkBatchResult` funciona.
- `rg "from lora_antenna.gis" src/lora_antenna/propagation` não retorna ocorrências.
