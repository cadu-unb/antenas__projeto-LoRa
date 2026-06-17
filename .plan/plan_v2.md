# Plano de Execução — Sistema de Antenas LoRa
> Revisado com base em `.reports/avaliacao-plan-v2.md`.  
> Objetos centrais: `AntennaSpec`, `NodeSpec`, `LinkScenario`.  
> Pasta de relatórios: `.reports/sistema-antenas/`.  
> Docs acessíveis: `docs/for-dummy/`.

---

## Escopo do MVP

MVP termina no checkpoint da **Fase 4**. Tudo a partir da Fase 5 é extensão funcional.

**MVP inclui:**
- Backend FastAPI com `/health`
- Schema `AntennaSpec` + CRUD em JSON
- Frontend estático servido pelo próprio FastAPI (sem Express)
- Sandbox analítico para dipolo (modo Rápido)
- Biblioteca de antenas (listar, salvar, importar, exportar)
- Link budget P2P simples (FSPL + margens)
- Documentação mínima por fase

**MVP não inclui:**
- MoM via PyNEC
- Longley-Rice completo
- Ray Tracing (fora do MVP — manter gancho arquitetural para futuro)
- Fila de jobs assíncrona avançada
- KML nível 1 com obstáculos físicos reais
- Modo Experimental
- Express como servidor separado

---

## Fase 0 — Convenções do Repositório

### Descrição
Fixar padrões antes de criar qualquer arquivo de código. Decisões tomadas agora evitam refatoração depois.

### Passos sugeridos
1. Confirmar stack: FastAPI + Pydantic v2 (backend), HTML/CSS/JS puro (frontend), FastAPI serve estático no MVP
2. Definir convenção de pastas: `.reports/`, `docs/for-dummy/`, `backend/`, `frontend/`, `.plan/`
3. Criar `docs/for-dummy/README.md` — stub com lista de arquivos planejados
4. Criar `docs/calculos/README.md` — stub com métodos planejados
5. Criar `.reports/sistema-antenas/` — pasta para relatórios de fase
6. Criar `docs/architecture.md` — diagrama dos três domínios (Sandbox / Library / Link Planner)
7. Criar `docs/simulation-modes.md` — tabela dos 4 modos e limites computacionais
8. Criar `backend/app/config.py` — configuração central: `MAX_RAM_GB = 25`, `MAX_RUNTIME_MIN = 30`

### Checkpoint
- [ ] Pasta `.reports/sistema-antenas/` existe
- [ ] Pasta `docs/for-dummy/` existe (não `for-dummies`)
- [ ] `docs/architecture.md` descreve os três domínios
- [ ] `backend/app/config.py` define `MAX_RAM_GB` e `MAX_RUNTIME_MIN`
- [ ] Nenhum arquivo criado fora das convenções definidas

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_0.md`

---

## Fase 1 — Backend Mínimo

### Descrição
Criar esqueleto funcional do backend. Sem lógica de negócio. Apenas FastAPI rodando, rota `/health`, estrutura de pastas, teste básico e Docker.

### Passos sugeridos
1. Criar estrutura de pastas:
   ```
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
2. `main.py` com `GET /health` → `{"status": "ok", "version": "0.1.0"}`
3. FastAPI serve frontend estático em `frontend/public/` via `StaticFiles`
4. Criar `docker-compose.yml` — apenas serviço `backend` nesta fase
5. `requirements.txt` com versões fixas: `fastapi`, `uvicorn`, `pydantic>=2`
6. Criar `README.md` nas pastas principais (`backend/`, `backend/app/`, `backend/data/`)
7. Criar `tests/test_health.py` — teste simples de `GET /health`

