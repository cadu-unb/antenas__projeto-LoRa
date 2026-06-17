# Fase 6.5 — Revisão PyNEC e Dependências

**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Motivação

Fase 6 marcou PyNEC como "não instalável no Windows" (limitação fixa). Usuário confirmou PyNEC instalado em WSL2/Ubuntu — revisão necessária para refletir que PyNEC é instalável e documentar o caminho correto.

---

## Mudanças realizadas

### `pyproject.toml` — PyNEC como dependência opcional

```toml
[project.optional-dependencies]
mom = ["PyNEC>=1.7.3.4"]
```

Instalar com:
```bash
uv pip install PyNEC
# ou
pip install -e ".[mom]"
```

### `tests/test_solvers.py` — testes condicionais

`test_mom_solver_fallback_sem_pynec` agora usa `@pytest.mark.skipif(_PYNEC_AVAILABLE)`.

Quando PyNEC **não** estiver instalado (Windows sem compilador):
- `test_mom_solver_fallback_sem_pynec` roda → verifica `solver_used == "mom_analitico"` e `warning` presente

Quando PyNEC **estiver** instalado (Linux / WSL2):
- `test_mom_solver_fallback_sem_pynec` é pulado
- `test_mom_solver_pynec_quando_disponivel` roda → verifica `solver_used == "mom_pynec"`, `warning is None`, ganho 1.8–2.5 dBi

### `README.md` — instruções de instalação PyNEC

Seção adicionada com dois caminhos:

**Linux / WSL2 (recomendado):**
```bash
pip install PyNEC
# ou
uv pip install PyNEC
```

**Windows nativo:**

Opção A — MSVC (Visual Studio Build Tools):
1. Instalar [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Selecionar "Desenvolvimento para desktop com C++"
3. `pip install PyNEC`

Opção B — MinGW-w64:
1. Instalar [MinGW-w64](https://www.mingw-w64.org/)
2. Adicionar `C:\mingw64\bin` ao PATH
3. `pip install PyNEC`

> Recomendação: usar WSL2 (Ubuntu) elimina dependência de compilador no Windows.

### `.reports/sistema-antenas/Fase_6.md` — seção "Erros conhecidos" atualizada

"PyNEC não instalável no Windows" substituído por descrição correta: requer compilador C, instruções no README, fallback automático quando ausente.

### `docs/calculos/03-metodo-dos-momentos-mom.md` — seção "Implementação" atualizada

Adicionadas instruções de instalação (Linux/WSL2 e Windows). Campo `solver_used` documentado para ambos os casos.

---

## Para usar PyNEC no WSL2

```bash
# no WSL2
uv pip install PyNEC
pytest tests/test_solvers.py -v
# test_mom_solver_pynec_quando_disponivel vai rodar (não pular)
```

---

## Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `pyproject.toml` | `[project.optional-dependencies] mom = ["PyNEC>=1.7.3.4"]` |
| `tests/test_solvers.py` | `skipif` condicional + novo `test_mom_solver_pynec_quando_disponivel` |
| `README.md` | Seção "Solver MoM (PyNEC) — opcional" com instruções por plataforma |
| `.reports/sistema-antenas/Fase_6.md` | Seção "Erros conhecidos" corrigida |
| `docs/calculos/03-metodo-dos-momentos-mom.md` | Seção "Implementação" com instruções de instalação |
