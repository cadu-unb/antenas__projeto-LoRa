# Fase 4 — Features Analíticas

**Objetivo:** implementar as features de análise comparativa que estão no MATLAB de referência mas ausentes no sistema Python — framework de comparação de cenários (A–E), score de robustez direcional, estimativa de consumo energético e seleção minimax de gateway.

**Dependências:** Fases 2 e 3 concluídas.
**Arquivos afetados:** `backend/app/api/link_routes.py`, `backend/app/domain/comparison.py` (novo), `backend/app/domain/energy.py` (novo), `backend/app/schemas/link_scenario.py`

---

## Etapa 1 — Framework de Comparação de Cenários A–E (Gap 5)

**Objetivo:** dado um cenário com N nós, varrer combinações de módulo LoRa × antena TX × antena GW e retornar tabela de resultados (margem mínima, média, falhas, links críticos, confortáveis).

### 1.1 — Criar `backend/app/domain/comparison.py`

```python
from dataclasses import dataclass, field
from typing import Optional
from backend.app.schemas.lora_module import LoRaModule
from backend.app.schemas.antenna_spec import AntennaSpec
from backend.app.domain.link_budget import compute_link
from backend.app.schemas.node_spec import NodeSpec

@dataclass
class ComparisonRow:
    scenario_label: str       # ex: "A", "B", "C" ou "mod:rfm95w | tx:helicoidal | gw:parabolica"
    module_id: str
    tx_antenna_type: str
    gw_antenna_type: str
    min_margin_db: float
    mean_margin_db: float
    max_margin_db: float
    failure_count: int         # enlaces com margem < 0
    critical_count: int        # 0 ≤ margem < 5 dB
    comfortable_count: int     # margem ≥ 10 dB
    robustness_score: float    # ver Etapa 2
    link_margins: list[float] = field(default_factory=list)


def run_comparison(
    sensor_nodes: list[NodeSpec],
    gateway_node: NodeSpec,
    freq_hz: float,
    modules: list[LoRaModule],
    tx_antenna_specs: list[AntennaSpec],
    gw_antenna_specs: list[AntennaSpec],
) -> list[ComparisonRow]:
    """
    Varre todas as combinações módulo × antena_tx × antena_gw.
    Para cada combinação, calcula margem em cada enlace sensor→gateway.
    Retorna lista de ComparisonRow ordenada por min_margin_db decrescente.
    """
    rows = []
    label_counter = 0

    for module in modules:
        for tx_ant in tx_antenna_specs:
            for gw_ant in gw_antenna_specs:
                label_counter += 1
                label = chr(64 + label_counter) if label_counter <= 26 else str(label_counter)

                margins = []
                for sensor in sensor_nodes:
                    # Módulo LoRa define sensibilidade e potência TX
                    node_tx = sensor.model_copy(update={
                        "tx_power_dbm": module.tx_power_options_dbm[-1],   # máxima potência
                        "rx_sensitivity_dbm": module.get_sensitivity(sf=12) or -137.0,
                    })
                    node_gw = gateway_node.model_copy(update={
                        "rx_sensitivity_dbm": module.get_sensitivity(sf=12) or -137.0,
                    })
                    result = compute_link(
                        node_tx, node_gw, freq_hz,
                        antenna_a=tx_ant, antenna_b=gw_ant,
                    )
                    margins.append(result.link_margin_db)

                row = ComparisonRow(
                    scenario_label=label,
                    module_id=module.id,
                    tx_antenna_type=tx_ant.antenna_type,
                    gw_antenna_type=gw_ant.antenna_type,
                    min_margin_db=min(margins),
                    mean_margin_db=sum(margins) / len(margins),
                    max_margin_db=max(margins),
                    failure_count=sum(1 for m in margins if m < 0),
                    critical_count=sum(1 for m in margins if 0 <= m < 5),
                    comfortable_count=sum(1 for m in margins if m >= 10),
                    robustness_score=0.0,   # preenchido na Etapa 2
                    link_margins=margins,
                )
                rows.append(row)

    rows.sort(key=lambda r: r.min_margin_db, reverse=True)
    return rows
```

### 1.2 — Adicionar endpoint de comparação em `link_routes.py`

