# Estrutura de Arquivos — Projeto e Análise de Antenas para Rede LoRa/LoRaWAN Aplicada a Sistema de Segurança da UnB

**Versão**: V0  
**Data**: 2026-06-10  

---

## Árvore de Pastas

```text
./lora-network-unb
    ├── pyproject.toml
    ├── uv.lock
    ├── Dockerfile
    ├── docker-compose.yml
    ├── README.md
    ├── .gitignore
    ├── docs/
    │   ├── formulas.md
    │   ├── antenna_details.md
    │   ├── antenna_types_complete.md
    │   ├── feed_specifications.md
    │   ├── propagation_model.md
    │   ├── tx_rx_chain_analysis.md
    │   ├── assumptions.md
    │   ├── limitations.md
    │   ├── validation.md
    │   ├── accuracy_matrix.md
    │   ├── test_cases.md
    │   ├── architecture.md
    │   └── references.md
    ├── src/
    │   └── lora_antenna/
    │       ├── __init__.py
    │       ├── app.py
    │       ├── config.py
    │       ├── constants.py
    │       │
    │       ├── antenna/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   ├── monopole.py
    │       │   ├── dipole.py
    │       │   ├── ground_plane.py
    │       │   ├── patch.py
    │       │   ├── yagi.py
    │       │   ├── reflector.py
    │       │   └── feeds.py
    │       │
    │       ├── rf_chain/
    │       │   ├── __init__.py
    │       │   ├── components.py
    │       │   ├── cables.py
    │       │   └── chain.py
    │       │
    │       ├── propagation/
    │       │   ├── __init__.py
    │       │   ├── friis.py
    │       │   ├── link_budget.py
    │       │   ├── link_directivity.py
    │       │   ├── obstacles.py
    │       │   └── fresnel.py
    │       │
    │       ├── patterns/
    │       │   ├── __init__.py
    │       │   └── radiation.py
    │       │
    │       ├── persistence/
    │       │   ├── __init__.py
    │       │   ├── schemas.py
    │       │   ├── json_store.py
    │       │   └── sqlite_store.py
    │       │
    │       ├── geo/
    │       │   ├── __init__.py
    │       │   ├── grid.py
    │       │   ├── coverage.py
    │       │   └── layers.py
    │       │
    │       ├── reports/
    │       │   ├── __init__.py
    │       │   └── markdown.py
    │       │
    │       └── ui/
    │           ├── __init__.py
    │           ├── pages.py
    │           ├── components.py
    │           ├── antenna_forms.py
    │           ├── link_forms.py
    │           ├── charts.py
    │           └── maps.py
    └── tests/
        ├── fixtures/
        │   ├── antennas.json
        │   └── known_cases.json
        ├── validation_matrix.md
        ├── test_formulas.py
        ├── test_antenna_monopole.py
        ├── test_antenna_dipole.py
        ├── test_antenna_ground_plane.py
        ├── test_antenna_patch.py
        ├── test_antenna_yagi.py
        ├── test_antenna_reflector.py
        ├── test_feeds.py
        ├── test_friis_budget.py
        ├── test_link_directivity.py
        ├── test_obstacles.py
        ├── test_rf_chain.py
        └── test_persistence.py
```

---

## Descrição das Pastas

### Raiz do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `pyproject.toml` | Configuração do projeto Python: dependências, versão mínima (3.11+), ferramentas de dev (ruff, mypy, pytest). Gerenciado por `uv`. |
| `uv.lock` | Lockfile gerado pelo `uv` — garante reprodutibilidade exata do ambiente. Não editar manualmente. |
| `Dockerfile` | Imagem Docker para empacotamento e deploy. Base Python 3.11-slim, expõe porta 3953. |
| `docker-compose.yml` | Orquestração Docker local: monta `src/` e `docs/` como volumes, porta 3953 na LAN. |
| `README.md` | Instruções de instalação, uso, limitações e referências do projeto. |

---

### `docs/`

Documentação técnica obrigatória. Criada no **CP-0.5**, antes de qualquer código científico. Toda aproximação física do modelo deve estar documentada aqui.

