# Plano de Implementação — Melhorias de Antenas

Referência principal: `.reports/melhorias-2/quadro-antenas.md`.

Objetivo: alinhar o sistema Python atual aos campos e critérios do material externo MATLAB, sem quebrar compatibilidade com os cenários e antenas já salvos.

## Escopo

Este plano cobre:

- Correções de documentação desatualizada.
- Evolução do `AntennaSpec` para guardar campos físicos explícitos.
- Uso consistente de ganho máximo, HPBW, polarização, modelo de padrão e scores.
- Ajustes nos solvers e rankings para reduzir inferência espalhada por tipo.
- Testes e validações para os 6 tipos atuais.

Não cobre:

- Reescrever o sistema de simulação inteiro.
- Implementar visualização 3D completa dos diagramas.
- Migrar todos os arquivos antigos em `backend/data/scenarios/` manualmente.

## Estado Atual Confirmado

Tipos aceitos hoje no código:

| Tipo Python | Equivalente externo |
|---|---|
| `dipolo` | `Dipole_HalfWave` |
| `monopolo` | `Monopole_GroundPlane` |
| `helicoidal` | `Helical_Axial` |
| `parabolica` | `Parabolic_Dish` |
| `pcb_compact` | `PCB_Compact` |
| `commercial_omni_6dbi` | `Commercial_Omni_6dBi` |

Campos externos que devem virar campos opcionais em `AntennaSpec`:

| Campo novo | Tipo sugerido | Default |
|---|---|---|
| `gmax_dbi` | `float \| None` | `None` |
| `hpbw_deg` | `float \| None` | `None` |
| `polarization` | `str \| None` | `None` |
| `is_directional` | `bool \| None` | `None` |
| `pattern_model` | `str \| None` | `None` |
| `practicality_score` | `float \| None` | `None` |
| `multi_direction_score` | `float \| None` | `None` |
| `notes` | `str` | `""` |

## Fase 1 — Correções Documentais

Prioridade: alta.

Arquivos:

- `docs/antenna-spec-schema.md`
- `docs/for-dummies/04-tipos-de-antena.md`
- `docs/for-dummies/05-como-criar-antena-no-sandbox.md`
- `.reports/externo/resume.md`, se for mantido como relatório vivo

Tarefas:

1. Atualizar a lista de tipos aceitos para incluir `pcb_compact` e `commercial_omni_6dbi`.
2. Corrigir a afirmação antiga de que Python possui apenas 4 tipos.
3. Documentar que o código atual tem ENU 3D, ganho direcional via `pattern_g()` quando `azimuth_deg` é definido e perdas extras via `NodeSpec`.
4. Incluir quadro curto com equivalência Python x MATLAB externo.
5. Explicar que `geometry` continua livre, mas haverá campos físicos opcionais no topo de `AntennaSpec`.

Critérios de aceite:

- A documentação não contradiz o registry atual de solvers.
- Os 6 tipos aparecem nos guias e no schema documentado.
- O texto diferencia claramente campos de antena (`AntennaSpec`) e campos de nó/enlace (`NodeSpec`).

Validação:

- `rg -n "dipolo.*monopolo.*helicoidal.*parabolica|pcb_compact|commercial_omni_6dbi" docs`
- Revisão manual dos exemplos JSON.

## Fase 2 — Evolução Compatível do Schema

Prioridade: alta.

Arquivos:

- `backend/app/schemas/antenna_spec.py`
- `tests/test_library.py`
- `tests/test_new_antenna_solvers.py`
- `docs/antenna-spec-schema.md`

Tarefas:

1. Adicionar campos opcionais ao `AntennaSpec`:
   - `gmax_dbi`
   - `hpbw_deg`
   - `polarization`
   - `is_directional`
   - `pattern_model`
   - `practicality_score`
   - `multi_direction_score`
   - `notes`
