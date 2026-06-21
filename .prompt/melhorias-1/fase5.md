# Fase 5 — Frontend e Integração

**Objetivo:** integrar ao frontend (`link-planner.html`, `api-client.js`) todos os novos campos e endpoints das Fases 1–4. Garantir que qualquer usuário possa usar as novas features sem acessar a API diretamente.

**Dependências:** Fases 1, 2, 3 e 4 concluídas (endpoints disponíveis).
**Arquivos afetados:** `frontend/public/link-planner.html`, `frontend/public/js/api-client.js`, `frontend/public/library.html`

> **Como testar frontend:** iniciar o servidor com `uv run uvicorn backend.app.main:app --reload` e abrir `http://localhost:8000` no browser. Testar cada etapa manualmente no browser após implementar.

---

## Etapa 1 — Presets de Coordenadas e Aviso de Distância

**Objetivo:** remover coordenadas de São Paulo dos presets; substituir por Distrito Federal. Mostrar aviso quando nós estão a >200 km.

### 1.1 — Atualizar coordenadas padrão em `link-planner.html`

Localizar os valores `value=""` dos inputs de lat/lon nos formulários de nós. Trocar:

```html
<!-- ANTES -->
<input id="node-a-lat" value="-23.50" ...>
<input id="node-a-lon" value="-46.60" ...>
<input id="node-b-lat" value="-23.55" ...>
<input id="node-b-lon" value="-46.65" ...>

<!-- DEPOIS -->
<input id="node-a-lat" value="-15.7801" ...>
<input id="node-a-lon" value="-47.9292" ...>
<input id="node-b-lat" value="-15.8300" ...>
<input id="node-b-lon" value="-48.0500" ...>
```

Fazer o mesmo para qualquer preset de "exemplo" ou botão "carregar exemplo" que inicializa coordenadas.

### 1.2 — Adicionar aviso de distância na UI

Em `api-client.js` ou no handler de resultado de cálculo, após receber o `LinkResult`:

```javascript
function handleLinkResult(result) {
  // Exibir resultado normalmente...
  renderLinkResult(result);

  // Aviso de distância
  if (result.warnings && result.warnings.length > 0) {
    const warningBox = document.getElementById("link-warnings");
    if (warningBox) {
      warningBox.innerHTML = result.warnings
        .map(w => `<div class="warning-msg">⚠ ${w}</div>`)
        .join("");
      warningBox.style.display = "block";
    }
  } else {
    const warningBox = document.getElementById("link-warnings");
    if (warningBox) warningBox.style.display = "none";
  }
}
```

Em `link-planner.html`, adicionar container para warnings logo abaixo do painel de resultado:

```html
<div id="link-warnings" style="display:none; background:#332200; border:1px solid #e8a82a; padding:8px; margin-top:8px; border-radius:4px;"></div>
```

---

## Etapa 2 — Seletor de Módulo LoRa

**Objetivo:** permitir que o usuário selecione um módulo LoRa para cada nó. Ao selecionar, os campos `tx_power_dbm` e `rx_sensitivity_dbm` são preenchidos automaticamente com os valores do módulo (SF12, BW125).

### 2.1 — Adicionar select de módulo em `link-planner.html`

Dentro do formulário de cada nó (Node A e Node B), adicionar:

```html
<label for="node-a-lora-module">Módulo LoRa</label>
<select id="node-a-lora-module" onchange="onModuleChange('a')">
  <option value="">— manual —</option>
  <!-- preenchido dinamicamente pelo JS ao carregar a página -->
</select>
```

### 2.2 — Carregar módulos ao iniciar página em `api-client.js`

