## BLOCO 1: SANDBOX DE SIMULAÇÃO

**Objetivo**: Construir e validar ambiente controlado para modelagem de antenas e enlaces, independentemente de dados geográficos reais.

**Duração estimada**: ~16-19 dias  
**Sprints**: 0.5, 0, 1, 2-3, 4, 5-6, 7

```
Bloco 1 = Núcleo científico + computacional do projeto
```

<!-- --- -->

### CP-0.5 | DOCUMENTAÇÃO TÉCNICA

**Duração**: 2 dias  
**Status**: BLOQUEADOR — nenhum sprint avança sem este  

**Entregas**:
- `docs/formulas.md` — fórmulas com derivações e referências (Balanis, Pozar, ARRL)
- `docs/antenna_details.md` — dimensões e parâmetros por tipo de antena
- `docs/propagation_model.md` — FSPL, obstáculos, Fresnel
- `docs/assumptions.md` — premissas do modelo
- `docs/limitations.md` — tudo que MVP NÃO faz
- `docs/validation.md` — casos de teste com valores esperados
- `docs/accuracy_matrix.md` — tolerâncias por tipo de cálculo
- `docs/references.md` — citações bibliográficas completas

**Critérios de Aceite**:
- [ ] 8 arquivos `.md` criados e estruturados
- [ ] Todas as fórmulas com unidades explícitas
- [ ] ≥ 15 casos de teste documentados e rastreáveis
- [ ] Limitações explícitas (sem surpresas)

**Commit**: `docs: checkpoint 0.5 - technical documentation`

<!-- --- -->

### CP-0 | INFRAESTRUTURA

**Duração**: 1-2 dias  
**Bloqueador**: CP-0.5 ✓

**Entregas**:
- Estrutura de diretórios criada (`src/`, `tests/`, `docs/`)
- `pyproject.toml` com dependências (`uv`)
- Streamlit app mínima rodando em `localhost:3953`
- `Dockerfile` + `docker-compose.yml` funcional
- Git inicializado com `.gitignore`

**Critérios de Aceite**:
- [ ] `uv run streamlit run src/lora_antenna/app.py --server.port 3953` funciona
- [ ] App abre em `http://localhost:3953`
- [ ] Docker build sem erro
- [ ] Docker Compose sobe em `http://0.0.0.0:3953`

**Commit**: `feat: checkpoint 0 - project scaffolding and infra`

<!-- --- -->

### CP-1 | NÚCLEO MATEMÁTICO

**Duração**: 3-4 dias  
**Bloqueador**: CP-0 ✓

**Entregas**:
- `src/lora_antenna/constants.py` — constantes físicas (c, π, ε₀)
- `src/lora_antenna/formulas.py` — funções matemáticas base:
  - `wavelength_m(frequency_hz)`
  - `effective_area_m2(gain_dbi, wavelength_m)`
  - `reflection_coefficient(z_load, z0)`
  - `vswr(z_load, z0)`
  - `return_loss_db(gamma)`
  - `fspl_db(distance_m, frequency_hz)`
  - `friis_received_power_dbm(...)`
- `tests/test_formulas.py` — casos de validação contra literatura

**Caso de teste obrigatório**:
```
Friis @ 915 MHz, 1 km:
  Input: Pt=14 dBm, Gt=2.15 dBi, Gr=2.15 dBi, d=1000m, f=915e6 Hz
  Expected: Pr ≈ -73.37 dBm
  Tolerance: ±0.5 dB
  Source: Friis equation
```

**Critérios de Aceite**:
- [ ] `pytest tests/test_formulas.py` passa 100%
- [ ] Coverage > 95%
- [ ] Sem warnings (`ruff`, `mypy`)
- [ ] Todos os casos dentro de tolerância

**Commit**: `feat: checkpoint 1 - core math formulas validated`

<!-- --- -->

### CP-2-3 | CLASSES ANTENNA

**Duração**: 5-6 dias  
**Bloqueador**: CP-1 ✓

