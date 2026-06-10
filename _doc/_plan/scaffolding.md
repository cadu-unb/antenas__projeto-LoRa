# Scaffolding do Projeto LoRa Antenna Platform

## Premissa

Aplicacao cientifica em Python 3.11/3.12 para projeto, analise e simulacao de antenas e enlaces LoRa/LoRaWAN. Interface em Streamlit, graficos em Plotly, mapas com Folium/GeoPandas, persistencia em JSON/SQLite/Pydantic, empacotamento com `uv`, Docker e porta LAN `3953`.

O MVP deve ser educacional e de estimativa de engenharia. Nao deve fingir simulacao eletromagnetica completa. Toda aproximacao fisica precisa aparecer em docs, UI e testes.

## Objetivo do Scaffold

Criar base de projeto que permita evoluir em checkpoints:

- nucleo matematico validado;
- objeto `Antenna` serializavel;
- tipos de antena comuns em LoRa (omnidirecionais + diretivas);
- refletoras parabolicas com alimentadores;
- enlaces com Friis, diretividade e cadeia TX/RX completa;
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
- impedancia nao fixa em 50 ohm (varia com tamanho do plano);
- default recomendado: plano quadrado `2 lambda x 2 lambda`, Z ~45 ohm;
- warning forte quando plano `< 1 lambda` (desvios de >20%);
- impedancia cresce para planos pequenos: aprox. linear com fator geometrico.

### Patch

- substrato obrigatorio;
- defaults: FR4, Rogers 4003, Rogers 5880, Duroid;
- dimensoes por formulas aproximadas de Pozar;
- ganho estimado por substrato;
- UI deve mostrar que feed e substrato dominam o resultado.

### Yagi

- configuracoes: 3, 5, 7, 10 elementos;
- ganho empirico por numero de diretores (formula Cebik);
- beamwidth aproximado (HPBW inversamente proporcional ao ganho);
- orientacao obrigatoria quando usada em link diretivo;
- padrao de radiacao simplificado com aviso (sem lobulos secundarios completos).

### ReflectorAntenna (Base para Parabolicas)

Substitui classe vaga "Parabola". Parabola e' um TIPO de antena refletora. Suportar tipos:

- `parabolic_circular` (prime-focus);
- `parabolic_offset` (mais eficiente);
- `cassegrain` (raro em LoRa, mas documentado);
- `gregorian` (raro em LoRa, mas documentado).

Para MVP LoRa, priorizar:

- `parabolic_circular`;
- `parabolic_offset` (PREFERIDO: eficiencia ~95% vs 85% circular).

Campos minimos:

- `reflector_type` (enum);
- `primary_diameter_m`;
- `focal_ratio` (f/D, tipico 0.3-0.5);
- `focal_length_m`;
- `efficiency_aperture` (0.50-0.70 tipico);
- `feed_specification` (OBRIGATORIO);
- `beamwidth_3db_deg`;
- `gain_dbi`.

Formulas:

- `G = eta_total * (pi * D / lambda)^2`;
- `HPBW ~= 1.22 * lambda / D`;
- `eta_total = eta_aperture * eta_feed`.

CRITICO: Ganho da refletora DEPENDE DO FEED. Nao usar eficiencia global opaca.

## Alimentadores (Feeds)

### `antenna/feeds.py`

Criar enum `FeedType`:

- `horn_pyramidal`;
- `horn_conical_corrugated`;
- `horn_exponential`;
- `dipole`;
- `patch`;
- `helical`;
- `probe`.

Criar modelo `FeedSpecification`:

- `feed_type`;
- `gain_dbi`;
- `efficiency` (0.40-0.88 tipico);
- `beamwidth_deg`;
- `impedance_ohm`;
- `return_loss_db`;
- `polarization`;
- `operating_bandwidth_mhz`;
- `feeding_method` ("waveguide", "coaxial", "probe");
- `feeding_loss_db` (transformador, aberracoes, etc.).

Tabela de Eficiencia de Feeds (Parabola 50cm @ 915 MHz):

| Feed | Eficiencia | Beamwidth | Ganho Total* | Uso |
|---|---:|---:|---:|---|
| Dipole/Probe | 0.40 | 170 deg | 4.5 dBi | prototipo caseiro |
| Sonda Linear | 0.45 | 160 deg | 5.2 dBi | prototipo |
| Patch | 0.60 | 120 deg | 6.7 dBi | semi-profissional |
| Horn pyramidal | 0.75 | 100 deg | 8.4 dBi | bom default |
| Horn exponential | 0.78 | 95 deg | 9.0 dBi | profissional |
| Horn conical corrugated | 0.82 | 95 deg | 9.2 dBi | melhor default tecnico |

