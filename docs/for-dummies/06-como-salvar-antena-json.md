# Como salvar uma antena em JSON

## O que é uma AntennaSpec?

JSON que descreve uma antena: tipo, frequência, geometria, resultados de simulação. Salvo em `backend/data/antenna_specs/{id}.json`.

## Campos obrigatórios

Só dois campos são obrigatórios:

| Campo | O que colocar |
|---|---|
| `name` | Nome que você vai ver na biblioteca |
| `type` | `dipolo`, `monopolo`, `helicoidal`, `parabolica`, `pcb_compact` ou `commercial_omni_6dbi` |
| `frequency_hz` | Frequência em Hz (ex: `915000000` para 915 MHz) |

## Exemplo mínimo

```json
{
  "name": "Meu Dipolo",
  "type": "dipolo",
  "frequency_hz": 915000000
}
```

Salve como `.json`, importe pela biblioteca. O sistema gera o `id` automaticamente.

## Exemplo completo

Ver `docs/antenna-spec-schema.md` para exemplos com todos os campos.

## Como importar pela interface

1. Abra `http://localhost:8000/library.html`
2. Clique **Importar JSON**
3. Selecione o arquivo `.json`
4. Se o JSON for inválido → mensagem de erro aparece em vermelho
5. Se válido → antena aparece na lista

## Como exportar

1. Clique **Export** na linha da antena
2. Arquivo `.json` baixa com todos os campos, incluindo `results`

## Como salvar via API

```bash
curl -X POST http://localhost:8000/api/v1/antennas \
  -H "Content-Type: application/json" \
  -d '{"name":"Dipolo","type":"dipolo","frequency_hz":915000000}'
```

Resposta: `201 Created` + spec completa com `id` gerado.

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| `422 Unprocessable Entity` | Campo obrigatório ausente ou tipo errado | Verificar `name`, `type`, `frequency_hz` |
| JSON inválido | Sintaxe quebrada (vírgula extra, aspas faltando) | Validar em [jsonlint.com](https://jsonlint.com) |
| `404 Not Found` no GET | `id` não existe | Listar todas: `GET /api/v1/antennas` |
