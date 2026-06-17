# Como usar a Biblioteca

A Biblioteca armazena todas as antenas que você salvou do Sandbox. Acesse em `/library.html`.

## Listar antenas

A página carrega automaticamente todas as antenas salvas. Cada cartão mostra:
- Nome
- Tipo (dipolo, monopolo, helicoidal, parabólica)
- Frequência de operação
- Ganho calculado (dBi)
- Modo de solver usado

## Importar antena (JSON)

1. Clicar **Importar JSON**
2. Selecionar arquivo `.json` válido (formato `AntennaSpec`)
3. A antena aparece na lista imediatamente

Formato mínimo de arquivo válido:
```json
{
  "name": "Dipolo 915 MHz",
  "type": "dipolo",
  "frequency_hz": 915000000,
  "units": "SI"
}
```

Arquivo inválido → mensagem de erro com campo problemático.

## Exportar antena

1. Clicar **Exportar** no cartão da antena
2. Download automático do `.json` com spec completa + resultados

O arquivo exportado contém `results` preenchidos se a antena foi simulada antes de salvar.

## Deletar antena

1. Clicar **Deletar** no cartão
2. Confirmar no diálogo
3. Arquivo removido do disco (`backend/data/antenna_specs/{id}.json`)

Deleção é permanente. Faça export antes se quiser backup.

## Reutilizar no Link Planner

1. Abrir Link Planner (`/link-planner.html`)
2. Em cada nó, clicar no dropdown de antena
3. Selecionar antena da biblioteca pelo nome

## API direta (opcional)

```bash
# listar todas
curl http://localhost:8000/api/v1/antennas

# detalhe de uma antena
curl http://localhost:8000/api/v1/antennas/{id}

# importar via API
curl -X POST http://localhost:8000/api/v1/antennas \
  -H "Content-Type: application/json" \
  -d @minha-antena.json

# deletar
curl -X DELETE http://localhost:8000/api/v1/antennas/{id}
```

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| `422 Unprocessable Entity` | JSON inválido ou campo obrigatório ausente | Verificar campos `name`, `type`, `frequency_hz`, `units` |
| `404 Not Found` | ID inexistente | Atualizar lista da biblioteca |
| Antena sem `results` | Salva antes de simular | Abrir no Sandbox, simular, salvar novamente |
