# Como importar um arquivo KML

## O que é KML?

Formato XML geográfico (Google Earth). Contém pontos (placemarks) e polígonos (áreas). Usado para posicionar nós no mapa sem digitar coordenadas manualmente.

## O que o sistema importa

| Elemento KML | O que vira | Nota |
|---|---|---|
| `<Point>` | Nó no mapa | Lat, lon e altitude extraídos |
| `<Polygon>` | Área visual no mapa | Apenas visual — sem penalidade física |
| Sem altitude | Altura = 0 m | Sistema avisa quando altitude ausente |

Polígonos são renderizados como áreas de interesse. **Não representam obstáculos físicos** — sem altura, material e modelo de perda configurados (disponível em fases futuras).

## Passo a passo

1. Abra `http://localhost:8000/link-planner.html`
2. Preencha **Nó A** e **Nó B** normalmente
3. Clique **Importar KML**
4. Selecione o arquivo `.kml` no explorador
5. Sistema cria o cenário automaticamente e importa
6. Mapa atualiza com os nós e polígonos importados

## Associar antenas aos nós importados

Após importar:

1. Clique em **Cadeia** ou **Estrela** na barra de topologia
2. Seção "Nós intermediários" aparece
3. Dropdown de antena aparece ao lado de cada nó importado
4. Selecione antena da biblioteca (opcional)

## Formato KML mínimo (pontos)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Gateway SP</name>
      <Point>
        <coordinates>-46.6333,-23.5505,30</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Sensor Campo</name>
      <Point>
        <coordinates>-46.8000,-23.7000,5</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

Formato das coordenadas: `longitude,latitude,altitude` (nessa ordem — igual Google Earth).

## Formato KML com polígono

```xml
<Placemark>
  <name>Área de cobertura</name>
  <Polygon>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
          -46.70,-23.60,0
          -46.60,-23.60,0
          -46.60,-23.50,0
          -46.70,-23.50,0
          -46.70,-23.60,0
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| "KML malformado" | XML inválido ou incompleto | Verifique o arquivo com editor de texto |
| Nenhum nó apareceu | KML sem `<Point>` | Confirme que tem `<Placemark><Point>` |
| Coordenadas trocadas | Longitude e latitude invertidas | KML usa lon,lat — não lat,lon |
| Polígono não fecha | Último ponto diferente do primeiro | Repita o primeiro ponto no final do anel |

## Limitações desta versão

- Sem `<MultiGeometry>` (múltiplas geometrias por placemark)
- Polígonos apenas visuais — sem modelo de obstrução físico
- Sem importação de linhas (`<LineString>`)
- Sem `<NetworkLink>` (KML com referências externas)
