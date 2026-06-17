# Site Selection — Método de Cálculo de Cobertura

## Objetivo

Avaliar quantos nós de campo conseguem se comunicar com um candidato a torre, dado um modelo de propagação.

---

## Modelo de propagação usado

**FSPL — Free Space Path Loss** (Perda no Espaço Livre).

Assumido em todos os candidatos nesta fase. Sem modelo de terreno.

```
FSPL (dB) = 20·log10(4π·d·f / c)
```

- `d` = distância geodésica (Haversine) entre candidato e nó de campo (m)
- `f` = frequência do cenário (Hz)
- `c` = 3×10⁸ m/s

---

## Cálculo de cobertura por candidato

Para cada par (candidato `k`, nó de campo `i`):

```
Rx_i (dBm) = P_tx + G_tx − L_tx − FSPL(d_ki, f) − L_rx_i + G_rx_i
margem_i   = Rx_i − sens_i
coberto_i  = (margem_i > 0)
```

Parâmetros da torre candidata (fixos nesta fase):
- `P_tx` = 20 dBm
- `G_tx` = 0 dBi
- `L_tx` = 0 dB

Parâmetros do nó de campo (`NodeSpec`):
- `G_rx_i` = ganho da antena associada (da biblioteca, 0 dBi se sem antena)
- `L_rx_i` = `cable_loss_db`
- `sens_i` = `rx_sensitivity_dbm`

Percentagem de cobertura:

```
coverage_pct = (Σ coberto_i) / N_nos × 100
```

---

## Semáforo de cobertura

| coverage_pct | Semáforo | Interpretação |
|---|---|---|
| ≥ 80% | Verde | Boa cobertura |
| 50–79% | Amarelo | Cobertura parcial |
| < 50% | Vermelho | Cobertura insuficiente |

---

## Como a altitude da torre entra no modelo

No FSPL puro, a altitude **não afeta** o cálculo de perda — apenas a distância horizontal (Haversine) e a frequência determinam o FSPL.

A altura `height_m` do candidato é armazenada e exibida como referência. No slider da UI, alterar a altura aciona um recálculo (`height_overrides`), mas o resultado numérico não muda com FSPL.

Com modelos mais avançados (Longley-Rice, Okumura-Hata), a altura da torre afeta significativamente:
- Longley-Rice: altura afeta o perfil de terreno e difração
- Okumura-Hata: `h_b` (altura da estação base) entra diretamente na fórmula de perda

Nesta fase, o slider é útil para:
- Registro e documentação do projeto
- Testes futuros quando os modelos com terreno forem integrados

---

## Ranking

Candidatos são ordenados por `coverage_pct` decrescente. O primeiro é o melhor candidato.

Em caso de empate exato, a ordem é determinada pela sequência de inserção.

---

## Height Override

`POST /site-selection` aceita `height_overrides: {candidate_id: new_height_m}`.

Permite recalcular com alturas diferentes sem modificar o cenário persistido — usado pelo slider da UI para feedback em tempo real.

---

## Limitações

- FSPL puro: sem terreno, sem vegetação, sem prédios
- Sem ray tracing
- Sem difração sobre obstáculos
- Parâmetros da torre candidata fixos: 20 dBm, 0 dBi, 0 dB cabo
- Sem otimização automática de posição — o sistema avalia apenas candidatos marcados pelo usuário
- `height_m` afeta resultado somente com modelos baseados em terreno (não implementados nesta fase)

---

## Referências

- ITU-R P.525-4 — *Calculation of free-space attenuation*
- Ver `docs/calculos/05-fspl.md` para derivação completa do FSPL
- Ver `docs/calculos/06-okumura-hata.md` e `07-longley-rice-itm.md` para modelos com terreno
