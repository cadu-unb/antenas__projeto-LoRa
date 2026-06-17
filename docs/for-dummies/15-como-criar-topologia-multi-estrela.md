# Como criar topologia multi-estrela

Multi-estrela (MULTI_STAR) conecta múltiplos hubs entre si, cada um com suas próprias folhas. Útil para redes LoRa com cobertura ampla dividida em zonas.

## Diferença entre STAR e MULTI_STAR

| Topologia | Hubs | Folhas por hub | Interconexão entre hubs |
|---|---|---|---|
| STAR | 1 | Ilimitado | Não |
| MULTI_STAR | 2 ou mais | Ilimitado por hub | Sim |

## Passo a passo

### 1. Selecionar MULTI_STAR

Clicar **Multi-Estrela** na barra de topologias do Link Planner.

### 2. Designar hubs

Nos cartões de nó (Nó A, Nó B, e extras), ativar o toggle **Hub** para os nós que funcionarão como gateways centrais.

- Hub: marcador azul no mapa
- Folha: marcador laranja no mapa

### 3. Criar enlaces

Use o modo de conexão no mapa:

1. **Hub–Hub:** conectar os dois gateways para criar o backbone
2. **Hub–Folha:** conectar cada folha ao hub responsável

### 4. Redundância opcional

Para proteger uma folha contra falha de hub:
- Criar dois enlaces para a mesma folha, a partir de hubs diferentes
- O sistema calculará as duas margens e identificará a melhor

### 5. Calcular

Clicar **Calcular enlaces**. O sistema retorna:
- Margem por hop
- Identificação de ilhas (nós sem enlace)
- Gargalo da rede (menor margem)

## Exemplo: dois hubs, quatro folhas

```
Folha 1 ─── Hub 1 ────── Hub 2 ─── Folha 3
Folha 2 ─┘              └─── Folha 4
```

Configuração:
- Nó A = Hub 1 (is_hub = true)
- Nó B = Hub 2 (is_hub = true)
- Extra 1 = Folha 1, Extra 2 = Folha 2, Extra 3 = Folha 3, Extra 4 = Folha 4
- Links: Hub1↔Hub2, Hub1→Folha1, Hub1→Folha2, Hub2→Folha3, Hub2→Folha4

## Ilhas

Se um nó não tiver nenhum enlace, aparece destacado em vermelho no mapa e listado em **Nós sem enlace**. Criar pelo menos um enlace para cada nó para garantir cobertura.

## Interpretação do semáforo

O semáforo da rede multi-estrela reflete o **gargalo** — o hop com menor margem de enlace. Se o backbone (Hub1↔Hub2) tiver margem negativa, toda a rede fica vermelha mesmo que os hops locais sejam verdes.

## Referência API

```bash
# calcular topologia completa
POST /api/v1/scenarios/{id}/calculate_links

# resposta inclui:
# - hops[]: margem por enlace
# - islands[]: IDs de nós isolados
# - bottleneck_margin_db: gargalo da rede
# - feasibility: verde | amarelo | vermelho
```
