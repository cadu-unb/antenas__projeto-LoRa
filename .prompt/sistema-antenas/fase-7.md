# Prompt — Sistema de Antenas LoRa — Fase 7

## Objetivo

Implementar fila de jobs para simulações pesadas, com status, progresso, cancelamento e logs.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_6.md`, se existir

## Tarefas

1. Criar `backend/app/workers/job_queue.py`.
2. Usar `asyncio.Queue` como primeira implementação.
3. Documentar Celery apenas como alternativa futura, se necessário.
4. Criar `backend/app/api/job_routes.py`.
5. Implementar rotas:

```text
GET    /api/v1/jobs
GET    /api/v1/jobs/{id}
DELETE /api/v1/jobs/{id}
```

6. Estados válidos:
   - `PENDING`
   - `RUNNING`
   - `DONE`
   - `FAILED_MEMORY_LIMIT`
   - `FAILED_TIME_LIMIT`
   - `CANCELLED`
7. Salvar logs em:

```text
backend/data/simulations/{job_id}/log.jsonl
```

8. Integrar fila no sandbox:
   - "Simular (Padrão)";
   - "Simular (Preciso)".
9. Criar `frontend/public/js/job-monitor.js`.
10. Implementar polling a cada 2 segundos.
11. Mostrar:
    - progress bar;
    - status;
    - resultado ao finalizar;
    - erro claro ao falhar.
12. Criar docs:
    - `docs/for-dummies/10-como-rodar-simulacao.md`
    - `docs/for-dummies/11-como-entender-resultados.md`
    - `docs/for-dummies/12-erros-comuns-e-como-resolver.md`

## Checkpoints obrigatórios

- [ ] Simulação pesada retorna `job_id` imediatamente
- [ ] Request HTTP não trava a UI
- [ ] `GET /api/v1/jobs/{id}` retorna status válido
- [ ] Frontend mostra progresso com polling de 2 segundos
- [ ] Job `DONE` mostra resultado no sandbox
- [ ] Job `FAILED_*` mostra mensagem clara e sugestão de ação
- [ ] `DELETE /api/v1/jobs/{id}` cancela job real
- [ ] Log parcial persiste em jobs cancelados

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_7.md
```

O relatório deve conter:

- fila criada;
- rotas criadas;
- estados implementados;
- logs gerados;
- integração frontend;
- comandos executados;
- checkpoints marcados;
- limitações conhecidas.

## Regra final

Não troque para Celery sem justificar no relatório.
