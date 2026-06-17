# Modelo Longley-Rice / ITM

## Conceito

Modelo estatístico de perda de percurso para rádio em terreno irregular. Combina:
- Propagação em visada direta (LOS): base em FSPL + correção de terreno
- Difração: modelo de faca (knife-edge) para enlace além do horizonte
- Espalhamento troposférico: para distâncias > 100 km

Desenvolvido por A. G. Longley e P. L. Rice no ESSA/ITS (1968). Adotado pelo NTIA como modelo de referência nos EUA.

## Intervalo de validade

| Parâmetro | Intervalo |
|---|---|
| Frequência | 20 MHz – 20 GHz |
| Distância | 1 – 2000 km |
| Irregularidade Δh | 0–500 m (parâmetro de entrada) |

## Parâmetros de entrada

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `frequency_mhz` | MHz | Frequência de operação |
| `dist_km` | km | Distância entre tx e rx |
| `h_tx_m` | metros | Altura da antena transmissora |
| `h_rx_m` | metros | Altura da antena receptora |
| `delta_h_m` | metros | Irregularidade de terreno. Padrão: 50 m |
| `climate` | 1–7 | Tipo climático ITM. 5 = continental temperado |

**Valores típicos de Δh:**
- Terreno plano: 10 m
- Colinas suaves: 50 m
- Colinas moderadas: 150 m
- Montanhas: 300–500 m

## Determinação de LOS

Distância máxima de visada (raio efetivo Terra k=4/3):
```
d_hor_tx = √(2 · 8495 km · h_tx)
d_hor_rx = √(2 · 8495 km · h_rx)
d_LOS    = d_hor_tx + d_hor_rx
```

Para h_tx=30m, h_rx=2m: d_LOS ≈ 28.4 km.

## Fórmulas por região

**LOS (d ≤ d_LOS):**
```
L = FSPL + A_terreno
```

**Difração (d > d_LOS):**
```
ν = (d − d_LOS) / √(λ · d / 2)
L = FSPL(d_LOS) + J(ν) + A_difração + A_terreno
```

Onde J(ν) é a atenuação de faca (Boithias, 1992).

## Implementação atual

Esta versão é uma implementação analítica simplificada. Não implementa:
- Lookup tables do ITM original (em Fortran)
- Espalhamento troposférico
- Variabilidade estatística (tempo, local, situação)

Para produção com modelos de elevação digital:
- **splat!** (domínio público, usa ITM completo)
- **NTIA/ITS ITM** em C++ (github.com/NTIA/itm)

## Limitações desta implementação

- Terreno tratado como parâmetro escalar (Δh), não perfil real
- Sem variabilidade estatística (ITM original fornece percentis)
- Difração: apenas faca simples — ITM usa método de Bullington completo
- Não inclui efeito de solo (condutividade e permissividade)

## Referências

- A. G. Longley & P. L. Rice, *Prediction of Tropospheric Radio Transmission Loss
  over Irregular Terrain*, ESSA Tech. Rep. ERL 79-ITS 67, 1968.
- G. A. Hufford, A. G. Longley & W. A. Kissick, *A Guide to the Use of the ITS
  Irregular Terrain Model (Longley-Rice Method)*, NTIA Report 82-100, 1982.
- L. Boithias, *Radio Wave Propagation*, McGraw-Hill, 1992.
