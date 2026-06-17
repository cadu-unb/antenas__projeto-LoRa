# FSPL — Free-Space Path Loss

## Conceito

Perda de percurso no espaço livre. Representa a atenuação do sinal de rádio devido à dispersão esférica da energia — sem reflexões, absorções ou obstruções. É o limite mínimo de perda entre dois pontos.

## Fórmula

```
FSPL (dB) = 20·log₁₀(d) + 20·log₁₀(f) + 92.45
```

Onde:
- `d` = distância em km
- `f` = frequência em GHz

Derivação: FSPL = (4πd/λ)² = (4πdf/c)²

Forma equivalente com MHz e km:
```
FSPL (dB) = 20·log₁₀(d_km) + 20·log₁₀(f_MHz) + 32.44
```

## Parâmetros de entrada

| Parâmetro | Unidade | Intervalo típico | Descrição |
|---|---|---|---|
| `frequency_hz` | Hz | 100 MHz–6 GHz | Frequência de operação |
| `distance_m` | metros | 1 m–2000 km | Distância entre tx e rx |

## Valores de referência (LoRa)

| Distância | Frequência | FSPL |
|---|---|---|
| 1 km | 915 MHz | 91.7 dB |
| 5 km | 915 MHz | 105.8 dB |
| 10 km | 915 MHz | 111.8 dB |
| 1 km | 868 MHz | 91.2 dB |
| 5 km | 868 MHz | 105.3 dB |

## Uso no link budget

```
Margem (dB) = EIRP_tx + G_rx − FSPL − limiar_rx
```

Onde:
- `EIRP_tx = P_tx (dBm) + G_tx (dBi) − perda_cabo (dB)`
- `limiar_rx` = sensibilidade do receptor (ex: −137 dBm para LoRa SF12)

## Limitações

- Assume propagação em linha reta sem obstrução
- Não inclui reflexões, difração, absorção por vegetação ou edificações
- Para terreno real: usar Okumura-Hata (`06`) ou Longley-Rice (`07`)
- Válido para distâncias >> comprimento de onda (campo distante)
- Não considera efeito do solo (reflexão de primeira ordem)

## Referências

- H. T. Friis, "A Note on a Simple Transmission Formula", *Proc. IRE*, vol. 34, pp. 254–256, 1946.
- ITU-R P.525-4, *Calculation of Free-Space Attenuation*, 2019.
