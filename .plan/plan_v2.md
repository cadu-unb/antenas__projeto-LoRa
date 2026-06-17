# Plano de Execução — Sistema de Antenas LoRa
> Baseado em `open1.md` + `g1.md`. Três objetos centrais: `AntennaSpec`, `NodeSpec`, `LinkScenario`.

---

## Fase 1 — Estrutura e Fundação

### Descrição
Criar scaffold completo do projeto. Sem lógica de negócio. Apenas esqueleto funcional: pastas, Docker, rotas vazias, documentação mínima em toda pasta.

### Passos sugeridos
1. Criar estrutura de pastas conforme spec (`backend/`, `frontend/`, `docs/`)
2. Inicializar `backend/` com FastAPI — `main.py`, rotas stub, `requirements.txt`
3. Inicializar `frontend/` com Express — `server.js`, páginas HTML stub (`index.html`, `sandbox.html`, `library.html`, `link-planner.html`)
4. Criar `docker-compose.yml` — serviços `backend` (Python) e `frontend` (Node)
5. Criar `README.md` raiz e `README.md` em toda pasta criada
6. Criar stubs de `docs/for-dummies/README.md` e `docs/calculos/README.md`
7. Criar `docs/architecture.md` com diagrama de domínios (Sandbox / Library / Link Planner)

### Checkpoint
- [ ] `docker-compose up` sobe backend e frontend sem erro
- [ ] `GET /health` → `{"status": "ok"}`
- [ ] Frontend entrega `index.html` em `localhost:3000`
- [ ] Toda pasta do repo contém `README.md` (pode ser stub)
- [ ] Estrutura de pastas bate com spec da seção 9 do `open1.md`
- [ ] `docs/architecture.md` descreve os três domínios e Express como proxy puro

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_1.md`

---

## Fase 2 — Schema & Biblioteca de Antenas

### Descrição
Definir o contrato central `AntennaSpec` JSON (schema Pydantic). Implementar API de biblioteca (CRUD) e página frontend de listagem, import e export.

### Passos sugeridos
1. Escrever `schemas/antenna_spec.py` — Pydantic model completo (campos da seção 2 do `open1.md`): `schema_version`, `id`, `name`, `type`, `frequency_hz`, `units`, `geometry`, `material`, `solver`, `results`, `metadata`
2. Implementar `api/library_routes.py`:
   - `GET    /api/v1/antennas` — lista
   - `POST   /api/v1/antennas` — cria
   - `GET    /api/v1/antennas/{id}` — detalhe
   - `PUT    /api/v1/antennas/{id}` — atualiza
   - `DELETE /api/v1/antennas/{id}` — remove
3. Storage: `backend/data/antenna_specs/{id}.json`
4. Criar `frontend/public/library.html` — lista de antenas, botão import JSON, botão export, botão delete
5. Criar `frontend/public/js/api-client.js` — wrapper fetch para todas rotas
6. Escrever `docs/antenna-spec-schema.md` — campos, tipos, exemplos
7. Escrever `docs/for-dummies/06-como-salvar-antena-json.md`

### Checkpoint
- [ ] `POST /api/v1/antennas` com payload válido → `201` + spec salva em disco
- [ ] `POST /api/v1/antennas` com payload inválido → `422` com campo e motivo
- [ ] `GET /api/v1/antennas` retorna array; vazio se sem antenas
- [ ] Frontend `library.html` carrega lista via `api-client.js`
- [ ] Upload de JSON válido cria antena; JSON inválido mostra erro
- [ ] Export baixa arquivo `.json` com spec completa e `results` incluídos
- [ ] `docs/antenna-spec-schema.md` documenta todos os campos com tipos e exemplos

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_2.md`

---

## Fase 3 — Sandbox de Antenas

### Descrição
Interface de criação e edição de antenas com 4 painéis fixos (seção 3 do `open1.md`): visual físico, parâmetros, resultado EM, irradiação. Modo Rápido (analítico) ativo nesta fase.

