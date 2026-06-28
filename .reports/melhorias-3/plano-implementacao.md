# Plano de Implementacao - Melhorias 3

Fonte obrigatoria: `.prompt/melhorias-3/_orientacoes_professor/email.md`.

Este plano cruza as orientacoes do professor com a estrutura atual do projeto. Nenhum parametro numerico da nova antena foi estimado. Os dados ausentes devem ser confirmados antes da implementacao.

## 1. Resumo Tecnico do E-mail

### 1.1 Nova antena a integrar

A antena indicada como alternativa as simulacoes com parabola e a **corneta**. O e-mail apresenta essa substituicao como opcional caso haja tempo, mas o presente plano considera sua integracao como requisito do projeto.

O professor faz as seguintes observacoes:

- parabólicas nao sao a melhor escolha para a aplicacao LoRa proposta;
- as simulacoes baseadas no PRAC podem ser substituidas por cornetas simuladas com uma planilha Excel;
- os diagramas de parabólicas podem permanecer apenas como ilustracao das areas de cobertura;
- cornetas tambem nao sao indicadas para a aplicacao, mas seriam mais compativeis com o intervalo de ganho necessario;
- cornetas facilitariam uma possivel setorizacao de celula, formando um diagrama composto equivalente omnidirecional no plano da terra;
- a viabilidade fisica da corneta depende da frequencia, que deve ser explicitada no relatorio.

### 1.2 Correcoes sobre microfitas

- Incluir a largura `W` na figura da geometria.
- Explicar o significado de `G12` e `G1` na equacao da diretividade.
- Destacar que, na microfita, a irradiacao e associada as aberturas equivalentes nas bordas, e nao diretamente a parte condutora.
- Explicar que, ao multiplicar as dimensoes de uma microfita operacional por um fator inteiro e impar `N`, o ganho cresce aproximadamente pelo mesmo fator, e nao por `N²`.
- Registrar que o modelo utilizado aparenta possuir essa limitacao ou erro.
- Comentar a geracao de lobulos espurios ou `fringe` associada a teoria de conjuntos faseados.
- Usar como referencia o trabalho de Marco A. B. Terada, *Trade-offs in Ultra-Wide Band Microstrip Antennas*, IEEE APS/URSI 2025.

### 1.3 Correcoes sobre ganho e eficiencia

- Separar a discussao do relatorio entre antenas de baixo ganho, identificadas no e-mail como antenas de fios, e antenas de alto ganho, identificadas como cornetas e refletores.
- Investigar e justificar um valor de ganho que separe os dois grupos. O e-mail nao fornece esse valor.
- Para antenas de fios, nao aplicar diretamente as formulas de abertura: usar area equivalente e consultar o livro de Stutzman.
- A informacao de que Kraus foi orientador de Stutzman e contextual; nao gera, por si so, requisito de software.

### 1.4 Correcoes sobre LoRa, apresentacao e ferramentas

- ~~Substituir a palavra "Armadilha" por "Engano" ou "Erro" no slide indicado como 5~~ não se aplica aqui.
- Explicar por que parabólicas nao sao a melhor escolha para a aplicacao.
- No slide indicado como 16, substituir a proposta de estender o PRAC pelo uso do GRADMAX e dos scripts de Russ para microfitas.
- Explicar que o GRADMAX analisa e otimiza antenas de fios, como omnidirecionais, dipolos, monopolos e helices.
- Registrar que refletores omnidirecionais no plano da terra existem e podem empregar geometrias como as descritas por Bergmann et al. (1988).
- Considerar a nova data-limite de entrega dos relatorios: **1 de julho**. O ano nao foi informado no e-mail.

### 1.5 Divergencia com a apresentacao atual

A numeracao do e-mail nao corresponde diretamente a `__roteiro/apres-v3.tex`:

- o bloco `Armadilha comum` esta no frame 6 de `apres-v3.tex`, e nao no frame 5;
- o frame 16 de `apres-v3.tex` e `Ranking agregado: combinacoes modulo-antena` e nao contem a secao `Solucao`;
- a frase sobre estender a analise aparece no frame 22 de `apres-v3.tex`;
- em `apres-v2.tex`, `Armadilha comum` aparece no frame 8.

Assim, as alteracoes devem ser localizadas pelo conteudo, nao apenas pelo numero do slide, ate que a versao enviada ao professor seja confirmada.

## 2. Especificacoes da Nova Antena

### 2.1 Dados explicitamente identificados

| Campo | Informacao presente no e-mail |
|---|---|
| Tipo | Corneta |
| Classe discutida | Antena de alto ganho |
| Aplicacao | Alternativa a parabola nas simulacoes LoRa |
| Adequacao | Tambem nao indicada como escolha ideal para a aplicacao |
| Ganho | Compativel com o intervalo necessario, sem valor numerico |
| Fonte da simulacao | Planilha Excel nao anexada ao repositorio |
| Comportamento de cobertura | Pode ser usada em setorizacao para compor cobertura equivalente omnidirecional no plano da terra |
| Frequencia | Deve ser explicitada; determina a viabilidade fisica |
| Comparacao requerida | Corneta versus parabola e antenas adequadas ao gateway LoRa |

### 2.2 Parametros ausentes

O e-mail nao informa:

- subtipo ou geometria da corneta;
- frequencia ou faixa de frequencias;
- dimensoes fisicas;
- ganho maximo em dBi;
- HPBW nos planos principais;
- polarizacao;
- impedancia;
- VSWR ou coeficiente de reflexao;
- eficiencia;
- perdas;
- diagrama de radiacao numerico;
- numero de setores e orientacao de cada corneta;
- formato, abas, colunas, unidades ou formulas da planilha Excel;
- criterio numerico para separar baixo e alto ganho.

Esses dados nao devem receber valores padrao inventados. Ate serem fornecidos, a corneta pode ter apenas seu contrato de dados preparado, sem preset numerico canonico.

## 3. Plano de Acao e Implementacao

### Fase 0 - Confirmar escopo e fontes

1. Identificar qual arquivo de apresentacao corresponde aos slides 5 e 16 citados.
2. Obter a planilha Excel mencionada e registrar sua origem e versao.
3. Confirmar o subtipo de corneta e a frequencia de operacao.
4. Confirmar se a parabola sera removida das comparacoes ou mantida como referencia ilustrativa.
5. Definir com o professor se a setorizacao sera apenas discutida ou tambem simulada.
6. Identificar o arquivo final do relatorio tecnico que recebera as correcoes de microfita, ganho e eficiencia.

**Criterio de aceite:** todas as perguntas bloqueantes da secao 4 possuem resposta documentada.

### Fase 1 - Preservar e validar os dados da planilha

1. Colocar a planilha em um diretorio versionado definido pela equipe.
2. Documentar abas, colunas, unidades, frequencias, angulos e convencao de polarizacao.
3. Verificar se os valores representam ganho realizado, diretividade ou ganho normalizado.
4. Verificar se ha cortes nos planos E e H e qual eixo representa o boresight.
5. Criar uma conversao deterministica para JSON ou CSV somente se isso facilitar o consumo pelo backend e pelo MATLAB.
6. Manter a planilha original imutavel e registrar a rastreabilidade dos dados derivados.

**Criterio de aceite:** um mesmo ponto da planilha e reproduzido sem alteracao de unidade no dado importado.

### Fase 2 - Definir o contrato da corneta

1. Adicionar o identificador `corneta` ao catalogo de tipos aceitos.
2. Reutilizar os campos gerais ja existentes em `AntennaSpec`: `frequency_hz`, `gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional`, `pattern_model`, `practicality_score`, `multi_direction_score` e `notes`.
3. Definir os campos de `geometry` somente apos conhecer a planilha e o subtipo da corneta.
4. Adicionar metadados de procedencia da planilha aos dados importados.
5. Nao criar preset numerico em `backend/app/domain/antenna_presets.py` antes da validacao dos valores.

