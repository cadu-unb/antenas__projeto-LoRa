## BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO

**Objetivo**: Aplicar objetos e algoritmos do Sandbox em ambiente geográfico real — Campus Darcy Ribeiro, Universidade de Brasília (UnB).

**Duração estimada**: ~11-14 dias  
**Sprints**: 8, 9, 10  
**Entrada**: Todos os objetos validados do Bloco 1 (sem modificação)

```
Bloco 2 = Bloco 1 + contexto geográfico real
```

<!-- --- -->

### CP-8 | GIS + COBERTURA

**Duração**: 6-7 dias  
**Bloqueador**: Gate Bloco 1 ✓

**Entregas**:
- `src/lora_antenna/gis/campus.py` — importação shapefile Campus Darcy Ribeiro
- `src/lora_antenna/gis/coverage_grid.py` — grade espacial configurável (5-50m)
- `src/lora_antenna/gis/heatmap.py` — cálculo de potência por ponto de grade
- `src/lora_antenna/pages/campus_coverage.py` — UI mapa Folium + heatmap
- Integração com objetos `Antenna` + `LinkBudget` do Bloco 1

**Critérios de Aceite**:
- [ ] Shapefile Campus Darcy Ribeiro importado e exibido
- [ ] Grade espacial configurável (5m, 10m, 20m, 50m)
- [ ] Heatmap de potência LoRa renderiza no mapa
- [ ] Posicionamento de antena interativo (clique no mapa)
- [ ] Cálculo de cobertura usa objetos do Bloco 1 sem modificação

**Commit**: `feat: checkpoint 8 - GIS campus coverage heatmap`

<!-- --- -->

### CP-9 | RELATÓRIOS

**Duração**: 3-4 dias  
**Bloqueador**: CP-8 ✓

**Entregas**:
- `src/lora_antenna/reports/markdown_report.py` — relatório em markdown
- `src/lora_antenna/reports/pdf_export.py` — conversão markdown → PDF
- Inclusão automática de gráficos e tabelas de link budget
- Seção de limitações no relatório

**Critérios de Aceite**:
- [ ] Relatório markdown gerado com parâmetros de antena + link budget
- [ ] PDF exportado com gráficos embutidos
- [ ] Tabelas de link budget corretas
- [ ] Seção de limitações presente no relatório

**Commit**: `feat: checkpoint 9 - markdown and PDF reports`

<!-- --- -->

### CP-10 | DEPLOY + QA FINAL

**Duração**: 2-3 dias  
**Bloqueador**: CP-9 ✓

**Entregas**:
- Docker build final + push
- Testes E2E (happy path + edge cases)
- `README.md` final com instruções de instalação e uso
- Deploy em LAN (porta 3953)

**Critérios de Aceite**:
- [ ] `docker compose up` sobe plataforma completa
- [ ] Testes E2E passam (Bloco 1 + Bloco 2)
- [ ] README cobre instalação, uso e limitações
- [ ] Plataforma acessível na LAN via porta 3953

**Commit**: `feat: checkpoint 10 - production deploy and QA`

<!-- --- -->

