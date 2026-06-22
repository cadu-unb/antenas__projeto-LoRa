# Report — Melhorias 2 — Fase 1

**Data:** 2026-06-22

## Arquivos alterados

| Arquivo | Correção principal |
|---|---|
| `docs/antenna-spec-schema.md` | Campo `type` atualizado para 6 tipos; adicionados exemplos JSON para `pcb_compact` e `commercial_omni_6dbi`; adicionadas tabela de equivalência Python↔MATLAB, seção de campos `AntennaSpec` vs `NodeSpec`, nota sobre ENU 3D e `pattern_g()`, nota sobre campos físicos opcionais futuros |
| `docs/for-dummies/04-tipos-de-antena.md` | Adicionadas seções PCB Compact e Commercial Omni 6dBi; tabela resumo expandida para 6 tipos com equivalências MATLAB |
| `docs/for-dummies/05-como-criar-antena-no-sandbox.md` | Passo 2 atualizado para listar 6 tipos; adicionada seção de parâmetros para `pcb_compact` e `commercial_omni_6dbi`; adicionada seção sobre ganho direcional, ENU 3D e separação `AntennaSpec`/`NodeSpec` |
| `docs/for-dummies/06-como-salvar-antena-json.md` | Tabela de campos obrigatórios: `type` atualizado para 6 opções |
| `docs/for-dummies/12-erros-comuns-e-como-resolver.md` | Mensagem de erro "tipo sem solver" corrigida para listar os 6 tipos aceitos |
| `docs/for-dummies/README.md` | Linha do `04-tipos-de-antena.md` atualizada para mencionar PCB Compact e Commercial Omni |
| `.reports/externo/resume.md` | Gap #1 corrigido (ganho direcional parcialmente implementado); Gap #2 corrigido (6 tipos implementados, tabela de equivalência adicionada); Gap #4 corrigido (perdas todas em `NodeSpec`, tabela de equivalência adicionada); tabela de prioridades atualizada com status de gaps resolvidos |

## Principais correções

1. `docs/antenna-spec-schema.md` dizia `type` = 4 valores → agora lista 6.
2. `04-tipos-de-antena.md` e `05-como-criar-antena-no-sandbox.md` não mencionavam `pcb_compact` nem `commercial_omni_6dbi`.
3. `12-erros-comuns-e-como-resolver.md` orientava usar "apenas 4 tipos" → corrigido.
4. `resume.md` marcava gaps #1, #2 e #4 como não implementados → corrigidos para refletir estado real do código.

## Validações executadas

```
rg -n "pcb_compact|commercial_omni_6dbi|dipolo|monopolo|helicoidal|parabolica" docs/
```

Resultado: todos 6 tipos aparecem em `antenna-spec-schema.md`, `04-tipos-de-antena.md`, `05-como-criar-antena-no-sandbox.md`, `06-como-salvar-antena-json.md` e `12-erros-comuns-e-como-resolver.md`.

Confirmado no registry de solvers (`backend/app/solvers/__init__.py`): todos 6 tipos mapeados.

## Pendências e riscos

| Pendência | Detalhe |
|---|---|
| `docs/for-dummies/07-como-usar-a-biblioteca.md` | Ainda menciona "Tipo (dipolo, monopolo, helicoidal, parabólica)" — campo visual de filtro. Baixa prioridade; não contradiz schema. |
| `docs/calculos/03-metodo-dos-momentos-mom.md` | Lista apenas 3 tipos no escopo do MoM — correto (pcb e colinear não usam MoM), mas pode confundir. Não é erro — é escopo do documento. |
| `resume.md` — prioridades restantes | Gaps #3 (módulos LoRa), #5 (cenários A–E) e #6 (orientação automática de antena) permanecem abertos. Fora do escopo desta fase. |
| Campos físicos opcionais em `AntennaSpec` | Documentados como planejados, mas não implementados. Schema ainda na versão `"1.0"` sem os novos campos. Fase 2 endereça. |
