# Roteiro de Apresentação — Projeto LoRa/LoRaWAN no Campus Darcy Ribeiro

**Projeto:** Sistema de antenas e planejamento de enlace LoRa/LoRaWAN para botões de emergência no Campus Darcy Ribeiro da UnB  
**Equipe:** Diogo Schwartz, João Victor e Carlos Eduardo  
**Objetivo da apresentação:** mostrar a motivação do projeto, a modelagem técnica das antenas e enlaces, e a plataforma computacional desenvolvida para apoiar simulações educacionais e estimativas de cobertura.

<!-- sugestão de imagem/ilustração: mapa aéreo do Campus Darcy Ribeiro com ícones simples indicando botões de emergência e um gateway central -->

---

## Abertura Geral

**[Fala: Diogo Schwartz]**

Bom dia/boa tarde, professor e banca. Nós vamos apresentar o projeto de uma rede LoRa/LoRaWAN aplicada a um sistema de botões de emergência no Campus Darcy Ribeiro da UnB.

A ideia central é simples: em pontos estratégicos do campus, um botão de emergência aciona um módulo LoRa, que envia uma mensagem para uma central de segurança representada por um gateway fixo. A partir disso, nosso projeto investiga se esse enlace é tecnicamente viável e quais combinações de módulos e antenas oferecem melhor desempenho.

O trabalho foi dividido em três frentes complementares:

- eu, Diogo Schwartz, fiquei responsável pela definição dos objetivos, estruturação das ideias principais e pesquisa técnica complementar;
- João Victor ficou responsável pelo planejamento das simulações computacionais e pela modelagem robusta em MATLAB;
- Carlos Eduardo ficou responsável pelo desenvolvimento da plataforma computacional Web, usada como ferramenta educacional de modelagem simplificada e estimativa de cobertura.

<!-- sugestão de imagem/ilustração: diagrama em três blocos com os nomes Diogo, João e Carlos e suas responsabilidades principais -->

---

# PARTE 1 — Contextualização e Fundamentação da Rede

## 1. Problema e motivação

**[Fala: Diogo Schwartz]**

O problema que motivou o projeto é a necessidade de comunicação confiável em situações de emergência dentro de um campus grande, aberto e com pontos espalhados. Em uma situação crítica, o sistema precisa transmitir uma mensagem curta, de baixo volume de dados, mas com boa robustez e alcance.

Nesse contexto, a tecnologia LoRa/LoRaWAN é uma alternativa adequada porque combina três características importantes:

1. **Longo alcance**, especialmente em ambientes abertos ou semiabertos;
2. **Baixo consumo de energia**, essencial para dispositivos de campo alimentados por bateria;
3. **Baixa taxa de dados**, suficiente para mensagens curtas de alarme.

Aqui, o objetivo não é transmitir áudio, vídeo ou grandes volumes de dados. O objetivo é garantir que uma mensagem de alerta consiga chegar até a central com margem de enlace suficiente.

<!-- sugestão de imagem/ilustração: fluxo simples "botão de emergência → módulo LoRa → gateway/central de segurança" -->

## 2. Cenário de aplicação no campus

**[Fala: Diogo Schwartz]**

O cenário estudado usa pontos reais do Campus Darcy Ribeiro, como FACE, BCE, Beijódromo, IB, IQ, ICC Sul, ICC Norte, CO e SG. Esses pontos possuem latitude, longitude e altitude, permitindo que a análise não fique apenas conceitual.

O gateway foi escolhido automaticamente no MATLAB pelo critério de minimizar a maior distância 3D até os demais pontos. Nesse critério, o ponto BCE apareceu como melhor candidato, com distância média de aproximadamente **617,75 m** e distância máxima de aproximadamente **886,56 m** no conjunto avaliado.

Isso é importante porque mostra que a escolha do gateway não foi arbitrária: ela foi baseada em uma análise geométrica do campus.

<!-- sugestão de imagem/ilustração: mapa com os pontos FACE, BCE, Beijódromo, IB, IQ, ICC Sul, ICC Norte, CO e SG; destacar BCE como gateway -->

## 3. Objetivos técnicos do projeto

**[Fala: Diogo Schwartz]**

Os objetivos técnicos foram organizados em quatro blocos:

