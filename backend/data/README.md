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
