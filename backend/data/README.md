# backend/data/

Dados persistidos em disco. Gerado pelo sistema em runtime. **Não versionar conteúdo.**

## Subpastas

| Pasta | Conteúdo | Pode apagar? |
|---|---|---|
| `antenna_specs/` | Specs de antenas salvas (`{id}.json`) | Com cuidado — dados de usuário |
| `scenarios/` | Cenários criados na UI (`{id}.json`) | Com cuidado — dados de usuário |
| `simulations/` | Logs de jobs de simulação (`{job_id}/log.jsonl`) | Sim — descartável |
| `kml_uploads/` | Arquivos KML importados | Com cuidado — upload de usuário |
| `reports/` | Relatórios exportados | Sim — regenerável |

## Limpeza segura

Arquivos são criados pelo container Docker com dono `root`. Usar `sudo`:

```bash
# Logs de simulação — seguro apagar
sudo rm -rf backend/data/simulations/*

# Relatórios gerados — seguro apagar
sudo rm -rf backend/data/reports/*

# Cenários de usuário — apaga trabalho salvo
sudo rm -rf backend/data/scenarios/*

# Specs de antenas salvas — apaga configurações do usuário
sudo rm -rf backend/data/antenna_specs/*
```

> **Atenção:** `scenarios/` e `antenna_specs/` contêm dados criados pelo usuário na interface.
> Não há backup automático. Apague só se tiver certeza.

## Backfill de campos físicos

Antenas salvas antes da Fase 2 das melhorias (`schema_version: "1.0"`) não possuem os campos físicos opcionais (`hpbw_deg`, `polarization`, `gmax_dbi`, etc.). A aplicação preenche esses campos em runtime a partir de presets canônicos, **sem reescrever os arquivos em disco**.

Para persistir os presets nos arquivos antigos de forma explícita, use o script:

```bash
# Ver o que seria alterado (dry-run, nada é escrito)
python scripts/backfill_antenna_fields.py

# Aplicar as alterações
python scripts/backfill_antenna_fields.py --write

# Usar diretório alternativo
python scripts/backfill_antenna_fields.py --data-dir /caminho/outro/antenna_specs --write
```

### Comportamento do script

| Caso | O que acontece |
|---|---|
| Spec sem campos físicos (v1.0) | Preenche com presets do tipo; eleva `schema_version` para `"2.0"` |
| Spec com alguns campos físicos já definidos | Preenche apenas os campos `None`; preserva os existentes |
| Spec com todos os campos físicos definidos | Skip — nada alterado |
| Tipo sem preset (`patch_array`, etc.) | Skip com aviso |
| JSON inválido | Registra erro, continua |

O script **não sobrescreve** `geometry`, `results`, `metadata` nem parâmetros geométricos do usuário.

### Reversibilidade

As alterações são reversíveis via `git`:

```bash
git diff backend/data/antenna_specs/
git checkout -- backend/data/antenna_specs/
```

> **Nota:** `backend/data/` está no `.gitignore` por padrão. Para usar `git` como backup, remova ou ajuste a regra antes de rodar o script com `--write`.
