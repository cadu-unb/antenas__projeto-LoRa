# Parabólica — Aproximação de Abertura

## Conceito

Para antenas onde o diâmetro D >> λ (regime de óptica geométrica), o ganho pode ser calculado diretamente a partir da área efetiva de abertura sem resolver distribuição de corrente.

```
G = η × (π D / λ)²
```

Onde η é a eficiência de abertura (típica: 0.55–0.75).

## Por que não usar MoM para parabólica

MoM discretiza a superfície do refletor em segmentos. Para uma parabólica de 0.6 m a 2.4 GHz:
- λ ≈ 12.5 cm → D/λ ≈ 4.8
- Número de segmentos necessários: ~(D/λ)² × 10 ≈ 230 segmentos na superfície
- MoM em regime de óptica geométrica converge para o mesmo resultado da abertura
- Custo computacional muito maior sem ganho de precisão

## Parâmetros de entrada

| Parâmetro | Tipo | Descrição |
|---|---|---|
| Frequência | Hz | Frequência de operação |
| `diameter_m` | metros | Diâmetro do refletor. Padrão: 0.6 m |
| `efficiency` | 0–1 | Eficiência de abertura η. Padrão: 0.55 |

## Saída

| Campo | Valor típico | Descrição |
|---|---|---|
| `gain_dbi` | 20–40 dBi | Ganho calculado |
| `swr` | 1.0 | Assumido casado (ajustado por feed separado) |
| `efficiency_pct` | 55% | η × 100 |
| `beamwidth_deg` | via `extra` | HPBW estimado: 70λ/D |
| `solver_used` | `"abertura"` | Identificador fixo |

## Valores de referência

| Diâmetro | Frequência | Ganho esperado |
|---|---|---|
| 0.6 m | 2.4 GHz | ≈ 24.0 dBi |
| 1.2 m | 2.4 GHz | ≈ 30.1 dBi |
| 0.6 m | 5.8 GHz | ≈ 30.0 dBi |
| 0.9 m | 915 MHz | ≈ 9.3 dBi |

## Limitações

- Não modela difração nas bordas do refletor
- Não inclui perda por iluminação desuniforme do feed
- HPBW empírico (70λ/D) — valor real depende do feed e da curva de iluminação
- Sem padrão de lóbulos laterais (modelo de abertura não os captura)
- Para D < 2λ, a aproximação perde validade

## Referências

- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Cap. 15.
- S. Silver, *Microwave Antenna Theory and Design*, MIT Radiation Lab Series, Vol. 12, 1949.