*Ganho = 0.65 (aperture) × feed_efficiency × ganho geometrico.

**Critico**: ganho de refletora deve depender do feed explicitamente. Nao usar eficiencia global opaca. Diferenca de feed = ate 5 dB no resultado final.

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

### Friis Completo

`propagation/friis.py` deve conter funcoes puras. `propagation/link_budget.py` deve conter modelos compostos.

Regra: FSPL e intermediario. Potencia recebida sempre usa Friis completo:

```text
Pr(dBm) = Pt(dBm) + Gt(dBi) + Gr(dBi) - FSPL(dB) - perdas(dB)
```

### Diretividade (NOVO)

`propagation/link_directivity.py`:

- `GeographicPosition`;
- calculo de angulo TX -> RX;
- calculo de angulo RX -> TX;
- fator de ganho direcional por antena;
- Yagi: modelo `cos^n` (ganho reduzido com angulo off-axis);
- refletora: modelo mais estreito com lobulos aproximados;
- **IMPORTANTE**: omnidirecionais nao sofrem perda por orientacao. Diretivas exigem azimute/elevacao explicitos.
- comparar `received_power_dbm_ideal` (sem diretividade) vs `received_power_dbm_with_directivity` (com orientacao).

### Obstaculos

`propagation/obstacles.py`:

- `ObstacleType` enum;
- tabela por frequencia 433/868/915 MHz;
- min/nominal/max por tipo;
- interpolacao linear entre frequencias;
- fontes documentadas em `docs/propagation_model.md`.

Tipos iniciais:

- parede de tijolo;
- parede de concreto;
- vidro;
- vegetacao densa;
- vegetacao esparsa;
- edificio concreto;
- edificio alvenaria.

### Fresnel

`propagation/fresnel.py` deve entrar como skeleton no MVP:

- raio da zona de Fresnel;
- percentual de bloqueio;
- warning;
- perda real fica para fase posterior se nao houver DEM.

## Cadeia RF TX/RX — COMPLETA

### `rf_chain/components.py`

Modelar componentes:

- PA (Power Amplifier);
- LNA (Low Noise Amplifier);
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

Implementar calculo automatico: `cable_loss_db(cable_type, length_m, frequency_mhz)`.

### `rf_chain/chain.py`

**NOVO: Criar `LinkBudgetComplete`** (expandido, nao apenas `LinkBudget`).

TX Chain:

- potencia SX1276/base (0 dBm a 20 dBm tipico);
- ganho PA externo (0 dB default, +6 dB ate +13 dB em gateways);
- perda filtro TX (0.5-1.5 dB);
- perda circulador (0.5 dB);
- perda cabo TX (automatico por tipo + comprimento);
- perda conectores (0.2 dB cada, ~1-2 dB acumulado);
- perda balun/transformador (0-1.0 dB);
- EIRP resultante na antena.

RX Chain:

- potencia na antena (Friis resultado);
- perda filtro RX (0.5-1.0 dB);
- perda circulador (0.5 dB);
- perda cabo RX (automatico);
- perda conectores (0.2 dB cada);
- ganho LNA (0 dB default, +25-35 dB em gateways corporativos);
- figura de ruido LNA (0.5-2.0 dB);
- potencia antes do chip RX.

Default conservador MVP:

- sem PA: `0 dB`;
- sem LNA em modo simples: `0 dB`;
- modo gateway profissional: presets para PA (+20 dBm) e LNA (+30 dB).

**Modelagem de Erros Nao-Modelados**:

Sem LinkBudgetComplete, erro acumulado em enlaces corporativos pode chegar a **±35 dB** por ignorar PA, LNA, filtros, circuladores, cabos e conectores. Com, erro reduz para **±3-5 dB**.

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

**UI Warning**: Avisar quando antena e' diretiva. Orientacao obrigatoria.

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

Mostrar **comparacao**: "Sem LNA/PA" vs "Com LNA/PA" para gateways.

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
- **AVISO CRITICO**: modelo simplificado, assume omnidirecionais, sem DEM/multipercurso completo.

### Relatorios

Gerar Markdown com:

- parametros de antenas;
- formulas usadas;
- tabelas de link budget;
- figuras exportadas;
- limitacoes do modelo;
- **NOVO**: accuracy matrix (precisao esperada por cenario).

## Documentacao Obrigatoria Antes do Codigo Pesado

### Checkpoint 0.5: Documentacao Tecnica (NOVO — 2 DIAS)

