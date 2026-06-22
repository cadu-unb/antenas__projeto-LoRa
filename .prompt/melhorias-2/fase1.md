# Prompt — Melhorias 2 — Fase 1

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 1 — Correções Documentais**. Antes de editar, leia também `.reports/melhorias-2/quadro-antenas.md` para confirmar a equivalência entre os tipos Python e os modelos externos MATLAB.

## Objetivo

Atualizar a documentação para refletir o estado atual do sistema de antenas: o código Python já aceita 6 tipos de antena, não apenas 4.

## Arquivos alvo

- `docs/antenna-spec-schema.md`
- `docs/for-dummies/04-tipos-de-antena.md`
- `docs/for-dummies/05-como-criar-antena-no-sandbox.md`
- `.reports/externo/resume.md`, somente se ainda for tratado como relatório vivo

## Passos

1. Leia o plano e o quadro de antenas.
2. Confirme no código a lista atual de tipos aceitos no registry de solvers e no sandbox.
3. Atualize a documentação para incluir:
   - `dipolo`
   - `monopolo`
   - `helicoidal`
   - `parabolica`
   - `pcb_compact`
   - `commercial_omni_6dbi`
4. Corrija qualquer texto que diga que Python possui somente 4 tipos de antena.
5. Documente que o sistema atual já possui:
   - ENU 3D;
   - ganho direcional via `pattern_g()` quando `azimuth_deg` é definido;
   - perdas extras via `NodeSpec`.
6. Inclua uma tabela curta de equivalência entre tipos Python e modelos MATLAB externos.
7. Explique que `geometry` continua livre, mas que o plano prevê campos físicos opcionais no topo de `AntennaSpec`.

## Critérios de aceite

- A documentação não contradiz o código atual.
- Os 6 tipos aparecem nos guias e no schema documentado.
- O texto separa claramente campos de antena (`AntennaSpec`) e campos de nó/enlace (`NodeSpec`).

## Validação

Execute, se possível:

```powershell
rg -n "pcb_compact|commercial_omni_6dbi|dipolo|monopolo|helicoidal|parabolica" docs
```

Revise manualmente os exemplos JSON atualizados.

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase1.md` descrevendo:

- arquivos alterados;
- principais correções feitas;
- validações executadas;
- pendências ou riscos restantes.
