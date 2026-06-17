# Fase 8 — Documentação e Polimento
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Docs completadas

### docs/for-dummies/ — 13/13 arquivos

| Arquivo | Status |
|---|---|
| `01-o-que-e-este-sistema.md` | ✅ Criado |
| `02-como-instalar-e-rodar.md` | ✅ Criado |
| `03-como-usar-o-sandbox.md` | ✅ Criado |
| `04-tipos-de-antena.md` | ✅ Criado |
| `05-como-criar-antena-no-sandbox.md` | ✅ Já existia (completo) |
| `06-como-salvar-antena-json.md` | ✅ Já existia (completo) |
| `07-como-usar-a-biblioteca.md` | ✅ Criado |
| `08-como-importar-kml.md` | ✅ Já existia (completo) |
| `09-como-montar-enlace.md` | ✅ Já existia (completo) |
| `10-como-rodar-simulacao.md` | ✅ Já existia (completo) |
| `11-como-entender-resultados.md` | ✅ Já existia (completo) |
| `12-erros-comuns-e-como-resolver.md` | ✅ Já existia (completo) |
| `13-glossario.md` | ✅ Criado |

### docs/calculos/ — 10/10 arquivos

| Arquivo | Status |
|---|---|
| `01-dipolo-analitico.md` | ✅ Criado |
| `02-monopolo-analitico.md` | ✅ Criado |
| `03-metodo-dos-momentos-mom.md` | ✅ Já existia (completo + atualizado na Fase 6.5) |
| `04-parabolica-aproximacao-abertura.md` | ✅ Já existia (completo) |
| `05-fspl.md` | ✅ Criado |
| `06-okumura-hata.md` | ✅ Já existia (completo) |
| `07-longley-rice-itm.md` | ✅ Já existia (completo) |
| `08-link-budget.md` | ✅ Criado |
| `09-limites-computacionais.md` | ✅ Já existia (completo) |
| `10-referencias-tecnicas.md` | ✅ Criado |

---

## READMEs revisados

| Arquivo | Status |
|---|---|
| `README.md` (raiz) | ✅ Atualizado com escopo negativo e seção de docs |
| `frontend/README.md` | ✅ Criado |
| `backend/README.md` | ✅ Já existia (completo) |
| `backend/app/README.md` | ✅ Já existia |
| `backend/data/README.md` | ✅ Já existia |
| `docs/for-dummies/README.md` | ✅ Já existia (índice dos 13 guias) |
| `docs/calculos/README.md` | ✅ Já existia (índice dos 10 métodos) |

---

## Escopo negativo criado

Seção **"Fora do MVP / Escopo Negativo"** adicionada ao `README.md` raiz:

- Sem detecção automática de obstáculos por imagem
- Sem Ray Tracing urbano completo sem modelo 3D
- Sem MoM para parabólicas grandes (usa abertura)
- Sem KML nível 2 (modelo 3D extrudado)

---

## Mensagens de erro da UI — revisão

### Backend (sandbox_routes.py / job_routes.py)

| Situação | Mensagem atual | Instrução acionável? |
|---|---|---|
| Modo rápido via `/simulate` | "Modo rápido é síncrono. Use POST /api/v1/sandbox/preview." | ✅ Sim |
| Job não encontrado | "Job não encontrado." | ✅ Sim |
| Job já finalizado (cancelar) | "Job não encontrado ou já finalizado." | ✅ Sim |
| Helicoidal fora do modo axial | Warning no resultado: "Circunferência fora da faixa..." | ✅ Sim |
| Tipo sem solver | Warning: "Tipo sem solver analítico. Fixture fixa retornada." | ✅ Sim |

### Frontend (job-monitor.js)

| Situação | Mensagem atual | Instrução acionável? |
|---|---|---|
| Job 404 durante polling | "Job não encontrado no servidor." | ✅ Sim |
| Erro genérico | `job.error ?? "Erro desconhecido."` | ⚠️ Genérico — depende do campo `error` do backend |

Nota: erros genéricos propagam a mensagem do campo `error` do backend, que é sempre acionável para `FAILED_MEMORY_LIMIT` e `FAILED_TIME_LIMIT`. Para exceções inesperadas, a mensagem pode ser técnica — limitação conhecida, documentada em `12-erros-comuns-e-como-resolver.md`.

---

## Teste end-to-end

Fluxo testado via suite de testes automatizados (113 passed, 1 skipped):

| Etapa | Resultado |
|---|---|
| Criar antena (Sandbox preview) | ✅ `POST /api/v1/sandbox/preview` → 200 |
| Salvar na Biblioteca | ✅ `POST /api/v1/antennas` → 201 |
| Listar Biblioteca | ✅ `GET /api/v1/antennas` → array |
| Montar enlace (criar cenário) | ✅ `POST /api/v1/scenarios` → 201 |
| Simular enlace | ✅ `POST /api/v1/scenarios/{id}/calculate` → margem em dB |
| Enfileirar job (Padrão/Preciso) | ✅ `POST /api/v1/sandbox/simulate` → job_id imediato |
| Consultar status job | ✅ `GET /api/v1/jobs/{id}` → status DONE |
| Cancelar job | ✅ `DELETE /api/v1/jobs/{id}` → 204 |
| Exportar cenário | ✅ `GET /api/v1/scenarios/{id}` → LinkScenario JSON |

---

## Referências técnicas criadas

`docs/calculos/10-referencias-tecnicas.md` — 16 referências verificáveis:
- Burke & Poggio, NEC-2 (1981)
- Longley & Rice, ITM (1968)
- Hata, IEEE TVT (1980)
- Friis, FSPL (1946)
- ITU-R P.525-4 (2019)
- LoRa Alliance Regional Parameters (2018)
- Balanis, Stutzman, Kraus, Boithias, Molisch

---

## Checkpoints

- [x] Todos 13 arquivos de `docs/for-dummies/` preenchidos
- [x] Todos 10 arquivos de `docs/calculos/` com conceito, parâmetros, limitações e referência
- [x] `docs/calculos/10-referencias-tecnicas.md` com referências verificáveis (16 entradas)
- [x] Toda pasta relevante tem `README.md` não-stub (`frontend/` criado, outras já existiam)
- [x] `README.md` raiz documenta escopo negativo (4 itens)
- [x] Fluxo end-to-end funcional — suite 113 passed, 1 skipped
- [x] Mensagens de erro com instrução acionável — erros estruturados ✅; erro genérico propagado do backend

---

## Pendências / limitações conhecidas

- Mensagem de erro genérica no frontend (`"Erro desconhecido."`) ocorre apenas para exceções não mapeadas no backend — campo `error` carrega a mensagem técnica real. Documentado em `12-erros-comuns-e-como-resolver.md`.
- Teste end-to-end manual (browser) não realizado — validado via testes automatizados.