**Criterio de aceite:** uma especificacao de corneta valida preserva frequencia, unidades e procedencia sem usar valores ficticios.

### Fase 3 - Implementar o modelo numerico

1. Criar um solver especifico para corneta em `backend/app/solvers/`.
2. Fazer o solver consumir os resultados validados da planilha Excel ou de sua exportacao rastreavel.
3. Implementar o ganho em funcao do angulo por interpolacao dos pontos fornecidos, sem extrapolacao silenciosa.
4. Retornar aviso quando frequencia ou angulo estiver fora do dominio dos dados.
5. Calcular apenas grandezas sustentadas pela planilha ou por uma referencia aprovada.
6. Registrar o solver no `_REGISTRY` de `backend/app/solvers/__init__.py`.
7. Manter `ApertureSolver` associado a parabola; nao reutiliza-lo automaticamente para corneta sem validacao tecnica.

**Criterio de aceite:** ganho e diagrama reproduzem pontos de referencia da planilha dentro de uma tolerancia definida apos o recebimento dos dados.

### Fase 4 - Integrar a corneta ao Sandbox e a API

1. Adicionar a funcao de resolucao da corneta em `backend/app/api/sandbox_routes.py`.
2. Registrar o tipo no mapa `_SOLVERS` e no fluxo dos modos de simulacao suportados.
3. Retornar `gain_dbi`, `impedance_ohm`, `swr`, `efficiency_pct`, `radiation_pattern`, `pattern_data`, `warning` e `extra` apenas quando houver dados correspondentes.
4. Expor claramente dados indisponiveis, em vez de preencher respostas fixas.
5. Verificar que salvar e recarregar a corneta pela Biblioteca preserva o `AntennaSpec`.

**Criterio de aceite:** a API aceita `type="corneta"`, processa dados validos e rejeita entradas incompletas com mensagem objetiva.

### Fase 5 - Integrar a interface Web

1. Adicionar `Corneta` ao seletor de antenas em `frontend/public/sandbox.html`.
2. Criar campos de geometria somente para parametros confirmados pela planilha.
3. Adicionar representacao fisica e diagrama de radiacao coerentes com os dados importados.
4. Preencher os campos fisicos a partir do backend ou de um preset validado, evitando duplicacao divergente entre Python e JavaScript.
5. Garantir que Biblioteca e Link Planner exibam o novo tipo sem tratamento especial quebrado.
6. Mostrar frequencia e dimensoes relevantes juntas para permitir a avaliacao da viabilidade fisica solicitada no e-mail.

**Criterio de aceite:** a corneta pode ser criada, visualizada, salva, selecionada em um enlace e recalculada sem perda de dados.

### Fase 6 - Atualizar link budget, comparacoes e setorizacao

1. Verificar o ganho efetivo angular da corneta em `backend/app/domain/link_budget.py`.
2. Validar o comportamento com boresight alinhado e desalinhado.
3. Incluir a corneta nas comparacoes de configuracoes em `backend/app/domain/comparison.py`.
4. Comparar, com os mesmos cenarios e frequencia, ao menos a corneta, a parabola e a antena de gateway recomendada pelo estudo.
5. Nao declarar a corneta como melhor solucao apenas por possuir maior ganho.
6. Se a setorizacao fizer parte do escopo confirmado, representar cada setor com orientacao propria e combinar a cobertura conforme uma regra documentada.
7. Se a setorizacao nao fizer parte do escopo, limitar-se a explicar sua possibilidade no relatorio.

**Criterio de aceite:** os resultados evidenciam ganho, cobertura angular, apontamento e adequacao ao cenario multi-azimute separadamente.

### Fase 7 - Atualizar a simulacao MATLAB

