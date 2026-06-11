# Preparação de KML no Google Earth

## Pré-requisitos

- Google Earth Pro (gratuito) ou Google Earth Web
- Coordenadas dos nós em WGS84 (latitude/longitude decimal)

## Estrutura KML Esperada

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Campus LoRa</name>

    <!-- Nó P1 -->
    <Placemark>
      <name>P1</name>
      <Point>
        <coordinates>-47.871879,-15.762987,0</coordinates>
      </Point>
    </Placemark>

    <!-- Nó P2 -->
    <Placemark>
      <name>P2</name>
      <Point>
        <coordinates>-47.869717,-15.765910,0</coordinates>
      </Point>
    </Placemark>

    <!-- Prédio (obstáculo com atenuação) -->
    <Placemark>
      <name>BUILDING</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -47.870,-15.763,0
              -47.869,-15.763,0
              -47.869,-15.764,0
              -47.870,-15.764,0
              -47.870,-15.763,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>

  </Document>
</kml>
```

**Ordem das coordenadas:** `longitude,latitude,altitude` — diferente de lat/lon usual.

## Criando Nós no Google Earth Pro

1. Abrir Google Earth Pro.
2. Menu **Adicionar → Marcador de local**.
3. Posicionar o pino no mapa ou digitar lat/lon em **Latitude/Longitude**.
4. Em **Nome**, usar `P1`, `P2`, … `P8`.
5. Clicar OK.
6. Repetir para cada nó.

## Criando Polígonos de Prédios

1. Menu **Adicionar → Polígono**.
2. Desenhar o contorno do prédio clicando nos vértices.
3. Em **Nome**, digitar `BUILDING` (ou `OBSTACLE` para obstáculos genéricos).
4. Clicar OK.

## Exportando o KML

1. No painel **Lugares**, selecionar a pasta ou documento.
2. Botão direito → **Salvar local como…**
3. Escolher formato **KML** (não KMZ — KMZ é comprimido).
4. Salvar como `campus.kml`.

## Verificação Rápida

Abrir o arquivo `.kml` em editor de texto e confirmar:

- `xmlns="http://www.opengis.net/kml/2.2"` presente
- Cada nó tem `<Point>` com `<coordinates>`
- Rótulos `<name>` coincidem exatamente com os usados no código (`P1`, `P2`, …)
- Polígonos fechados: primeiro e último vértice iguais

## Altitude

- Altitude no KML é opcional. Se ausente, valor é 0.
- O simulador prioriza altitude SRTM 30m (quando disponível) sobre altitude do KML.
- Campo `altitude_srtm_m` em `GeographicPosition` é preenchido automaticamente se SRTM ativo.
- Diferença de altitude impacta `distance_3d_m` e portanto o FSPL calculado.

## Erros Comuns de KML

| Problema | Sintoma | Solução |
|----------|---------|---------|
| KMZ em vez de KML | `ParseError` ao abrir | Descompactar: renomear para `.zip`, extrair `doc.kml` |
| Namespace errado | Nenhum ponto encontrado | Verificar `xmlns` no elemento `<kml>` |
| Polígono não fechado | `shapely` buffer warning | Garantir que primeiro = último vértice em `<coordinates>` |
| Nome com espaço | `KeyError` no simulador | Usar `P1` não `Ponto 1` |
