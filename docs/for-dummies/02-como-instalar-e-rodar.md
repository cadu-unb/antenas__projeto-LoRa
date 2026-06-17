# Como instalar e rodar

## Pré-requisitos

- Python 3.13 ou superior
- [uv](https://docs.astral.sh/uv/) instalado
- Git

Verificar versão do Python:
```bash
python --version  # deve ser 3.13+
```

Instalar uv (se necessário):
```bash
pip install uv
```

## Instalação

```bash
# 1. Clonar repositório
git clone <url-do-repositorio>
cd antenas__projeto-LoRa

# 2. Instalar dependências
uv sync

# 3. (Opcional) Instalar PyNEC para modo Padrão/Preciso
#    Linux / WSL2:
uv pip install PyNEC
#    Windows: requer MSVC ou MinGW — ver README.md raiz
```

## Rodar localmente

```bash
uv run uvicorn backend.app.main:app --reload
```

Acessar em: `http://localhost:8000`

Páginas disponíveis:
- `http://localhost:8000` → Sandbox
- `http://localhost:8000/library.html` → Biblioteca
- `http://localhost:8000/link-planner.html` → Link Planner

## Rodar com Docker

```bash
docker-compose up --build
```

Mesmo endereço: `http://localhost:8000`

## Verificar instalação

```bash
curl http://localhost:8000/health
# Esperado: {"status": "ok", "version": "0.1.0"}
```

## Rodar testes

```bash
uv run pytest tests/ -q
```

## Estrutura de dados persistidos

Todos os dados ficam em `backend/data/` (não versionado):

```
backend/data/
├── antenna_specs/   # antenas salvas (.json por ID)
├── scenarios/       # cenários do Link Planner (.json por ID)
├── simulations/     # logs de jobs (.jsonl por job_id)
├── kml_uploads/     # arquivos KML importados
└── reports/         # relatórios exportados
```

## Problemas comuns

| Erro | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: fastapi` | Dependências não instaladas | `uv sync` |
| Porta 8000 em uso | Outro processo | `uv run uvicorn backend.app.main:app --reload --port 8001` |
| PyNEC não encontrado | Compilador C ausente (Windows) | Usar WSL2 ou instalar MSVC |
