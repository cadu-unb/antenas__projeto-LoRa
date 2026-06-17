# Prompt — Sistema de Antenas LoRa — Fase 5

## Objetivo

Implementar importação de KML e mapa Leaflet.

KML nível 0 é obrigatório. KML nível 1 renderiza polígonos apenas como visual.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_4.md`, se existir

## Tarefas

1. Criar `backend/app/domain/kml/parser.py`.
2. Parser deve aceitar:
   - pontos;
   - altitude quando existir;
   - polígonos.
3. Criar rota:

```text
POST /api/v1/scenarios/{id}/kml
```

4. Integrar Leaflet em `link-planner.html`.
5. Renderizar no mapa:
   - nós importados;
   - polígonos importados.
6. Associar antenas da biblioteca aos nós importados.
7. Implementar modos básicos:
   - P2P;
   - cadeia;
   - estrela.
8. Atualizar cálculo de link budget após importação.
9. Criar `docs/for-dummies/08-como-importar-kml.md`.
10. Atualizar `docs/for-dummies/09-como-montar-enlace.md`.

## Restrições

- Não aplicar penalidade física por polígono nesta fase.
- Não chamar polígono de obstáculo físico sem altura, material e modelo de perda.
- Não implementar Ray Tracing.

## Checkpoints obrigatórios

- [ ] KML de pontos importado vira nós no mapa
- [ ] Coordenadas dos nós ficam corretas
- [ ] KML com polígonos renderiza áreas no mapa
- [ ] Nó importado aceita `AntennaSpec`
- [ ] Link budget após KML bate com P2P direto quando não há obstáculos reais
- [ ] Modos P2P, cadeia e estrela aparecem na interface
- [ ] Parser retorna erro claro para KML malformado

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_5.md
```

O relatório deve conter:

- parser criado;
- tipos KML suportados;
- rotas criadas;
- telas alteradas;
- limitações do KML nível 1;
- checkpoints marcados;
- erros conhecidos.

## Regra final

Não implemente penalidade física nem Ray Tracing nesta fase.