```python
from backend.app.domain.comparison import run_comparison, ComparisonRow
from backend.app.storage import lora_module_storage
from backend.app.storage import antenna_storage

@router.post("/{scenario_id}/compare", response_model=list[dict])
async def compare_scenarios(
    scenario_id: str,
    module_ids: list[str] = Query(default=[]),
    tx_antenna_ids: list[str] = Query(default=[]),
    gw_antenna_ids: list[str] = Query(default=[]),
):
    """
    Compara combinações módulo × antena_tx × antena_gw para o cenário.
    Retorna tabela ordenada por margem mínima.

    Query params:
    - module_ids: lista de IDs de módulos LoRa (default: todos os 3 do catálogo)
    - tx_antenna_ids: IDs de antenas TX da biblioteca
    - gw_antenna_ids: IDs de antenas de gateway da biblioteca
    """
    scenario = scenario_storage.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    if not module_ids:
        modules = lora_module_storage.list_modules()
    else:
        modules = [lora_module_storage.get_module(m) for m in module_ids]
        modules = [m for m in modules if m is not None]

    # Obter antenas da biblioteca
    all_antennas = antenna_storage.list_antennas()
    tx_ants = [a for a in all_antennas if a.id in tx_antenna_ids] if tx_antenna_ids else all_antennas[:3]
    gw_ants = [a for a in all_antennas if a.id in gw_antenna_ids] if gw_antenna_ids else all_antennas[:3]

    # Nós sensores = node_b + extra_nodes; gateway = node_a (ou nó hub)
    sensor_nodes = [scenario.node_b] + scenario.extra_nodes
    gateway_node = scenario.node_a

    rows = run_comparison(
        sensor_nodes=sensor_nodes,
        gateway_node=gateway_node,
        freq_hz=scenario.frequency_hz,
        modules=modules,
        tx_antenna_specs=tx_ants,
        gw_antenna_specs=gw_ants,
    )

    return [
        {
            "label": r.scenario_label,
            "module": r.module_id,
            "tx_antenna": r.tx_antenna_type,
            "gw_antenna": r.gw_antenna_type,
            "min_margin_db": round(r.min_margin_db, 2),
            "mean_margin_db": round(r.mean_margin_db, 2),
            "failure_count": r.failure_count,
            "critical_count": r.critical_count,
            "comfortable_count": r.comfortable_count,
            "robustness_score": round(r.robustness_score, 3),
        }
        for r in rows
    ]
```

### 1.3 — Testes do framework de comparação

Criar `tests/test_comparison.py`:

```python
def test_comparison_returns_rows_for_all_combinations(client, scenario_with_nodes):
    resp = client.post(f"/api/v1/scenarios/{scenario_with_nodes}/compare")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) > 0
    # Verificar campos presentes
    assert "min_margin_db" in rows[0]
    assert "failure_count" in rows[0]

def test_comparison_sorted_by_min_margin(client, scenario_with_nodes):
    resp = client.post(f"/api/v1/scenarios/{scenario_with_nodes}/compare")
    rows = resp.json()
    margins = [r["min_margin_db"] for r in rows]
    assert margins == sorted(margins, reverse=True)
```

---

## Etapa 2 — Score de Robustez Direcional (Gap 9)

**Objetivo:** penalizar antenas diretivas que não conseguem servir múltiplos nós simultaneamente — uma antena parabólica apontada para um nó específico perde eficácia para os demais.

### 2.1 — Adicionar `robustness_score` à `comparison.py`

```python
def _compute_robustness(margins: list[float], tx_antenna_type: str) -> float:
    """
    Score de robustez: penaliza antenas diretivas com alta variância de margem.

    Fórmula:
      base_score = mean_margin / (std_margin + 1)
      directivity_penalty = 0.5 se antena diretiva E std > 10 dB, senão 1.0
      robustness_score = base_score * directivity_penalty
    
    Antenas diretivas: helicoidal, parabolica, commercial_omni_6dbi (elevação estreita).
    """
    import statistics

    DIRECTIONAL = {"helicoidal", "parabolica", "commercial_omni_6dbi"}

    mean_m = statistics.mean(margins)
    std_m  = statistics.stdev(margins) if len(margins) > 1 else 0.0

    base = mean_m / (std_m + 1.0)

    if tx_antenna_type in DIRECTIONAL and std_m > 10.0:
        penalty = 0.5
    else:
        penalty = 1.0

    return base * penalty


# No loop de run_comparison, após calcular margins:
row.robustness_score = _compute_robustness(margins, tx_ant.antenna_type)
```