1. **Modelar os pontos do campus**, usando coordenadas geográficas reais;
2. **Comparar módulos LoRa**, como RFM95W, LRO2 ASR6601 e E220-900T22D;
3. **Comparar diferentes antenas**, sem assumir previamente qual é a melhor;
4. **Avaliar o orçamento de enlace**, considerando potência transmitida, ganho das antenas, perdas, sensibilidade do receptor e margem final.

Um ponto importante do projeto é que ele não trata a antena apenas como um número fixo de ganho. Nós consideramos padrão de radiação, diretividade, orientação e robustez para múltiplas direções, porque uma antena que funciona muito bem em um enlace ponto a ponto pode não ser a melhor para um gateway que precisa receber sinais vindos de vários azimutes.

<!-- sugestão de imagem/ilustração: comparação visual entre antena omnidirecional recebendo de vários pontos e antena diretiva apontando para apenas uma direção -->

## 4. Transição para a engenharia de antenas

**[Transição para João Victor — Diogo Schwartz]**

Com essa motivação e o cenário definidos, a próxima etapa foi transformar o problema em um modelo de engenharia: quais antenas comparar, quais parâmetros usar, como calcular a geometria dos enlaces e como avaliar a margem de comunicação. Essa parte foi desenvolvida pelo João Victor, com foco nas simulações em MATLAB.

---

# PARTE 2 — Engenharia de Antenas e Simulação em MATLAB

## 5. Planejamento das simulações

**[Fala: João Victor]**

A minha parte do projeto foi estruturar as simulações computacionais em MATLAB, buscando uma modelagem educacional, mas fisicamente coerente, para comparar antenas e módulos LoRa.

O primeiro cuidado foi separar o problema em bases independentes:

1. **Base de pontos do campus**, com nome, latitude, longitude e altitude;
2. **Base de módulos LoRa**, com frequência, potência, sensibilidade e dados de consumo;
3. **Base de antenas**, com ganho máximo, largura de feixe, polarização, diretividade e modelo de padrão de radiação;
4. **Cálculo de enlace**, usando geometria, perda de espaço livre e ganho efetivo das antenas.

Essa separação facilita a comparação, porque podemos trocar módulo, antena ou posição do gateway sem reescrever a lógica inteira.

<!-- sugestão de imagem/ilustração: arquitetura da simulação MATLAB em quatro blocos: pontos, módulos, antenas e cálculo de enlace -->

## 6. Modelos de antenas avaliados

**[Fala: João Victor]**

Foram avaliados seis modelos de antena:

| Antena | Característica principal |
|---|---|
| `Dipole_HalfWave` | Dipolo de meia onda, omnidirecional no plano horizontal, ganho aproximado de 2,15 dBi |
| `Monopole_GroundPlane` | Monopolo sobre plano de terra, ganho ideal de 5,15 dBi |
| `Helical_Axial` | Helicoidal axial, direcional, ganho aproximado de 11 dBi |
| `Parabolic_Dish` | Parabólica/diretiva, ganho alto, em torno de 20 dBi no modelo usado |
| `PCB_Compact` | Antena compacta integrada ao circuito, ganho baixo, quase omnidirecional |
| `Commercial_Omni_6dBi` | Antena comercial omnidirecional vertical de 6 dBi, referência prática do kit E220 |

O ponto principal é que o ganho efetivo depende da direção. Por isso, a simulação calcula `Gtx(theta, phi)` e `Grx(theta, phi)` em vez de usar somente o ganho máximo.

<!-- sugestão de imagem/ilustração: painel com miniaturas ou padrões simplificados das seis antenas comparadas -->

## 7. Geometria dos enlaces

**[Fala: João Victor]**

Depois de escolher o gateway, o MATLAB converte as coordenadas geográficas para coordenadas locais ENU: leste, norte e altitude relativa.

Com isso, para cada ponto de alarme em relação ao gateway, calculamos:

- distância 2D;
- distância 3D;
- azimute;
- ângulo de elevação;
- ângulos `theta` e `phi` no sistema da antena transmissora;
- ângulos `theta` e `phi` no sistema da antena receptora.

Essa etapa é essencial para antenas diretivas. Uma antena helicoidal ou parabólica só entrega seu ganho máximo quando o boresight está apontado para o destino. Se estiver desalinhada, a margem de enlace cai.