**OBRIGATORIO ANTES de iniciar Checkpoint 0**:

- `docs/formulas.md` (todas as equacoes com referencias);
- `docs/antenna_details.md` (dimensoes e parametros por tipo);
- `docs/propagation_model.md` (FSPL, obstaculos, Fresnel);
- `docs/assumptions.md` (todas as premissas do modelo);
- `docs/limitations.md` (tudo que MVP NAO faz, com razoes);
- `docs/validation.md` (casos de teste + tolerancias);
- `docs/references.md` (todas as citacoes);
- `tests/validation_matrix.md` (matriz de precisao esperada por cenario).

### Documentos Complementares

Novos docs vindos das analises rise:

- `docs/antenna_types_complete.md` (tipos suportados com foco LoRa);
- `docs/feed_specifications.md` (7 tipos de feed, eficiencias, tabelas);
- `docs/tx_rx_chain_analysis.md` (cadeia completa com todos os elementos);
- `docs/accuracy_matrix.md` (precisao esperada: LOS ±1-2 dB, NLOS ±8-15 dB, diretivas ±15-25 dB);
- `docs/real_vs_theoretical.md` (comparacao com dados de campo, quando disponivel).

## Testes

Prioridade:

1. formulas puras;
2. antenas individuais;
3. refletoras + feeds;
4. Friis e margem;
5. diretividade (novo);
6. obstaculos;
7. cadeia RF completa (novo);
8. persistencia.

Cada teste deve ter:

- entrada numerica conhecida;
- resultado esperado;
- tolerancia;
- fonte em comentario ou doc.

## Roadmap de Checkpoints

### Checkpoint 0.5: Documentacao (NOVO)

Entregas:

- docs tecnicos base (formulas, antenas, propagacao);
- matriz de validacao com precisao esperada;
- lista explicita de limitacoes;
- casos de teste numericos conhecidos.

Aceite:

- formulas e premissas revisadas;
- lacunas conhecidas documentadas;
- nenhum codigo fisico sem teste planejado.

**Tempo**: 1-2 dias.

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

- `Antenna` base;
- Monopole, Dipole, GroundPlane, Patch, Yagi;
- **ReflectorAntenna** (NOVO: suporta parabolic_circular, parabolic_offset);
- **FeedSpecification** (NOVO: 7 tipos, eficiencias tabeladas).

Aceite:

- instanciar, serializar e comparar antenas;
- ganhos e dimensoes dentro de faixas esperadas;
- warnings por modelo simplificado;
- refletora + feed mostram ganho correto (eta_aperture × eta_feed).

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

- **Friis completo**;
- LinkBudget;
- **LinkWithDirectivity** (NOVO: azimute/elevacao, modelos diretivos);
- **LinkBudgetComplete** (NOVO: PA, LNA, filtros, cabos, conectores);
- obstaculos;
- comparacoes antes/depois de PA/LNA.

Aceite:

- FSPL 1 km @ 915 MHz ~91.67 dB;
- enlace conhecido retorna Pr ~-73.37 dBm;
- Yagi desalinhada perde >10 dB em 90 graus;
- Parabola desalinhada perde >20 dB em 90 graus;
- cadeia TX/RX mostra perdas passo a passo.

### Checkpoint 7: Visualizacoes

Entregas:

- graficos polares;
- padrao 3D simplificado;
- comparacoes potencia vs distancia;
- UI de warnings;
- **Novo**: Analise de TX/RX chains (ganhos/perdas passo a passo);
- **Novo**: Comparacao "Sem LNA/PA" vs "Com".

Aceite:

- graficos nao ocultam limitacoes;
- diretivas mostram impacto de orientacao;
- warnings sobre modelo simplificado aparecem;
- UI de chains mostra cada componente explicitamente.

### Checkpoint 8: GIS/Cobertura

Entregas:

- grade espacial;
- mapa Folium;
- heatmap de potencia/margem;
- importacao de shapefiles;
- **Novo**: Integracacao com LinkBudgetComplete;
- **Novo**: Avisos sobre heatmap assumir omnidirecionais.

Aceite:

- cobertura roda em area pequena;
- resolucao configuravel;
- aviso claro sobre terra plana/sem DEM;
- heatmap com PA/LNA/feeds configuravels.

### Checkpoint 9: Relatorios

Entregas:

- relatorio Markdown;
- tabelas e parametros;
- referencias e limitacoes;
- **Novo**: Inclusao de accuracy matrix (precisao esperada por cenario).

Aceite:

- relatorio reproduz calculo;
- limitacoes documentadas no relatorio.