### Checkpoint
- [ ] `docker-compose up` sobe backend sem erro
- [ ] `GET /health` → `{"status": "ok", "version": "0.1.0"}`
- [ ] Frontend entrega `index.html` em `localhost:8000` (servido pelo FastAPI)
- [ ] `pytest tests/test_health.py` passa
- [ ] `README.md` existe em `backend/`, `backend/app/`, `backend/data/`
- [ ] `config.py` importável sem erro

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_1.md`

---

## Fase 2 — AntennaSpec e Biblioteca

### Descrição
Definir e implementar o contrato central `AntennaSpec`. CRUD de antenas em JSON. Frontend de biblioteca com listagem, import e export.

### Passos sugeridos
1. `schemas/antenna_spec.py` — Pydantic model completo:
   - `schema_version`, `id`, `name`, `type`, `frequency_hz`, `units`
   - `geometry`, `material`, `solver`, `results`, `metadata`
2. `api/library_routes.py`:
   - `GET    /api/v1/antennas` — lista
   - `POST   /api/v1/antennas` — cria (valida schema)
   - `GET    /api/v1/antennas/{id}` — detalhe
   - `PUT    /api/v1/antennas/{id}` — atualiza
   - `DELETE /api/v1/antennas/{id}` — remove
3. Storage: `backend/data/antenna_specs/{id}.json`
4. `frontend/public/library.html` — lista de antenas, botão import JSON, export, delete
5. `frontend/public/js/api-client.js` — wrapper fetch para todas rotas
6. Criar exemplos JSON reais em `docs/antenna-spec-schema.md` (mínimo 2 exemplos: dipolo e parabólica)
7. Escrever `docs/for-dummy/06-como-salvar-antena-json.md`
8. `tests/test_library.py` — testes: salvar, listar, rejeitar inválido

### Checkpoint
- [ ] `POST /api/v1/antennas` com payload válido → `201` + spec salva em disco
- [ ] `POST /api/v1/antennas` com payload inválido → `422` com campo e motivo
- [ ] `GET /api/v1/antennas` retorna array (vazio se sem antenas)
- [ ] `GET /api/v1/antennas/{id}` retorna spec individual
- [ ] `DELETE /api/v1/antennas/{id}` remove do disco
- [ ] Frontend `library.html` carrega lista via `api-client.js`
- [ ] Upload de JSON válido cria antena; JSON inválido mostra erro
- [ ] Export baixa `.json` com spec completa incluindo campo `results`
- [ ] `pytest tests/test_library.py` passa

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_2.md`

---

## Fase 3 — Sandbox Rápido

### Descrição
Interface de criação de antenas com 4 painéis. Modo Rápido (analítico, < 2 s) como único solver nesta fase. Solvers avançados entram na Fase 6. Usar dados fixos de teste para desenvolver UI antes de solver real.

### Passos sugeridos
1. `sandbox.html` — layout 4-painéis (CSS grid)
2. **Painel 1 — Visual físico:** SVG por tipo (dipolo: braços; monopolo: haste + plano; helicoidal: espiras; parabólica: refletor + foco)
3. **Painel 2 — Parâmetros:** formulário por tipo, blocos: frequência / geometria / material / alimentação / solver (seletor de modo — apenas Rápido habilitado)
4. `api/sandbox_routes.py` — `POST /api/v1/sandbox/preview`:
   - Aceita `AntennaSpec` parcial
   - Retorna resultados analíticos em modo Rápido
   - Retorna fixture fixa para tipos ainda sem solver real
5. **Painel 3 — Resultado EM:** ganho (dBi), impedância (Ω), SWR, eficiência (%)
6. **Painel 4 — Irradiação:** diagrama polar 2D com Canvas
7. Botão "Salvar na Biblioteca" → `POST /api/v1/antennas` com spec + results
8. `docs/for-dummy/05-como-criar-antena-no-sandbox.md`
9. `tests/test_sandbox.py` — testar preview endpoint com inputs válidos e inválidos

