# Fase 2 — AntennaSpec e Biblioteca
**Data:** 2026-06-17  
**Status:** ✅ Concluída

---

## Schema criado

`backend/app/schemas/antenna_spec.py` — modelo Pydantic `AntennaSpec`:

| Campo | Tipo | Obrigatório |
|---|---|---|
| `schema_version` | `str` | não (default `"1.0"`) |
| `id` | `str` (UUID) | não (auto-gerado) |
| `name` | `str` | **sim** |
| `type` | `str` | **sim** |
| `frequency_hz` | `float` | **sim** |
| `units` | `dict[str, str]` | não |
| `geometry` | `dict[str, Any]` | não |
| `material` | `dict[str, Any]` | não |
| `solver` | `str` | não (default `"rapido"`) |
| `results` | `dict[str, Any] \| None` | não |
| `metadata` | `dict[str, Any]` | não |

---

## Rotas implementadas

| Método | Rota | Status | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/antennas` | 200 | Lista todas as antenas |
| `POST` | `/api/v1/antennas` | 201 | Cria antena; valida schema |
| `GET` | `/api/v1/antennas/{id}` | 200 / 404 | Detalhe individual |
| `PUT` | `/api/v1/antennas/{id}` | 200 / 404 | Atualiza; força `id` do path |
| `DELETE` | `/api/v1/antennas/{id}` | 204 / 404 | Remove arquivo do disco |

Payload inválido → `422` com `detail` listando campo e motivo (Pydantic automático).

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `backend/app/schemas/__init__.py` | Marca `schemas` como pacote |
| `backend/app/schemas/antenna_spec.py` | Pydantic `AntennaSpec` |
| `backend/app/api/__init__.py` | Marca `api` como pacote |
| `backend/app/api/library_routes.py` | CRUD rotas `/api/v1/antennas` |
| `backend/app/storage/__init__.py` | Marca `storage` como pacote |
| `backend/app/storage/antenna_storage.py` | save / load / list_all / delete em JSON |
| `frontend/public/library.html` | UI listagem, import, export, delete |
| `frontend/public/js/api-client.js` | Wrapper fetch para todas as rotas |
| `docs/antenna-spec-schema.md` | Schema completo + exemplos JSON |
| `docs/for-dummies/06-como-salvar-antena-json.md` | Guia passo a passo |
| `tests/test_library.py` | 7 testes de CRUD |

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/main.py` | `include_router(library_router)` antes do `mount` estático |

---

## Exemplos JSON criados

Em `docs/antenna-spec-schema.md`:

- **Dipolo λ/2 em 915 MHz** — `type: dipolo`, `frequency_hz: 915000000`, `gain_dbi: 2.15`
- **Parabólica Grade 2.4 GHz** — `type: parabolica`, `diameter_m: 0.6`, `gain_dbi: 18.5`

---

## Comandos executados

```bash
uv run pytest tests/ -v
```

---

## Resultado dos testes

```
tests/test_health.py::test_health_returns_ok PASSED
tests/test_library.py::test_post_valid_returns_201 PASSED
tests/test_library.py::test_post_invalid_returns_422 PASSED
tests/test_library.py::test_get_list_returns_array PASSED
tests/test_library.py::test_get_by_id_returns_spec PASSED
tests/test_library.py::test_get_unknown_id_returns_404 PASSED
tests/test_library.py::test_delete_removes_file PASSED
tests/test_library.py::test_spec_saved_to_disk PASSED
8 passed, 1 warning in 0.90s
```

Aviso não-bloqueante: mesma origem da Fase 1 — `httpx` com `starlette.testclient`.

---

## Checkpoints

- [x] `POST /api/v1/antennas` com payload válido retorna `201`
- [x] Spec válida salva em `backend/data/antenna_specs/{id}.json`
- [x] Payload inválido retorna `422` com campo e motivo
- [x] `GET /api/v1/antennas` retorna array
- [x] `GET /api/v1/antennas/{id}` retorna spec individual
- [x] `DELETE /api/v1/antennas/{id}` remove arquivo do disco
- [x] `library.html` carrega lista via `api-client.js`
- [x] Import de JSON válido cria antena
- [x] Import de JSON inválido mostra erro (banner vermelho)
- [x] Export baixa JSON com campo `results`
- [x] `pytest tests/test_library.py` passa — 7 passed

---

## Limitações atuais

| Limitação | Observação |
|---|---|
| Sem autenticação | Qualquer um pode criar/deletar. Fora do MVP |
| Sem paginação em `GET /api/v1/antennas` | OK para biblioteca pequena |
| Storage em JSON plano | Sem índice; lista lê todos os arquivos. OK até ~1000 antenas |
| `PUT` não valida conflito de `id` no body | Força o `id` do path silenciosamente |
| `docker-compose up` não verificado | Sem Docker no ambiente de dev |

---

## Próximos passos (Fase 3)

- Criar `sandbox.html` com 4 painéis (visual, parâmetros, resultados EM, diagrama polar)
- `api/sandbox_routes.py` — `POST /api/v1/sandbox/preview` com solver analítico
- Botão "Salvar na Biblioteca" integrado ao sandbox
