# Limites Computacionais

## Configuração ativa

Definidos em `backend/app/config.py`:

| Parâmetro | Valor | Descrição |
|---|---|---|
| `MAX_RAM_GB` | 25 GB | Limite de memória RAM do processo de simulação |
| `MAX_RUNTIME_MIN` | 30 min | Tempo máximo por simulação |

## Como funciona o guardião

`backend/app/workers/resource_guard.py` monitora dois recursos:

### Verificação de RAM

Antes de iniciar a simulação:
```python
guard.check_ram()  # levanta FAILED_MEMORY_LIMIT se RAM usada ≥ 25 GB
```

Usa `psutil.virtual_memory().used` para medir RAM em uso pelo sistema.

### Verificação de tempo

Durante a execução via `asyncio.wait_for`:
```python
await guard.run_guarded(coroutine)
```

Se a simulação demorar mais que `MAX_RUNTIME_MIN × 60` segundos, `asyncio.TimeoutError` é capturado e convertido em `ResourceLimitError`.

## Códigos de erro

| Código | Causa | Ação recomendada |
|---|---|---|
| `FAILED_MEMORY_LIMIT` | RAM usada ≥ 25 GB | Reduzir número de segmentos; fechar outras aplicações |
| `FAILED_TIME_LIMIT` | Tempo ≥ 30 min | Usar modo Padrão em vez de Preciso; reduzir geometria |

## Log de simulação

Cada simulação grava em `backend/data/simulations/{id}/log.jsonl`:

```jsonl
{"ts": 1234567890.0, "event": "START", "max_ram_gb": 25, "max_runtime_min": 30}
{"ts": 1234567891.5, "event": "DONE", "elapsed_min": 0.025}
```

Evento `FAILED_*` é gravado mesmo quando a simulação é abortada. Permite diagnóstico post-mortem sem perder contexto.

Eventos possíveis: `START`, `DONE`, `FAILED_MEMORY_LIMIT`, `FAILED_TIME_LIMIT`, `ERROR`.

## Modos de simulação e custo estimado

| Modo | Solver ativo | RAM típica | Tempo típico |
|---|---|---|---|
| Rápido | Analítico | < 1 MB | < 0.1 s |
| Padrão | MoM (PyNEC) | 10–500 MB | 1–30 s |
| Preciso | MoM completo | 500 MB–5 GB | 1–30 min |

> Nota: se PyNEC não disponível, todos os modos usam analítico. RAM e tempo permanecem baixos.

## Extensões futuras

- Cancelamento manual de job em andamento (Fase 7)
- Limite de RAM por job individual (além do sistema)
- Notificação via webhook quando job completa
- Fila com prioridade (jobs interativos vs. batch)