### Checkpoint
- [ ] Seleção de tipo muda SVG do Painel 1 sem reload
- [ ] Edição de parâmetro reflete no SVG em tempo real
- [ ] `POST /api/v1/sandbox/preview` retorna resultado em < 2 s
- [ ] Painel 3 exibe valores com unidades corretas (dBi, Ω, —)
- [ ] Diagrama polar no Painel 4 coerente por tipo
- [ ] "Salvar na Biblioteca" grava spec com `results` preenchidos
- [ ] Antena salva aparece em `library.html` sem reload de página
- [ ] Input inválido no formulário mostra erro antes de chamar API
- [ ] `pytest tests/test_sandbox.py` passa

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_3.md`

---

## Fase 4 — Link Budget P2P  *(fim do MVP)*

### Descrição
Módulo mínimo de planejamento de enlace. Dois nós, uma antena por nó, distância + FSPL + margem. Sem KML, sem mapa, sem topologias complexas. Base para extensão nas fases seguintes.

### Passos sugeridos
1. Definir schemas Pydantic: `NodeSpec`, `LinkSpec`, `LinkScenario` mínimos
2. `api/link_routes.py`:
   - `POST /api/v1/scenarios` — criar cenário
   - `GET  /api/v1/scenarios/{id}` — detalhe
   - `POST /api/v1/scenarios/{id}/calculate` — calcular link budget
3. Cálculos: distância geodésica entre coordenadas, azimute, elevação, FSPL, margem de enlace
4. `link-planner.html` — formulário de dois nós, seleção de antenas da biblioteca, resultado em tabela
5. Semáforo de viabilidade: verde (margem > 10 dB) / amarelo (0–10 dB) / vermelho (< 0 dB)
6. `docs/for-dummy/09-como-montar-enlace.md` (versão P2P simples)
7. `docs/link-planner-schema.md` — campos, tipos, exemplos de `NodeSpec` e `LinkScenario`
8. `tests/test_link_budget.py` — testar FSPL, distância, margem com valores fixos documentados

### Checkpoint
- [ ] `POST /api/v1/scenarios/{id}/calculate` retorna margem de enlace em dB
- [ ] Distância geodésica entre dois pontos GPS reais calculada corretamente (tolerância ±1%)
- [ ] FSPL calculado corretamente para frequência e distância conhecidas (tolerância ±0.5 dB)
- [ ] Semáforo exibe cor correta conforme margem calculada
- [ ] Nó aceita `AntennaSpec` da biblioteca (dropdown de antenas salvas)
- [ ] Cenário exportável como JSON (`LinkScenario` completo)
- [ ] `pytest tests/test_link_budget.py` passa com fixtures documentadas

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_4.md`

---

## Fase 5 — KML e Mapa

### Descrição
Import de KML para posicionar nós no mapa Leaflet. Nível 0 (pontos) obrigatório. Nível 1 (polígonos) renderiza no mapa mas **não aplica penalidade física ainda** — apenas visual de obstáculo.

### Passos sugeridos
1. `domain/kml/parser.py` — parser KML nível 0 (pontos + altitude) e nível 1 (polígonos)
2. `api/link_routes.py` — `POST /api/v1/scenarios/{id}/kml` — upload e parse
3. `link-planner.html` — integrar Leaflet, renderizar nós e polígonos importados
4. Associar antenas da biblioteca aos nós importados via interface
5. Modos de topologia básicos: P2P, cadeia, estrela (malha manual e gateway setorial são extensões)
6. `docs/for-dummy/08-como-importar-kml.md`
7. Atualizar `docs/for-dummy/09-como-montar-enlace.md` com fluxo KML

> **Nota:** polígonos KML nível 1 são renderizados no mapa como áreas de interesse.
> Penalidade de obstrução física (com altura, material, modelo de interseção) fica fora desta fase.
> Chamar de "obstáculo físico" só quando houver altura + material + modelo de perda configurado.

