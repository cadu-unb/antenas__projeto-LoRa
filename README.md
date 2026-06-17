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
