# Como usar o Sandbox

O Sandbox é a tela principal de criação de antenas. Organizado em 4 painéis.

## Painel 1 — Visual físico

SVG gerado automaticamente conforme o tipo de antena selecionado.

| Tipo | Visual |
|---|---|
| Dipolo | Dois braços horizontais com ponto de alimentação central |
| Monopolo | Haste vertical sobre plano de terra |
| Helicoidal | Espiral com eixo vertical |
| Parabólica | Refletor côncavo com feed no foco |

O SVG atualiza em tempo real conforme você altera os parâmetros.

## Painel 2 — Parâmetros

Dividido em blocos:

**Frequência:** frequência de operação em MHz. Para LoRa BR/AU: 915 MHz. Para LoRa EU: 868 MHz.

**Geometria:** depende do tipo:
- Dipolo: comprimento total (padrão: λ/2)
- Monopolo: altura da haste (padrão: λ/4)
- Helicoidal: número de espiras, circunferência, ângulo de passo
- Parabólica: diâmetro do refletor, eficiência de abertura

**Solver:** modo de simulação. Ver `10-como-rodar-simulacao.md`.

## Painel 3 — Resultado EM

| Campo | Unidade | O que significa |
|---|---|---|
| Ganho | dBi | Ganho máximo sobre antena isotrópica |
| Impedância | Ω | Impedância de entrada (parte real) |
| SWR | — | Standing Wave Ratio (1.0 = casado perfeito) |
| Eficiência | % | Fração da potência irradiada vs. entregue |

SWR < 2.0 é aceitável para a maioria dos sistemas. SWR > 3.0 indica descasamento.

## Painel 4 — Diagrama de irradiação

Diagrama polar 2D no plano azimutal (corte horizontal).

- Anel externo = ganho máximo
- Lóbulo principal aponta para o eixo de maior irradiação
- Lóbulos laterais e traseiro: presentes em antenas direcionais

## Fluxo completo

1. Selecionar tipo de antena
2. Definir frequência
3. Ajustar geometria (ou deixar padrão λ/2, λ/4)
4. Clicar **Calcular Preview**
5. Ver resultado nos Painéis 3 e 4
6. Se satisfeito: clicar **Salvar na Biblioteca**

## Modo Rápido vs. avançado

Modo Rápido (padrão): resposta imediata, resultado analítico.
Modos Padrão/Preciso: resultado via MoM ou abertura, enfileirado como job assíncrono.

Ver `10-como-rodar-simulacao.md` para detalhes.
