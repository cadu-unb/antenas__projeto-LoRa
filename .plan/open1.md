Perfeito. O problema do `g1.md` não é que ele esteja “errado”; ele está **bom como visão inicial**, mas ainda mistura arquitetura, solver, visualização e produto na mesma camada. Ele já define a separação `core/`, `api/`, `static/` e `templates/`, as quatro antenas, os métodos MoM/Ray Tracing/Okumura-Hata/Longley-Rice e os limites da máquina.  O que falta agora é transformar isso em uma **especificação de sistema**, com contratos claros entre sandbox, biblioteca de antenas salvas e módulo de enlace.

Minha recomendação principal: **backend Python puro para cálculo e API; frontend em HTML/CSS/JS; Express apenas como servidor estático/proxy**, sem regra de negócio. Express não é exatamente “front-end”; ele é Node.js no lado servidor. Então, se a regra é “backend só Python”, o Express só deve entregar arquivos e repassar chamadas para a API Python. O Flask com Blueprints continua coerente com o desenho do `g1.md`, porque Blueprints servem justamente para modularizar componentes de aplicação. ([Flask][1]) Mas, se você quiser uma separação ainda mais clara por contrato de API, eu consideraria **FastAPI + Pydantic**, porque o FastAPI é orientado a APIs Python com type hints, validação e documentação OpenAPI automática. ([FastAPI][2])

A melhoria estrutural que eu faria é esta:

## 1. Separar o projeto em três domínios, não apenas duas telas

Em vez de pensar só em “Sandbox” e “Enlace”, pense em:

**1. Antenna Sandbox**
Onde o usuário cria, parametriza, simula e visualiza uma antena individual.

**2. Antenna Library**
Onde o usuário salva e carrega antenas em JSON. Essa biblioteca vira uma ponte entre o sandbox e o enlace.

**3. Link Planner**
Onde o usuário monta nós, escolhe antenas salvas, define orientação entre elas, importa KML e roda modelos de propagação.

Essa divisão resolve sua frustração principal: a antena criada no sandbox deixa de ser um resultado solto e passa a ser um **objeto reutilizável**.

## 2. O JSON da antena deve ser um “spec”, não só um dump de formulário

Eu salvaria cada antena assim:

```json
{
  "schema_version": "1.0",
  "id": "ant_2026_001",
  "name": "Dipolo 915 MHz - versão inicial",
  "type": "dipole",
  "frequency_hz": 915000000,
  "units": {
    "length": "m",
    "gain": "dBi",
    "power": "dBm"
  },
  "geometry": {
    "length_m": 0.164,
    "wire_radius_m": 0.0015,
    "segments": 31
  },
  "material": {
    "conductor": "copper",
    "conductivity_s_per_m": 58000000
  },
  "solver": {
    "method": "mom",
    "precision": "standard",
    "max_ram_gb": 25,
    "max_runtime_minutes": 30
  },
  "results": {
    "gain_peak_dbi": null,
    "impedance_ohm": null,
    "swr": null,
    "radiation_pattern_file": null
  },
  "metadata": {
    "created_at": "2026-06-16T00:00:00",
    "created_by": "user",
    "notes": "Antena criada no sandbox para uso posterior no enlace."
  }
}
```

O ponto importante: o JSON precisa guardar **entrada, método e resultado**. Assim, quando o usuário subir essa antena no enlace, o sistema sabe se ela já foi simulada, com qual método, em qual frequência e com qual limite computacional.

## 3. Visualmente, cada antena precisa ter quatro camadas

Para a parte de apresentação visual dos objetos, eu organizaria cada antena no sandbox com quatro painéis fixos:

**Painel 1: Forma física simplificada**
Desenho geométrico da antena com medidas: comprimento, raio, diâmetro, número de espiras, foco, refletor etc.

**Painel 2: Parâmetros editáveis**
Inputs organizados por blocos: frequência, geometria, material, alimentação, solver.

**Painel 3: Resultado eletromagnético**
Ganho, impedância, SWR, eficiência, largura de feixe, lóbulos principais e secundários.

