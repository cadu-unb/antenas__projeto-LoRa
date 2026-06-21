# Fase 1 — Correções Fundamentais

**Objetivo:** corrigir os dois gaps de infraestrutura que distorcem todos os resultados atuais: a escala de distância dos fixtures/presets (Gap 19) e a ausência de persistência seletiva de cenários (Gap 18).

**Dependências:** nenhuma — pode iniciar imediatamente.
**Arquivos afetados:** `tests/`, `backend/app/api/link_routes.py`, `backend/app/schemas/link_scenario.py`, `frontend/public/link-planner.html`, `frontend/public/js/api-client.js`

---

## Etapa 1 — Correção de Escala de Distância

**Problema:** fixtures de teste usam coordenadas com distâncias de centenas a milhares de km (RJ-SP scale). Presets de UI seguem a mesma escala. LoRa opera em 10–90 km — resultados atuais são fisicamente absurdos.

### 1.1 — Atualizar fixtures de `tests/test_site_selection.py`

Substituir as coordenadas atuais por pontos dentro do Distrito Federal (escala 10–80 km):

```python
# Antigo (escala intercontinental — REMOVER)
BASE_SCENARIO = {
    "node_a": {"lat": -23.50, "lon": -46.60, "height_m": 5},
    "node_b": {"lat": -23.55, "lon": -46.65, "height_m": 5},
}
CANDIDATE_NEAR = {"lat": -23.525, "lon": -46.625, "height_m": 30.0}
CANDIDATE_FAR  = {"lat": -1.0,   "lon": -35.0,   "height_m": 30.0}

# Novo (escala LoRa real — Distrito Federal / Entorno)
BASE_SCENARIO = {
    "node_a": {"lat": -15.7801, "lon": -47.9292, "height_m": 5},   # Plano Piloto centro
    "node_b": {"lat": -15.8300, "lon": -48.0500, "height_m": 5},   # ~13 km W
}
CANDIDATE_NEAR = {"lat": -15.7900, "lon": -47.9800, "height_m": 30.0}   # ~5 km — deve cobrir
CANDIDATE_FAR  = {"lat": -15.6500, "lon": -47.6000, "height_m": 30.0}   # ~37 km NE — margem limítrofe com SF12
```

> **Nota:** com SF12, TX=20 dBm, sensibilidade=-137 dBm e FSPL, o alcance teórico em espaço livre excede 2000 km. Por isso `CANDIDATE_FAR` deve estar a uma distância em que o ambiente urbano/vegetação torna a ligação improvável (>40–50 km), OU os testes de "falha" devem usar parâmetros de link mais fracos (SF7, sensibilidade=-118 dBm, TX=7 dBm). Revisar junto com o ajuste.

### 1.2 — Revisar parâmetros padrão de `NodeSpec` nos fixtures

Em `tests/conftest.py` (se existir) ou em cada arquivo de teste que instancia `NodeSpec` diretamente, verificar `tx_power_dbm`, `rx_sensitivity_dbm` e `cable_loss_db` nos cenários de "falha". Onde o objetivo é testar margem negativa, usar:

```python
# Parâmetros para forçar falha em distância moderada (LoRa realista)
tx_power_dbm = 7          # modo econômico
rx_sensitivity_dbm = -118  # SF7 / HighDataRate — não SF12
cable_loss_db = 3.0
```

### 1.3 — Revisar demais arquivos de teste com coordenadas fixas

Buscar em todo o diretório `tests/` por coordenadas hardcoded com `lon` próximo de `-46` (São Paulo) ou `lat` próximo de `-23`:

```bash
grep -rn "lon.*-46\|lat.*-23\|lon.*-35\|lat.*-1.0" tests/
```

Para cada ocorrência, migrar para o range DF: `lat ∈ [-16.5, -15.5]`, `lon ∈ [-48.5, -47.3]`.

### 1.4 — Adicionar validação de distância no backend

Em `backend/app/domain/link_budget.py`, logo após o cálculo de `haversine()`:

```python
LORA_MAX_PRACTICAL_KM = 200  # aviso, não erro

def compute_link(node_a, node_b, freq_hz, antenna_a=None, antenna_b=None):
    dist_m = haversine(node_a.lat, node_a.lon, node_b.lat, node_b.lon)
    warnings = []
    if dist_m > LORA_MAX_PRACTICAL_KM * 1000:
        warnings.append(
            f"Distância {dist_m/1000:.0f} km excede escopo prático de LoRa ({LORA_MAX_PRACTICAL_KM} km)."
        )
    # ... resto do cálculo
    result.warnings = warnings   # adicionar campo warnings: list[str] ao LinkResult
    return result
```

