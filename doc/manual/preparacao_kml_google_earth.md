# Preparação de KML no Google Earth

## Pré-requisitos

- Google Earth Pro (gratuito) ou Google Earth Web
- Coordenadas dos nós em WGS84 (latitude/longitude decimal)

## Arquivo de Referência

O repositório inclui um KML de exemplo do campus Darcy Ribeiro (UnB):

```
_path/kml/mascara_campus_darcy_ribeiro.kml
```

Use-o como modelo de estrutura para criar KMLs de outros campi.

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

    <!-- Prédio (obstáculo com atenuação RF) -->
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

    <!-- Obstáculo genérico (sem atenuação extra definida) -->
    <Placemark>
      <name>OBSTACLE</name>
      <Polygon>
        ...
      </Polygon>
    </Placemark>

    <!-- Limite do campus (só visual, não impacta cálculo RF) -->
    <Placemark>
      <name>CAMPUS</name>
      <Polygon>
        ...
      </Polygon>
    </Placemark>

  </Document>
</kml>
```

**Ordem das coordenadas:** `longitude,latitude,altitude` — diferente da notação lat/lon usual.

## Criando Marcadores de Nós (P1–P8)

1. Abrir Google Earth Pro.
2. Menu **Adicionar → Marcador de local**.
3. Posicionar o pino no mapa ou digitar lat/lon em **Latitude/Longitude**.
4. Em **Nome**, digitar exatamente `P1`, `P2`, … `P8`.
   - Sem espaços: `P1` não `Ponto 1`.
   - Case-sensitive: `P1` ≠ `p1`.
5. Clicar OK.
6. Repetir para cada nó. Mínimo 2 nós para calcular enlaces.

## Criando Polígonos

### BUILDING (prédio com atenuação)

1. Menu **Adicionar → Polígono**.
2. Desenhar o contorno do prédio clicando nos vértices.
3. Em **Nome**, digitar `BUILDING`.
4. Clicar OK.
5. Repetir para cada prédio — todos com o mesmo nome `BUILDING`.

### OBSTACLE (obstáculo genérico)

Mesmo processo com nome `OBSTACLE`.

### CAMPUS (limite de área)

Mesmo processo com nome `CAMPUS`.
Polígonos `CAMPUS` aparecem no mapa mas **não afetam o cálculo RF**.

## Exportando como KML

**Importante:** exportar como `.kml`, não `.kmz`. KMZ é um arquivo comprimido e o simulador não descomprime automaticamente.

1. No painel **Lugares**, selecionar a pasta ou documento raiz.
2. Botão direito → **Salvar local como…**
3. Escolher formato **KML** (não KMZ).
4. Salvar como `campus.kml`.

## Verificação Rápida

Abrir o arquivo `.kml` em editor de texto e confirmar:

- `xmlns="http://www.opengis.net/kml/2.2"` presente na tag `<kml>`
- Cada nó tem `<Point>` com `<coordinates>`
- Rótulos `<name>` são exatamente `P1`, `P2`, … (sem espaços ou variações)
- Polígonos fechados: primeiro vértice = último vértice em `<coordinates>`
- Arquivo inicia com `<?xml version="1.0"` — não deve haver BOM (byte order mark)

## Altitude

- Altitude no KML é opcional. Se ausente, valor é 0.
- O simulador prioriza altitude SRTM 30m (quando disponível) sobre altitude do KML.
- Diferença de altitude entre nós impacta `distance_3d_m` e portanto o FSPL calculado.
- Em ambiente offline (Docker sem acesso à internet), altitude cai para 0 automaticamente.

## Validação de Nomes de Pontos

O simulador aceita qualquer string como rótulo de nó, mas recomenda-se `P1`–`P8`.
Restrições práticas:

| Regra | Correto | Errado |
|-------|---------|--------|
| Sem espaços | `P1` | `Ponto 1` |
| Sem acentos | `P1` | `Ponto_1_leste` (funciona, mas evitar) |
| Case-sensitive | `P1` | `p1` |
| Único por arquivo | Um `P1` por KML | Dois elementos com nome `P1` |

## Mensagens de Erro Comuns no Upload

| Mensagem | Causa | Solução |
|----------|-------|---------|
| `Erro ao processar KML: ...` + ParseError | Arquivo KMZ ou XML malformado | Exportar como `.kml`; verificar estrutura XML |
| `Nenhum ponto encontrado` | Namespace errado ou `<Placemark>` sem `<Point>` | Verificar `xmlns="http://www.opengis.net/kml/2.2"` |
| `At least two KML points required` | Menos de 2 `<Placemark>` tipo Point | Adicionar mais marcadores de nó |
| `KeyError: P3` | Código referencia `P3` mas KML não tem ponto com `<name>P3</name>` | Verificar nome exato no KML |
| Polígono aparece como ponto no mapa | `<Polygon>` com menos de 3 vértices distintos | Redesenhar polígono |
| `shapely` warning sobre polígono inválido | Polígono não fechado | Garantir primeiro = último vértice |
