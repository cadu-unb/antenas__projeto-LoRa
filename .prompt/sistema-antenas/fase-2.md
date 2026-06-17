# Prompt — Sistema de Antenas LoRa — Fase 2

## Objetivo

Implementar `AntennaSpec` e biblioteca de antenas com CRUD JSON, import, export e testes.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_1.md`, se existir

## Tarefas

1. Criar `backend/app/schemas/antenna_spec.py`.
2. Definir model Pydantic `AntennaSpec` com:
   - `schema_version`
   - `id`
   - `name`
   - `type`
   - `frequency_hz`
   - `units`
   - `geometry`
   - `material`
   - `solver`
   - `results`
   - `metadata`
3. Criar `backend/app/api/library_routes.py`.
4. Implementar rotas:

```text
GET    /api/v1/antennas
POST   /api/v1/antennas
GET    /api/v1/antennas/{id}
PUT    /api/v1/antennas/{id}
DELETE /api/v1/antennas/{id}
```

5. Salvar arquivos em:

```text
backend/data/antenna_specs/{id}.json
```

6. Integrar rotas no `main.py`.
7. Criar `frontend/public/library.html`.
8. Criar `frontend/public/js/api-client.js`.
9. Implementar no frontend:
   - listar antenas;
   - importar JSON;
   - exportar JSON;
   - deletar antena;
   - exibir erro para JSON inválido.
10. Criar `docs/antenna-spec-schema.md` com exemplos reais:
    - dipolo;
    - parabólica.
11. Criar `docs/for-dummies/06-como-salvar-antena-json.md`.
12. Criar `tests/test_library.py`.

## Checkpoints obrigatórios

- [ ] `POST /api/v1/antennas` com payload válido retorna `201`
- [ ] Spec válida é salva em `backend/data/antenna_specs/{id}.json`
- [ ] Payload inválido retorna `422` com campo e motivo
- [ ] `GET /api/v1/antennas` retorna array
- [ ] `GET /api/v1/antennas/{id}` retorna spec individual
- [ ] `DELETE /api/v1/antennas/{id}` remove arquivo do disco
- [ ] `library.html` carrega lista via `api-client.js`
- [ ] Import de JSON válido cria antena
- [ ] Import de JSON inválido mostra erro
- [ ] Export baixa JSON com campo `results`
- [ ] `pytest tests/test_library.py` passa

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_2.md
```

O relatório deve conter:

- schema criado;
- rotas implementadas;
- arquivos criados;
- exemplos JSON criados;
- comandos executados;
- resultado dos testes;
- checkpoints marcados;
- limitações atuais.

## Regra final

Não implemente sandbox visual nesta fase.
