# Modos de Simulação

O sistema oferece quatro modos de simulação, com diferentes trade-offs entre velocidade e precisão.

## Tabela de modos

| Modo | Solver | Tempo esperado | RAM típica | Fase MVP | Quando usar |
|---|---|---|---|---|---|
| **Rápido** | Analítico (fórmulas fechadas) | < 2 s | < 100 MB | Fase 3 ✓ | Exploração rápida, dipolo/monopolo padrão, comparação de parâmetros |
| **Padrão** | MoM via PyNEC / Abertura | 10 s – 5 min | 1–4 GB | Fase 6 | Geometrias reais, validação de projeto, uso cotidiano |
| **Preciso** | MoM refinado (malha densa) | 5–30 min | 4–25 GB | Fase 6 | Validação final antes de fabricação, geometrias complexas |
| **Experimental** | A definir (placeholder) | — | — | Pós-MVP | Novos modelos em avaliação; resultados não garantidos |

## Limites computacionais

Todos os modos respeitam os limites definidos em `backend/app/config.py`:

- `MAX_RAM_GB = 25` — simulação abortada se uso de RAM ultrapassar este valor
- `MAX_RUNTIME_MIN = 30` — simulação abortada se tempo ultrapassar este valor

Quando abortada, o sistema retorna:
- `FAILED_MEMORY_LIMIT` — acompanhado de log parcial e sugestão de reduzir malha
- `FAILED_TIME_LIMIT` — acompanhado de log parcial e sugestão de usar modo menos preciso

## Disponibilidade por tipo de antena

| Tipo | Rápido | Padrão | Preciso |
|---|---|---|---|
| Dipolo | ✓ analítico | ✓ MoM | ✓ MoM refinado |
| Monopolo | ✓ analítico | ✓ MoM | ✓ MoM refinado |
| Helicoidal | ✓ analítico (aprox.) | ✓ MoM | ✓ MoM refinado |
| Parabólica | ✓ analítico (apertura) | ✓ Abertura | ✓ Abertura refinada |

## Notas

- Modo Rápido é o único disponível no MVP (Fases 1–4).
- Modos Padrão e Preciso requerem PyNEC instalado (Fase 6). Se ausente, sistema faz fallback automático para Rápido e registra aviso no log.
- Modo Experimental não tem solver definido. Habilitado apenas em ambiente de desenvolvimento.
- Ray Tracing está fora do MVP e fora desta tabela. Gancho arquitetural reservado em `backend/app/solvers/ray_tracing_solver.py`.