```javascript
async function loadLoraModules() {
  const resp = await fetch("/api/v1/library/lora-modules");
  if (!resp.ok) return;
  const modules = await resp.json();

  ["a", "b"].forEach(nodeId => {
    const select = document.getElementById(`node-${nodeId}-lora-module`);
    if (!select) return;
    modules.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.text = `${m.name} (SF12: ${getSF12Sensitivity(m)} dBm)`;
      select.appendChild(opt);
    });
  });

  window._loraModules = modules;  // cache global
}

function getSF12Sensitivity(module) {
  const mode = module.sensitivity_modes.find(m => m.sf === 12 && m.bw_khz === 125);
  return mode ? mode.sensitivity_dbm : "—";
}

function onModuleChange(nodeId) {
  const select = document.getElementById(`node-${nodeId}-lora-module`);
  const moduleId = select.value;
  if (!moduleId) return;

  const module = window._loraModules.find(m => m.id === moduleId);
  if (!module) return;

  // Preencher campos automaticamente
  document.getElementById(`node-${nodeId}-tx-power`).value = Math.max(...module.tx_power_options_dbm);
  document.getElementById(`node-${nodeId}-rx-sensitivity`).value = getSF12Sensitivity(module);

  // Salvar lora_module_id no objeto do nó
  window._nodeData[nodeId] = window._nodeData[nodeId] || {};
  window._nodeData[nodeId].lora_module_id = moduleId;
}

// Chamar no DOMContentLoaded:
document.addEventListener("DOMContentLoaded", loadLoraModules);
```

---

## Etapa 3 — Campos de Orientação e Perdas Adicionais

**Objetivo:** expor os novos campos de `NodeSpec` na UI — azimute, tilt, perda extra, fading, polarização.

### 3.1 — Adicionar campos em `link-planner.html`

Para cada nó, adicionar seção "Configurações avançadas" (colapsável com `<details>`):

```html
<details>
  <summary>Configurações avançadas de antena e perdas</summary>

  <label for="node-a-azimuth">Azimute do boresight (°, 0=Norte)</label>
  <input type="number" id="node-a-azimuth" placeholder="vazio = omni" min="0" max="359" step="1">

  <label for="node-a-tilt">Inclinação (°, positivo = acima do horizonte)</label>
  <input type="number" id="node-a-tilt" value="0" min="-90" max="90" step="1">

  <label for="node-a-extra-loss">Perda extra por obstrução (dB)</label>
  <input type="number" id="node-a-extra-loss" value="0" min="0" max="30" step="0.5">

  <label for="node-a-fading">Margem de fading (dB)</label>
  <input type="number" id="node-a-fading" value="0" min="0" max="20" step="0.5">

  <label for="node-a-polarization">Perda de polarização (dB)</label>
  <input type="number" id="node-a-polarization" value="0" min="0" max="6" step="0.5">
</details>
```

Repetir para Node B.

### 3.2 — Incluir campos no payload enviado à API

Em `api-client.js`, na função que constrói o objeto `node_a`/`node_b`:

```javascript
function buildNodeSpec(nodeId) {
  const azimuthRaw = document.getElementById(`node-${nodeId}-azimuth`)?.value;
  return {
    name: document.getElementById(`node-${nodeId}-name`)?.value || `Node ${nodeId.toUpperCase()}`,
    lat: parseFloat(document.getElementById(`node-${nodeId}-lat`)?.value),
    lon: parseFloat(document.getElementById(`node-${nodeId}-lon`)?.value),
    height_m: parseFloat(document.getElementById(`node-${nodeId}-height`)?.value || 0),
    tx_power_dbm: parseFloat(document.getElementById(`node-${nodeId}-tx-power`)?.value || 14),
    rx_sensitivity_dbm: parseFloat(document.getElementById(`node-${nodeId}-rx-sensitivity`)?.value || -137),
    cable_loss_db: parseFloat(document.getElementById(`node-${nodeId}-cable-loss`)?.value || 0),
    // Novos campos:
    azimuth_deg: azimuthRaw ? parseFloat(azimuthRaw) : null,
    tilt_deg: parseFloat(document.getElementById(`node-${nodeId}-tilt`)?.value || 0),
    extra_loss_db: parseFloat(document.getElementById(`node-${nodeId}-extra-loss`)?.value || 0),
    fading_margin_db: parseFloat(document.getElementById(`node-${nodeId}-fading`)?.value || 0),
    polarization_loss_db: parseFloat(document.getElementById(`node-${nodeId}-polarization`)?.value || 0),
    lora_module_id: window._nodeData?.[nodeId]?.lora_module_id || null,
  };
}
```

### 3.3 — Exibir ganho efetivo no resultado

No painel de resultado do link budget, adicionar linha:

