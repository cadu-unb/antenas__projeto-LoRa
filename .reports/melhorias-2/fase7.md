# Report — Melhorias 2 — Fase 7

**Data:** 2026-06-22

## Mudanças na API e Storage

### `backend/app/api/library_routes.py`

Sem alterações necessárias. Rotas já usam `AntennaSpec` como request/response model via Pydantic. Todos os campos físicos opcionais (`gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional`, `pattern_model`, `practicality_score`, `multi_direction_score`, `notes`) são preservados automaticamente em todas as operações CRUD.

### `backend/app/storage/antenna_storage.py`

Sem alterações necessárias. `model_dump_json(indent=2)` serializa todos os campos (incluindo nulos). `model_validate_json` reconstrói com validação — campos ausentes ficam como `None`. Compatibilidade com JSONs antigos mantida.

## Mudanças no Frontend

### `frontend/public/sandbox.html`

1. **Tipos adicionados ao dropdown**: `pcb_compact` e `commercial_omni_6dbi`

2. **SVG visuais** para os dois tipos:
   - `pcb_compact`: placa PCB com traço de antena L e chip SoC central
   - `commercial_omni_6dbi`: bastão vertical colinear com divisores de slot

3. **Pattern3D** para os dois tipos:
   - `pcb_compact`: padrão quasi-omni (reutiliza geometria dipolo com label próprio)
   - `commercial_omni_6dbi`: lóbulos horizontais largos (colinear de alta eficiência)

4. **GEO_FIELDS** `[]` para ambos: solvers são determinísticos por frequência, sem geometria configurável. UI mostra note "Sem parâmetros geométricos configuráveis".

5. **Seção `<details>` "Campos Físicos"** (colapsável):
   - Campos: `gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional` (select), `pattern_model`, `practicality_score`, `multi_direction_score`
   - Posicionada após os campos de geometria — não polui o fluxo principal

6. **`PHYSICAL_PRESETS` (JS)**: dict espelho de `ANTENNA_PRESETS` do backend. Sem roundtrip de rede.

7. **`fillPhysicalFields(type)`**: chamada ao trocar tipo e no init. Preenche campos físicos com preset. Usuário pode editar livremente.

8. **`getPhysicalFields()`**: lê campos do DOM, retorna objeto com nulls para vazios. `is_directional` usa select tri-state (`"" / "true" / "false"` → `null / true / false`).

9. **Save handler**: `...getPhysicalFields()` incluído no spec enviado à API. Campos null → `Optional[T] = None` no Pydantic.

### `frontend/public/library.html`

1. **Nova coluna "Física"** entre Solver e Resultados.
2. Função `physicalBadges(spec)`: mostra HPBW, polarização e "direcional" como badges. Retorna "—" se nenhum campo físico presente.
3. `colspan` nas mensagens de estado ajustado para 7.

### `frontend/public/js/api-client.js`

Sem alterações. `createAntenna(spec)` e `getAntenna(id)` já passam o objeto completo.

## Documentação

### `docs/for-dummies/06-como-salvar-antena-json.md`

Reescrito. Adicionado:
- Tabela de campos físicos opcionais com tipos e descrições
- Tabela de valores preset por tipo (todos os 6 tipos)
- Exemplo JSON com campos físicos explícitos
- Erros novos: `hpbw_deg <= 0`, score fora de 0–10
- Seção "Como salvar via sandbox" explicando o auto-preenchimento

## Teste Manual Mínimo (verificado)

| Passo | Resultado |
|---|---|
| Selecionar `commercial_omni_6dbi` no sandbox | `hpbw_deg=35`, `polarization="linear vertical"` preenchidos automaticamente |
| Selecionar `pcb_compact` | `hpbw_deg=120`, `polarization="linear"`, `is_directional="false"` |
| Campos físicos colapsáveis | Seção não expande por padrão; layout limpo |
| `POST /api/v1/antennas` com JSON antigo (sem campos físicos) | `201 Created`, campos null, schema_version `"1.0"` |
| `POST` com `hpbw_deg` + `polarization` | `201 Created`, campos persistidos, schema_version `"2.0"` |
| `GET /api/v1/antennas/{id}` | Campos físicos retornados no JSON |
| Export via biblioteca | JSON inclui campos físicos |

## Testes Automatizados

```powershell
uv run pytest tests/test_library.py -v
```
Resultado: **17 passed** (inclui `test_physical_fields_preserved_on_save_and_load`, `test_schema_version_bumped_to_2_when_physical_fields_present`, `test_old_spec_without_physical_fields_loads`).

```powershell
uv run pytest
```
Resultado: **323 passed, 1 skipped, 1 warning** (regressão zero, mesmo total que Fase 6).

## Pendências e Riscos

| Item | Detalhe |
|---|---|
| `getPhysicalFields()` sempre envia null fields | Pydantic aceita null para Optional — comportamento correto. Se no futuro quiser excluir nulls do JSON salvo, usar `model_dump(exclude_none=True)` no storage. |
| Seção física colapsada por padrão | Usuário tem que expandir para ver/editar. Alternativa seria abrir para tipos que têm preset. Trade-off: manter UI limpa por padrão. |
| `pcb_compact` sem geometria no sandbox | Solver ignora geometry para este tipo. Seção física é o principal ponto de customização. |
| biblioteca não mostra scores | Coluna "Física" exibe HPBW + polarização + direcional. Scores omitidos para não poluir. Visíveis no JSON exportado. |
