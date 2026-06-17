# Dipolo — Solver Analítico

## Conceito

O dipolo de meia onda é a antena de referência universal. O solver analítico calcula ganho, impedância e SWR a partir de fórmulas fechadas sem discretização numérica — resultado instantâneo, < 1 ms.

Para comprimento L ≠ λ/2, a fórmula é parametrizada pelo fator `ratio = kL/π` (onde k = 2π/λ):

```
ratio = (2π/λ × L) / π = L / (λ/2)
```

## Fórmulas

**Ganho (dBi):**
```
ratio ≤ 1.0:  G = 2.15 − 6·(1 − ratio)²
ratio > 1.0:  G = 2.15 − 2·(ratio − 1)²
```

**Impedância de entrada (Ω):**
```
ratio ≤ 1.0:  Z = max(1, 73·min(ratio,1)²)
ratio > 1.0:  Z = 73 + 20·(ratio − 1)
```

**SWR** (referência Z₀ = 50 Ω):
```
Γ = |Z − Z₀| / (Z + Z₀)
SWR = (1 + Γ) / (1 − Γ)
```

## Parâmetros de entrada

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `frequency_hz` | Hz | 915e6 | Frequência de operação |
| `length_m` | metros | λ/2 | Comprimento total do dipolo |

## Valores de referência

| Comprimento | Frequência | Ganho | Impedância | SWR |
|---|---|---|---|---|
| λ/2 | qualquer | 2.15 dBi | 73 Ω | 1.46 |
| λ/2 | 915 MHz | 2.15 dBi | 73 Ω | 1.46 |
| 0.9λ | 915 MHz | ~1.9 dBi | ~95 Ω | ~1.9 |

## Limitações

- Fio fino assumido (raio → 0)
- Sem modelagem de plano de terra ou estrutura de suporte
- Fórmula de impedância é aproximação — NEC-2 é mais preciso para Z
- Não modela perdas resistivas do material (eficiência fixada em 98%)
- Para comprimentos muito fora de λ/2 (ratio < 0.5 ou > 1.5), erro cresce

## Referências

- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Cap. 4, Wiley, 2016.
- R. C. Johnson, *Antenna Engineering Handbook*, 3rd ed., McGraw-Hill, 1993.