<!-- sugestão de imagem/ilustração: diagrama ENU mostrando eixos leste, norte e altitude, vetor transmissor-gateway, azimute e elevação -->

## 8. Demonstração MATLAB — sequência sugerida

**[Fala: João Victor]**

Na demonstração em MATLAB, a sequência recomendada é:

1. Abrir `main_LoRa_AntennaComparison.m`;
2. Mostrar que ele carrega os pontos do campus com `loadCampusPoints.m`;
3. Mostrar a escolha automática do gateway por `chooseGateway.m`;
4. Exibir a tabela de coordenadas ENU e geometria dos enlaces;
5. Mostrar os modelos de antena em `loadAntennaModels.m`;
6. Mostrar `antennaPattern.m`, onde o ganho angular é calculado;
7. Executar os cenários em `compareScenarios.m`;
8. Exibir os rankings em `rankConfigurations.m`;
9. Mostrar a discussão automática final.

Durante a demonstração, é importante destacar que o MATLAB compara os cenários:

- **Cenário A:** mesma antena no transmissor e no gateway;
- **Cenário B:** gateway omnidirecional e transmissores variados;
- **Cenário C:** transmissores diretivos apontados para o gateway;
- **Cenário D:** transmissores diretivos desalinhados;
- **Cenário E:** comparação entre módulos LoRa.

<!-- sugestão de imagem/ilustração: captura da janela MATLAB com tabelas de geometria, resultados e ranking final -->

## 9. Link budget e resultados numéricos

**[Fala: João Victor]**

O cálculo de link budget usa a fórmula de perda em espaço livre:

```text
FSPL(dB) = 32,44 + 20 log10(f_MHz) + 20 log10(d_km)
```

E a potência recebida é estimada por:

```text
Prx = Ptx + Gtx + Grx - FSPL - perdas
```

No exemplo principal, a frequência usada foi **915 MHz**. O script inclui perdas de cabo, perdas extras e margem de fading. No cenário demonstrado, foram considerados:

- 0,5 dB de perda de cabo no transmissor;
- 0,5 dB de perda de cabo no receptor;
- 8 dB de perda extra por instalação/obstáculos leves;
- 10 dB de margem de fading.

Isso totaliza **19 dB** de perdas adicionais conservadoras.

<!-- sugestão de imagem/ilustração: equação visual do link budget com blocos Ptx + Gtx + Grx - FSPL - perdas = Prx -->

Mesmo com essas perdas, as margens obtidas para os pontos do campus ficaram confortáveis no cenário modelado. O ranking agregado indicou:

- melhor antena para transmissores: `Commercial_Omni_6dBi`;
- melhor antena para gateway: `Commercial_Omni_6dBi`;
- melhor módulo em margem agregada: `LRO2_ASR6601`;
- módulo com melhor consumo entre os dados disponíveis: `RFM95W_915MHz`.

<!-- sugestão de imagem/ilustração: gráfico de barras ou tabela destacando Commercial_Omni_6dBi como melhor antena agregada e LRO2_ASR6601 como melhor módulo em margem -->

## 10. Interpretação técnica

**[Fala: João Victor]**

Um resultado importante é que antenas muito diretivas, como helicoidal axial e parabólica, podem ter ganhos altos, mas exigem alinhamento. Para um gateway único recebendo sinais de vários pontos do campus, uma antena omnidirecional comercial de 6 dBi tende a ser mais robusta.

Isso não significa que antenas diretivas sejam ruins. Elas podem ser excelentes em enlaces ponto a ponto. Mas para uma rede de emergência com múltiplos pontos distribuídos, a robustez multidirecional se torna um critério decisivo.

<!-- sugestão de imagem/ilustração: dois cenários lado a lado: enlace ponto a ponto com parabólica alinhada e gateway recebendo múltiplos azimutes com antena omnidirecional -->

## 11. Transição para a plataforma Web

**[Transição para Carlos Eduardo — João Victor]**

Com o MATLAB, nós conseguimos uma análise mais completa dos modelos, dos cenários e dos rankings. Em paralelo, o Carlos desenvolveu uma plataforma Web para transformar esses conceitos em uma ferramenta visual, interativa e educacional, permitindo testar antenas, salvar modelos e estimar enlaces de forma mais acessível.

---