**Entregas**:
- `src/lora_antenna/antenna/base.py` — classe `Antenna` (Pydantic BaseModel)
- `src/lora_antenna/antenna/monopole.py` — `Monopole` (λ/4, 2.15 dBi)
- `src/lora_antenna/antenna/dipole.py` — `Dipole` (λ/2, ambientes)
- `src/lora_antenna/antenna/ground_plane.py` — `GroundPlane` (plano parametrizado)
- `src/lora_antenna/antenna/patch.py` — `Patch` (substratos: FR4, Rogers)
- `src/lora_antenna/antenna/yagi.py` — `Yagi` (fórmula Cebik, 3-10 elementos)
- `src/lora_antenna/antenna/reflector.py` — `ReflectorAntenna` (circular, offset, cassegrain)
- `src/lora_antenna/antenna/feed.py` — `FeedSpecification` (7 tipos, η = 0.40-0.88)
- `tests/test_antenna_*.py` — um arquivo por classe

**Critérios de Aceite**:
- [ ] 6 classes de antena + `FeedSpecification` implementados
- [ ] Serialização Pydantic funciona (`to_json`, `from_json`)
- [ ] `pytest tests/test_antenna_*.py` passa
- [ ] Impedância, VSWR, ganho dentro de faixas esperadas
- [ ] Warnings e disclaimers aparecem corretamente

**Commit**: `feat: checkpoint 2-3 - antenna classes with Pydantic`

<!-- --- -->

### CP-4 | UI STANDALONE

**Duração**: 3-4 dias  
**Bloqueador**: CP-2-3 ✓

**Entregas**:
- `src/lora_antenna/pages/antenna_builder.py` — UI para criar qualquer tipo de antena
- Seletor de tipo de antena
- Formulário de parâmetros dinâmico por tipo
- Exibição de parâmetros calculados (gain, impedância, VSWR, λ, dimensões)
- Export/import JSON
- Gráfico básico de ganho (Plotly)

**Critérios de Aceite**:
- [ ] Streamlit app roda sem erro
- [ ] Todos os 6 tipos de antena criáveis via UI
- [ ] Parâmetros calculados exibidos corretamente
- [ ] JSON exporta/importa sem perda
- [ ] Gráficos renderizam (sem crash)

**Commit**: `feat: checkpoint 4 - standalone antenna UI`

<!-- --- -->

### CP-5-6 | LINK BUDGET + DIRETIVIDADE

**Duração**: 5-6 dias  
**Bloqueador**: CP-4 ✓

**Entregas**:
- `src/lora_antenna/propagation/link.py` — `LinkBudget` (Friis básico)
- `src/lora_antenna/propagation/link_directivity.py` — `LinkWithDirectivity` (azimute/elevação)
- `src/lora_antenna/rf_chain/chain.py` — `TXChain`, `RXChain`, `LinkBudgetComplete`
  - PA, LNA, filtros, cabos, conectores modelados
- `src/lora_antenna/pages/link_budget.py` — UI para dois antennas + link
- `tests/test_friis_budget.py`
- `tests/test_link_directivity.py`

**Critérios de Aceite**:
- [ ] `LinkBudget`, `LinkWithDirectivity`, `LinkBudgetComplete` implementados
- [ ] RF chain completo (PA, LNA, filtros, cabos, conectores)
- [ ] Margem de enlace calculada corretamente
- [ ] Comparação PA/LNA on/off mostra diferenças reais
- [ ] `pytest tests/test_friis_budget.py` passa

**Commit**: `feat: checkpoint 5-6 - link budget with RF chain`

<!-- --- -->

### CP-7 | VISUALIZAÇÕES

**Duração**: 5-6 dias  
**Bloqueador**: CP-5-6 ✓

**Entregas**:
- `src/lora_antenna/visualizations/polar.py` — diagramas polares (azimute + elevação)
- `src/lora_antenna/visualizations/pattern_3d.py` — padrão 3D simplificado (skeleton aceitável)
- `src/lora_antenna/visualizations/power_distance.py` — gráfico potência vs distância
- `src/lora_antenna/visualizations/chain_breakdown.py` — breakdown TX/RX chain
- Disclaimers `"MODELO SIMPLIFICADO"` em todos os gráficos

**Critérios de Aceite**:
- [ ] Gráficos polares renderizam para todos os tipos de antena
- [ ] Padrão 3D implementado (ou skeleton explícito)
- [ ] Gráficos potência vs distância corretos
- [ ] TX/RX chain breakdown visual funciona
- [ ] Disclaimers `"SIMPLIFIED"` nos gráficos

**Commit**: `feat: checkpoint 7 - radiation pattern visualizations`
