# V1 Architecture Specification — Block V1

**Status**: especificação arquitetural aprovada para implementação  
**Escopo**: Bloco V1 da plataforma LoRa/LoRaWAN com Sandbox RF, integração KML/GIS e simulação multiponto no Campus Darcy Ribeiro  
**Fonte de decisão**: `_doc/_plan/rise_3/integracao_kml_analise_arquitetural.md`  
**Restrição regulatória**: no Brasil, LoRa deve operar somente na faixa `915-928 MHz`; o default de simulação é `915e6 Hz`.

---

## 1. File_structure

```text
lora-antenna-platform/
├── pyproject.toml
├── uv.lock
├── README.md
├── .streamlit/
│   └── config.toml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── formulas.md
│   ├── antenna_models.md
│   ├── propagation_models.md
│   ├── gis_kml_contracts.md
│   ├── report_templates.md
│   └── regulatory_anatel_915_928.md
├── src/
│   └── lora_antenna/
│       ├── __init__.py
│       ├── app.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   ├── formulas.py
│       │   ├── validators.py
│       │   ├── models.py
│       │   └── units.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── geo.py
│       ├── antenna/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── monopole.py
│       │   ├── dipole.py
│       │   ├── ground_plane.py
│       │   ├── patch.py
│       │   ├── yagi.py
│       │   ├── reflector.py
│       │   ├── feeds.py
│       │   └── factory.py
│       ├── propagation/
│       │   ├── __init__.py
│       │   ├── friis.py
│       │   ├── link_budget.py
│       │   ├── link_directivity.py
│       │   ├── obstacles.py
│       │   ├── sensitivity.py
│       │   └── batch/
│       │       ├── __init__.py
│       │       ├── contracts.py
│       │       ├── executor.py
│       │       └── dataframe_adapter.py
│       ├── rf_chain/
│       │   ├── __init__.py
│       │   ├── chain.py
│       │   ├── cables.py
│       │   ├── filters.py
│       │   └── devices.py
│       ├── gis/
│       │   ├── __init__.py
│       │   ├── kml_parser.py
│       │   ├── shapefile_handler.py
│       │   ├── distance_matrix.py
│       │   ├── geodesic.py
│       │   ├── multi_link.py
│       │   ├── campus_context.py
│       │   ├── heatmap.py
│       │   ├── map_renderer.py
│       │   └── reference_tables.py
│       ├── reports/
│       │   ├── __init__.py
│       │   ├── markdown_report.py
│       │   ├── tables.py
│       │   ├── figures.py
│       │   └── export.py
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── antenna_builder.py
│       │   ├── link_budget.py
│       │   ├── campus_coverage.py
│       │   └── reports.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── charts.py
│       │   ├── tables.py
│       │   ├── state.py
│       │   └── components.py
│       └── persistence/
│           ├── __init__.py
│           ├── schemas.py
│           ├── repositories.py
│           └── migrations/
│               └── 001_initial.sql
└── tests/
    ├── fixtures/
    │   ├── campus_p1_p8.kml
    │   ├── campus_boundary.kml
    │   ├── invalid_empty.kml
    │   ├── invalid_duplicate_labels.kml
    │   └── known_link_cases.json
    ├── unit/
    │   ├── test_core_constants.py
    │   ├── test_core_formulas.py
    │   ├── test_core_validators.py
    │   ├── test_antenna_monopole.py
    │   ├── test_antenna_dipole.py
    │   ├── test_antenna_ground_plane.py
    │   ├── test_antenna_patch.py
    │   ├── test_antenna_yagi.py
    │   ├── test_antenna_reflector.py
    │   ├── test_rf_chain.py
    │   ├── test_friis.py
    │   ├── test_link_budget.py
    │   ├── test_link_directivity.py
    │   └── test_obstacles.py
    ├── gis/
    │   ├── test_kml_parser.py
    │   ├── test_shapefile_handler.py
    │   ├── test_geodesic.py
    │   ├── test_distance_matrix.py
    │   ├── test_multi_link.py
    │   ├── test_campus_context.py
    │   └── test_map_renderer_contracts.py
    ├── integration/
    │   ├── test_kml_to_distance_matrix.py
    │   ├── test_kml_to_batch_link_budget.py
    │   ├── test_campus_coverage_session_state.py
    │   └── test_report_from_batch_results.py
    └── e2e/
        ├── test_streamlit_antenna_builder.py
        ├── test_streamlit_campus_kml_upload.py
        └── test_streamlit_report_download.py
```