| Arquivo | Descrição |
|---------|-----------|
| `formulas.md` | Todas as equações implementadas com derivações, unidades explícitas e referências (Balanis, Pozar, ARRL). |
| `antenna_details.md` | Dimensões geométricas, parâmetros nominais e faixas esperadas por tipo de antena (Monopole, Dipole, Patch, Yagi, Reflector). |
| `antenna_types_complete.md` | Tipos de antena suportados com foco em LoRa: comparação, casos de uso, ganho esperado, disclaimers. |
| `feed_specifications.md` | 7 tipos de alimentadores (feeds) com eficiências tabeladas (0.40–0.88), beamwidth, e impacto no ganho de antenas refletoras. |
| `propagation_model.md` | Modelos de propagação: FSPL, tabela de obstáculos (~~433 MHz~~ (Fora da faixa definida pela ANATEL) / ~~868 MHz~~ (Fora da faixa definida pela ANATEL) / 915 MHz), Fresnel zones. Inclui min/nominal/max por tipo de obstáculo. |
| `tx_rx_chain_analysis.md` | Análise da cadeia RF completa TX/RX: PA, LNA, filtros, circulador, cabos, conectores. Erro sem modelagem: ±35 dB. Com: ±3–5 dB. |
| `assumptions.md` | Premissas do modelo científico: campo distante, terra plana, polarização alinhada, sem fading, sem DEM. |
| `limitations.md` | Tudo que o MVP **não** faz: sem lóbulos secundários reais, sem multipercurso, sem DEM, sem calibração hardware. |
| `validation.md` | Casos de teste com entrada, valor esperado, tolerância e fonte bibliográfica (≥15 casos). |
| `accuracy_matrix.md` | Precisão esperada por cenário: LOS ±1–2 dB, NLOS ±8–15 dB, diretivas ±15–25 dB. |
| `test_cases.md` | Casos de teste detalhados para validação numérica de fórmulas. Complementa `validation.md`. |
| `architecture.md` | Visão arquitetural do sistema: módulos, dependências, fluxo de dados, decisões de design. |
| `references.md` | Todas as citações bibliográficas: ARRL Antenna Book, Balanis (Antenna Theory, 3ª ed.), Pozar (Microwave Engineering, 4ª ed.), Semtech, LoRa Alliance. |

---

### `src/lora_antenna/`

Pacote Python principal. Instalado via `uv` como pacote editável. Ponto de entrada: `app.py`.

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Ponto de entrada Streamlit. Configura navegação entre páginas e carrega estado global. |
| `config.py` | Configurações da aplicação: porta, caminhos de dados, flags de debug, presets de gateway. |
| `constants.py` | Constantes físicas (`c`, `π`, `ε₀`, `Z0=50Ω`) e bandas LoRa (~~433 MHz~~ (Fora da faixa definida pela ANATEL), ~~868 MHz~~ (Fora da faixa definida pela ANATEL), 915 MHz) com sensibilidades SX1276 por SF/BW. |

---

### `src/lora_antenna/antenna/`

Classes de antena. Hierarquia baseada em `Antenna` (Pydantic BaseModel). Cada subclasse calcula seus próprios parâmetros físicos ao instanciar.

| Arquivo | Descrição |
|---------|-----------|
| `base.py` | Modelo Pydantic base `Antenna`: `id`, `name`, `frequency_hz`, `gain_dbi`, `impedance_ohm`, `vswr`, `efficiency`, `polarization`, `effective_area_m2`, `orientation_azimuth_deg`, `orientation_elevation_deg`, `location`, `schema_version`. |
| `monopole.py` | Monopolo λ/4. Ganho ~2.15 dBi. Impedância ressonante ~36.5+j21Ω. Disclaimer de plano de terra obrigatório. |
| `dipole.py` | Dipolo λ/2 com 4 ambientes parametrizados: `free_space`, `above_ground`, `near_structure`, `cavity`. Impedância e VSWR ajustados por ambiente. |
| `ground_plane.py` | Monopolo λ/4 sobre plano de terra parametrizado (tamanho em λ, forma: square/circular/infinite). Aviso quando plano < 1λ (desvio > 20%). |
| `patch.py` | Antena microstrip (patch). Substrato obrigatório: FR4, Rogers 4003, Rogers 5880, Duroid. Dimensões por fórmulas de Pozar. Ganho 5–9 dBi conforme substrato. |
| `yagi.py` | Yagi-Uda de 3–10 elementos. Ganho empírico via fórmula Cebik. HPBW ∝ 1/ganho. Orientação explícita obrigatória em enlaces. |
| `reflector.py` | `ReflectorAntenna`: base para paraboloides. Tipos: `parabolic_circular`, `parabolic_offset`, `cassegrain`, `gregorian`. Ganho = η_total × (πD/λ)². Exige `FeedSpecification`. |
| `feeds.py` | `FeedSpecification` e enum `FeedType` com 7 tipos (horn_pyramidal, horn_conical_corrugated, horn_exponential, dipole, patch, helical, probe). Eficiência 0.40–0.88 determina ganho final da refletora. |

