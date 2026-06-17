# Link Budget

## Conceito

Contabilidade de todos os ganhos e perdas em um enlace de rádio, do transmissor ao receptor. O resultado é a **margem de enlace**: quanto sobrará de sinal acima do limiar mínimo de recepção.

```
Margem = EIRP_tx − FSPL − (limiar_rx − G_rx)
```

Margem positiva = enlace viável. Margem negativa = sinal insuficiente.

## Fórmula completa

```
P_rx (dBm) = P_tx (dBm)
           + G_tx (dBi)
           − L_cabo_tx (dB)
           − FSPL (dB)
           − L_atmosfera (dB)
           + G_rx (dBi)
           − L_cabo_rx (dB)

Margem (dB) = P_rx − S_min
```

Onde:
- `P_tx` = potência de transmissão
- `G_tx`, `G_rx` = ganho das antenas
- `L_cabo_*` = perda de cabos/conectores
- `FSPL` = perda no espaço livre (ver `05-fspl.md`)
- `L_atmosfera` = perdas por chuva/absorção (geralmente 0 em < 6 GHz, < 20 km)
- `S_min` = sensibilidade do receptor (limiar mínimo de recepção)

## Parâmetros implementados no sistema

| Parâmetro | Campo | Unidade |
|---|---|---|
| Potência do transmissor | `p_tx_dbm` | dBm |
| Ganho da antena TX | da spec TX | dBi |
| Ganho da antena RX | da spec RX | dBi |
| Distância | calculada a partir das coordenadas GPS | km |
| FSPL | calculado automaticamente | dB |
| Limiar de recepção | `rx_sensitivity_dbm` | dBm |

## Valores de referência (LoRa 915 MHz)

| Cenário | P_tx | G_tx | Distância | FSPL | G_rx | S_min | Margem |
|---|---|---|---|---|---|---|---|
| Gateway + dipolo, 1 km | 20 dBm | 2 dBi | 1 km | 91.7 dB | 2 dBi | −137 dBm | 69.3 dB |
| Gateway + dipolo, 10 km | 20 dBm | 2 dBi | 10 km | 111.8 dB | 2 dBi | −137 dBm | 49.2 dB |
| Nó + dipolo, 10 km | 14 dBm | 2 dBi | 10 km | 111.8 dB | 2 dBi | −137 dBm | 43.2 dB |

## Semáforo de viabilidade

| Margem | Cor | Interpretação |
|---|---|---|
| > 10 dB | Verde | Enlace robusto |
| 0–10 dB | Amarelo | Enlace marginal — considerar fade margin |
| < 0 dB | Vermelho | Enlace inviável neste cenário |

## Limitações

- FSPL como modelo de propagação: válido apenas em espaço livre
- Sem modelagem de fade margin para desvanecimento multi-caminho
- Perdas atmosféricas ignoradas (aceitável para < 6 GHz e < 50 km)
- Sem modelo de terreno — para terreno irregular usar Longley-Rice + FSPL base

## Referências

- A. F. Molisch, *Wireless Communications*, 2nd ed., Wiley-IEEE, 2011, Cap. 5.
- H. T. Friis, "A Note on a Simple Transmission Formula", *Proc. IRE*, 1946.
- LoRa Alliance, *LoRaWAN Regional Parameters*, v1.0.3, 2018.
