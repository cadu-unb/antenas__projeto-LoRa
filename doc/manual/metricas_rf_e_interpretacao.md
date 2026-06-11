# Métricas RF e Interpretação

## Canais LoRa ANATEL (Brasil)

Segundo a ANATEL, LoRa no Brasil opera **exclusivamente** na faixa **915–928 MHz**.
Qualquer frequência fora desse intervalo é rejeitada com `ValidationError` antes de qualquer cálculo.

Os 8 canais padronizados com espaçamento de 1,6 MHz são:

| Índice | Frequência (MHz) | Frequência (Hz) |
|--------|-----------------|-----------------|
| 0 | 915,2 | 915.200.000 |
| 1 | 916,8 | 916.800.000 |
| 2 | 918,4 | 918.400.000 |
| 3 | 920,0 | 920.000.000 |
| 4 | 921,6 | 921.600.000 |
| 5 | 923,2 | 923.200.000 |
| 6 | 924,8 | 924.800.000 |
| 7 | 926,4 | 926.400.000 |

Frequências como 433 MHz e 868 MHz são utilizadas em outros países mas **não são permitidas pela ANATEL para LoRa no Brasil**. O simulador recusa essas frequências.

## Potência em dBm

dBm é potência relativa a 1 mW:

```
P_dBm = 10 · log10(P_mW)
```

Valores típicos:

| Potência | dBm |
|----------|-----|
| 1 mW | 0 dBm |
| 10 mW | 10 dBm |
| 25 mW (máx. LoRaWAN BR) | 13,98 dBm ≈ 14 dBm |
| 100 mW | 20 dBm |

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

Onde `d` é a **distância 3D** em metros e `f` a frequência em Hz.

A distância 3D inclui a diferença de altitude entre os nós:

```
d_3D = sqrt(d_2D² + Δh²)
```

Usar `d_3D` é conservador: FSPL levemente maior do que com `d_2D` plana, o que é correto fisicamente.

## Margem de Enlace

```
margem = Pr − sensibilidade_RX   [dB]
```

- `margem > 0` → enlace **viável** (`feasible = True`)
- `margem ≤ 0` → enlace **inviável** (`feasible = False`)
- Margem mínima recomendada para operação robusta em campo: 10 dB

## Sensibilidade RX — SX1276

| SF | BW (kHz) | Sensibilidade típica (dBm) |
|----|----------|---------------------------|
| 7  | 125      | −123 |
| 8  | 125      | −126 |
| 9  | 125      | −129 |
| 10 | 125      | −132 |
| 11 | 125      | −134,5 |
| 12 | 125      | −137 |

O simulador usa `DEFAULT_RX_SENSITIVITY_DBM = −137.0` (SF12/BW125 kHz).

**Por que −137,0 dBm como padrão?**  
SF12 é o spreading factor de maior alcance — maximiza tempo no ar e sensibilidade. Usar −137,0 como padrão calcula o enlace no cenário mais favorável de sensibilidade, dando uma estimativa de alcance máximo. Para dimensionamento conservador, usar sensibilidade de SF menor (ex: −123,0 para SF7).

## Risco do Enlace (LinkRisk)

| Classificação | Condição | Interpretação |
|--------------|----------|---------------|
| `LOW` | margem > 20 dB | Enlace robusto — boa margem para desvanecimento e obstáculos não mapeados |
| `MEDIUM` | 0 < margem ≤ 20 dB | Enlace viável com margem limitada — pode falhar com obstruções adicionais |
| `HIGH` | margem ≤ 0 dB | Enlace inviável — potência recebida abaixo da sensibilidade |

## SIR — Relação Sinal-Interferência

```
SIR = Pr_sinal − 10·log10(Σ Pr_interferentes_mW)   [dB]
```

A soma dos interferentes é feita em mW (linear), não em dBm:

```python
interferentes_mW = sum(10 ** (pr_dbm / 10) for pr_dbm in potencias_interferentes)
sir_db = pr_sinal_dbm - 10 * log10(interferentes_mW)
```

Os interferentes são todos os outros transmissores chegando ao mesmo receptor no mesmo canal.

**Caso especial:** enlace único sem outros transmissores → `SIR = ∞`, `sir_decodable = True`.

## Enlace Decodificável (sir_decodable)

O enlace é decodificável se `SIR ≥ limiar_SF`.
Limiares para SX1276 (ortogonalidade imperfeita entre SFs — valores do datasheet):

| SF | Limiar SIR (dB) |
|----|----------------|
| 7  | −7,5 |
| 8  | −9,0 |
| 9  | −11,5 |
| 10 | −13,5 |
| 11 | −15,0 |
| 12 | −20,0 |

LoRa tem limiares SIR negativos porque a modulação chirp permite decodificar mesmo com interferentes mais fortes que o sinal útil.

## Diferença entre `feasible` e `sir_decodable`

| Campo | Pergunta respondida |
|-------|---------------------|
| `feasible` | O enlace tem potência suficiente para superar a sensibilidade do receptor? |
| `sir_decodable` | O sinal consegue ser decodificado apesar dos interferentes presentes? |

Combinações possíveis:

| `feasible` | `sir_decodable` | Diagnóstico | Ação recomendada |
|------------|-----------------|-------------|------------------|
| True | True | Enlace OK | — |
| True | False | Sinal chega mas interferência impede decodificação | Mudar canal, aumentar SF ou reduzir n° de nós co-canal |
| False | — | Sinal não chega | Aumentar potência/ganho, reduzir distância, verificar obstruções |

Um enlace `feasible=False` nunca é decodificável, independente do SIR.

## Atenuação por Prédios

Cada prédio cruzado pelo ray tracing 2D adiciona perda padrão de `15 dB`.
O ray tracing verifica se a linha reta entre origem e destino intersecta polígonos `BUILDING` ou `OBSTACLE`.

`extra_loss_db` no resultado é a soma de: perdas por prédios + perdas extras configuradas pelo usuário.

## Interferência Co-canal e Otimização de Canais

Interferência co-canal ocorre quando dois nós no mesmo canal transmitem simultânea ou quase simultaneamente, degradando o SIR de quem recebe.

A otimização de canais (Welsh-Powell greedy) atribui canais distintos a nós que se interferem mutuamente, reduzindo colisões. O grafo de interferência é construído a partir das entradas `sir_decodable=False` da matriz SIR.

## Distância Haversine vs Referência MATLAB/Flat-earth

O simulador calcula distâncias usando Haversine (distância geodésica sobre elipsoide esférico).
A referência MATLAB usa modelo flat-earth (projeção plana local).

Diferença típica para distâncias curtas (< 1 km):

| Par | Haversine (m) | MATLAB flat-earth (m) | Delta (m) |
|-----|--------------|----------------------|-----------|
| P1–P2 | 399,0 | 399,4 | −0,4 |

O campo `delta_reference_m` em `DistanceMatrixEntry` registra essa diferença para fins de calibração e validação do modelo.
Para distâncias típicas de campus (100–1000 m), a diferença é inferior a 1 m e não impacta o resultado de viabilidade.
