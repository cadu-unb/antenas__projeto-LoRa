# backend/app/

Código da aplicação FastAPI.

## Arquivos principais

| Arquivo/Pasta | Função |
|---|---|
| `main.py` | Entry point — FastAPI app, rota `/health`, mount estático |
| `config.py` | Constantes globais: `MAX_RAM_GB`, `MAX_RUNTIME_MIN` |
| `api/` | Rotas HTTP (uma por domínio: library, sandbox, link) |
| `domain/` | Lógica de negócio pura, sem dependência de HTTP |
| `schemas/` | Modelos Pydantic: `AntennaSpec`, `NodeSpec`, `LinkScenario` |
| `solvers/` | Solvers de cálculo EM e propagação |
| `storage/` | Leitura/escrita de arquivos JSON em `backend/data/` |
| `workers/` | Guardião de recursos, fila de jobs assíncronos |
