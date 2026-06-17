# Avaliação do `.plan/plan_v2.md`

## Contexto analisado

Arquivos-base lidos:

- `.plan/g1.md`
- `.plan/open1.md`
- `.plan/plan_v2.md`

Versão considerada mais atual:

- `.plan/plan_v2.md`

## Síntese geral

O `plan_v2.md` é uma evolução clara dos planos anteriores. Ele transforma ideias soltas sobre antenas, simulação, enlace, KML e documentação em um roadmap por fases, com objetos centrais (`AntennaSpec`, `NodeSpec`, `LinkScenario`) e checkpoints verificáveis.

O ponto forte principal é a organização incremental: primeiro estrutura, depois biblioteca, sandbox, solvers, link planner, fila de jobs e documentação.

O ponto fraco principal é o tamanho do escopo. O plano mistura MVP, produto completo, simulação pesada, documentação extensa e arquitetura final. Isso pode atrasar a primeira versão funcional se não houver cortes claros.

## Pontos fortes

### 1. Boa divisão em fases

O plano separa o desenvolvimento em 7 fases:

1. estrutura e fundação;
2. schema e biblioteca;
3. sandbox;
4. solvers e propagação;
5. link planner;
6. fila de jobs;
7. documentação e polimento.

Isso ajuda a evitar que o projeto comece direto pela parte mais difícil, como MoM, Longley-Rice ou Ray Tracing.

Solução para preservar esse ponto forte:

- Manter as fases.
- Só iniciar uma fase quando o checkpoint da fase anterior estiver funcionando.
- Criar relatório real ao fim de cada fase em `.reports/sistema-antenas/Fase_X.md`.

### 2. Objetos centrais bem escolhidos

O plano usa três objetos principais:

- `AntennaSpec`
- `NodeSpec`
- `LinkScenario`

Essa escolha é boa porque conecta o sandbox, a biblioteca e o link planner.

Solução para fortalecer:

- Criar schemas Pydantic logo na Fase 2.
- Criar exemplos JSON reais para cada objeto.
- Usar os mesmos schemas no backend, nos testes e na documentação.

### 3. Separação correta entre sandbox, biblioteca e enlace

O plano entende que criar uma antena não basta. A antena precisa ser salva e reaproveitada depois no módulo de enlace.

Isso resolve um problema dos planos anteriores: a antena simulada não fica solta.

Solução para fortalecer:

- Fazer a biblioteca funcionar antes do sandbox completo.
- Permitir salvar, listar, abrir, duplicar, importar e exportar antenas.
- Fazer o link planner depender de antenas salvas, não de dados duplicados.

### 4. Checkpoints objetivos

Cada fase tem critérios de validação.

Exemplos bons:

- `GET /health` retorna `{"status": "ok"}`;
- frontend entrega `index.html`;
- `POST /api/v1/antennas` salva JSON;
- simulação rápida retorna em menos de 2 segundos;
- job pesado retorna `job_id`.

Solução para fortalecer:

- Converter checkpoints em testes automatizados quando possível.
- Separar checkpoint manual de checkpoint automatizável.
- Criar script de verificação por fase.

### 5. Boa preocupação com limites computacionais

O plano prevê:

- limite de RAM;
- limite de tempo;
- log parcial;
- erro claro para o usuário.

Isso é importante porque simulação eletromagnética pode ficar pesada.

Solução para fortalecer:

- Na Fase 1 ou 2, criar configuração central de limites.
- Não esperar a Fase 4 para pensar em erro e timeout.
- Tratar limite de RAM como proteção do sistema, não como detalhe do solver.

### 6. Documentação aparece como parte do produto

O plano exige documentação `for-dummies`, documentação de cálculos e `README.md` em pastas.

Isso é excelente para um projeto técnico com matemática, antenas, simulação e KML.

Solução para fortalecer:

- Criar docs mínimas desde a Fase 1.
- Completar docs progressivamente.
- Não deixar toda documentação real para a Fase 7.

## Pontos fracos

### 1. Escopo grande demais para um MVP

O plano inclui:

- backend;
- frontend;
- biblioteca;
- sandbox visual;
- vários tipos de antena;
- MoM;
- PyNEC;
- abertura para parabólica;
- Okumura-Hata;
- Longley-Rice;
- Ray Tracing;
- KML;
- Leaflet;
- fila de jobs;
- documentação extensa.

Tudo isso é válido, mas grande demais para primeira entrega.

Solução:

- Definir um MVP menor:
  1. FastAPI com `/health`;
  2. CRUD de `AntennaSpec`;
  3. sandbox rápido analítico para dipolo;
  4. biblioteca de antenas;
  5. link budget simples entre dois nós;
  6. documentação mínima.

Deixar para depois:

- MoM completo;
- Longley-Rice;
- Ray Tracing;
- malha complexa;
- jobs assíncronos avançados.

### 2. Fase 1 pode virar trabalho burocrático

A Fase 1 exige `README.md` em toda pasta criada. Isso é bom, mas pode atrasar o primeiro sistema rodando.

Solução:

- Na Fase 1, criar apenas README curto nas pastas principais.
- Completar README detalhado na Fase 7.
- Trocar “toda pasta” por “toda pasta pública ou importante”.

### 3. Express pode ser excesso no início

O plano diz que o frontend usa Express como servidor estático/proxy.

Isso pode ser útil, mas no começo adiciona Node, `package.json`, proxy e mais uma camada para depurar.

Solução:

- Opção A: manter Express, mas limitar a servir arquivos estáticos.
- Opção B: no MVP, servir frontend estático pelo próprio FastAPI.
- Só adicionar Express se houver motivo claro.

### 4. Solvers técnicos aparecem cedo demais como obrigação

A Fase 4 exige MoM via PyNEC, Longley-Rice e guardião de recursos.

Isso é tecnicamente pesado e pode travar o projeto se entrar antes do fluxo básico estar maduro.

Solução:

- Criar interface de solver primeiro.
- Implementar solver analítico simples antes.
- Tratar PyNEC e Longley-Rice como plugins futuros.
- Criar dados falsos controlados para desenvolver UI antes da simulação real.

### 5. `docs/for-dummies` e `docs/for-dummy` estão inconsistentes

O histórico do projeto usa `docs/for-dummy/`, mas o `plan_v2.md` usa `docs/for-dummies/`.

Isso cria confusão de padrão.

Solução:

- Escolher um nome único.
- Recomendação: usar `docs/for-dummy/`, porque já foi usado nas skills/documentação do repositório.
- Atualizar `plan_v2.md` para não alternar nomes.

### 6. `.report/` conflita com padrão atual `.reports/`

O `plan_v2.md` manda escrever relatórios em `.report/sistema-antenas/Fase_X.md`.

Mas o padrão corrigido no repositório é `.reports/`.

Solução:

- Trocar todos os destinos:

```text
.report/sistema-antenas/Fase_X.md
```

por:

```text
.reports/sistema-antenas/Fase_X.md
```

### 7. Critérios de sucesso técnicos precisam de tolerância

Exemplo:

- “Dipolo λ/2 em modo PADRAO → ganho ~2.15 dBi”

Isso é bom, mas precisa de tolerância, ambiente e método.

Solução:

- Usar critérios como:

```text
ganho esperado entre 1.8 dBi e 2.5 dBi para cenário de referência documentado
```

- Criar fixtures de teste com entrada fixa.
- Documentar condições do cálculo.

### 8. KML nível 1 pode parecer mais simples do que é

O plano diz que polígonos KML entram como obstáculos.

Isso é possível, mas transformar polígonos em perda real exige altura, material, interseção geométrica e modelo de penalidade.

Solução:

- No MVP, renderizar polígonos no mapa.
- Depois, aplicar penalidade manual configurável.
- Só chamar de obstáculo físico quando houver altura/material.

### 9. Ray Tracing deve ficar fora do MVP real

O plano coloca Ray Tracing como modo preciso no Link Planner.

Sem modelo 3D confiável, ele pode virar visual bonito, mas tecnicamente fraco.

