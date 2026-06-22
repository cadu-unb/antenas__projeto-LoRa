# projeto-LoRa

Projeto final do curso de Antenas — Prof. Marco Antônio Brasil Terada, 2026/1.

Sistema de planejamento de enlace LoRa com solvers eletromagnéticos (MoM via NEC-2, abertura, Okumura-Hata, Longley-Rice).

## Instalação

```bash
# dependências base
uv sync

# backend
uvicorn backend.app.main:app --reload
```

## Solver MoM (PyNEC) — opcional

O modo **Padrão/Preciso** usa PyNEC (Python wrapper para NEC-2) quando disponível.
Sem PyNEC, o sistema usa fallback analítico automaticamente — nenhuma funcionalidade é perdida.

### Linux / WSL2 (recomendado)

```bash
pip install PyNEC
# ou com uv:
uv pip install PyNEC
```

### Windows nativo

Requer compilador C instalado antes do `pip install PyNEC`:

**Opção A — MSVC (Visual Studio Build Tools):**
1. Instalar [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Selecionar "Desenvolvimento para desktop com C++"
3. `pip install PyNEC`

**Opção B — MinGW-w64:**
1. Instalar [MinGW-w64](https://www.mingw-w64.org/)
2. Adicionar `C:\mingw64\bin` ao PATH
3. `pip install PyNEC`

> Recomendação: usar WSL2 (Ubuntu) elimina dependência de compilador no Windows.

## Fora do MVP / Escopo Negativo

Funcionalidades fora do escopo deste projeto:

- **Sem detecção automática de obstáculos por imagem** — árvores, prédios e relevo não são identificados automaticamente por satélite ou câmera. Obstáculos físicos requerem modelo KML com altura e material.
- **Sem Ray Tracing urbano completo** — ray tracing 3D exige modelo geométrico da cena (edifícios, superfícies). O arquivo `solvers/ray_tracing_solver.py` é um stub arquitetural sem lógica implementada.
- **Sem MoM para parabólicas grandes** — antenas parabólicas usam aproximação de abertura (G = η·(πD/λ)²), não MoM. MoM em regime de óptica geométrica converge para o mesmo resultado com custo muito maior.
- **Sem KML nível 2** — KML com modelo 3D extrudado (edificações com altura e geometria) não é suportado. Polígonos KML (nível 1) são renderizados no mapa apenas visualmente, sem penalidade física de obstrução.
- **Sem otimização automática de posição de torre** — o sistema avalia candidatos marcados manualmente. Não sugere posições ideais por algoritmo.
- **Sem modelo de terreno em site selection** — cobertura calculada com FSPL puro. Modelos Longley-Rice e Okumura-Hata disponíveis para link budget, mas não integrados ao ranking de candidatos nesta versão.

## Documentação

- `docs/for-dummies/` — guias em linguagem acessível (instalação, uso, tipos de antena, erros comuns)
- `docs/calculos/` — documentação técnica dos métodos de cálculo (MoM, Okumura-Hata, Longley-Rice, link budget)
- `docs/calculos/10-referencias-tecnicas.md` — referências bibliográficas verificáveis


## Docker

Chamar o docker (linux):
```bash
sudo systemctl start docker
```

```bash
# hard copile
docker compose build 2>&1 | tail -100 && docker compose up -d
docker compose build --no-cache 2>&1 && docker compose up -d --force-recreate
```

## Como Publicar e Rodar a Imagem Docker do Projeto Antenas LoRa

Siga os passos abaixo para gerar a imagem do backend do projeto, publicá-la no Docker Hub e rodá-la em qualquer máquina.

---

### Passo 1: Criar uma conta no Docker Hub

Se ainda não tiver, acesse [hub.docker.com](https://hub.docker.com/) e crie uma conta gratuita. O usuário configurado para este exemplo é `cadu0`.

### Passo 2: Fazer login pelo Terminal

No terminal da sua máquina, conecte-se à sua conta do Docker Hub:

```bash
docker login
```

Insira o seu usuário (`cadu0`) e a sua senha, ou um Access Token gerado no site do Docker Hub.

### Passo 3: Criar a Imagem (Build) com a Tag Correta

Navegue até a pasta do projeto onde está o `Dockerfile` e rode:

```bash
docker build -t cadu0/antenas__projeto-lora-backend:v3 .
```

Atenção: o ponto `.` no final indica o contexto atual e é obrigatório. A tag `v3` identifica a versão da imagem.

Se você já buildou a imagem antes via Docker Compose, pode apenas renomeá-la localmente:

```bash
docker tag antenas__projeto-lora-backend cadu0/antenas__projeto-lora-backend:v3
```

### Passo 4: Enviar a Imagem (Push) para o Docker Hub

Agora, envie a imagem gerada para a nuvem:

```bash
docker push cadu0/antenas__projeto-lora-backend:v3
```

Isso pode levar alguns minutos dependendo do tamanho do projeto e da sua conexão de internet.

### Como rodar em qualquer outra máquina

Com a imagem publicada, você não precisa clonar o GitHub nem configurar o ambiente do zero em uma nova máquina. Basta que o novo computador tenha o Docker instalado e execute:

```bash
docker run -d -p 8000:8000 cadu0/antenas__projeto-lora-backend:v3
```

Depois, acesse:

```text
http://localhost:8000
```

Nota: este projeto está configurado para servir a aplicação na porta `8000`. Se você alterar a porta no Dockerfile ou no servidor, ajuste o trecho `-p 8000:8000` conforme necessário.
