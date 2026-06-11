<link rel="stylesheet" type="text/css" href="../css/style_.css">

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
  FrequĂªncy: ~~433 MHz~~ (Fora da faixa definida pela ANATEL), ~~868 MHz~~ (Fora da faixa definida pela ANATEL), 915 MHz
  
  Type: Brick Wall
    ~~433 MHz: min=3, nominal=6, max=12 dB~~ (Fora da faixa definida pela ANATEL).
    ~~868 MHz: min=4, nominal=8, max=15 dB~~ (Fora da faixa definida pela ANATEL).
    915 MHz: min=4, nominal=8, max=15 dB
  
  Type: Concrete Wall
    ~~433 MHz: min=6, nominal=12, max=25 dB~~ (Fora da faixa definida pela ANATEL).
    ~~868 MHz: min=8, nominal=15, max=30 dB~~ (Fora da faixa definida pela ANATEL).
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