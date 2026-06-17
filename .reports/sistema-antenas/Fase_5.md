# Fase 5 — KML e Mapa
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Parser KML criado

`backend/app/domain/kml/parser.py`

### Tipos KML suportados

| Tipo | Nível | Resultado | Penalidade física |
|---|---|---|---|
| `<Point>` | 0 | `KmlPoint` (lat, lon, altitude) | Não |
| `<Polygon>` | 1 | `KmlPolygon` (outer_ring com [lon, lat, alt]) | Não (apenas visual) |

### Namespaces suportados
- `http://www.opengis.net/kml/2.2` (padrão OGC)
- `http://earth.google.com/kml/2.2` (Google Earth 2.2)
- `http://earth.google.com/kml/2.1` (Google Earth 2.1)
- Sem namespace (detecção automática)

### Modelos Pydantic

```
KmlPoint:    name, lat, lon, altitude (Optional)
KmlPolygon:  name, outer_ring ([[lon, lat, alt], ...])
KmlParseResult: points, polygons
```

Erros de XML mal-formado levantam `ValueError("KML malformado: ...")`.

---

## Rotas criadas

| Método | Rota | Status | Descrição |
|---|---|---|---|
| `POST` | `/api/v1/scenarios/{id}/kml` | 200/404/422 | Upload KML, parse, persiste em `extra_nodes` + `polygons` |

Retorna `KmlImportResult`: `scenario_id`, `nodes_imported`, `polygons_imported`, `nodes`, `polygons`.

Requer `python-multipart` (adicionado como dependência).

---

## Schemas alterados

`LinkScenario` — campos adicionados:

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `topology_type` | string | `"P2P"` | `"P2P"` / `"CHAIN"` / `"STAR"` |
| `extra_nodes` | list[NodeSpec] | `[]` | Nós além de node_a/node_b |
| `polygons` | list[dict] | `[]` | Polígonos KML (apenas visual) |

`KmlImportResult` — schema novo (response do endpoint KML).

---

## Telas alteradas

### `link-planner.html`

**Adicionado:**
- Leaflet 1.9.4 (CDN CSS + JS) com tiles OpenStreetMap
- Barra de topologia: botões P2P / Cadeia / Estrela
- Mapa interativo com:
  - Marcador azul = Nó A
  - Marcador verde = Nó B
  - Marcador laranja = nós extras (manual + KML)
  - Linhas tracejadas vermelhas por topologia (P2P, cadeia, estrela)
  - Polígonos roxos semi-transparentes (KML nível 1)
  - Auto-fit bounds ao conjunto de nós
- Seção "Nós extras" (aparece em Cadeia / Estrela):
  - Adicionar nó manual com formulário
  - Nós KML importados como read-only com dropdown de antena
  - Remover nó manual
- Botão "Importar KML" → file input → POST kml → atualiza mapa
- Banners de erro e info (substitui banner único)
- `ensureScenario()` — cria cenário automaticamente antes do upload KML
- Mapa atualiza em tempo real ao editar coordenadas Nó A/B

---

## Limitações do KML nível 1

- Polígonos são apenas visuais — sem penalidade de sinal
- Sem `<MultiGeometry>` (múltiplas geometrias por Placemark)
- Sem `<LineString>`
- Sem `<NetworkLink>`
- Sem KML nível 2 (modelos 3D extrudados)
- Penalidade física de obstáculo: requer altura + material + modelo de perda (Fase pós-MVP)

---

## Arquivos criados

| Arquivo | Descrição |
|---|---|
| `backend/app/domain/kml/__init__.py` | Pacote kml |
| `backend/app/domain/kml/parser.py` | Parser KML nível 0 e 1 |
| `docs/for-dummies/08-como-importar-kml.md` | Guia de importação KML |
| `tests/test_kml.py` | 19 testes (parser + API) |

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/schemas/link_scenario.py` | `topology_type`, `extra_nodes`, `polygons`, `KmlImportResult` |
| `backend/app/api/link_routes.py` | `POST /{id}/kml` + imports multipart |
| `frontend/public/link-planner.html` | Leaflet + mapa + topologias + KML upload |
| `docs/for-dummies/09-como-montar-enlace.md` | Seções: topologias, KML, mapa |
| `pyproject.toml` (via uv) | `python-multipart==0.0.32` adicionado |

---

## Resultado dos testes

```
tests/test_kml.py — 19 passed
Suite completa — 65 passed, 1 warning in 1.53s
```

---

## Checkpoints

- [x] KML de pontos importado vira nós no mapa
- [x] Coordenadas dos nós ficam corretas (SP: lat=-23.5505, lon=-46.6333 validado)
- [x] KML com polígonos renderiza áreas no mapa (apenas visual)
- [x] Nó importado aceita `AntennaSpec` (dropdown por nó KML)
- [x] Link budget após KML bate com P2P direto quando não há obstáculos reais (`test_kml_calculate_after_import_same_as_direct`)
- [x] Modos P2P, cadeia e estrela aparecem na interface (barra de topologia)
- [x] Parser retorna erro claro para KML malformado (`ValueError: "KML malformado: ..."` → HTTP 422)

---

## Erros conhecidos

- Polígono KML sem tag `<outerBoundaryIs>` explícita: parser tenta fallback via `.//{t('coordinates')}` — pode capturar coordenadas de `innerBoundaryIs` em casos extremos. Solução: usar estrutura KML padrão.
- Leaflet carregado via CDN — requer conexão à internet no navegador. Sem CDN, mapa não carrega (tiles ficam cinza mas marcadores e linhas continuam funcionais).
