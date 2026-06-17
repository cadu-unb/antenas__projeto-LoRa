# Fase 0 — Convenções do Repositório
**Data:** 2026-06-17  
**Status:** ✅ Concluída

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `docs/for-dummies/README.md` | Índice dos 13 guias planejados com fase de entrega |
| `docs/calculos/README.md` | Índice dos 10 métodos de cálculo com solver e fase |
| `docs/architecture.md` | Descrição dos três domínios: Sandbox, Biblioteca, Link Planner |
| `docs/simulation-modes.md` | Tabela dos 4 modos: Rápido, Padrão, Preciso, Experimental |
| `backend/app/config.py` | Configuração central: `MAX_RAM_GB = 25`, `MAX_RUNTIME_MIN = 30` |

## Pastas criadas

| Pasta | Descrição |
|---|---|
| `docs/for-dummies/` | Guias acessíveis por fase |
| `docs/calculos/` | Documentação técnica de métodos |
| `backend/app/` | Aplicação FastAPI |
| `frontend/public/` | Assets estáticos servidos pelo FastAPI |

## Arquivos alterados

| Arquivo | Descrição |
|---|---|
| `.reports/sistema-antenas/Fase_0.md` | Este relatório (estava como placeholder vazio) |

---

## Decisões de stack confirmadas

| Item | Decisão |
|---|---|
| Backend | FastAPI |
| Validação de schemas | Pydantic v2 |
| Gerenciador de pacotes Python | UV |
| Frontend | HTML/CSS/JS puro (sem framework) |
| Servidor de estáticos | FastAPI `StaticFiles` (sem Express) |
| Storage no MVP | JSON em disco |
| Containerização | Docker + docker-compose (Fase 1) |

---

## Convenções adotadas

| Convenção | Valor |
|---|---|
| Relatórios de fase | `.reports/sistema-antenas/Fase_X.md` |
| Guias de usuário | `docs/for-dummies/` |
| Documentação técnica | `docs/calculos/` |
| Skills | `.codex/skills/` |
| Prompts de fase | `.prompt/sistema-antenas/` |
| Backend | `backend/` |
| Frontend | `frontend/` |

---

## Checkpoints

- [x] `.reports/sistema-antenas/` existe
- [x] `docs/for-dummies/` existe
- [x] `docs/calculos/` existe
- [x] `docs/architecture.md` descreve Sandbox, Biblioteca e Link Planner
- [x] `docs/simulation-modes.md` lista os 4 modos (Rápido, Padrão, Preciso, Experimental)
- [x] `backend/app/config.py` define `MAX_RAM_GB` e `MAX_RUNTIME_MIN`
- [x] Nenhum arquivo criado fora das convenções

---

## Pendências e riscos

| Item | Tipo | Nota |
|---|---|---|
| `backend/app/__init__.py` | Pendente | Criado na Fase 1 junto com `main.py` |
| `frontend/public/index.html` | Pendente | Criado na Fase 1 |
| PyNEC no Windows | Risco | Fallback analítico documentado; instalação em `docs/for-dummies/` |
| `docs/` não tinha existência prévia | Observação | Pasta `__docs/` existia mas não segue convenção — não foi removida nesta fase |
