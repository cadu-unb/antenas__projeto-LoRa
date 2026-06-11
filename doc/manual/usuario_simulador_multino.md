# Manual do Usuário — Simulador Multiponto LoRa

## Finalidade

O simulador calcula orçamentos de enlace LoRa entre múltiplos nós georreferenciados.
Para cada par de nós, calcula:

- Potência recebida (dBm) via equação de Friis
- Margem de enlace (dB)
- Viabilidade (`feasible = margem > 0`)
- Relação sinal-interferência (SIR)
- Risco: `LOW / MEDIUM / HIGH`

## Entrada

| Item | Formato | Exemplo |
|------|---------|---------|
| Arquivo de nós e obstáculos | KML 2.2 | `campus.kml` |
| Frequência | MHz, dentro de 915–928 | `915.2` |
| Potência TX | dBm | `14.0` |
| Ganho de antena | dBi | `2.15` |
| Sensibilidade RX | dBm | `−137.0` (SX1276 SF12) |
| Perdas extras | dB | `3.0` |
| Spreading Factor | 7–12 | `12` |

## Nomenclatura de Nós

Rótulos recomendados: `P1`, `P2`, … `P8`.
O rótulo deve coincidir com o campo `<name>` do elemento `<Placemark>` no KML.
Rótulos são case-sensitive: `P1 ≠ p1`.

## Nomenclatura de Polígonos

| Papel | Valor em `<description>` ou `<name>` |
|-------|--------------------------------------|
| Prédio com atenuação | `BUILDING` |
| Obstáculo genérico | `OBSTACLE` |
| Limite do campus | `CAMPUS` |

Polígonos `BUILDING` e `OBSTACLE` são usados no ray tracing 2D.
`CAMPUS` é ignorado no cálculo RF.

## Saída

Cada enlace produz um `LinkBatchResult` com:

| Campo | Tipo | Significado |
|-------|------|-------------|
| `distance_m` | float | Distância 2D horizontal (m) |
| `distance_3d_m` | float | Distância 3D com diferença de altitude (m) |
| `fspl_db` | float | Perda no espaço livre (dB) |
| `extra_loss_db` | float | Atenuação por prédios + perdas extras (dB) |
| `received_power_dbm` | float | Potência recebida (dBm) |
| `link_margin_db` | float | Margem = recebida − sensibilidade (dB) |
| `link_risk` | LOW/MEDIUM/HIGH | Risco do enlace |
| `feasible` | bool | True se margem > 0 |
| `sir_db` | float | SIR em dB (∞ se sem interferentes) |
| `sir_decodable` | bool | SIR acima do limiar para o SF |
| `n_buildings_crossed` | int | Prédios cruzados pelo ray tracing |

## Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `ValidationError: frequency_hz` | Frequência fora de 915–928 MHz | Usar canal ANATEL válido |
| `KeyError: KML point not found` | Rótulo no código ≠ rótulo no KML | Verificar `<name>` no KML |
| `ValueError: At least two KML points` | KML tem menos de 2 pontos | Adicionar mais `<Placemark>` tipo Point |
| `ValueError: distance_m must be positive` | Dois nós na mesma coordenada | Verificar coordenadas duplicadas |
| `feasible=False` em todos os enlaces | Sensibilidade muito restritiva ou distâncias grandes | Verificar parâmetros de antena e SF |
