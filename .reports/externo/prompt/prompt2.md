Quero modificar e ampliar um projeto MATLAB de simulação de rede LoRa/LoRaWAN para um sistema de segurança no Campus Darcy Ribeiro da UnB.

Contexto geral:
O sistema terá vários pontos de alarme distribuídos pelo campus. Quando um alarme for ativado, um módulo LoRa transmitirá uma mensagem para uma central de segurança. A central será representada por um gateway fixo. O objetivo do projeto é comparar diferentes combinações de módulos LoRa e antenas, analisando o desempenho do enlace de comunicação.

O projeto é de antenas, portanto a comparação não pode assumir previamente qual antena é a melhor. O código deve comparar diferentes antenas com base em:

* padrão de radiação;
* ganho direcional;
* orientação da antena;
* distância entre transmissor e gateway;
* perda de espaço livre;
* potência recebida;
* sensibilidade do receptor;
* margem de enlace;
* robustez para múltiplas direções;
* praticidade de instalação.

Separar claramente:

1. Base de dados dos módulos LoRa;
2. Base de dados dos modelos de antenas;
3. Geometria dos pontos do campus;
4. Cálculo de enlace.

COORDENADAS DOS PONTOS DE ALARME

FACE:
lat = -15.75765082870043;
lon = -47.87083077618352;
alt = 1034.446264894265;

BCE:
lat = -15.76127034065908;
lon = -47.86745724717513;
alt = 1019.61698099038;

Beijódromo:
lat = -15.76377698277078;
lon = -47.86520966364652;
alt = 1024.139071702697;

IB:
lat = -15.76601060040457;
lon = -47.86657645286517;
alt = 1033.408014943337;

IQ:
lat = -15.76831173033475;
lon = -47.86572517133772;
alt = 1037.985829588322;

ICC Sul:
lat = -15.76591092048512;
lon = -47.86971992266324;
alt = 1039.931640249285;

ICC Norte:
lat = -15.76298853031727;
lon = -47.87187806988097;
alt = 1038.798361313413;

CO:
lat = -15.76448213579672;
lon = -47.8598793136273;
alt = 1022.504171087457;

SG:
lat = -15.76679349641666;
lon = -47.87124591627169;
alt = 1046.761186877331;

MÓDULOS LORA A SEREM COMPARADOS

Criar uma função chamada loadLoRaModules.m que retorne uma tabela ou struct array com os módulos abaixo.

Módulo 1: RFM95W 915 MHz

* Nome: "RFM95W_915MHz";
* Frequência nominal: 915 MHz;
* Faixa de frequência: considerar 915 MHz como frequência de operação;
* Tensão de operação: 1.8 a 3.7 V;
* Potência máxima de transmissão: +20 dBm;
* Correntes de transmissão:

  * 120 mA em +20 dBm;
  * 90 mA em +17 dBm;
  * 29 mA em +13 dBm;
* Corrente em recepção: 10 a 14 mA;
* Corrente em repouso:

  * 0.2 uA em sleep;
  * 1.5 uA em idle;
* Sensibilidades disponíveis:

  * -139 dBm;
  * -136 dBm;
  * -118 dBm;
* Erro de frequência: ±7 kHz;
* FIFO: 64 bytes;
* Taxa de transmissão LoRa: 0.018 kbps a 37.5 kbps;
* Modulação: LoRa;
* Interface: SPI;
* Temperatura de operação: -40 °C a 85 °C.

Observação: como as sensibilidades -139, -136 e -118 dBm não foram associadas diretamente a SF/BW específicos, tratá-las como modos operacionais:

* modo "LongRange" = -139 dBm;
* modo "Balanced" = -136 dBm;
* modo "HighDataRate" = -118 dBm.

Módulo 2: LRO2 DEV Kit ASR6601

* Nome: "LRO2_ASR6601";
* Frequências suportadas: 433 MHz, 475 MHz, 868 MHz e 915 MHz;
* Frequência usada na simulação: 915 MHz;
* Potência de transmissão: 0 a 22 dBm;
* Tensão de alimentação: 3 a 5.5 V;
* Sensibilidade de recepção: -138 dBm;
* Tamanho do módulo: 36 mm x 16.5 mm;
* Distância de referência:

  * até 8 km em visada aberta;
  * até 3.8 km em ambiente urbano;
* Tipo: módulo LoRa;
* Modulação: LoRa.

Módulo 3: E220-900T22D

