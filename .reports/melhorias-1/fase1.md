# Relatório — Fase 1: Correções Fundamentais

**Data:** 2026-06-21  
**Branch:** versao-2  
**Status:** CONCLUÍDA — 162 passed, 1 skipped, 0 falhas

---

## Resumo

Dois gaps corrigidos:

1. **Gap 19 — Escala de distância:** todos os fixtures migrados de coordenadas intercontinentais (SP/RJ scale) para o Distrito Federal (10–90 km). Aviso automático no backend quando enlace excede 200 km.
2. **Gap 18 — Persistência seletiva:** novo endpoint `GET /api/v1/scenarios/{id}/export` com query param `?include_results=true|false`. Serialização separada setup vs. completo. 11 testes novos.

---

## Arquivos Alterados

### Backend

| Arquivo | Alteração |
|---|---|
| `backend/app/schemas/link_scenario.py` | `LinkResult.warnings: list[str] = []`; métodos `export_setup()` e `export_full()` em `LinkScenario` |
| `backend/app/api/link_routes.py` | Aviso > 200 km em `calculate()`; novo endpoint `GET /{id}/export` |
| `backend/app/storage/scenario_storage.py` | `encoding="utf-8"` em todos `write_text()` / `read_text()` (fix Windows cp1252) |

### Testes

| Arquivo | Alteração |
|---|---|
| `tests/test_link_budget.py` | Coords SP/RJ → Plano Piloto/Taguatinga; assert distância `12_000 < d_m < 16_000` |
| `tests/test_site_selection.py` | `BASE_SCENARIO` → Plano Piloto/Taguatinga; `CANDIDATE_NEAR` ~5 km DF; `CANDIDATE_FAR` mantido em lat=-1/lon=-35 (~2200 km) — ver nota abaixo |
| `tests/test_topology.py` | Todos nós migrados para range DF (`lat ∈ [-16.5, -15.5]`, `lon ∈ [-48.5, -47.3]`) |
| `tests/test_kml.py` | KML fixtures, `KML_POINTS`, `SCENARIO_BASE`, assertions lat/lon → DF |
| `tests/test_scenario_export.py` | **Novo** — 11 testes cobrindo setup/full, Content-Disposition, 404, warning presença/ausência |

---

## Detalhes de Implementação

### Escala de Distância

Referência DF adotada:
- **Plano Piloto centro:** lat=-15.7801, lon=-47.9292
- **Taguatinga:** lat=-15.8300, lon=-48.0500 (~13 km W)
- **CANDIDATE_NEAR:** lat=-15.7900, lon=-47.9800 (~5 km de Plano Piloto)

**Decisão sobre CANDIDATE_FAR:** mantido em lat=-1.0, lon=-35.0 (~2200 km do DF). Motivo: o endpoint `site_selection` hardcodeia `tx_power_dbm=20.0` com sensibilidade SF12 (-137 dBm), resultando em alcance teórico FSPL de ~1847 km em espaço livre. Para forçar margem negativa, o candidato precisa estar genuinamente fora desse alcance. Candidatos a ~40–50 km do DF resultam em margem fortemente positiva, tornando o teste de "cobertura insuficiente" impossível sem alterar os parâmetros de RF — o que seria out-of-scope da Fase 1.

### Aviso de Distância

Threshold: 200 km (escopo prático LoRa em campo).  
Implementado em `link_routes.py:calculate()` — produz entrada em `LinkResult.warnings`.  
Não bloqueia o cálculo (warning, não erro).

### Fix de Encoding Windows

`scenario_storage.py` usava `write_text()` / `read_text()` sem `encoding=`, causando `UnicodeEncodeError: 'charmap' codec can't encode character '→'` ao salvar cenários com caracteres especiais (ex: "→" em nomes). Fix: `encoding="utf-8"` explícito em todas as operações de arquivo.

### Endpoint de Exportação

```
GET /api/v1/scenarios/{id}/export
GET /api/v1/scenarios/{id}/export?include_results=true
```

- Setup (padrão): exclui `results`, `topology_result`, `site_selection_result`
- Completo: retorna `model_dump()` completo
- Header: `Content-Disposition: attachment; filename="scenario_{id}_setup.json"` ou `"_completo.json"`
- 404 para cenário inexistente
- Rota original `GET /{id}` não alterada

---

## Testes Executados

```
uv run pytest tests/ -v --tb=short
162 passed, 1 skipped, 0 warnings em 4.44s
```

O skipped é `test_nec_pattern` em `test_antenna_solvers.py` — PyNEC não instalado no ambiente (esperado, documentado no roadmap).

### Cobertura dos critérios da fase

| Critério | Status |
|---|---|
| Zero falhas em `pytest tests/` | ✅ 162 passed |
| Nenhum fixture fora do range DF (exceto CANDIDATE_FAR documentado) | ✅ |
| `GET /export` retorna 200 sem campos de resultado | ✅ `test_export_setup_excludes_results` |
| `GET /export?include_results=true` retorna campos de resultado | ✅ `test_export_full_includes_results` |
| `GET /{id}` original não alterado | ✅ `test_get_scenario_original_unaffected` |

---

## Pendências e Decisões para Fases Futuras

| Item | Fase destino |
|---|---|
| `CANDIDATE_FAR` geograficamente distante — viável resolver só ao implementar parâmetros de RF por candidato (NodeSpec extensions) | Fase 2 |
| Frontend: presets de UI ainda usam coordenadas SP/RJ — aguardando Fase 5 | Fase 5 |
| Frontend: botões de exportação setup/completo não implementados | Fase 5 |
| Botão de aviso de distância não exibido na UI | Fase 5 |

---

## Riscos

- Nenhum risco crítico aberto nesta fase.
- Aviso de 200 km é threshold arbitrário; pode precisar de ajuste empírico quando dados de campo reais estiverem disponíveis (Fase 4/5).