2. Bumpar `schema_version` para `"2.0"` em specs que contiverem ao menos um dos novos campos; manter `"1.0"` em specs antigas não modificadas. O backfill da Fase 8 usa essa distinção.
3. Manter defaults retrocompatíveis para JSONs antigos.
4. Aceitar specs antigas sem esses campos.
5. Atualizar exemplos de criação de antena com os novos campos.
6. Validar ranges mínimos sem ser rígido demais:
   - scores entre `0` e `10`, se preenchidos;
   - `hpbw_deg > 0`, se preenchido;
   - `gmax_dbi` numérico, se preenchido.

Critérios de aceite:

- Antenas antigas continuam carregando.
- Novas antenas podem ser salvas com campos externos explícitos.
- Os campos continuam opcionais.

Validação:

- `uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py`

## Fase 3 — Presets Canônicos dos 6 Tipos

Prioridade: alta.

Arquivos:

- Novo arquivo sugerido: `backend/app/domain/antenna_presets.py`
- `backend/app/api/sandbox_routes.py`
- `backend/app/solvers/__init__.py`
- `tests/test_new_antenna_solvers.py`

Tarefas:

1. Criar um registry único com presets canônicos por tipo:

| Tipo | `gmax_dbi` | `hpbw_deg` | `polarization` | `is_directional` | `pattern_model` | `practicality_score` | `multi_direction_score` |
|---|---:|---:|---|---|---|---:|---:|
| `dipolo` | `2.15` | `78` | `linear vertical` | `false` | `dipole` | `8` | `9` |
| `monopolo` | `5.15` | `55` | `linear vertical` | `false` | `monopole` | `7` | `8` |
| `helicoidal` | `11` | `55` | `circular/elliptical` | `true` | `helical` | `5` | `3` |
| `parabolica` | `20` | `18` | `feed-dependent` | `true` | `parabolic` | `2` | `1` |
| `pcb_compact` | `1` | `120` | `linear` | `false` | `pcb` | `10` | `7` |
| `commercial_omni_6dbi` | `6` | `35` | `linear vertical` | `false` | `omni_colinear` | `9` | `8` |

2. Usar presets para preencher campos ausentes em specs antigas.
3. Evitar duplicar valores em `sandbox_routes.py`, solvers e comparison.
4. Expor helper como `apply_antenna_defaults(spec)`.

Nota — `pattern_model` dos presets segue convenção curta (`dipole`, `monopole`, `helical`, `parabolic`, `pcb`, `omni_colinear`), separada do `type` Python. Permite ao solver identificar modelo angular sem depender do nome comercial.

Critérios de aceite:

- Cada tipo tem um preset único e testado.
- `AntennaSpec` antigo recebe defaults em runtime sem modificar o arquivo em disco.
- O registry de solver continua separado do registry de metadados físicos.

Validação:

- Teste unitário para cada preset.
- Teste de spec mínima: `AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)`.

## Fase 4 — Uso dos Campos no Cálculo de Ganho

Prioridade: média-alta.

Arquivos:

- `backend/app/domain/link_budget.py`
- `backend/app/solvers/mom_solver.py`
- `backend/app/solvers/aperture_solver.py`
- `backend/app/solvers/pcb_solver.py`
- `backend/app/solvers/colinear_solver.py`
- `tests/test_phase3_link_budget.py`
- `tests/test_solvers.py`

Tarefas:

1. Fazer `_effective_gain()` priorizar campos explícitos:
   - `pattern_model`, quando existir;
   - `gmax_dbi`, quando o solver permitir override;
   - `hpbw_deg`, quando o padrão usa largura de feixe.
2. Padronizar o significado de `theta_deg` nos solvers:
   - off-boresight para diretivas;
   - ângulo polar/elevacional para omnis, conforme implementação atual.
3. Permitir que `hpbw_deg` da spec sobrescreva constantes internas:
   - colinear: hoje `20°`;
   - parabólica: hoje `70lambda/D`;
   - helicoidal: hoje não usa HPBW explícito.
