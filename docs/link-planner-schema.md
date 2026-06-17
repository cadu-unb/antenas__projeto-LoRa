# Link Planner — Schemas

Schemas do domínio de planejamento de enlace. Salvos em `backend/data/scenarios/{id}.json`.

---

## NodeSpec

Representa um nó da rede (gateway, sensor, repetidor).

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | Identificador único |
| `name` | string | **sim** | — | Nome legível |
| `lat` | float | **sim** | — | Latitude em graus decimais |
| `lon` | float | **sim** | — | Longitude em graus decimais |
| `height_m` | float | não | `0.0` | Altura sobre o solo em metros |
| `antenna_id` | string \| null | não | `null` | ID da `AntennaSpec` da biblioteca |
| `tx_power_dbm` | float | não | `14.0` | Potência de transmissão em dBm |
| `rx_sensitivity_dbm` | float | não | `-137.0` | Sensibilidade do receptor em dBm |
| `cable_loss_db` | float | não | `0.0` | Perda de cabo/conector em dB |

### Exemplo NodeSpec

```json
{
  "id": "a1b2c3d4-...",
  "name": "Gateway SP",
  "lat": -23.5505,
  "lon": -46.6333,
  "height_m": 30.0,
  "antenna_id": "f9e8d7c6-...",
  "tx_power_dbm": 20.0,
  "rx_sensitivity_dbm": -137.0,
  "cable_loss_db": 0.5
}
```

---

## LinkResult

Resultado calculado de um enlace P2P.

| Campo | Tipo | Unidade | Descrição |
|---|---|---|---|
| `distance_m` | float | m | Distância geodésica (Haversine) |
| `azimuth_deg` | float | ° | Azimute inicial de A→B (0–360°) |
| `elevation_deg` | float | ° | Ângulo de elevação de A→B |
| `fspl_db` | float | dB | FSPL = 20·log10(4π·d·f/c) |
| `rx_power_dbm` | float | dBm | Potência recebida estimada |
| `link_margin_db` | float | dB | Margem = Rx power − sensibilidade |
| `feasibility` | string | — | `"verde"` / `"amarelo"` / `"vermelho"` |

### Critério de viabilidade

| Margem | Semáforo | Significado |
|---|---|---|
| > 10 dB | Verde | Enlace robusto |
| 0 – 10 dB | Amarelo | Enlace marginal — ruído/obstáculos podem derrubar |
| < 0 dB | Vermelho | Enlace inviável com parâmetros atuais |

---

## LinkScenario

Cenário completo — dois nós + resultado.

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | Identificador único |
| `name` | string | **sim** | — | Nome do cenário |
| `node_a` | NodeSpec | **sim** | — | Nó transmissor |
| `node_b` | NodeSpec | **sim** | — | Nó receptor |
| `frequency_hz` | float | **sim** | — | Frequência de operação em Hz |
| `results` | LinkResult \| null | não | `null` | Preenchido após `/calculate` |
| `metadata` | dict | não | `{}` | Dados livres |

### Exemplo LinkScenario (com resultado)

```json
{
  "id": "cc3d2b1a-...",
  "name": "Enlace SP–RJ",
  "node_a": {
    "name": "São Paulo",
    "lat": -23.5505,
    "lon": -46.6333,
    "height_m": 30.0,
    "tx_power_dbm": 20.0,
    "rx_sensitivity_dbm": -137.0,
    "cable_loss_db": 0.0
  },
  "node_b": {
    "name": "Rio de Janeiro",
    "lat": -22.9068,
    "lon": -43.1729,
    "height_m": 30.0,
    "tx_power_dbm": 14.0,
    "rx_sensitivity_dbm": -137.0,
    "cable_loss_db": 0.0
  },
  "frequency_hz": 915000000.0,
  "results": {
    "distance_m": 357468.2,
    "azimuth_deg": 73.14,
    "elevation_deg": 0.0,
    "fspl_db": 133.74,
    "rx_power_dbm": -113.74,
    "link_margin_db": 23.26,
    "feasibility": "verde"
  },
  "metadata": {}
}
```

---

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/scenarios` | Cria cenário (sem calcular) |
| `GET` | `/api/v1/scenarios` | Lista todos os cenários |
| `GET` | `/api/v1/scenarios/{id}` | Retorna cenário por ID |
| `POST` | `/api/v1/scenarios/{id}/calculate` | Calcula link budget e salva results |

---

## Fórmulas usadas

### FSPL (Free Space Path Loss)
```
FSPL (dB) = 20·log10(4π·d·f / c)
```
- `d` = distância em metros
- `f` = frequência em Hz
- `c` = 3×10⁸ m/s

### Haversine (distância geodésica)
```
a = sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)
d = 2·R·atan2(√a, √(1−a))   (R = 6 371 000 m)
```

### Link Budget
```
Rx (dBm) = Tx (dBm) + G_tx (dBi) − L_tx (dB) − FSPL (dB) − L_rx (dB) + G_rx (dBi)
Margem    = Rx (dBm) − Sensibilidade (dBm)
```

### Limitações nesta fase (MVP)
- Sem efeitos de terreno (Longley-Rice — Fase 6)
- Sem perdas adicionais de difração, chuva ou vegetação
- Sem topologias multi-hop (Fase 9)
- Sem KML e mapa (Fase 5)
