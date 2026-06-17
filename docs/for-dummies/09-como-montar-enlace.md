# Como montar um enlace P2P

## O que é o Link Planner?

Calcula se dois pontos geográficos conseguem se comunicar por rádio com as antenas e parâmetros escolhidos. Resultado: margem de enlace em dB + semáforo de viabilidade.

## Pré-requisitos

- Coordenadas GPS dos dois pontos (latitude e longitude)
- Frequência de operação (ex: 915 MHz para LoRa AU/BR)
- Potência de transmissão (ex: 14 dBm para LoRa padrão)
- Sensibilidade do receptor (ex: -137 dBm para SF12 LoRa)
- Opcional: antenas salvas na biblioteca (para incluir ganho)

## Passo a passo

1. Abra `http://localhost:8000/link-planner.html`
2. Preencha **Nó A** (transmissor):
   - Nome, latitude, longitude, altura sobre solo
   - Selecione antena da biblioteca (opcional)
   - Potência Tx e perda de cabo
3. Preencha **Nó B** (receptor):
   - Nome, latitude, longitude, altura sobre solo
   - Selecione antena da biblioteca (opcional)
   - Sensibilidade Rx e perda de cabo
4. Defina frequência em MHz
5. Clique **Calcular Link Budget**
6. Analise os resultados e o semáforo

## Interpretar os resultados

| Campo | Descrição |
|---|---|
| Distância | Distância geodésica entre os nós (km) |
| Azimute | Direção de A para B em graus (0° = Norte) |
| Elevação | Ângulo vertical de A para B |
| FSPL | Perda no espaço livre — depende de distância e frequência |
| Potência Rx | Potência estimada no receptor (dBm) |
| Margem | Quanto sobra acima da sensibilidade mínima (dB) |

## Semáforo de viabilidade

| Cor | Margem | O que fazer |
|---|---|---|
| 🟢 Verde | > 10 dB | Enlace robusto — pode continuar |
| 🟡 Amarelo | 0 – 10 dB | Marginal — considerar antena com mais ganho ou aumentar Tx |
| 🔴 Vermelho | < 0 dB | Inviável — reduzir distância, aumentar ganho ou mudar frequência |

## Fórmula simplificada

```
Rx (dBm) = Tx (dBm) + G_tx (dBi) - FSPL (dB) + G_rx (dBi)
Margem   = Rx (dBm) - Sensibilidade (dBm)
FSPL     = 20·log10(4π·d·f/c)
```

## Exemplo: Enlace LoRa rural a 5 km, 915 MHz

| Parâmetro | Valor |
|---|---|
| Tx Power | 14 dBm |
| G_tx (dipolo λ/2) | 2.15 dBi |
| Distância | 5000 m |
| Frequência | 915 MHz |
| FSPL | ~105.7 dB |
| G_rx (dipolo λ/2) | 2.15 dBi |
| Rx Power | 14 + 2.15 − 105.7 + 2.15 = **−87.4 dBm** |
| Sensibilidade | −137 dBm |
| **Margem** | **49.6 dB → Verde** |

## Topologias disponíveis

Use a barra de topologia no topo da página:

| Topologia | Descrição | Nó A é... |
|---|---|---|
| P2P | Um enlace direto entre dois nós | Transmissor |
| Cadeia | Série de nós em linha | Início da cadeia |
| Estrela | Hub central conectado a múltiplos nós | Hub central |

Cadeia e Estrela permitem adicionar nós extras manualmente ou via KML.

## Importar nós via KML

Arquivo `.kml` do Google Earth ou similar:

1. Preencha Nó A e Nó B
2. Clique **Importar KML**
3. Selecione o arquivo `.kml`
4. Nós importados aparecem no mapa e na seção de nós extras
5. Selecione topologia Cadeia ou Estrela para incluí-los no enlace

Ver guia completo em `docs/for-dummies/08-como-importar-kml.md`.

## Mapa Leaflet

O mapa mostra automaticamente:
- Nó A (azul) e Nó B (verde)
- Nós extras manuais ou importados (laranja)
- Linhas de enlace (vermelho tracejado) por topologia
- Polígonos KML (roxo, apenas visual)

## Exportar o cenário

Após calcular, clique **Exportar JSON** para baixar o `LinkScenario` completo (nós, parâmetros, resultado). Útil para documentação ou importar em outro momento.

## Limitações desta versão

- Sem modelo de terreno — assume espaço livre (FSPL puro)
- Sem obstáculos físicos (árvores, prédios, montanhas)
- Sem efeitos atmosféricos
- Apenas enlace P2P — sem multi-hop ou topologias avançadas
- Modelos avançados (Longley-Rice, Okumura-Hata) chegam na Fase 6