---

## Etapa 3 — Estimativa de Consumo Energético (Gap 10)

**Objetivo:** dado um módulo LoRa e parâmetros de transmissão, estimar energia por transmissão e consumo diário.

### 3.1 — Criar `backend/app/domain/energy.py`

```python
from dataclasses import dataclass
from backend.app.schemas.lora_module import LoRaModule

@dataclass
class EnergyEstimate:
    tx_duration_ms: float           # tempo de transmissão por pacote
    energy_per_tx_mj: float         # energia por transmissão (mJ)
    daily_tx_count: int             # número de transmissões por dia
    daily_energy_mj: float          # energia total/dia (mJ)
    daily_energy_mwh: float         # energia total/dia (mWh)
    battery_life_days: float        # duração estimada com bateria de 2000 mAh / 3.3V


def estimate_energy(
    module: LoRaModule,
    tx_power_dbm: float,
    sf: int = 12,
    bw_khz: int = 125,
    payload_bytes: int = 20,
    transmissions_per_day: int = 96,    # a cada 15 min
    battery_capacity_mah: float = 2000,
    battery_voltage_v: float = 3.3,
) -> EnergyEstimate:
    """
    Estima consumo energético de um módulo LoRa.

    Fórmulas:
      ToA = (2^SF / BW) * (payload_bytes * 8 / SF + preamble_symbols)
      E_tx = I_tx * V * ToA
    """
    # Encontrar corrente de TX para a potência solicitada
    options = list(zip(module.tx_power_options_dbm, module.tx_current_options_ma))
    tx_current_ma = module.tx_current_options_ma[-1]  # default: máxima
    for pwr, cur in options:
        if abs(pwr - tx_power_dbm) < 0.5:
            tx_current_ma = cur
            break

    bw_hz = bw_khz * 1000
    symbol_duration_ms = (2 ** sf / bw_hz) * 1000  # ms

    # Time on Air simplificado (sem codificação LoRa completa)
    preamble_ms = 8 * symbol_duration_ms
    payload_symbols = math.ceil(payload_bytes * 8 / sf)
    tx_duration_ms = preamble_ms + payload_symbols * symbol_duration_ms

    # Energia por transmissão: E = I × V × t
    # I em A, V em V, t em s → E em J → converter para mJ
    energy_per_tx_mj = (tx_current_ma / 1000) * battery_voltage_v * (tx_duration_ms / 1000) * 1000

    daily_energy_mj  = energy_per_tx_mj * transmissions_per_day
    daily_energy_mwh = daily_energy_mj / 3600  # 1 mWh = 3600 mJ

    battery_mj = battery_capacity_mah * battery_voltage_v * 3.6  # mAh × V × 3.6 = mJ
    battery_life_days = battery_mj / daily_energy_mj if daily_energy_mj > 0 else float("inf")

    return EnergyEstimate(
        tx_duration_ms=tx_duration_ms,
        energy_per_tx_mj=energy_per_tx_mj,
        daily_tx_count=transmissions_per_day,
        daily_energy_mj=daily_energy_mj,
        daily_energy_mwh=daily_energy_mwh,
        battery_life_days=battery_life_days,
    )

import math  # adicionar ao topo do arquivo
```

### 3.2 — Adicionar endpoint de estimativa energética

Em `library_routes.py` (onde os módulos LoRa estão):

```python
from backend.app.domain.energy import estimate_energy, EnergyEstimate

@router.post("/lora-modules/{module_id}/energy", response_model=dict)
async def estimate_module_energy(
    module_id: str,
    sf: int = Query(12, ge=7, le=12),
    bw_khz: int = Query(125),
    tx_power_dbm: float = Query(20.0),
    payload_bytes: int = Query(20, ge=1, le=255),
    transmissions_per_day: int = Query(96),
):
    module = lora_module_storage.get_module(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")

    est = estimate_energy(module, tx_power_dbm, sf, bw_khz, payload_bytes, transmissions_per_day)
    return {
        "module": module_id,
        "tx_duration_ms": round(est.tx_duration_ms, 2),
        "energy_per_tx_mj": round(est.energy_per_tx_mj, 4),
        "daily_tx_count": est.daily_tx_count,
        "daily_energy_mwh": round(est.daily_energy_mwh, 4),
        "battery_life_days": round(est.battery_life_days, 1) if est.battery_life_days != float("inf") else None,
    }
```

