# Prompt — Sistema de Antenas LoRa — Fase 10

## Objetivo

Implementar Site Selection: onde colocar a estação base e com qual altura de torre.

Usuário marca candidatos, sistema calcula cobertura por candidato e ranqueia.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_9.md`, se existir

## Pré-requisitos

- Fase 6 completa (Okumura-Hata e/ou Longley-Rice funcionando)
- Fase 5 completa (mapa Leaflet, KML de pontos)

## Tarefas

1. Criar schema `CandidateSite`:
   - `id`
   - `name`
   - `lat`
   - `lon`
   - `height_m`
   - `is_existing_tower`
   - `notes`
2. Criar schema `CoverageResult`:
   - por candidato: lista de nós com margem calculada e status semáforo
3. Criar rotas:

```text
POST /api/v1/scenarios/{id}/candidates
GET  /api/v1/scenarios/{id}/candidates
POST /api/v1/scenarios/{id}/site-selection
```

4. KML: reconhecer ponto como torre existente via nome ou tag e importar como `CandidateSite` com `is_existing_tower: true`.
5. UI — mapa:
   - marcador diferente para candidatos vs nós de campo;
   - adicionar candidato por clique no mapa.
6. UI — resultado:
   - tabela ranqueada por % de nós cobertos (margem > 0 dB);
   - candidato com maior cobertura destacado.
7. UI — detalhe por candidato:
   - cada nó de campo com margem e semáforo.
8. UI — slider de altura:
   - usuário ajusta altura da torre;
   - cobertura recalcula sem reload.
9. Criar `docs/for-dummies/16-como-usar-site-selection.md`.
10. Criar `docs/for-dummies/17-como-interpretar-cobertura.md`.
11. Criar `tests/test_site_selection.py`.

## Checkpoints obrigatórios

- [ ] `POST /api/v1/scenarios/{id}/site-selection` retorna ranking com % cobertura
- [ ] Candidato com maior % aparece primeiro na tabela
- [ ] Slider de altura recalcula cobertura sem reload
- [ ] KML com torre existente importa `CandidateSite` com `is_existing_tower: true`
- [ ] Tabela de detalhe mostra margem por nó para candidato selecionado
- [ ] Semáforo por nó consistente com critérios da Fase 4
- [ ] `pytest tests/test_site_selection.py` passa com fixtures documentadas

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_10.md
```

O relatório deve conter:

- schemas criados;
- rotas criadas;
- método de cálculo de cobertura usado;
- lógica do slider de altura;
- fixtures de teste;
- checkpoints marcados;
- limitações conhecidas.

## Restrições

- Não implementar otimização automática de posição (ex: algoritmo que sugere coordenada ideal).
- Slider manual é suficiente para esta fase.

## Regra final

Não implementar Ray Tracing nem KML nível 2 nesta fase.