* Nome: "E220_900T22D";
* Frequência de operação: 815.125 MHz a 930.125 MHz;
* Frequência usada na simulação: 915 MHz;
* Potência de transmissão: 10 a 22 dBm;
* Distância de referência: 5 km;
* Sensibilidade de recepção: não informada diretamente nos dados fornecidos.
  Portanto, criar o campo Sensitivity_dBm como NaN por padrão, mas permitir que o usuário defina um valor manualmente.
  Para rodar simulações comparativas automáticas, permitir um parâmetro opcional defaultSensitivity_dBm, por exemplo -137 dBm, deixando claro no código que é uma hipótese ajustável.
* O kit acompanha duas antenas 868/915 MHz com:

  * conector SMA-J macho;
  * ganho máximo: 6 dBi;
  * padrão de radiação: omnidirecional;
  * polarização: vertical;
  * cabo de 1 metro.

Observação importante:
Há uma possível inconsistência comercial entre “100 mW” e “22 dBm”, pois 100 mW corresponde a 20 dBm, enquanto 22 dBm corresponde aproximadamente a 158 mW. O código deve apenas registrar a potência informada como 10 a 22 dBm e permitir ajuste manual.

ANTENAS A SEREM COMPARADAS

Criar uma função loadAntennaModels.m com os seguintes modelos:

1. Dipolo de meia onda vertical

* Nome: "Dipole_HalfWave";
* Ganho máximo aproximado: 2.15 dBi;
* Polarização: linear vertical;
* Padrão: omnidirecional no plano horizontal;
* Nulos ao longo do eixo do dipolo, isto é, theta = 0 e theta = pi;
* Máximo próximo de theta = pi/2.

2. Monopolo vertical sobre plano de terra

* Nome: "Monopole_GroundPlane";
* Ganho máximo aproximado: 5.15 dBi para modelo ideal;
* Polarização: linear vertical;
* Padrão: omnidirecional no plano horizontal;
* Irradiação considerada principalmente no semiespaço superior;
* Máximo próximo de theta = pi/2.

3. Helicoidal axial

* Nome: "Helical_Axial";
* Ganho máximo configurável, por exemplo 10 a 12 dBi;
* Polarização: circular ou elíptica, dependendo da aproximação adotada;
* Padrão: direcional;
* O ganho máximo ocorre no eixo de apontamento, ou boresight;
* Deve ter parâmetro HPBW_deg para controlar a largura de feixe aproximada.

4. Parabólica/diretiva

* Nome: "Parabolic_Dish";
* Ganho máximo configurável, por exemplo 15 a 24 dBi, dependendo do diâmetro hipotético;
* Padrão: altamente direcional;
* O ganho máximo ocorre no boresight;
* Deve ter HPBW_deg pequeno;
* Deve ficar claro na simulação que uma parabólica não é adequada para um gateway único recebendo sinais vindos de muitos azimutes, salvo se houver múltiplas antenas, setorização ou apontamento individual.

5. PCB compacta

* Nome: "PCB_Compact";
* Ganho máximo configurável, por exemplo 0 a 2 dBi;
* Polarização: linear;
* Padrão: quase omnidirecional, mas com pequenas irregularidades em theta e phi;
* Representa uma antena compacta de baixo custo integrada ao circuito.

6. Antena comercial omnidirecional vertical 6 dBi

* Nome: "Commercial_Omni_6dBi";
* Ganho máximo: 6 dBi;
* Frequência: 868/915 MHz;
* Polarização: vertical;
* Padrão: omnidirecional no plano horizontal;
* Usar como referência prática, pois acompanha o kit E220-900T22D.
* O modelo deve ser semelhante ao monopolo/colinear vertical, com ganho mais concentrado próximo do horizonte.

FUNÇÕES MATLAB A SEREM CRIADAS

1. main_LoRa_AntennaComparison.m
   Script principal.
   Deve:

* carregar os pontos do campus;
* carregar a base de dados dos módulos LoRa;
* carregar a base de dados das antenas;
* escolher o gateway;
* converter coordenadas geográficas para coordenadas locais;
* calcular a geometria dos enlaces;
* plotar os diagramas de radiação;
* rodar os cenários de comparação;
* gerar tabelas de resultado;
* gerar rankings por módulo, antena e combinação módulo-antena.

2. loadCampusPoints.m
   Retornar uma tabela MATLAB com:
   Name, Lat, Lon, Alt.

3. loadLoRaModules.m
   Retornar uma tabela ou struct array com:
   Name;
   f_MHz;
   PtxMin_dBm;
   PtxMax_dBm;
   PtxOptions_dBm;
   SensitivityOptions_dBm;
   VoltageMin_V;
   VoltageMax_V;
   RxCurrent_mA;
   TxCurrentOptions_mA;
   SleepCurrent_uA;
   IdleCurrent_uA;
   DataRateMin_kbps;
   DataRateMax_kbps;
   Interface;
   Modulation;
   Notes.

