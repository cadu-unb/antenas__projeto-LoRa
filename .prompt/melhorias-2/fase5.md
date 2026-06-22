# Prompt — Melhorias 2 — Fase 5

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 5 — Polarização Automática**. Consulte `.reports/melhorias-2/quadro-antenas.md` para os campos de polarização vindos do material externo.

## Objetivo

Adicionar estimativa automática de perda de polarização entre antenas, preservando a perda manual já existente em `NodeSpec.polarization_loss_db`.

## Arquivos alvo

- `backend/app/domain/link_budget.py`
- `backend/app/domain/comparison.py`
- `backend/app/schemas/link_scenario.py`
- `tests/test_link_budget.py`
- `tests/test_comparison.py`

## Passos

1. Leia o plano e confirme a regra de polarização.
2. Crie função `estimate_polarization_loss(tx_ant, rx_ant)`.
3. Implemente regra aproximada:
   - circular/elíptica vs linear: `3 dB`;
   - lineares incompatíveis: penalidade pequena configurável;
   - iguais ou desconhecidas: `0 dB`.
4. Some a perda automática com `NodeSpec.polarization_loss_db`.
5. Adicione campo novo `LinkResult.polarization_loss_db: float = 0.0`.
6. Preserve rastreabilidade:
   - não esconda polarização dentro de `extra_loss_db` sem campo separado;
   - defina claramente se `extra_loss_db` continua representando perda total aplicada ou apenas perda manual;
   - se necessário, adicione `total_additional_loss_db` para compatibilidade e clareza.
7. Atualize serialização/API para expor o novo campo.
8. Adicione testes para polarização circular vs linear, duas lineares verticais, perda manual e perda automática somadas.

## Critérios de aceite

- Helicoidal circular/elíptica contra dipolo linear recebe penalidade.
- Duas antenas lineares verticais não recebem penalidade automática.
- Perda manual em `NodeSpec.polarization_loss_db` continua funcionando.
- A resposta de link budget expõe a perda de polarização aplicada.
- A semântica de `extra_loss_db` fica compatível ou claramente migrada.

## Validação

Execute:

```powershell
uv run pytest tests/test_link_budget.py tests/test_comparison.py
```

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase5.md` descrevendo:

- regra de polarização implementada;
- campos novos em `LinkResult`;
- decisão final sobre `extra_loss_db` e perda total;
- testes criados ou alterados;
- validações executadas;
- pendências ou riscos restantes.
