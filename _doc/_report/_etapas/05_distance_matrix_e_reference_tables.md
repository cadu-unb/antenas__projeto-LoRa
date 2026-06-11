# 05 — DistanceMatrix e Reference Tables

## Problema

`DistanceMatrix` é atualmente `dict[tuple[str, str], float]`, sem metadados de método, sem rastreabilidade e sem delta contra referência.

## Arquivos Alvo

Modificado:

- `src/lora_antenna/gis/distance_matrix.py`

Novo:

- `src/lora_antenna/gis/reference_tables.py`

## Solução `DistanceMatrix`

Criar modelos Pydantic:

- `DistanceMatrixEntry`
- `DistanceMatrix`

Campos de `DistanceMatrixEntry`:

- `origin_label`
- `dest_label`
- `distance_m`
- `method = "WGS84_GEODESIC"`
- `delta_reference_m: float | None`

Métodos de `DistanceMatrix`:

- `to_dict()`
- `get_distance(origin_label, dest_label)`
- `with_reference_delta(reference_table)`

## Solução `reference_tables.py`

Criar tabela estática P1-P8 com 28 pares derivados de `_path/mathlab/EnlacesLora.m`.

Funções:

- `normalize_pair(origin, dest)`
- `reference_distance_m(origin, dest)`
- `delta_reference_m(origin, dest, computed_distance_m)`

## Cuidados

- Manter compatibilidade temporária para funções que ainda esperam `dict`.
- Documentar que a referência MATLAB usa aproximação flat-earth, enquanto Python usa Haversine.

## Validação

- P1-P8 geram 28 entradas.
- `get_distance("P1", "P2")` e `get_distance("P2", "P1")` retornam o mesmo valor.
- `delta_reference_m` fica registrado sem bloquear execução.
