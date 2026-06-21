# Gap Analysis — MATLAB (referência) vs Sistema Python atual

**Fonte MATLAB:** `prompt2.md` (especificação) + `prompt1.md` (saída de simulação)
**Data:** 2026-06-21

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

**MATLAB:** `AdditionalLosses_dB = 19 dB` (obstáculos/clutter de campus) presente em todos os enlaces. Campo configurável.

**Python:** FSPL puro. Não há campo de perda adicional por obstrução/clutter no `NodeSpec` ou no cálculo de enlace.

---

### 5. Comparação de cenários — ausente

**MATLAB:** 5 cenários (A–E) rodando combinações de módulo × antena TX × antena GW, gerando tabelas de margem mínima, média, falhas, links críticos, confortáveis.

**Python:** calcula um enlace por vez. Não existe framework de comparação de cenários.

---

## Gaps significativos — implementado de forma rudimentar

### 6. Base de dados de módulos LoRa

**MATLAB:** `loadLoRaModules.m` — tabela com RFM95W, LRO2_ASR6601, E220-900T22D incluindo: PtxOptions, múltiplas sensibilidades por SF/BW, TxCurrentOptions, VoltageRange, SleepCurrent, DataRate.

**Python:** `NodeSpec` tem um campo `rx_sensitivity_dbm` (único valor). Não existe tabela de módulos. Sensibilidade é inputada manualmente por nó, sem vínculo com especificação do módulo.

**RFM95W tem 3 modos de sensibilidade:** -139 dBm (LongRange), -136 dBm (Balanced), -118 dBm (HighDataRate). Python não modela isso.

---

### 7. Distância 3D — altitude ignorada

**MATLAB:** calcula distância 2D e distância 3D com diferença de altitude (ENU). No campus UnB há diferenças de ~27 m entre pontos (SG: alt 1046 m vs BCE: alt 1019 m).

**Python:** Haversine puro — distância 2D. Altitude do KML importado é armazenada no `NodeSpec.height_m` mas não entra na fórmula FSPL.

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

## Resumo de prioridade

| # | Gap | Severidade | Necessário para |
|---|-----|-----------|----------------|
| 1 | G(θ,φ) — ganho direcional real | Alta | Resultados fisicamente corretos para helicoidal/parabólica |
| 2 | PCB_Compact + Commercial_Omni_6dBi | Alta | Paridade com MATLAB; referência prática do kit |
| 3 | Orientação/apontamento de antena | Alta | Cenários C e D do MATLAB |
| 4 | Perdas adicionais por obstrução | Média | Realismo em ambiente de campus |
| 5 | Comparação de cenários A–E | Média | Análise comparativa módulo × antena |
| 6 | Base de módulos LoRa | Média | Sensibilidades por SF, corrente de TX |
| 7 | Distância 3D com altitude | Baixa | Precisão em terreno com desnível |
| 8 | Seleção automática de gateway (minimax) | Baixa | Alternativa ao site selection atual |
| 9 | Robustez direcional no ranking | Baixa | Score mais justo para antenas diretivas |
| 10 | Consumo energético | Baixa | Comparação de módulos por consumo |
| 11 | Perda de polarização | Baixa | Cenários com polarização mista |
| 12 | Ranking multi-critério | Baixa | Paridade com rankConfigurations.m |
| 13 | Conversão ENU | Baixa | Pré-requisito para gap #1 e #3 |