---

### `src/lora_antenna/rf_chain/`

Modelagem completa da cadeia RF entre o rádio e a antena. Sem esta cadeia, erro acumulado em gateways corporativos pode chegar a ±35 dB.

| Arquivo | Descrição |
|---------|-----------|
| `components.py` | Modelos de componentes RF: PA (Power Amplifier), LNA (Low Noise Amplifier), filtros TX/RX, circulador/diplexador, conectores, balun/acoplador. |
| `cables.py` | Tabela de perdas por tipo de cabo (RG-58, RG-8, RG-214, LMR-400, Waveguide) em dB/100m @ 915 MHz. Função `cable_loss_db(cable_type, length_m, frequency_mhz)`. |
| `chain.py` | `TXChain`, `RXChain` e `LinkBudgetComplete`. Modela potência passo a passo: TX_power → PA → filtro → circulador → cabo → conectores → antena → espaço livre → antena → conectores → cabo → circulador → filtro → LNA → chip RX. |

---

### `src/lora_antenna/propagation/`

Modelos de propagação de sinal no meio físico. Separação entre funções puras (`friis.py`) e modelos compostos (`link_budget.py`).

| Arquivo | Descrição |
|---------|-----------|
| `friis.py` | Funções puras de propagação: `wavelength_m`, `fspl_db`, `friis_received_power_dbm`, `link_margin_db`, `eirp_dbm`. Base matemática do projeto. |
| `link_budget.py` | Modelos compostos: `LinkBudget` (Friis básico TX↔RX com parâmetros de antena e distância). |
| `link_directivity.py` | `LinkWithDirectivity` e `GeographicPosition`. Calcula ângulo TX→RX e RX→TX, aplica redução de ganho por off-axis. Compara `Pr_ideal` vs `Pr_with_directivity`. |
| `obstacles.py` | `ObstacleType` enum + tabela de atenuação por frequência (~~433 MHz~~ (Fora da faixa definida pela ANATEL) / ~~868 MHz~~ (Fora da faixa definida pela ANATEL) / 915 MHz) com min/nominal/max. Tipos: parede tijolo, concreto, vidro, vegetação densa/esparsa, edifício. |
| `fresnel.py` | Skeleton de zona de Fresnel: raio R₁, percentual de bloqueio, warning de obstrução. Perda real dependente de DEM (fase futura). |

---

### `src/lora_antenna/patterns/`

Padrões de radiação aproximados para visualização. Todos com disclaimers explícitos de modelo simplificado.

| Arquivo | Descrição |
|---------|-----------|
| `radiation.py` | Geração de padrões de radiação 2D/3D por tipo de antena. Omnidirecionais: padrão toroidal. Diretivas: modelo cos^n (Yagi) e feixe estreito (Reflector). Disclaimer obrigatório em toda saída. |

---

### `src/lora_antenna/persistence/`

Camada de persistência. Suporta JSON (portabilidade) e SQLite (histórico e consulta).

| Arquivo | Descrição |
|---------|-----------|
| `schemas.py` | Schemas Pydantic para persistência: `AntennaRecord`, `FeedRecord`, `LinkRecord`, `CoverageRunRecord`, `ReportRecord`. Campo `schema_version` para migração. |
| `json_store.py` | Leitura e escrita de antenas, feeds, links e simulações em JSON. Validação via Pydantic. |
| `sqlite_store.py` | Tabelas SQLite: `antennas`, `feeds`, `links`, `coverage_runs`, `reports`. Consultas por parâmetros. |

---

### `src/lora_antenna/geo/`

Módulo geográfico. **Exclusivo do Bloco 2** (Campus Darcy Ribeiro). Reutiliza objetos `Antenna` e `Link` do Bloco 1 sem modificação.

