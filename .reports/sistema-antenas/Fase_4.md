# Fase 4 — Link Budget P2P
**Data:** 2026-06-17  
**Status:** ✅ Concluída — **MVP encerrado**

---

## Schemas criados

### `NodeSpec` (`backend/app/schemas/node_spec.py`)

| Campo | Tipo | Padrão |
|---|---|---|
| `id` | UUID auto | — |
| `name` | string | obrigatório |
| `lat` / `lon` | float | obrigatório |
| `height_m` | float | `0.0` |
| `antenna_id` | string\|null | `null` |
| `tx_power_dbm` | float | `14.0` |
| `rx_sensitivity_dbm` | float | `-137.0` |
| `cable_loss_db` | float | `0.0` |

### `LinkResult` + `LinkScenario` (`backend/app/schemas/link_scenario.py`)

`LinkResult`: `distance_m`, `azimuth_deg`, `elevation_deg`, `fspl_db`, `rx_power_dbm`, `link_margin_db`, `feasibility`

`LinkScenario`: `id`, `name`, `node_a`, `node_b`, `frequency_hz`, `results`, `metadata`

---

## Rotas criadas

| Método | Rota | Status | Descrição |
|---|---|---|---|
| `POST` | `/api/v1/scenarios` | 201 | Cria cenário |
| `GET` | `/api/v1/scenarios` | 200 | Lista cenários |
| `GET` | `/api/v1/scenarios/{id}` | 200/404 | Detalhe |
| `POST` | `/api/v1/scenarios/{id}/calculate` | 200/404 | Calcula e persiste result |

---

## Fórmulas usadas

### FSPL
```
FSPL (dB) = 20·log10(4π·d·f / c)
```
Referência: d=1000 m, f=915 MHz → **91.68 dB** (validado no teste `test_fspl_1km_915mhz`)

### Haversine
```
a = sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)
d = 2·R·atan2(√a, √(1−a))   R = 6 371 000 m
```
Referência: (0°,0°)→(1°,0°) → **111 195 m** (tolerância ±1% validada)

### Azimute
```
θ = atan2(sin(Δλ)·cos(φ₂), cos(φ₁)·sin(φ₂) − sin(φ₁)·cos(φ₂)·cos(Δλ))
az = (θ_deg + 360) mod 360
```
Referências: Norte=0°, Leste=90° (validados)

### Link Budget
```
Rx = Tx + G_tx − L_tx − FSPL − L_rx + G_rx
Margem = Rx − Sensibilidade
```

### Semáforo
| Condição | Resultado |
|---|---|
| Margem > 10 dB | `"verde"` |
| 0 ≤ Margem ≤ 10 dB | `"amarelo"` |
| Margem < 0 dB | `"vermelho"` |

---

## Fixtures de teste documentadas

| Fixture | Valor esperado | Tolerância |
|---|---|---|
| FSPL (1 km, 915 MHz) | 91.68 dB | ±0.5 dB |
| Haversine (0°,0°)→(1°,0°) | 111 195 m | ±1% |
| Distância SP→RJ | ~357 km | 350–370 km |
| Azimute Norte | 0° | ±0.01° |
| Azimute Leste | 90° | ±0.1° |

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `backend/app/schemas/node_spec.py` | `NodeSpec` |
| `backend/app/schemas/link_scenario.py` | `LinkResult` + `LinkScenario` |
| `backend/app/domain/__init__.py` | Pacote domain |
| `backend/app/domain/link_budget.py` | Funções analíticas puras |
| `backend/app/storage/scenario_storage.py` | save/load/list cenários |
| `backend/app/api/link_routes.py` | 4 rotas de cenário |
| `frontend/public/link-planner.html` | UI P2P completa |
| `docs/link-planner-schema.md` | Documentação de schemas e fórmulas |
| `docs/for-dummies/09-como-montar-enlace.md` | Guia de usuário |
| `tests/test_link_budget.py` | 26 testes |

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/main.py` | `include_router(link_router)` |
| `frontend/public/js/api-client.js` | `createScenario`, `getScenario`, `calculateScenario` |

---

## Resultado dos testes

```
tests/test_link_budget.py — 26 passed
Suite completa — 46 passed, 1 warning in 1.28s
```

---

## Checkpoints

- [x] `POST /api/v1/scenarios/{id}/calculate` retorna margem em dB
- [x] Distância entre dois pontos GPS (0°,0°)→(1°,0°): 111 195 m ±1%
- [x] FSPL a 1 km, 915 MHz: 91.68 dB ±0.5 dB
- [x] Semáforo mostra cor correta conforme margem (3 casos testados)
- [x] Nó aceita `antenna_id` da biblioteca; gain_dbi usado no cálculo
- [x] Cenário exporta `LinkScenario` completo via GET + download frontend
- [x] `pytest tests/test_link_budget.py` passa — 26 passed

---

## Confirmação de fim do MVP

Fases 0–4 concluídas:

| Fase | Entrega |
|---|---|
| 0 | Convenções, estrutura de pastas, config.py |
| 1 | FastAPI + /health + Docker + testes |
| 2 | AntennaSpec CRUD + biblioteca |
| 3 | Sandbox analítico + 4 painéis + diagrama polar |
| **4** | **Link Budget P2P + semáforo + export** |

---

## O que ficou fora do MVP

| Item | Fase planejada |
|---|---|
| MoM via PyNEC (modos Padrão/Preciso) | 6 |
| Longley-Rice (terreno irregular) | 6 |
| Okumura-Hata (empírico) | 6 |
| Fila de jobs assíncrona | 7 |
| Import de KML | 5 |
| Mapa Leaflet | 5 |
| Topologias multi-hop (malha, estrela, cadeia) | 9 |
| Site selection / planejamento de torre | 10 |
| Ray Tracing | Fora do MVP |
| Detecção automática de obstáculos por imagem | Fora do MVP |
| Modo Experimental | Fora do MVP |
