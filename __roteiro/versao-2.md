# Roteiro de Apresentação — Projeto LoRa/LoRaWAN no Campus Darcy Ribeiro

**Projeto:** Sistema de antenas e planejamento de enlace LoRa/LoRaWAN para botões de emergência no Campus Darcy Ribeiro da UnB  
**Equipe:** Diogo Schwartz, João Victor e Carlos Eduardo  
**Objetivo da apresentação:** mostrar a motivação do projeto, a modelagem técnica das antenas e enlaces, e a plataforma computacional desenvolvida para apoiar simulações educacionais e estimativas de cobertura.

<!-- sugestão de imagem/ilustração: mapa aéreo do Campus Darcy Ribeiro com ícones simples indicando botões de emergência e um gateway central -->

---

## Abertura Geral

**[Fala: Diogo Schwartz]**

Bom dia/boa tarde, professor e banca.

Imaginem um estudante em dificuldade na BCE, às dez da noite. Ele aciona um botão de emergência. Esse botão não precisa transmitir vídeo nem áudio — precisa enviar apenas uma mensagem curta, confiável, que chegue até a central de segurança. E precisa funcionar com bateria, sem infraestrutura de rede celular.

Esse é o problema que este projeto resolve.

Vamos apresentar uma análise técnica completa de uma rede LoRa/LoRaWAN para botões de emergência no Campus Darcy Ribeiro da UnB — investigando se o enlace é viável, quais módulos e antenas oferecem melhor desempenho, e como esse conhecimento pode ser acessado por meio de uma ferramenta computacional.

O trabalho foi dividido em três frentes:

- **Diogo Schwartz** — definição do problema, estruturação técnica e pesquisa complementar;
- **João Victor** — modelagem em MATLAB, simulações de enlace e comparação de cenários;
- **Carlos Eduardo** — plataforma Web educacional para modelagem de antenas e estimativa de cobertura.

<!-- sugestão de imagem/ilustração: diagrama em três blocos com os nomes e responsabilidades -->

---

# PARTE 1 — Contextualização e Fundamentação da Rede

## 1. Problema, motivação e cenário

**[Fala: Diogo Schwartz]**

LoRa/LoRaWAN é a tecnologia escolhida por três razões que se encaixam diretamente no problema:

1. **Longo alcance** em ambientes abertos e semiabertos — adequado para o campus;
2. **Baixo consumo** — dispositivos de campo alimentados por bateria funcionam por meses ou anos;
3. **Baixa taxa de dados** — suficiente para mensagens curtas de alarme.

O cenário usa pontos reais do Campus Darcy Ribeiro: FACE, BCE, Beijódromo, IB, IQ, ICC Sul, ICC Norte, CO e SG, com latitude, longitude e altitude conhecidas. A análise não fica no abstrato — cada enlace tem distância e geometria reais.

O gateway foi escolhido automaticamente pelo MATLAB usando o critério de minimizar a maior distância 3D até os demais pontos. O resultado indicou a **BCE** como melhor posição, com distância média de **617,75 m** e distância máxima de **886,56 m** no conjunto avaliado. Não foi uma escolha arbitrária.

<!-- sugestão de imagem/ilustração: mapa com os pontos do campus; destaque BCE como gateway; fluxo "botão → módulo LoRa → gateway/central" -->

## 2. Objetivos técnicos

**[Fala: Diogo Schwartz]**

Quatro objetivos estruturam o trabalho:

1. **Modelar os pontos do campus** com coordenadas geográficas reais;
2. **Comparar módulos LoRa** — RFM95W, LRO2 ASR6601 e E220-900T22D;
3. **Comparar seis modelos de antena**, sem assumir previamente qual é a melhor;
4. **Avaliar o link budget** considerando potência, ganho efetivo, perdas e margem de recepção.

Um ponto central do projeto: a antena não é tratada como um número fixo de ganho. Consideramos padrão de radiação, diretividade, orientação e robustez multidirecional. Uma antena que performa bem em um enlace ponto a ponto pode ser ruim para um gateway recebendo sinais de vários azimutes simultaneamente.

<!-- sugestão de imagem/ilustração: antena omnidirecional recebendo de vários pontos vs. antena diretiva apontando para um só -->