---

## 2. Princípios Arquiteturais V1

### 2.1 Fronteira entre Bloco 1 e Bloco 2

O Bloco 1 é o motor matemático e eletromagnético. Ele contém fórmulas, modelos de antena, cadeia RF, perdas, sensibilidade e link budget. O Bloco 2 é a camada geográfica. Ele traduz arquivos e coordenadas para entradas numéricas consumíveis pelo Bloco 1.

O Bloco 1 nunca deve importar:

- `lora_antenna.gis`
- `streamlit`
- `folium`
- `geopandas`
- `pyproj` diretamente, exceto se a dependência for encapsulada em `gis/geodesic.py`
- parsers KML, shapefile ou qualquer formato de arquivo geográfico
- `st.session_state`

O Bloco 2 pode importar:

- `lora_antenna.core`
- `lora_antenna.models`
- `lora_antenna.antenna`
- `lora_antenna.propagation`
- `lora_antenna.rf_chain`

Essa direção de dependência é intencional. O Bloco 2 conhece o motor RF para montar simulações; o motor RF não conhece o contexto geográfico.

### 2.2 Dados Batch como padrão oficial

V1 adota estruturas batch como contrato de primeira classe. O sistema deve suportar vetores de pontos, matrizes de distância e listas de pares de enlace sem forçar a UI a iterar regras de domínio.

Contratos oficiais:

- `KMLPoint`: ponto extraído de arquivo KML.
- `KMLDocument`: documento validado com metadados e lista de pontos.
- `GeographicPosition`: posição neutra WGS84 e campos cartesianos compatíveis.
- `DistanceMatrix`: matriz triangular de distâncias geodésicas por par de labels.
- `LinkPair`: par lógico de enlace com distância e parâmetros RF.
- `LinkBatchRequest`: requisição batch para N pares.
- `LinkBatchResult`: resultado individual com FSPL, potência recebida, margem e status.
- `GeographicSessionContext`: contexto de upload, CRS, hash, warnings e versão de schema.

### 2.3 Estados de upload e sessão geográfica

O estado de arquivos e resultados deve ficar isolado em `pages/campus_coverage.py` ou em helpers de `ui/state.py`.

Chaves obrigatórias:

- `kml_document`: `KMLDocument | None`
- `distance_matrix`: `DistanceMatrix | None`
- `geo_context`: `GeographicSessionContext | None`
- `link_batch_request`: `LinkBatchRequest | None`
- `link_results`: `list[LinkBatchResult] | None`
- `selected_pairs`: `list[tuple[str, str]] | None`

Regras de reset:

- Novo upload de KML apaga `distance_matrix`, `link_batch_request`, `link_results` e `selected_pairs`.
- Mudança de antena, potência, sensibilidade, perdas ou frequência apaga `link_results`.
- Mudança apenas de visualização não recalcula batch.
- O hash do arquivo carregado deve ser armazenado em `geo_context.file_sha256`.

---

## 3. Bloco `core/`

### 3.1 Propósito e Escopo

`src/lora_antenna/core/` isola constantes físicas, fórmulas matemáticas puras, validações de unidade e modelos Pydantic base. Este bloco é determinístico, sem estado global mutável, sem leitura de arquivos e sem dependências de UI.

### 3.2 Módulos e Classes Principais

`constants.py`:

- `C_M_PER_S = 299_792_458`
- `Z0_OHM = 50.0`
- `LORA_BR_MIN_HZ = 915e6`
- `LORA_BR_MAX_HZ = 928e6`
- `LORA_DEFAULT_HZ = 915e6`
- `EPSILON_0_F_PER_M`
- `MU_0_H_PER_M`

`formulas.py`:

- `wavelength_m(frequency_hz: float) -> float`
- `effective_area_m2(gain_dbi: float, wavelength_m: float) -> float`
- `reflection_coefficient(z_load: complex, z0: float) -> complex`
- `vswr(gamma: complex) -> float`
- `return_loss_db(gamma: complex) -> float`
- `dbi_to_linear(gain_dbi: float) -> float`
- `linear_to_dbi(gain_linear: float) -> float`

`validators.py`:

- `validate_lora_br_frequency_hz(frequency_hz: float) -> float`
- `validate_positive_distance_m(distance_m: float) -> float`
- `validate_gain_dbi(gain_dbi: float) -> float`
- `validate_power_dbm(power_dbm: float) -> float`

`models.py`:

- `SimulationMetadata`
- `ValidationWarning`
- `FrequencyConfig`
- `SerializableModel`

`units.py`:

- `mhz_to_hz(value_mhz: float) -> float`
- `hz_to_mhz(value_hz: float) -> float`
- `dbm_to_mw(value_dbm: float) -> float`
- `mw_to_dbm(value_mw: float) -> float`

### 3.3 Ingestão e Fluxo de Dados

`core/` recebe apenas escalares e estruturas Pydantic genéricas. Ele não recebe arquivos, bytes, dataframes, coordenadas geográficas ou objetos Streamlit. O fluxo é:

```text
Entrada numérica validada
  -> validators.py
  -> formulas.py
  -> retorno escalar ou modelo base
```

### 3.4 Restrições Arquiteturais

- `core/` não importa `antenna/`, `propagation/`, `gis/`, `pages/`, `reports/` ou `persistence/`.
- `core/` não conhece `KMLPoint`, `KMLDocument`, `DistanceMatrix` ou Folium.
- Toda frequência LoRa configurável deve passar por `validate_lora_br_frequency_hz`.
- Fórmulas devem ser puras, testáveis e livres de I/O.

---

## 4. Bloco `models/`

### 4.1 Propósito e Escopo

`src/lora_antenna/models/` contém modelos de dados neutros compartilhados por mais de uma camada. O principal contrato V1 é `GeographicPosition`, extraído de `propagation/link_directivity.py` para evitar dependência circular entre `gis/` e `propagation/`.

### 4.2 Módulos e Classes Principais

`geo.py`:

- `GeographicPosition`
- `CoordinateReferenceSystem`
- `GeographicBounds`

`GeographicPosition` deve conter:

- `label: str`
- `latitude: float`
- `longitude: float`
- `altitude_m: float = 0.0`
- `x_m: float = 0.0`
- `y_m: float = 0.0`
- `z_m: float = 0.0`

Campos `x_m`, `y_m` e `z_m` existem para retrocompatibilidade com cálculo cartesiano em `LinkWithDirectivity`. Campos `latitude`, `longitude` e `altitude_m` existem para o Bloco 2.

### 4.3 Ingestão e Fluxo de Dados

```text
gis/kml_parser.py
  -> KMLPoint
  -> GeographicPosition
  -> gis/distance_matrix.py
  -> propagation/link_directivity.py quando orientação for necessária
```

### 4.4 Restrições Arquiteturais

- `models/` não importa `gis/`, `propagation/`, `antenna/` ou UI.
- Validadores de latitude e longitude devem rejeitar valores fora de WGS84.
- `GeographicPosition` não executa cálculo geodésico; cálculo pertence a `gis/geodesic.py`.

---

## 5. Bloco `antenna/`

### 5.1 Propósito e Escopo

`src/lora_antenna/antenna/` modela antenas e suas propriedades RF. O bloco representa características físicas e eletromagnéticas de antenas, sem conhecer topologia de rede, mapas, KML ou sessão.

### 5.2 Módulos e Classes Principais

`base.py`:

- `Antenna`
- `AntennaType`
- `RadiationPattern`
- `AntennaValidationError`

`monopole.py`:

- `Monopole`
- cálculo de comprimento `lambda/4`
- ganho típico e impedância simplificada

`dipole.py`:

- `Dipole`
- `DipoleEnvironment`
- cálculo de comprimento `lambda/2`

`ground_plane.py`:

- `GroundPlane`
- `GroundPlaneConfiguration`
- plano de terra e radiais

`patch.py`:

- `Patch`
- `PatchSubstrate`
- dimensões de patch retangular

`yagi.py`:

- `Yagi`
- `YagiConfiguration`
- elementos, boom, diretor/refletor e ganho aproximado

`reflector.py`:

- `ReflectorAntenna`
- `ParabolicReflector`
- `OffsetReflector`
- ganho por abertura e beamwidth

`feeds.py`:

- `FeedSpecification`
- `FeedType`
- eficiência de iluminação

`factory.py`:

- `build_antenna(antenna_type: str, frequency_hz: float, **kwargs) -> Antenna`
- cria antenas validadas para UI e batch.

### 5.3 Ingestão e Fluxo de Dados

```text
UI ou batch seleciona tipo de antena
  -> antenna/factory.py
  -> classe especializada
  -> valida frequência via core.validators
  -> fornece gain_dbi, geometry e pattern para propagation/
```

### 5.4 Restrições Arquiteturais

- `antenna/` não importa `gis/`, `pages/`, `reports/` ou `persistence/`.
- Antena não conhece latitude, longitude, campus ou KML.
- Antenas devem aceitar somente frequências válidas para o projeto; `~~433 MHz~~ (Fora da faixa definida pela ANATEL)` e `~~868 MHz~~ (Fora da faixa definida pela ANATEL)` não são opções operacionais do V1 Brasil.
- Serialização deve ser Pydantic/JSON compatível para uso em sessão e relatórios.

---

## 6. Bloco `propagation/`

### 6.1 Propósito e Escopo

`src/lora_antenna/propagation/` calcula perdas, potência recebida, margem de enlace, diretividade e efeitos de obstáculos. O bloco opera sobre distâncias em metros e parâmetros RF. Ele não sabe como a distância foi obtida.

### 6.2 Módulos e Classes Principais

`friis.py`:

- `fspl_db(distance_m: float, frequency_hz: float) -> float`
- `friis_received_power_dbm(tx_power_dbm, tx_gain_dbi, rx_gain_dbi, distance_m, frequency_hz, losses_db) -> float`
- `link_margin_db(received_power_dbm: float, rx_sensitivity_dbm: float) -> float`

`link_budget.py`:

- `LinkBudget`
- `LinkBudgetResult`
- cálculo simples ponto a ponto.

`link_directivity.py`:

- `LinkWithDirectivity`
- importa `GeographicPosition` de `lora_antenna.models.geo`
- calcula off-axis e redução de ganho para antenas diretivas.

`obstacles.py`:

- `ObstacleType`
- `ObstacleLossTable`
- perdas por material para `915 MHz`.

`sensitivity.py`:

- `LoRaSensitivityProfile`
- `SX1276SensitivityTable`
- sensibilidade por SF/BW.

`batch/contracts.py`:

- `LinkPair`
- `LinkBatchRequest`
- `LinkBatchResult`

`batch/executor.py`:

- `execute_link_batch(request: LinkBatchRequest) -> list[LinkBatchResult]`
- executor matemático independente de GIS.

`batch/dataframe_adapter.py`:

- converte resultados para estruturas tabulares consumidas pela UI e relatórios.

### 6.3 Ingestão e Fluxo de Dados

```text
distance_m + antenna + RF params
  -> propagation/friis.py
  -> propagation/link_budget.py
  -> propagation/batch/executor.py
  -> LinkBatchResult[]
```

Para fluxo GIS:

```text
gis/multi_link.py monta LinkBatchRequest
  -> propagation/batch/executor.py
  -> LinkBatchResult[]
  -> gis/map_renderer.py e reports/
```

### 6.4 Restrições Arquiteturais

- `propagation/` não importa `gis/`.
- `propagation/` não importa `streamlit`, `folium`, `contextily`, `geopandas` ou parsers XML.
- `LinkBatchRequest` recebe distâncias já calculadas; não calcula latitude/longitude.
- `LinkWithDirectivity` pode usar `GeographicPosition`, mas apenas como contrato neutro.
- `obstacles.py` deve manter tabelas oficiais em `915 MHz`; dados `~~433~~ (Fora da faixa definida pela ANATEL)` e `~~868~~ (Fora da faixa definida pela ANATEL)` devem permanecer marcados como fora da faixa quando aparecerem em documentação histórica.

---

## 7. Bloco `rf_chain/`

### 7.1 Propósito e Escopo

`src/lora_antenna/rf_chain/` modela cadeia transmissora e receptora: potência base, PA, filtros, cabos, conectores, LNA, ruído e sensibilidade efetiva. O bloco é reutilizado pelo link budget simples e batch.

### 7.2 Módulos e Classes Principais

`chain.py`:

- `TxChain`
- `RxChain`
- `LinkBudgetComplete`
- cálculo de EIRP e sensibilidade efetiva.

`cables.py`:

- `CableType`
- `CableLossModel`
- perdas em dB por comprimento e frequência `915 MHz`.

`filters.py`:

- `FilterSpec`
- `BandPassFilter`
- perda de inserção e rejeição fora de banda.

`devices.py`:

- `RadioDevice`
- `SX1276`
- perfis de rádio e limites operacionais.

### 7.3 Ingestão e Fluxo de Dados

```text
UI ou batch informa TX/RX config
  -> rf_chain/chain.py
  -> eirp_dbm e effective_sensitivity_dbm
  -> propagation/link_budget.py
```

### 7.4 Restrições Arquiteturais

- `rf_chain/` não conhece coordenadas nem arquivos.
- Cabos e filtros podem depender de frequência, mas devem validar `915-928 MHz`.
- O bloco retorna componentes de perda/ganho, não renderiza gráficos.

---

## 8. Bloco `gis/`

### 8.1 Propósito e Escopo

`src/lora_antenna/gis/` é a camada geográfica do Bloco 2. Ela ingere KML/shapefile, valida coordenadas, calcula distâncias geodésicas, constrói contexto de campus e traduz os dados geográficos para requisições batch de link budget.

### 8.2 Módulos e Classes Principais

`kml_parser.py`:

- `KMLPoint`
- `KMLDocument`
- `parse_kml(kml_bytes: bytes) -> KMLDocument`
- valida placemarks, labels únicos, latitude/longitude e altitude opcional.

`shapefile_handler.py`:

- `ShapefileDocument`
- `CampusBoundary`
- `load_shapefile(path_or_bytes) -> ShapefileDocument`
- suporte posterior ao MVP; não substitui KML P1-P8.

`geodesic.py`:

- `geodesic_distance_m(a: GeographicPosition, b: GeographicPosition) -> float`
- `bearing_deg(a, b) -> float`
- encapsula `pyproj.Geod` ou fallback Haversine.

`distance_matrix.py`:

- `DistanceMatrix`
- `DistanceMatrixEntry`
- `compute_distance_matrix(points: list[GeographicPosition]) -> DistanceMatrix`
- `validate_against_reference(computed, reference, tolerance_m)`.

`multi_link.py`:

- `build_link_pairs(kml_doc, distance_matrix, antenna_template, antenna_map=None)`.
- `build_link_batch_request(...) -> LinkBatchRequest`.
- `run_geographic_batch(...) -> list[LinkBatchResult]`.

`campus_context.py`:

- `GeographicSessionContext`
- `CampusScenario`
- `UploadMetadata`
- armazena CRS, bounds, warnings, quantidade de pontos, hash e versão de schema.

`heatmap.py`:

- `CoverageGrid`
- `CoveragePoint`
- `compute_coverage_grid(...)`
- extensão para grade 5-50m.

`map_renderer.py`:

- `build_kml_link_map(kml_doc, results)`.
- `build_heatmap_layer(grid)`.
- `style_link_by_margin(result)`.
- não calcula RF; apenas representa.

`reference_tables.py`:

- `REFERENCE_TABLE_P1P8`
- distâncias de referência para validação de regressão.

### 8.3 Ingestão e Fluxo de Dados

```text
bytes KML
  -> kml_parser.parse_kml
  -> KMLDocument
  -> GeographicPosition[]
  -> distance_matrix.compute_distance_matrix
  -> DistanceMatrix
  -> multi_link.build_link_batch_request
  -> propagation.batch.executor
  -> LinkBatchResult[]
  -> map_renderer e reports
```

### 8.4 Restrições Arquiteturais

- `gis/` pode importar `core/`, `models/`, `antenna/`, `propagation/` e `rf_chain/`.
- `gis/` não altera classes do Bloco 1; ele compõe objetos existentes.
- `kml_parser.py` não calcula Friis.
- `distance_matrix.py` não conhece antenas.
- `multi_link.py` é a única ponte entre dados geográficos e batch RF.
- `map_renderer.py` não deve ser usado por `propagation/` ou `core/`.
- KML com menos de dois pontos deve falhar com erro amigável.
- KML com labels duplicados deve falhar antes de calcular matriz.
- KML com mais de 50 pontos deve gerar warning de performance.

---

## 9. Bloco `pages/`

### 9.1 Propósito e Escopo