Adicionar campo `warnings: list[str] = []` ao schema `LinkResult` em `backend/app/schemas/link_scenario.py`.

### 1.5 — Rodar os testes

```bash
uv run pytest tests/ -v
```

Todos devem passar. Se algum teste de cobertura falhar porque `CANDIDATE_FAR` agora "cobre" (margem positiva), ajustar o parâmetro de link desse teste conforme 1.2.

---

## Etapa 2 — Persistência Seletiva de Cenários (Gap 18)

**Problema:** `GET /api/v1/scenarios/{id}` sempre retorna tudo — configuração + resultados. Não há como exportar só a configuração (setup), nem exportar resultados separadamente.

**Solução:** novo endpoint de exportação com query param `?include=results`.

### 2.1 — Adicionar campo `warnings` ao `LinkResult`

Em `backend/app/schemas/link_scenario.py`, localizar a classe `LinkResult` e adicionar:

```python
class LinkResult(BaseModel):
    # campos existentes...
    warnings: list[str] = []
```

### 2.2 — Criar helper de serialização no schema

Em `backend/app/schemas/link_scenario.py`, adicionar método ao `LinkScenario`:

```python
class LinkScenario(BaseModel):
    # campos existentes...

    def export_setup(self) -> dict:
        """Retorna apenas campos de configuração, sem resultados."""
        return self.model_dump(
            exclude={"results", "topology_result", "site_selection_result"}
        )

    def export_full(self) -> dict:
        """Retorna tudo — configuração + resultados."""
        return self.model_dump()
```

### 2.3 — Adicionar endpoint de exportação em `link_routes.py`

Em `backend/app/api/link_routes.py`, após o endpoint `GET /{id}`:

```python
@router.get("/{scenario_id}/export", response_class=JSONResponse)
async def export_scenario(
    scenario_id: str,
    include_results: bool = Query(False, alias="include_results"),
):
    """
    Exporta cenário como JSON para download.
    - ?include_results=false (padrão): apenas configuração (nós, antenas, links, candidatos)
    - ?include_results=true: configuração + todos os resultados de simulação
    """
    scenario = scenario_storage.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    if include_results:
        data = scenario.export_full()
        filename = f"scenario_{scenario_id}_completo.json"
    else:
        data = scenario.export_setup()
        filename = f"scenario_{scenario_id}_setup.json"

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return JSONResponse(content=data, headers=headers)
```

> **Imports necessários:** `from fastapi import Query`, `from fastapi.responses import JSONResponse`.
> Verificar que `scenario_storage` já está importado no arquivo (deve estar, pois outros endpoints o usam).

### 2.4 — Testar o endpoint

```bash
# Exportar apenas setup
curl "http://localhost:8000/api/v1/scenarios/{id}/export" -o setup.json

# Exportar completo (com resultados)
curl "http://localhost:8000/api/v1/scenarios/{id}/export?include_results=true" -o completo.json
```

Verificar que `completo.json` contém `results`, `topology_result` e `site_selection_result` (se calculados), e que `setup.json` não contém nenhum desses campos.

### 2.5 — Escrever teste automatizado

Em `tests/test_scenario_export.py` (criar arquivo):

```python
def test_export_setup_excludes_results(client, scenario_with_results):
    resp = client.get(f"/api/v1/scenarios/{scenario_with_results.id}/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" not in data
    assert "topology_result" not in data
    assert "site_selection_result" not in data

def test_export_full_includes_results(client, scenario_with_results):
    resp = client.get(
        f"/api/v1/scenarios/{scenario_with_results.id}/export?include_results=true"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
```

---

## Critério de Conclusão da Fase 1

- [ ] `uv run pytest tests/ -v` — zero falhas
- [ ] Nenhum fixture de teste usa coordenadas fora do range DF (`lat ∈ [-16.5, -15.5]`, `lon ∈ [-48.5, -47.3]`) ou usa parâmetros de link explicitamente documentados como "modo intercontinental para teste de limite"
- [ ] `GET /api/v1/scenarios/{id}/export` responde 200 com JSON sem campos de resultado
- [ ] `GET /api/v1/scenarios/{id}/export?include_results=true` responde 200 com campos de resultado presentes
- [ ] `GET /api/v1/scenarios/{id}` (rota original) não foi alterado — mantém comportamento existente
