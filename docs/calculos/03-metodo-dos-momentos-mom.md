# Método dos Momentos (MoM)

## Conceito

Método numérico para resolver equações integrais de campo EM. Discretiza a distribuição de corrente na antena em N segmentos e resolve o sistema linear resultante para obter correntes em cada segmento.

Resultado: impedância de entrada, padrão de irradiação, ganho e eficiência.

## Parâmetros de entrada

| Parâmetro | Tipo | Descrição |
|---|---|---|
| Tipo de antena | string | `dipolo`, `monopolo`, `helicoidal` |
| Frequência | Hz | Frequência de operação |
| `length_m` (dipolo) | metros | Comprimento total. Padrão: λ/2 |
| `height_m` (monopolo) | metros | Altura da haste. Padrão: λ/4 |
| `turns` (helicoidal) | int | Número de espiras |
| `circumference_m` | metros | Circunferência de uma espira (modo axial: ≈ λ) |
| `pitch_angle_deg` | graus | Ângulo de passo. Típico: 14° |

## Saída

| Campo | Unidade | Descrição |
|---|---|---|
| `gain_dbi` | dBi | Ganho máximo sobre isotrópico |
| `impedance_ohm` | Ω | Impedância de entrada (parte real) |
| `swr` | — | Standing Wave Ratio (referência: Z₀ = 50 Ω) |
| `efficiency_pct` | % | Eficiência de irradiação |
| `solver_used` | string | `mom_pynec` ou `mom_analitico` (fallback) |

## Valores de referência

| Antena | Frequência | Ganho esperado | Fonte |
|---|---|---|---|
| Dipolo λ/2 | qualquer | 2.15 dBi | Balanis, Cap. 4 |
| Monopolo λ/4 | qualquer | 5.15 dBi | Balanis, Cap. 4 |
| Helicoidal axial (N=10, C≈λ, α=14°) | qualquer | ≈ 14 dBi | Kraus, 1949 |

## Implementação

Usa `PyNEC` (Python wrapper para NEC-2) — dependência opcional.

**Instalação:**
- Linux / WSL2: `pip install PyNEC` ou `uv pip install PyNEC`
- Windows nativo: requer MSVC ou MinGW instalado antes. Ver `README.md`.

Se `PyNEC` não estiver disponível:
- Fallback analítico ativado automaticamente
- Campo `warning` no resultado indica que PyNEC não foi usado
- Ganho calculado por aproximação de Balanis (Eq. 4-79 para dipolo)
- `solver_used` retorna `"mom_analitico"` em vez de `"mom_pynec"`

## Limitações

- Sem modelagem de plano de terra real (monopolo assume GND perfeito)
- Helicoidal: modo normal calculado analiticamente; modo axial por NEC se PyNEC disponível
- Não aplicável a antenas parabólicas (usar `ApertureSolver`)
- Materiais com perdas: eficiência fixa em 98% no fallback analítico

## Referências

- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016.
- G. J. Burke & A. J. Poggio, *NEC: Method of Moments*, LLNL, 1981.
- J. D. Kraus, "Helical Beam Antenna", *Electronics*, vol. 20, pp. 109–111, 1947.
