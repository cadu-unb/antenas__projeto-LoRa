# Gap Analysis — MATLAB (referência) vs Sistema Python atual

**Fonte MATLAB:** `prompt2.md` (especificação) + `prompt1.md` (saída de simulação)
**Data:** 2026-06-21

---

## Fontes verificadas nesta revisão

- `.reports/externo/prompt/prompt1.md` e `.reports/externo/prompt/prompt2.md`
- `.reports/externo/prompt/return/*.m`
- `backend/app/**`, `frontend/public/**`, `tests/**`, `README.md` e `docs/**`

---

## Estado atual do sistema Python

O projeto atual não é apenas um script de cálculo isolado. Ele já é um sistema web/API com:

- FastAPI em `backend/app/main.py`, frontend estático em `frontend/public/` e página inicial com checagem de `/health`.
- Biblioteca de antenas em `/api/v1/antennas`, com CRUD, importação/exportação JSON e persistência em `backend/data/antennas`.
- Sandbox em `/api/v1/sandbox/preview` e `/api/v1/sandbox/simulate`.
- Modelos de sandbox para `dipolo`, `monopolo`, `helicoidal` e `parabolica`.
- Simulação assíncrona por jobs para modos `padrao` e `preciso`, com progresso, cancelamento e logs.
- Solver MoM via PyNEC quando disponível, com fallback analítico.
- Solver de abertura para parabólicas.
- Solvers Okumura-Hata e Longley-Rice simplificado como módulos Python testados, mas ainda não integrados à rota principal de link budget.
- Stub arquitetural de ray tracing, explicitamente fora do MVP.
- Link Planner com cenários, P2P, cadeia, estrela, malha e multi-estrela.
- Enlaces manuais para malha/multi-estrela, cálculo por hop, gargalo de margem e detecção de ilhas.
- Importação KML de pontos e polígonos; placemarks com `torre`/`tower` viram candidatos a torre.
- Site selection com candidatos, ajuste de altura, ranking por cobertura e detalhe de margem por nó.
- Documentação técnica e guias em `docs/calculos/` e `docs/for-dummies/`.

Importante: o link budget principal usa FSPL com distância Haversine 2D. `height_m` entra no cálculo de elevação exibida, mas não altera a distância usada na perda de percurso nem o site selection FSPL atual.

---

## Features presentes nos prompts/retornos externos

Os arquivos de `.reports/externo/prompt/return/` listam ou implementam estas features MATLAB:

- Pontos do Campus Darcy Ribeiro com latitude, longitude e altitude.
- Seleção manual ou automática de gateway por minimax de distância 3D.
- Conversão geodésica para ENU local.
- Geometria 2D/3D do enlace, azimute, elevação e ângulos `theta`/`phi`.
- Base de módulos LoRa: `RFM95W_915MHz`, `LRO2_ASR6601`, `E220_900T22D`.
- Base de antenas: `Dipole_HalfWave`, `Monopole_GroundPlane`, `Helical_Axial`, `Parabolic_Dish`, `PCB_Compact`, `Commercial_Omni_6dBi`.
- Ganho direcional aproximado `G(theta, phi)` por tipo de antena.
- Orientação/apontamento de antenas e cenário de desalinhamento.
- Link budget com FSPL, perda de cabo TX/RX, perda de polarização, perda extra e margem de fading.
- Cenários A-E de comparação módulo x antena.
- Rankings por combinação, módulo, antena transmissora e antena do gateway.
- Scores de robustez multidirecional e praticidade.
- Estimativa simples de energia por transmissão.
- Gráficos de padrões de radiação, mapa do campus e discussão automática.
- Scripts de apoio `EnlacesLora.m` e `ProjetoAntenas.m`, cobrindo matriz de conectividade por raio fixo e alinhamento/feixe direcional entre coordenadas.

---

## Funcionalidades já implementadas que estavam pouco destacadas

- O sistema calcula mais que um enlace P2P: há topologias, redes multi-hop e site selection.
- KML já é suportado para pontos, polígonos visuais e torres candidatas.
- Há persistência de antenas, cenários e logs.
- Há fila de jobs para simulações mais pesadas.
- Okumura-Hata e Longley-Rice existem como solvers testados, mas ainda não estão conectados ao fluxo principal de link budget.
- Ray tracing existe apenas como stub arquitetural, não como solver funcional.

