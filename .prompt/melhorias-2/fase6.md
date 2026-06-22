# Prompt — Melhorias 2 — Fase 6

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 6 — Ranking com Scores de Antena**. Esta fase depende dos presets e campos da Fase 3.

## Objetivo

Atualizar o ranking de comparação para usar `is_directional`, `multi_direction_score` e `practicality_score`, reduzindo inferência fixa por nome de tipo.

## Arquivos alvo

- `backend/app/domain/comparison.py`
- `tests/test_comparison.py`

## Passos

1. Leia o plano e confirme os campos disponíveis via spec/preset:
   - `is_directional`;
   - `multi_direction_score`;
   - `practicality_score`.
2. Remova ou reduza dependência da lista fixa `_DIRECTIONAL` quando `is_directional` estiver disponível.
3. Use `multi_direction_score` no cálculo de robustez quando existir.
4. Use `practicality_score` no ranking agregado.
5. Defina os campos de saída necessários em `ComparisonRow` ou estrutura equivalente:
   - score de robustez;
   - score de praticidade, se entrar no ranking;
   - score agregado, se houver;
   - justificativa mínima para penalidade de antena diretiva, se cabível.
6. Preserve fallback atual para specs antigas sem scores.
7. Garanta penalidade para gateway com antena muito diretiva em cenário multi-azimute.
8. Adicione testes comparando `Commercial_Omni_6dBi` e parabólica em cenário multi-sensor.

## Critérios de aceite

- `Commercial_Omni_6dBi` tende a ranquear melhor em gateway multi-azimute que parabólica.
- Parabólica apontada pode continuar boa em P2P, mas sofre em cenário multi-sensor.
- Resultados antigos não quebram quando os scores faltam.
- A saída do ranking deixa claro quais scores foram usados.

## Validação

Execute:

```powershell
uv run pytest tests/test_comparison.py
```

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase6.md` descrevendo:

- mudanças no cálculo de robustez/ranking;
- campos adicionados ou alterados na saída;
- fallbacks mantidos;
- testes criados ou alterados;
- validações executadas;
- pendências ou riscos restantes.
