### Objetivos Curto Prazo
- Upload e parsing de arquivos `.kml` com pontos de interesse P1-P8.
- Cálculo automático da matriz de distâncias geodésicas entre todos os pares.
- Execução batch do link budget usando o motor matemático do Bloco 1 sem alterações internas.
- Mapa Folium com marcadores, linhas de enlace e status por margem.
- Grade espacial configurável (5-50m) e heatmap como extensão sobre a base multiponto.
- Importação de shapefiles permanece opcional para o MVP, subordinada ao contrato `gis/`.

### Contrato Arquitetural

- `src/lora_antenna/gis/` é a única camada que conhece KML, shapefile, coordenadas WGS84 e matriz geodésica.
- `src/lora_antenna/propagation/` recebe apenas distâncias em metros, ganhos, perdas e parâmetros RF; não recebe bytes KML, `KMLDocument`, Folium ou `st.session_state`.
- `src/lora_antenna/core/` e `src/lora_antenna/antenna/` não importam `gis/`.
- `GeographicPosition` deve ser extraído para um módulo neutro antes da integração: `src/lora_antenna/models/geo.py`.
- Toda frequência LoRa no Brasil deve usar faixa `915-928 MHz`; defaults de Sprint 8 usam `915e6 Hz`.

### Novos Módulos

```text
src/lora_antenna/models/geo.py
src/lora_antenna/gis/kml_parser.py
src/lora_antenna/gis/distance_matrix.py
src/lora_antenna/gis/multi_link.py
src/lora_antenna/gis/map_renderer.py
src/lora_antenna/pages/campus_coverage.py
tests/fixtures/campus_p1_p8.kml
tests/test_kml_parser.py
tests/test_distance_matrix.py
tests/test_multi_link_batch.py
```

### Fluxo Obrigatório

```text
Upload KML
  -> gis/kml_parser.py
  -> KMLDocument(points=[KMLPoint])
  -> gis/distance_matrix.py
  -> DistanceMatrix
  -> gis/multi_link.py
  -> LinkBatchRequest
  -> propagation/link_budget.py e rf_chain/chain.py
  -> LinkBatchResult[]
  -> gis/map_renderer.py + pages/campus_coverage.py
```

### Estados de Sessão

`pages/campus_coverage.py` deve manter os seguintes estados com reset explícito:

- `st.session_state["kml_document"]`: documento KML validado ou `None`.
- `st.session_state["distance_matrix"]`: matriz geodésica calculada ou `None`.
- `st.session_state["link_batch_request"]`: parâmetros RF e pares selecionados.
- `st.session_state["link_results"]`: resultados batch; deve ser apagado ao trocar KML ou antena.
- `st.session_state["geo_context"]`: metadados de sessão, incluindo CRS, nome do arquivo, hash do upload e timestamp.

### Critérios de Aceite

- [ ] KML real do Campus Darcy Ribeiro carrega sem caminho absoluto.
- [ ] Labels P1-P8 são preservados e validados como únicos.
- [ ] Distâncias entre oito pontos geram 28 pares.
- [ ] Distância calculada pode ser comparada contra tabela de referência com tolerância configurável.
- [ ] Batch executa usando antena padrão única e `antenna_map` opcional por ponto.
- [ ] UI reseta resultados quando o arquivo, a antena ou os parâmetros RF mudam.
- [ ] Nenhum módulo do Bloco 1 importa `gis/`, Folium, Streamlit ou parsers de arquivo.
- [ ] Testes unitários cobrem parser KML, matriz de distância e batch link budget.
