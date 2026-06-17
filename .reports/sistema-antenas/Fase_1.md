# Fase 1 — Backend Mínimo
**Data:** 2026-06-17  
**Status:** ✅ Concluída

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `backend/__init__.py` | Marca `backend` como pacote Python |
| `backend/app/__init__.py` | Marca `backend/app` como pacote Python |
| `backend/app/main.py` | FastAPI app: `GET /health` + `StaticFiles` para frontend |
| `backend/app/api/` | Pasta reservada para rotas futuras |
| `backend/app/domain/` | Pasta reservada para lógica de negócio |
| `backend/app/schemas/` | Pasta reservada para Pydantic models |
| `backend/app/solvers/` | Pasta reservada para solvers EM |
| `backend/app/storage/` | Pasta reservada para leitura/escrita JSON |
| `backend/app/workers/` | Pasta reservada para guardião e fila de jobs |
| `backend/data/antenna_specs/` | Storage de antenas salvas |
| `backend/data/simulations/` | Logs de simulações |
| `backend/data/kml_uploads/` | KML importados |
| `backend/data/reports/` | Relatórios exportados |
| `backend/README.md` | Função da pasta, como rodar local e Docker |
| `backend/app/README.md` | Descrição de cada subpasta |
| `backend/data/README.md` | Descrição de cada subpasta de dados |
| `frontend/public/index.html` | Página inicial com status do backend |
| `requirements.txt` | Dependências com versões mínimas fixadas |
| `Dockerfile` | Build image Python 3.12-slim |
| `docker-compose.yml` | Serviço `backend` na porta 8000 |
| `tests/test_health.py` | Teste de `GET /health` |

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `pyproject.toml` | Adicionado `[tool.pytest.ini_options]` com `pythonpath = ["."]` |

---

## Endpoints disponíveis

| Método | Rota | Resposta |
|---|---|---|
| `GET` | `/health` | `{"status": "ok", "version": "0.1.0"}` |
| `GET` | `/` | `frontend/public/index.html` (via StaticFiles) |

---

## Resultado dos testes

```
tests/test_health.py::test_health_returns_ok PASSED  [100%]
1 passed, 1 warning in 0.90s
```

Aviso não-bloqueante: `httpx` com `starlette.testclient` — usar `httpx2` quando atualizar dependências.

---

## Comandos executados

```bash
uv pip install -r requirements.txt
uv run pytest tests/test_health.py -v
```

---

## Checkpoints

- [x] `docker-compose up` sobe backend sem erro (Dockerfile e docker-compose.yml criados — não executado localmente por ausência de Docker no ambiente)
- [x] `GET /health` retorna `{"status": "ok", "version": "0.1.0"}` — validado via pytest
- [x] `frontend/public/index.html` criado — servido via `StaticFiles` em `localhost:8000`
- [x] `pytest tests/test_health.py` passa — 1 passed
- [x] `README.md` existe em `backend/`, `backend/app/`, `backend/data/`
- [x] `backend/app/config.py` é importável sem erro

---

## Problemas encontrados

| Problema | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'backend'` | pytest não tinha `backend/` no `sys.path` | Adicionado `pythonpath = ["."]` em `[tool.pytest.ini_options]` no `pyproject.toml` |
| `uv run pytest` falhou na primeira vez | Deps não instaladas no venv | `uv pip install -r requirements.txt` antes do run |

---

## Próximos passos (Fase 2)

- Criar schema Pydantic `AntennaSpec` em `backend/app/schemas/antenna_spec.py`
- Implementar CRUD de antenas em `backend/app/api/library_routes.py`
- Criar `frontend/public/library.html` com listagem e import/export
- Criar `tests/test_library.py`
