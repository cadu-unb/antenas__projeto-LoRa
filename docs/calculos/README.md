# docs/calculos

Documentação técnica dos métodos de cálculo usados no sistema. Cada arquivo cobre: conceito, parâmetros de entrada/saída, limitações e referência técnica.

## Métodos planejados

| Arquivo | Método | Solver | Fase |
|---|---|---|---|
| `01-dipolo-analitico.md` | Dipolo λ/2 analítico: ganho, impedância, SWR | Rápido | 3 |
| `02-monopolo-analitico.md` | Monopolo λ/4 analítico com plano de terra | Rápido | 3 |
| `03-metodo-dos-momentos-mom.md` | MoM via PyNEC: malha de correntes, matriz de impedância | Padrão | 6 |
| `04-parabolica-aproximacao-abertura.md` | Aproximação de abertura para refletor parabólico | Padrão | 6 |
| `05-fspl.md` | Free-Space Path Loss: fórmula, faixa válida, limitações | Rápido | 4 |
| `06-okumura-hata.md` | Okumura-Hata: perda em área urbana/rural (150–1500 MHz) | Padrão | 6 |
| `07-longley-rice-itm.md` | Longley-Rice ITM: terreno irregular, variabilidade | Padrão | 6 |
| `08-link-budget.md` | Link budget: EIRP, FSPL, margem, limiar de recepção | Rápido | 4 |
| `09-limites-computacionais.md` | MAX_RAM_GB, MAX_RUNTIME_MIN, guardião de recursos | — | 6 |
| `10-referencias-tecnicas.md` | Referências bibliográficas verificáveis | — | 8 |