Solução:

- Documentar Ray Tracing como fora do MVP.
- Manter gancho de arquitetura para futuro.
- Priorizar FSPL, Okumura-Hata e Longley-Rice antes.

### 10. Falta seção explícita de riscos

O plano tem fases e checkpoints, mas não lista riscos.

Riscos principais:

- PyNEC difícil de instalar no Windows;
- Longley-Rice pode exigir biblioteca externa;
- KML pode não ter altitude útil;
- simulação pesada pode travar máquina;
- frontend pode ficar complexo sem framework;
- escopo pode crescer antes de existir MVP.

Solução:

- Adicionar seção “Riscos e mitigação” no fim do plano.
- Para cada risco, escrever plano B.

## Soluções prioritárias

### Prioridade 1 — Ajustar convenções de pasta

Corrigir no plano:

- usar `.reports/`, não `.report/`;
- usar `docs/for-dummy/` ou `docs/for-dummies/`, mas não ambos;
- manter `.codex/skills/` para skills do Codex.

### Prioridade 2 — Definir MVP menor

MVP recomendado:

1. Backend FastAPI.
2. `GET /health`.
3. Schema `AntennaSpec`.
4. CRUD de antenas em JSON.
5. Frontend simples para listar e salvar antenas.
6. Preview analítico simples para um tipo de antena.
7. Link budget P2P simples.
8. Relatório e documentação mínima.

### Prioridade 3 — Adiar simulação pesada

Mover para fase futura:

- PyNEC;
- Ray Tracing;
- Longley-Rice completo;
- fila complexa de jobs;
- modo experimental.

Antes disso, criar:

- interfaces;
- contratos JSON;
- logs;
- erros claros;
- testes com dados fixos.

### Prioridade 4 — Transformar checkpoints em testes

Criar testes para:

- validação de schema;
- salvar e listar antenas;
- rejeitar JSON inválido;
- calcular distância entre dois pontos;
- calcular FSPL;
- retornar `/health`.

### Prioridade 5 — Separar “produto”, “engenharia” e “pesquisa”

Produto:

- telas;
- fluxos;
- import/export;
- mensagens de erro.

Engenharia:

- schemas;
- rotas;
- storage;
- testes;
- logs.

Pesquisa:

- solvers pesados;
- modelos avançados;
- Ray Tracing;
- validação científica.

Essa separação evita que pesquisa bloqueie produto.

## Proposta de revisão para o início do plano

Sugestão de novo recorte:

```text
Fase 0 — Convenções do repositório
- definir .reports/
- definir docs/for-dummy/
- definir .codex/skills/
- definir stack inicial

Fase 1 — Backend mínimo
- FastAPI
- GET /health
- estrutura de pastas
- teste básico

Fase 2 — AntennaSpec e biblioteca
- schema
- CRUD JSON
- import/export

Fase 3 — Sandbox rápido
- formulário simples
- preview analítico
- salvar na biblioteca

Fase 4 — Link budget P2P
- NodeSpec
- LinkScenario mínimo
- distância, FSPL, margem

Fase 5 — KML e mapa
- importar pontos
- renderizar no mapa
- associar antenas

Fase 6 — Solvers avançados
- MoM
- Longley-Rice
- guardião de recursos

Fase 7 — Jobs e simulações pesadas
- fila
- polling
- cancelamento

Fase 8 — Documentação e polimento
- completar docs
- revisar UX
- validar fluxo completo
```

## Conclusão

O `plan_v2.md` é uma boa base arquitetural. Ele está mais maduro que `g1.md` porque cria fases, checkpoints, objetos centrais e contratos entre módulos.

Mas ainda precisa de cortes para virar execução real.

Melhor caminho:

1. corrigir convenções de pasta;
2. reduzir MVP;
3. implementar contratos JSON primeiro;
4. adiar solvers pesados;
5. documentar riscos;
6. transformar checkpoints em testes.

Assim o projeto ganha uma primeira versão funcional antes de entrar nas partes mais caras: MoM, Longley-Rice, Ray Tracing e fila de jobs.
