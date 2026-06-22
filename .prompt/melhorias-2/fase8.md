# Prompt — Melhorias 2 — Fase 8

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 8 — Compatibilidade e Migração Leve**. Esta fase deve ser conservadora para evitar churn em dados salvos.

## Objetivo

Criar uma estratégia opcional de backfill para antenas salvas, sem regravar arquivos antigos automaticamente durante a execução normal da aplicação.

## Arquivos alvo

- `backend/app/storage/antenna_storage.py`
- Novo script opcional: `scripts/backfill_antenna_fields.py`
- `backend/data/README.md`
- Testes novos ou existentes em diretório temporário

## Passos

1. Leia o plano e confirme a regra: leitura normal não deve modificar arquivos.
2. Verifique como antenas são salvas e carregadas atualmente.
3. Garanta que `antenna_storage.py` não regrave specs antigas só por aplicar defaults em runtime.
4. Crie script opcional `scripts/backfill_antenna_fields.py`.
5. O script deve:
   - ler specs antigas;
   - aplicar presets por `type`;
   - preservar `metadata`, `results` e `geometry`;
   - não sobrescrever parâmetros geométricos definidos pelo usuário;
   - escrever somente com flag explícita, por exemplo `--write`;
   - ter modo dry-run por padrão.
6. Documente o uso do script em `backend/data/README.md`.
7. Teste com diretório temporário, não com dados reais sem necessidade.

## Critérios de aceite

- Rodar a aplicação não regrava arquivos antigos.
- Backfill é explícito.
- Dry-run mostra o que seria alterado.
- Com `--write`, o script atualiza apenas o necessário.
- Alterações são reversíveis via git.

## Validação

Execute teste em diretório temporário. Se houver teste automatizado, rode a parte correspondente da suíte.

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase8.md` descrevendo:

- comportamento normal de leitura;
- funcionamento do script de backfill;
- flags disponíveis;
- validação em diretório temporário;
- pendências ou riscos restantes.
