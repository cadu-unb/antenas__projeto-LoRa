Oi pessoal, a data limite de entrega dos relatórios foi alterada no aprender para primeiro de julho. Seguem abaixo alguns comentários, separados por projeto:

*Microfitas:

-Incluir a largura "W" na figura da geometria.
-O que é G12 e G1 na equação da diretividade?
-Evidenciar o fato de como visto em sala a microfita é a única antena em que a parte condutora não é a responsável pela irradiação, e sim as áreas das aberturas equivalentes nas bordas. Desta forma ao multiplicarmos as dimensões de uma microfita operacional por um fator N (inteiro e ímpar, para facilitar), o ganho é multiplicado por aproximadamente o mesmo fator, mas NÃO N ao quadrado como muitos modelos indicam. O modelo utilizado parece possuir esta mesma limitação/erro, comentar sobre isto no relatório, incluindo a geração de lóbulos "espúrios" ou "fringe" provenientes da teoria de conjuntos faseados. Usar para estas considerações a referência abaixo (os slides da apresentação estão disponíveis no aprender, seção artigos e apresentações):

MARCO A.B. TERADA, "Trade-offs in Ultra-Wide Band Microstrip Antennas", 2025 IEEE INTERNATIONAL SYMPOSIUM ON ANTENNAS AND PROPAGATION & NORTH AMERICAN RADIO SCIENCE MEETING,  v. 1. p. 1-1, Ottawa, Canadá, 2025.


*Fórmulas de Ganho e Eficiência:

-Separar o relatório em antenas de baixo (fios) e alto ganho (cornetas e refletores). Na investigação de vocês qual seria o valor sugerido de ganho que separa estes casos?
-Para as antenas de fios as fórmulas não se aplicam diretamente, é necessário usar uma área equivalente; ver o livro do Stutzman para detalhes e não deixar de comentar sobre isso no relatório.
-Apenas para informação, o Kraus foi o orientador do Stutzman.


*LoRa:
-Substituir no slide 5 a palavra "armadilha" por "Engano" ou "Erro".
-Parabólicas não são a melhor escolha para esta aplicação. Comentar sobre isto, ou se o tempo permitir, substituir as simulações com o PRAC por cornetas simuladas com a planilha Excel (os diagramas poderiam ser mantidos apenas para ilustrar as áreas de cobertura). Apesar das cornetas também não serem indicadas nesta aplicação, elas seriam mais compatíveis com o range de ganho necessário, e mais fáceis de serem usadas em situações de "setorização" de célula para gerar um diagrama equivalente composto omnidirecional no plano terra (a viabilidade física do uso de cornetas depende da frequência que deve ser explicitada no relatório).
-No slide 16, na parte "Solução", substituir a sugestão de extender o PRAC pelo uso do GRADMAX e os scripts do Russ para microfitas. O GRADMAX é um software de análise de antenas de fios, disponível no aprender, que analiza e otimiza as antenas citadas (ominidirecionais, dipolos, monopolos, hélices, etc...). Não foram cobertas antenas de fios neste semestre, talvez da próxima vez, dada a importância em ERBs e roteadores Wi-Fi.

-Refletores ominidirecionais no plano terra existem e envolvem geometrias como a da referência abaixo:

J. R. Bergmann, R. C. Brown, P. J. B. Clarricoats, and Z. Hay, "Synthesis of shaped-beam reflector antennas patterns", IEE Proc. 135(H): 48–53 (1988).



Prof. Marco Terada, Ph.D.
Dept. of Electrical Engineering
University of Brasilia - Brazil
www.ene.unb.br/terada