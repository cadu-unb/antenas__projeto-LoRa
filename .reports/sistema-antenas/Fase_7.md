# Fase 7 — Jobs e Simulações Pesadas
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Fila criada

`backend/app/workers/job_queue.py` — `JobQueue` com `asyncio.Queue`.

**Decisão: asyncio em vez de Celery.**
Celery resolve escala multi-processo/multi-máquina, mas exige Redis ou RabbitMQ como broker.
Para um MVP single-process sem infraestrutura extra, `asyncio.Queue` é suficiente e sem dependências adicionais.
Se a escala exigir múltiplos workers ou processos separados, migrar para Celery — a interface de `enqueue(coro_fn)` é compatível com a mudança.

**Mecanismo de worker:**
- Single worker coroutine iniciada no startup via `asyncio.create_task` (lifespan FastAPI).
- Jobs executados sequencialmente: um por vez.
- `coro_fn(set_progress)` — a coroutine do job recebe callback `set_progress(pct)`.
- `set_progress` levanta `asyncio.CancelledError` se `_cancel_requested=True`, interrompendo o job sem cancelar o worker.

---

## Rotas criadas

`backend/app/api/job_routes.py`:

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/jobs` | Lista todos os jobs (mais recente primeiro) |
| `GET` | `/api/v1/jobs/{id}` | Status, progresso, resultado e erro do job |
| `DELETE` | `/api/v1/jobs/{id}` | Cancela job (retorna 204) |

`backend/app/api/sandbox_routes.py` — novo endpoint:

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/sandbox/simulate` | Enfileira simulação Padrão/Preciso, retorna `job_id` imediatamente |

---

## Estados implementados

| Estado | Condição |
|---|---|
| `PENDING` | Job enfileirado, não iniciado |
| `RUNNING` | Worker processando |
| `DONE` | Simulação concluída com sucesso |
| `FAILED_MEMORY_LIMIT` | RAM >= 25 GB (via `ResourceGuard`) |
| `FAILED_TIME_LIMIT` | Tempo >= 30 min ou erro inesperado¹ |
| `CANCELLED` | Usuário solicitou cancelamento (flag + CancelledError) |

¹ Erros inesperados (exceções não-ResourceLimitError) são mapeados para `FAILED_TIME_LIMIT` com
mensagem descritiva no campo `error`. Limitação conhecida — não há estado genérico `FAILED` na spec.

---

## Logs gerados

Cada job herda o `ResourceGuard` da Fase 6. Logs gravados em:

```
backend/data/simulations/{job_id}/log.jsonl
```

Eventos: `START`, `DONE`, `FAILED_MEMORY_LIMIT`, `FAILED_TIME_LIMIT`, `ERROR`.
Log parcial persiste mesmo em jobs cancelados ou interrompidos.

---

## Integração frontend

`backend/app/api/sandbox_routes.py`:
- `POST /api/v1/sandbox/simulate` — recebe `SandboxPreviewRequest` com `solver=padrao|preciso`.
- Modo `rapido` rejeitado com HTTP 400 (usar `POST /preview`).
- Coroutine `_simulate_coro(req, set_progress)`: progress steps + `run_in_executor` para solver.

`frontend/public/js/job-monitor.js` — `JobMonitor`:
- Polling `GET /api/v1/jobs/{id}` a cada 2 segundos.
- Callbacks: `onProgress(pct, status)`, `onDone(result)`, `onFailed(status, msg)`, `onCancelled()`.

`frontend/public/sandbox.html`:
- Badges Padrão e Preciso habilitados (removido "— Fase 6").
- Botões **Simular (Padrão)** e **Simular (Preciso)** adicionados.
- Seção de job monitor com barra de progresso, status colorido e botão **✕ Cancelar**.
- Resultado exibido automaticamente no Painel 3 ao status `DONE`.
- Mensagem de erro com texto acionável ao status `FAILED_*`.

`frontend/public/js/api-client.js`:
- `simulateAntenna(req)` — POST `/sandbox/simulate`
- `listJobs()`, `getJob(id)`, `cancelJob(id)`

---

## Comandos executados

```bash
uv add pytest httpx fastapi pydantic uvicorn --dev
uv run python -m pytest tests/ -q
```

---

## Checkpoints

- [x] Simulação pesada retorna `job_id` imediatamente (não trava UI)
- [x] Request HTTP não trava a UI — job enfileirado, resposta imediata
- [x] `GET /api/v1/jobs/{id}` retorna status válido
- [x] Frontend mostra progresso com polling de 2 segundos
- [x] Job `DONE` mostra resultado no sandbox (via `showResults(job.result)`)
- [x] Job `FAILED_*` mostra mensagem clara e sugestão de ação
- [x] `DELETE /api/v1/jobs/{id}` cancela job real (flag + CancelledError em `set_progress`)
- [x] Log parcial persiste em jobs cancelados (herdado do `ResourceGuard`)

---

## Resultado dos testes

```
tests/test_jobs.py  — 15 passed
Suite completa      — 113 passed, 1 skipped, 2 warnings in 2.45s
```

---

## Limitações conhecidas

1. **Worker single-process:** jobs rodando em `asyncio.Queue` não escalam além de um processo.
   Migrar para Celery se múltiplos workers forem necessários.
2. **Erros inesperados → `FAILED_TIME_LIMIT`:** não há estado genérico `FAILED` na spec.
   O campo `error` contém a mensagem real do erro.
3. **Cancelamento cooperativo:** cancela ao próximo checkpoint `set_progress`, não imediatamente.
   Para solvers síncronos em `run_in_executor`, o thread continua até completar; o resultado é descartado.
4. **Jobs em memória:** reiniciar o servidor perde todos os jobs. Logs JSONL persistem.