---

## Gaps críticos — funcionalidade ausente

### 1. Ganho direcional G(θ,φ) — não implementado

**MATLAB:** para cada enlace calcula azimute e elevação reais → consulta `antennaPattern(type, theta, phi)` → usa G_tx(θ,φ) e G_rx(θ,φ) efetivos.

**Python:** usa sempre `G_max` da antena. Não existe consulta angular. O sandbox gera um diagrama visual, mas o cálculo de link budget não usa esse padrão — usa o pico.

**Impacto:** antenas diretivas (helicoidal, parabólica) sempre aparecem com ganho máximo, independente do ângulo real de enlace. Resultado fisicamente incorreto quando o boresight não aponta para o receptor.

---

### 2. Tipos de antena ausentes

**MATLAB:** 6 tipos — Dipole_HalfWave, Monopole_GroundPlane, Helical_Axial, Parabolic_Dish, **PCB_Compact**, **Commercial_Omni_6dBi**.

**Python:** 4 tipos — Dipolo, Monopolo, Helicoidal, Parabólica.

Faltam:
- `PCB_Compact` — antena integrada ao PCB, quasi-omni, G ≈ 0–2 dBi com irregularidades angulares
- `Commercial_Omni_6dBi` — antena colinear comercial 6 dBi, padrão mais estreito em elevação que o dipolo simples; usada como referência prática no kit E220-900T22D

---

### 3. Orientação e apontamento de antena — ausente

**MATLAB:** `TxOrientation` (vertical/horizontal), opção de apontar boresight para o gateway (cenário C) vs. não apontar (cenário D). Penalidade de desalinhamento calculada via G(θ,φ).

**Python:** não existe orientação de antena. Não existe conceito de boresight ou apontamento. Impossível reproduzir o cenário D (desalinhamento diretivo).

---

### 4. Perdas adicionais — não parametrizadas

**MATLAB:** o `linkBudget.m` aceita perdas de cabo TX/RX, perda de polarização, perda extra e margem de fading. No `main_LoRa_AntennaComparison.m`, o exemplo soma 19 dB no total: 0,5 dB cabo TX + 0,5 dB cabo RX + 8 dB perda extra + 10 dB fading.

**Python:** o link budget principal usa FSPL e `cable_loss_db` por nó. Não há campos explícitos para perda adicional por obstrução/clutter, perda de polarização ou margem de fading no `NodeSpec` ou no cálculo de enlace.

---

### 5. Comparação de cenários — ausente

**MATLAB:** 5 cenários (A–E) rodando combinações de módulo × antena TX × antena GW, gerando tabelas de margem mínima, média, falhas, links críticos, confortáveis.

**Python:** calcula P2P, topologias multi-hop e site selection, mas não possui framework de varredura automática módulo × antena × cenário no estilo MATLAB A-E.

---

## Gaps significativos — implementado de forma rudimentar

### 6. Base de dados de módulos LoRa

**MATLAB:** `loadLoRaModules.m` — tabela com RFM95W, LRO2_ASR6601, E220-900T22D incluindo: PtxOptions, múltiplas sensibilidades por SF/BW, TxCurrentOptions, VoltageRange, SleepCurrent, DataRate.

**Python:** `NodeSpec` tem um campo `rx_sensitivity_dbm` (único valor). Não existe tabela de módulos. Sensibilidade é inputada manualmente por nó, sem vínculo com especificação do módulo.

**RFM95W tem 3 modos de sensibilidade:** -139 dBm (LongRange), -136 dBm (Balanced), -118 dBm (HighDataRate). Python não modela isso.

---

### 7. Distância 3D — altitude ignorada

**MATLAB:** calcula distância 2D e distância 3D com diferença de altitude (ENU). No campus UnB há diferenças de ~27 m entre pontos (SG: alt 1046 m vs BCE: alt 1019 m).

**Python:** usa Haversine 2D na fórmula FSPL. A altitude/altura (`height_m`) é armazenada no `NodeSpec` e entra no ângulo de elevação exibido, mas não entra na distância de perda nem no site selection FSPL.

