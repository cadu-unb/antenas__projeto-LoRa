# Prompt — Melhorias 2 — Fase 3

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 3 — Presets Canônicos dos 6 Tipos**. Consulte `.reports/melhorias-2/quadro-antenas.md` para conferir valores vindos do material externo.

## Objetivo

Criar uma fonte única de presets físicos para os 6 tipos de antena, evitando defaults duplicados entre sandbox, solvers, comparação e documentação.

## Arquivos alvo

- Novo arquivo sugerido: `backend/app/domain/antenna_presets.py`
- `backend/app/api/sandbox_routes.py`
- `backend/app/solvers/__init__.py`
- `tests/test_new_antenna_solvers.py`

## Passos

1. Leia o plano e confirme a tabela de presets.
2. Crie um registry único de presets por tipo:
   - `dipolo`: `gmax_dbi=2.15`, `hpbw_deg=78`, `polarization="linear vertical"`, `is_directional=false`, `pattern_model="dipole"`, `practicality_score=8`, `multi_direction_score=9`;
   - `monopolo`: `5.15`, `55`, `linear vertical`, `false`, `monopole`, `7`, `8`;
   - `helicoidal`: `11`, `55`, `circular/elliptical`, `true`, `helical`, `5`, `3`;
   - `parabolica`: `20`, `18`, `feed-dependent`, `true`, `parabolic`, `2`, `1`;
   - `pcb_compact`: `1`, `120`, `linear`, `false`, `pcb`, `10`, `7`;
   - `commercial_omni_6dbi`: `6`, `35`, `linear vertical`, `false`, `omni_colinear`, `9`, `8`.
3. Exponha um helper, por exemplo `apply_antenna_defaults(spec)`.
4. Garanta que o helper aplique defaults em runtime sem modificar arquivos antigos em disco.
5. Preserve distinção entre valor de preset e valor informado explicitamente pelo usuário. Essa distinção será importante para a Fase 4, principalmente em `pcb_compact`.
6. Garanta que o registry de solver continue separado do registry de metadados físicos.
7. Adicione testes unitários para todos os presets.

## Critérios de aceite

- Cada tipo tem preset único e testado.
- `AntennaSpec` mínima recebe defaults em runtime.
- O código não regrava specs antigas só por leitura.
- Fica possível distinguir preset aplicado de valor explícito do usuário.

## Validação

Execute:

```powershell
uv run pytest tests/test_new_antenna_solvers.py
```

Inclua teste de spec mínima:

```python
AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)
```

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase3.md` descrevendo:

- arquivo de presets criado;
- valores finais adotados;
- como defaults são aplicados sem mutar arquivos antigos;
- como valores explícitos do usuário são diferenciados dos presets;
- testes e validações executados.
