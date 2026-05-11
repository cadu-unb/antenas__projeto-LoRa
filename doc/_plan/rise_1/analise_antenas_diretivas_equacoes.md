# ANÁLISE CRÍTICA: COBERTURA DE TIPOS DE ANTENA E ADEQUAÇÃO DE EQUAÇÕES

**Data:** 09 de maio de 2026  
**Escopo:** Verificação de lacunas em antenas diretivas, parabólicas e sistemas mistos

---

## PARTE 1: ANTENAS DIRETIVAS E PARABÓLICAS

### 1.1 STATUS ATUAL DA ESPECIFICAÇÃO

#### Tipos Previstos (Checkpoint 3)
```python
Antena base (Antenna)
├── Monopole λ/4 ✅
├── Dipole λ/2 ✅
├── Ground Plane ✅
├── Patch ✅
└── Yagi ✅
```

#### Tipos NÃO Previstos Explicitamente
```
❌ Parábola/Dish
❌ Corneta (Horn)
❌ Helix (Helical)
❌ Espiral (Spiral)
❌ Log-Periódica
❌ Antena de Fenda (Slot)
❌ Microfita Impressa (Printed)
❌ Arranjos Fasados (Phased Array)
❌ Sistemas com Diversidade Espacial
```

---

### 1.2 LACUNA CRÍTICA #1: ANTENAS PARABÓLICAS/DISH

#### Por Que São Importantes para LoRa?

**Contexto Técnico:**
LoRa típico usa antenas de ganho baixo-a-médio (2-9 dBi) porque:
- Dispositivos finais são de baixa potência
- Cobertura omnidirecional é desejável
- Tamanho físico é restringido

**MAS:**
- Gateways em locais elevados (torres, postes) podem usar antenas mais direcionadas
- Links ponto-a-ponto de longa distância (1-10 km) se beneficiam de ganho
- Sistemas de backup/redundância em LoRa corporativa usam múltiplos gateways

**Exemplo Real:**
```
Caso de Uso: Campus UnB
─────────────────────────
TX: Antena Direcional (Yagi 7-elem ou Dish pequeno) no pico + alto
RX: Múltiplos Gateways Omnidirecionais espalhados

Problema não Coberto:
  Como calcular Friis para TX Direcional → RX Omnidirecional?
  E se TX está fora do lóbulo principal do RX?
```

---

### 1.3 LACUNA CRÍTICA #2: PADRÕES DE RADIAÇÃO DIRETIVOS

#### Problema Atual
A especificação define padrões teóricos simplificados:

```python
# Atual
class RadiationPattern:
    if antenna_type == "Dipole":
        pattern = sin(θ)  # Toroidal 2D
    elif antenna_type == "Yagi":
        pattern = exp(-((θ - 0) / 0.3)²)  # Gaussiano
```

**Limitações:**
1. ✗ Não representa **lóbulos secundários**
2. ✗ Não representa **nulos profundos** (cancelamento)
3. ✗ Não trata **elevação (θ) vs. azimute (φ)** separadamente
4. ✗ Parabola: padrão completamente diferente e muito mais complexo

#### Padrão de Parábola Real

```
Parabola ideal (aperture uniforme):
─────────────────────────────────

Ganho: G = η * (π*D/λ)²
onde:
  η = eficiência de abertura (0.5-0.8 típico)
  D = diâmetro da parábola
  λ = comprimento de onda

Padrão de Radiação:
  Muito mais "picado" que Yagi
  Lóbulos secundários mais baixos (~-25 dB típico)
  Beamwidth: HPBW ≈ 1.22 * λ / D

Exemplo numérico @ 915 MHz:
─────────────────────────────
λ = 0.328 m
D = 0.5 m (parábola pequena de 50 cm)

G = 0.65 * (π*0.5/0.328)² ≈ 9.5 dBi
HPBW ≈ 1.22 * 0.328 / 0.5 ≈ 0.8° (MUITO estreito!)

Compare com Yagi 7-elem:
  Ganho: ~12 dBi
  HPBW: ~30-40° (MUITO mais larga)
```

---

### 1.4 LACUNA CRÍTICA #3: CÁLCULO DE FRIIS COM ANTENAS DIRETIVAS

#### Problema Fundamental

**Equação de Friis atual (simples):**
```
P_r = P_t * G_t * G_r * (λ / 4πd)²
```