```javascript
// Após receber LinkResult:
const gainsLine = `TX gain: ${result.tx_gain_dbi.toFixed(1)} dBi | RX gain: ${result.rx_gain_dbi.toFixed(1)} dBi`;
// Se azimute definido, adicionar nota:
const azNote = nodeA.azimuth_deg !== null ? " (direcional)" : " (G_max)";
renderField("Ganho efetivo TX", gainsLine + azNote);
```

---

## Etapa 4 — Exportação Seletiva (Setup / Completo)

**Objetivo:** adicionar dois botões de export no painel de cenário — um para setup-only e outro para setup+resultados.

### 4.1 — Adicionar botões em `link-planner.html`

No painel de gerenciamento de cenário (onde já devem existir botões de salvar/carregar):

```html
<div class="export-buttons">
  <button onclick="exportScenario(false)">Exportar Setup (.json)</button>
  <button onclick="exportScenario(true)">Exportar Completo (.json)</button>
</div>
```

### 4.2 — Implementar `exportScenario` em `api-client.js`

```javascript
async function exportScenario(includeResults = false) {
  const scenarioId = getCurrentScenarioId();
  if (!scenarioId) {
    alert("Salve o cenário antes de exportar.");
    return;
  }

  const url = `/api/v1/scenarios/${scenarioId}/export${includeResults ? "?include_results=true" : ""}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    alert("Erro ao exportar cenário.");
    return;
  }

  const blob = await resp.blob();
  const filename = includeResults
    ? `scenario_${scenarioId}_completo.json`
    : `scenario_${scenarioId}_setup.json`;

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
```

---

## Etapa 5 — Seletor de Modelo de Propagação

**Objetivo:** expor o campo `propagation_model` do `LinkScenario` na UI.

### 5.1 — Adicionar select em `link-planner.html`

```html
<label for="propagation-model">Modelo de propagação</label>
<select id="propagation-model">
  <option value="fspl">FSPL — Espaço Livre</option>
  <option value="okumura_hata">Okumura-Hata — Urbano/Suburbano</option>
  <option value="longley_rice">Longley-Rice — Terreno Irregular</option>
</select>
```

### 5.2 — Incluir no payload de criação/atualização do cenário

Em `api-client.js`, ao construir o objeto do cenário:

```javascript
function buildScenarioPayload() {
  return {
    // ...campos existentes...
    propagation_model: document.getElementById("propagation-model")?.value || "fspl",
  };
}
```

### 5.3 — Exibir modelo usado no resultado

```javascript
renderField("Modelo de propagação", result.propagation_model || "fspl");
```

---

## Etapa 6 — Painel de Comparação de Cenários

**Objetivo:** adicionar seção "Comparar Cenários" que dispara `POST /compare` e exibe tabela de resultados.

### 6.1 — Adicionar seção em `link-planner.html`

```html
<section id="comparison-panel">
  <h3>Comparação de Módulos × Antenas</h3>
  <p>Compara automaticamente os módulos LoRa disponíveis com as antenas da biblioteca.</p>
  <button onclick="runComparison()">Executar Comparação</button>
  <div id="comparison-results"></div>
</section>
```

### 6.2 — Implementar `runComparison` em `api-client.js`

```javascript
async function runComparison() {
  const scenarioId = getCurrentScenarioId();
  if (!scenarioId) { alert("Salve o cenário antes de comparar."); return; }

  const resp = await fetch(`/api/v1/scenarios/${scenarioId}/compare`, { method: "POST" });
  if (!resp.ok) { alert("Erro na comparação."); return; }

  const rows = await resp.json();
  renderComparisonTable(rows);
}

