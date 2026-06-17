# Fase 3 — Sandbox Rápido
**Data:** 2026-06-17  
**Status:** ✅ Concluída

---

## Telas criadas

### `frontend/public/sandbox.html`

Layout 4 painéis em CSS Grid (2×2):

| Painel | Conteúdo |
|---|---|
| 1 — Visual físico | SVG inline por tipo; atualiza em tempo real ao editar parâmetros |
| 2 — Parâmetros | Seletor de tipo, frequência, geometria dinâmica, badges de solver |
| 3 — Resultado EM | Métricas: ganho (dBi), impedância (Ω), SWR, eficiência (%), padrão de radiação |
| 4 — Irradiação | Canvas 2D — diagrama polar (plano E); graticule + curva + área preenchida |

SVG por tipo:
- Dipolo: dois braços horizontais escalados por comprimento/λ
- Monopolo: haste vertical + plano terra horizontal
- Helicoidal: espiral projetada em 2D com N espiras
- Parabólica: curva parabólica + ponto focal + distância focal

---

## Endpoint criado

### `POST /api/v1/sandbox/preview`

**Request:** `SandboxPreviewRequest`
- `type` (obrigatório), `frequency_hz` (obrigatório)
- `geometry`, `material`, `solver` (opcionais)
- `name` (opcional, default `"Antena"`)

**Response:** `PreviewResult`

| Campo | Tipo | Descrição |
|---|---|---|
| `gain_dbi` | float | Ganho em dBi |
| `impedance_ohm` | float | Resistência de entrada em Ω |
| `swr` | float | SWR relativo a 50 Ω |
| `efficiency_pct` | float | Eficiência em % |
| `radiation_pattern` | string | Descrição do padrão |
| `pattern_data` | list[PatternPoint] | 360 pontos (angle_deg, gain_linear) |
| `solver_used` | string | `"rapido"` |
| `is_fixture` | bool | True se tipo sem solver real |
| `warning` | string\|null | Aviso de condição fora do ideal |

---

## Comportamento do preview

### Dipolo
- F(θ) = [cos(kL/2·cos θ) - cos(kL/2)] / sin θ (Balanis)
- Ganho: 2.15 dBi em λ/2; cai fora da ressonância
- Impedância: ~73 Ω em ressonância; aproximação polinomial

### Monopolo
- λ/4 sobre plano perfeito: ganho 5.15 dBi, Z ≈ 36.5 Ω
- Mesmo padrão de elevação do dipolo (hemisfério superior)

### Helicoidal
- Modo axial (0.75λ < C < 1.33λ): fórmula de Kraus; ganho ≈ 15·N·(C/λ)²·sin(α) linear
- Modo normal: fallback para dipolo + aviso

### Parabólica
- Ganho por abertura: G = η·(πD/λ)², η = 0.55
- Beamwidth: 70·λ/D graus; padrão gaussiano

### Fixture (tipos desconhecidos)
- Valores fixos; `is_fixture: true`; warning no campo

---

## Integração com biblioteca

Botão "Salvar na Biblioteca":
1. Monta `AntennaSpec` com campos do formulário + `results` do último preview
2. Chama `POST /api/v1/antennas`
3. Mensagem de sucesso aparece com `id` truncado
4. Antena disponível imediatamente em `library.html`

Botão desabilitado até calcular preview.

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `backend/app/api/sandbox_routes.py` | Solvers analíticos + rota `/preview` |
| `frontend/public/sandbox.html` | UI 4 painéis completa |
| `docs/for-dummies/05-como-criar-antena-no-sandbox.md` | Guia de uso |
| `tests/test_sandbox.py` | 12 testes do preview |

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/main.py` | `include_router(sandbox_router)` |
| `frontend/public/js/api-client.js` | Adicionado `previewAntenna(req)` |

---

## Comandos executados

```bash
uv run pytest tests/test_sandbox.py -v
uv run pytest tests/ -v
```

---

## Resultado dos testes

```
tests/test_sandbox.py::test_preview_dipolo_returns_200 PASSED
tests/test_sandbox.py::test_preview_dipolo_fields PASSED
tests/test_sandbox.py::test_preview_dipolo_half_wave_gain PASSED
tests/test_sandbox.py::test_preview_dipolo_half_wave_impedance PASSED
tests/test_sandbox.py::test_preview_monopolo_gain_higher_than_dipolo PASSED
tests/test_sandbox.py::test_preview_helicoidal_axial_directional PASSED
tests/test_sandbox.py::test_preview_parabolica_high_gain PASSED
tests/test_sandbox.py::test_preview_unknown_type_returns_fixture PASSED
tests/test_sandbox.py::test_preview_missing_required_returns_422 PASSED
tests/test_sandbox.py::test_preview_responds_under_2s PASSED
tests/test_sandbox.py::test_preview_pattern_data_normalized PASSED
tests/test_sandbox.py::test_preview_swr_positive PASSED
12 passed, 1 warning in 1.01s

Total suite: 20 passed, 1 warning in 0.99s
```

---

## Checkpoints

- [x] Seleção de tipo muda SVG sem reload
- [x] Edição de parâmetro atualiza SVG em tempo real
- [x] `POST /api/v1/sandbox/preview` retorna em < 2 s (< 10 ms analítico)
- [x] Painel 3 exibe ganho (dBi), impedância (Ω), SWR, eficiência (%)
- [x] Painel 4 exibe diagrama polar 2D com Canvas
- [x] "Salvar na Biblioteca" grava spec com `results` preenchidos
- [x] Antena salva aparece em `library.html` sem reload de página
- [x] Input inválido (frequência ≤ 0) mostra erro antes de chamar API
- [x] `pytest tests/test_sandbox.py` passa — 12 passed

---

## Limitações dos solvers rápidos

| Tipo | Limitação |
|---|---|
| Dipolo | Modelo de fio fino; ignora acoplamento, efeitos de extremidade, alimentação balanceada |
| Monopolo | Assume plano terra infinito perfeito; plano real degrada ganho |
| Helicoidal | Fórmula empírica de Kraus; válida para 3–20 espiras; ignora perdas de substrato |
| Parabólica | η fixo em 0.55; ignora padrão de feed, spillover, obstrução do suporte focal |
| Todos | Sem efeitos de temperatura, corrosão, proximidade com estruturas |
| Todos | Sem validação de campo — resultados são estimativas de projeto inicial |

---

## Próximos passos (Fase 4)

- Schemas `NodeSpec`, `LinkSpec`, `LinkScenario`
- `api/link_routes.py` — criar cenário + calcular link budget
- FSPL, distância geodésica, margem de enlace
- `link-planner.html` — seleção de antenas da biblioteca, semáforo de viabilidade
