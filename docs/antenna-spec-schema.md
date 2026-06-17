# AntennaSpec — Schema e Exemplos

Schema central de antenas. Salvo em `backend/data/antenna_specs/{id}.json`.

## Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `schema_version` | string | não | Versão do schema (default `"1.0"`) |
| `id` | string (UUID) | não | Gerado automaticamente se omitido |
| `name` | string | **sim** | Nome legível da antena |
| `type` | string | **sim** | `dipolo`, `monopolo`, `helicoidal`, `parabolica` |
| `frequency_hz` | float | **sim** | Frequência central em Hz |
| `units` | dict | não | Unidades dos campos numéricos |
| `geometry` | dict | não | Parâmetros geométricos específicos por tipo |
| `material` | dict | não | Material condutor e constantes |
| `solver` | string | não | `rapido` (default), `padrao`, `preciso`, `experimental` |
| `results` | dict \| null | não | Resultados de simulação (preenchido pelo solver) |
| `metadata` | dict | não | Notas, tags, timestamps livres |

---

## Exemplo — Dipolo λ/2 em 915 MHz

```json
{
  "schema_version": "1.0",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Dipolo Meia Onda 915 MHz",
  "type": "dipolo",
  "frequency_hz": 915000000.0,
  "units": {
    "frequency": "Hz",
    "gain": "dBi",
    "impedance": "Ohm",
    "length": "m"
  },
  "geometry": {
    "length_m": 0.164,
    "diameter_mm": 1.5
  },
  "material": {
    "conductor": "cobre",
    "conductivity": 58000000.0
  },
  "solver": "rapido",
  "results": {
    "gain_dbi": 2.15,
    "impedance_ohm": 73.0,
    "swr": 1.02,
    "efficiency_pct": 98.5,
    "radiation_pattern": "omnidirecional"
  },
  "metadata": {
    "created_at": "2026-06-17T00:00:00Z",
    "notes": "Dipolo de referência para LoRa 915 MHz"
  }
}
```

---

## Exemplo — Parabólica 2.4 GHz

```json
{
  "schema_version": "1.0",
  "id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "name": "Parabólica Grade 2.4 GHz",
  "type": "parabolica",
  "frequency_hz": 2400000000.0,
  "units": {
    "frequency": "Hz",
    "gain": "dBi",
    "diameter": "m",
    "beamwidth": "graus"
  },
  "geometry": {
    "diameter_m": 0.6,
    "focal_length_m": 0.22,
    "f_d_ratio": 0.367
  },
  "material": {
    "reflector": "aluminio",
    "feed_type": "dipolo_focal"
  },
  "solver": "rapido",
  "results": {
    "gain_dbi": 18.5,
    "beamwidth_deg": 12.0,
    "efficiency_pct": 55.0,
    "sidelobe_level_db": -20.0
  },
  "metadata": {
    "created_at": "2026-06-17T00:00:00Z",
    "notes": "Parabólica para enlace ponto a ponto"
  }
}
```

---

## Notas

- `results: null` — antena não simulada ainda; apenas spec geométrica salva.
- `solver: "rapido"` — analítico, sem PyNEC. Preciso para referência; não validado em campo.
- `geometry` e `material` são dicts livres — estrutura varia por tipo de antena.