**Impacto:** pequeno para campus (<1 km), mas sistematicamente subestima FSPL em terreno irregular.

---

### 8. Seleção automática de gateway

**MATLAB:** `chooseGateway.m` — escolhe gateway que minimiza distância máxima (minimax). Retorna ranking de candidatos com distância média e máxima.

**Python:** `POST /candidates` + `POST /site-selection` ranqueia candidatos por **cobertura%** (número de nós com margem > 0). Não calcula distância média/máxima. Não tem modo minimax explícito.

**Nota:** site selection existe, mas com critério diferente e sem as métricas de distância do MATLAB.

---

### 9. Score de robustez direcional — ausente

**MATLAB:** `RobustnessScore` penaliza antenas diretivas que não conseguem servir múltiplos azimutes simultaneamente. `PracticalityScore` considera facilidade de instalação.

**Python:** ranking de cobertura% não penaliza direcionalidade. Uma antena parabólica apontada para um nó específico apareceria com margem alta, sem penalidade para os demais.

---

### 10. Estimativa de consumo energético

**MATLAB:** `estimateEnergyConsumption.m` — energia por transmissão e consumo diário a partir de TxCurrent, Vtx e tempo de transmissão.

**Python:** não existe.

---

## Gaps menores — ausentes ou superficiais

### 11. Perda de polarização

**MATLAB:** campo `PolarizationLoss_dB` no cálculo de enlace (mostrado como 0 no output, mas parametrizável).

**Python:** não existe campo de polarization loss.

---

### 12. Ranking multi-critério de combinações

**MATLAB:** `rankConfigurations.m` gera ranking por MinMargin, MeanMargin, Failures, CriticalLinks, ComfortableLinks, RobustnessScore, PracticalityScore, TxCurrent.

**Python:** site selection ranqueia apenas por `coverage_pct`. Não há MinMargin/MeanMargin por candidato, nem score de praticidade.

---

### 13. Conversão geodésica ENU

**MATLAB:** `geodeticToLocalENU.m` — coordenadas locais em metros com origem no gateway (East, North, Up). Usado para geometria de apontamento de antenas diretivas.

**Python:** não existe. Para implementar G(θ,φ) corretamente, será necessário.

---

### 14. Visualização 3D de padrões de radiação

**MATLAB:** `plotRadiationPatterns.m` gera cortes em `theta`, cortes em `phi` e superfícies 3D simplificadas para todas as antenas.

**Python:** o sandbox mostra visual físico SVG e diagrama polar 2D. Não há visualização 3D nativa dos padrões.

---

### 15. Matriz automática por raio e feixe direcional no mapa

**MATLAB:** `EnlacesLora.m` calcula matriz de conectividade por raio fixo e desenha cobertura omnidirecional; `ProjetoAntenas.m` desenha alinhamento/feixe direcional entre dois pontos.

**Python:** topologias manuais cobrem parte da ideia de enlaces, e o P2P calcula azimute/elevação. Ainda não há recurso dedicado de matriz automática por raio fixo nem visualização de setor/feixe direcional.

---

### 16. Polígonos KML como obstáculos físicos

**Python atual:** importa e renderiza polígonos KML como geometrias visuais.

**Ausente:** usar polígonos como obstáculos com altura, material e penalidade física de propagação.

---

### 17. Integração de Okumura-Hata/Longley-Rice ao Link Planner

**Python atual:** os solvers existem e são testados.

**Ausente:** seleção de modelo de propagação na UI/API do Link Planner e uso desses modelos no cálculo P2P, multi-hop ou site selection.

---

## Resumo de prioridade

