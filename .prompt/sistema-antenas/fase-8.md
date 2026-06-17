# Prompt — Sistema de Antenas LoRa — Fase 8

## Objetivo

Completar documentação, polir UX de erros e validar fluxo end-to-end.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_7.md`, se existir

## Tarefas

1. Completar todos os 13 arquivos de `docs/for-dummies/`.
2. Completar todos os 10 arquivos de `docs/calculos/`.
3. Cada arquivo de cálculo deve conter:
   - conceito;
   - parâmetros;
   - limitações;
   - referência técnica.
4. Criar ou completar `docs/calculos/10-referencias-tecnicas.md` com:
   - Burke & Poggio, NEC;
   - Longley & Rice, ITM;
   - Hata, IEEE TVT 1980;
   - ITU-R P.1410.
5. Verificar `README.md` em toda pasta relevante.
6. Cada `README.md` deve explicar:
   - função da pasta;
   - arquivos principais;
   - se é editável ou gerado.
7. Atualizar `README.md` raiz com seção:

```text
Fora do MVP / Escopo Negativo
```

8. Escopo negativo deve declarar:
   - sem detecção automática de árvores/prédios por imagem;
   - sem Ray Tracing urbano completo sem modelo 3D;
   - sem MoM para parabólica grande;
   - sem KML nível 2.
9. Revisar mensagens de erro da UI.
10. Cada erro deve ter instrução acionável.
11. Testar fluxo end-to-end:
    - criar antena;
    - salvar na biblioteca;
    - montar enlace;
    - simular;
    - exportar resultado.

## Checkpoints obrigatórios

- [ ] Todos 13 arquivos de `docs/for-dummies/` estão preenchidos
- [ ] Todos 10 arquivos de `docs/calculos/` têm conceito, parâmetros, limitações e referência
- [ ] `docs/calculos/10-referencias-tecnicas.md` tem referências verificáveis
- [ ] Toda pasta relevante tem `README.md` não-stub
- [ ] `README.md` raiz documenta escopo negativo
- [ ] Fluxo end-to-end funciona sem erro inesperado
- [ ] Nenhuma mensagem de erro da UI fica sem instrução de resolução

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_8.md
```

O relatório deve conter:

- docs completadas;
- READMEs revisados;
- escopo negativo criado;
- erros de UI revisados;
- resultado do teste end-to-end;
- checkpoints marcados;
- pendências finais.

## Regra final

Não adicionar nova funcionalidade nesta fase. Apenas documentação, polimento e validação.
