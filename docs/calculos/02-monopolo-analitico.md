# Monopolo — Solver Analítico

## Conceito

Monopolo é uma haste condutora sobre plano de terra (GND) condutor infinito. O plano de terra espelha a haste: o sistema se comporta eletricamente como um dipolo completo de comprimento 2h, irradiando apenas no hemisfério superior.

O ganho é exatamente o dobro do dipolo equivalente no mesmo hemisfério: monopolo λ/4 → 5.15 dBi (vs. 2.15 dBi do dipolo λ/2).

## Fórmulas

**Ganho (dBi):**
```
kh = 2π/λ × h
ratio = kh / (π/2)   (1.0 = λ/4 exato)

ratio ≤ 1.0:  G = 5.15 − 6·(1 − ratio)²
ratio > 1.0:  G = 5.15 − 2·(ratio − 1)²
```

**Impedância de entrada (Ω):**
```
ratio ≤ 1.0:  Z = max(1, 36.5·min(ratio,1)²)
```

Nota: impedância do monopolo λ/4 ≈ 36.5 Ω (metade do dipolo λ/2: 73/2 = 36.5 Ω).

**SWR** (referência Z₀ = 50 Ω): mesma fórmula do dipolo.

## Parâmetros de entrada

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `frequency_hz` | Hz | 915e6 | Frequência de operação |
| `height_m` | metros | λ/4 | Altura da haste acima do GND |

## Valores de referência

| Altura | Frequência | Ganho | Impedância | SWR |
|---|---|---|---|---|
| λ/4 | qualquer | 5.15 dBi | 36.5 Ω | 1.37 |
| λ/4 | 915 MHz | 5.15 dBi | 36.5 Ω | 1.37 |
| 0.3λ | 915 MHz | ~4.8 dBi | ~33 Ω | ~1.5 |

## Limitações

- GND assumido perfeito e infinito — na prática GND finito reduz o ganho
- Sem modelagem de perdas no solo real (condutividade σ, permissividade ε)
- Para hastes > λ/2 a fórmula perde validade
- Eficiência fixada em 98% (sem perdas resistivas)

## Referências

- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Cap. 4, Wiley, 2016.
- W. L. Stutzman & G. A. Thiele, *Antenna Theory and Design*, 3rd ed., Wiley, 2012.
