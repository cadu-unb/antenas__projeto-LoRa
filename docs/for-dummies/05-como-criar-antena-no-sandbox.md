# Como criar uma antena no Sandbox

## O que é o Sandbox?

Ambiente para projetar e simular antenas antes de salvar na biblioteca. Modo Rápido (analítico, < 2 s) está disponível. Modos Padrão e Preciso (MoM/PyNEC) chegam na Fase 6.

## Layout — 4 painéis

| Painel | Conteúdo |
|---|---|
| **1 — Visual físico** | SVG geométrico da antena; atualiza em tempo real |
| **2 — Parâmetros** | Tipo, frequência, geometria, solver |
| **3 — Resultado EM** | Ganho (dBi), Impedância (Ω), SWR, Eficiência (%) |
| **4 — Irradiação** | Diagrama polar 2D — plano E |

## Passo a passo

1. Abra `http://localhost:8000/sandbox.html`
2. Escolha o tipo de antena: `dipolo`, `monopolo`, `helicoidal`, `parabolica`, `pcb_compact`, `commercial_omni_6dbi`
3. Ajuste a frequência em MHz
4. Edite os parâmetros de geometria — o SVG atualiza ao digitar
5. Clique **Calcular Preview** → resultado aparece nos Painéis 3 e 4
6. Se satisfeito, clique **Salvar na Biblioteca** → spec + resultados são gravados

## Tipos disponíveis e parâmetros

### Dipolo
- `length_m` — comprimento total. Valor ótimo: λ/2 = c/(2f)
- `diameter_mm` — diâmetro do condutor

### Monopolo
- `height_m` — altura da haste. Valor ótimo: λ/4
- `ground_diameter_m` — diâmetro do plano terra

### Helicoidal (modo axial)
- `turns` — número de espiras (recomendado: ≥ 3)
- `circumference_m` — circunferência de espira (ótimo: ≈ λ)
- `pitch_angle_deg` — ângulo de passo (típico: 12–14°)

> Se circunferência estiver fora de 0.75λ–1.33λ, aviso aparece no Painel 3 e solver usa modo normal.

### Parabólica
- `diameter_m` — diâmetro do refletor
- `focal_length_m` — distância focal (típico: D × 0.367)

### PCB Compact
- Nenhum parâmetro de geometria obrigatório — o solver usa a frequência para calcular o ganho por faixa automaticamente.

### Commercial Omni 6dBi
- Nenhum parâmetro de geometria obrigatório — ganho fixo nominal 6 dBi, padrão colinear aplicado pelo solver.

## Ganho direcional e orientação de antena

Para antenas direcionais (`helicoidal`, `parabolica`), o sistema aplica ganho angular real via `pattern_g()` quando o nó tem `azimuth_deg` definido no Link Planner. Sem `azimuth_deg`, o solver usa o ganho máximo (boresight).

O sistema usa coordenadas ENU 3D para calcular geometria de enlace (azimute e elevação reais entre os nós). Perdas extras por enlace (`cable_loss_db`, `extra_loss_db`, `fading_margin_db`, `polarization_loss_db`) ficam em `NodeSpec`, não em `AntennaSpec`.

## Interpretar os resultados

| Métrica | O que significa | Referência |
|---|---|---|
| Ganho (dBi) | Ganho sobre isotrópica | Dipolo λ/2: 2.15 dBi |
| Impedância (Ω) | Resistência de entrada | Alvo: ~50 Ω para SWR baixo |
| SWR | Standing Wave Ratio (relativo a 50 Ω) | Bom: < 1.5 |
| Eficiência (%) | Potência irradiada / potência de entrada | Cobre em 915 MHz: ~98% |

## Limitações do modo Rápido

- Fórmulas analíticas simplificadas — não substituem simulação EM completa
- Dipolo/Monopolo: modelo unidimensional; ignora efeitos de extremidade e acoplamento mútuo
- Helicoidal: fórmula empírica de Kraus; válida para 3–20 espiras em modo axial
- Parabólica: aproximação de abertura com η=0.55; ignora padrão do feed e spillover
- Sem efeitos de proximidade com estruturas físicas
- Solvers MoM e Longley-Rice chegam na Fase 6

## Fluxo de salvar na biblioteca

Ao clicar "Salvar na Biblioteca", o sistema envia:

```json
{
  "name": "<nome do campo>",
  "type": "<tipo selecionado>",
  "frequency_hz": "<frequência em Hz>",
  "geometry": { ... },
  "solver": "rapido",
  "results": {
    "gain_dbi": ...,
    "impedance_ohm": ...,
    "swr": ...,
    "efficiency_pct": ...,
    "radiation_pattern": "..."
  }
}
```

A antena salva aparece em `library.html` imediatamente (sem reload de página).