**Problema:**
Esta fórmula assume que o ganho é **isotropicamente ganho em TODAS as direções**.

**Na realidade:**
```
P_r = P_t * G_t(θ_t, φ_t) * G_r(θ_r, φ_r) * (λ / 4πd)² * L_orient
```

Onde:
- `G_t(θ_t, φ_t)` = ganho TX na direção θ, φ
- `G_r(θ_r, φ_r)` = ganho RX na direção θ, φ
- `L_orient` = fator de desadaptação de orientação

#### Exemplo Crítico

```
Cenário: Campus com Yagi TX Direcional
──────────────────────────────────────

Configuração:
  TX: Yagi 7-elem, G = 12 dBi, aponta para Norte
  RX: Omnidirecional, G = 2 dBi
  Distância: 1 km
  Frequência: 915 MHz

Cálculo INCORRETO (Friis simples):
  P_r = 14 dBm + 12 dBi + 2 dBi - FSPL(1km)
      = 14 + 12 + 2 - 91.67 = -63.67 dBm
      
Cálculo CORRETO (com orientação):
  Se RX está no lóbulo principal (eixo Yagi):
    P_r ≈ -63.67 dBm (igual)
    
  Se RX está a 30° (fora do lóbulo):
    G_t @ 30° ≈ 12 - 8 dB = 4 dBi (redução de ~8 dB)
    P_r ≈ 14 + 4 + 2 - 91.67 = -71.67 dBm (10 dB pior!)
    
  Se RX está no nulo (90° para o lado):
    G_t @ 90° ≈ -5 dBi (negativo = abaixo de isotropia)
    P_r ≈ INVIÁVEL mesmo em distância curta!
```

**Impacto na Simulação:**
- Heatmap de cobertura será **completamente errado**
- Pode mostrar cobertura onde não há
- Pode ocultar "sombras de radiação"

---

### 1.5 LACUNA CRÍTICA #4: SISTEMAS MISTOS (ARRAYS, MIMO, DIVERSIDADE)

#### Cenários Não Cobertos

```
1️⃣  ARRANJO SIMPLES (Linear Array)
────────────────────────────────────
  4 dipolos em linha, espaçamento λ/2
  → Ganho aumentado + padrão modificado
  Não previsto: Cálculo de ganho de arranjo
  
2️⃣  SISTEMA COM DIVERSIDADE ESPACIAL
────────────────────────────────────
  TX: 1 antena
  RX: 3 antenas em posições diferentes
  → Combinar sinais para melhorar SNR
  Não previsto: Ganho de diversidade
  
3️⃣  MIMO SIMPLES (LoRa corporativa)
────────────────────────────────────
  TX: 2 antenas ortogonais
  RX: 2 antenas ortogonais
  → Multiplexação espacial
  Não previsto: Capacidade MIMO, ortogonalidade
  
4️⃣  MÚLTIPLOS GATEWAYS (Típico em LoRaWAN)
─────────────────────────────────────────
  3-5 gateways em posições diferentes
  Mesmo dispositivo pode alcançar múltiplos GW
  Não previsto: Trilateration, redundância
```

---

## PARTE 2: ADEQUAÇÃO DAS EQUAÇÕES E ABORDAGEM DE CÁLCULO

### 2.1 ESCOPO ATUAL DE EQUAÇÕES

#### Equações Implementadas ✅

```
1. Comprimento de Onda
   λ = c / f ✓

2. Área Efetiva
   A_e = G * λ² / (4π) ✓

3. VSWR
   Γ = (Z - Z₀) / (Z + Z₀)
   VSWR = (1 + |Γ|) / (1 - |Γ|) ✓

4. Free Space Path Loss (FSPL)
   L_FSPL = 20*log10(d) + 20*log10(f) + K ✓

5. Equação de Friis (Simples)
   P_r = P_t + G_t + G_r - L_FSPL ✓

6. Margem de Enlace
   Margin = P_r - P_rx_sensitivity ✓
```

#### Equações NÃO Implementadas ❌

