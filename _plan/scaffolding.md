# Scaffolding do Projeto LoRa Antenna Platform

## Premissa

Aplicacao cientifica em Python 3.11/3.12 para projeto, analise e simulacao de antenas e enlaces LoRa/LoRaWAN. Interface em Streamlit, graficos em Plotly, mapas com Folium/GeoPandas, persistencia em JSON/SQLite/Pydantic, empacotamento com `uv`, Docker e porta LAN `3953`.

O MVP deve ser educacional e de estimativa de engenharia. Nao deve fingir simulacao eletromagnetica completa. Toda aproximacao fisica precisa aparecer em docs, UI e testes.

## Objetivo do Scaffold

Criar base de projeto que permita evoluir em checkpoints:

- nucleo matematico validado;
- objeto `Antenna` serializavel;
- tipos de antena comuns em LoRa;
- enlaces com Friis, diretividade e cadeia TX/RX;
- visualizacoes 2D/3D;
- mapas de cobertura;
- relatorios tecnicos;
- deploy em LAN.

## Estrutura Recomendada

```text
.
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
├── README.md
├── docs/
│   ├── architecture.md
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
│   └── references.md
├── src/
│   └── lora_antenna/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── constants.py
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
│       ├── rf_chain/
│       │   ├── __init__.py
│       │   ├── cables.py
│       │   ├── components.py
│       │   └── chain.py
│       ├── propagation/
│       │   ├── __init__.py
│       │   ├── friis.py
│       │   ├── link_budget.py
│       │   ├── link_directivity.py
│       │   ├── obstacles.py
│       │   └── fresnel.py
│       ├── patterns/
│       │   ├── __init__.py
│       │   └── radiation.py
│       ├── persistence/
│       │   ├── __init__.py
│       │   ├── schemas.py
│       │   ├── json_store.py
│       │   └── sqlite_store.py
│       ├── geo/
│       │   ├── __init__.py
│       │   ├── grid.py
│       │   ├── coverage.py
│       │   └── layers.py
│       ├── reports/
│       │   ├── __init__.py
│       │   └── markdown.py
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

## Dependencias Base

```toml
[project]
requires-python = ">=3.11,<3.13"
dependencies = [
  "streamlit",
  "pydantic>=2",
  "numpy",
  "pandas",
  "plotly",
  "folium",
  "streamlit-folium",
  "geopandas",
  "shapely",
  "pyproj",
]