4. Corrigir divergências documentadas:

   **`commercial_omni_6dbi` HPBW:**
   - MATLAB externo usa `35°`; Python usa `20°` no `ColinearSolver`.
   - Decisão: usar `hpbw_deg=35` do preset/spec; manter `20°` só como fallback interno legado.

   **`pcb_compact` Gmax:**
   - MATLAB externo usa `Gmax_dBi=1` (valor nominal fixo).
   - Python usa ganho dependente de frequência: `0 dBi (<800 MHz)`, `1.5 dBi (800–1000 MHz)`, `2.0 dBi (>1000 MHz)`.
   - Decisão recomendada: o solver continua com ganho por faixa (mais preciso para link budget); o preset guarda `gmax_dbi=1` como referência nominal para comparação com MATLAB. A Fase 4 deve fazer `_effective_gain()` ignorar `gmax_dbi` do preset para `pcb_compact` e manter o cálculo por faixa, a não ser que o usuário forneça `gmax_dbi` explícito na spec.

Critérios de aceite:

- Alterar `hpbw_deg` muda o ganho angular de diretivas/colinear.
- Specs sem novos campos mantêm resultado próximo ao comportamento atual.
- Testes cobrem antena apontada e desalinhada.

Validação:

- `uv run pytest tests/test_phase3_link_budget.py tests/test_solvers.py tests/test_new_antenna_solvers.py`

## Fase 5 — Polarização Automática

Prioridade: média.

Arquivos:

- `backend/app/domain/link_budget.py`
- `backend/app/domain/comparison.py`
- `tests/test_link_budget.py`
- `tests/test_comparison.py`

Tarefas:

1. Criar função `estimate_polarization_loss(tx_ant, rx_ant)`.
2. Reusar regra aproximada do MATLAB externo:
   - circular/elíptica vs linear: `3 dB`;
   - lineares incompatíveis: penalidade pequena configurável;
   - iguais/desconhecidas: `0 dB`.
3. Somar perda automática com `NodeSpec.polarization_loss_db`.
4. Retornar a perda total em campo novo `LinkResult.polarization_loss_db` (float, default `0.0`). Não somar em `extra_loss_db` para manter rastreabilidade separada. API e serialização devem expor esse campo.

Critérios de aceite:

- Helicoidal circular contra dipolo linear recebe penalidade.
- Duas verticais lineares não recebem penalidade.
- Perda manual ainda funciona.

Validação:

- `uv run pytest tests/test_link_budget.py tests/test_comparison.py`

## Fase 6 — Ranking com Scores de Antena

Depende de: Fase 3 (campos `is_directional`, `multi_direction_score` e `practicality_score` disponíveis via preset/spec).

Prioridade: média.

Arquivos:

- `backend/app/domain/comparison.py`
- `tests/test_comparison.py`

Tarefas:

1. Remover inferência fixa `_DIRECTIONAL` quando `is_directional` existir.
2. Usar `multi_direction_score` no cálculo de robustez, quando disponível.
3. Usar `practicality_score` no ranking agregado.
4. Manter fallback atual para specs antigas.
5. Deixar explícito que gateway com antena muito diretiva deve ser penalizado em cenários multi-azimute.

Critérios de aceite:

- `Commercial_Omni_6dBi` tende a ranquear melhor em gateway multi-azimute que parabólica.
- Parabólica apontada pode continuar boa em P2P, mas sofre em cenário multi-sensor.
- Resultados antigos não quebram quando os scores faltam.

Validação:

- `uv run pytest tests/test_comparison.py`

## Fase 7 — API, Biblioteca e Frontend

Prioridade: média.

Arquivos:

- `backend/app/api/library_routes.py`
- `backend/app/storage/antenna_storage.py`
- `frontend/public/sandbox.html`
- `frontend/public/library.html`
- `frontend/public/js/api-client.js`
- `docs/for-dummies/06-como-salvar-antena-json.md`

Tarefas:

1. Garantir que CRUD de antenas preserva os novos campos.
2. Mostrar campos físicos no detalhe da biblioteca.
3. No sandbox, preencher valores sugeridos por tipo:
   - ganho máximo;
   - HPBW;
   - polarização;
   - modelo de padrão;
   - direcionalidade.
4. Evitar UI pesada: campos avançados podem ficar recolhidos.
5. Atualizar export/import JSON.

Critérios de aceite:

- Criar uma antena `commercial_omni_6dbi` pela UI salva `hpbw_deg`, `polarization` e scores.
- Importar JSON antigo continua funcionando.
- Exportar JSON novo mantém os campos.

Validação:

- Testes de API existentes.
- Teste manual mínimo descrito:
  1. Criar `commercial_omni_6dbi` no sandbox → verificar que `hpbw_deg=35` e `polarization="linear vertical"` aparecem pré-preenchidos.
  2. Salvar e reabrir da biblioteca → campos persistidos.
  3. Exportar como JSON → campos presentes.
  4. Importar JSON antigo (sem novos campos) → carrega sem erro.

## Fase 8 — Compatibilidade e Migração Leve

Prioridade: média-baixa.

Arquivos:

- `backend/app/storage/antenna_storage.py`
- Novo script opcional: `scripts/backfill_antenna_fields.py`
- `backend/data/README.md`

Tarefas:

1. Não migrar automaticamente arquivos antigos ao ler, para evitar churn.
2. Criar script opcional de backfill para antenas salvas.
3. O script deve:
   - ler specs antigas;
   - aplicar presets por `type`;
   - preservar `metadata`, `results` e `geometry` (sem sobrescrever parâmetros geométricos definidos pelo usuário);
   - escrever somente com flag explícita.
4. Documentar que cenários antigos seguem válidos.

Critérios de aceite:

- Rodar a aplicação não regrava arquivos antigos.
- Backfill é explícito e reversível via git.

Validação:

- Teste em diretório temporário.

## Fase 9 — Testes de Regressão Integrados

Prioridade: alta antes de encerrar.

Comandos:

```powershell
uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py tests/test_phase3_link_budget.py tests/test_link_budget.py tests/test_comparison.py
uv run pytest
```

Casos mínimos a cobrir:

| Caso | Resultado esperado |
|---|---|
| Antena antiga sem campos novos | Carrega e calcula |
| `pcb_compact` em 915 MHz | Ganho = `1.5 dBi` (cálculo por faixa, não sobrescrito pelo preset `gmax_dbi=1`) |
| `pcb_compact` com `gmax_dbi=1` explícito na spec | Ganho override = `1.0 dBi` usado no link budget |
| `commercial_omni_6dbi` com `hpbw_deg=35` | Padrão angular usa esse HPBW |
| Helicoidal apontada | Margem maior |
| Helicoidal desalinhada | Margem menor |
| Parabólica em cenário multi-sensor | Penalizada no ranking multi-direção |
| Polarização circular vs linear | Perda automática aplicada |
| Export/import de antena nova | Campos preservados |

## Ordem Recomendada de Execução

1. Fase 1: documentação.
2. Fase 2: schema opcional.
3. Fase 3: presets canônicos.
4. Fase 4: ganho angular com campos explícitos.
5. Fase 5: polarização automática.
6. Fase 6: ranking com scores.
7. Fase 7: UI/API.
8. Fase 8: backfill opcional.
9. Fase 9: regressão completa.

## Riscos e Cuidados

| Risco | Mitigação |
|---|---|
| Quebrar JSONs antigos | Campos sempre opcionais; presets em runtime |
| Mudar margem de enlace inesperadamente | Manter fallbacks atuais quando campos novos ausentes |
| Duplicar defaults em vários arquivos | Criar registry único de presets |
| Confundir HPBW externo com cálculo geométrico | Definir prioridade: spec explícita > preset > cálculo interno |
| Penalizar errado antenas omni | Usar `is_directional` e `multi_direction_score`, não só nome do tipo |
| Regravar massa de dados em `backend/data` | Backfill apenas via script explícito |

## Entregável Final Esperado

Ao final, o projeto deve ter:

- `AntennaSpec` compatível com os campos do MATLAB externo.
- 6 presets canônicos alinhados com `.reports/externo/`.
- Documentação atualizada para os 6 tipos.
- Cálculo de enlace usando campos explícitos quando disponíveis.
- Ranking que considera robustez multidirecional e praticidade.
- Testes cobrindo compatibilidade antiga e novos campos.
