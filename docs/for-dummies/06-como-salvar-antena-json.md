# Como salvar uma antena em JSON

## O que é uma AntennaSpec?

JSON que descreve uma antena: tipo, frequência, geometria, resultados de simulação e campos físicos opcionais. Salvo em `backend/data/antenna_specs/{id}.json`.

## Campos obrigatórios

Três campos são obrigatórios:

| Campo | O que colocar |
|---|---|
| `name` | Nome que você vai ver na biblioteca |
| `type` | `dipolo`, `monopolo`, `helicoidal`, `parabolica`, `pcb_compact` ou `commercial_omni_6dbi` |
| `frequency_hz` | Frequência em Hz (ex: `915000000` para 915 MHz) |

## Campos físicos (opcionais, schema v2.0)

Adicionados na Fase 2 das melhorias. Todos opcionais — JSONs antigos sem esses campos continuam funcionando.

| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `gmax_dbi` | `float` | `6.0` | Ganho máximo nominal (dBi) |
| `hpbw_deg` | `float > 0` | `35.0` | Half-power beamwidth (°) |
| `polarization` | `string` | `"linear vertical"` | Polarização: `"linear vertical"`, `"linear horizontal"`, `"linear"`, `"circular/elliptical"`, `"feed-dependent"` |
| `is_directional` | `bool` | `false` | Se antena é direcional |
| `pattern_model` | `string` | `"omni_colinear"` | Modelo de padrão: `"dipole"`, `"monopole"`, `"helical"`, `"parabolic"`, `"pcb"`, `"omni_colinear"` |
| `practicality_score` | `float 0–10` | `9.0` | Score de praticidade de instalação |
| `multi_direction_score` | `float 0–10` | `8.0` | Score multi-direção (gateway) |
| `notes` | `string` | `""` | Observações livres |

Presença de qualquer campo físico eleva `schema_version` para `"2.0"` automaticamente.

### Valores preset por tipo

| Tipo | gmax_dbi | hpbw_deg | polarização | direcional | praticidade | multi-dir |
|---|---:|---:|---|---|---:|---:|
| `dipolo` | 2.15 | 78 | linear vertical | não | 8 | 9 |
| `monopolo` | 5.15 | 55 | linear vertical | não | 7 | 8 |
| `helicoidal` | 11 | 55 | circular/elliptical | sim | 5 | 3 |
| `parabolica` | 20 | 18 | feed-dependent | sim | 2 | 1 |
| `pcb_compact` | 1 | 120 | linear | não | 10 | 7 |
| `commercial_omni_6dbi` | 6 | 35 | linear vertical | não | 9 | 8 |

O sistema preenche campos ausentes em runtime a partir desses presets — não é necessário incluí-los no JSON.

## Exemplo mínimo

```json
{
  "name": "Meu Dipolo",
  "type": "dipolo",
  "frequency_hz": 915000000
}
```

## Exemplo com campos físicos explícitos

```json
{
  "name": "Omni Gateway",
  "type": "commercial_omni_6dbi",
  "frequency_hz": 915000000,
  "hpbw_deg": 35.0,
  "polarization": "linear vertical",
  "is_directional": false,
  "practicality_score": 9.0,
  "multi_direction_score": 8.0
}
```

O campo `schema_version` será automaticamente `"2.0"` ao salvar.

## Como importar pela interface

1. Abra `http://localhost:8000/library.html`
2. Clique **Importar JSON**
3. Selecione o arquivo `.json`
4. Se o JSON for inválido → mensagem de erro aparece em vermelho
5. Se válido → antena aparece na lista

## Como exportar

1. Clique **Export** na linha da antena
2. Arquivo `.json` baixa com todos os campos, incluindo `results` e campos físicos

## Como salvar via sandbox

1. Abra `http://localhost:8000/sandbox.html`
2. Selecione o tipo — os campos físicos são preenchidos automaticamente
3. Ajuste parâmetros e clique **⚡ Rápido** ou **▶ Padrão (MoM)**
4. Clique **💾 Salvar** — campos físicos são incluídos no JSON salvo

## Como salvar via API

```bash
curl -X POST http://localhost:8000/api/v1/antennas \
  -H "Content-Type: application/json" \
  -d '{"name":"Dipolo","type":"dipolo","frequency_hz":915000000}'
```

Resposta: `201 Created` + spec completa com `id` gerado.

```bash
# Com campos físicos explícitos
curl -X POST http://localhost:8000/api/v1/antennas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Omni 6dBi",
    "type": "commercial_omni_6dbi",
    "frequency_hz": 915000000,
    "hpbw_deg": 35.0,
    "polarization": "linear vertical"
  }'
```

## Erros comuns

| Erro | Causa | Solução |
|---|---|---|
| `422 Unprocessable Entity` | Campo obrigatório ausente ou tipo errado | Verificar `name`, `type`, `frequency_hz` |
| `422` com `hpbw_deg` | `hpbw_deg <= 0` | Usar valor positivo (ex: `35.0`) |
| `422` com `practicality_score` | Score fora de 0–10 | Usar valor entre `0` e `10` |
| JSON inválido | Sintaxe quebrada (vírgula extra, aspas faltando) | Validar em [jsonlint.com](https://jsonlint.com) |
| `404 Not Found` no GET | `id` não existe | Listar todas: `GET /api/v1/antennas` |