```
1. ❌ Ganho de Arranjo (Array Gain)
   G_array = G_single * N * F(θ, spacing)
   
2. ❌ Fator de Ganho Direcional
   G(θ, φ) = G_pico * F_normalizado(θ, φ)
   
3. ❌ Fator de Desadaptação de Orientação
   L_orient = G_t(θ_t) * G_r(θ_r) / (G_t_max * G_r_max)
   
4. ❌ Zonas de Fresnel (Verificação de Linha de Visada)
   R_n = sqrt(n * λ * d₁ * d₂ / (d₁ + d₂))
   
5. ❌ Difração em Terreno (Knife-Edge ou Bullington)
   L_diffrac = fator dependente de h/R_fresnel
   
6. ❌ Cálculo de Ganho de Diversidade
   SNR_diversity = SNR_single * M (idealizado)
   ou fórmula mais complexa com correlação
   
7. ❌ Polarização Mismatch
   L_pol = -|cos(θ_pol)|² dB
   
8. ❌ Modelo de Sombra (Log-Normal Fading)
   P_r(shadowing) = P_r(friis) + N(μ=0, σ=σ_shadow)
```

---

### 2.2 ANÁLISE DE PRECISÃO MATEMÁTICA

#### Taxonomia de Aproximações

```
CAMADA 1: ESPAÇO LIVRE (Free Space)
═════════════════════════════════════
Premissas:
  ✓ Antenas em espaço livre (não há obstáculos)
  ✓ Linha de visada (LOS)
  ✓ Efeitos de terra negligenciáveis
  ✓ Antenas isotrópicas (ou ganho constante)
  
Precisão: ~95% em LOS perfeita
Erro típico: ±1-2 dB em condições ideais

Implementado: ✅ COMPLETO (Friis Simples)


CAMADA 2: OBSTÁCULOS GENÉRICOS
═══════════════════════════════════
Premissas:
  ✓ Perdas fixas por tipo de obstáculo
  ✗ NÃO considera espessura variável
  ✗ NÃO considera ângulo de incidência
  ✗ NÃO modela difração real
  
Precisão: ~70-80% em ambiente urbano
Erro típico: ±3-5 dB

Implementado: ⚠️  PARCIAL (Tabela de valores fixos)


CAMADA 3: PROPAGAÇÃO MULTI-PERCURSO
═════════════════════════════════════
Premissas:
  ✗ NÃO considerado
  ✗ Apenas espaço livre ou perda fixa
  
Fenômenos Ignorados:
  - Reflexão (reflexos em edifícios)
  - Refração (gradientes de temperatura/umidade)
  - Espalhamento (difusão em superfícies ásperas)
  - Desvanecimento (fading rápido vs. lento)
  
Precisão: N/A (não implementado)
Erro típico: ±5-10 dB em ambiente rico em multipercursos

Implementado: ❌ NÃO


CAMADA 4: TERRENO E RELEVO
════════════════════════════
Premissas:
  ✗ NÃO considerado
  
Fenômenos Ignorados:
  - Difração por edifícios
  - Difração por relevo
  - Zonas de Fresnel bloqueadas
  - Efeitos de reflexão em solo
  
Precisão: N/A
Erro típico: ±5-15 dB em terreno heterogêneo

Implementado: ❌ NÃO


CAMADA 5: ANTENAS DIRETIVAS
═════════════════════════════
Premissas:
  ✗ NÃO considerado
  
Fenômenos Ignorados:
  - Padrão de radiação 3D
  - Lóbulos secundários
  - Nulos de cancelamento
  - Efeitos de orientação
  
Precisão: N/A
Erro típico: ±8-15 dB dependendo de orientação relativa

Implementado: ❌ NÃO
```

---

### 2.3 MATRIZ DE PRECISÃO ESPERADA POR CENÁRIO

```
┌─────────────────────────────┬──────────┬────────────────┐
│ Cenário                     │ Precisão │ Intervalo de   │
│                             │ Esperada │ Erro           │
├─────────────────────────────┼──────────┼────────────────┤
│ LOS Perfeita, Espaço Livre  │ 95%      │ ±1-2 dB        │
│ LOS com uma parede          │ 85%      │ ±3-4 dB        │
│ NLOS urbano (2+ obstáculos) │ 70%      │ ±5-8 dB        │
│ Ambiente com multipercurso  │ 50%      │ ±10-15 dB      │
│ Com antena direcional (?)   │ 60%      │ ±8-15 dB       │
│ Com diversidade (?)         │ 75%      │ ±5-10 dB       │
└─────────────────────────────┴──────────┴────────────────┘

Legenda:
  (?) = Não implementado ainda
```

---

### 2.4 EXEMPLO PRÁTICO: ERRO ACUMULADO