## 3. Transição para a engenharia de antenas

**[Transição para João Victor — Diogo Schwartz]**

Com o cenário e os objetivos definidos, a próxima etapa foi transformar esse problema em modelo computacional: quais parâmetros usar, como calcular a geometria dos enlaces e como comparar antenas de forma sistemática. Essa parte ficou com o João Victor.

---

# PARTE 2 — Engenharia de Antenas e Simulação em MATLAB

## 4. Planejamento das simulações

**[Fala: João Victor]**

A minha parte foi estruturar as simulações em MATLAB de forma que os resultados fossem reais o suficiente para orientar decisões técnicas, mas organizados de forma que possamos trocar qualquer componente sem reescrever a lógica.

A simulação está dividida em quatro bases independentes:

1. **Pontos do campus** — nome, latitude, longitude, altitude;
2. **Módulos LoRa** — frequência, potência TX, sensibilidade RX, consumo;
3. **Antenas** — ganho máximo, HPBW, polarização, diretividade, modelo de padrão;
4. **Cálculo de enlace** — geometria ENU, perda de percurso, ganho efetivo direcional.

<!-- sugestão de imagem/ilustração: quatro blocos da arquitetura MATLAB -->

## 5. Modelos de antenas avaliados

**[Fala: João Victor]**

Foram avaliados seis modelos:

| Antena | Ganho máximo | Característica |
|---|---:|---|
| `Dipole_HalfWave` | 2,15 dBi | Omnidirecional, referência de meia-onda |
| `Monopole_GroundPlane` | 5,15 dBi | Omnidirecional sobre plano de terra |
| `Helical_Axial` | 11 dBi | Direcional, alta faixa, circularmente polarizado |
| `Parabolic_Dish` | 20 dBi | Altamente direcional, ganho máximo entre os seis |
| `PCB_Compact` | ~1 dBi | Compacta, integrada ao circuito |
| `Commercial_Omni_6dBi` | 6 dBi | Omnidirecional vertical, referência prática do kit E220 |

O ponto crítico é que o ganho efetivo depende da direção. A simulação calcula `Gtx(θ, φ)` e `Grx(θ, φ)` para cada enlace — não usa só o valor máximo.

<!-- sugestão de imagem/ilustração: painel com os padrões simplificados das seis antenas -->

## 6. Geometria dos enlaces

**[Fala: João Victor]**

As coordenadas geográficas são convertidas para o sistema ENU — leste, norte e altitude relativa ao gateway. Com isso, para cada ponto de alarme calculamos:

- distância 2D e 3D;
- azimute;
- ângulo de elevação;
- ângulos θ e φ no sistema da antena transmissora e da receptora.

Essa etapa é fundamental para antenas diretivas. Uma helicoidal ou parabólica só entrega ganho máximo quando o boresight aponta para o destino. Desalinhada, a margem cai — às vezes abaixo do mínimo de recepção.

<!-- sugestão de imagem/ilustração: diagrama ENU com vetor transmissor-gateway, azimute e elevação -->

## 7. Link budget e resultados numéricos

**[Fala: João Victor]**

A perda de espaço livre foi calculada por:

```
FSPL(dB) = 32,44 + 20 log₁₀(f_MHz) + 20 log₁₀(d_km)
```

E a potência recebida por:

```
Prx = Ptx + Gtx(θ,φ) + Grx(θ,φ) - FSPL - perdas
```

Frequência: **915 MHz**. Perdas adicionais conservadoras:

| Componente | Perda |
|---|---:|
| Cabo TX | 0,5 dB |
| Cabo RX | 0,5 dB |
| Obstáculos leves / instalação | 8 dB |
| Margem de fading | 10 dB |
| **Total** | **19 dB** |

Mesmo com essas perdas, as margens obtidas foram confortáveis para todos os pontos do campus. O ranking agregado indicou:

- **Melhor antena para transmissores e gateway:** `Commercial_Omni_6dBi`
- **Melhor módulo em margem agregada:** `LRO2_ASR6601`
- **Melhor módulo em consumo:** `RFM95W_915MHz`

<!-- sugestão de imagem/ilustração: gráfico de barras do ranking ou tabela destacando os resultados -->

## 8. Interpretação técnica

**[Fala: João Victor]**