| # | Gap | Severidade | Necessário para |
|---|-----|-----------|----------------|
| 1 | G(θ,φ) — ganho direcional real | Alta | Resultados fisicamente corretos para helicoidal/parabólica |
| 2 | Orientação/apontamento de antena | Alta | Cenários C e D do MATLAB |
| 3 | Base de módulos LoRa | Alta | Sensibilidades por SF, corrente de TX |
| 4 | Perdas adicionais por obstrução | Média | Realismo em ambiente de campus |
| 5 | Comparação de cenários A–E | Média | Análise comparativa módulo × antena |
| 6 | PCB_Compact + Commercial_Omni_6dBi | Média | Paridade com MATLAB; referência prática do kit |
| 7 | Distância 3D com altitude | Média | Precisão e geometria angular |
| 8 | Seleção automática de gateway (minimax) | Baixa | Alternativa ao site selection atual |
| 9 | Robustez direcional no ranking | Baixa | Score mais justo para antenas diretivas |
| 10 | Consumo energético | Baixa | Comparação de módulos por consumo |
| 11 | Perda de polarização | Baixa | Cenários com polarização mista |
| 12 | Ranking multi-critério | Baixa | Paridade com rankConfigurations.m |
| 13 | Conversão ENU | Baixa | Pré-requisito para gap #1 e #3 |
| 14 | Visualização 3D de padrões | Baixa | Paridade visual com MATLAB |
| 15 | Matriz por raio e feixe direcional | Baixa | Paridade com scripts de apoio |
| 16 | Polígonos KML como obstáculos | Baixa | Modelagem física de campus |
| 17 | Integrar Okumura/Longley ao planner | Baixa | Modelos além de FSPL no fluxo principal |
| 18 | Persistência setup vs. setup+resultados | Média | Exportação seletiva, auditoria sem reprocessamento |
| 19 | Escala de distância — fixtures e presets | Média | Testes e UI refletirem escopo real (10–90 km) |

---

### 18. Persistência de cenários — sem separação setup vs. resultados

**Python atual:** `LinkScenario` é um objeto único. `GET /scenarios/{id}` retorna sempre tudo: configuração de nós, arestas, antenas, topologia, resultados de cálculo e site selection. Não há modo de salvar ou exportar apenas a estrutura do cenário sem os resultados anexados.

**Necessário:** duas opções explícitas de salvamento:

- **Opção A — Salvar Configuração (Setup):** persiste parâmetros de antenas, posicionamento geográfico dos nós e conexões. Não inclui dados de simulação. Ideal para reexecutar ou modificar sem carregar payloads pesados.
- **Opção B — Salvar Cenário Completo (Setup + Resultados):** persiste tudo do Opção A mais todos os dados brutos e métricas gerados após a execução. Ideal para auditoria, relatórios e análises sem reprocessamento.

Ambas devem ser exportáveis em `.json`. A distinção exige ou dois endpoints de export separados, ou um query param `?include=results` na rota de GET/export.

---

### 19. Escala de distância — fixtures e presets fora do escopo real

**Problema atual:** os cenários padrão e fixtures de teste usam nós com coordenadas de escala intermunicipal (~400 km, equivalente à distância RJ–SP). Isso distorce validações de FSPL, site selection e cobertura — margens surgem como absurdas (positivas em distâncias impossíveis para LoRa).

**Exemplo:** `CANDIDATE_FAR` em `tests/test_site_selection.py` usa `lat=-1.0, lon=-35.0` (~2500 km) para forçar margem negativa — o que revela que, sem essa distância extrema, até candidatos distantes cobrem tudo com LoRa SF12 + TX=20 dBm.

**Diretriz correta:** escopo operacional de **10 km a 90 km**, condizente com a realidade técnica de LoRa em ambiente aberto/suburbano com antenas de ganho moderado.

**Ação necessária:**
- Atualizar coordenadas de fixtures de teste para nós dentro de ~30–80 km entre si (ex: pontos em Brasília-DF).
- Rever presets/exemplos da UI para refletirem essa escala.
- Considerar validação de interface que avise quando nós estão a >200 km (fora do escopo prático do projeto).

---

## Resumo de prioridade

O relatório anterior capturava corretamente vários gaps físicos, mas subdescrevia o projeto Python atual. A principal correção é: o sistema já possui infraestrutura web/API, biblioteca, sandbox, KML, topologias, site selection, jobs e solvers auxiliares. O maior gap frente ao material MATLAB externo está na camada de comparação física: ganho angular, orientação/apontamento, catálogo de módulos, perdas parametrizadas e rankings multi-critério.

Gaps adicionados nesta revisão: persistência de cenários em dois modos (setup vs. completo) e ajuste de escala de distância dos fixtures/presets para a faixa operacional real de LoRa (10–90 km).