`src/lora_antenna/pages/` contém páginas Streamlit. A UI orquestra entrada do usuário, estado de sessão, comandos e renderização, mas não deve conter fórmulas RF, parsing KML ou cálculo geodésico.

### 9.2 Módulos e Classes Principais

`antenna_builder.py`:

- seleção de antena
- edição de parâmetros
- visualização de dimensões
- export/import JSON.

`link_budget.py`:

- calculadora standalone ponto a ponto
- modo Friis, diretividade e RF chain completa.

`campus_coverage.py`:

- upload KML
- seleção de antena padrão ou `antenna_map`
- seleção de pares ou matriz completa
- execução batch
- mapa e tabela.

`reports.py`:

- pré-visualização e download de relatórios.

### 9.3 Ingestão e Fluxo de Dados

```text
Usuário faz upload KML
  -> pages/campus_coverage.py lê bytes
  -> gis/kml_parser.py
  -> st.session_state["kml_document"]
  -> botão de cálculo
  -> gis/multi_link.py
  -> st.session_state["link_results"]
  -> ui/tables.py + gis/map_renderer.py
```

### 9.4 Restrições Arquiteturais

- UI não implementa Haversine, Friis ou parser XML.
- UI reseta resultados quando parâmetros mudam.
- UI exibe warnings de ANATEL, KML inválido e divergência de referência.
- UI não persiste KML sem schema versionado.
- UI não deve criar dependência circular com `gis/`; helpers visuais vivem em `ui/` ou `gis/map_renderer.py`.

---

## 10. Bloco `reports/`

### 10.1 Propósito e Escopo

`src/lora_antenna/reports/` transforma resultados de simulação em documentação exportável. Ele recebe dados já calculados e não executa simulação RF.

### 10.2 Módulos e Classes Principais

`markdown_report.py`:

- `generate_kml_batch_report(context, request, results) -> str`
- inclui parâmetros, matriz, resultados, limitações e faixa ANATEL.

`tables.py`:

- `distance_matrix_to_markdown(matrix) -> str`
- `link_results_to_markdown(results) -> str`

`figures.py`:

- exportação de gráficos e mapas para anexos.

`export.py`:

- `export_markdown`
- `export_pdf`
- `export_zip_bundle`

### 10.3 Ingestão e Fluxo de Dados

```text
GeographicSessionContext + LinkBatchRequest + LinkBatchResult[]
  -> reports/tables.py
  -> reports/markdown_report.py
  -> export.py
```

### 10.4 Restrições Arquiteturais

- `reports/` não recalcula distância nem link budget.
- Relatórios devem registrar `915-928 MHz` como restrição regulatória.
- Relatórios devem incluir limitações: modelo simplificado, ausência de multipercurso detalhado e dependência da precisão do KML.

---

## 11. Bloco `persistence/`

### 11.1 Propósito e Escopo

`src/lora_antenna/persistence/` versiona salvamento de cenários, uploads e resultados. V1 pode operar sem banco persistente, mas qualquer persistência deve respeitar schema explícito.

### 11.2 Módulos e Classes Principais

`schemas.py`:

- `kml_imports`
- `coverage_runs`
- `antenna_configs`
- `link_batch_results`

`repositories.py`:

- `KMLImportRepository`
- `CoverageRunRepository`
- `AntennaConfigRepository`

`migrations/001_initial.sql`:

- cria tabelas versionadas.

### 11.3 Ingestão e Fluxo de Dados

```text
KMLDocument + GeographicSessionContext
  -> persistence/repositories.py
  -> kml_imports

LinkBatchRequest + LinkBatchResult[]
  -> coverage_runs + link_batch_results
```

### 11.4 Restrições Arquiteturais

- KML importado não deve ser gravado junto de `coverage_runs` sem chave estrangeira e versão.
- Dados binários originais devem ser opcionais; hash e metadados são obrigatórios.
- Persistência não deve ser dependência obrigatória para testes unitários.

---

## 12. Contratos de Dados V1

### 12.1 `KMLPoint`

Responsabilidade: representar um ponto de interesse extraído do KML.

Campos:

- `label: str`
- `latitude: float`
- `longitude: float`
- `altitude_m: float = 0.0`
- `description: str | None = None`
- `source_index: int`

Validações:

- latitude entre `-90` e `90`.
- longitude entre `-180` e `180`.
- label não vazio.

### 12.2 `KMLDocument`

Responsabilidade: representar documento KML validado.