### Passos sugeridos
1. Criar layout 4-painéis em `sandbox.html` (CSS grid)
2. **Painel 1 — Visual físico:** SVG por tipo (dipolo: dois braços; monopolo: haste + plano de terra; helicoidal: espiras; parabólica: refletor + foco + alimentador). Parâmetros editáveis refletem no SVG.
3. **Painel 2 — Parâmetros editáveis:** formulário por tipo com blocos frequência / geometria / material / alimentação / solver
4. Criar `api/sandbox_routes.py` — `POST /api/v1/sandbox/preview` (modo Rápido, retorno < 2 s)
5. **Painel 3 — Resultado EM:** ganho (dBi), impedância (Ω), SWR, eficiência (%)
6. **Painel 4 — Irradiação:** diagrama polar 2D com Canvas; corte horizontal e vertical
7. Botão "Salvar na Biblioteca" → chama `POST /api/v1/antennas` com spec + results
8. Escrever `docs/for-dummies/05-como-criar-antena-no-sandbox.md`

### Checkpoint
- [ ] Seleção de tipo muda SVG do Painel 1 dinamicamente
- [ ] Edição de parâmetro atualiza SVG sem reload de página
- [ ] `POST /api/v1/sandbox/preview` retorna resultado analítico em < 2 s
- [ ] Painel 3 exibe valores com unidades corretas (dBi, Ω, —)
- [ ] Diagrama polar no Painel 4 coerente por tipo (rosquinha para dipolo, omnidirecional para monopolo)
- [ ] "Salvar na Biblioteca" grava spec com `results` preenchidos
- [ ] Antena salva aparece em `library.html` imediatamente

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_3.md`

---

## Fase 4 — Solvers & Modelos de Propagação

### Descrição
Implementar solvers técnicos e os 4 modos de simulação. Aplicar guardião de recursos: limite 25 GB RAM, 30 min tempo. Log e mensagem clara ao usuário em caso de falha.

### Passos sugeridos
1. `solvers/mom_solver.py` — MoM via PyNEC para dipolo, monopolo, helicoidal
2. `solvers/aperture_solver.py` — aproximação de abertura para parabólica
3. `solvers/okumura_hata.py` — perda de percurso empírica (banda 150–1500 MHz)
4. `solvers/longley_rice.py` — perda em terreno irregular (wrapper ou implementação)
5. Definir `SimulationMode` enum: `RAPIDO` / `PADRAO` / `PRECISO` / `EXPERIMENTAL`
6. Implementar guardião de recursos em `workers/resource_guard.py`:
   - monitor de RAM com `psutil`
   - timeout via `asyncio`
   - ao exceder → `FAILED_MEMORY_LIMIT` ou `FAILED_TIME_LIMIT` + log parcial
7. Integrar modos no Painel 2 do sandbox (seletor de modo + spinner de progresso)
8. Escrever `docs/calculos/03-metodo-dos-momentos-mom.md`
9. Escrever `docs/calculos/04-parabolica-aproximacao-abertura.md`
10. Escrever `docs/calculos/06-okumura-hata.md`
11. Escrever `docs/calculos/07-longley-rice-itm.md`
12. Escrever `docs/calculos/09-limites-computacionais.md`

### Checkpoint
- [ ] Modo `RAPIDO` retorna resultado analítico em < 2 s
- [ ] Modo `PADRAO` roda MoM simplificado e retorna resultado válido
- [ ] Dipolo λ/2 em modo `PADRAO` → ganho ~2.15 dBi (referência padrão)
- [ ] Parabólica usa `aperture_solver`, não MoM
- [ ] Simulação > 25 GB → `FAILED_MEMORY_LIMIT` + mensagem acionável na UI
- [ ] Simulação > 30 min → `FAILED_TIME_LIMIT` + mensagem acionável na UI
- [ ] Log parcial persiste em disco mesmo em jobs abortados
- [ ] Okumura-Hata retorna perda em dB para frequência/distância/altura válidos
- [ ] Longley-Rice retorna perda em dB para perfil de terreno válido

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_4.md`