O resultado mais importante não é o número em si — é o que ele revela.

Helicoidal axial e parabólica têm ganhos muito maiores que os 6 dBi da omni comercial. Mas num gateway que precisa receber sinais de todos os pontos do campus, o ganho direcional não ajuda: o boresight não pode apontar para todos ao mesmo tempo.

A `Commercial_Omni_6dBi` vence porque equilibra ganho suficiente com cobertura total em azimute. Isso é o que chamamos de robustez multidirecional — um critério que a maioria dos projetos ignora quando escolhe antenas só pelo número de dBi.

Antenas diretivas continuam sendo boas escolhas em enlaces ponto a ponto fixos e alinhados. Mas para uma rede de emergência com múltiplos transmissores distribuídos, a omni vence.

<!-- sugestão de imagem/ilustração: P2P com parabólica alinhada vs. gateway recebendo múltiplos azimutes com omni -->

## 9. Demonstração MATLAB

**[Fala: João Victor]**

Na demonstração, o fluxo que a banca verá é:

1. **Pontos do campus e gateway** — tabela com coordenadas e escolha automática da BCE;
2. **Geometria dos enlaces** — distâncias, azimutes, elevações para cada ponto;
3. **Padrões de antena** — gráficos de `antennaPattern.m` para cada modelo;
4. **Comparação de cenários** — margens de enlace em A (antenas iguais), B (gateway omni, TX variado), C (TX diretivos alinhados), D (TX diretivos desalinhados) e E (módulos LoRa);
5. **Ranking final** — agregado por margem mínima, média e robustez.

O ponto a destacar na demo: mostrar Cenário C vs. D para evidenciar que a penalidade de desalinhamento é real e quantificável.

<!-- sugestão de imagem/ilustração: captura da janela MATLAB com tabela de resultados e ranking -->

## 10. Transição para a plataforma Web

**[Transição para Carlos Eduardo — João Victor]**

O MATLAB deu a análise técnica completa. Em paralelo, o Carlos desenvolveu uma plataforma que transforma esses conceitos em uma ferramenta visual e interativa — onde qualquer pessoa pode criar antenas, estimar enlaces e explorar como as escolhas afetam a cobertura.

---

# PARTE 3 — Plataforma Computacional e Simulador Web

## 11. Arquitetura da aplicação

**[Fala: Carlos Eduardo]**

A plataforma foi construída para tornar acessível o que o MATLAB mostra em detalhe técnico.

Três módulos principais:

1. **Sandbox** — criar e pré-visualizar antenas interativamente;
2. **Biblioteca** — salvar, exportar e importar especificações de antenas;
3. **Link Planner** — montar cenários com nós geográficos e calcular link budget.

Backend: **FastAPI** com schemas **Pydantic**. Frontend: **HTML, CSS e JavaScript puro** — sem framework. Dados persistidos em JSON, auditáveis e portáveis.

<!-- sugestão de imagem/ilustração: diagrama frontend → FastAPI → Pydantic → arquivos JSON -->

## 12. Objetos centrais

**[Fala: Carlos Eduardo]**

A plataforma gira em torno de três objetos:

- **`AntennaSpec`** — tipo, frequência, geometria, solver, resultados, e campos físicos: ganho máximo, HPBW, polarização, diretividade;
- **`NodeSpec`** — latitude, longitude, altura, potência TX, sensibilidade RX, perdas, orientação;
- **`LinkScenario`** — conjunto de nós, frequência, modelo de propagação e resultados calculados.

Essa separação é importante na prática: uma antena criada no Sandbox pode ser salva na Biblioteca e reutilizada em qualquer cenário do Link Planner — sem redigitar os parâmetros.

<!-- sugestão de imagem/ilustração: fluxo Sandbox → Biblioteca → Link Planner com os três objetos -->

## 13. Demonstração Web

**[Fala: Carlos Eduardo]**

Na demonstração, vamos percorrer o fluxo completo:

**Sandbox:**
1. Selecionar tipo de antena — dipolo, monopolo, helicoidal, parabólica, PCB compacta ou omni comercial de 6 dBi;
2. Ajustar frequência e parâmetros geométricos;
3. Executar simulação rápida;
4. Observar ganho, impedância, SWR, eficiência e diagrama de radiação.