Campos:

- `schema_version: str = "1.0"`
- `name: str`
- `points: list[KMLPoint]`
- `warnings: list[str] = []`

Regras:

- mínimo de dois pontos.
- labels únicos.
- ordem dos pontos preservada para matriz triangular.

### 12.3 `DistanceMatrix`

Responsabilidade: armazenar distâncias entre pares.

Estrutura:

```text
entries:
  - origin_label
  - dest_label
  - distance_m
  - method = "WGS84_GEODESIC"
  - delta_reference_m opcional
```

Regras:

- Para N pontos, matriz completa triangular deve conter `N*(N-1)/2` entradas.
- Distância deve ser positiva.
- Pares devem ser ordenados pela ordem de `KMLDocument.points`.

### 12.4 `LinkBatchRequest`

Responsabilidade: transportar simulação multiponto para o executor RF.

Campos:

- `pairs: list[LinkPair]`
- `frequency_hz: float = 915e6`
- `tx_power_dbm: float = 14.0`
- `rx_sensitivity_dbm: float = -137.0`
- `extra_losses_db: float = 0.0`
- `tx_chain: TxChain | None`
- `rx_chain: RxChain | None`
- `metadata: SimulationMetadata`

Regras:

- frequência deve estar entre `915e6` e `928e6`.
- `pairs` não pode ser vazio.
- `distance_m` já deve estar calculada.

### 12.5 `LinkBatchResult`

Responsabilidade: resultado unitário de um par.

Campos:

- `origin_label: str`
- `dest_label: str`
- `distance_m: float`
- `fspl_db: float`
- `received_power_dbm: float`
- `link_margin_db: float`
- `feasible: bool`
- `warnings: list[str]`

Regras:

- `feasible = link_margin_db > 0`.
- arredondamento de apresentação pertence à UI; resultado interno pode manter precisão.

---

## 13. Fluxo End-to-End V1

```text
1. Usuário abre pages/campus_coverage.py
2. Usuário carrega campus_p1_p8.kml
3. UI lê bytes e chama gis/kml_parser.py
4. Parser retorna KMLDocument validado
5. UI grava kml_document e geo_context em st.session_state
6. distance_matrix.compute_distance_matrix calcula 28 pares para P1-P8
7. UI apresenta tabela de distâncias e opções de pares
8. Usuário escolhe antena, potência, sensibilidade e perdas
9. gis/multi_link.py cria LinkBatchRequest
10. propagation/batch/executor.py calcula FSPL, potência recebida e margem
11. UI grava link_results em st.session_state
12. gis/map_renderer.py renderiza mapa com marcadores e enlaces
13. ui/tables.py renderiza tabela de resultados
14. reports/markdown_report.py gera relatório técnico exportável
```

---

## 14. Estratégia de Testes

### 14.1 Unit Tests

`tests/unit/` cobre fórmulas, antenas, RF chain e propagação sem GIS.

Obrigatórios:

- `test_core_formulas.py`: comprimento de onda e conversões.
- `test_friis.py`: FSPL 1 km @ 915 MHz.
- `test_link_budget.py`: potência recebida e margem.
- `test_antenna_*`: dimensões e serialização de antenas.
- `test_rf_chain.py`: EIRP e sensibilidade efetiva.

### 14.2 GIS Tests

`tests/gis/` cobre parsing, coordenadas e matriz.

Obrigatórios:

- `test_kml_parser.py`: extrai P1-P8, valida labels, rejeita KML vazio e duplicado.
- `test_geodesic.py`: distância P1-P2 aproximada.
- `test_distance_matrix.py`: 8 pontos geram 28 pares.
- `test_multi_link.py`: batch cria resultados para todos os pares.
- `test_map_renderer_contracts.py`: renderer aceita resultados sem recalcular RF.

### 14.3 Integration Tests

`tests/integration/` cobre fluxo completo sem abrir UI real.

Obrigatórios:

- `test_kml_to_distance_matrix.py`
- `test_kml_to_batch_link_budget.py`
- `test_campus_coverage_session_state.py`
- `test_report_from_batch_results.py`

### 14.4 E2E Tests

`tests/e2e/` cobre a experiência Streamlit.

Obrigatórios:

- upload KML válido.
- warning para KML inválido.
- cálculo batch completo.
- tabela com 28 resultados.
- download de relatório.