### 3.3 — Testes de energia

```python
def test_energy_sf12_slower_and_more_energy_than_sf7():
    from backend.app.domain.energy import estimate_energy
    module = lora_module_storage.get_module("rfm95w_915")
    e12 = estimate_energy(module, tx_power_dbm=20, sf=12)
    e7  = estimate_energy(module, tx_power_dbm=20, sf=7)
    assert e12.tx_duration_ms > e7.tx_duration_ms
    assert e12.battery_life_days < e7.battery_life_days

def test_energy_endpoint_returns_battery_life(client):
    resp = client.post("/api/v1/library/lora-modules/rfm95w_915/energy?sf=12&tx_power_dbm=20")
    assert resp.status_code == 200
    data = resp.json()
    assert "battery_life_days" in data
    assert data["battery_life_days"] > 1
```

---

## Etapa 4 — Seleção Minimax de Gateway (Gap 8)

**Objetivo:** oferecer modo de seleção de gateway que minimiza a distância máxima a qualquer sensor (minimax), como alternativa ao critério atual de cobertura%.

### 4.1 — Adicionar campo `selection_mode` ao request de site selection

Em `link_routes.py`, no endpoint `POST /{id}/site-selection`, adicionar query param:

```python
@router.post("/{scenario_id}/site-selection")
async def run_site_selection(
    scenario_id: str,
    selection_mode: Literal["coverage", "minimax"] = Query("coverage"),
):
```

### 4.2 — Implementar lógica minimax em `link_budget.py` ou novo módulo

```python
def minimax_gateway_rank(candidates, sensor_nodes, freq_hz, antenna=None):
    """
    Ranqueia candidatos a gateway pelo critério minimax:
    minimiza a distância máxima até qualquer sensor.
    
    Retorna lista de dicts com: candidate_id, max_dist_m, mean_dist_m, rank.
    """
    from backend.app.domain.geometry import geodetic_to_enu
    results = []
    for cand in candidates:
        dists = []
        for sensor in sensor_nodes:
            enu = geodetic_to_enu(
                cand.lat, cand.lon, cand.height_m,
                sensor.lat, sensor.lon, sensor.height_m,
            )
            dists.append(enu.distance_3d)
        results.append({
            "candidate_id": cand.id,
            "max_dist_m": max(dists),
            "mean_dist_m": sum(dists) / len(dists),
        })

    results.sort(key=lambda r: r["max_dist_m"])
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results
```

### 4.3 — Integrar ao endpoint existente

O endpoint `POST /{id}/site-selection` deve chamar `minimax_gateway_rank` quando `selection_mode="minimax"` e o critério de cobertura quando `selection_mode="coverage"`.

### 4.4 — Testes

```python
def test_minimax_ranks_central_candidate_first(client, scenario_with_candidates):
    resp = client.post(
        f"/api/v1/scenarios/{scenario_with_candidates}/site-selection?selection_mode=minimax"
    )
    assert resp.status_code == 200
    # Candidato mais central (menor distância máxima) deve ter rank=1
    data = resp.json()
    assert data[0]["rank"] == 1
```

---

## Critério de Conclusão da Fase 4

- [ ] `uv run pytest tests/ -v` — zero falhas
- [ ] `POST /api/v1/scenarios/{id}/compare` retorna lista com ao menos 1 row e campos `min_margin_db`, `failure_count`, `robustness_score`
- [ ] Comparação retorna rows ordenadas por `min_margin_db` decrescente
- [ ] `POST /api/v1/library/lora-modules/rfm95w_915/energy?sf=12` retorna `battery_life_days > 1`
- [ ] `POST /api/v1/scenarios/{id}/site-selection?selection_mode=minimax` retorna resultado sem erro 422
- [ ] `robustness_score` para antena diretiva com alta variância de margem é menor que para antena omni com mesma margem média
- [ ] Ao final da execução, escrever relatório em `.reports/melhorias-1/fase4.md`

## Relatório Final Obrigatório

Ao concluir esta fase, criar ou atualizar `.reports/melhorias-1/fase4.md` com:

- Resumo do que foi implementado.
- Arquivos alterados.
- Testes/validações executados e resultado.
- Pendências, riscos ou decisões deixadas para fases futuras.
