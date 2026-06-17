# Prompt — Sistema de Antenas LoRa — Fase 0

## Objetivo

Fixar convenções do repositório antes de criar lógica de negócio.

Esta fase prepara estrutura, documentação mínima, pastas padrão e configuração central.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/avaliacao-plan-v2.md`

Use estas convenções:

- Relatórios em `.reports/sistema-antenas/`
- Documentação simples em `docs/for-dummies/`
- Backend em `backend/`
- Frontend em `frontend/`
- Skills em `.codex/skills/`
- Prompts em `.prompt/sistema-antenas/`

## Tarefas

1. Confirmar stack do MVP:
   - FastAPI
   - Pydantic v2
   - Gerenciador de pacotes, UV
   - HTML/CSS/JS puro
   - frontend estático servido pelo FastAPI
2. Criar ou ajustar pastas:
   - `.reports/sistema-antenas/`
   - `docs/for-dummies/`
   - `docs/calculos/`
   - `backend/app/`
   - `frontend/public/`
3. Criar `docs/for-dummies/README.md` com lista dos guias planejados.
4. Criar `docs/calculos/README.md` com lista dos métodos planejados.
5. Criar `docs/architecture.md` explicando:
   - Sandbox
   - Biblioteca
   - Link Planner
6. Criar `docs/simulation-modes.md` com tabela:
   - Rápido
   - Padrão
   - Preciso
   - Experimental
7. Criar `backend/app/config.py` com:
   - `MAX_RAM_GB = 25`
   - `MAX_RUNTIME_MIN = 30`
8. Não criar lógica de API nesta fase.

## Checkpoints obrigatórios

- [ ] `.reports/sistema-antenas/` existe
- [ ] `docs/for-dummies/` existe
- [ ] `docs/calculos/` existe
- [ ] `docs/architecture.md` descreve Sandbox, Biblioteca e Link Planner
- [ ] `docs/simulation-modes.md` lista os 4 modos
- [ ] `backend/app/config.py` define `MAX_RAM_GB` e `MAX_RUNTIME_MIN`
- [ ] Nenhum arquivo foi criado fora das convenções

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_0.md
```

O relatório deve conter:

- arquivos criados;
- arquivos alterados;
- decisões de stack confirmadas;
- convenções adotadas;
- checkpoints marcados;
- pendências ou riscos.

## Regra final

Não avance para a Fase 1.
