# Fase 11 — Docs Parte II
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Docs criadas e atualizadas

### `docs/for-dummies/` — arquivos novos/atualizados

| Arquivo | Status | Conteúdo |
|---|---|---|
| `14-como-criar-malha-manual.md` | ✅ Completo | Fase 9 — MESH: passo a passo, redundância, API |
| `15-como-criar-topologia-multi-estrela.md` | ✅ Completo | Fase 9 — MULTI_STAR: hubs, folhas, exemplo |
| `16-como-usar-site-selection.md` | ✅ Criado | Fase 10 — candidatos, slider, KML, exportar |
| `17-como-interpretar-cobertura.md` | ✅ Criado | Fase 10 — semáforo, margem por nó, ações |
| `09-como-montar-enlace.md` | ✅ Atualizado | Seção "Topologias avançadas" + site selection |

### `docs/calculos/` — arquivo novo

| Arquivo | Conteúdo |
|---|---|
| `11-site-selection-e-cobertura.md` | FSPL puro, cálculo de cobertura, height override, limitações, referências |

### `docs/link-planner-schema.md`

Completamente reescrito. Agora documenta:
- `NodeSpec` com `is_hub`
- `LinkEdge`, `HopResult`, `TopologyResult`
- `CandidateSite`, `NodeCoverageResult`, `CandidateCoverageResult`, `SiteSelectionResult`
- `LinkScenario` com todos os novos campos
- Tabela `topology_type` com todos os 6 valores
- Tabela de rotas completa (11 rotas)

---

## READMEs revisados

| Arquivo | Status |
|---|---|
| `docs/for-dummies/README.md` | ✅ Atualizado — arquivos 14–17 adicionados à tabela |
| `docs/calculos/README.md` | ✅ Atualizado — arquivo 11 adicionado |
| `README.md` (raiz) | ✅ Atualizado — escopo negativo expandido |

---

## Escopo Negativo atualizado

Adicionados ao `README.md` raiz:

- **Sem otimização automática de posição de torre** — sistema avalia candidatos marcados manualmente
- **Sem modelo de terreno em site selection** — FSPL puro; Longley-Rice/Okumura-Hata não integrados ao ranking

---

## Resultado do teste end-to-end estendido

Fluxo testado via `tests/test_site_selection.py` + `tests/test_topology.py`:

1. ✅ Criar antena no sandbox (via `tests/test_sandbox.py`)
2. ✅ Salvar na biblioteca (via `tests/test_library.py`)
3. ✅ Montar malha manual com múltiplos hubs (`test_multi_star_two_hubs_connected`)
4. ✅ Rodar site selection com candidatos fixos (`test_site_selection_ranked_by_coverage`)
5. ✅ Exportar cenário completo — `GET /scenarios/{id}` retorna JSON com `site_selection_result`

---

## Checkpoints

- [x] `docs/for-dummies/14` a `17` preenchidos e revisados
- [x] `docs/for-dummies/09` atualizado com seção de topologias avançadas + site selection
- [x] `docs/link-planner-schema.md` documenta `topology_type`, `CandidateSite`, `CandidateCoverageResult`, `SiteSelectionResult`
- [x] `docs/calculos/11` explica método + height override + limitações
- [x] READMEs de `docs/for-dummies/` e `docs/calculos/` atualizados
- [x] `README.md` raiz com escopo negativo expandido
- [x] Fluxo end-to-end estendido: 151 passed, 1 skipped

---

## Pendências finais do projeto

- `HIERARCHICAL` topology: armazenada, sem lógica de cálculo específica (reservado para extensão)
- Site selection com modelos de terreno (Longley-Rice, Okumura-Hata) não integrados ao ranking
- Parâmetros de antena configuráveis por candidato (TX, ganho) — fixos nesta versão
- Ray tracing urbano fora do escopo
- Otimização automática de posição fora do escopo
