# 08 — UI Campus KML, Interferência e Canais

## Problema

A interface Campus futura precisa guiar o usuário por upload KML, cálculo RF, SIR, mapa e otimização de canais sem misturar regra de domínio dentro da UI.

## Escopo

Plano prospectivo para CP-8/CP-8B.

## Fases da UI

1. Upload e validação KML.
2. Configuração RF.
3. Simulação multiponto.
4. Exploração visual.
5. Otimização de canais.

## Estados de Sessão

- `kml_document`
- `distance_matrix`
- `geo_context`
- `link_batch_request`
- `link_results`
- `sir_matrix`
- `channel_assignments`

## Mapa

Camadas:

- nós P1-P8
- polígonos de prédios/obstáculos
- enlaces coloridos por risco
- destaque de enlaces indecodificáveis por SIR
- canais otimizados

## Otimização

Fluxo:

1. `results_to_sir_matrix(results)`
2. `build_interference_graph(sir_matrix, sf=sf)`
3. `greedy_channel_assignment(nodes, graph)`
4. `count_channel_collisions(assignments, graph)`

## Validação

- A UI não implementa SIR.
- A UI não implementa coloração de grafos.
- A UI reseta resultados quando KML ou parâmetros RF mudam.