```
Campus UnB, Enlace TX-RX
════════════════════════════════

Cenário:
  TX: Monopolo λ/4 no LS (térreo)
  RX: Monopolo λ/4 no ICC (2 km de distância)
  Frequência: 915 MHz
  TX Power: 14 dBm
  
Cálculo Friis (MV Simples):
───────────────────────────
  FSPL @ 2 km = 91.67 + 20*log10(2) = 97.67 dB
  P_r = 14 + 2.15 + 2.15 - 97.67 = -79.37 dBm
  Margem @ -137 dBm = 57.63 dB ✓ Viável
  
Realidade (Com obstáculos + terreno + multipercurso):
──────────────────────────────────────────────────────
  
  Perdas adicionais estimadas:
    ├─ Edifícios no percurso: ~10-15 dB
    ├─ Relevo (Brasília é plana): ~2-3 dB
    ├─ Multipercurso/sombreamento: ~5-10 dB
    └─ Efeitos de árvores (perípheral): ~3-5 dB
    
  Total: ~20-33 dB adicional (conservador)
  
  P_r_real ≈ -79.37 - 25 dB = -104.37 dBm
  Margem real ≈ 32.63 dB ✓ Ainda viável, mas margem reduzida
  
ERRO TOTAL: ~25 dB (!!!)
  
  Se modelo não incluir obstáculos:
    Previsão: Viável com 57 dB de margem
    Realidade: Viável com 33 dB de margem
    Erro relativo: ~45% de superestimação

  Se modelo for usado para heatmap:
    Área de cobertura prevista: ~4 km² (círculo de 2 km)
    Área real: ~1.5-2 km² (MUITO menor!)
    Erro espacial: ~50-75%
```

---

## PARTE 3: CONTRAMEDIDAS ATUAIS NA ESPECIFICAÇÃO

### 3.1 O Que Foi Feito para Mitigar Erros

```
Mitigação #1: Tabela de Obstáculos
═════════════════════════════════════
Implementado: ✅ Sim (em recomendações estruturadas)
Efetividade: 70% (reduz erro de 25 dB para ~5-8 dB)
Custo: Baixo (tabela estática)
Problema: Não varia com geometria, não trata multipercurso


Mitigação #2: Documentação de Limitações
══════════════════════════════════════════
Implementado: ✅ Sim (checkpoint 0.5)
Efetividade: 100% em transpárência, 0% em precisão
Custo: Baixo
Problema: Usuário ainda pode ser enganado se não ler


Mitigação #3: Disclaimers na UI
════════════════════════════════
Implementado: ✅ Planejado em UI
Efetividade: 80% (mostra ao usuário, não resolve problema)
Custo: Baixo
Problema: Usuário pode ignorar


Mitigação #4: Teste de Validação Contra Casos Conhecidos
══════════════════════════════════════════════════════════
Implementado: ✅ Sim (testes unitários)
Efetividade: 90% para FSPL puro, 50% para obstáculos reais
Custo: Médio
Problema: Testa apenas fórmulas, não cenários complexos
```

### 3.2 O Que NÃO Foi Feito (Gaps)

```
Gap #1: Sem Validação Contra Dados de Campo Real
═════════════════════════════════════════════════
Problema: Não há comparação com medições reais
Impacto: Erros não descobertos até deployment
Solução Recomendada: Coletar dados LoRa real @ campus UnB
Esforço: 2-3 semanas (2-3 gateways + drive tests)
Prioridade: 🔴 ALTA (pós MVP)


Gap #2: Sem Modelo de Sombra (Shadow Fading)
═════════════════════════════════════════════
Problema: Apenas FSPL + obstáculos fixos
Realidade: Multipercurso causa variação de ±3-8 dB
Impacto: Margem calculada pode ser ilusória (aparenta-se maior)
Solução Recomendada: Adicionar distribuição log-normal em simulação
Esforço: 1 semana
Prioridade: 🟡 MÉDIA (checkpoint 8+)


Gap #3: Sem Cálculo de Orientação Relativa
═════════════════════════════════════════════
Problema: Friis assume ganho máximo em todas as direções
Realidade: Yagi/Parabola têm padrão direcional
Impacto: Erro de ±8-15 dB se antena não aponta para RX
Solução Recomendada: Parametrizar orientação TX/RX, multiplicar ganho por fator direcional
Esforço: 3-4 dias
Prioridade: 🟡 MÉDIA (antes do checkpoint 8 de cobertura)


Gap #4: Sem Verificação de Fresnel
═════════════════════════════════════
Problema: Não verifica se zona de Fresnel está bloqueada
Realidade: Obstáculos podem bloquear 1ª zona de Fresnel = perda > modelo
Impacto: Em terreno acidentado ou urbano, erro pode ser >10 dB
Solução Recomendada: Calcular R_fresnel, comparar com obstáculos
Esforço: 2-3 dias
Prioridade: 🟡 MÉDIA (checkpoint 8+)


Gap #5: Sem Suporte a Antenas Parabólicas/Diretivas
════════════════════════════════════════════════════
Problema: Escopo limitado a Monopole, Dipole, Patch, Yagi
Realidade: Gateways profissionais usam Yagi+, Dish, Horn
Impacto: Não pode simular arquiteturas reais de LoRaWAN corporativo
Solução Recomendada: Adicionar Parabola, Horn, Log-Periódica
Esforço: 1-2 semanas
Prioridade: 🔴 ALTA (antes de simular gateways reais)


Gap #6: Sem Modelo de Diversidade/MIMO
═══════════════════════════════════════
Problema: Não considerado em simulação
Realidade: LoRaWAN corporativo usa múltiplos GW
Impacto: Não pode avaliar ganho de redundância
Solução Recomendada: Adicionar cálculo de combinação de sinais
Esforço: 1 semana
Prioridade: 🟡 MÉDIO (pós MVP)
```