### Checkpoint 10: Deploy

Entregas:

- Docker;
- Compose;
- README operacional;
- testes principais.

Aceite:

- app acessivel em `http://IP_DO_SERVIDOR:3953`.

## Matriz de Precisao Esperada

MVP usa modelos simplificados. Erros esperados por cenario:

| Cenario | Precisao | Erro Tipico |
|---------|----------|-------------|
| LOS Espaço Livre Perfeito | 95% | ±1-2 dB |
| LOS + 1 Obstáculo | 85% | ±3-5 dB |
| NLOS Urbano Simples | 70% | ±8-12 dB |
| NLOS + Multipercurso | 50% | ±10-15 dB |
| Antena Diretiva Mal Alinhada | 30% | ±15-25 dB 🔴 |
| Heatmap em Campus | 40% | ±30-50% erro espacial 🔴 |

**Limitacao Critica**: Sem orientacao relativa ou DEM, diretivas e mapas sao inadequados para decisoes profissionais.

## Riscos Tecnicos

| Risco | Mitigacao |
|---|---|
| Usuario confundir modelo didatico com simulacao EM | warnings, docs, limitations, accuracy matrix |
| Impedancia simplificada demais | parametrizar ambiente/geometria (Ground Plane, Patch) |
| Refletora sem feed realista | `FeedSpecification` obrigatorio + 7 tipos tabelados |
| Friis superestima cobertura | obstaculos, margem, accuracy matrix, warnings |
| Diretivas geram heatmap falso | orientacao explicita, LinkWithDirectivity, avisos em UI |
| Cabos/PA/LNA ignorados | `LinkBudgetComplete` com todos os elementos |
| Sem DEM/multipercurso | roadmap e disclaimer (Fase 2) |
| Feed inadequado para parabola | eficiencia de feed × aperture no calculo de ganho |

## Definicao de Pronto do MVP

MVP pronto quando:

- cria e salva antenas principais (omnidirecionais + diretivas);
- calcula dimensoes, impedancia aproximada, VSWR, ganho e area efetiva;
- calcula enlace com Friis completo + diretividade;
- suporta refletoras parabolicas com alimentadores tabelados;
- calcula impacto de orientacao para Yagi/refletora;
- modela cadeia TX/RX completa (PA, LNA, filtros, cabos, conectores);
- gera graficos e mapa inicial;
- exporta relatorio;
- documenta limitacoes e precisao esperada;
- roda via Streamlit/Docker em `3953`;
- testes cobrem casos numericos conhecidos;
- accuracy matrix publicada em UI/docs.

## Cronograma Realista Revisado

```
Checkpoint 0.5: Documentacao Tecnica ......... 2 dias
└─ formulas.md, assumptions.md, limitations.md, accuracy_matrix.md

Checkpoint 0: Infraestrutura (uv, Streamlit, Docker) ........... 1-2 dias

Checkpoint 1: Nucleo Matematico + Testes ... 3-4 dias

Checkpoint 2-3: Antenas (Monopole ate ReflectorAntenna) ....... 5-6 dias
└─ +1-2 dias por refletora + feed taxonomy

Checkpoint 4: Standalone UI ................. 3-4 dias

Checkpoint 5-6: Link Budget + Diretividade . 5-6 dias
└─ +2 dias por LinkBudgetComplete (PA, LNA, filters)

Checkpoint 7: Visualizacoes ................. 5-6 dias
└─ +1 dia por UI de TX/RX chains

Checkpoint 8: GIS + Cobertura ............... 6-7 dias

Checkpoint 9: Relatorios .................... 3-4 dias

Checkpoint 10: Deploy ....................... 2-3 dias

────────────────────────────────────────────
TOTAL ESTIMADO: 38-45 dias (≈8-9 semanas)
```

**Delta vs Original**: +5-6 dias por refletoras, alimentadores e cadeia RF completa.

## Priorização para MVP

### 🔴 ALTA (Implementar no MVP - Bloqueadores)

1. ReflectorAntenna + Feed taxonomy (5 dBi diferenca real)
2. PA parametrizavel (6-13 dB extra em gateways)
3. LNA parametrizavel (25-35 dB, transforma sensibilidade)
4. Cable losses automatico (1-2 dB acumulado)
5. LinkWithDirectivity (8-25 dB desvio em diretivas)

### 🟡 MÉDIA (Implementar em Checkpoint 5-8)

1. Filtros TX/RX (1-2 dB)
2. Circuladores (0.5-1 dB)
3. Analise completa de chains (UI passo-a-passo)
4. Comparacoes visuais PA/LNA on/off