| Arquivo | Descrição |
|---------|-----------|
| `grid.py` | Geração de grade espacial configurável (5–50m) sobre área geográfica delimitada. |
| `coverage.py` | Cálculo de potência recebida em cada ponto da grade usando `LinkBudget` do Bloco 1. Produz matriz de cobertura. |
| `layers.py` | Importação e gerenciamento de camadas geográficas: shapefile Campus Darcy Ribeiro (UnB), limites, edifícios. |

---

### `src/lora_antenna/reports/`

Geração de relatórios técnicos exportáveis.

| Arquivo | Descrição |
|---------|-----------|
| `markdown.py` | Geração de relatório Markdown estruturado: parâmetros de antena, fórmulas usadas, tabelas de link budget, gráficos exportados, accuracy matrix e seção obrigatória de limitações do modelo. |

---

### `src/lora_antenna/ui/`

Camada de interface Streamlit. Primeira tela deve ser ferramenta, não landing page.

| Arquivo | Descrição |
|---------|-----------|
| `pages.py` | Definição e roteamento das páginas: Antena, Enlace, Diretividade, Cobertura, Biblioteca, Relatórios, Limitações. |
| `components.py` | Componentes reutilizáveis: cards de parâmetros, badges de warning, tabelas de resultado, disclaimers de modelo simplificado. |
| `antenna_forms.py` | Formulários dinâmicos por tipo de antena: frequência, parâmetros geométricos, substrato (Patch), feed (Reflector), orientação (diretivas). |
| `link_forms.py` | Formulários de enlace: seleção TX/RX, distância, potência TX, SF/BW/sensibilidade, modo simples ou cadeia RF completa, obstáculos. |
| `charts.py` | Gráficos Plotly: diagramas polares (azimute/elevação), padrão 3D, potência vs distância, breakdown TX/RX chain. |
| `maps.py` | Mapa Folium para página Cobertura: exibição de campus, posicionamento interativo de antena, heatmap de potência por ponto de grade. |

---

### `tests/`

Suite de testes. Cada teste deve ter: entrada numérica, resultado esperado, tolerância e fonte em comentário.

| Pasta/Arquivo | Descrição |
|---------------|-----------|
| `fixtures/antennas.json` | Antenas de referência pré-configuradas para reuso entre testes. |
| `fixtures/known_cases.json` | Casos conhecidos da literatura com valores esperados e tolerâncias (ex.: FSPL 1km@915MHz = 91.67 dB). |
| `validation_matrix.md` | Matriz de precisão: cenário × tolerância esperada × fonte. Base para critérios de aceite de cada checkpoint. |
| `test_formulas.py` | Testes de funções puras: λ, FSPL, Friis, VSWR, EIRP. Validação contra casos conhecidos (±0.5 dB). |
| `test_antenna_monopole.py` | Monopolo: comprimento λ/4, ganho, impedância, serialização Pydantic. |
| `test_antenna_dipole.py` | Dipolo: 4 ambientes, impedância por ambiente, VSWR contra 50Ω. |
| `test_antenna_ground_plane.py` | Ground Plane: impedância vs tamanho do plano, warning para plano < 1λ. |
| `test_antenna_patch.py` | Patch: dimensões Pozar por substrato, ganho por substrato, serialização. |
| `test_antenna_yagi.py` | Yagi: ganho Cebik para 3/5/7/10 elementos, HPBW, serialização. |
| `test_antenna_reflector.py` | ReflectorAntenna: ganho = η_aperture × η_feed × ganho_geométrico, HPBW, tipos (circular/offset/cassegrain). |
| `test_feeds.py` | FeedSpecification: 7 tipos, eficiências na faixa 0.40–0.88, impacto no ganho da refletora. |
| `test_friis_budget.py` | LinkBudget e LinkBudgetComplete: Friis básico, cadeia TX/RX completa, margem de enlace. |
| `test_link_directivity.py` | LinkWithDirectivity: perda por desalinhamento Yagi (>10 dB @ 90°), Reflector (>20 dB @ 90°). |
| `test_obstacles.py` | Tabela de atenuação: valores nominais para cada obstáculo nas 3 frequências. |
| `test_rf_chain.py` | Cadeia RF: PA, LNA, filtros, cabos, conectores — EIRP e potência recebida passo a passo. |
| `test_persistence.py` | JSON e SQLite: salvar, carregar, validar via Pydantic, migração de schema_version. |
