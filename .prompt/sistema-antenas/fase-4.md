# Prompt — Sistema de Antenas LoRa — Fase 4

## Objetivo

Implementar Link Budget P2P mínimo.

Esta fase encerra o MVP.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_3.md`, se existir

## Tarefas

1. Criar schemas Pydantic mínimos:
   - `NodeSpec`
   - `LinkSpec`
   - `LinkScenario`
2. Criar `backend/app/api/link_routes.py`.
3. Implementar rotas:

```text
POST /api/v1/scenarios
GET  /api/v1/scenarios/{id}
POST /api/v1/scenarios/{id}/calculate
```

4. Implementar cálculos:
   - distância geodésica;
   - azimute;
   - elevação;
   - FSPL;
   - margem de enlace.
5. Criar `frontend/public/link-planner.html`.
6. Interface deve ter:
   - formulário para dois nós;
   - seleção de antenas da biblioteca;
   - tabela de resultado;
   - semáforo de viabilidade.
7. Semáforo:
   - verde: margem > 10 dB;
   - amarelo: 0 a 10 dB;
   - vermelho: < 0 dB.
8. Exportar cenário como JSON completo.
9. Criar `docs/for-dummies/09-como-montar-enlace.md`.
10. Criar `docs/link-planner-schema.md`.
11. Criar `tests/test_link_budget.py`.

## Checkpoints obrigatórios

- [ ] `POST /api/v1/scenarios/{id}/calculate` retorna margem em dB
- [ ] Distância entre dois pontos GPS reais tem tolerância ±1%
- [ ] FSPL tem tolerância ±0.5 dB para caso conhecido
- [ ] Semáforo mostra cor correta conforme margem
- [ ] Nó aceita `AntennaSpec` da biblioteca
- [ ] Cenário exporta `LinkScenario` completo
- [ ] `pytest tests/test_link_budget.py` passa

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_4.md
```

O relatório deve conter:

- schemas criados;
- rotas criadas;
- fórmulas usadas;
- fixtures de teste;
- resultado dos testes;
- checkpoints marcados;
- confirmação de fim do MVP;
- o que ficou fora do MVP.

## Regra final

Não implemente KML, Leaflet, Longley-Rice ou Ray Tracing nesta fase.