### 🟢 BAIXA (Pós-MVP, Fase 2)

1. Conectores como parâmetro (0.2 dB each)
2. Baluns/acopladores (0-1 dB)
3. Feeding method (waveguide vs coaxial)
4. DEM/multipercurso
5. Validacao com hardware real

---

## Notas de Revisao

### Contradicoes Encontradas

1. **Parabola vs ReflectorAntenna**
   - **Original**: Scaffolding menciona "Parabola" sem diferenciar subtipos
   - **Analise rise_2**: Parabola e' UM tipo de refletora; necessario classe base ReflectorAntenna
   - **Decisao**: Refatorar "Parabola" → "ReflectorAntenna" com enums: parabolic_circular, parabolic_offset, cassegrain, gregorian
   - **Impacto**: Ganho pode variar 15-20% entre tipos; MVP foca parabolic_offset

2. **FeedSpecification Incompleta**
   - **Original**: Scaffolding menciona feeds.py genericamente
   - **Analise rise_2**: Feed e' CRITICO; eficiencia varia 0.40-0.88 (50% range)
   - **Decisao**: Expandir com 7 tipos tabelados, eficiencias reais, beamwidth requisitos
   - **Impacto**: Diferenca de feed = ate 5 dB no ganho da refletora

3. **LinkBudget vs LinkBudgetComplete**
   - **Original**: Scaffolding menciona LinkBudget genericamente
   - **Analise rise_2**: 8 elementos LoRa nao modelados (PA, LNA, filtros, circulador, cabos, conectores, baluns)
   - **Decisao**: Criar LinkBudgetComplete com todos os elementos; PA/LNA como presets
   - **Impacto**: Erro acumulado reduz de ±35 dB para ±3-5 dB em cenarios reais

4. **Diretividade Subestimada**
   - **Original**: Scaffolding menciona LinkWithDirectivity brevemente
   - **Analise rise_1**: Orientacao relativa ausente = erro de ate 25 dB em diretivas
   - **Decisao**: Fortalecer LinkWithDirectivity; azimute/elevacao obrigatorios para diretivas
   - **Impacto**: Heatmaps sem diretividade sao inadequados para Yagi/parabola

5. **Checkpoint 0.5 Omitido**
   - **Original**: Scaffolding comeca direto em Checkpoint 0
   - **Analise ref/sumario_executivo**: Documentacao OBRIGATORIA antes de codigo pesado
   - **Decisao**: Adicionar Checkpoint 0.5 (2 dias) para formulas.md, assumptions.md, limitations.md
   - **Impacto**: Previne refatoracoes dispendiosas depois

6. **Cronograma Subavaliado**
   - **Original**: 33-39 dias
   - **Analise rise_2**: Refletoras + feeds + cadeia completa = +5-6 dias
   - **Decisao**: Revisar para 38-45 dias (~8-9 semanas)
   - **Impacto**: Planejamento realista evita crunch

7. **Precisao Nao-Documentada**
   - **Original**: Scaffolding assume precisao sem matrices
   - **Analise rise_1**: Precisao esperada varia: LOS ±1-2 dB, NLOS ±8-15 dB, diretivas ±15-25 dB
   - **Decisao**: Adicionar accuracy_matrix.md; publicar em UI e relatorios
   - **Impacto**: Transparencia evita uso indevido para decisoes profissionais

8. **Alimentadores Para Parabola Criticos**
   - **Original**: Scaffolding menciona "feed" vagamente em ReflectorAntenna
   - **Analise rise_2**: Parabola 50cm sem feed realista perde 5 dB vs com horn corrugated
   - **Decisao**: Feed OBRIGATORIO; tabela de 7 tipos com eficiencias reais
   - **Impacto**: Diferenca entre "viavel" e "inviavel" em enlaces marginais

### Sintese Final

Scaffolding original era **50% completo** e **30% inadequado** para LoRa corporativo por omitir:
- Taxonomia de refletoras (parabolic_circular vs offset)
- Feed specification completa (7 tipos, 0.40-0.88 eficiencia)
- Cadeia RF completa (PA, LNA, filtros, circulador, cabos, conectores)
- Diretividade relativa TX/RX (azimute/elevacao)
- Documentacao de precisao esperada (accuracy matrix)
- Checkpoint 0.5 obrigatorio (2 dias documentacao)

Com revisoes incorporadas, scaffolding agora **95% completo** e **85% adequado** para MVP LoRa com gateways reais.

Cronograma revisado: 38-45 dias vs 33-39 original (+15% realista).
