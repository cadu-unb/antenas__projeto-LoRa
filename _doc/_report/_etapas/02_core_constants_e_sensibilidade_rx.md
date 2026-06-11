# 02 — Core Constants e Sensibilidade RX

## Problema

`src/lora_antenna/core/constants.py` ainda não contém todas as constantes físicas previstas para o Sprint 1 e usa sensibilidade RX conservadora demais para o perfil SX1276/SF12.

## Arquivo Alvo

- `src/lora_antenna/core/constants.py`

## Solução

Adicionar:

```python
Z0_OHM = 50.0
EPSILON_0_F_PER_M = 8.854_187_817e-12
MU_0_H_PER_M = 1.256_637_061_435_917e-6
DEFAULT_RX_SENSITIVITY_DBM = -137.0
```

## Justificativa

- `Z0_OHM` é necessário para impedância, reflexão, VSWR e retorno.
- `EPSILON_0_F_PER_M` e `MU_0_H_PER_M` são constantes base para documentação e fórmulas eletromagnéticas.
- `-137.0 dBm` representa melhor o comportamento SX1276 em SF12/BW125 do que `-110.0 dBm`, que é conservador demais para a ferramenta educacional.

## Cuidados

- Não alterar validação ANATEL `915-928 MHz`.
- Permitir que usuários sobrescrevam sensibilidade em cenários conservadores.

## Validação

- Importar constantes via `from lora_antenna.core.constants import ...`.
- Confirmar que `LinkBatchRequest()` herda o novo default.
- Garantir que testes e exemplos existentes continuam funcionando.
