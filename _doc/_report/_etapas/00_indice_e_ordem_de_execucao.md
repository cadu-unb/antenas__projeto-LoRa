# 00 — Índice e Ordem de Execução

## Objetivo

Dividir o relatório `_doc/_report/2026.06.10_correcao_arquitetural_e_manuais_usuario.md` em etapas menores, rastreáveis e executáveis. Cada arquivo desta pasta descreve um problema identificado, o plano de solução e os critérios mínimos de aceite.

## Ordem Recomendada

1. `01_diagnostico_rise5_e_prioridades.md`
2. `02_core_constants_e_sensibilidade_rx.md`
3. `03_propagation_batch_contracts.md`
4. `04_propagation_batch_executor.md`
5. `05_distance_matrix_e_reference_tables.md`
6. `06_refatoracao_gis_multi_link.md`
7. `07_ui_cp4_standalone_e_feasible.md`
8. `08_ui_campus_kml_interferencia_canais.md`
9. `09_manuais_usuario_e_operacao_lan.md`
10. `10_criterios_aceite_e_governanca.md`

## Dependências

- As etapas 02, 03 e 04 são pré-requisitos técnicos para CP-4 e CP-5/6.
- A etapa 05 é pré-requisito para CP-8, pois normaliza a matriz de distâncias.
- A etapa 06 depende das etapas 03, 04 e 05.
- As etapas 07, 08 e 09 são especificações funcionais e documentais para UI, campus e operação.
- A etapa 10 consolida os gates de saída.

## Regra de Fronteira

`propagation/`, `core/` e `antenna/` continuam sem importar `gis/`, `network/`, `streamlit`, `shapely` ou `requests`. `gis/` orquestra dados geográficos e injeta escalares no motor matemático.
