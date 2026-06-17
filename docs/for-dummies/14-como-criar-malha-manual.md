# Como criar malha manual

Malha manual (topologia MESH) permite conectar nós livremente — cada enlace é desenhado individualmente no mapa.

## Quando usar

- Rede LoRa com roteamento flexível entre nós
- Redundância: nó alcançável por dois caminhos
- Topologia que não segue cadeia nem estrela

## Passo a passo

### 1. Selecionar topologia MESH

No Link Planner, clicar **Malha** na barra de topologias.

### 2. Configurar nós

- Preencher **Nó A** e **Nó B** com coordenadas, altura e antena
- Adicionar nós extras clicando **+ Adicionar nó** (seção aparece abaixo dos cartões principais)
- Cada nó pode ter sua própria antena, potência Tx e sensibilidade Rx

### 3. Criar enlaces no mapa

Com a topologia MESH ativa, o mapa entra em **modo de conexão**:

1. Clicar **Conectar nós** (botão no painel do mapa)
2. Clicar no primeiro nó no mapa (marcador fica destacado em amarelo)
3. Clicar no segundo nó → enlace criado (linha vermelha no mapa)

Repetir para cada enlace desejado.

### 4. Remover enlace

Clicar na linha de enlace no mapa → popup aparece com botão **Remover**.

### 5. Calcular link budget

Clicar **Calcular enlaces**. O sistema calcula:
- Margem por hop (cada enlace individualmente)
- **Gargalo**: menor margem entre todos os hops
- **Ilhas**: nós sem nenhum enlace (destacados em vermelho no mapa)

### 6. Interpretar resultados

| Campo | Descrição |
|---|---|
| Margem por hop | Quanto de sinal sobra em cada enlace |
| Gargalo | Pior hop — determina viabilidade da rede |
| Ilhas | Nós desconectados — sem cobertura |

## Nó com dois caminhos (redundância)

Se um nó tem dois enlaces de hubs diferentes, a tabela mostra ambas as margens. O sistema identifica a **melhor margem** — a que garante cobertura mesmo se um dos hubs falhar.

## Exemplo típico

```
Hub 1 ──── Hub 2
  │               │
Folha A     Folha B
```

- Hub 1 e Hub 2 conectados entre si (enlace backbone)
- Cada hub conectado às suas folhas
- Folha pode ser configurada com dois hubs para redundância

## API (opcional)

```bash
# adicionar enlace
curl -X POST http://localhost:8000/api/v1/scenarios/{id}/links \
  -H "Content-Type: application/json" \
  -d '{"node_a_id": "id-do-no-a", "node_b_id": "id-do-no-b"}'

# remover enlace
curl -X DELETE http://localhost:8000/api/v1/scenarios/{id}/links/{link_id}

# calcular todos os enlaces
curl -X POST http://localhost:8000/api/v1/scenarios/{id}/calculate_links
```
