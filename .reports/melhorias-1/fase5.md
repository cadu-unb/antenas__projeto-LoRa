# Relatório — Fase 5: Frontend e Integração

**Data:** 2026-06-21  
**Branch:** versao-2  
**Status:** CONCLUÍDA — 246 passed, 1 skipped, 0 falhas (backend intacto)

---

## Resumo

7 etapas implementadas integrando ao frontend todos os novos endpoints e campos das Fases 1–4.

---

## Etapas Implementadas

### Etapa 1 — Presets de Coordenadas e Aviso de Distância
- Nó A: `-15.7801`, `-47.9292` (Brasília-DF)
- Nó B: `-15.8300`, `-48.0500`
- Mapa inicializa em `[-15.85, -47.98]`, zoom 9
- Nome padrão do cenário: "Enlace DF"
- Div `#link-warnings` renderiza `result.warnings` após calcular

### Etapa 2 — Seletor de Módulo LoRa
- Select `a-lora-module` e `b-lora-module` em cada node card
- `loadLoraModules()` busca `GET /api/v1/antennas/lora-modules` ao inicializar
- `window.onModuleChange(nodeId)` auto-preenche `tx_power` (nó A) e `rx_sensitivity` (nó B) ao selecionar módulo
- `getSF12Sensitivity(module)` extrai sensibilidade SF12/BW125 do catálogo
- `nodeModuleId` persiste seleção e inclui `lora_module_id` no payload

### Etapa 3 — Campos de Orientação e Perdas Adicionais
- `<details class="adv">` colapsável em cada node card com: azimute, tilt, extra_loss, fading, polarização
- `buildScenario()` inclui: `azimuth_deg`, `tilt_deg`, `extra_loss_db`, `fading_margin_db`, `polarization_loss_db`, `lora_module_id`, `propagation_model`
- `azimuth_deg`: null se campo vazio (omni); valor numérico se preenchido
- `renderResults()` exibe ganho efetivo via label "Perda (modelo)" quando modelo ≠ FSPL, e exibe modelo no grid

### Etapa 4 — Exportação Seletiva
- Botão "Exportar Setup (.json)" → `GET /export` (sem results)
- Botão "Exportar Completo (.json)" → `GET /export?include_results=true`
- Ambos usam `fetch` + blob download via `URL.createObjectURL`
- Botão antigo de export substituído pela dupla de botões

### Etapa 5 — Seletor de Modelo de Propagação
- Select `propagation-model` na `global-row` com opções: FSPL, Okumura-Hata, Longley-Rice
- Incluído no payload via `buildScenario()`
- Resultado exibe modelo usado no grid de métricas

### Etapa 6 — Painel de Comparação de Cenários
- Seção `#comparison-panel` aparece automaticamente após calcular link
- Botão "Executar Comparação" dispara `POST /compare` via `api.compareScenario(lastScenarioId)`
- `renderComparisonTable(rows)`: tabela com 8 colunas, color-coded (verde/amarelo/vermelho)
- Sem antenas na biblioteca → mensagem orientando o usuário

### Etapa 7 — Estimativa de Consumo em library.html
- Seção `#lora-modules-panel` com cards de todos os módulos do catálogo
- Form de energia: módulo, SF, potência TX, transmissões/dia
- `runEnergyEstimate()` → `POST /api/v1/antennas/lora-modules/{id}/energy?...`
- Exibe: ToA (ms), energia/TX (mJ), energia/dia (mWh), vida útil (dias)

---

## Arquivos Modificados

| Arquivo | Alteração |
|---|---|
| `frontend/public/link-planner.html` | Coords DF; LoRa selects; advanced details; propagation model select; warning div; export buttons duplos; comparison panel; mapa centrado DF; buildScenario + renderResults atualizados |
| `frontend/public/library.html` | +seção LoRa modules com cards + energy estimation form + JS inline |
| `frontend/public/js/api-client.js` | +`listLoraModules`, `getModuleEnergy`, `compareScenario` |

---

## Validações

| Critério | Status |
|---|---|
| Coordenadas padrão no DF | ✅ Confirmado via HTTP response |
| LoRa module dropdown carrega módulos | ✅ `/api/v1/antennas/lora-modules` retorna 3 módulos (200) |
| Campos avançados (azimute/tilt/extra_loss/fading/polarização) presentes | ✅ Todos os IDs verificados no HTML |
| Botões Exportar Setup / Exportar Completo | ✅ Ambos presentes, wired ao endpoint correto |
| Select propagation-model visível | ✅ Presente no global-row |
| Painel de comparação com tabela | ✅ `#comparison-panel` presente e wired |
| library.html: estimativa de energia RFM95W SF12 | ✅ Form completo + JS inline |
| Backend: 246 passed, 0 falhas | ✅ Todas as fases anteriores intactas |

---

## Decisões de Implementação

### URL de energia correta
Prompt usava `/api/v1/library/lora-modules/...` — prefixo incorreto. Usado `/api/v1/antennas/lora-modules/...` conforme rota real em `library_routes.py`.

### onModuleChange via window global
Script é ES module → `onchange="onModuleChange('a')"` no HTML requer função global. Exposto via `window.onModuleChange`. Alternativa seria event listeners declarados no JS, mas a abordagem inline é consistente com `window.removeCandidate` já existente.

### Comparison panel oculto até calcular
`#comparison-panel` sem classe `visible` por padrão. `renderResults()` chama `.classList.add("visible")` após cálculo bem-sucedido. Garante que usuário não tenta comparar sem cenário salvo.

### buildScenario com fv() helper
Adicionado helper `fv(id, def=0)` = `parseFloat(el?.value) || def` para reduzir repetição nos novos campos numéricos.

---

## Pendências

| Item | Nota |
|---|---|
| Teste E2E automatizado do frontend | Critérios validados manualmente via HTTP + inspeção de HTML |
| `lora_module_id` sobrescrevendo rx_sensitivity no backend | NodeSpec tem o campo mas `compute_link_full` não usa para override automático — campo passado mas lógica de override pendente no domain |
| Propagation model Longley-Rice | Registrado no enum mas sem implementação real no backend — retorna FSPL como fallback |