**Painel 4: Visualização de irradiação**
Diagrama polar 2D e, se possível, lóbulo 3D.

Se você quiser manter o frontend absolutamente restrito a HTML/CSS/JS puro, use **SVG** para o desenho físico e **Canvas** para gráficos. Se aceitar uma biblioteca JS, eu recomendaria **Three.js** para visualizar antenas e lóbulos em 3D, porque é uma biblioteca JavaScript focada em renderização 3D na web. ([Three.js][3]) Para mapas do enlace, **Leaflet** é a recomendação leve e direta para mapas interativos. ([Leaflet][4]) Para gráficos 2D e 3D científicos, **Plotly.js** é mais pesado, mas já oferece vários tipos de gráficos, inclusive 3D. ([Plotly][5])

## 4. As quatro antenas devem ter visualizações específicas

Eu detalharia assim:

| Antena     | Visual físico                                                 | Resultado visual principal                         | Solver recomendado         |
| ---------- | ------------------------------------------------------------- | -------------------------------------------------- | -------------------------- |
| Dipolo     | Dois braços alinhados, alimentação central, comprimento total | Diagrama em “rosquinha”, polar horizontal/vertical | MoM                        |
| Monopolo   | Haste vertical sobre plano de terra                           | Diagrama omnidirecional com elevação               | MoM                        |
| Helicoidal | Espiras, passo, diâmetro e plano de terra                     | Lóbulo axial ou normal, conforme configuração      | MoM ou modelo aproximado   |
| Parabólica | Refletor, foco, alimentador, eixo de apontamento              | Feixe estreito, abertura angular, ganho diretivo   | Aproximação de abertura/PO |

O `g1.md` já acerta ao dizer que MoM faz sentido para dipolo, monopolo e helicoidal, enquanto a parabólica pode ficar pesada demais para MoM e tende a ser melhor tratada por aproximação de abertura/óptica física. 

## 5. No enlace, pense em grafo, não apenas em lista de antenas

A sua ideia das oito antenas é ótima. Eu modelaria o enlace como um **grafo configurável**:

```json
{
  "nodes": [
    {
      "id": "node_1",
      "name": "Antena 1",
      "lat": -15.763,
      "lon": -47.870,
      "height_m": 8,
      "antenna_spec_id": "ant_2026_001"
    }
  ],
  "links": [
    {
      "id": "link_1",
      "from": "node_1",
      "to": "node_2",
      "tx_antenna": "ant_2026_001",
      "rx_antenna": "ant_2026_002",
      "pointing_mode": "manual",
      "azimuth_deg": 42.5,
      "elevation_deg": 3.2
    }
  ]
}
```

Na interface, o usuário poderia escolher:

**Modo ponto a ponto:** antena 1 aponta para antena 2.
**Modo cadeia:** 1 → 2 → 3 → 4.
**Modo estrela:** todas apontam para uma antena central.
**Modo malha manual:** usuário cria enlaces livremente.
**Modo gateway setorial:** várias antenas no gateway, cada uma cobrindo um setor angular.

Isso é melhor do que “calcular tudo contra tudo” desde o início. Primeiro o usuário desenha a intenção do enlace; depois o backend calcula.

## 6. KML: dá para ler objetos, mas não “detectar” prédios e árvores automaticamente

Aqui precisa ficar bem claro no planejamento. O KML pode conter pontos, linhas, polígonos, modelos e multigeometrias; a referência do Google KML lista esses elementos, e a OGC também descreve KML como padrão com geometrias como ponto, linha, anel linear e polígono. ([Google for Developers][6]) Mas um KML **não detecta sozinho** árvores e prédios a partir da imagem do campus.

Então eu criaria três níveis:

**Nível 0: KML de pontos**
Só nós, coordenadas e talvez altitude. Serve para distância, azimute, elevação e link budget básico.

**Nível 1: KML com polígonos manuais**
Se o usuário desenhar prédios, bosques ou áreas de obstrução como polígonos, o sistema pode aplicar penalidades.

