# Sistema de Antenas LoRa/LoRaWAN — Campus Darcy Ribeiro UnB

Imagem Docker da plataforma educacional desenvolvida para modelagem simplificada de antenas e planejamento de enlaces LoRa/LoRaWAN no contexto de botões de emergência para o Campus Darcy Ribeiro da Universidade de Brasília.

## Sobre a imagem

Esta imagem empacota uma aplicação Web com backend FastAPI e frontend estático em HTML/CSS/JavaScript. A plataforma permite criar modelos de antenas, visualizar parâmetros eletromagnéticos aproximados, salvar especificações em JSON e estimar a viabilidade de enlaces LoRa entre pontos geográficos.

O projeto foi desenvolvido como trabalho final da disciplina de Antenas e combina conceitos de engenharia de telecomunicações, simulação eletromagnética e planejamento de cobertura.

## Principais recursos

- Sandbox para criação e pré-visualização de antenas.
- Biblioteca de antenas com importação e exportação em JSON.
- Link Planner para cálculo de enlaces ponto a ponto e multi-nó.
- Estimativa de distância, azimute, elevação, FSPL, potência recebida e margem de enlace.
- Modelos de antenas como dipolo, monopolo, helicoidal, parabólica, PCB compacta e omnidirecional comercial de 6 dBi.
- Suporte a perdas de cabo, perdas extras, margem de fading, polarização e orientação de antena.
- Solvers analíticos e suporte a PyNEC/NEC-2 para simulações em modo mais detalhado.
- Modelos de propagação como FSPL, Okumura-Hata e Longley-Rice no backend.
- Importação de KML para pontos e geometrias visuais do cenário.

## Tecnologias incluídas

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- UV
- Frontend estático sem framework
- PyNEC compilado a partir do código-fonte
- Ferramentas de build necessárias para NEC/PyNEC

## Como executar

Exemplo usando Docker:

```bash
docker run --rm -p 8000:8000 <nome-da-imagem>
```

Depois acesse:

```text
http://localhost:8000
```

Rotas úteis:

- `/` — interface principal/Sandbox
- `/library.html` — biblioteca de antenas
- `/link-planner.html` — planejador de enlaces
- `/health` — verificação simples da API

## Persistência de dados

A aplicação usa arquivos JSON para salvar dados do backend. Para manter os dados entre execuções, monte um volume no diretório:

```text
/app/backend/data
```

Exemplo:

```bash
docker run --rm -p 8000:8000 -v ./backend/data:/app/backend/data <nome-da-imagem>
```

## Escopo e limitações

Esta imagem não entrega um simulador urbano completo. O objetivo é educacional e de apoio ao planejamento inicial de enlaces.

Limitações assumidas:

- Não faz detecção automática de obstáculos por imagem.
- Não implementa ray tracing urbano completo.
- Polígonos KML são usados principalmente como referência visual.
- Antenas parabólicas grandes usam aproximação de abertura.
- O resultado deve ser interpretado como estimativa técnica inicial, não como validação de campo definitiva.

## Contexto acadêmico

Projeto final da disciplina de Antenas, orientado ao estudo de redes LoRa/LoRaWAN para comunicação de emergência em ambiente universitário. A plataforma ajuda a visualizar como frequência, geometria da antena, ganho, perdas e distância afetam a margem de enlace.

## Resumo curto

Plataforma Web em Docker para simular antenas e estimar enlaces LoRa/LoRaWAN, com foco educacional em planejamento de cobertura, link budget e comparação de antenas para um sistema de botões de emergência no Campus Darcy Ribeiro da UnB.
