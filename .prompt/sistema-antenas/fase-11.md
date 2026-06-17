# Prompt — Sistema de Antenas LoRa — Fase 11

## Objetivo

Documentação Parte II: cobrir funcionalidades das Fases 9 e 10.

Atualizar guias, schemas, READMEs e escopo negativo.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_10.md`, se existir

## Tarefas

1. Completar:
   - `docs/for-dummies/14-como-criar-malha-manual.md`
   - `docs/for-dummies/15-como-criar-topologia-multi-estrela.md`
   - `docs/for-dummies/16-como-usar-site-selection.md`
   - `docs/for-dummies/17-como-interpretar-cobertura.md`
2. Atualizar `docs/for-dummies/09-como-montar-enlace.md` — adicionar seção sobre topologias avançadas.
3. Atualizar `docs/link-planner-schema.md`:
   - documentar `topology_type` e todos os valores válidos;
   - documentar `CandidateSite`;
   - documentar `CoverageResult`.
4. Criar `docs/calculos/11-site-selection-e-cobertura.md`:
   - método de cálculo de cobertura por candidato;
   - como altitude da torre entra no modelo;
   - limitações (sem otimização automática, sem ray tracing).
5. Verificar `README.md` em toda pasta criada ou alterada nas Fases 9–10.
6. Atualizar seção **Fora do MVP / Escopo Negativo** no `README.md` raiz:
   - remover itens agora implementados;
   - adicionar novos limites: sem otimização automática de posição de torre, sem ray tracing urbano.
7. Testar fluxo end-to-end estendido:
   - criar antena no sandbox;
   - salvar na biblioteca;
   - montar malha manual com múltiplos hubs;
   - rodar site selection com candidatos fixos;
   - exportar cenário completo como JSON.

## Checkpoints obrigatórios

- [ ] `docs/for-dummies/14` a `17` preenchidos e revisados
- [ ] `docs/for-dummies/09` atualizado com seção de topologias avançadas
- [ ] `docs/link-planner-schema.md` documenta `topology_type`, `CandidateSite` e `CoverageResult`
- [ ] `docs/calculos/11` explica método + limitações do site selection
- [ ] Toda pasta nova das Fases 9–10 tem `README.md` não-stub
- [ ] `README.md` raiz com escopo negativo atualizado
- [ ] Fluxo end-to-end estendido funciona sem erro inesperado

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_11.md
```

O relatório deve conter:

- docs criadas e atualizadas;
- READMEs revisados;
- escopo negativo atualizado;
- resultado do teste end-to-end estendido;
- checkpoints marcados;
- pendências finais do projeto.

## Regra final

Não adicionar nova funcionalidade nesta fase. Apenas documentação, atualização e validação.
