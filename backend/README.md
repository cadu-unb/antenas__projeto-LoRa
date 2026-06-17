# backend/

Backend FastAPI do sistema de antenas LoRa.

## Estrutura

```
backend/
├── app/          # Aplicação FastAPI
└── data/         # Dados persistidos em disco (não versionados)
```

## Como rodar localmente

```bash
uv pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Acesse: http://localhost:8000

## Como rodar com Docker

```bash
docker-compose up
```