function renderComparisonTable(rows) {
  const container = document.getElementById("comparison-results");
  if (!rows.length) { container.innerHTML = "<p>Sem resultados.</p>"; return; }

  const headers = ["Cenário", "Módulo", "Antena TX", "Antena GW",
                   "Margem mín (dB)", "Margem média (dB)", "Falhas", "Robustez"];

  const thead = `<tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>`;
  const tbody = rows.map(r => `
    <tr class="${r.failure_count > 0 ? 'row-fail' : r.min_margin_db < 5 ? 'row-warn' : 'row-ok'}">
      <td>${r.label}</td>
      <td>${r.module}</td>
      <td>${r.tx_antenna}</td>
      <td>${r.gw_antenna}</td>
      <td>${r.min_margin_db.toFixed(1)}</td>
      <td>${r.mean_margin_db.toFixed(1)}</td>
      <td>${r.failure_count}</td>
      <td>${r.robustness_score.toFixed(2)}</td>
    </tr>
  `).join("");

  container.innerHTML = `<table><thead>${thead}</thead><tbody>${tbody}</tbody></table>`;
}
```

---

## Etapa 7 — Estimativa de Consumo no Painel de Biblioteca

**Objetivo:** na página `library.html`, ao selecionar um módulo LoRa, mostrar estimativa de energia.

### 7.1 — Adicionar painel de energia em `library.html`

Criar seção de módulos LoRa com campos SF, potência e botão de estimativa:

```html
<section id="lora-modules-panel">
  <h2>Módulos LoRa</h2>
  <div id="lora-modules-list"><!-- preenchido pelo JS --></div>

  <h3>Estimativa de consumo</h3>
  <label>Módulo: <select id="energy-module-select"></select></label>
  <label>SF: <select id="energy-sf">
    <option value="7">7</option><option value="10">10</option>
    <option value="12" selected>12</option>
  </select></label>
  <label>Potência TX (dBm): <input id="energy-tx-power" type="number" value="20"></label>
  <label>Transmissões/dia: <input id="energy-tx-count" type="number" value="96"></label>
  <button onclick="runEnergyEstimate()">Calcular</button>
  <div id="energy-result"></div>
</section>
```

### 7.2 — Implementar em `api-client.js` (ou novo `library.js`)

```javascript
async function runEnergyEstimate() {
  const moduleId = document.getElementById("energy-module-select").value;
  const sf = document.getElementById("energy-sf").value;
  const txPower = document.getElementById("energy-tx-power").value;
  const txCount = document.getElementById("energy-tx-count").value;

  const url = `/api/v1/library/lora-modules/${moduleId}/energy?sf=${sf}&tx_power_dbm=${txPower}&transmissions_per_day=${txCount}`;
  const resp = await fetch(url, { method: "POST" });
  const data = await resp.json();

  document.getElementById("energy-result").innerHTML = `
    <table>
      <tr><td>Tempo no ar (ToA)</td><td>${data.tx_duration_ms.toFixed(1)} ms</td></tr>
      <tr><td>Energia por TX</td><td>${data.energy_per_tx_mj.toFixed(3)} mJ</td></tr>
      <tr><td>Energia/dia</td><td>${data.daily_energy_mwh.toFixed(3)} mWh</td></tr>
      <tr><td>Vida útil (bat. 2000 mAh/3.3V)</td>
          <td>${data.battery_life_days ? data.battery_life_days.toFixed(0) + " dias" : "∞"}</td></tr>
    </table>
  `;
}
```

---

## Critério de Conclusão da Fase 5

- [ ] Abrir `http://localhost:8000/link-planner.html` — coordenadas padrão são no DF, não SP
- [ ] Calcular link entre dois nós a >200 km → aviso aparece no painel de resultado
- [ ] Dropdown de módulo LoRa popula ao carregar — ao selecionar RFM95W, `rx_sensitivity_dbm` muda para -139
- [ ] Campos de azimute, tilt, extra_loss, fading e polarização aparecem em "Configurações avançadas"
- [ ] Botão "Exportar Setup" faz download de JSON sem campos de resultado
- [ ] Botão "Exportar Completo" faz download de JSON com campos de resultado (se cenário foi calculado)
- [ ] Select de modelo de propagação visível; ao selecionar Okumura-Hata e calcular, `path_loss_db` no resultado é diferente do FSPL
- [ ] Botão "Executar Comparação" mostra tabela com ao menos 1 linha e colunas de margem/falhas/robustez
- [ ] Em `library.html`, estimativa de energia retorna `battery_life_days` > 1 para RFM95W SF12
- [ ] Nenhuma funcionalidade anterior regride (P2P, topologias, KML, site selection continuam funcionando)