---

## 15. Gates de Aceite V1

### Gate V1-A: Bloco 1 preservado

- [ ] Nenhum arquivo em `core/`, `antenna/`, `propagation/` ou `rf_chain/` importa `gis/`.
- [ ] Fórmulas e classes de antena continuam passando testes existentes.
- [ ] `GeographicPosition` está em `models/geo.py`.

### Gate V1-B: KML/GIS

- [ ] `campus_p1_p8.kml` carrega com oito pontos.
- [ ] Labels P1-P8 preservados.
- [ ] Matriz gera 28 pares.
- [ ] Distâncias positivas e coerentes com referência.

### Gate V1-C: Batch RF

- [ ] `LinkBatchRequest` valida frequência `915e6`.
- [ ] Executor batch calcula todos os pares.
- [ ] Resultados incluem FSPL, potência recebida, margem e status.

### Gate V1-D: UI e Sessão

- [ ] Novo upload reseta resultados antigos.
- [ ] Mudança de antena reseta batch.
- [ ] UI não implementa regras matemáticas.
- [ ] Warnings regulatórios aparecem quando aplicável.

### Gate V1-E: Relatórios

- [ ] Relatório inclui matriz de distâncias.
- [ ] Relatório inclui tabela de link budgets.
- [ ] Relatório cita faixa ANATEL `915-928 MHz`.
- [ ] Relatório lista limitações do modelo.

---

## 16. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Dependência circular entre `gis/` e `propagation/` | Alto | `GeographicPosition` em `models/geo.py`; `propagation/` nunca importa `gis/`. |
| Parser KML frágil para namespaces variados | Médio | Usar parser com namespace dinâmico e fixtures reais. |
| UI mantendo resultado antigo após troca de arquivo | Médio | Centralizar reset em `ui/state.py`. |
| Uso acidental de `~~433 MHz~~ (Fora da faixa definida pela ANATEL)` / `~~868 MHz~~ (Fora da faixa definida pela ANATEL)` | Crítico | Validação em `core.validators` e documentação ANATEL. |
| Performance com muitos pontos | Médio | Warning acima de 50 pontos; background job em versão futura. |
| Misturar DataFrame com domínio | Médio | DataFrame apenas em `ui/` e `reports/`; domínio usa Pydantic/dataclass. |

---

## 17. Decisões Normativas

1. KML é entrada primária do Bloco V1 para pontos P1-P8.
2. Shapefile é suporte secundário e não bloqueia o MVP V1.
3. O Bloco 1 permanece matemático e sem dependência geográfica.
4. Batch é contrato oficial, não adaptação temporária da UI.
5. `DistanceMatrix` é calculada antes do link budget.
6. `LinkBatchRequest` é a fronteira entre Bloco 2 e executor RF.
7. `915e6 Hz` é default operacional; `~~433 MHz~~ (Fora da faixa definida pela ANATEL)` e `~~868 MHz~~ (Fora da faixa definida pela ANATEL)` não são frequências válidas para LoRa Brasil neste projeto.
8. UI não contém lógica de domínio.
9. Relatórios não recalculam simulação.
10. Persistência de KML exige schema versionado.

---

## 18. Critério de Pronto para Implementação

A implementação do Bloco V1 pode iniciar quando:

- Este documento estiver versionado em `_doc/architecture/`.
- `Implementation-roadmap.md` e `parts/sprint/SPRINT-8.md` refletirem a integração KML/GIS.
- A equipe aceitar a fronteira de dependências Bloco 1/Bloco 2.
- Fixtures KML reais ou aproximadas estiverem disponíveis em `tests/fixtures/`.
- Testes de regressão do Bloco 1 estiverem verdes antes de iniciar o Bloco 2.

---

## 19. Resultado Esperado do Bloco V1

Ao final do Bloco V1, a plataforma deve permitir:

- construir ou selecionar antenas LoRa em `915 MHz`;
- carregar um KML com pontos P1-P8;
- calcular automaticamente todas as distâncias entre pontos;
- executar link budget batch para todos os pares ou pares selecionados;
- visualizar mapa com enlaces viáveis e inviáveis;
- consultar tabela técnica com distância, FSPL, potência recebida e margem;
- exportar relatório com parâmetros, resultados e limitações;
- manter a separação estrita entre motor matemático e camada geográfica.