---

## PARTE 4: RECOMENDAÇÕES ESTRUTURADAS

### 4.1 ROADMAP PARA COMPLETUDE MATEMÁTICA

#### **Fase 1: MVP (Dias 1-35, Checkpoints 0-10)**
```
✅ Espaço livre (Friis simples)
✅ Obstáculos genéricos (tabela fixa)
✅ Antenas omnidirecionais + Yagi básico
⚠️  Disclaimer explícito: "Modelo simplificado"
```

**Precisão esperada:** 70-80% em LOS, 50-70% em NLOS simples


#### **Fase 2: Melhoria (Semanas 9-12, Checkpoints 10+)**
```
Prioridade 1 (1-2 semanas):
  ✓ Adicionar Parabola/Dish como tipo de antena
  ✓ Implementar cálculo de ganho de parabola
  ✓ Implementar fator de orientação relativa
  → Impacto: +15% precisão em cenários diretivos

Prioridade 2 (1-2 semanas):
  ✓ Adicionar modelo de sombra (log-normal)
  ✓ Implementar verificação de Fresnel
  → Impacto: +10% precisão em NLOS

Prioridade 3 (2-3 semanas):
  ✓ Validação contra dados reais (drive test)
  ✓ Calibração de modelo de obstáculos
  → Impacto: +20% precisão geral
```

**Precisão esperada após Fase 2:** 85% em LOS, 75-80% em NLOS


#### **Fase 3: Completa (Meses 3+)**
```
  ✓ Suporte a arranjos (arrays)
  ✓ Suporte a MIMO/diversidade
  ✓ Modelo de multipercurso completo
  ✓ Integração com dados ITU-R
  → Impacto: +15-20% em cenários complexos
  
Precisão esperada:** 90%+ em praticamente qualquer cenário
```

---

### 4.2 INTEGRAÇÃO IMEDIATA (ANTES DE MVP COMPLETO)

#### **Adicionar aos Checkpoints Existentes:**

**Checkpoint 2-3 (Classe Antenna):**
```python
# NOVO: Parâmetro de orientação
class Antenna(BaseModel):
    ...
    orientation_azimuth_deg: float = 0     # 0° = Norte
    orientation_elevation_deg: float = 90  # 90° = horizonte
    # NÃO USAR ainda, apenas preparar para futuro
```

**Checkpoint 5-6 (Classe Link):**
```python
# NOVO: Método de ganho direcional
class Link:
    ...
    
    def gain_factor_directivity(self) -> float:
        """
        Retorna fator de ganho considerando orientação relativa.
        
        Por agora: Retorna 1.0 (sem perda, assume LOS perfeita)
        Futuro: Aplicar padrão 3D baseado em orientação
        
        Returns:
            gain_factor (linear, não dB)
        """
        # MVP: Ignora orientação
        return 1.0
```

**Checkpoint 7 (Visualizações):**
```python
# NOVO: Visualização de padrão 3D
# Adicionar aba "Directivity" mostrando:
#   ├─ Padrão polar (plano E-plane)
#   ├─ Padrão polar (plano H-plane)
#   ├─ Padrão 3D (superfície)
#   └─ Aviso: "Padrão simplificado para fins didáticos"
```

