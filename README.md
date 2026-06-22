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


```bash

# hard copile
docker compose build 2>&1 | tail -100 && docker compose up -d
docker compose build --no-cache 2>&1 && docker compose up -d --force-recreate
```