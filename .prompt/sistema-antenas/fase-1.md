# Prompt — Sistema de Antenas LoRa — Fase 1

## Objetivo

Criar backend mínimo com FastAPI, rota `/health`, frontend estático servido pelo backend, teste básico e Docker.

Sem lógica de negócio nesta fase.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_0.md`, se existir

## Tarefas

1. Criar estrutura:

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── domain/
│   ├── schemas/
│   ├── solvers/
│   ├── storage/
│   └── workers/
└── data/
    ├── antenna_specs/
    ├── simulations/
    ├── kml_uploads/
    └── reports/
```

2. Criar `backend/app/main.py`.
3. Implementar `GET /health` retornando:

```json
{"status": "ok", "version": "0.1.0"}
```

4. Servir `frontend/public/` via FastAPI `StaticFiles`.
5. Criar `frontend/public/index.html` mínimo.
6. Criar `requirements.txt` com versões fixas ou compatíveis:
   - `fastapi`
   - `uvicorn`
   - `pydantic>=2`
   - `pytest`
   - `httpx`
7. Criar `docker-compose.yml` com serviço `backend`.
8. Criar `README.md` em:
   - `backend/`
   - `backend/app/`
   - `backend/data/`
9. Criar `tests/test_health.py`.

## Checkpoints obrigatórios

- [ ] `docker-compose up` sobe backend sem erro
- [ ] `GET /health` retorna `{"status": "ok", "version": "0.1.0"}`
- [ ] `frontend/public/index.html` é servido em `localhost:8000`
- [ ] `pytest tests/test_health.py` passa
- [ ] `README.md` existe em `backend/`, `backend/app/`, `backend/data/`
- [ ] `backend/app/config.py` é importável sem erro

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_1.md
```

O relatório deve conter:

- arquivos criados;
- comandos executados;
- resultado dos testes;
- endpoints disponíveis;
- checkpoints marcados;
- problemas encontrados;
- próximos passos recomendados.

## Regra final

Não implemente CRUD, sandbox ou link budget nesta fase.