# PARTE 3 — Plataforma Computacional e Simulador Web

## 12. Arquitetura da aplicação

**[Fala: Carlos Eduardo]**

A minha parte foi desenvolver uma plataforma computacional Web para apoiar a modelagem simplificada de antenas e o planejamento de enlace LoRa.

A aplicação foi estruturada em três módulos principais:

1. **Sandbox**, para criar e pré-visualizar antenas;
2. **Biblioteca**, para salvar, importar e exportar especificações de antenas;
3. **Link Planner**, para montar cenários com nós geográficos e calcular o link budget.

Do ponto de vista técnico, o backend usa **FastAPI** com schemas **Pydantic**, e o frontend é feito com **HTML, CSS e JavaScript puro**, sem framework. Os dados são persistidos em arquivos JSON, o que facilita auditoria e reuso durante o projeto.

<!-- sugestão de imagem/ilustração: diagrama da arquitetura Web com frontend, FastAPI, schemas Pydantic e arquivos JSON -->

## 13. Objetos centrais da plataforma

**[Fala: Carlos Eduardo]**

A plataforma gira em torno de três objetos principais:

- `AntennaSpec`, que representa uma antena com tipo, frequência, geometria, material, solver, resultados e campos físicos como ganho, HPBW, polarização e diretividade;
- `NodeSpec`, que representa um ponto da rede com latitude, longitude, altura, potência, sensibilidade, perdas e orientação;
- `LinkScenario`, que representa o cenário de enlace, com nós, frequência, modelo de propagação, resultados e topologias.

Essa separação permite que uma antena criada no Sandbox seja salva na Biblioteca e reutilizada depois no Link Planner.

<!-- sugestão de imagem/ilustração: fluxo "Sandbox → Biblioteca → Link Planner" com os objetos AntennaSpec, NodeSpec e LinkScenario -->

## 14. Demonstração Web — Sandbox

**[Fala: Carlos Eduardo]**

Na demonstração do Sandbox, a sequência sugerida é:

1. Abrir a página principal da aplicação;
2. Escolher o tipo de antena, por exemplo dipolo, monopolo, helicoidal, parabólica, PCB compacta ou omnidirecional comercial de 6 dBi;
3. Ajustar frequência e parâmetros geométricos;
4. Executar o modo rápido de simulação;
5. Mostrar os resultados:
   - ganho em dBi;
   - impedância;
   - SWR;
   - eficiência;
   - padrão de radiação simplificado.

O Sandbox não substitui um simulador eletromagnético completo. Ele foi pensado como uma ferramenta educacional para entender como mudanças de parâmetros alteram o comportamento aproximado da antena.

<!-- sugestão de imagem/ilustração: captura do Sandbox mostrando formulário de antena, resultados de ganho/impedância/SWR e diagrama polar -->

## 15. Demonstração Web — Biblioteca

**[Fala: Carlos Eduardo]**

Depois de simular uma antena, podemos salvá-la na Biblioteca. A Biblioteca permite:

- listar antenas criadas;
- exportar uma antena como JSON;
- importar especificações;
- reutilizar a antena em cenários de enlace.

Esse fluxo é importante porque transforma a antena em um objeto persistente, não apenas em um resultado temporário de simulação.

<!-- sugestão de imagem/ilustração: captura da Biblioteca com lista de antenas salvas e botões de importar/exportar JSON -->

## 16. Demonstração Web — Link Planner

**[Fala: Carlos Eduardo]**

No Link Planner, configuramos os nós da rede com latitude, longitude, altura e antenas associadas. A aplicação calcula:

- distância 3D por ENU;
- azimute;
- elevação;
- perda de percurso por FSPL ou modelos disponíveis;
- potência recebida;
- margem de enlace;
- semáforo de viabilidade.

O sistema também suporta perdas adicionais, margem de fading, perda de polarização, orientação de antena e seleção de módulos LoRa. A ideia é permitir que o usuário explore cenários sem precisar alterar código.

Na demonstração, podemos montar um enlace entre um ponto de alarme e o gateway, selecionar uma antena comercial omnidirecional e observar a margem. Em seguida, podemos alterar a orientação de uma antena diretiva para mostrar como o desalinhamento reduz o ganho efetivo.

