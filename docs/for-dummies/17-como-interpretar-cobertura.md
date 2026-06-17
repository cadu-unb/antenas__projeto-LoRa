# Como interpretar cobertura

Cobertura indica quantos nós de campo conseguem se comunicar com a torre candidata com margem positiva de enlace.

## O que é "coberto"?

Um nó está coberto quando:

```
margem de enlace = Rx (dBm) − sensibilidade (dBm) > 0 dB
```

Se a margem for negativa, o sinal chega abaixo do mínimo necessário — o nó **não está coberto**.

## Porcentagem de cobertura

```
cobertura (%) = (nós cobertos / total de nós) × 100
```

Exemplo: 3 de 4 nós cobertos → 75%.

## Semáforo de cobertura

| Cor | Cobertura | Interpretação |
|---|---|---|
| 🟢 Verde | ≥ 80% | Boa cobertura — a maioria dos nós alcança a torre |
| 🟡 Amarelo | 50–79% | Cobertura parcial — considerar reposicionar ou aumentar altura |
| 🔴 Vermelho | < 50% | Cobertura insuficiente — torre inadequada para esta área |

## Tabela de detalhe

Para cada nó de campo, a tabela exibe:

| Campo | O que significa |
|---|---|
| **Dist (km)** | Distância geodésica entre torre e nó |
| **Margem (dB)** | Quanto sinal sobra acima da sensibilidade mínima |
| **Status** | Verde / Amarelo / Vermelho conforme margem |

### Interpretar a margem por nó

| Margem | Semáforo | Significado prático |
|---|---|---|
| > 10 dB | Verde | Enlace robusto — funciona mesmo com obstáculos leves |
| 0–10 dB | Amarelo | Marginal — pode falhar em condições adversas |
| < 0 dB | Vermelho | Inviável — sinal insuficiente |

## Efeito da altura da torre

Aumentar a altura da torre **não muda** o FSPL diretamente (FSPL depende apenas de distância e frequência). O que muda:
- Menor obstrução física (linha de visada melhora em terreno irregular)
- Maior eficiência de antena de alta diretividade

Neste modelo (FSPL puro), a altura `height_m` é registrada para referência mas não altera o cálculo de propagação. Modelos com terreno (Longley-Rice, Okumura-Hata) usam a altura para penalidades de difração.

## Por que dois candidatos na mesma posição podem ter coberturas diferentes?

Porque os parâmetros dos nós de campo variam. Se o Nó A tem sensibilidade −137 dBm (SF12) e o Nó B tem −120 dBm (SF7), o candidato pode cobrir Nó A mas não Nó B — mesmo com os mesmos parâmetros de torre.

## Comparando candidatos

1. Candidato com maior cobertura aparece primeiro (⭐)
2. Empate em cobertura: ambos cobrem os mesmos nós — escolha pelo custo ou acessibilidade
3. Candidato "Torre existente" (importado via KML) aparece com ícone amarelo no mapa — útil para avaliar se a infraestrutura atual é suficiente

## Quando a cobertura não é suficiente

- Aumentar altura do candidato (slider)
- Adicionar candidatos em posições diferentes
- Melhorar antena dos nós de campo (maior ganho)
- Aumentar potência TX do nó de campo
- Considerar repetidores (topologia CHAIN ou MESH)