1. Tratar `.reports/externo/prompt/return/` como material externo de referencia, nao como implementacao principal do repositorio.
2. Definir um local versionado para os scripts MATLAB efetivamente mantidos pelo projeto.
3. Adicionar a corneta ao carregamento de modelos somente com os valores confirmados da planilha.
4. Adicionar o modelo angular correspondente no equivalente de `antennaPattern.m`.
5. Substituir os cenarios PRAC/parabola pelos cenarios de corneta quando essa decisao for confirmada.
6. Preservar os diagramas de parabola apenas quando estiverem rotulados como ilustrativos de area de cobertura.
7. Reexecutar rankings e tabelas; nao reaproveitar resultados numericos antigos apos a troca da antena.

**Criterio de aceite:** os resultados MATLAB identificam fonte dos dados, frequencia, antena e cenario sem misturar numeros antigos da parabola com a corneta.

### Fase 8 - Corrigir relatorio e apresentacao

1. Separar a discussao entre antenas de fios e antenas de alto ganho.
2. Apresentar como resultado de investigacao, e nao como dado do e-mail, o limiar escolhido entre baixo e alto ganho.
3. Corrigir a figura de microfita com a largura `W`.
4. Definir `G12` e `G1` no ponto em que aparecem na equacao.
5. Explicar o mecanismo de irradiacao pelas aberturas equivalentes nas bordas.
6. Registrar a limitacao de escala por `N`, o erro de previsao por `N²` e os lobulos `fringe`, citando Terada (2025).
7. Explicar o uso de area equivalente para antenas de fios com a referencia de Stutzman.
8. Substituir `Armadilha comum` por `Engano comum` ou `Erro comum` na versao correta da apresentacao.
9. Substituir a proposta de extensao do PRAC por GRADMAX e scripts de Russ para microfitas.
10. Explicitar a frequencia ao discutir a viabilidade fisica da corneta.
11. Incluir a referencia de Bergmann et al. (1988) ao mencionar refletores omnidirecionais no plano da terra.
12. Atualizar roteiro, tabelas, imagens e conclusoes para nao recomendar parabólicas como solucao geral de LoRa.

**Criterio de aceite:** cada observacao do e-mail pode ser ligada a um trecho corrigido do relatorio ou da apresentacao.

### Fase 9 - Testes e validacao final

1. Adicionar testes unitarios do importador da planilha e do solver da corneta.
2. Testar pontos exatos, pontos interpolados e entradas fora da faixa.
3. Adicionar testes da API do Sandbox para a corneta.
4. Adicionar testes de persistencia na Biblioteca.
5. Adicionar testes de ganho efetivo no boresight e fora dele.
6. Adicionar comparacao de gateway multi-azimute para impedir conclusao baseada apenas no ganho maximo.
7. Executar a suite completa com `uv run pytest`.
8. Revisar manualmente os slides contra o e-mail e conferir referencias, unidades e frequencia.

**Criterio de aceite:** testes automatizados passam e uma lista de verificacao demonstra cobertura de todas as orientacoes do professor.

### 3.1 Componentes impactados

| Componente | Arquivos atuais | Impacto planejado |
|---|---|---|
| Contrato de antena | `backend/app/schemas/antenna_spec.py` | Validar se os campos genericos bastam; adicionar apenas validacoes sustentadas pelos dados |
| Presets | `backend/app/domain/antenna_presets.py` | Registrar corneta somente apos obter parametros confiaveis |
| Solver | `backend/app/solvers/` e `backend/app/solvers/__init__.py` | Criar modelo orientado pelos dados da planilha e registrar o tipo |
| Sandbox API | `backend/app/api/sandbox_routes.py` | Aceitar, simular e devolver o diagrama da corneta |
| Link budget | `backend/app/domain/link_budget.py` | Aplicar ganho angular e orientacao da corneta |
| Ranking | `backend/app/domain/comparison.py` | Incluir corneta sem confundir ganho maximo com adequacao multi-azimute |
| Interface | `frontend/public/sandbox.html` | Adicionar tipo, entradas confirmadas e visualizacoes |
| Biblioteca | `backend/app/storage/antenna_storage.py`, `backend/app/api/library_routes.py`, `frontend/public/library.html` | Verificar persistencia e exibicao do novo tipo |
| Link Planner | `backend/app/api/link_routes.py`, `frontend/public/link-planner.html` | Permitir selecao e comparacao da corneta |
| MATLAB | `.reports/externo/prompt/return/*.m` como referencia e local principal ainda a definir | Substituir cenarios PRAC/parabola e recalcular resultados |
| Apresentacao | `__roteiro/apres-v3.tex`, possivelmente `__roteiro/apres-v2.tex` | Corrigir terminologia, ferramentas e conclusoes |
| Roteiro oral | `__roteiro/versao-1.md`, `__roteiro/versao-2.md` | Alinhar falas com a nova simulacao e suas limitacoes |
| Documentacao | `docs/antenna-spec-schema.md`, `docs/simulation-modes.md`, `docs/calculos/`, `docs/for-dummies/04-tipos-de-antena.md` | Documentar corneta, fonte dos dados e limites |
| Testes | `tests/test_solvers.py`, `tests/test_sandbox.py`, `tests/test_new_antenna_solvers.py`, `tests/test_phase3_link_budget.py`, `tests/test_comparison.py`, `tests/test_library.py` | Cobrir solver, API, persistencia e comparacoes |