**Biblioteca:**
1. Salvar a antena criada;
2. Mostrar lista de antenas salvas com campos físicos (HPBW, polarização, direcionalidade);
3. Exportar como JSON — campos preservados.

**Link Planner:**
1. Configurar dois nós com coordenadas reais do campus;
2. Associar antenas da Biblioteca;
3. Calcular margem de enlace — distância 3D, FSPL, ganho efetivo, semáforo de viabilidade;
4. Alterar orientação de uma antena diretiva e mostrar queda no ganho efetivo.

Esse último passo é o mais didático: a mesma antena com boresight alinhado e desalinhado, mostrando concretamente o que o João mostrou no MATLAB.

<!-- sugestão de imagem/ilustração: capturas das três telas — Sandbox, Biblioteca e Link Planner -->

## 14. Limites assumidos e decisões de projeto

**[Fala: Carlos Eduardo]**

A plataforma é uma ferramenta educacional e de apoio ao planejamento inicial. Seus limites são conscientemente escolhidos:

- Não faz ray tracing urbano com detecção de obstáculos;
- KML com polígonos é tratado como informação visual, não como barreira de propagação;
- Parabólicas usam aproximação de abertura, não MoM eletromagnético completo;
- Propagação usa FSPL por padrão, com opções de Okumura-Hata e Longley-Rice disponíveis.

Esses limites não são falhas — são escolhas que mantêm a ferramenta usável sem exigir dados de terreno ou processamento pesado.

<!-- sugestão de imagem/ilustração: matriz MATLAB (análise detalhada) vs. Web (ferramenta interativa educacional) -->

## 15. Conclusão técnica

**[Fala: Carlos Eduardo]**

O enlace LoRa no campus Darcy Ribeiro é viável para mensagens de emergência com módulos e antenas adequados. A análise mostrou margens confortáveis mesmo com 19 dB de perdas conservadoras.

A plataforma Web entrega esses conceitos de forma interativa: qualquer pessoa pode reproduzir os cenários, testar novas combinações e visualizar como parâmetros afetam a cobertura.

## 16. Fechamento

**[Fala: Diogo Schwartz]**

Este projeto responde à pergunta que colocamos no início: é possível construir uma rede de emergência confiável no Campus Darcy Ribeiro com LoRa?

A resposta é sim — com a escolha certa de antena e módulo. Mas a contribuição do projeto vai além do "sim": mostramos **por que** a omni comercial de 6 dBi vence, com análise geométrica, cálculo de ganho direcional e ranking quantitativo. E entregamos uma ferramenta que permite explorar esse raciocínio de forma interativa.

Obrigado. Estamos à disposição para perguntas.

<!-- sugestão de imagem/ilustração: slide final com três evidências: (1) margens confortáveis — números do link budget, (2) omni 6 dBi robusta — ranking, (3) plataforma funcional — captura Web -->

---

# Roteiro rápido de demonstração

## Demonstração 1 — MATLAB

**Responsável:** João Victor

1. Abrir `main_LoRa_AntennaComparison.m`;
2. Mostrar pontos do campus e escolha automática da BCE como gateway;
3. Exibir tabela de geometria dos enlaces (distâncias, azimutes, elevações);
4. Mostrar padrões de radiação das seis antenas;
5. Executar comparação de cenários — destacar Cenário C (alinhado) vs. D (desalinhado);
6. Exibir ranking final com interpretação automática.

## Demonstração 2 — Plataforma Web

**Responsável:** Carlos Eduardo

1. Sandbox: criar omni comercial de 6 dBi → mostrar ganho, HPBW, diagrama;
2. Salvar na Biblioteca → mostrar campos físicos preservados;
3. Link Planner: configurar enlace com coordenadas reais do campus;
4. Calcular margem → semáforo verde;
5. Trocar para antena diretiva desalinhada → mostrar queda no ganho efetivo e impacto na margem.

## Fechamento coordenado

**Responsável:** Diogo Schwartz

Sintetizar os três pontos de evidência:
- Problema real e bem delimitado;
- Análise quantitativa com resultados claros (omni vence por robustez multidirecional);
- Ferramenta educacional que torna os conceitos acessíveis e reproduzíveis.