---

## Fase 5 — Link Planner

### Descrição
Módulo de planejamento de enlace como grafo (`NodeSpec` + `LinkSpec` + `LinkScenario`). Import KML (nível 0 e 1), mapa Leaflet, link budget, modos de topologia, semáforo de viabilidade.

### Passos sugeridos
1. Definir schemas Pydantic: `NodeSpec`, `LinkSpec`, `LinkScenario` (seção 5 do `open1.md`)
2. `api/link_routes.py`:
   - `GET/POST /api/v1/scenarios`
   - `GET/PUT/DELETE /api/v1/scenarios/{id}`
   - `POST /api/v1/scenarios/{id}/calculate`
3. `domain/kml/parser.py` — KML nível 0 (pontos + altitude) e nível 1 (polígonos como obstáculos)
4. `link-planner.html` — mapa Leaflet, painel lateral de nós, painel de enlaces
5. Associar `AntennaSpec` salva a nó via `antenna_spec_id`
6. Calcular azimute, elevação, distância entre nós (geodésica)
7. Link budget: FSPL + ganhos + perdas Okumura-Hata/Longley-Rice + sensibilidade LoRa
8. Modos de topologia configuráveis na UI: P2P / cadeia / estrela / malha manual / gateway setorial
9. Tabela de resultados com semáforo: verde (margem > 10 dB) / amarelo (0–10 dB) / vermelho (< 0 dB)
10. Escrever `docs/for-dummies/08-como-importar-kml.md`
11. Escrever `docs/for-dummies/09-como-montar-enlace.md`
12. Escrever `docs/link-planner-schema.md`

### Checkpoint
- [ ] KML de pontos importado → nós aparecem no mapa Leaflet com coordenadas corretas
- [ ] KML com polígonos → polígonos renderizados como áreas de obstrução
- [ ] Nó aceita `AntennaSpec` da biblioteca (dropdown de antenas salvas)
- [ ] Azimute e elevação calculados corretamente para dois pontos GPS reais
- [ ] Link budget P2P retorna margem de enlace em dB
- [ ] Semáforo exibe cor correta conforme margem calculada
- [ ] Todos 5 modos de topologia configuráveis na interface
- [ ] Cenário exportável como JSON (`LinkScenario` completo)

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_5.md`

---

## Fase 6 — Fila de Jobs & Monitoramento

### Descrição
Desacoplar simulações pesadas (modo Preciso / Experimental / ray tracing) da request HTTP. Fila async, status polling, frontend de acompanhamento de jobs.

### Passos sugeridos
1. Implementar `workers/job_queue.py` — fila com `asyncio.Queue` (ou Celery se escala exigir)
2. `api/job_routes.py`:
   - `GET    /api/v1/jobs` — lista jobs do usuário
   - `GET    /api/v1/jobs/{id}` — status + progresso
   - `DELETE /api/v1/jobs/{id}` — cancela job
3. Salvar logs parciais em `backend/data/simulations/{job_id}/log.jsonl`
4. Integrar fila no sandbox: botão "Simular (Preciso/Experimental)" → cria job → retorna `job_id`
5. Integrar fila no link planner: ray tracing como job assíncrono
6. `frontend/public/js/job-monitor.js` — polling a cada 2 s, progress bar, log stream, resultado ao DONE
7. Escrever `docs/for-dummies/10-como-rodar-simulacao.md`
8. Escrever `docs/for-dummies/11-como-entender-resultados.md`
9. Escrever `docs/for-dummies/12-erros-comuns-e-como-resolver.md`

### Checkpoint
- [ ] Simulação pesada retorna `job_id` imediatamente (não trava UI)
- [ ] `GET /api/v1/jobs/{id}` retorna `status`: `PENDING` / `RUNNING` / `DONE` / `FAILED_MEMORY_LIMIT` / `FAILED_TIME_LIMIT` / `CANCELLED`
- [ ] Frontend mostra progresso em tempo real (polling 2 s)
- [ ] Job `DONE` → resultado exibido no sandbox ou link planner
- [ ] Job `FAILED_*` → mensagem de erro clara + sugestão de ação
- [ ] Log parcial persiste em disco para jobs cancelados e com erro
- [ ] Cancelamento via `DELETE /api/v1/jobs/{id}` interrompe processo real

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_6.md`