4. loadAntennaModels.m
   Retornar tabela ou struct array com:
   Name;
   Type;
   Gmax_dBi;
   HPBW_deg;
   Polarization;
   IsDirectional;
   PatternModel;
   Notes.

5. chooseGateway.m
   Permitir escolher o gateway de duas formas:
   a) manualmente, pelo nome do ponto, por exemplo "BCE";
   b) automaticamente, escolhendo o ponto que minimiza a maior distância 3D até os demais pontos.
   Retornar:

* índice do gateway;
* tabela com distância média e distância máxima de cada candidato;
* ranking dos candidatos a gateway.

6. geodeticToLocalENU.m
   Converter latitude, longitude e altitude para coordenadas locais ENU em metros, usando o gateway como origem.
   Se o MATLAB tiver Mapping Toolbox, usar geodetic2enu e wgs84Ellipsoid.
   Caso contrário, implementar aproximação local:

* x = deslocamento leste-oeste em metros;
* y = deslocamento norte-sul em metros;
* z = diferença de altitude.
  Para a escala do campus, a aproximação local é aceitável.

7. linkGeometry.m
   Para cada ponto de alarme em relação ao gateway, calcular:

* vetor transmissor → receptor;
* distância 2D;
* distância 3D;
* azimute;
* ângulo de elevação;
* theta e phi no sistema local da antena transmissora;
* theta e phi no sistema local da antena receptora.

Usar a convenção:

* theta = ângulo polar medido a partir do eixo z local da antena;
* phi = azimute no plano xy local.

Para antenas verticais:

* eixo z = vertical;
* enlaces aproximadamente horizontais devem ficar próximos de theta = 90 graus.

Para antenas diretivas:

* incluir opção de apontar o boresight da antena transmissora para o gateway;
* incluir opção de deixar a antena não apontada para avaliar penalidade por desalinhamento;
* para o gateway, permitir simular antena omnidirecional ou antena diretiva fixa com boresight único.

8. antennaPattern.m
   Função:
   G_dBi = antennaPattern(antennaType, theta, phi, params)

A função deve retornar o ganho em dBi na direção especificada.
Implementar modelos aproximados, coerentes fisicamente e adequados para comparação educacional.

Modelos:

* Dipolo de meia onda:
  padrão dependente de theta;
  nulos em theta = 0 e theta = pi;
  máximo próximo de theta = pi/2;
  Gmax_dBi = 2.15.

* Monopolo vertical:
  padrão semelhante ao dipolo no semiespaço superior;
  Gmax_dBi configurável, default 5.15;
  forte radiação perto do horizonte.

* Helicoidal axial:
  padrão diretivo aproximado;
  ganho máximo no boresight;
  queda angular controlada por HPBW_deg;
  Gmax_dBi default 11 dBi.

* Parabólica:
  padrão altamente diretivo;
  ganho máximo no boresight;
  HPBW_deg pequeno;
  Gmax_dBi configurável.

* PCB compacta:
  padrão quase omnidirecional;
  Gmax_dBi default 1 dBi;
  pequenas variações com theta e phi para representar irregularidade.

* Comercial omnidirecional 6 dBi:
  padrão omnidirecional no plano horizontal;
  ganho máximo 6 dBi;
  polarização vertical;
  padrão mais estreito em elevação do que um dipolo simples.

Todos os modelos devem ter piso mínimo de ganho, por exemplo -40 dBi, para evitar valores indefinidos.

9. plotRadiationPatterns.m
   Para cada antena, plotar:
   a) corte em theta, com phi fixo;
   b) corte em phi, com theta = 90 graus;
   c) padrão 3D simplificado usando surf, se possível.

Os gráficos devem permitir comparar visualmente:

* dipolo;
* monopolo;
* helicoidal;
* parabólica;
* PCB;
* comercial omnidirecional 6 dBi.

10. linkBudget.m
    Função que calcule:
    FSPL_dB = 32.44 + 20*log10(f_MHz) + 20*log10(d_km);

Prx_dBm = Ptx_dBm + Gtx_dBi + Grx_dBi - FSPL_dB - L_cabo_tx_dB - L_cabo_rx_dB - L_extra_dB;

Margin_dB = Prx_dBm - Sensitivity_dBm.

Permitir configurar:

* frequência;
* potência de transmissão;
* sensibilidade;
* perdas de cabo;
* perda por polarização;
* perda adicional por obstáculos;
* margem de fading;
* perdas por desalinhamento angular já incorporadas via ganho direcional.

11. compareScenarios.m
    Rodar os seguintes cenários:

Cenário A:
Mesmo tipo de antena no transmissor e no gateway.