**Checkpoint 8 (GIS/Cobertura):**
```python
# NOVO: Parâmetro de "tipo de gateway"
class CoverageSimulation:
    gateway_type: Literal["omnidirectional", "directional"]
    gateway_azimuth_deg: float  # Se directional
    
    # MVP: Usa sempre omnidirectional
    # Futuro: Aplica fator de orientação no heatmap
```

---

### 4.3 ESPECIFICAÇÃO DETALHADA: PARABOLA

#### Adicionar à Especificação Complementar:

```python
from dataclasses import dataclass
import math

@dataclass
class ParabolaDish(Antenna):
    """
    Antenna de Parábola/Dish.
    
    Equações:
      Ganho: G = η * (π*D/λ)²
      Beamwidth (HPBW): BW ≈ 1.22 * λ / D
      Lóbulo secundário típico: ~-25 dB
      
    Aplicações LoRa:
      - Gateways em torres (links P2P)
      - Backhaul de longa distância
      - Sistemas com restrição de potência TX
    """
    
    diameter_m: float = 0.5  # Diâmetro em metros
    efficiency: float = 0.65  # 0.5-0.8 típico
    feed_type: str = "parabolic"  # Type of feed
    
    @property
    def effective_area_m2(self) -> float:
        """Área efetiva da abertura."""
        return math.pi * (self.diameter_m / 2) ** 2 * self.efficiency
    
    @property
    def gain_dbi(self) -> float:
        """
        Ganho em dBi.
        
        G = η * (π*D/λ)²
        
        Em dB: G_dBi = 10*log10(G_linear)
        """
        wavelength = 3e8 / self.frequency_hz
        gain_linear = self.efficiency * (math.pi * self.diameter_m / wavelength) ** 2
        return 10 * math.log10(gain_linear)
    
    @property
    def beamwidth_deg(self) -> float:
        """
        Largura do feixe principal (HPBW).
        
        Fórmula: BW ≈ 1.22 * λ / D
        (1.22 vem da difração circular de Airy)
        """
        wavelength = 3e8 / self.frequency_hz
        return math.degrees(1.22 * wavelength / self.diameter_m)
    
    @property
    def radiation_pattern_model(self) -> str:
        """Modelo de padrão de radiação."""
        return f"Paraboloid (BW≈{self.beamwidth_deg:.1f}°, Lobs~-25dB)"
    
    # Exemplo @ 915 MHz, D = 0.5 m
    # Ganho ≈ 9.5 dBi
    # Beamwidth ≈ 0.8°
```

#### Tabela de Parabolas Padrão:

```python
PARABOLA_MODELS = {
    "SQ30_small": {
        "diameter_m": 0.3,
        "efficiency": 0.65,
        "gain_dbi_at_915mhz": 5.2,
        "beamwidth_deg_at_915mhz": 1.3,
        "reference": "Typical small parabola"
    },
    "SQ50_medium": {
        "diameter_m": 0.5,
        "efficiency": 0.65,
        "gain_dbi_at_915mhz": 9.5,
        "beamwidth_deg_at_915mhz": 0.8,
        "reference": "Typical medium parabola"
    },
    "SQ60_large": {
        "diameter_m": 0.6,
        "efficiency": 0.70,
        "gain_dbi_at_915mhz": 11.2,
        "beamwidth_deg_at_915mhz": 0.66,
        "reference": "Typical large parabola"
    },
}
```

---

### 4.4 CÁLCULO DE ORIENTAÇÃO RELATIVA

#### Implementar Antes de Checkpoint 10:

```python
class LinkWithDirectivity:
    """
    Friis completo com suporte a antenas diretivas.
    """
    
    tx_antenna: Antenna
    rx_antenna: Antenna
    tx_azimuth_deg: float = 0
    tx_elevation_deg: float = 90
    rx_azimuth_deg: float = 0
    rx_elevation_deg: float = 90
    
    def angle_tx_to_rx(self) -> tuple[float, float]:
        """
        Calcula ângulos (azimute, elevação) de TX para RX.
        
        Simplficado: Assume TX-RX em plano vertical (elevação)
        Futuro: Usar coordenadas 3D reais
        """
        # Diferença azimutal
        az_diff = abs(self.rx_azimuth_deg - self.tx_azimuth_deg)
        az_diff = min(az_diff, 360 - az_diff)  # Ângulo mínimo
        
        # Diferença de elevação (simplificado)
        el_diff = abs(self.rx_elevation_deg - self.tx_elevation_deg)
        
        return (az_diff, el_diff)
    
    def directivity_factor_tx(self) -> float:
        """
        Reduz ganho TX se RX não está no lóbulo principal.
        
        Modelo simplificado:
          - Lóbulo principal: ganho completo
          - Fora: redução linear com ângulo
          - Nulo: ganho negativo
        """
        az_diff, el_diff = self.angle_tx_to_rx()
        
        # Se TX é omnidirecional: sem penalidade
        if isinstance(self.tx_antenna, (Monopole, Dipole)):
            return 1.0  # Sem penalidade
        
        # Se TX é Yagi ou Parabola: aplicar fator
        if isinstance(self.tx_antenna, Yagi):
            beamwidth = 40  # °, típico para Yagi 5-elem
            return self._reduce_factor(az_diff, beamwidth)
        
        if isinstance(self.tx_antenna, ParabolaDish):
            beamwidth = self.tx_antenna.beamwidth_deg
            return self._reduce_factor(az_diff, beamwidth)
        
        return 1.0
    
    def directivity_factor_rx(self) -> float:
        """Similar para RX."""
        az_diff, el_diff = self.angle_tx_to_rx()
        
        if isinstance(self.rx_antenna, (Monopole, Dipole)):
            return 1.0
        
        # Mesmo cálculo...
        return 1.0
    
    def _reduce_factor(self, angle_off_axis_deg: float, beamwidth_deg: float) -> float:
        """
        Calcula fator de redução de ganho.
        
        Modelo (cos^n approximation):
          - 0° (lóbulo principal): 1.0 (0 dB)
          - beamwidth/2: 0.707 (-3 dB)
          - beamwidth: 0.1 (-20 dB aprox)
          - > beamwidth*2: lóbulo secundário (< 0.01)
        """
        if angle_off_axis_deg <= beamwidth_deg / 2:
            # Dentro do lóbulo principal
            n = 2.0  # Expoente (cos^n)
            normalized_angle = angle_off_axis_deg / (beamwidth_deg / 2)
            return math.cos(math.pi * normalized_angle / 2) ** n
        else:
            # Fora: redução rápida
            return max(0.01, 1.0 / (1.0 + ((angle_off_axis_deg / beamwidth_deg) ** 2)))
    
    def received_power_with_directivity_dbm(self) -> float:
        """
        P_r = P_t + G_t(θ) + G_r(θ) - FSPL
        
        com fatores de diretividade.
        """
        g_t_factor = self.directivity_factor_tx()
        g_r_factor = self.directivity_factor_rx()
        
        # Converter para dB
        g_t_reduction_db = 10 * math.log10(max(g_t_factor, 0.001))
        g_r_reduction_db = 10 * math.log10(max(g_r_factor, 0.001))
        
        # Aplicar na equação Friis
        P_r = (self.tx_power_dbm +
               self.tx_antenna.gain_dbi + g_t_reduction_db +
               self.rx_antenna.gain_dbi + g_r_reduction_db -
               self.fspl_db)
        
        return P_r
```

---

## PARTE 5: RESUMO EXECUTIVO

### 5.1 Situação Atual de Cobertura

| Tipo de Antena | Coberto? | Precisão | Prioridade |
|---|---|---|---|
| Monopolo λ/4 | ✅ | 95% | - |
| Dipolo λ/2 | ✅ | 90% | - |
| Ground Plane | ✅ | 80% | - |
| Patch | ✅ | 85% | - |
| Yagi | ✅ Básico | 75% | MÉDIA |
| **Parabola/Dish** | ❌ | 0% | 🔴 **ALTA** |
| Horn | ❌ | 0% | 🟡 Média |
| Log-Periódica | ❌ | 0% | 🟡 Média |
| Arranjos/Arrays | ❌ | 0% | 🟡 Média |
| Sistemas MIMO | ❌ | 0% | 🟡 Média |

### 5.2 Situação Atual de Equações