**Nível 2: Modelo 3D real**
Para ray tracing sério, seriam necessários dados 3D de prédios, alturas, materiais ou ao menos polígonos extrudados. Sem isso, o ray tracing vira uma aproximação visual, não uma simulação confiável.

## 7. Eu criaria modos de simulação, para controlar custo computacional

Como você aceita simulações longas, mas quer evitar estouro de memória, eu faria assim:

| Modo         | Uso                        | Métodos                                                           |
| ------------ | -------------------------- | ----------------------------------------------------------------- |
| Rápido       | Feedback instantâneo       | Fórmulas analíticas, FSPL, link budget simples                    |
| Padrão       | Resultado técnico razoável | MoM simplificado, Longley-Rice/Okumura-Hata, difração por terreno |
| Preciso      | Simulação pesada           | MoM com mais segmentos, ray tracing limitado, múltiplas reflexões |
| Experimental | Pesquisa                   | Ray tracing mais custoso, varredura de cenários, sensibilidade    |

O limite de 25 GB deve ser tratado como regra de execução:

```text
Se uso de RAM >= 25 GB:
  interromper processo
  salvar log parcial
  marcar job como FAILED_MEMORY_LIMIT
  retornar mensagem clara ao usuário
```

A mensagem da interface poderia ser:

```text
A simulação foi interrompida porque atingiu o limite de segurança de 25 GB de RAM. Reduza a precisão, diminua o número de segmentos, simplifique o cenário 3D ou execute em modo padrão.
```

## 8. Ray tracing deve entrar só na segunda vertente

Eu concordo com você: ray tracing faz mais sentido no **Link Planner**, não no sandbox isolado. No sandbox, o foco é a antena. No enlace, o foco é propagação, obstáculos, terreno e orientação.

Fluxo ideal:

```text
1. Usuário importa KML.
2. Sistema extrai nós, altitude e geometrias.
3. Usuário associa antenas salvas aos nós.
4. Usuário define enlaces.
5. Sistema calcula azimute, elevação, distância e visada.
6. Sistema roda modelo empírico.
7. Sistema oferece ray tracing se houver geometria suficiente.
8. Sistema compara os resultados.
```

O `g1.md` já prevê link budget com potência transmitida, ganhos, perdas, obstrução e sensibilidade LoRa, o que deve continuar sendo o núcleo técnico da segunda vertente. 

## 9. Estrutura revisada de pastas

Eu mudaria a estrutura para ficar mais clara:

```text
projeto-antenas/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── sandbox_routes.py
│   │   │   ├── library_routes.py
│   │   │   ├── link_routes.py
│   │   │   └── job_routes.py
│   │   ├── domain/
│   │   │   ├── antennas/
│   │   │   ├── propagation/
│   │   │   ├── link_planning/
│   │   │   └── kml/
│   │   ├── solvers/
│   │   │   ├── mom_solver.py
│   │   │   ├── aperture_solver.py
│   │   │   ├── ray_tracing_solver.py
│   │   │   ├── okumura_hata.py
│   │   │   └── longley_rice.py
│   │   ├── schemas/
│   │   ├── storage/
│   │   └── workers/
│   └── data/
│       ├── antenna_specs/
│       ├── simulations/
│       ├── kml_uploads/
│       └── reports/
│
├── frontend/
│   ├── server.js
│   ├── public/
│   │   ├── index.html
│   │   ├── sandbox.html
│   │   ├── library.html
│   │   ├── link-planner.html
│   │   ├── css/
│   │   └── js/
│   │       ├── api-client.js
│   │       ├── antenna-editor.js
│   │       ├── antenna-viewer.js
│   │       ├── link-builder.js
│   │       ├── map-viewer.js
│   │       └── job-monitor.js
│
└── docs/
    ├── for-Dummy/

    ├── architecture.md
    ├── antenna-spec-schema.md
    ├── link-planner-schema.md
    └── simulation-modes.md
```

## 10. O que ainda precisa entrar no `g1.md`

