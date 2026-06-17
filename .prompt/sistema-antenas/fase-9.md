# Prompt — Sistema de Antenas LoRa — Fase 9

## Objetivo

Implementar topologias avançadas: malha manual e multi-estrela.

Malha manual: usuário desenha enlaces livremente no mapa.
Multi-estrela: múltiplos hubs interconectados, cada um com suas folhas.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_8.md`, se existir

## Pré-requisitos

- Fase 5 completa (mapa Leaflet funcionando, nós no mapa)
- Fase 4 completa (link budget P2P calculando)

## Tarefas

1. Estender `LinkScenario` com campo `topology_type`:
   - `P2P`
   - `CHAIN`
   - `STAR`
   - `MESH`
   - `MULTI_STAR`
   - `HIERARCHICAL`
2. Criar rotas:

```text
POST   /api/v1/scenarios/{id}/links
DELETE /api/v1/scenarios/{id}/links/{link_id}
```

3. UI — modo malha manual:
   - arrastar entre dois nós cria enlace;
   - clique em enlace existente permite removê-lo.
4. UI — modo multi-estrela:
   - usuário designa nós como hub (marcador diferente);
   - cada folha associada a um hub via UI.
5. Validação de ilhas:
   - detectar nós sem nenhum enlace;
   - avisar usuário com destaque visual.
6. Link budget multi-hop:
   - acumular perdas ao longo da cadeia de hops;
   - mostrar margem total por caminho.
7. Redundância:
   - nó com dois hubs upstream;
   - exibir melhor margem entre os dois caminhos.
8. Criar `docs/for-dummies/14-como-criar-malha-manual.md`.
9. Criar `docs/for-dummies/15-como-criar-topologia-multi-estrela.md`.
10. Criar `tests/test_topology.py`.

## Checkpoints obrigatórios

- [ ] Enlace criado por arrastar entre dois nós no mapa
- [ ] Enlace removido individualmente sem apagar o cenário
- [ ] Nós sem enlace (ilhas) marcados visualmente
- [ ] Multi-estrela: dois hubs com folhas próprias + enlace hub-a-hub calculado
- [ ] Link budget multi-hop acumula perdas corretamente
- [ ] Nó com dois hubs mostra melhor margem dos dois caminhos
- [ ] `pytest tests/test_topology.py` passa

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_9.md
```

O relatório deve conter:

- topologias implementadas;
- rotas criadas;
- lógica de link budget multi-hop;
- validações de ilha;
- testes criados;
- checkpoints marcados;
- limitações conhecidas.

## Regra final

Não implementar otimização automática de posição de nó nem site selection nesta fase.
