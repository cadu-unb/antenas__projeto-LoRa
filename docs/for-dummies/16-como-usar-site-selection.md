# Como usar a Seleção de Torre (Site Selection)

Seleção de Torre responde a pergunta: **onde instalar a estação base para cobrir o maior número de sensores?**

O sistema avalia candidatos a torre e ranqueia por porcentagem de cobertura.

## Quando usar

- Você tem vários sensores LoRa no campo e precisa escolher onde colocar o gateway
- Quer comparar uma torre nova com uma já existente
- Quer saber como a altura da torre afeta a cobertura

## Passo a passo

### 1. Configurar os nós de campo

Preencha **Nó A**, **Nó B** e nós extras com as posições dos sensores que precisam de cobertura. Esses são os pontos que a torre vai atender.

### 2. Abrir o painel de Seleção de Torre

Clicar em **📡 Seleção de Torre** no Link Planner.

O painel abre abaixo da barra de topologia.

### 3. Adicionar candidatos

#### Por clique no mapa

1. Clicar **+ Candidato no mapa**
2. Clicar na posição desejada no mapa
3. O candidato aparece com marcador verde em forma de diamante

#### Via KML

Importar arquivo `.kml` com pontos cujo nome contenha **"torre"** ou **"tower"**:
- O sistema reconhece automaticamente como candidato existente
- Ícone amarelo: torre já existente
- Ícone verde: candidato novo

### 4. Ajustar altura

Cada candidato tem um slider de **Altura (m)**. Arraste para testar diferentes alturas de antena.

A cobertura recalcula automaticamente quando o slider muda (sem recarregar a página).

### 5. Calcular cobertura

Clicar **Calcular Cobertura**.

O sistema calcula o link budget entre cada candidato e cada nó de campo.

### 6. Interpretar o ranking

| Campo | Descrição |
|---|---|
| ⭐ Primeiro | Melhor candidato — maior cobertura |
| Cobertura (%) | Porcentagem de nós com margem > 0 dB |
| Status verde | ≥ 80% dos nós cobertos |
| Status amarelo | 50–79% |
| Status vermelho | < 50% |

### 7. Ver detalhe por candidato

Clicar em uma linha da tabela para ver o detalhe de cobertura por nó:
- Distância ao nó
- Margem de enlace (dB)
- Semáforo por nó

## Parâmetros da torre candidata

O cálculo usa parâmetros conservadores para a torre:
- Potência TX: 20 dBm
- Ganho de antena: 0 dBi (dipolo simples)
- Perda de cabo: 0 dB

A sensibilidade dos nós de campo e o ganho das antenas associadas são usados no lado receptor.

## KML: torres existentes

Para marcar uma torre existente no KML, nomeie o ponto com "torre" ou "tower":

```xml
<Placemark>
  <name>Torre Nordeste</name>
  <Point><coordinates>-46.50,-23.40,45.0</coordinates></Point>
</Placemark>
```

- Altitude no KML (`45.0` no exemplo) é importada como `height_m`
- `is_existing_tower = true` ativado automaticamente
- Ícone diferente no mapa (amarelo)

## Exportar resultado

Após calcular, clique **Exportar JSON** para baixar o cenário com `site_selection_result` preenchido. O JSON inclui o ranking completo com margens por nó.

## Limitações

- Modelo de propagação: FSPL puro (espaço livre) — sem terreno, prédios ou vegetação
- Sem otimização automática de posição (o sistema avalia os candidatos que você marcou, não sugere novas posições)
- Sem ray tracing urbano
- Candidatos não têm configuração avançada de antena nesta versão
