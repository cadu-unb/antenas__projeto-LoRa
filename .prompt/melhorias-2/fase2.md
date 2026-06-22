# Prompt — Melhorias 2 — Fase 2

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 2 — Evolução Compatível do Schema**. Leia também `.reports/melhorias-2/quadro-antenas.md` para entender quais campos externos devem ser promovidos para `AntennaSpec`.

## Objetivo

Evoluir o schema `AntennaSpec` de forma retrocompatível para armazenar campos físicos explícitos usados na comparação externa MATLAB.

## Arquivos alvo

- `backend/app/schemas/antenna_spec.py`
- `tests/test_library.py`
- `tests/test_new_antenna_solvers.py`
- `docs/antenna-spec-schema.md`

## Passos

1. Leia o plano e confirme os campos novos definidos para `AntennaSpec`.
2. Adicione campos opcionais ao schema:
   - `gmax_dbi`
   - `hpbw_deg`
   - `polarization`
   - `is_directional`
   - `pattern_model`
   - `practicality_score`
   - `multi_direction_score`
   - `notes`
3. Mantenha compatibilidade com specs antigas sem esses campos.
4. Defina claramente o comportamento de `schema_version`:
   - specs antigas não modificadas continuam com `"1.0"`;
   - specs novas ou com campos novos devem usar `"2.0"` na persistência/exportação;
   - evite regravar arquivos antigos apenas por leitura.
5. Adicione validações mínimas:
   - `practicality_score` e `multi_direction_score` entre `0` e `10`, quando preenchidos;
   - `hpbw_deg > 0`, quando preenchido;
   - `gmax_dbi` numérico, quando preenchido.
6. Atualize exemplos de documentação.
7. Adicione ou ajuste testes para garantir que specs antigas carregam e specs novas preservam os campos.

## Critérios de aceite

- Antenas antigas continuam carregando.
- Novas antenas podem ser salvas com campos externos explícitos.
- Os campos continuam opcionais.
- A regra de `schema_version` fica documentada e testada.

## Validação

Execute:

```powershell
uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py
```

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase2.md` descrevendo:

- campos adicionados;
- regra final de versionamento;
- testes criados ou alterados;
- validações executadas;
- pendências ou riscos restantes.
