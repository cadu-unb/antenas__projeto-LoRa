# Tipos de antena

## Dipolo

Antena de referência universal. Dois braços lineares no mesmo eixo, alimentados no centro.

| Parâmetro | Valor típico |
|---|---|
| Comprimento | λ/2 (meia-onda) |
| Ganho | 2.15 dBi |
| Impedância | ~73 Ω (λ/2) |
| Padrão | Omnidirecional no plano azimutal |

**Quando usar:** gateway LoRa com cobertura 360° no plano horizontal. Padrão para calibração — todo valor de referência em antenas usa o dipolo λ/2.

**Limitação:** sem ganho direcional. Para enlaces ponto-a-ponto, a parabólica ou yagi é mais eficiente.

---

## Monopolo

Metade de um dipolo sobre plano de terra condutor. O plano espelha a haste, comportando-se como o segundo braço.

| Parâmetro | Valor típico |
|---|---|
| Comprimento | λ/4 |
| Ganho | 5.15 dBi (com GND perfeito) |
| Impedância | ~36.5 Ω |
| Padrão | Omnidirecional hemisférico |

**Quando usar:** nó de campo LoRa com plano de terra (caixa metálica, chão). Menor que o dipolo — útil em instalações compactas.

**Limitação:** exige plano de terra real para atingir 5.15 dBi. Sem GND adequado, o ganho cai.

---

## Helicoidal

Fio enrolado em espiral ao longo de um eixo. Dois modos de operação:

**Modo axial** (circunferência ≈ λ): irradiação ao longo do eixo, altamente direcional, polarização circular.

| Parâmetro | Valor típico |
|---|---|
| Ganho | ~14 dBi (N=10 espiras) |
| Circunferência | 0.75λ–1.33λ |
| Ângulo de passo | 12°–14° |

**Modo normal** (circunferência << λ): omnidirecional, comportamento similar ao dipolo.

**Quando usar:** modo axial para links LoRa direcionais em 915 MHz com cobertura de ~10 dBi sem refletor. Polarização circular reduz perda por orientação.

---

## Parabólica

Refletor côncavo que concentra a energia em um foco, onde fica o elemento irradiador (feed).

| Parâmetro | Valor típico |
|---|---|
| Diâmetro | 0.6–1.8 m |
| Eficiência | 0.55–0.75 |
| Ganho (0.6 m, 2.4 GHz) | ~24 dBi |
| Ganho (1.2 m, 2.4 GHz) | ~30 dBi |

**Fórmula:** G = η × (πD/λ)²

**Quando usar:** links ponto-a-ponto de longa distância. Para LoRa 915 MHz com parabólica de 0.9 m: ~9 dBi de ganho.

**Limitação:** feixe estreito — alinhamento preciso necessário. Solver: aproximação de abertura (não MoM).

---

---

## PCB Compact

Antena integrada diretamente ao PCB do módulo LoRa. Sem componentes externos — menor custo e tamanho.

| Parâmetro | Valor típico |
|---|---|
| Ganho | 0–2 dBi (dependente da frequência) |
| HPBW | ~120° |
| Polarização | linear |
| Impedância | 50 Ω |
| Eficiência | ~85% |

**Ganho por faixa no solver:**
- < 800 MHz → 0 dBi
- 800–1000 MHz → 1.5 dBi
- > 1000 MHz → 2.0 dBi

**Quando usar:** protótipos, nós de campo com espaço restrito, baixo custo. Não requer geometria extra.

**Limitação:** ganho baixo; irregular em elevação. Para links longos ou com obstáculos, ganho insuficiente.

---

## Commercial Omni 6dBi

Antena colinear comercial vertical. Referência prática para gateways LoRa — especialmente o kit E220-900T22D.

| Parâmetro | Valor típico |
|---|---|
| Ganho | 6 dBi (fixo nominal) |
| HPBW elevação | ~35° (feixe mais estreito que dipolo) |
| Polarização | linear vertical |
| Impedância | 50 Ω |
| Eficiência | ~95% |

**Quando usar:** gateway LoRa que precisa de cobertura 360° no azimute com ganho maior que o dipolo simples. Melhor custo-benefício para gateway multi-sensor.

**Limitação:** feixe de elevação estreito (~35°) penaliza nós muito próximos ou em ângulo de elevação alto. Não requer geometria extra.

---

## Resumo de uso no sistema

O sistema aceita 6 tipos. Todos têm solver analítico rápido disponível.

| Tipo Python | Equivalente MATLAB | Solver Rápido | Solver Padrão/Preciso |
|---|---|---|---|
| `dipolo` | `Dipole_HalfWave` | Analítico (Balanis) | MoM (PyNEC) |
| `monopolo` | `Monopole_GroundPlane` | Analítico | MoM (PyNEC) |
| `helicoidal` | `Helical_Axial` | Analítico (Kraus) | MoM axial → analítico |
| `parabolica` | `Parabolic_Dish` | Abertura (G = η(πD/λ)²) | Abertura |
| `pcb_compact` | `PCB_Compact` | Por faixa de frequência | Por faixa de frequência |
| `commercial_omni_6dbi` | `Commercial_Omni_6dBi` | Colinear analítico | Colinear analítico |
