<link rel="stylesheet" type="text/css" href="../css/style_.css">

# Implementation Roadmap — LoRa Antenna Platform MVP

**Status**: Ready for Development  
**Duration**: 38-45 dias (~8-9 semanas)  
**Target**: Production-ready MVP com gateways LoRa corporativos  
**Last Updated**: 2026-05-11  

> [SUMARIO](#sumário)

---

## Visão Geral

Roadmap segmentado em 11 sprints (Checkpoint 0.5 até 10), cada um com:
- Objetivos de curto prazo (semanal)
- Dependências explícitas
- Critérios de aceite (DoD)
- Rotinas de auto-validação (gatekeeping)
- Plano de rollback

**Gatekeeping**: Nenhum sprint avança sem passar na validação anterior.

---

## Sumário

- [Implementation Roadmap — LoRa Antenna Platform MVP](#implementation-roadmap--lora-antenna-platform-mvp)
  - [Visão Geral](#visão-geral)
  - [Sumário](#sumário)
  - [Arquitetura de Blocos](#arquitetura-de-blocos)
    - [BLOCO 1: SANDBOX DE SIMULAÇÃO (Sprints 0.5-7)](#bloco-1-sandbox-de-simulação-sprints-05-7)
    - [BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO (Sprints 8-10)](#bloco-2-simulação-em-campus-darcy-ribeiro-sprints-8-10)
  - [SPRINT 0.5: DOCUMENTAÇÃO TÉCNICA](#sprint-05-documentação-técnica)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo)
    - [Dependências](#dependências)
    - [Tarefas Principais](#tarefas-principais)
      - [1.1 `docs/formulas.md` (4 horas)](#11-docsformulasmd-4-horas)
      - [1.2 `docs/antenna_details.md` (5 horas)](#12-docsantenna_detailsmd-5-horas)
      - [1.3 `docs/propagation_model.md` (4 horas)](#13-docspropagation_modelmd-4-horas)
      - [1.4 `docs/assumptions.md` (3 horas)](#14-docsassumptionsmd-3-horas)
      - [1.5 `docs/limitations.md` (3 horas)](#15-docslimitationsmd-3-horas)
      - [1.6 `docs/accuracy_matrix.md` (2 horas)](#16-docsaccuracy_matrixmd-2-horas)
      - [1.7 `docs/references.md` (2 horas)](#17-docsreferencesmd-2-horas)
      - [1.8 `tests/validation_matrix.md` (2 horas)](#18-testsvalidation_matrixmd-2-horas)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod)
    - [Validação Automática](#validação-automática)
    - [Rollback Plan](#rollback-plan)
  - [SPRINT 0: INFRAESTRUTURA](#sprint-0-infraestrutura)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-1)
    - [Dependências](#dependências-1)
    - [Tarefas Principais](#tarefas-principais-1)
      - [2.1 Inicializar Projeto `uv`](#21-inicializar-projeto-uv)
      - [2.2 `pyproject.toml` Configurado](#22-pyprojecttoml-configurado)
      - [2.3 Estrutura Streamlit Minima](#23-estrutura-streamlit-minima)
      - [2.4 Docker \& Docker Compose](#24-docker--docker-compose)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-1)
    - [Validação Automática](#validação-automática-1)
    - [Rollback Plan](#rollback-plan-1)
  - [SPRINT 1: NÚCLEO MATEMÁTICO](#sprint-1-núcleo-matemático)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-2)
    - [Dependências](#dependências-2)
    - [Tarefas Principais](#tarefas-principais-2)
      - [3.1 `src/lora_antenna/constants.py`](#31-srclora_antennaconstantspy)
      - [3.2 `src/lora_antenna/formulas.py`](#32-srclora_antennaformulaspy)
      - [3.3 `tests/test_formulas.py`](#33-teststest_formulaspy)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-2)
    - [Validação Automática](#validação-automática-2)
    - [Rollback Plan](#rollback-plan-2)
  - [SPRINT 2-3: CLASSES ANTENNA](#sprint-2-3-classes-antenna)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-3)
    - [Dependências](#dependências-3)
    - [Tarefas Principais](#tarefas-principais-3)
      - [4.1 `src/lora_antenna/antenna/base.py`](#41-srclora_antennaantennabasepy)
      - [4.2 `src/lora_antenna/antenna/monopole.py`](#42-srclora_antennaantennamonopolepy)
      - [4.3 `src/lora_antenna/antenna/dipole.py`](#43-srclora_antennaantennadipolepy)
      - [4.4 `src/lora_antenna/antenna/ground_plane.py`](#44-srclora_antennaantennaground_planepy)
      - [4.5 `src/lora_antenna/antenna/patch.py`](#45-srclora_antennaantennapatchpy)
      - [4.6 `src/lora_antenna/antenna/yagi.py`](#46-srclora_antennaantennayagipy)
      - [4.7 `src/lora_antenna/antenna/reflector.py` (NOVO)](#47-srclora_antennaantennareflectorpy-novo)
      - [4.8 `src/lora_antenna/antenna/feeds.py` (NOVO)](#48-srclora_antennaantennafeedspy-novo)
      - [4.9 Testes de Antenas](#49-testes-de-antenas)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-3)
    - [Validação Automática](#validação-automática-3)
    - [Rollback Plan](#rollback-plan-3)
  - [SPRINT 4: UI STANDALONE](#sprint-4-ui-standalone)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-4)
    - [Tarefas Principais](#tarefas-principais-4)
      - [5.1 `src/lora_antenna/ui/pages/antenna.py`](#51-srclora_antennauipagesantennapy)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-4)
    - [Validação Automática](#validação-automática-4)
  - [SPRINT 5-6: LINK BUDGET + DIRETIVIDADE](#sprint-5-6-link-budget--diretividade)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-5)
    - [Tarefas Principais](#tarefas-principais-5)
      - [6.1 `src/lora_antenna/propagation/link_budget.py`](#61-srclora_antennapropagationlink_budgetpy)
      - [6.2 `src/lora_antenna/propagation/link_directivity.py` (NOVO)](#62-srclora_antennapropagationlink_directivitypy-novo)
      - [6.3 `src/lora_antenna/rf_chain/chain.py` (NOVO)](#63-srclora_antennarf_chainchainpy-novo)
      - [6.4 UI para Link Budget](#64-ui-para-link-budget)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-5)
    - [Validação Automática](#validação-automática-5)
  - [SPRINT 7: VISUALIZAÇÕES](#sprint-7-visualizações)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-6)
    - [Tarefas Principais](#tarefas-principais-6)
      - [7.1 `src/lora_antenna/ui/charts.py` (NOVO)](#71-srclora_antennauichartspy-novo)
    - [Critérios de Aceite (DoD)](#critérios-de-aceite-dod-6)
  - [✅ BLOCO 1 COMPLETO — TRANSIÇÃO PARA BLOCO 2](#-bloco-1-completo--transição-para-bloco-2)
  - [📍 BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO](#-bloco-2-simulação-em-campus-darcy-ribeiro)
  - [SPRINT 8: GIS/COBERTURA](#sprint-8-giscobertura)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-7)
  - [SPRINT 9: RELATÓRIOS](#sprint-9-relatórios)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-8)
  - [SPRINT 10: DEPLOY + QA](#sprint-10-deploy--qa)
    - [Objetivos Curto Prazo](#objetivos-curto-prazo-9)
  - [Gatekeeping Checklist Master](#gatekeeping-checklist-master)
  - [Rollback Procedures](#rollback-procedures)
    - [Quick Rollback (Sem perda de código)](#quick-rollback-sem-perda-de-código)
    - [Full Rollback (Volta ao estado anterior)](#full-rollback-volta-ao-estado-anterior)
    - [Database Rollback (Se houver)](#database-rollback-se-houver)
  - [Métricas de Saúde do Projeto](#métricas-de-saúde-do-projeto)
  - [Conclusão](#conclusão)

---

## Arquitetura de Blocos

Projeto dividido em **2 blocos complementares e integrados**, desenvolvidos sequencialmente:

### BLOCO 1: SANDBOX DE SIMULAÇÃO (Sprints 0.5-7)
**Objetivo**: Construir e validar ambiente controlado para modelagem de antenas e enlaces.

- Todos os modelos matemáticos implementados
- Classes Antenna + RF chain especificadas
- Testes contra literatura (ARRL, Balanis, Pozar)
- UI para criar/visualizar antenas
- Link budget com diretividade validado
- Padrões de radiação simulados

**Duração**: ~16-19 dias  
**Saída**: MVP Sandbox completo, pronto para integração geográfica

**Gate de Saída (Bloco 1 → Bloco 2)**:
- [ ] Todos 5 tipos de antena instanciados + testados
- [ ] Link budget validado contra ≥3 casos conhecidos
- [ ] UI sandbox executa sem erros
- [ ] Visualizações (polar, gain) renderizam corretamente
- [ ] Coverage heatmap funciona em espaço abstrato

---

### BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO (Sprints 8-10)
**Objetivo**: Aplicar objetos Antenna + Link do Sandbox em mapa real (UnB Campus).

- Importação de shapefile campus
- Grade espacial (5-50m) configurável
- Heatmap LoRa com cálculo de potência por ponto
- Relatórios com parâmetros + gráficos
- Deploy em container LAN

**Duração**: ~11-14 dias  
**Entrada**: Todos objetos validados do Bloco 1  
**Saída**: Plataforma completa em produção

**Relação entre blocos**:
```
Bloco 1 (Sandbox)
    ↓ validação ✓
Objetos Antenna + Link prontos
    ↓ reuso direto (sem modificação)
Bloco 2 (Campus)
    ↓ aplicação geográfica
Heatmap + Relatórios → Produção
```

> [SUMARIO](#sumário)

---

## SPRINT 0.5: DOCUMENTAÇÃO TÉCNICA
**Duração**: 2 dias  
**Responsável**: Arquiteto + Especialista Técnico  
**Status**: BLOQUEADOR para Sprints posteriores  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Documentar todas as fórmulas com derivações
- Listar limitações explícitas do modelo
- Criar matriz de precisão esperada
- Validar casos de teste numericos contra literatura

### Dependências
- Nenhuma (fase inicial)

### Tarefas Principais

#### 1.1 `docs/formulas.md` (4 horas)
Documentar:
- `wavelength_m(frequency_hz)`: λ = c / f
- `effective_area_m2(gain_dbi, wavelength_m)`: A_e = G * λ² / (4π)
- `reflection_coefficient(z_load, z0)`: Γ = (Z_L - Z0) / (Z_L + Z0)
- `vswr(z_load, z0)`: VSWR = (1 + |Γ|) / (1 - |Γ|)
- `return_loss_db(gamma)`: RL = -20 * log10(|Γ|)
- `fspl_db(distance_m, frequency_hz)`: FSPL = 20 * log10(distance) + 20 * log10(frequency) + 20 * log10(4π/c)
- `friis_received_power_dbm(...)`: Pr = Pt + Gt + Gr - FSPL - losses
- Fórmulas específicas por tipo de antena (Monopole, Dipole, Patch, Yagi, ReflectorAntenna)

**Referências obrigatórias**:
- Balanis, Antenna Theory, 3ª ed.
- Pozar, Microwave Engineering, 4ª ed.
- ARRL Antenna Book

#### 1.2 `docs/antenna_details.md` (5 horas)
Dimensões e parâmetros por tipo:

```
Monopole (λ/4):
  - Comprimento: λ/4 = c / (4 * f)
  - Ganho: ~2.15 dBi (espaço livre)
  - Impedância: Z ≈ 36.5 + j21.25 Ω (ressonante)
  - VSWR: ~2.0 typ
  - Padrão: hemisferico simplificado
  - Disclaimer: plano de terra essencial

Dipole (λ/2):
  - Comprimento: λ/2 = c / (2 * f)
  - Ganho: ~2.15 dBi (free space), varia com ambiente
  - Ambientes: free_space, above_ground, near_structure, cavity
  - Impedância por ambiente: 73.1Ω (free), ↓ (above_ground), etc.
  - VSWR: 1.2-3.0 dep. ambiente
  - Padrão: omnidireccional em azimute

Ground Plane (λ/4 + plano):
  - Monopole: λ/4
  - Plano: 2λ × 2λ recomendado
  - Impedância: 45 Ω (plano grande), aumenta com tamanho < 2λ
  - Ganho: similar monopole standalone
  - Warning: plano < 1λ → desvio > 20%

Patch (Microstrip):
  - Substrato obrigatório (FR4, Rogers 4003, 5880, Duroid)
  - Dimensões por Pozar aprox
  - Ganho: 5-9 dBi (dep. substrato)
  - Eficiência: ~80-90%
  - Bandwidth: ~2-3%
  - Padrão: quasi-omnidireccional elevacao, direcional azimute

Yagi (3-10 elementos):
  - Ganho empírico (Cebik formula):
    G ≈ 8 + 4.5 * log10(N_directors)
  - HPBW ≈ 50 / (Ganho em dBi)
  - Padrão: pico principal + lóbulos laterais
  - Disclaimer: modelo cos^n simplificado

ReflectorAntenna (Parabolic):
  - Tipos: circular, offset, cassegrain, gregorian
  - Ganho: G = η_total * (π * D / λ)²
  - HPBW: ~1.22 * λ / D
  - η_total = η_aperture * η_feed
  - Feed obrigatório (FeedSpecification)
```

#### 1.3 `docs/propagation_model.md` (4 horas)
Modelos de propagacao e atenuacao:

```
Free Space Path Loss (FSPL):
  FSPL(dB) = 20 * log10(distance_m) + 20 * log10(freq_hz) + 20 * log10(4π/c)
  Exemplo 915 MHz, 1 km: 91.67 dB

Obstacles (Tabela):
  FrequĂªncy: 433 MHz, 868 MHz, 915 MHz
  
  Type: Brick Wall
    433 MHz: min=3, nominal=6, max=12 dB
    868 MHz: min=4, nominal=8, max=15 dB
    915 MHz: min=4, nominal=8, max=15 dB
  
  Type: Concrete Wall
    433 MHz: min=6, nominal=12, max=25 dB
    868 MHz: min=8, nominal=15, max=30 dB
    915 MHz: min=8, nominal=15, max=30 dB
  
  [Outros tipos: Vidro, Vegetação densa/esparsa, Edifício concreto, Alvenaria]

Fresnel Zone:
  R_1 = sqrt(λ * d1 * d2 / (d1 + d2))
  Bloqueio > 50%: considerar atenuacao
  [Implementacao skeleton no MVP]
```

#### 1.4 `docs/assumptions.md` (3 horas)
Premissas do modelo:

```
Modelo Científico:
  - Antenas operadas no regime de campo distante (fraunhofer)
  - Padrões de radiação são modelos aproximados
  - Sem lóbulos secundários detalhados
  - Sem multipercurso explícito
  - Sem difração (exceto Fresnel básico)

Ambiente:
  - Terra plana (sem DEM)
  - Polarização alinhada TX/RX (sem desalinhamento)
  - Sem fading (Rayleigh, Rician, log-normal)
  - Sem interferência co-canal

Elétrica:
  - Cabo coaxial ideal (perdas tabeladas apenas)
  - Sem mismatch ativo (VSWR > 1 modelado passivamente)
  - Componentes RF ideais (PA, LNA, filtros como caixas pretas)

LoRa Específico:
  - SX1276 como chipset base
  - Sensibilidade por SF/BW conforme Semtech datasheet
  - Sem adaptação dinâmica (SF fixo)
  - Sem LoRaWAN overhead (apenas air-time RF)
```

#### 1.5 `docs/limitations.md` (3 horas)
Tudo que MVP NÃO faz:

```
⚠️  CRÍTICO: Ler antes de usar para decisões engenharia
  
MODELO SIMPLIFICADO:
  ✗ Sem simulação eletromagnética completa (FDTD, MoM)
  ✗ Padrões 2D (sem elevação complexa)
  ✗ Sem lóbulos secundários realistas
  ✗ Sem interferência (crosstalk, co-channel)

PROPAGAÇÃO:
  ✗ Sem multipercurso complexo
  ✗ Sem fading (Rayleigh, Rician, log-normal)
  ✗ Sem sombra (shadowing) dinâmica
  ✗ Sem difração exata (Fresnel skeleton)
  ✗ DEM não suportado (terra plana assumida)

ANTENAS DIRETIVAS:
  ✗ Sem patterns 3D completos
  ✗ Modelo cos^n para Yagi é aproximado
  ✗ Parabola assume feed simétrico

CADEIA RF:
  ✗ PA/LNA modelados como caixas pretas
  ✗ Sem ruído de fase (phase noise)
  ✗ Sem intermodulação
  ✗ Sem efeito de temperatura

VALIDAÇÃO:
  ✗ Sem testes de campo (drive test)
  ✗ Sem calibração com hardware real
  ✗ Sem dados de propagação reais

CONCLUSÃO:
  → Ferramenta EDUCACIONAL e ESTIMATIVA
  → NÃO para decisões críticas de produção SEM validação
  → Precisão esperada: ±1-25 dB dep. cenário (vide accuracy_matrix.md)
```

#### 1.6 `docs/accuracy_matrix.md` (2 horas)

```
┌─────────────────────────────┬──────────┬──────────────────┐
│ Cenário                     │ Precisão │ Erro Típico      │
├─────────────────────────────┼──────────┼──────────────────┤
│ LOS Espaço Livre Perfeito   │ 95%      │ ±1-2 dB          │
│ LOS + 1 Obstáculo           │ 85%      │ ±3-5 dB          │
│ NLOS Urbano Simples         │ 70%      │ ±8-12 dB         │
│ NLOS + Multipercurso        │ 50%      │ ±10-15 dB        │
│ Antena Diretiva Desalinhada │ 30%      │ ±15-25 dB 🔴     │
│ Heatmap em Campus           │ 40%      │ ±30-50% espacial │
└─────────────────────────────┴──────────┴──────────────────┘

Recomendações de Uso:
  ✓ LOS: Confiável (±2 dB)
  ✓ NLOS simples: Uso com ressalvas
  ⚠️  Diretivas: Validar com orientação explícita
  ❌ Heatmap para decisões críticas: Rejeitar
```

#### 1.7 `docs/references.md` (2 horas)
Citações e fontes:

```
Antenas Teóricas:
  [1] Balanis, C. A. (2012). Antenna Theory: Analysis and Design (3ª ed.)
  [2] Pozar, D. M. (2012). Microwave Engineering (4ª ed.)
  [3] ARRL Antenna Book (23ª ed., 2019)

LoRa/LoRaWAN:
  [4] Semtech SX1276 Datasheet v5.1 (2015)
  [5] LoRa Alliance Technical Committee. LoRaWAN Specification v1.0.3 (2018)
  [6] LoRa Alliance. RP002 Regional Parameters (2020)

Propagação:
  [7] ITU-R P.1238-10: Propagation data and prediction methods for indoor
  [8] ITU-R P.1546-6: Method for point-to-area predictions for terrestrial services
  [9] Friis, H.T. "A Note on a Simple Transmission Formula", IRE, 1946

Validação Empírica:
  [10] Cebik, L.B. Yagi Antenna Design (2007)
  [11] Various antenna measurement data from NIST/IEEE archives
```

#### 1.8 `tests/validation_matrix.md` (2 horas)

```
CASOS DE TESTE CONHECIDOS
════════════════════════════

Test #1: Wavelength @ 915 MHz
  Input: f = 915e6 Hz
  Expected: λ ≈ 0.3278 m
  Tolerance: ±0.1%
  Source: Basic physics (c/f)

Test #2: Dipole Length
  Input: f = 915e6 Hz, λ = 0.3278 m
  Expected: length = λ/2 ≈ 0.1639 m
  Tolerance: ±0.1%
  Source: Antenna design

Test #3: FSPL @ 1 km
  Input: distance = 1000 m, f = 915e6 Hz
  Expected: FSPL ≈ 91.67 dB
  Tolerance: ±0.1 dB
  Source: Friis formula

Test #4: Link Budget (Monopole-Monopole)
  Input: Pt=14 dBm, Gt=2.15 dBi, Gr=2.15 dBi, dist=1000m, f=915MHz
  Expected: Pr ≈ -73.37 dBm
  Tolerance: ±0.5 dB
  Source: Friis completo

Test #5: Parabola Gain @ 915 MHz, D=50cm
  Input: D = 0.5 m, η_aperture = 0.65, f = 915e6
  Expected: G ≈ 17.3 dBi (antes do feed)
  Tolerance: ±0.5 dB
  Source: G = η * (π*D/λ)²

Test #6: HPBW Parabola
  Input: D = 0.5 m, f = 915e6 MHz
  Expected: HPBW ≈ 0.8°
  Tolerance: ±10%
  Source: HPBW ≈ 1.22 * λ / D

[... 10+ testes adicionais]
```

### Critérios de Aceite (DoD)

- [ ] 8 arquivos `.md` criados e estruturados
- [ ] Todas as fórmulas com unidades explícitas
- [ ] Referências bibliográficas validadas
- [ ] Casos de teste documentados e rastreáveis
- [ ] Limitações não causam surpresas (explícitas)
- [ ] Accuracy matrix publicável em UI

### Validação Automática

```bash
# Checklist para aprovação Sprint 0.5

# 1. Arquivo checksum
find docs/ -name "*.md" | wc -l  # Esperado: 8

# 2. Validação de markdown
for f in docs/*.md; do
  pandoc "$f" -o /dev/null || echo "ERRO: $f"
done

# 3. Verificar formulascom regex (sample)
grep -c "$$" docs/formulas.md  # LaTeX ou notação clara

# 4. Revisar limitacoes documentadas
grep -c "⚠️\|❌\|🔴" docs/limitations.md

# 5. Casos de teste enumerados
grep -c "Test #" tests/validation_matrix.md  # Esperado: ≥ 15
```

### Rollback Plan

- Git: `git reset --hard origin/main` (nunca feito, fase documental)
- Não há dependências de código ainda

> [SUMARIO](#sumário)

---

## SPRINT 0: INFRAESTRUTURA
**Duração**: 1-2 dias  
**Responsável**: DevOps Engineer  
**Bloqueador anterior**: Sprint 0.5 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Python 3.11+ com `uv` configurado
- Streamlit minimo rodando
- Docker/Compose funcional
- Porta 3953 acessível em LAN

### Dependências
- Sprint 0.5 concluído (docs)
- Git configurado
- Python 3.11+, Docker, `uv` instalados

### Tarefas Principais

#### 2.1 Inicializar Projeto `uv`
```bash
# Criar diretório
mkdir -p lora-antenna-platform && cd lora-antenna-platform

# Inicializar uv
uv init --python 3.11

# Estrutura base
mkdir -p src/lora_antenna tests docs
```

#### 2.2 `pyproject.toml` Configurado
```toml
[project]
name = "lora-antenna-platform"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
  "streamlit>=1.28",
  "pydantic>=2.0",
  "numpy>=1.24",
  "pandas>=2.0",
  "plotly>=5.14",
  "folium>=0.14",
  "streamlit-folium>=0.6",
  "geopandas>=0.12",
  "shapely>=2.0",
  "pyproj>=3.4",
]

[dependency-groups]
dev = [
  "pytest>=7.0",
  "pytest-cov>=4.0",
  "ruff>=0.1",
  "mypy>=1.0",
]
```

#### 2.3 Estrutura Streamlit Minima
```python
# src/lora_antenna/app.py
import streamlit as st
from lora_antenna import __version__

st.set_page_config(
    page_title="LoRa Antenna Platform",
    page_icon="📡",
    layout="wide"
)

st.title("LoRa Antenna Platform")
st.markdown(f"**Version**: {__version__}")
st.info("MVP: Plataforma educacional para análise de antenas LoRa")

# Página de exemplo
with st.sidebar:
    page = st.radio("Navegação", ["Home", "Sobre"])

if page == "Home":
    st.write("Bem-vindo! Selecione uma opção acima.")
elif page == "Sobre":
    st.markdown("Ferramenta educacional para análise de antenas LoRa/LoRaWAN.")
```

#### 2.4 Docker & Docker Compose
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar uv
RUN pip install --no-cache-dir uv

# Copy projeto
COPY . .

# Instalar dependências
RUN uv pip install -e .

EXPOSE 3953

CMD ["streamlit", "run", "src/lora_antenna/app.py", "--server.port", "3953"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  lora-antenna:
    build: .
    ports:
      - "3953:3953"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=3953
    volumes:
      - ./src:/app/src
      - ./docs:/app/docs
```

### Critérios de Aceite (DoD)

- [ ] `uv run streamlit run src/lora_antenna/app.py --server.port 3953` funciona
- [ ] App abre em `http://localhost:3953`
- [ ] Docker build sem erro
- [ ] Docker Compose roda em `http://0.0.0.0:3953`
- [ ] Git commit do estado inicial

### Validação Automática

```bash
# Checklist Sprint 0

# 1. Dependências instaladas
uv pip list | grep streamlit

# 2. App roda localmente
timeout 5 uv run streamlit run src/lora_antenna/app.py --server.port 3953 &

# 3. Docker build
docker build -t lora-antenna:latest .

# 4. Docker Compose
docker-compose up -d
curl -I http://localhost:3953

# 5. Git setup
git log --oneline | head -1
```

### Rollback Plan

```bash
# Se Docker falhar
docker system prune -a --volumes

# Se pyproject.toml corrompido
git checkout pyproject.toml

# Se app não sobe
streamlit run src/lora_antenna/app.py --logger.level=debug
```

> [SUMARIO](#sumário)

---

## SPRINT 1: NÚCLEO MATEMÁTICO
**Duração**: 3-4 dias  
**Responsável**: Engenheiro de Física/Matemática  
**Bloqueador anterior**: Sprint 0 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Funções matemáticas puras implementadas
- Testes unitários para casos conhecidos
- Validação contra literatura (cases conhecidos)

### Dependências
- Sprint 0.5: docs com fórmulas ✓
- Sprint 0: ambiente rodando ✓

### Tarefas Principais

#### 3.1 `src/lora_antenna/constants.py`
```python
# Constantes físicas
C_M_PER_S = 299_792_458  # Velocidade da luz

# Bandas LoRa
FREQ_433_MHZ = 433e6
FREQ_868_MHZ = 868e6
FREQ_915_MHZ = 915e6

# Impedância de referência
Z0_OHM = 50

# SX1276 sensibilidades (SF7-SF12 @ BW=125kHz)
SX1276_SENSITIVITY_DBM = {
    7: -123,
    8: -126,
    9: -129,
    10: -132,
    11: -134,
    12: -137,
}
```

#### 3.2 `src/lora_antenna/formulas.py`
```python
import math
from lora_antenna.constants import C_M_PER_S

def wavelength_m(frequency_hz: float) -> float:
    """λ = c / f"""
    return C_M_PER_S / frequency_hz

def effective_area_m2(gain_dbi: float, wavelength_m: float) -> float:
    """A_e = G * λ² / (4π)"""
    gain_linear = 10 ** (gain_dbi / 10)
    return gain_linear * wavelength_m ** 2 / (4 * math.pi)

def reflection_coefficient(z_load: complex, z0: float = 50) -> complex:
    """Γ = (Z_L - Z0) / (Z_L + Z0)"""
    return (z_load - z0) / (z_load + z0)

def vswr(z_load: complex, z0: float = 50) -> float:
    """VSWR = (1 + |Γ|) / (1 - |Γ|)"""
    gamma = reflection_coefficient(z_load, z0)
    gamma_mag = abs(gamma)
    return (1 + gamma_mag) / (1 - gamma_mag)

def return_loss_db(gamma: complex) -> float:
    """RL = -20 * log10(|Γ|)"""
    return -20 * math.log10(abs(gamma))

def fspl_db(distance_m: float, frequency_hz: float) -> float:
    """FSPL = 20*log10(distance) + 20*log10(f) + 20*log10(4π/c)"""
    const = 20 * math.log10(4 * math.pi / C_M_PER_S)
    return 20 * math.log10(distance_m) + 20 * math.log10(frequency_hz) + const

def friis_received_power_dbm(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float,
    distance_m: float,
    frequency_hz: float,
    losses_db: float = 0
) -> float:
    """Pr(dBm) = Pt + Gt + Gr - FSPL - losses"""
    fspl = fspl_db(distance_m, frequency_hz)
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - fspl - losses_db

def link_margin_db(received_power_dbm: float, sensitivity_dbm: float) -> float:
    """Margem = Pr - Sensibilidade"""
    return received_power_dbm - sensitivity_dbm
```

#### 3.3 `tests/test_formulas.py`
```python
import math
import pytest
from lora_antenna.formulas import (
    wavelength_m, effective_area_m2, vswr, fspl_db, friis_received_power_dbm
)

class TestFormulas:
    
    def test_wavelength_915mhz(self):
        """Test case: λ @ 915 MHz ≈ 0.3276 m"""
        expected = 0.3276
        actual = wavelength_m(915e6)
        assert abs(actual - expected) < 0.0005  # ±0.1%
    
    def test_wavelength_868mhz(self):
        """Test case: λ @ 868 MHz ≈ 0.3456 m"""
        expected = 0.3456
        actual = wavelength_m(868e6)
        assert abs(actual - expected) < 0.0005
    
    def test_fspl_1km_915mhz(self):
        """Test case: FSPL @ 1 km, 915 MHz ≈ 91.67 dB"""
        expected = 91.67
        actual = fspl_db(1000, 915e6)
        assert abs(actual - expected) < 0.1
    
    def test_friis_monopole_monopole(self):
        """
        Test case: Monopole-Monopole link
        Pt=14 dBm, Gt=2.15 dBi, Gr=2.15 dBi, dist=1km, f=915MHz
        Expected Pr ≈ -73.37 dBm
        """
        actual = friis_received_power_dbm(
            tx_power_dbm=14,
            tx_gain_dbi=2.15,
            rx_gain_dbi=2.15,
            distance_m=1000,
            frequency_hz=915e6,
            losses_db=0
        )
        expected = -73.37
        assert abs(actual - expected) < 0.5
```

### Critérios de Aceite (DoD)

- [ ] `pytest tests/test_formulas.py` passa 100%
- [ ] Todos os casos conhecidos dentro de tolerância
- [ ] Code coverage > 95%
- [ ] Sem warnings (ruff, mypy)
- [ ] Documentação em docstrings

### Validação Automática

```bash
# Checklist Sprint 1

# 1. Testes passam
uv run pytest tests/test_formulas.py -v

# 2. Coverage
uv run pytest tests/test_formulas.py --cov=src/lora_antenna --cov-report=term

# 3. Linting
uv run ruff check src/lora_antenna/formulas.py

# 4. Type check
uv run mypy src/lora_antenna/formulas.py

# 5. Docstring coverage
python -m doctest src/lora_antenna/formulas.py -v
```

### Rollback Plan

```bash
# Se teste falhar
git diff tests/test_formulas.py  # Revisar mudança
git checkout tests/test_formulas.py

# Se fórmula estiver errada
# Consultar docs/formulas.md e literatura
```

> [SUMARIO](#sumário)

---

## SPRINT 2-3: CLASSES ANTENNA
**Duração**: 5-6 dias  
**Responsável**: Python Developer + Domain Expert  
**Bloqueador anterior**: Sprint 1 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Modelos Pydantic para antenas
- 6 tipos de antena funcionais (Monopole até ReflectorAntenna)
- Serialização JSON/SQLite
- Testes de instanciação

### Dependências
- Sprint 1: formulas.py ✓
- docs/antenna_details.md ✓

### Tarefas Principais

#### 4.1 `src/lora_antenna/antenna/base.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List

class Antenna(BaseModel):
    """Base class para todas as antenas"""
    
    id: str = Field(..., description="UUID único")
    name: str = Field(..., description="Nome descritivo")
    antenna_type: str = Field(..., description="Tipo (Monopole, Dipole, etc)")
    frequency_hz: float = Field(..., gt=0, description="Frequência em Hz")
    gain_dbi: float = Field(..., description="Ganho em dBi")
    impedance_ohm: complex = Field(default=complex(50, 0))
    vswr: float = Field(default=1.0)
    efficiency: float = Field(default=0.9)
    polarization: str = Field(default="Linear")
    effective_area_m2: float = Field(default=0.0)
    orientation_azimuth_deg: float = Field(default=0.0)
    orientation_elevation_deg: float = Field(default=0.0)
    location: Optional[Dict] = Field(default=None)
    schema_version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)
    radiation_pattern: Optional[Dict[str, List[float]]] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ant-001",
                "name": "Monopole 915MHz",
                "antenna_type": "Monopole",
                "frequency_hz": 915e6,
                "gain_dbi": 2.15,
            }
        }
```

#### 4.2 `src/lora_antenna/antenna/monopole.py`
```python
import math
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class Monopole(Antenna):
    """Antena monopolo λ/4"""
    
    def __init__(self, frequency_hz: float, **kwargs):
        self.antenna_type = "Monopole"
        self.frequency_hz = frequency_hz
        
        # Cálculos automáticos
        wl = wavelength_m(frequency_hz)
        self.height_m = wl / 4
        self.gain_dbi = 2.15  # Nominal
        self.impedance_ohm = complex(36.5, 21.25)  # Ressonante
        self.vswr = 2.0
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.9
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.3 `src/lora_antenna/antenna/dipole.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class DipoleEnvironment(str, Enum):
    FREE_SPACE = "free_space"
    ABOVE_GROUND = "above_ground"
    NEAR_STRUCTURE = "near_structure"
    CAVITY = "cavity"

class Dipole(Antenna):
    """Antena dipolo λ/2"""
    
    def __init__(
        self,
        frequency_hz: float,
        environment: DipoleEnvironment = DipoleEnvironment.FREE_SPACE,
        **kwargs
    ):
        self.antenna_type = "Dipole"
        self.frequency_hz = frequency_hz
        self.environment = environment
        
        wl = wavelength_m(frequency_hz)
        self.length_m = wl / 2
        self.gain_dbi = 2.15  # Base
        
        # Ajustar por ambiente
        if environment == DipoleEnvironment.FREE_SPACE:
            self.impedance_ohm = complex(73.1, 0)
            self.vswr = 1.45
        elif environment == DipoleEnvironment.ABOVE_GROUND:
            self.impedance_ohm = complex(60, -25)
            self.vswr = 2.0
        elif environment == DipoleEnvironment.NEAR_STRUCTURE:
            self.impedance_ohm = complex(50, -50)
            self.vswr = 2.5
        else:  # CAVITY
            self.impedance_ohm = complex(80, 40)
            self.vswr = 2.8
        
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.85
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.4 `src/lora_antenna/antenna/ground_plane.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class GroundPlaneShape(str, Enum):
    SQUARE = "square"
    CIRCULAR = "circular"
    INFINITE = "infinite"

class GroundPlane(Antenna):
    """Monopolo λ/4 sobre plano de terra"""
    
    def __init__(
        self,
        frequency_hz: float,
        plane_size_wavelengths: float = 2.0,
        shape: GroundPlaneShape = GroundPlaneShape.SQUARE,
        **kwargs
    ):
        self.antenna_type = "Ground Plane"
        self.frequency_hz = frequency_hz
        self.plane_size_wavelengths = plane_size_wavelengths
        self.shape = shape
        
        wl = wavelength_m(frequency_hz)
        self.monopole_height_m = wl / 4
        self.plane_size_m = plane_size_wavelengths * wl
        self.gain_dbi = 5.15  # +3 dB vs monopole standalone
        
        # Impedância depende do tamanho do plano
        if plane_size_wavelengths >= 2.0:
            self.impedance_ohm = complex(45, 0)
            self.design_note = "✓ Tamanho adequado (≥ 2λ)"
        else:
            factor = plane_size_wavelengths / 2.0
            z_real = 45 / factor
            self.impedance_ohm = complex(z_real, 0)
            self.design_note = "⚠️ Aviso: Plano pequeno, impedância pode variar ±20%"
        
        self.vswr = 1.5
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.9
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.5 `src/lora_antenna/antenna/patch.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class SubstrateType(str, Enum):
    FR4 = "FR4"
    ROGERS_4003 = "Rogers 4003"
    ROGERS_5880 = "Rogers 5880"
    DUROID = "Duroid"

# Tabela de substratos
SUBSTRATE_DATA = {
    "FR4": {"epsilon_r": 4.4, "tan_delta": 0.02, "thickness_mm": 1.6},
    "Rogers 4003": {"epsilon_r": 3.55, "tan_delta": 0.0027, "thickness_mm": 0.508},
    "Rogers 5880": {"epsilon_r": 2.2, "tan_delta": 0.0009, "thickness_mm": 0.787},
    "Duroid": {"epsilon_r": 2.17, "tan_delta": 0.0009, "thickness_mm": 0.787},
}

class Patch(Antenna):
    """Antena Patch (Microstrip)"""
    
    def __init__(
        self,
        frequency_hz: float,
        substrate: SubstrateType = SubstrateType.FR4,
        **kwargs
    ):
        self.antenna_type = "Patch"
        self.frequency_hz = frequency_hz
        self.substrate_type = substrate
        
        wl = wavelength_m(frequency_hz)
        sub = SUBSTRATE_DATA[substrate.value]
        
        # Dimensões (Pozar aproximado)
        self.length_m = wl / (2 * (sub["epsilon_r"] ** 0.5))
        self.width_m = self.length_m * 1.2
        
        # Ganho depende do substrato
        if substrate == SubstrateType.FR4:
            self.gain_dbi = 5.5
            self.efficiency = 0.8
        elif substrate == SubstrateType.ROGERS_4003:
            self.gain_dbi = 6.0
            self.efficiency = 0.85
        elif substrate == SubstrateType.ROGERS_5880:
            self.gain_dbi = 6.5
            self.efficiency = 0.9
        else:  # DUROID
            self.gain_dbi = 6.8
            self.efficiency = 0.92
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.2
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.6 `src/lora_antenna/antenna/yagi.py`
```python
import math
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class Yagi(Antenna):
    """Antena Yagi-Uda com 3-10 elementos"""
    
    def __init__(
        self,
        frequency_hz: float,
        num_elements: int = 5,
        **kwargs
    ):
        self.antenna_type = "Yagi"
        self.frequency_hz = frequency_hz
        self.num_elements = num_elements
        
        if num_elements < 3 or num_elements > 10:
            raise ValueError("num_elements deve estar entre 3 e 10")
        
        wl = wavelength_m(frequency_hz)
        
        # Ganho empírico (Cebik formula)
        num_directors = num_elements - 2
        self.gain_dbi = 8 + 4.5 * math.log10(max(num_directors, 1))
        
        # HPBW aproximado
        self.hpbw_deg = 50 / max(self.gain_dbi, 1)
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.3
        self.efficiency = 0.95
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        # Orientation obrigatória para diretivas
        self.design_note = "⚠️ Orientação (azimute/elevação) OBRIGATÓRIA"
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.7 `src/lora_antenna/antenna/reflector.py` (NOVO)
```python
from enum import Enum
from typing import Optional
from pydantic import Field
from lora_antenna.antenna.base import Antenna
from lora_antenna.antenna.feeds import FeedSpecification
from lora_antenna.formulas import wavelength_m, effective_area_m2
import math

class ReflectorType(str, Enum):
    PARABOLIC_CIRCULAR = "parabolic_circular"
    PARABOLIC_OFFSET = "parabolic_offset"
    CASSEGRAIN = "cassegrain"
    GREGORIAN = "gregorian"

class ReflectorAntenna(Antenna):
    """Antena refletora (base para paraboloides)"""
    
    reflector_type: ReflectorType = Field(..., description="Tipo de refletora")
    primary_diameter_m: float = Field(..., gt=0, description="Diâmetro primário")
    focal_ratio: float = Field(default=0.4, gt=0, lt=1)
    efficiency_aperture: float = Field(default=0.65, gt=0, lt=1)
    feed_specification: FeedSpecification = Field(..., description="Alimentador (OBRIGATÓRIO)")
    
    def __init__(
        self,
        frequency_hz: float,
        reflector_type: ReflectorType = ReflectorType.PARABOLIC_OFFSET,
        primary_diameter_m: float = 0.5,
        feed_specification: FeedSpecification = None,
        **kwargs
    ):
        self.antenna_type = "ReflectorAntenna"
        self.frequency_hz = frequency_hz
        self.reflector_type = reflector_type
        self.primary_diameter_m = primary_diameter_m
        
        if feed_specification is None:
            raise ValueError("feed_specification é OBRIGATÓRIO")
        self.feed_specification = feed_specification
        
        wl = wavelength_m(frequency_hz)
        
        # Ganho: G = η_total * (π * D / λ)²
        self.focal_length_m = self.focal_ratio * primary_diameter_m
        eta_total = self.efficiency_aperture * feed_specification.efficiency
        gain_linear = eta_total * (math.pi * primary_diameter_m / wl) ** 2
        self.gain_dbi = 10 * math.log10(gain_linear)
        
        # HPBW: ~1.22 * λ / D
        self.beamwidth_3db_deg = 1.22 * wl / primary_diameter_m
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.5
        self.efficiency = eta_total
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        # CRÍTICO: Feed determina o resultado
        self.design_note = (
            f"⚠️ Ganho depende do feed: "
            f"G = {self.gain_dbi:.1f} dBi "
            f"(aperture {self.efficiency_aperture:.0%} × feed {feed_specification.efficiency:.0%})"
        )
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.8 `src/lora_antenna/antenna/feeds.py` (NOVO)
```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal

class FeedType(str, Enum):
    HORN_PYRAMIDAL = "horn_pyramidal"
    HORN_CONICAL_CORRUGATED = "horn_conical_corrugated"
    HORN_EXPONENTIAL = "horn_exponential"
    DIPOLE = "dipole"
    PATCH = "patch"
    HELICAL = "helical"
    PROBE = "probe"

# Tabela de Feeds (eficiências reais)
FEED_TABLE = {
    "dipole": {"efficiency": 0.40, "beamwidth_deg": 170, "gain_dbi": 2.0},
    "probe": {"efficiency": 0.45, "beamwidth_deg": 160, "gain_dbi": 2.5},
    "patch": {"efficiency": 0.60, "beamwidth_deg": 120, "gain_dbi": 5.0},
    "horn_pyramidal": {"efficiency": 0.75, "beamwidth_deg": 100, "gain_dbi": 12.0},
    "horn_exponential": {"efficiency": 0.78, "beamwidth_deg": 95, "gain_dbi": 12.5},
    "horn_conical_corrugated": {"efficiency": 0.82, "beamwidth_deg": 95, "gain_dbi": 13.0},
    "helical": {"efficiency": 0.70, "beamwidth_deg": 110, "gain_dbi": 11.0},
}

class FeedSpecification(BaseModel):
    """Especificação de alimentador para refletoras"""
    
    feed_type: FeedType = Field(..., description="Tipo de feed")
    efficiency: float = Field(..., gt=0, lt=1, description="Eficiência (0-1)")
    beamwidth_deg: float = Field(..., gt=0, description="Beamwidth em graus")
    impedance_ohm: complex = Field(default=complex(50, 0))
    return_loss_db: float = Field(default=-20.0)
    polarization: str = Field(default="Linear")
    operating_bandwidth_mhz: float = Field(default=10.0)
    feeding_method: Literal["waveguide", "coaxial", "probe"] = Field(default="coaxial")
    feeding_loss_db: float = Field(default=0.5)
    gain_dbi: float = Field(default=0.0)
    
    @classmethod
    def from_type(cls, feed_type: FeedType) -> "FeedSpecification":
        """Factory method para criar feeds a partir de tipo"""
        data = FEED_TABLE.get(feed_type.value)
        if not data:
            raise ValueError(f"Feed type {feed_type} não encontrado na tabela")
        
        return cls(
            feed_type=feed_type,
            efficiency=data["efficiency"],
            beamwidth_deg=data["beamwidth_deg"],
            gain_dbi=data["gain_dbi"],
        )
```

#### 4.9 Testes de Antenas
```python
# tests/test_antenna_monopole.py
import pytest
from lora_antenna.antenna.monopole import Monopole

def test_monopole_915mhz():
    ant = Monopole(frequency_hz=915e6, name="Test Monopole", id="mon-001")
    assert ant.antenna_type == "Monopole"
    assert abs(ant.gain_dbi - 2.15) < 0.1
    assert ant.height_m > 0
    assert abs(ant.height_m - 0.0819) < 0.0005  # λ/4

def test_monopole_pydantic_export():
    ant = Monopole(frequency_hz=868e6, name="Test", id="mon-002")
    json_str = ant.model_dump_json()
    assert "Monopole" in json_str
    assert "868" in json_str
```

### Critérios de Aceite (DoD)

- [ ] 6 classes de antena implementadas (Monopole até ReflectorAntenna)
- [ ] FeedSpecification com 7 tipos tabelados
- [ ] Serialização Pydantic funciona (to_json, from_json)
- [ ] Todos os testes passam: `pytest tests/test_antenna_*.py`
- [ ] Impedância, VSWR, ganho dentro de faixas esperadas
- [ ] Warnings e disclaimers aparecem corretamente

### Validação Automática

```bash
# Checklist Sprint 2-3

# 1. Testes de antenas
uv run pytest tests/test_antenna_*.py -v

# 2. Cobertura
uv run pytest tests/test_antenna_*.py --cov=src/lora_antenna/antenna

# 3. Linting
uv run ruff check src/lora_antenna/antenna/

# 4. Type checking
uv run mypy src/lora_antenna/antenna/

# 5. Serialização JSON
python -c "
from lora_antenna.antenna.monopole import Monopole
m = Monopole(frequency_hz=915e6, id='test', name='Test')
print(m.model_dump_json())
"
```

### Rollback Plan

```bash
# Se antena quebrar
git diff src/lora_antenna/antenna/

# Se teste falhar, revisar valores esperados
# Consultar docs/antenna_details.md

# Rollback completo do sprint
git reset --hard <commit-anterior>
```

> [SUMARIO](#sumário)

---

## SPRINT 4: UI STANDALONE
**Duração**: 3-4 dias  
**Responsável**: Frontend Developer + UX Designer  
**Bloqueador anterior**: Sprint 2-3 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Interface Streamlit para criar antena
- Exibição de parâmetros calculados
- Gráficos 2D/3D de padrão de radiação
- Salvar/carregar antenas (JSON)

### Tarefas Principais

#### 5.1 `src/lora_antenna/ui/pages/antenna.py`
```python
import streamlit as st
from lora_antenna.antenna.monopole import Monopole
from lora_antenna.antenna.dipole import Dipole, DipoleEnvironment
# ... outras imports

st.set_page_config(page_title="Antenna Designer", layout="wide")

st.title("📡 Antenna Designer")

# Sidebar: Configurações
with st.sidebar:
    st.header("Antenna Configuration")
    
    antenna_type = st.selectbox(
        "Antenna Type",
        ["Monopole", "Dipole", "Ground Plane", "Patch", "Yagi", "ReflectorAntenna"]
    )
    
    frequency = st.selectbox(
        "Frequency",
        {"433 MHz": 433e6, "868 MHz": 868e6, "915 MHz": 915e6, "Custom": None}
    )
    
    if frequency is None:
        frequency = st.number_input("Custom Frequency (Hz)", min_value=100e6, value=915e6)
    
    name = st.text_input("Antenna Name", value=f"{antenna_type} {frequency/1e6:.0f}MHz")

# Criar antena based on type
if antenna_type == "Monopole":
    ant = Monopole(frequency_hz=frequency, name=name, id=f"ant-{int(time.time())}")

elif antenna_type == "Dipole":
    env = st.sidebar.selectbox("Environment", list(DipoleEnvironment))
    ant = Dipole(frequency_hz=frequency, environment=DipoleEnvironment(env), name=name, id=f"ant-{int(time.time())}")

# ... outros tipos

# Exibir resultados em tabs
tab1, tab2, tab3, tab4 = st.tabs(["Parameters", "Radiation Pattern", "Impedance", "Export"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Frequency", f"{frequency/1e6:.0f} MHz")
    col2.metric("Gain", f"{ant.gain_dbi:.2f} dBi")
    col3.metric("VSWR", f"{ant.vswr:.2f}")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Effective Area", f"{ant.effective_area_m2:.4f} m²")
    col5.metric("Impedance", f"{ant.impedance_ohm}")
    col6.metric("Efficiency", f"{ant.efficiency:.1%}")

with tab2:
    st.info("🔴 DISCLAIMER: Padrões simplificados (sem lóbulos secundários)")
    # Gráficos Plotly aqui

with tab3:
    # Análise de impedância e VSWR

with tab4:
    # Exportar JSON
    json_data = ant.model_dump_json()
    st.download_button(
        "Download JSON",
        data=json_data,
        file_name=f"{name}.json",
        mime="application/json"
    )
```

### Critérios de Aceite (DoD)

- [ ] Streamlit app roda sem erro
- [ ] Todos os tipos de antena podem ser criados via UI
- [ ] Parâmetros calculados aparecem corretamente
- [ ] Gráficos renderizam (Plotly)
- [ ] JSON exporta/importa corretamente

### Validação Automática

```bash
# Checklist Sprint 4

# 1. App roda
timeout 10 uv run streamlit run src/lora_antenna/app.py --server.port 3953 &

# 2. Verificar páginas carregam
curl -s http://localhost:3953 | grep -q "Antenna"

# 3. Export JSON válido
python -c "
import json
from lora_antenna.antenna.monopole import Monopole
m = Monopole(frequency_hz=915e6, id='test', name='Test')
data = json.loads(m.model_dump_json())
assert data['antenna_type'] == 'Monopole'
"
```

> [SUMARIO](#sumário)

---

## SPRINT 5-6: LINK BUDGET + DIRETIVIDADE
**Duração**: 5-6 dias  
**Responsável**: RF Engineer + Backend Developer  
**Bloqueador anterior**: Sprint 4 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- LinkBudget simples e completo
- LinkWithDirectivity (azimute/elevação)
- UI para enlace com 2 antenas
- Comparação PA/LNA on/off

### Tarefas Principais

#### 6.1 `src/lora_antenna/propagation/link_budget.py`
```python
from dataclasses import dataclass
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import friis_received_power_dbm, link_margin_db

@dataclass
class LinkBudget:
    """Link budget simples (Friis sem diretividade)"""
    
    tx_antenna: Antenna
    rx_antenna: Antenna
    distance_m: float
    tx_power_dbm: float = 14
    losses_db: float = 0
    
    @property
    def received_power_dbm(self) -> float:
        """Potência recebida via Friis"""
        return friis_received_power_dbm(
            tx_power_dbm=self.tx_power_dbm,
            tx_gain_dbi=self.tx_antenna.gain_dbi,
            rx_gain_dbi=self.rx_antenna.gain_dbi,
            distance_m=self.distance_m,
            frequency_hz=self.tx_antenna.frequency_hz,
            losses_db=self.losses_db
        )
    
    def link_margin_db(self, rx_sensitivity_dbm: float = -137) -> float:
        """Margem de enlace"""
        return link_margin_db(self.received_power_dbm, rx_sensitivity_dbm)
```

#### 6.2 `src/lora_antenna/propagation/link_directivity.py` (NOVO)
```python
import math
from dataclasses import dataclass
from typing import Tuple
from lora_antenna.antenna.base import Antenna

@dataclass
class GeographicPosition:
    """Posição geográfica (x, y, z em metros)"""
    x_m: float
    y_m: float
    z_m: float = 0

class LinkWithDirectivity:
    """Link budget com diretividade (azimute/elevação)"""
    
    def __init__(
        self,
        tx_antenna: Antenna,
        rx_antenna: Antenna,
        tx_position: GeographicPosition,
        rx_position: GeographicPosition,
        tx_azimuth_deg: float = 0,
        tx_elevation_deg: float = 0,
        rx_azimuth_deg: float = 0,
        rx_elevation_deg: float = 0,
        distance_m: float = None,
        tx_power_dbm: float = 14,
        losses_db: float = 0,
    ):
        self.tx_antenna = tx_antenna
        self.rx_antenna = rx_antenna
        self.tx_position = tx_position
        self.rx_position = rx_position
        self.tx_azimuth_deg = tx_azimuth_deg
        self.tx_elevation_deg = tx_elevation_deg
        self.rx_azimuth_deg = rx_azimuth_deg
        self.rx_elevation_deg = rx_elevation_deg
        self.tx_power_dbm = tx_power_dbm
        self.losses_db = losses_db
        
        # Calcular distância se não fornecida
        if distance_m is None:
            dx = rx_position.x_m - tx_position.x_m
            dy = rx_position.y_m - tx_position.y_m
            dz = rx_position.z_m - tx_position.z_m
            self.distance_m = math.sqrt(dx**2 + dy**2 + dz**2)
        else:
            self.distance_m = distance_m
    
    def _directivity_gain_reduction_db(
        self,
        antenna_type: str,
        off_axis_angle_deg: float
    ) -> float:
        """Redução de ganho por off-axis angle"""
        
        if antenna_type == "Monopole" or antenna_type == "Dipole":
            # Omnidirecionais: sem perda
            return 0
        
        elif antenna_type == "Yagi":
            # Modelo cos^n simplificado
            n = 2
            off_axis_rad = math.radians(off_axis_angle_deg)
            reduction = -10 * n * math.log10(abs(math.cos(off_axis_rad)) + 0.01)
            return min(reduction, -30)  # Máximo -30 dB atrás
        
        elif antenna_type == "ReflectorAntenna":
            # Parabola: modelo estreito (gaussiano)
            beamwidth = getattr(self.antenna, 'beamwidth_3db_deg', 1.0)
            reduction = -12 * (off_axis_angle_deg / beamwidth) ** 2
            return min(reduction, -40)  # Máximo -40 dB
        
        else:
            return 0
    
    def received_power_dbm_with_directivity(self) -> float:
        """Potência recebida considerando diretividade"""
        
        # TX: perda por desalinhamento
        tx_off_axis = math.degrees(
            math.acos(max(-1, min(1, math.cos(math.radians(self.tx_azimuth_deg)))))
        )
        tx_reduction = self._directivity_gain_reduction_db(
            self.tx_antenna.antenna_type, tx_off_axis
        )
        
        # RX: perda por desalinhamento
        rx_off_axis = math.degrees(
            math.acos(max(-1, min(1, math.cos(math.radians(self.rx_azimuth_deg)))))
        )
        rx_reduction = self._directivity_gain_reduction_db(
            self.rx_antenna.antenna_type, rx_off_axis
        )
        
        # Friis com ganhos reduzidos
        from lora_antenna.formulas import friis_received_power_dbm
        
        tx_gain_effective = self.tx_antenna.gain_dbi + tx_reduction
        rx_gain_effective = self.rx_antenna.gain_dbi + rx_reduction
        
        return friis_received_power_dbm(
            tx_power_dbm=self.tx_power_dbm,
            tx_gain_dbi=tx_gain_effective,
            rx_gain_dbi=rx_gain_effective,
            distance_m=self.distance_m,
            frequency_hz=self.tx_antenna.frequency_hz,
            losses_db=self.losses_db
        )
```

#### 6.3 `src/lora_antenna/rf_chain/chain.py` (NOVO)
```python
from dataclasses import dataclass, field
from typing import Optional
from lora_antenna.antenna.base import Antenna

@dataclass
class TxChain:
    """Cadeia transmissora completa"""
    
    base_power_dbm: float = 14  # SX1276 ou similar
    pa_gain_db: float = 0  # 0 (sem PA) até +13 dB
    tx_filter_loss_db: float = 1.0
    tx_circulator_loss_db: float = 0.5
    tx_cable_loss_db: float = 0  # Calculado automaticamente
    tx_connectors_loss_db: float = 0.4  # ~2 conectores @ 0.2 dB each
    
    @property
    def eirp_dbm(self, antenna_gain_dbi: float) -> float:
        """EIRP = Pt + PA + Gt - todas as perdas"""
        losses = (
            self.tx_filter_loss_db +
            self.tx_circulator_loss_db +
            self.tx_cable_loss_db +
            self.tx_connectors_loss_db
        )
        return self.base_power_dbm + self.pa_gain_db + antenna_gain_dbi - losses

@dataclass
class RxChain:
    """Cadeia receptora completa"""
    
    rx_filter_loss_db: float = 1.0
    rx_circulator_loss_db: float = 0.5
    rx_cable_loss_db: float = 0
    rx_connectors_loss_db: float = 0.4
    lna_gain_db: float = 0  # 0 (sem LNA) até +35 dB
    lna_nf_db: float = 1.0  # Figura de ruído
    
    @property
    def effective_sensitivity_dbm(self, base_sensitivity_dbm: float) -> float:
        """Sensibilidade efetiva com LNA"""
        losses = (
            self.rx_filter_loss_db +
            self.rx_circulator_loss_db +
            self.rx_cable_loss_db +
            self.rx_connectors_loss_db
        )
        return base_sensitivity_dbm - self.lna_gain_db + losses + self.lna_nf_db

@dataclass
class LinkBudgetComplete:
    """Link budget COMPLETO (cadeia TX/RX + todas as perdas)"""
    
    tx_antenna: Antenna
    rx_antenna: Antenna
    distance_m: float
    
    tx_chain: TxChain = field(default_factory=TxChain)
    rx_chain: RxChain = field(default_factory=RxChain)
    
    obstacles_loss_db: float = 0
    
    def link_margin_db(self, rx_base_sensitivity_dbm: float = -137) -> float:
        """Margem com cadeia completa"""
        
        eirp = self.tx_chain.eirp_dbm(self.tx_antenna.gain_dbi)
        
        # FSPL
        from lora_antenna.formulas import fspl_db
        fspl = fspl_db(self.distance_m, self.tx_antenna.frequency_hz)
        
        # Potência recebida
        received = eirp - fspl - self.obstacles_loss_db + self.rx_antenna.gain_dbi
        
        # Sensibilidade efetiva
        eff_sensitivity = self.rx_chain.effective_sensitivity_dbm(rx_base_sensitivity_dbm)
        
        return received - eff_sensitivity
```

#### 6.4 UI para Link Budget
```python
# src/lora_antenna/ui/pages/link.py
import streamlit as st
from lora_antenna.propagation.link_budget import LinkBudget, LinkWithDirectivity, GeographicPosition
from lora_antenna.rf_chain.chain import LinkBudgetComplete, TxChain, RxChain

st.title("🔗 Link Budget Calculator")

# Carregar antenas (from database ou session)
# ...

col1, col2 = st.columns(2)

with col1:
    st.subheader("TX Antenna")
    tx_antenna = st.selectbox("Select TX Antenna", ["Monopole 915MHz", "Yagi 915MHz"])

with col2:
    st.subheader("RX Antenna")
    rx_antenna = st.selectbox("Select RX Antenna", ["Monopole 915MHz", "Parabola 915MHz"])

# Distância
distance = st.slider("Distance (m)", 100, 10000, 1000)

# Modo simples vs completo
mode = st.radio("Mode", ["Simple (Friis)", "With Directivity", "Complete (TX/RX Chains)"])

if mode == "Simple (Friis)":
    # LinkBudget simples
    pass

elif mode == "With Directivity":
    # LinkWithDirectivity
    st.subheader("Orientation")
    col1, col2 = st.columns(2)
    with col1:
        tx_az = st.number_input("TX Azimuth (°)", 0, 360, 0)
        tx_el = st.number_input("TX Elevation (°)", -90, 90, 0)
    with col2:
        rx_az = st.number_input("RX Azimuth (°)", 0, 360, 180)
        rx_el = st.number_input("RX Elevation (°)", -90, 90, 0)

elif mode == "Complete (TX/RX Chains)":
    st.subheader("TX Chain")
    pa_gain = st.slider("PA Gain (dB)", 0, 13, 0)
    
    st.subheader("RX Chain")
    lna_gain = st.slider("LNA Gain (dB)", 0, 35, 0)
    
    # Comparação antes/depois
    # ...
```

### Critérios de Aceite (DoD)

- [ ] LinkBudget, LinkWithDirectivity, LinkBudgetComplete implementados
- [ ] UI para link budget funciona
- [ ] Comparação PA/LNA on/off mostra diferenças reais
- [ ] Testes passam: `pytest tests/test_friis_budget.py`
- [ ] Margem de enlace calculada corretamente

### Validação Automática

```bash
# Checklist Sprint 5-6

# 1. Testes
uv run pytest tests/test_friis_budget.py tests/test_link_directivity.py -v

# 2. Validação de casos conhecidos
python -c "
from lora_antenna.propagation.link_budget import LinkBudget
from lora_antenna.antenna.monopole import Monopole

tx = Monopole(frequency_hz=915e6, id='tx', name='TX')
rx = Monopole(frequency_hz=915e6, id='rx', name='RX')
link = LinkBudget(tx, rx, distance_m=1000, tx_power_dbm=14)

pr = link.received_power_dbm
assert abs(pr - (-73.37)) < 0.5, f'Expected -73.37 dBm, got {pr}'
print(f'✓ Link budget: {pr:.2f} dBm')
"

# 3. UI testa
timeout 10 uv run streamlit run src/lora_antenna/app.py &
```

> [SUMARIO](#sumário)

---

## SPRINT 7: VISUALIZAÇÕES
**Duração**: 5-6 dias  
**Responsável**: Frontend Developer (Plotly Expert)  
**Bloqueador anterior**: Sprint 5-6 ✓ PASSA  
**Bloco**: BLOCO 1

### Objetivos Curto Prazo
- Gráficos polares para padrões de radiação
- Padrão 3D simplificado
- Gráficos de potência vs distância
- TX/RX chain breakdown visual

### Tarefas Principais

#### 7.1 `src/lora_antenna/ui/charts.py` (NOVO)
```python
import plotly.graph_objects as go
import numpy as np
from lora_antenna.antenna.base import Antenna

def radiation_pattern_polar(antenna: Antenna, num_points: int = 360):
    """Gráfico polar do padrão de radiação"""
    
    angles = np.linspace(0, 360, num_points)
    
    # Padrão simplificado (cos^n para diretivas, omni para monopole/dipole)
    if antenna.antenna_type in ["Monopole", "Dipole"]:
        # Omnidireccional em azimute
        pattern = np.ones(num_points)
    elif antenna.antenna_type == "Yagi":
        # Modelo cos^n
        n = 2
        off_axis = np.radians(angles)
        pattern = np.maximum(np.cos(off_axis) ** n, 0)
    elif antenna.antenna_type == "ReflectorAntenna":
        # Parabola: gaussiano
        beamwidth = getattr(antenna, 'beamwidth_3db_deg', 1.0)
        pattern = np.exp(-2.77 * (angles / beamwidth) ** 2)
    else:
        pattern = np.ones(num_points)
    
    # Converter para dB
    pattern_db = 10 * np.log10(pattern + 0.001)
    
    fig = go.Figure(data=
        go.Scatterpolar(
            r=pattern_db,
            theta=angles,
            fill='toself',
            name=antenna.antenna_type
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-20, 0])),
        title=f"Radiation Pattern: {antenna.name}",
        showlegend=True
    )
    
    return fig

def power_vs_distance(link_budget, max_distance: float = 5000):
    """Gráfico: Potência recebida vs distância"""
    
    distances = np.linspace(100, max_distance, 100)
    powers = [link_budget.friis_received_power_dbm(d) for d in distances]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distances,
        y=powers,
        mode='lines',
        name='Received Power',
        line=dict(color='blue')
    ))
    
    # Adicionar linha de sensibilidade
    if hasattr(link_budget, 'rx_sensitivity_dbm'):
        fig.add_hline(
            y=link_budget.rx_sensitivity_dbm,
            line_dash="dash",
            annotation_text="RX Sensitivity",
            annotation_position="right"
        )
    
    fig.update_layout(
        title="Received Power vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Power (dBm)",
        hovermode='x unified'
    )
    
    return fig

def tx_rx_chain_breakdown(tx_chain, rx_chain, antenna_gain_tx, antenna_gain_rx):
    """Breakdown visual da cadeia TX/RX"""
    
    # TX chain
    tx_stages = [
        f"Base Power: {tx_chain.base_power_dbm:.1f} dBm",
        f"+ PA Gain: +{tx_chain.pa_gain_db:.1f} dB",
        f"+ Antenna: +{antenna_gain_tx:.1f} dBi",
        f"- Losses: -{tx_chain.tx_filter_loss_db + tx_chain.tx_cable_loss_db + tx_chain.tx_connectors_loss_db:.1f} dB",
    ]
    
    eirp = tx_chain.base_power_dbm + tx_chain.pa_gain_db + antenna_gain_tx - (...)
    
    # Gráfico em barras horizontal
    fig = go.Figure()
    
    # ... plotar TX chain
    # ... plotar RX chain
    
    return fig
```

### Critérios de Aceite (DoD)

- [ ] Gráficos polares renderizam para todos os tipos de antena
- [ ] Padrão 3D simplificado implementado (ou skeleton)
- [ ] Gráficos de potência vs distância corretos
- [ ] TX/RX chain breakdown visual funciona
- [ ] Disclaimers aparecem nos gráficos ("SIMPLIFIED", etc)

> [SUMARIO](#sumário)

---

## ✅ BLOCO 1 COMPLETO — TRANSIÇÃO PARA BLOCO 2

**Marco Crítico**: Sprint 7 concluído com sucesso  
**Status**: Sandbox de simulação validado e pronto

**Checklist de Saída Bloco 1**:
- ✓ 5 tipos de antena operacionais (Monopole, Dipole, GroundPlane, Patch, Yagi + ReflectorAntenna)
- ✓ Link budget com diretividade implementado
- ✓ Friis equation validado contra 3+ casos de teste conhecidos
- ✓ UI sandbox executável sem erros
- ✓ Visualizações polares + ganho renderizam
- ✓ Heatmap funciona em espaço abstrato (sem coordenadas reais)
- ✓ Persistência (Pydantic + JSON) operacional
- ✓ Testes unitários passam (coverage > 95%)

**Próximo Passo**: Integração geográfica com Campus Darcy Ribeiro  
**Data Esperada**: Fim do dia 19-22 do cronograma total

> [SUMARIO](#sumário)

---

## 📍 BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO

Blocos 1 e 2 compartilham objetos Antenna + Link do Sandbox **sem modificação**.  
Bloco 2 adiciona contexto geográfico, mapa e relatórios.

> [SUMARIO](#sumário)

---

## SPRINT 8: GIS/COBERTURA
**Duração**: 6-7 dias  
**Responsável**: GIS Engineer + Backend Developer  
**Bloqueador anterior**: Sprint 7 ✓ PASSA  
**Bloco**: BLOCO 2

### Objetivos Curto Prazo
- Grade espacial configurável (5-50m)
- Mapa Folium com heatmap
- Cálculo de potência em cada ponto
- Importação de shapefiles (opcional MVP)

> [SUMARIO](#sumário)

---

## SPRINT 9: RELATÓRIOS
**Duração**: 3-4 dias  
**Responsável**: Backend Developer  
**Bloqueador anterior**: Sprint 8 ✓ PASSA  
**Bloco**: BLOCO 2

### Objetivos Curto Prazo
- Geração de markdown com parâmetros
- Tabelas de link budget
- Inclusão de gráficos em PDF
- Documentação de limitações no relatório

> [SUMARIO](#sumário)

---

## SPRINT 10: DEPLOY + QA
**Duração**: 2-3 dias  
**Responsável**: DevOps + QA  
**Bloqueador anterior**: Sprint 9 ✓ PASSA  
**Bloco**: BLOCO 2

### Objetivos Curto Prazo
- Docker build e push
- Testes E2E
- README final
- Deploy em LAN (porta 3953)

> [SUMARIO](#sumário)

---

## Gatekeeping Checklist Master

```markdown
# MASTER VALIDATION GATE

## Gate 0.5 → 0 (Documentação → Infra)
- [ ] 8 docs .md criados
- [ ] Todas as fórmulas com referências
- [ ] Casos de teste enumerados (≥15)
- [ ] Accuracy matrix definida

## Gate 0 → 1 (Infra → Formulas)
- [ ] `uv run streamlit run ...` funciona
- [ ] Docker build sucesso
- [ ] Git initial commit

## Gate 1 → 2-3 (Formulas → Antenas)
- [ ] `pytest tests/test_formulas.py` 100%
- [ ] Coverage > 95%
- [ ] Casos conhecidos dentro de tolerância

## Gate 2-3 → 4 (Antenas → UI)
- [ ] 6 classes de antena implementadas
- [ ] FeedSpecification com 7 tipos
- [ ] Serialização JSON funciona
- [ ] `pytest tests/test_antenna_*.py` 100%

## Gate 4 → 5-6 (UI → Link Budget)
- [ ] Streamlit antena page funciona
- [ ] Parâmetros exibem corretamente
- [ ] JSON export/import funciona

## Gate 5-6 → 7 (Link Budget → Visualizations)
- [ ] `pytest test_friis_budget.py` 100%
- [ ] LinkBudgetComplete testado
- [ ] Casos de teste Friis validados

## Gate 7 → 8 (Visualizations → GIS)
- [ ] Gráficos polares renderizam
- [ ] Power vs distance gráfico ok
- [ ] TX/RX breakdown visual ok

## Gate 8 → 9 (GIS → Reports)
- [ ] Heatmap renderiza em 5 min ou menos
- [ ] Grade configurável 5-50m
- [ ] Aviso de modelo simplificado aparece

## Gate 9 → 10 (Reports → Deploy)
- [ ] Markdown export funciona
- [ ] Gráficos incluídos em relatório
- [ ] Limitações documentadas

## Gate 10: FINAL QA
- [ ] App acessível em http://0.0.0.0:3953
- [ ] Testes E2E passam
- [ ] Docker funciona
- [ ] README completo
```

> [SUMARIO](#sumário)

---

## Rollback Procedures

### Quick Rollback (Sem perda de código)

```bash
# Se último commit quebrou algo
git log --oneline | head -5
git revert <commit-id>

# Se quer voltar a antes do sprint
git reset --soft origin/main
git status  # Mudanças estarão em staging
```

### Full Rollback (Volta ao estado anterior)

```bash
# Backup das mudanças (para salvaguarda)
git stash
git log --oneline > sprint-backup.log

# Voltar ao HEAD anterior a este sprint
git reset --hard <commit-id>

# Limpar Docker e ambiente
docker system prune -a --volumes
rm -rf .venv uv.lock
```

### Database Rollback (Se houver)

```bash
# Se uma migração quebrar
sqlite3 gestao.db ".tables"
sqlite3 gestao.db ".schema"

# Restaurar backup anterior
cp gestao.db.backup gestao.db
```

> [SUMARIO](#sumário)

---

## Métricas de Saúde do Projeto

**A cada sprint, medir**:

1. **Code Quality**
   - Test coverage (target: > 95%)
   - Linting issues (target: 0)
   - Type check errors (target: 0)

2. **Performance**
   - Streamlit load time: < 3s
   - Heatmap render: < 5m (1km²)
   - API response: < 200ms

3. **Status de Funcionalidades**
   - Critérios de aceite: 100%
   - Bugs críticos: 0
   - Warnings em UI: minimizados

> [SUMARIO](#sumário)

---

## Conclusão

Roadmap segue abordagem **"caminho feliz primeiro"**: funcionalidades básicas antes de otimização.

**Gate keepers** impedem avanço até que fase anterior esteja sólida.

**Documentação** (Sprint 0.5) é bloqueador proposital para evitar refatorações dispendiosas.

Cronograma realista **38-45 dias** com margem para contingências.
