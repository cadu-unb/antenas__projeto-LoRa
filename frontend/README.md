# frontend/

Frontend estático do sistema de antenas LoRa. Servido diretamente pelo FastAPI via `StaticFiles`.

## Estrutura

```
frontend/
└── public/
    ├── index.html          # Sandbox (tela principal)
    ├── library.html        # Biblioteca de antenas
    ├── link-planner.html   # Link Planner P2P
    └── js/
        ├── api-client.js   # Wrapper fetch para todas as rotas da API
        ├── job-monitor.js  # Polling de jobs assíncronos (2 s)
        └── sandbox.js      # Lógica do Sandbox (SVG, formulário, resultados)
```

## Acesso

Com o backend rodando:
- Sandbox: `http://localhost:8000`
- Biblioteca: `http://localhost:8000/library.html`
- Link Planner: `http://localhost:8000/link-planner.html`

## Tecnologia

HTML/CSS/JS puro — sem framework. Sem build step, sem bundler.

## Editável

Todos os arquivos são editáveis diretamente. Mudanças refletem imediatamente ao recarregar a página (uvicorn em modo `--reload` não precisa reiniciar para mudanças no frontend).

## Não versionado

`frontend/public/` é versionado. Não há arquivos gerados nesta pasta.
