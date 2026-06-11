# 09 — Manuais de Usuário e Operação LAN

## Problema

O relatório contém conteúdo de manual de usuário e deploy misturado com correções arquiteturais. Isso deve virar documentação separada e consumível.

## Documentos Futuros Sugeridos

- `_doc/_manual/usuario_simulador_multino.md`
- `_doc/_manual/preparacao_kml_google_earth.md`
- `_doc/_manual/metricas_rf_e_interpretacao.md`
- `_doc/_manual/operacao_lan_e_deploy.md`

## Conteúdo do Manual do Usuário

- finalidade do simulador
- preparação de KML
- nomenclatura P1-P8
- nomenclatura BUILDING/OBSTACLE/CAMPUS
- interpretação de dBm, margem, SIR e risco
- erros comuns e correções

## Conteúdo do Manual LAN

- pré-requisitos
- `uv sync`
- `uv run`
- porta `3953`
- Dockerfile futuro
- `docker-compose.yml` futuro
- firewall e acesso por IP local

## Observação

Streamlit e Docker ainda são prospectivos. A documentação deve explicitar quando um comando depende de `app.py` ou UI ainda não implementada.

## Validação

- Usuário entende como preparar KML.
- Usuário entende diferença entre enlace viável e enlace decodificável.
- Operador entende como executar em LAN quando a UI existir.
