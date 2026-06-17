# Arquitetura — Sistema de Antenas LoRa

## Visão geral

O sistema é dividido em três domínios funcionais independentes que compartilham o objeto central `AntennaSpec`.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Sandbox   │────▶│  Biblioteca │◀────│  Link Planner   │
│             │     │             │     │                 │
│ Criar e     │     │ Salvar,     │     │ Montar cenários │
│ simular     │     │ listar,     │     │ de enlace P2P   │
│ antenas     │     │ exportar    │     │ e multi-nó      │
└─────────────┘     └─────────────┘     └─────────────────┘
       │                   ▲                    │
       │   AntennaSpec      │                    │
       └───────────────────┘                    │
                                   NodeSpec + LinkScenario
```

---

## Sandbox

**Responsabilidade:** interface de criação e pré-visualização de antenas.

- Usuário configura tipo, geometria, frequência e material
- Sistema calcula ganho, impedância, SWR e diagrama polar
- Resultado pode ser salvo na Biblioteca como `AntennaSpec` completo
- Modos de simulação disponíveis: Rápido (analítico), Padrão (MoM), Preciso (MoM refinado)
- Frontend: `sandbox.html` (4 painéis: SVG físico, parâmetros, resultado EM, diagrama polar)
- Backend: `POST /api/v1/sandbox/preview`

**Objetos:** `AntennaSpec` (rascunho — ainda não salvo)

---

## Biblioteca

**Responsabilidade:** persistência e gestão de antenas salvas.

- CRUD completo de `AntennaSpec` em arquivos JSON
- Import/export individual e em lote
- Antenas salvas ficam disponíveis para o Link Planner
- Storage: `backend/data/antenna_specs/{id}.json`
- Frontend: `library.html`
- Backend: `GET/POST/PUT/DELETE /api/v1/antennas`

**Objetos:** `AntennaSpec` (salvo em disco)

---

## Link Planner

**Responsabilidade:** planejamento de enlace entre nós de campo.

- Dois ou mais nós, cada um com uma antena da Biblioteca
- Calcula distância geodésica, azimute, elevação, FSPL e margem de enlace
- Semáforo de viabilidade: verde (> 10 dB) / amarelo (0–10 dB) / vermelho (< 0 dB)
- Suporte a topologias: P2P, cadeia, estrela (malha e multi-estrela em fases futuras)
- Import de posições via KML (Fase 5)
- Storage: `backend/data/simulations/{id}/`
- Frontend: `link-planner.html`
- Backend: `POST/GET /api/v1/scenarios`, `POST /api/v1/scenarios/{id}/calculate`

**Objetos:** `NodeSpec`, `LinkScenario`

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Pydantic v2 |
| Gerenciador de pacotes | UV |
| Frontend | HTML/CSS/JS puro (sem framework) |
| Servidor estático | FastAPI `StaticFiles` (sem Express) |
| Storage | JSON em disco (sem banco de dados no MVP) |
| Containerização | Docker + docker-compose |

---

## Separação de responsabilidades

| Camada | O que faz |
|---|---|
| **Produto** | Telas, fluxos, import/export, mensagens de erro |
| **Engenharia** | Schemas, rotas, storage, testes, logs |
| **Pesquisa** | Solvers pesados, MoM, Longley-Rice, Ray Tracing |

Pesquisa não bloqueia produto. Fases 3 e 4 (produto) devem estar funcionais antes das Fases 6–7 (pesquisa/solvers avançados).