### Checkpoint
- [ ] KML de pontos importado → nós aparecem no mapa Leaflet com coordenadas corretas
- [ ] KML com polígonos → polígonos renderizados no mapa (apenas visual)
- [ ] Nó importado aceita `AntennaSpec` da biblioteca
- [ ] Link budget recalcular após importar KML produz mesmo resultado que P2P direto (sem obstáculos reais)
- [ ] Modos P2P, cadeia e estrela configuráveis na interface
- [ ] Parser KML retorna erro claro se arquivo malformado

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_5.md`

---

## Fase 6 — Solvers Avançados

### Descrição
Implementar solvers técnicos reais como plugins sobre a interface já existente. Criar interface de solver primeiro; depois conectar PyNEC e Longley-Rice. Guardião de recursos entra aqui (não antes).

### Passos sugeridos
1. Definir interface base `solvers/base_solver.py` — contrato: `solve(spec) → SolverResult`
2. `solvers/mom_solver.py` — MoM via PyNEC para dipolo, monopolo, helicoidal
   - Usar como plugin: fallback para analítico se PyNEC não disponível
3. `solvers/aperture_solver.py` — aproximação de abertura para parabólica
4. `solvers/okumura_hata.py` — perda de percurso empírica (150–1500 MHz)
5. `solvers/longley_rice.py` — perda em terreno irregular
6. `workers/resource_guard.py` — monitor RAM com `psutil` + timeout com `asyncio`:
   ```text
   se RAM >= MAX_RAM_GB → FAILED_MEMORY_LIMIT + log parcial
   se tempo >= MAX_RUNTIME_MIN → FAILED_TIME_LIMIT + log parcial
   ```
7. Integrar modos Padrão e Preciso no sandbox (seletor agora habilita além de Rápido)
8. `docs/calculos/03-metodo-dos-momentos-mom.md`
9. `docs/calculos/04-parabolica-aproximacao-abertura.md`
10. `docs/calculos/06-okumura-hata.md`
11. `docs/calculos/07-longley-rice-itm.md`
12. `docs/calculos/09-limites-computacionais.md`
13. `tests/test_solvers.py` — fixtures com inputs fixos e tolerâncias documentadas

> **Nota sobre PyNEC:** pode ser difícil instalar no Windows. Criar fallback explícito.
> Se `import PyNEC` falhar → solver usa analítico e registra aviso no log.

> **Ray Tracing:** fora desta fase e do MVP. Manter gancho arquitetural (`solvers/ray_tracing_solver.py` como stub).

### Checkpoint
- [ ] Interface `BaseSolver.solve()` importável e documentada
- [ ] Dipolo λ/2 em modo Padrão → ganho entre **1.8 dBi e 2.5 dBi** (cenário de referência documentado em `tests/test_solvers.py`)
- [ ] Parabólica usa `aperture_solver`, não MoM
- [ ] Simulação > 25 GB → `FAILED_MEMORY_LIMIT` + mensagem acionável na UI
- [ ] Simulação > 30 min → `FAILED_TIME_LIMIT` + mensagem acionável na UI
- [ ] Log parcial persiste em `backend/data/simulations/{id}/log.jsonl` mesmo em jobs abortados
- [ ] Se PyNEC não disponível → fallback analítico + aviso no log (não erro fatal)
- [ ] Okumura-Hata retorna perda em dB para frequência/distância/altura válidos (tolerância ±1 dB vs referência publicada)
- [ ] `pytest tests/test_solvers.py` passa com fixtures documentadas

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_6.md`

---

## Fase 7 — Jobs e Simulações Pesadas

### Descrição
Desacoplar simulações pesadas da request HTTP. Fila async, status polling, cancelamento, frontend de monitoramento.

### Passos sugeridos
1. `workers/job_queue.py` — fila com `asyncio.Queue` (Celery como alternativa se escala exigir — documentar decisão)
2. `api/job_routes.py`:
   - `GET    /api/v1/jobs` — lista jobs
   - `GET    /api/v1/jobs/{id}` — status + progresso
   - `DELETE /api/v1/jobs/{id}` — cancela job
3. Salvar logs em `backend/data/simulations/{job_id}/log.jsonl`
4. Integrar fila no sandbox: botões "Simular (Padrão)" e "Simular (Preciso)" → criam job → retornam `job_id`
5. `frontend/public/js/job-monitor.js` — polling 2 s, progress bar, resultado ao DONE, erro claro ao FAILED
6. `docs/for-dummy/10-como-rodar-simulacao.md`
7. `docs/for-dummy/11-como-entender-resultados.md`
8. `docs/for-dummy/12-erros-comuns-e-como-resolver.md`