Cenário B:
Gateway com antena omnidirecional vertical, por exemplo dipolo, monopolo ou comercial omnidirecional 6 dBi, e transmissores variando entre dipolo, monopolo, helicoidal, parabólica, PCB e comercial 6 dBi.

Cenário C:
Transmissores diretivos apontados para o gateway e gateway omnidirecional.

Cenário D:
Transmissores diretivos não necessariamente apontados para o gateway, para mostrar o efeito de desalinhamento.

Cenário E:
Comparação entre módulos LoRa:

* RFM95W;
* LRO2 ASR6601;
* E220-900T22D.

Para cada cenário, produzir tabela com:

* Nome do ponto;
* Nome do módulo LoRa;
* tipo de antena transmissora;
* tipo de antena do gateway;
* distância 2D;
* distância 3D;
* azimute;
* elevação;
* Gtx efetivo;
* Grx efetivo;
* potência transmitida;
* sensibilidade usada;
* FSPL;
* perdas adicionais;
* potência recebida;
* margem de enlace;
* status do enlace.

Classificação do status:

* "Falha" se Margin_dB < 0;
* "Crítico" se 0 <= Margin_dB < 10;
* "Confortável" se Margin_dB >= 10.

12. plotCampusMap.m
    Plotar os pontos no mapa.
    Se geoplot/geobasemap estiver disponível, usar mapa geográfico.
    Caso contrário, plotar coordenadas locais x-y.

O gráfico deve:

* destacar o gateway;
* mostrar os pontos de alarme;
* desenhar linhas entre cada alarme e o gateway;
* colorir as linhas conforme margem de enlace:

  * vermelho para falha;
  * amarelo para crítico;
  * verde para confortável.

13. rankConfigurations.m
    Criar ranking das combinações módulo-antena por:

* maior margem mínima;
* maior margem média;
* menor número de enlaces críticos;
* menor número de enlaces em falha;
* robustez a múltiplas direções;
* praticidade para instalação;
* consumo estimado de corrente na transmissão.

14. estimateEnergyConsumption.m
    Função opcional para estimar consumo por transmissão.
    Usar dados de corrente dos módulos quando disponíveis.
    Entradas:

* módulo;
* potência de transmissão;
* tempo de transmissão estimado;
* tensão de alimentação;
* número de transmissões por dia.
  Saídas:
* energia por transmissão;
* consumo diário estimado;
* comparação relativa entre módulos.
  Não precisa modelar toda a pilha LoRaWAN; basta uma estimativa simples com base em corrente, tensão e tempo.

REQUISITOS FÍSICOS IMPORTANTES

* Não assumir que o ganho da antena é igual em todas as direções.
* Para cada enlace, calcular a direção real entre o alarme e o gateway.
* Usar essa direção para consultar o ganho efetivo da antena transmissora e da antena receptora.
* O cálculo de enlace deve usar Gtx(theta,phi) e Grx(theta,phi), e não apenas o ganho máximo da antena.
* Para dipolo e monopolo verticais, enlaces no plano horizontal devem ficar próximos do máximo de radiação.
* Para dipolo vertical, deve haver nulos em theta = 0 e theta = 180 graus.
* Para helicoidal e parabólica, o ganho máximo só deve ocorrer quando o boresight estiver apontado para o gateway.
* Para o gateway, deixar claro que antenas muito diretivas não são boas para receber sinais de todos os lados, salvo com múltiplas antenas, setorização ou apontamento controlado.
* A antena comercial omnidirecional vertical de 6 dBi deve ser usada como referência prática de comparação.
* A frequência padrão da simulação deve ser 915 MHz.
* O código deve permitir alterar frequência, potência, sensibilidade e perdas.

SAÍDAS ESPERADAS

1. Figuras dos diagramas de radiação em theta e phi para todas as antenas.
2. Figura 3D simplificada dos padrões de radiação.
3. Mapa do campus com os enlaces até o gateway.
4. Tabela de cálculo de enlace para todos os pontos.
5. Tabela de comparação entre módulos LoRa.
6. Tabela de comparação entre antenas.
7. Ranking de combinações módulo-antena.
8. Discussão automática simples no console, indicando:

   * melhor antena para os nós transmissores;
   * melhor antena para o gateway;
   * melhor módulo em margem de enlace;
   * melhor módulo em consumo estimado;
   * riscos de usar antenas muito diretivas;
   * efeito do desalinhamento angular.

O objetivo não é construir um simulador eletromagnético completo. O objetivo é criar uma simulação educacional de engenharia de antenas e enlace LoRa, usando modelos aproximados, mas fisicamente coerentes, para justificar tecnicamente a escolha das antenas e dos módulos