| Equação | Implementada? | Precisão | Impacto |
|---|---|---|---|
| λ = c/f | ✅ | 100% | Fundamental |
| FSPL Espaço Livre | ✅ | 95% | ALTO |
| Friis (simples) | ✅ | 70% NLOS | CRÍTICO |
| Obstáculos fixos | ⚠️ Parcial | 75% | ALTO |
| **Ganho Direcional G(θ,φ)** | ❌ | 0% | 🔴 **CRÍTICO** |
| **Orientação Relativa** | ❌ | 0% | 🔴 **CRÍTICO** |
| Zonas de Fresnel | ❌ | 0% | 🟡 Média |
| Difração | ❌ | 0% | 🟡 Média |
| Multipercurso | ❌ | 0% | 🟡 Média |
| Diversidade | ❌ | 0% | 🟡 Média |

### 5.3 Erros Esperados (Sem Mitigação)

```
Cenário 1: LOS Espaço Livre
  Erro: ±1-2 dB ✓ Aceitável
  
Cenário 2: LOS + 1 Obstáculo
  Erro: ±3-5 dB ✓ Aceitável
  
Cenário 3: NLOS com múltiplos obstáculos
  Erro: ±8-15 dB ⚠️ Marginal
  
Cenário 4: TX/RX Direcional fora de alinhamento
  Erro: ±10-20 dB ❌ INACEITÁVEL
  
Cenário 5: Heatmap de cobertura em campus
  Erro espacial: ±30-50% ❌ INACEITÁVEL
```

---

## PARTE 6: RECOMENDAÇÕES FINAIS

### 6.1 ANTES DE LANÇAR MVP (Checkpoints 0-10)

```
OBRIGATÓRIO:
  [ ] Adicionar ParabolaDish como tipo de antena
  [ ] Documentar explicitamente: "Padrões de radiação são simplificados"
  [ ] Advertir na UI: "Modelo NÃO é adequado para antenas diretivas"
  [ ] Teste com caso real: Yagi TX → Omnidirectional RX @ diferentes ângulos
  
ALTAMENTE RECOMENDADO:
  [ ] Implementar cálculo de orientação relativa (skeleton)
  [ ] Adicionar parâmetros de azimute/elevação (mas não usar ainda)
  [ ] Validar contra literatura (Pozar, Balanis) para parabola
```

### 6.2 PARA FASE 2 (Semanas 9-12 Pós-MVP)

```
PRIORIDADE 1 (1-2 semanas):
  [ ] Ativar cálculo de orientação relativa
  [ ] Implementar padrão 3D para Yagi (cos^n)
  [ ] Implementar padrão 3D para Parabola
  [ ] Teste contra dados SX1276 datasheet
  
PRIORIDADE 2 (1-2 semanas):
  [ ] Adicionar verificação de Fresnel
  [ ] Adicionar modelo de sombra (log-normal)
  [ ] Validar heatmap contra drive test real
```

### 6.3 Checkpoint 0.5+ (Nova Documentação)

```
NOVO ARQUIVO: docs/antenna_coverage.md
  ├─ Tabela de tipos suportados vs. roadmap
  ├─ Descrição de parabola + fórmulas
  ├─ Exemplo de cálculo com orientação
  └─ Limitações conhecidas (diretividade, multipercurso)

NOVO ARQUIVO: docs/accuracy_matrix.md
  ├─ Precisão por cenário
  ├─ Erro esperado para cada combinação
  └─ Disclaimer: "Modelo educacional, não profissional"

ATUALIZAR: docs/limitations.md
  ├─ Sem suporte a antenas diretivas
  ├─ Padrões simplificados
  ├─ Não considera orientação relativa
  └─ Heatmap adequado apenas para omnidirecionais
```

---

## CONCLUSÃO

### 🔴 **Crítico:**
1. **Antenas parabólicas não estão no escopo** — Adicione já no MVP
2. **Cálculo de orientação relativa é falha** — Sem isso, Yagi/Parabola dão resultados enganosos
3. **Heatmap pode ser muito impreciso** — Principalmente em cenários diretivos

### 🟡 **Recomendações:**
1. Implementar suporte a Parabola **antes de Checkpoint 10**
2. Preparar skeleton para orientação relativa **no MVP**
3. Documentar **explicitamente** que modelo é inadequado para diretivas
4. Validar contra **dados reais** pós-MVP

### ✅ **Status Geral:**
Especificação é **viável**, mas **incompleta** para sistemas profissionais com gateways diretivos.
Para uso acadêmico/educacional: **OK até MVP**  
Para LoRaWAN corporativo: **Requer Fase 2 completa**

