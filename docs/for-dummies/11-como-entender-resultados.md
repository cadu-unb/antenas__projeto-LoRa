# Como entender os resultados de simulação

## Painel de resultados (Painel 3)

| Campo | Unidade | O que significa |
|---|---|---|
| Ganho | dBi | Ganho em relação a antena isotrópica. Dipolo λ/2 ≈ 2,15 dBi. |
| Impedância | Ω | Resistência de entrada. Ideal para coaxial 50 Ω: próximo de 50 Ω. |
| SWR | — | Standing Wave Ratio. SWR < 1,5 = boa adaptação. SWR > 3 = desperdício de potência. |
| Eficiência | % | Fração da potência irradiada vs. fornecida. |

## Diagrama polar (Painel 4)

Mostra como a antena irradia energia em 360° (plano E).

- **Lobo principal**: região de maior irradiação.
- **Lobos laterais**: irradiação indesejada fora do lobo principal (prejudica diretividade).
- Os anéis concêntricos representam –12 dB, –6 dB, –3 dB e 0 dB relativos ao máximo.

## Diferença entre modos

| Modo | Solver | Resultado |
|---|---|---|
| Rápido | Analítico (fórmulas fechadas) | Aproximação, instantâneo |
| Padrão | MoM via PyNEC (ou fallback analítico) | Mais preciso, alguns segundos |
| Preciso | MoM com maior resolução | Melhor para geometrias complexas |

> Se PyNEC não estiver instalado, os modos Padrão e Preciso usam o solver analítico automaticamente.
> O campo `solver_used` no resultado indica qual foi usado.

## Campo `warning`

Se aparecer uma caixa amarela de aviso, leia a mensagem — ela indica:
- Parâmetros fora da faixa ideal do modelo
- Fallback de solver ativo
- Fixture fixa retornada (tipo sem solver implementado)

## Salvar na Biblioteca

Após obter resultado (Rápido ou via job), clique **Salvar na Biblioteca**.
O spec + resultados são gravados em `backend/data/antenna_specs/{id}.json`.
