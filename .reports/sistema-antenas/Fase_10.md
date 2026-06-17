# Fase 10 — Site Selection / Planejamento de Torre
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Schemas criados

### `CandidateSite`
```python
class CandidateSite(BaseModel):
    id: str  # UUID
    name: str
    lat: float
    lon: float
    height_m: float = 20.0
    is_existing_tower: bool = False
    notes: str = ""
```
Representa candidato a posição de torre. `is_existing_tower=True` para torres importadas via KML.

### `NodeCoverageResult`
```python
class NodeCoverageResult(BaseModel):
    node_id: str
    node_name: str
    distance_m: float
    link_margin_db: float
    feasibility: str
```
Resultado de cobertura para um nó de campo específico avaliado por um candidato.

### `CandidateCoverageResult`
```python
class CandidateCoverageResult(BaseModel):
    candidate_id: str
    candidate_name: str
    height_m: float          # efetivo (pode ser override)
    coverage_pct: float      # % de nós com margem > 0
    node_results: list[NodeCoverageResult]
    feasibility: str         # verde >=80% | amarelo >=50% | vermelho <50%
```

### `SiteSelectionResult`
```python
class SiteSelectionResult(BaseModel):
    candidates: list[CandidateCoverageResult]  # ordenado desc por coverage_pct
```

### Extensões em schemas existentes
- `LinkScenario` → `candidates: list[CandidateSite]` + `site_selection_result: Optional[SiteSelectionResult]`
- `KmlImportResult` → `candidates_imported: int` + `candidates: list[CandidateSite]`

---

## Rotas criadas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/scenarios/{id}/candidates` | Adicionar candidato a torre |
| `GET` | `/api/v1/scenarios/{id}/candidates` | Listar candidatos do cenário |
| `POST` | `/api/v1/scenarios/{id}/site-selection` | Calcular cobertura de todos os candidatos |

### Body de site-selection

```json
{
  "height_overrides": {
    "candidate-id-1": 50.0
  }
}
```

`height_overrides` é opcional. Permite alterar alturas sem modificar o cenário persistido — usado pelo slider da UI.

---

## Método de cálculo de cobertura

Para cada par (candidato, nó de campo):

```
FSPL = 20·log10(4π·d·f / c)
Rx   = 20 dBm + 0 dBi − 0 dB − FSPL + G_rx − L_rx
margem = Rx − sensibilidade_rx

coberto = (margem > 0)
coverage_pct = cobertos / total_nos × 100
```

Parâmetros da torre candidata: TX 20 dBm, ganho 0 dBi, cabo 0 dB (fixos nesta fase).
Parâmetros dos nós de campo: sensibilidade, ganho de antena e perda de cabo da `NodeSpec`.

Sem modelo de terreno — FSPL puro.

---

## KML: detecção de torres

```python
_TOWER_KEYWORDS = {"torre", "tower"}

def _is_tower_name(name: str) -> bool:
    low = name.lower()
    return any(kw in low for kw in _TOWER_KEYWORDS)
```

Placemarks com "torre" ou "tower" no nome → `CandidateSite` com `is_existing_tower=True`. Altitude do KML vira `height_m`.

---

## Lógica do slider de altura

1. "Calcular Cobertura" cria cenário, adiciona candidatos, chama `/site-selection`
2. Slider HTML por candidato: `<input type="range" min="1" max="120">`
3. `oninput` → `updateCandidateHeight()` → `recalculateSiteWithOverrides()`
4. `recalculateSiteWithOverrides()` → `POST /site-selection` com `height_overrides` dos sliders
5. Resultados re-renderizados sem reload

---

## Fixtures de teste

| Fixture | Descrição |
|---|---|
| `BASE_SCENARIO` | 2 nós a ~23.5°S / 46.6°W, 915 MHz, sens -137 dBm |
| `CANDIDATE_NEAR` | ~3 km dos nós → cobertura 100%, verde |
| `CANDIDATE_FAR` | ~2500 km → FSPL ≈ 161 dB → cobertura 0%, vermelho |

---

## Checkpoints

- [x] `POST /api/v1/scenarios/{id}/site-selection` retorna ranking com % cobertura
- [x] Candidato com maior % aparece primeiro na tabela
- [x] Slider de altura recalcula cobertura sem reload
- [x] KML com "torre" no nome importa `CandidateSite` com `is_existing_tower: true`
- [x] Tabela de detalhe mostra margem por nó para candidato selecionado
- [x] Semáforo por nó consistente com critérios da Fase 4
- [x] `pytest tests/test_site_selection.py` passa (17/17)

---

## Resultado dos testes

```
tests/test_site_selection.py — 17 passed
Suite completa               — 151 passed, 1 skipped, 2 warnings in 3.65s
```

---

## Limitações conhecidas

- Parâmetros da torre candidata fixos (20 dBm, 0 dBi) — sem configuração avançada
- FSPL puro — sem terreno, difração, chuva
- `height_m` registrado mas não altera propagação (só UI/referência)
- Sem otimização automática de posição
- Sem ray tracing (fora do MVP)
