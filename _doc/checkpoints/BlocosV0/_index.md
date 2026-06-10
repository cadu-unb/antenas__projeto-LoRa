<link rel="stylesheet" type="text/css" href="../../css/style_.css">

# Estrutura de Blocos — LoRa Antenna Platform MVP

**Versão**: V0  
**Data**: 2026-06-10  
**Referência**: `doc/architecture/Implementation-roadmap.md`

<!-- --- -->

![[bloco1]]

<!-- --- -->

## Gate de Saída — BLOCO 1 → BLOCO 2

**Checklist obrigatório antes de avançar**:

- [ ] 6+ tipos de antena operacionais e testados
- [ ] Link budget com diretividade implementado
- [ ] Friis validado contra ≥ 3 casos conhecidos da literatura
- [ ] UI sandbox executa sem erros
- [ ] Visualizações polares + ganho renderizam
- [ ] Heatmap funciona em espaço abstrato (sem coordenadas reais)
- [ ] Persistência Pydantic + JSON operacional
- [ ] Testes unitários: coverage > 95%

**Data Esperada**: Fim do dia 19-22 do cronograma total

<!-- --- -->

![[bloco2]]

<!-- --- -->

## Relação entre Blocos

```
Bloco 1 — Sandbox
    ↓
Validação dos modelos matemáticos
    ↓
Criação dos objetos Antenna e Link (RF chain)
    ↓
Persistência e serialização (Pydantic + JSON)
    ↓
Gate de Saída: todos os critérios ✓
    ↓
Bloco 2 — Campus Darcy Ribeiro
    ↓
Aplicação dos mesmos objetos em mapas reais
    ↓
Simulação de cobertura LoRa/LoRaWAN
    ↓
Relatórios + Deploy
```

<!-- --- -->

## Cronograma Resumido

| Sprint | Bloco | Duração | Acumulado |
<!-- <!-- <!-- <!-- <!-- <!-- <!-- <!-- <!-- <!-- |--------|-------|---------|-----------| --> --> --> --> --> --> --> --> --> -->
| CP-0.5 | Bloco 1 | 2 dias | 2 dias |
| CP-0 | Bloco 1 | 1-2 dias | 3-4 dias |
| CP-1 | Bloco 1 | 3-4 dias | 6-8 dias |
| CP-2-3 | Bloco 1 | 5-6 dias | 11-14 dias |
| CP-4 | Bloco 1 | 3-4 dias | 14-18 dias |
| CP-5-6 | Bloco 1 | 5-6 dias | 19-24 dias |
| CP-7 | Bloco 1 | 5-6 dias | 24-30 dias |
| **Gate Bloco 1** | — | — | **dia ~22-27** |
| CP-8 | Bloco 2 | 6-7 dias | 30-37 dias |
| CP-9 | Bloco 2 | 3-4 dias | 33-41 dias |
| CP-10 | Bloco 2 | 2-3 dias | 35-44 dias |
| **TOTAL** | — | **35-44 dias** | **~7-9 semanas** |