---

## Fase 7 — Documentação & Polimento

### Descrição
Completar toda documentação (`for-dummies`, `calculos`, `README.md` em toda pasta). Refinar UX de erros. Definir escopo negativo explícito. Validar fluxo end-to-end.

### Passos sugeridos
1. Completar todos 13 arquivos de `docs/for-dummies/` (stubs → conteúdo real)
2. Completar todos 10 arquivos de `docs/calculos/` — incluir: conceito, parâmetros, limitações, referência técnica
3. Preencher `docs/calculos/10-referencias-tecnicas.md` com referências reais (Burke/Poggio NEC, Longley-Rice ITM, Hata 1980, ITU-R P.1410)
4. Verificar `README.md` em toda pasta — preencher faltantes com: função da pasta, arquivos principais, se é editável ou gerado
5. Completar `docs/architecture.md`, `docs/simulation-modes.md`
6. Escrever seção **Escopo Negativo / Fora do MVP** no `README.md` raiz: sem detecção automática de árvores/prédios, sem ray tracing urbano completo sem modelo 3D, sem MoM completo para parabólica grande
7. Revisar todas mensagens de erro da UI: cada erro deve ter instrução acionável
8. Testar fluxo end-to-end: criar antena no sandbox → salvar na biblioteca → montar enlace → simular → exportar resultado

### Checkpoint
- [ ] Todos 13 arquivos de `docs/for-dummies/` preenchidos e revisados
- [ ] Todos 10 arquivos de `docs/calculos/` têm: conceito, parâmetros, limitações, referência
- [ ] `docs/calculos/10-referencias-tecnicas.md` contém referências reais e verificáveis
- [ ] Toda pasta do repo tem `README.md` não-stub
- [ ] Escopo negativo documentado explicitamente no `README.md` raiz
- [ ] Fluxo end-to-end funcional sem erros inesperados
- [ ] Nenhuma mensagem de erro na UI sem instrução de resolução

### Report ao final da fase
Escrever `.report/sistema-antenas/Fase_7.md`

---

## Resumo de Domínios e Objetos Centrais

| Domínio | Objeto central | Arquivo principal | Rota base |
|---|---|---|---|
| Sandbox | `AntennaSpec` (rascunho) | `sandbox_routes.py` | `/api/v1/sandbox` |
| Library | `AntennaSpec` (salva) | `library_routes.py` | `/api/v1/antennas` |
| Link Planner | `NodeSpec` + `LinkScenario` | `link_routes.py` | `/api/v1/scenarios` |
| Jobs | `Job` | `job_routes.py` | `/api/v1/jobs` |

## Solvers por contexto

| Solver | Antenas | Modo mínimo |
|---|---|---|
| MoM (PyNEC) | Dipolo, Monopolo, Helicoidal | Padrão |
| Abertura | Parabólica | Padrão |
| Okumura-Hata | Link budget empírico | Rápido |
| Longley-Rice | Link budget em terreno | Padrão |
| Ray Tracing | Link Planner com polígonos | Preciso |

## KML — Três níveis

| Nível | Conteúdo | Suporte |
|---|---|---|
| 0 | Pontos + altitude | Fase 5 |
| 1 | Polígonos de obstáculos | Fase 5 |
| 2 | Modelo 3D extrudado | Fora do MVP |