Eu acrescentaria estas seções:

1. **Contrato entre Sandbox e Link Planner**
   Explicar que antenas criadas no sandbox são salvas como `antenna_spec.json`.

2. **Biblioteca de antenas**
   Listar, importar, exportar, duplicar, versionar e excluir antenas.

3. **Modelo visual das antenas**
   Definir SVG/Canvas/Three.js, painéis, diagramas e cards.

4. **Modelo de enlace como grafo**
   Nós, antenas, apontamentos, links e cenários.

5. **Modos de simulação**
   Rápido, padrão, preciso e experimental.

6. **Política de memória e tempo**
   Limite de 25 GB, limite de 30 minutos, interrupção segura e log.

7. **KML e obstáculos**
   Separar KML de pontos, KML com polígonos e modelo 3D real.

8. **Fila de simulação**
   Simulações pesadas não devem travar a interface; devem rodar como jobs acompanháveis.

9. **Critérios de sucesso visual**
   Mapa, tabela, semáforo de viabilidade, margem de enlace e relatório exportável.

10. **Escopo negativo**
    Deixar claro o que não será feito no MVP: detecção automática de árvores por imagem, ray tracing urbano completo sem modelo 3D, MoM completo para parabólica grande etc.

Minha síntese: o projeto deve deixar de ser “uma calculadora de antenas com tela de enlace” e virar um sistema com **três objetos centrais**: `AntennaSpec`, `NodeSpec` e `LinkScenario`. Essa tríade resolve a estrutura, melhora a visualização e permite reutilizar no enlace tudo que foi criado no sandbox.

## Tópico Extra: Documentação Obrigatória do Projeto

Além da separação entre backend, frontend, sandbox, biblioteca de antenas e planejamento de enlace, o repositório deverá conter uma política explícita de documentação, com três exigências principais.

### 1. Pasta `docs/for-dummies/`

Criar a pasta:

```text
docs/for-dummies/
```

Essa pasta deverá conter explicações simples, passo a passo, em linguagem acessível, como se fossem guias “for dummies” do projeto. O objetivo é permitir que qualquer pessoa entenda, inicialize, use, teste e mantenha o sistema sem depender diretamente do desenvolvedor original.

Conteúdos mínimos sugeridos:

```text
docs/for-dummies/
├── README.md
├── 01-o-que-e-o-projeto.md
├── 02-como-instalar.md
├── 03-como-iniciar-backend.md
├── 04-como-iniciar-frontend.md
├── 05-como-criar-antena-no-sandbox.md
├── 06-como-salvar-antena-json.md
├── 07-como-carregar-antena-no-enlace.md
├── 08-como-importar-kml.md
├── 09-como-montar-enlace.md
├── 10-como-rodar-simulacao.md
├── 11-como-entender-resultados.md
├── 12-erros-comuns-e-como-resolver.md
└── 13-glossario-do-projeto.md
```

Cada arquivo deverá responder perguntas práticas, por exemplo:

* Como inicializar o projeto?
* Como instalar dependências?
* Como rodar backend e frontend?
* Como criar uma antena?
* Como salvar especificações em JSON?
* Como reaproveitar antenas no módulo de enlace?
* Como importar um KML?
* Como interpretar ganho, perda, margem de enlace, azimute e elevação?
* O que fazer quando uma simulação falha por memória, tempo ou entrada inválida?

### 2. `README.md` obrigatório em todas as pastas

Toda pasta do repositório deverá conter um `README.md`.

Esse arquivo deverá explicar brevemente:

* qual é a função da pasta;
* quais arquivos principais existem ali;
* o que cada arquivo faz;
* se a pasta é parte do backend, frontend, documentação, dados, testes ou simulações;
* se os arquivos são editáveis manualmente ou gerados automaticamente.

Exemplo mínimo de `README.md` por pasta:

```markdown
# Pasta: `backend/app/solvers`

Esta pasta contém os módulos responsáveis pelos métodos numéricos e empíricos usados nas simulações de antenas e enlaces.

## Arquivos

- `mom_solver.py`: implementa ou encapsula rotinas baseadas no Método dos Momentos para antenas de fio.
- `aperture_solver.py`: calcula aproximações de abertura para antenas parabólicas.
- `ray_tracing_solver.py`: executa simulações de propagação por traçado de raios quando houver dados geométricos suficientes.
- `okumura_hata.py`: calcula perda de percurso com modelo empírico Okumura-Hata.
- `longley_rice.py`: calcula perda de propagação sobre terreno irregular com Longley-Rice/ITM.

## Observação

Arquivos desta pasta fazem parte do núcleo técnico do backend. Alterações devem ser testadas com cuidado, pois afetam diretamente os resultados das simulações.
```

### 3. Documentação específica dos cálculos

Criar uma área específica para explicar os cálculos usados no projeto:

```text
docs/calculos/
```

Estrutura sugerida:

```text
docs/calculos/
├── README.md
├── 01-visao-geral-dos-calculos.md
├── 02-antenas-e-parametros.md
├── 03-metodo-dos-momentos-mom.md
├── 04-parabolica-aproximacao-abertura.md
├── 05-link-budget.md
├── 06-okumura-hata.md
├── 07-longley-rice-itm.md
├── 08-ray-tracing.md
├── 09-limites-computacionais.md
└── 10-referencias-tecnicas.md
```

Essa documentação deverá explicar, em linguagem clara:

* quais métodos são usados;
* em qual parte do sistema cada método entra;
* quais entradas são necessárias;
* quais saídas são geradas;
* quais limitações existem;
* quando o resultado é aproximação e quando é simulação mais pesada;
* quais referências técnicas justificam o uso do método.

Para métodos mais difíceis, como Método dos Momentos, Longley-Rice/ITM e Ray Tracing, não é necessário explicar toda a formulação matemática em profundidade no MVP. Basta apresentar:

* explicação conceitual;
* papel do método no projeto;
* parâmetros usados;
* limitações práticas;
* referência técnica confiável para aprofundamento.

### 4. Referências técnicas mínimas

O arquivo `docs/calculos/10-referencias-tecnicas.md` deverá conter referências reais e verificáveis para os métodos utilizados.

Referências mínimas recomendadas:

* Burke, G. J.; Poggio, A. J. *Numerical Electromagnetics Code (NEC): Method of Moments*. Lawrence Livermore Laboratory.
* Longley, A. G.; Rice, P. L. *Prediction of Tropospheric Radio Transmission Loss Over Irregular Terrain*. Modelo conhecido como Longley-Rice ou ITM.
* Hata, M. “Empirical Formula for Propagation Loss in Land Mobile Radio Services”. *IEEE Transactions on Vehicular Technology*, 1980.
* ITU-R P.1410. *Propagation data and prediction methods for the planning of short-range outdoor radiocommunication systems and radio local area networks*.
* Documentação técnica da biblioteca ou implementação efetivamente usada no projeto, quando houver.

### 5. Regra de ouro da documentação

Nenhuma pasta deve ser “autoexplicativa por intuição”.
Toda pasta deve explicar sua função.
Todo cálculo relevante deve ter justificativa.
Toda simulação pesada deve informar limite de memória, tempo máximo, precisão esperada e motivo de falha quando interrompida.


[1]: https://flask.palletsprojects.com/en/stable/blueprints/?utm_source=chatgpt.com "Modular Applications with Blueprints"
[2]: https://fastapi.tiangolo.com/?utm_source=chatgpt.com "FastAPI - FastAPI"
[3]: https://threejs.org/?utm_source=chatgpt.com "Three.js – JavaScript 3D Library"
[4]: https://leafletjs.com/?utm_source=chatgpt.com "Leaflet - a JavaScript library for interactive maps"
[5]: https://plotly.com/javascript/?utm_source=chatgpt.com "Plotly JavaScript Open Source Graphing Library"
[6]: https://developers.google.com/kml/documentation/kmlreference?utm_source=chatgpt.com "KML Reference | Keyhole Markup Language"
