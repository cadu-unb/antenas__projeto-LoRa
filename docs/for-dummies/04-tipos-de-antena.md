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

## Resumo de uso no sistema

| Tipo | Solver Rápido | Solver Padrão/Preciso |
|---|---|---|
| Dipolo | Analítico (Balanis Eq. 4-79) | MoM (PyNEC) |
| Monopolo | Analítico | MoM (PyNEC) |
| Helicoidal | Analítico (Kraus) | MoM (modo axial PyNEC não suportado → analítico) |
| Parabólica | Analítico (abertura) | Abertura (G = η(πD/λ)²) |
