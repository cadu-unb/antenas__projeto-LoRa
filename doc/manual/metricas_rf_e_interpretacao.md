# Métricas RF e Interpretação

## Canais LoRa ANATEL (Brasil)

Segundo a ANATEL, LoRa no Brasil opera **exclusivamente** na faixa 915–928 MHz.
Os 8 canais padronizados com espaçamento de 1,6 MHz são:

| Canal | Frequência (MHz) |
|-------|-----------------|
| 0 | 915,2 |
| 1 | 916,8 |
| 2 | 918,4 |
| 3 | 920,0 |
| 4 | 921,6 |
| 5 | 923,2 |
| 6 | 924,8 |
| 7 | 926,4 |

Qualquer frequência fora de 915–928 MHz é rejeitada com `ValidationError`.

## Equação de Friis

```
Pr = Pt + Gt + Gr − FSPL − perdas_extras   [dBm]
```

| Símbolo | Significado | Unidade |
|---------|-------------|---------|
| `Pr` | Potência recebida | dBm |
| `Pt` | Potência transmitida | dBm |
| `Gt` | Ganho TX | dBi |
| `Gr` | Ganho RX | dBi |
| `FSPL` | Perda no espaço livre | dB |
| `perdas_extras` | Prédios + cabos + margens | dB |

## FSPL (Free-Space Path Loss)

```
FSPL = 20·log10(d) + 20·log10(f) + 20·log10(4π/c)   [dB]
```

Onde `d` é a distância 3D em metros e `f` a frequência em Hz.
A distância 3D inclui diferença de altitude entre os nós.

## Margem de Enlace

```
margem = Pr − sensibilidade_RX   [dB]
```

- `margem > 0` → enlace **viável** (`feasible = True`)
- `margem ≤ 0` → enlace **inviável** (`feasible = False`)
- Margem mínima recomendada para operação robusta: 10 dB

## Sensibilidade RX — SX1276

| SF | BW (kHz) | Sensibilidade típica (dBm) |
|----|----------|---------------------------|
| 7  | 125      | −123 |
| 8  | 125      | −126 |
| 9  | 125      | −129 |
| 10 | 125      | −132 |
| 11 | 125      | −134,5 |
| 12 | 125      | −137 |

O simulador usa `DEFAULT_RX_SENSITIVITY_DBM = −137.0` (SF12/BW125, máxima alcance).

## Risco do Enlace (LinkRisk)

| Classificação | Condição | Interpretação |
|--------------|----------|---------------|
| `LOW` | margem > 20 dB | Enlace robusto |
| `MEDIUM` | 0 < margem ≤ 20 dB | Enlace viável com margem limitada |
| `HIGH` | margem ≤ 0 dB | Enlace inviável |

## SIR — Relação Sinal-Interferência

```
SIR = Pr_sinal − 10·log10(Σ Pr_interferentes_mW)   [dB]
```

Os interferentes são todos os outros transmissores chegando ao mesmo receptor.
A soma é feita em mW (linear), não em dBm.

## Enlace Decodificável (sir_decodable)

O enlace é decodificável se `SIR ≥ limiar_SF`.
Limiares típicos por SF:

| SF | Limiar SIR (dB) |
|----|----------------|
| 7  | −7,5 |
| 8  | −9,0 |
| 9  | −11,5 |
| 10 | −13,5 |
| 11 | −15,0 |
| 12 | −20,0 |

(Valores SX1276 datasheet — ortogonalidade imperfeita entre SFs.)

## Diferença entre `feasible` e `sir_decodable`

| Campo | Pergunta respondida |
|-------|---------------------|
| `feasible` | O enlace tem potência suficiente para superar a sensibilidade do receptor? |
| `sir_decodable` | O sinal consegue ser decodificado apesar dos interferentes presentes? |

Um enlace pode ser `feasible=True` e `sir_decodable=False` quando há muita interferência cocanal.
Um enlace `feasible=False` nunca é decodificável independente do SIR.

## Atenuação por Prédios

Cada prédio cruzado pelo ray tracing 2D adiciona perda padrão de `15 dB` (configurável).
O ray tracing verifica se a linha reta entre origem e destino intersecta polígonos `BUILDING` ou `OBSTACLE`.

## Interpretação Rápida para o Operador

| `feasible` | `sir_decodable` | Ação recomendada |
|------------|-----------------|------------------|
| True | True | Enlace OK |
| True | False | Reduzir interferência: mudar canal ou aumentar SF |
| False | — | Verificar obstruções, aumentar potência/ganho, reduzir distância |