[dependency-groups]
dev = [
  "pytest",
  "ruff",
  "mypy",
]
```

## Nucleo Cientifico

### `constants.py`

Responsavel por constantes fisicas e bandas LoRa:

- `C_M_PER_S = 299_792_458`;
- frequencias padrao: 433, 868, 915 MHz;
- impedancia de referencia `Z0_OHM = 50`;
- sensibilidades SX1276 por SF/BW.

### `antenna/base.py`

Modelo Pydantic central:

- `id`;
- `name`;
- `antenna_type`;
- `frequency_hz`;
- `gain_dbi`;
- `impedance_ohm` como par real/imag ou tipo serializavel;
- `vswr`;
- `efficiency`;
- `polarization`;
- `effective_area_m2`;
- `orientation_azimuth_deg`;
- `orientation_elevation_deg`;
- `location`;
- `schema_version`;
- `created_at`;
- `updated_at`;
- `notes`.

Critico: `radiation_pattern` deve ser estrutura serializavel, por exemplo `dict[str, list[float]]`, nao objeto Python solto.

## Tipos de Antena

### Monopole

- comprimento: `lambda / 4`;
- ganho nominal: ~2.15 dBi;
- impedancia aproximada ressonante;
- padrao hemisferico simplificado;
- disclaimer de plano de terra e ambiente.

### Dipole

- comprimento: `lambda / 2`;
- ganho nominal: 2.15 dBi;
- ambiente parametrizado:
  - `free_space`;
  - `above_ground`;
  - `near_structure`;
  - `cavity`.
- impedancia ajustada por ambiente;
- VSWR calculado contra 50 ohm.

### Ground Plane

- monopolo `lambda / 4`;
- plano parametrizado por forma e tamanho em lambdas;
- impedancia nao fixa em 50 ohm;
- default recomendado: plano quadrado `2 lambda x 2 lambda`, Z ~45 ohm;
- warning forte quando plano `< 1 lambda`.

### Patch

- substrato obrigatorio;
- defaults: FR4, Rogers 4003, Rogers 5880, Duroid;
- dimensoes por formulas aproximadas de Pozar;
- ganho estimado por substrato;
- UI deve mostrar que feed e substrato dominam o resultado.

### Yagi

- configuracoes: 3, 5, 7, 10 elementos;
- ganho empirico por numero de diretores;
- beamwidth aproximado;
- orientacao obrigatoria quando usada em link diretivo;
- padrao de radiacao simplificado com aviso.

### ReflectorAntenna

Substitui uma classe vaga `Parabola`. Parabolica e um tipo de antena refletora.

Tipos:

- `parabolic_circular`;
- `parabolic_offset`;
- `cassegrain`;
- `gregorian`;
- `cylindrical`;
- `ellipsoidal`.

Para MVP LoRa, priorizar:

- `parabolic_circular`;
- `parabolic_offset`.

Campos minimos:

- `reflector_type`;
- `primary_diameter_m`;
- `focal_ratio`;
- `focal_length_m`;
- `efficiency_aperture`;
- `feed_specification`;
- `beamwidth_3db_deg`;
- `gain_dbi`.

Formulas:

- `G = eta_total * (pi * D / lambda)^2`;
- `HPBW ~= 1.22 * lambda / D`;
- `eta_total = eta_aperture * eta_feed`.

## Alimentadores

### `antenna/feeds.py`

Criar `FeedType`:

- `horn_pyramidal`;
- `horn_conical_corrugated`;
- `horn_exponential`;
- `dipole`;
- `patch`;
- `helical`;
- `probe`.

Criar `FeedSpecification`:

- `feed_type`;
- `gain_dbi`;
- `efficiency`;
- `beamwidth_deg`;
- `impedance_ohm`;
- `return_loss_db`;
- `polarization`;
- `operating_bandwidth_mhz`;
- `feeding_method`;
- `feeding_loss_db`.

Tabela inicial:

| Feed | Eficiencia | Beamwidth | Uso |
|---|---:|---:|---|
| Dipole | 0.40 | 170 deg | prototipo caseiro |
| Probe | 0.45 | 160 deg | prototipo |
| Patch | 0.60 | 120 deg | semi-profissional |
| Horn pyramidal | 0.75 | 100 deg | bom default |
| Horn exponential | 0.78 | 95 deg | profissional |
| Horn conical corrugated | 0.82 | 95 deg | melhor default tecnico |

Critico: ganho de refletora deve depender do feed. Nao usar eficiencia global opaca.

## Formulas Fundamentais

Implementar e testar:

- `wavelength_m(frequency_hz)`;
- `effective_area_m2(gain_dbi, wavelength_m)`;
- `reflection_coefficient(z_load, z0)`;
- `vswr(z_load, z0)`;
- `return_loss_db(gamma)`;
- `eirp_dbm(tx_power_dbm, antenna_gain_dbi, losses_db)`;
- `fspl_db(distance_m, frequency_hz)`;
- `friis_received_power_dbm(tx_power_dbm, tx_gain_dbi, rx_gain_dbi, fspl_db, losses_db)`;
- `link_margin_db(received_power_dbm, sensitivity_dbm)`.

Casos conhecidos:

- `lambda @ 915 MHz ~= 0.3276 m`;
- dipolo `lambda/2 @ 915 MHz ~= 0.1638 m`;
- `FSPL @ 1 km, 915 MHz ~= 91.67 dB`;
- enlace: `14 dBm + 2.15 + 2.15 - 91.67 ~= -73.37 dBm`.

## Propagacao

### Friis

`propagation/friis.py` deve conter funcoes puras. `propagation/link_budget.py` deve conter modelos compostos.

Regra: FSPL e intermediario. Potencia recebida sempre usa Friis completo:

```text
Pr(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - FSPL(dB) - perdas(dB)
```

### Obstaculos

`propagation/obstacles.py`:

- `ObstacleType`;
- tabela por frequencia 433/868/915 MHz;
- min/nominal/max;
- interpolacao linear;
- fontes documentadas em `docs/propagation_model.md`.

Tipos iniciais:

- parede de tijolo;
- parede de concreto;
- vidro;
- vegetacao densa;
- vegetacao esparsa;
- edificio concreto;
- edificio alvenaria.

### Diretividade

`propagation/link_directivity.py`:

- `GeographicPosition`;
- angulo TX -> RX;
- angulo RX -> TX;
- fator de ganho direcional por antena;
- Yagi: modelo `cos^n`;
- refletora: modelo mais estreito, com lobulos laterais aproximados;
- comparar `received_power_dbm_ideal` vs `received_power_dbm_with_directivity`.

Regra: omnidirecionais nao sofrem perda por orientacao. Diretivas exigem azimute/elevacao.

### Fresnel

`propagation/fresnel.py` deve entrar como skeleton no MVP:

- raio da zona de Fresnel;
- percentual de bloqueio;
- warning;
- perda real fica para fase posterior se nao houver DEM.

## Cadeia RF TX/RX

### `rf_chain/components.py`

Modelar componentes:

- PA;
- LNA;
- filtro TX;
- filtro RX;
- circulador/diplexador;
- conector;
- balun/acoplador.

### `rf_chain/cables.py`

Tabela automatica de perdas:

| Cabo | Perda @ 915 MHz |
|---|---:|
| RG-58 | ~6 dB/100m |
| RG-8 | ~2.5 dB/100m |
| RG-214 | ~2 dB/100m |
| LMR-400 | ~1.8 dB/100m |
| Waveguide | ~0.05 dB/m |

### `rf_chain/chain.py`

Criar `TxChain`, `RxChain` e `LinkBudgetComplete`.

TX:

- potencia SX1276/base;
- ganho PA;
- perda filtro;
- perda circulador;
- perda cabo;
- perda conectores;
- potencia na antena.

RX:

- potencia na antena;
- perda filtro;
- perda circulador;
- perda cabo;
- perda conectores;
- ganho LNA;
- figura de ruido;
- potencia antes do chip.

Default conservador:

- sem PA: `0 dB`;
- sem LNA em modo simples: `0 dB`;
- modo gateway profissional: PA/LNA presets.

## Persistencia

### JSON

Salvar:

- antenas;
- feeds;
- links;
- simulacoes de cobertura;
- versao de schema.

### SQLite

Tabelas sugeridas:

- `antennas`;
- `feeds`;
- `links`;
- `coverage_runs`;
- `reports`.

Pydantic faz validacao e migracao leve por `schema_version`.

## Interface Streamlit

Primeira tela deve ser ferramenta, nao landing page.

Paginas:

- `Antena`;
- `Enlace`;
- `Diretividade`;
- `Cobertura`;
- `Biblioteca`;
- `Relatorios`;
- `Limitacoes`.

### Antena

Controles:

- frequencia: 433/868/915/custom;
- tipo de antena;
- parametros geometricos;
- feed se refletora;
- substrato se patch;
- orientacao se diretiva;
- resultados calculados;
- graficos 2D/3D.

### Enlace

Controles:

- antena TX;
- antena RX;
- distancia;
- potencia TX;
- SF/BW/sensibilidade;
- cadeia TX/RX simples ou completa;
- perdas por obstaculos;
- resultado: FSPL, Pr, margem, status.

### Diretividade

Mostrar:

- direcao alvo;
- azimute/elevacao de cada antena;
- perda por desalinhamento;
- Friis ideal vs Friis com diretividade.

### Cobertura

MVP:

- area de interesse;
- grade ajustavel 5-50 m;
- default 10 ou 20 m;
- heatmap por potencia recebida;
- warning: modelo simplificado, sem DEM/multipercurso completo.

### Relatorios

Gerar Markdown com:

- parametros de antenas;
- formulas usadas;
- tabelas de link budget;
- figuras exportadas;
- limitacoes do modelo.

## Documentacao Obrigatoria Antes do Codigo Pesado

Checkpoint 0.5:

- `docs/formulas.md`;
- `docs/antenna_details.md`;
- `docs/propagation_model.md`;
- `docs/assumptions.md`;
- `docs/limitations.md`;
- `docs/validation.md`;
- `docs/references.md`;
- `tests/validation_matrix.md`.

Novos docs vindos das analises rise:

- `docs/antenna_types_complete.md`;
- `docs/feed_specifications.md`;
- `docs/tx_rx_chain_analysis.md`;
- `docs/accuracy_matrix.md`;
- `docs/real_vs_theoretical.md`.

## Testes

Prioridade:

1. formulas puras;
2. antenas individuais;
3. refletoras + feeds;
4. Friis e margem;
5. obstaculos;
6. diretividade;
7. cadeia RF;
8. persistencia.

Cada teste deve ter:

- entrada numerica conhecida;
- resultado esperado;
- tolerancia;
- fonte em comentario ou doc.

## Roadmap de Checkpoints

### Checkpoint 0.5: Documentacao

Entregas:

- docs tecnicos base;
- matriz de validacao;
- lista explicita de limitacoes.

Aceite:

- formulas e premissas revisadas;
- lacunas conhecidas documentadas;
- nenhum codigo fisico sem teste planejado.

### Checkpoint 0: Infra

Entregas:

- `uv`;
- `pyproject.toml`;
- Streamlit minimo;
- Docker/Docker Compose;
- porta `3953`.

Aceite:

- `uv run streamlit run src/lora_antenna/app.py --server.port 3953`;
- app abre em LAN.

### Checkpoint 1: Formulas

Entregas:

- funcoes matematicas puras;
- testes de casos conhecidos.

Aceite:

- `pytest tests/test_formulas.py`;
- valores 915 MHz batem tolerancia.

### Checkpoint 2-3: Antenas

Entregas:

- `Antenna`;
- Monopole, Dipole, GroundPlane, Patch, Yagi;
- ReflectorAntenna;
- FeedSpecification.

Aceite:

- instanciar, serializar e comparar antenas;
- ganhos e dimensoes dentro de faixas esperadas;
- warnings por modelo simplificado.

### Checkpoint 4: Standalone UI

Entregas:

- criar antena;
- exibir parametros;
- plotar padrao;
- salvar/carregar.

Aceite:

- usuario cria antena 915 MHz e exporta JSON.

### Checkpoint 5-6: Link

Entregas:

- Friis completo;
- LinkBudget;
- LinkWithDirectivity;
- LinkBudgetComplete;
- obstaculos.

Aceite:

- FSPL 1 km @ 915 MHz ~91.67 dB;
- enlace conhecido retorna Pr ~-73.37 dBm;
- Yagi desalinhada perde >10 dB em 90 graus;
- cadeia TX/RX mostra perdas passo a passo.

### Checkpoint 7: Visualizacoes

Entregas:

- graficos polares;
- padrao 3D simplificado;
- comparacoes potencia vs distancia;
- UI de warnings.

Aceite:

- graficos nao ocultam limitacoes;
- diretivas mostram impacto de orientacao.

### Checkpoint 8: GIS/Cobertura

Entregas:

- grade espacial;
- mapa Folium;
- heatmap de potencia/margem;
- importacao de shapefiles.

Aceite:

- cobertura roda em area pequena;
- resolucao configuravel;
- aviso claro sobre terra plana/sem DEM se aplicavel.

### Checkpoint 9: Relatorios

Entregas:

- relatorio Markdown;
- tabelas e parametros;
- referencias e limitacoes.

Aceite:

- relatorio reproduz calculo.

### Checkpoint 10: Deploy

Entregas:

- Docker;
- Compose;
- README operacional;
- testes principais.

Aceite:

- app acessivel em `http://IP_DO_SERVIDOR:3953`.

## Riscos Tecnicos

| Risco | Mitigacao |
|---|---|
| Usuario confundir modelo didatico com simulacao EM | warnings, docs, limitations |
| Impedancia simplificada demais | parametrizar ambiente/geometria |
| Refletora sem feed realista | `FeedSpecification` obrigatorio |
| Friis superestima cobertura | obstaculos, margem, accuracy matrix |
| Diretivas geram heatmap falso | orientacao explicita e aviso no GIS |
| Cabos/PA/LNA ignorados | `LinkBudgetComplete` |
| Falta DEM/multipercurso | roadmap e disclaimer |

## Definicao de Pronto do MVP

MVP pronto quando:

- cria e salva antenas principais;
- calcula dimensoes, impedancia aproximada, VSWR, ganho e area efetiva;
- calcula enlace com Friis completo;
- suporta ao menos uma refletora parabolica com feed;
- calcula impacto de orientacao para Yagi/refletora;
- modela cadeia TX/RX simples e completa;
- gera graficos e mapa inicial;
- exporta relatorio;
- documenta limitacoes;
- roda via Streamlit/Docker em `3953`;
- testes cobrem casos numericos conhecidos.