### Checkpoint
- [ ] Simulação pesada retorna `job_id` imediatamente (não trava UI)
- [ ] `GET /api/v1/jobs/{id}` retorna `status` válido: `PENDING` / `RUNNING` / `DONE` / `FAILED_MEMORY_LIMIT` / `FAILED_TIME_LIMIT` / `CANCELLED`
- [ ] Frontend mostra progresso em tempo real (polling 2 s)
- [ ] Job `DONE` → resultado exibido no sandbox
- [ ] Job `FAILED_*` → mensagem clara + sugestão de ação
- [ ] Cancelamento via `DELETE` interrompe processo real
- [ ] Log parcial persiste mesmo em jobs cancelados

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_7.md`

---

## Fase 8 — Documentação e Polimento

### Descrição
Completar toda documentação. Refinar UX de erros. Validar fluxo end-to-end. Definir escopo negativo explícito no `README.md` raiz.

### Passos sugeridos
1. Completar todos 13 arquivos de `docs/for-dummy/`
2. Completar todos 10 arquivos de `docs/calculos/` — cada um com: conceito, parâmetros, limitações, referência técnica
3. `docs/calculos/10-referencias-tecnicas.md` — referências reais:
   - Burke & Poggio, *NEC: Method of Moments*
   - Longley & Rice, *Prediction of Tropospheric Radio Transmission Loss*
   - Hata, *IEEE TVT 1980*
   - ITU-R P.1410
4. Verificar `README.md` em toda pasta — preencher faltantes com: função, arquivos principais, editável ou gerado
5. `README.md` raiz — seção **Fora do MVP / Escopo Negativo**:
   - sem detecção automática de árvores/prédios por imagem
   - sem ray tracing urbano completo sem modelo 3D
   - sem MoM para parabólica grande
   - sem KML nível 2 (modelo 3D extrudado)
6. Revisar todas mensagens de erro da UI — cada erro deve ter instrução acionável
7. Testar fluxo end-to-end: criar antena → salvar → montar enlace → simular → exportar

### Checkpoint
- [ ] Todos 13 arquivos de `docs/for-dummy/` preenchidos
- [ ] Todos 10 arquivos de `docs/calculos/` com conceito + parâmetros + limitações + referência
- [ ] `docs/calculos/10-referencias-tecnicas.md` contém referências verificáveis
- [ ] Toda pasta do repo tem `README.md` não-stub
- [ ] Escopo negativo documentado no `README.md` raiz
- [ ] Fluxo end-to-end funcional sem erros inesperados
- [ ] Nenhuma mensagem de erro na UI sem instrução de resolução

### Report ao final da fase
Escrever `.reports/sistema-antenas/Fase_8.md`

---

## Riscos e Mitigação

| Risco | Probabilidade | Mitigação |
|---|---|---|
| PyNEC difícil de instalar no Windows | Alta | Fallback analítico explícito; documentar instalação em `docs/for-dummy/` |
| Longley-Rice exige biblioteca externa | Média | Wrapper com stub; usar Okumura-Hata como fallback documentado |
| KML sem altitude útil | Alta | Nível 0 funciona sem altitude; avisar usuário quando altitude ausente |
| Simulação pesada trava máquina | Média | `resource_guard.py` com limites desde a Fase 6; nunca rodar em thread principal |
| Frontend complexo sem framework | Média | Manter JS puro e modular; não misturar lógica de UI com chamadas API |
| Escopo cresce antes do MVP | Alta | MVP termina na Fase 4 — checklist explícito bloqueia adição sem decisão |
| Ray Tracing sem modelo 3D = resultado enganoso | Alta | Fora do MVP; stub arquitetural apenas; documentar limitação |

---

## Resumo de Objetos e Rotas

| Domínio | Objeto | Rota base |
|---|---|---|
| Sandbox | `AntennaSpec` (rascunho) | `/api/v1/sandbox` |
| Biblioteca | `AntennaSpec` (salva) | `/api/v1/antennas` |
| Link Planner | `NodeSpec` + `LinkScenario` | `/api/v1/scenarios` |
| Jobs | `Job` | `/api/v1/jobs` |

## Solvers por contexto

| Solver | Antenas / Uso | Modo mínimo | Fase |
|---|---|---|---|
| Analítico | Todos (fallback) | Rápido | 3 |
| MoM (PyNEC) | Dipolo, Monopolo, Helicoidal | Padrão | 6 |
| Abertura | Parabólica | Padrão | 6 |
| Okumura-Hata | Link budget empírico | Rápido | 6 |
| Longley-Rice | Link budget em terreno | Padrão | 6 |
| Ray Tracing | Link Planner (fora do MVP) | Preciso | — |

## KML — Níveis de suporte

| Nível | Conteúdo | Fase | Obstáculo físico? |
|---|---|---|---|
| 0 | Pontos + altitude | 5 | Não |
| 1 | Polígonos | 5 | Não (apenas visual) |
| 1+ | Polígonos + altura + material | Pós-MVP | Sim (com modelo de perda) |
| 2 | Modelo 3D extrudado | Fora do MVP | Sim |

## Separação de preocupações

| Camada | Responsabilidade |
|---|---|
| **Produto** | Telas, fluxos, import/export, mensagens de erro |
| **Engenharia** | Schemas, rotas, storage, testes, logs |
| **Pesquisa** | Solvers pesados, modelos avançados, Ray Tracing, validação científica |

> Pesquisa não bloqueia produto. Fase 3 e 4 (produto) devem estar funcionais antes das Fases 6–7 (pesquisa).
