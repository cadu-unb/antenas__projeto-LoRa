# Manual do Usuário — Simulador Multiponto LoRa

## Finalidade

O simulador calcula orçamentos de enlace LoRa entre múltiplos nós georreferenciados.
Para cada par de nós, calcula:

- Potência recebida (dBm) via equação de Friis
- Margem de enlace (dB)
- Viabilidade (`feasible = margem > 0`)
- Relação sinal-interferência (SIR)
- Risco: `LOW / MEDIUM / HIGH`
- Plano de canais otimizado por coloração de grafo (Welsh-Powell)

## Páginas da Aplicação

A aplicação possui duas páginas acessíveis pelo menu lateral:

### Simulação Standalone

Página para cálculo ponto a ponto sem KML.

Útil para:
- Estimar viabilidade de um enlace antes de montar o KML completo
- Testar o impacto de diferentes SFs, potências e distâncias
- Verificar rapidamente margem e risco para um par de nós

**Entradas (barra lateral):**

| Parâmetro | Controle | Padrão |
|-----------|----------|--------|
| Frequência | Selectbox 8 canais ANATEL | 915,2 MHz |
| Potência TX | Slider | 14 dBm |
| Ganho antena | Input numérico | 2,15 dBi |
| Perdas extras | Input numérico | 0 dB |
| Distância 2D | Input numérico | 300 m |
| Distância 3D | Input numérico | 300 m |
| Sensibilidade RX | Input numérico | −137,0 dBm |
| SF | Selectbox | 12 |

**Saída:** métricas em cards (potência recebida, margem, risco, viabilidade) e tabela filtrável.

**Nota:** Standalone não importa nem usa KML, GIS ou ray tracing. SIR = ∞ pois há apenas um transmissor.

---

### Campus KML

Página para simulação multiponto completa com arquivo KML.

Fluxo em 5 fases:

#### Fase 1 — Upload KML

- Arrastar ou selecionar arquivo `.kml` (não `.kmz`).
- O simulador detecta automaticamente pontos (`Placemark/Point`) e polígonos (`Placemark/Polygon`).
- Um novo upload substitui os resultados anteriores na sessão.
- Mensagem de confirmação exibe contagem de pontos e polígonos carregados.

#### Fase 2 — Configuração RF

Parâmetros no mesmo painel lateral da página Standalone.
Alterar parâmetros RF não re-executa a simulação automaticamente — clicar em **Executar simulação** é necessário.

#### Fase 3 — Simulação

Botão **Executar simulação** dispara:

1. Cálculo batch para todos os pares de nós (`run_link_budget_batch`)
2. Ray tracing 2D para identificar prédios cruzados por cada enlace
3. Cálculo de FSPL com distância 3D
4. Cálculo de SIR: para cada receptor, soma-se a potência de todos os outros transmissores como interferentes
5. Classificação de risco e flag `sir_decodable`

Resultado: tabela com todos os enlaces, filtrável por viabilidade.

#### Fase 4 — Mapa Folium

Mapa interativo gerado automaticamente após simulação:

| Elemento | Visual |
|----------|--------|
| Nós (pontos) | Marcadores azuis com tooltip do rótulo |
| Polígonos BUILDING | Cinza preenchido |
| Polígonos OBSTACLE | Laranja preenchido |
| Polígono CAMPUS | Cadet blue |
| Enlace LOW risk | Linha verde sólida |
| Enlace MEDIUM risk | Linha laranja sólida |
| Enlace HIGH risk | Linha vermelha sólida |
| Enlace não decodificável (`sir_decodable=False`) | Linha tracejada |

#### Fase 5 — Otimização de Canais

Botão **Otimizar canais** executa coloração de grafo (Welsh-Powell greedy):

- Nós com interferência mútua acima do limiar SIR recebem canais diferentes
- Algoritmo minimiza colisões de canal
- Resultado: tabela de atribuição `nó → canal (MHz) → índice`
- Métrica **Colisões de canal**: contagem de arestas do grafo onde ambos os nós têm o mesmo canal

## Nomenclatura de Nós

Rótulos recomendados: `P1`, `P2`, … `P8`.
O rótulo deve coincidir com o campo `<name>` do elemento `<Placemark>` no KML.
Rótulos são case-sensitive: `P1 ≠ p1`.

## Nomenclatura de Polígonos

| Papel | Valor em `<name>` |
|-------|-------------------|
| Prédio com atenuação | `BUILDING` |
| Obstáculo genérico | `OBSTACLE` |
| Limite do campus | `CAMPUS` |

Polígonos `BUILDING` e `OBSTACLE` são usados no ray tracing 2D.
`CAMPUS` é exibido no mapa mas ignorado no cálculo RF.

## Saída por Enlace

Cada enlace produz um resultado com:

| Campo | Tipo | Significado |
|-------|------|-------------|
| `distance_m` | float | Distância 2D horizontal (m) |
| `distance_3d_m` | float | Distância 3D com diferença de altitude (m) |
| `fspl_db` | float | Perda no espaço livre (dB) |
| `extra_loss_db` | float | Atenuação por prédios + perdas extras (dB) |
| `received_power_dbm` | float | Potência recebida (dBm) |
| `link_margin_db` | float | Margem = recebida − sensibilidade (dB) |
| `link_risk` | LOW/MEDIUM/HIGH | Risco do enlace |
| `feasible` | bool | True se margem > 0 |
| `sir_db` | float | SIR em dB (∞ se sem interferentes) |
| `sir_decodable` | bool | SIR acima do limiar para o SF configurado |
| `n_buildings_crossed` | int | Prédios cruzados pelo ray tracing |

## Limitações do Modelo

- Ray tracing é 2D: não considera difração vertical nem reflexão.
- SRTM 30m: altitude depende de conectividade com `opentopodata.org`; sem internet, altitude = 0.
- Atenuação por prédio: valor fixo padrão (15 dB/prédio); não considera material ou espessura real.
- SIR assume que todos os nós transmitem simultaneamente no mesmo canal — cenário de pior caso.
- Modelo de propagação é espaço livre (Friis); não inclui multirreflexão, difração ou efeito solo.
- Máximo recomendado: 8 nós (P1–P8). Mais nós aumentam o tempo de ray tracing.

## Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `ValidationError: frequency_hz` | Frequência fora de 915–928 MHz | Usar canal ANATEL válido |
| `Erro ao processar KML` | Arquivo KMZ, namespace inválido ou polígono malformado | Ver manual de preparação KML |
| `KeyError: KML point not found` | Rótulo no código ≠ rótulo no KML | Verificar `<name>` no KML |
| `ValueError: At least two KML points` | KML tem menos de 2 pontos | Adicionar mais `<Placemark>` tipo Point |
| `ValueError: distance_m must be positive` | Dois nós na mesma coordenada | Verificar coordenadas duplicadas |
| `feasible=False` em todos os enlaces | Sensibilidade restritiva ou distâncias grandes | Verificar parâmetros RF e SF |
| Mapa não carrega | `folium` ou `streamlit-folium` ausente | `uv sync` para instalar dependências |