<!-- sugestão de imagem/ilustração: captura do Link Planner com mapa/nós, campos de potência/perdas e resultado de margem em semáforo verde/amarelo/vermelho -->

## 17. Integração entre MATLAB e plataforma Web

**[Fala: Carlos Eduardo]**

O MATLAB e a plataforma Web têm papéis complementares.

O MATLAB foi usado para uma comparação mais detalhada entre módulos, antenas e cenários, com rankings e discussão automática. Já a plataforma Web organiza esse conhecimento em uma interface mais acessível, permitindo visualizar antenas, salvar modelos e estimar enlaces de forma interativa.

É importante destacar também os limites da plataforma:

- ela não faz ray tracing urbano completo;
- não detecta obstáculos automaticamente por imagens;
- KML com polígonos é tratado principalmente como informação visual;
- parabólicas grandes usam aproximação de abertura, não MoM completo.

Essas limitações são assumidas conscientemente, porque o objetivo da plataforma é educacional e de apoio ao planejamento inicial.

<!-- sugestão de imagem/ilustração: matriz comparando MATLAB como análise detalhada e Web como ferramenta interativa educacional -->

## 18. Conclusão técnica

**[Fala: Carlos Eduardo]**

Com os resultados obtidos, a conclusão é que o enlace LoRa no cenário estudado é tecnicamente viável para mensagens curtas de emergência no campus, desde que sejam escolhidos módulos e antenas adequados.

A análise em MATLAB mostrou margens confortáveis para os pontos avaliados, mesmo com perdas conservadoras. Ao mesmo tempo, a plataforma Web mostrou como esses conceitos podem ser explorados visualmente e reutilizados em cenários de simulação.

<!-- sugestão de imagem/ilustração: slide de conclusão com três evidências: margens confortáveis, antena omni 6 dBi robusta, plataforma Web funcional -->

## 19. Fechamento coordenado

**[Fala: Diogo Schwartz]**

Para fechar, o projeto mostra uma integração entre pesquisa técnica, simulação e aplicação computacional.

Do ponto de vista do problema, partimos de uma necessidade real de comunicação de emergência no campus.

**[Fala: João Victor]**

Do ponto de vista da engenharia de antenas, mostramos que a escolha da antena depende não só do ganho máximo, mas também do padrão de radiação, orientação, robustez multidirecional e margem de enlace.

**[Fala: Carlos Eduardo]**

E do ponto de vista computacional, entregamos uma plataforma Web que permite experimentar esses conceitos, salvar antenas e estimar enlaces de maneira visual e didática.

**[Fala: Diogo Schwartz]**

Assim, o projeto combina fundamentação, simulação e ferramenta prática para justificar tecnicamente a escolha de antenas e módulos LoRa/LoRaWAN no Campus Darcy Ribeiro da UnB.

Obrigado. Estamos à disposição para perguntas.

<!-- sugestão de imagem/ilustração: slide final com resumo em três pilares: problema real, simulação técnica e plataforma educacional -->

---

# Roteiro rápido de demonstração

## Demonstração 1 — MATLAB

**Responsável:** João Victor

1. Abrir `main_LoRa_AntennaComparison.m`;
2. Mostrar carregamento dos pontos do campus;
3. Mostrar escolha automática do gateway, destacando BCE;
4. Exibir geometria dos enlaces;
5. Mostrar os seis modelos de antena;
6. Rodar comparação de cenários;
7. Mostrar ranking final e interpretação.

## Demonstração 2 — Plataforma Web

**Responsável:** Carlos Eduardo

1. Abrir o Sandbox;
2. Criar ou selecionar uma antena;
3. Mostrar ganho, impedância, SWR e diagrama;
4. Salvar na Biblioteca;
5. Abrir Link Planner;
6. Configurar nós e antenas;
7. Calcular margem de enlace;
8. Mostrar efeito de orientação/perdas.

## Fechamento conceitual

**Responsável:** Diogo Schwartz

Reforçar que:

- o problema é comunicação de emergência com baixo consumo;
- LoRa/LoRaWAN é adequado para mensagens curtas e alcance amplo;
- antenas omnidirecionais práticas foram mais robustas para o gateway;
- antenas diretivas são úteis em enlaces ponto a ponto, mas exigem alinhamento;
- a solução final integra objetivos, simulação e plataforma educacional.