## 4. Riscos ou Pontos Omissos no E-mail

### 4.1 Riscos tecnicos

- **Planilha ausente:** sem ela, nao e possivel implementar ou validar o modelo solicitado.
- **Frequencia ausente:** impede avaliar dimensoes e viabilidade fisica da corneta.
- **Geometria ausente:** `corneta` pode designar modelos diferentes, com parametros distintos.
- **Ganho e HPBW ausentes:** impedem criar preset e comparar numericamente com as antenas atuais.
- **Setorizacao indefinida:** o e-mail menciona a possibilidade, mas nao define quantidade de setores nem regra de composicao.
- **Criterio de ganho indefinido:** o limite entre baixo e alto ganho deve ser investigado e justificado, nao presumido.
- **Fonte principal MATLAB indefinida:** os arquivos detalhados estao em uma pasta de retorno externo; e necessario decidir onde manter a implementacao oficial.
- **Numeracao de slides divergente:** editar pelo numero pode alterar o conteudo errado.
- **Relatorio final nao localizado:** nao esta claro qual arquivo recebe as correcoes academicas.
- **Prazo sem ano:** `1 de julho` foi informado, mas o ano nao aparece no e-mail.

### 4.2 Pontos a Clarificar com o remetente

1. Qual subtipo de corneta deve ser simulado?
2. Qual e a frequencia ou faixa de frequencias obrigatoria?
3. Onde esta a planilha Excel e qual versao deve ser considerada oficial?
4. Quais abas, colunas e curvas da planilha devem alimentar a simulacao?
5. O ganho da planilha e ganho realizado, diretividade ou ganho normalizado?
6. A corneta deve substituir integralmente a parabola ou apenas ser adicionada para comparacao?
7. Os diagramas de parabola podem permanecer em quais slides e com qual rotulo de limitacao?
8. A setorizacao deve ser simulada? Em caso positivo, quantos setores e quais azimutes devem ser usados?
9. Qual faixa de ganho o professor considera necessaria para a aplicacao?
10. O valor que separa baixo e alto ganho deve vir de uma referencia especifica ou da investigacao comparativa da equipe?
11. Qual edicao e capitulo do livro de Stutzman devem ser citados para area equivalente?
12. Quais scripts de Russ devem ser usados e onde eles estao disponiveis?
13. Qual versao da apresentacao corresponde aos slides 5 e 16 mencionados?
14. Qual e o arquivo oficial do relatorio a ser corrigido?
15. A data de 1 de julho se refere a qual ano e horario-limite?

## Ordem recomendada

As Fases 0 e 1 sao bloqueantes. Depois delas, executar as Fases 2 a 7 em sequencia. A Fase 8 pode comecar pelas correcoes textuais que nao dependem da planilha, mas tabelas, conclusoes e comparacoes devem aguardar os novos resultados. Finalizar com a Fase 9.
