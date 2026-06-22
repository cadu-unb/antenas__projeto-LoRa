# AntennaSpec — Schema e Exemplos

Schema central de antenas. Salvo em `backend/data/antenna_specs/{id}.json`.

## Campos

### Campos base (v1.0)

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `schema_version` | string | não | `"1.0"` (default) ou `"2.0"` (auto quando campos físicos presentes) |
| `id` | string (UUID) | não | Gerado automaticamente se omitido |
| `name` | string | **sim** | Nome legível da antena |
| `type` | string | **sim** | `dipolo`, `monopolo`, `helicoidal`, `parabolica`, `pcb_compact`, `commercial_omni_6dbi` |
| `frequency_hz` | float | **sim** | Frequência central em Hz |
| `units` | dict | não | Unidades dos campos numéricos |
| `geometry` | dict | não | Parâmetros geométricos específicos por tipo |
| `material` | dict | não | Material condutor e constantes |
| `solver` | string | não | `rapido` (default), `padrao`, `preciso`, `experimental` |
| `results` | dict \| null | não | Resultados de simulação (preenchido pelo solver) |
| `metadata` | dict | não | Notas, tags, timestamps livres |

### Campos físicos opcionais (v2.0)

Campos alinhados com a referência MATLAB externa. Todos opcionais — specs antigas sem esses campos continuam válidas.

| Campo | Tipo | Validação | Descrição |
|---|---|---|---|
| `gmax_dbi` | float \| null | numérico | Ganho máximo nominal (boresight) em dBi |
| `hpbw_deg` | float \| null | > 0 | Half-Power Beamwidth em graus |
| `polarization` | string \| null | — | Ex: `"linear vertical"`, `"circular/elliptical"`, `"linear"` |
| `is_directional` | bool \| null | — | `true` para antenas com boresight definido |
| `pattern_model` | string \| null | — | Identificador do modelo angular: `dipole`, `monopole`, `helical`, `parabolic`, `pcb`, `omni_colinear` |
| `practicality_score` | float \| null | 0–10 | Facilidade de instalação/uso (referência MATLAB) |
| `multi_direction_score` | float \| null | 0–10 | Adequação para cobertura multi-azimute |
| `notes` | string | — | Observações livres (default `""`) |

**Regra de versionamento:** se ao menos um campo físico for preenchido, `schema_version` é automaticamente promovido para `"2.0"`. Specs antigas sem campos físicos mantêm `"1.0"` e não são regravadas em disco pela leitura.

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

---

## Exemplo — PCB Compact 915 MHz

```json
{
  "schema_version": "1.0",
  "name": "PCB Compact 915 MHz",
  "type": "pcb_compact",
  "frequency_hz": 915000000.0,
  "solver": "rapido",
  "results": {
    "gain_dbi": 1.5,
    "impedance_ohm": 50.0,
    "efficiency_pct": 85.0,
    "radiation_pattern": "quasi-omni"
  }
}
```

Nota: `pcb_compact` não exige campos em `geometry`. O solver calcula ganho por faixa de frequência automaticamente.

---

## Exemplo — Commercial Omni 6dBi com campos físicos (v2.0)

```json
{
  "schema_version": "2.0",
  "name": "Omni Colinear 6dBi 915 MHz",
  "type": "commercial_omni_6dbi",
  "frequency_hz": 915000000.0,
  "solver": "rapido",
  "gmax_dbi": 6.0,
  "hpbw_deg": 35.0,
  "polarization": "linear vertical",
  "is_directional": false,
  "pattern_model": "omni_colinear",
  "practicality_score": 9.0,
  "multi_direction_score": 8.0,
  "notes": "Kit E220-900T22D reference antenna",
  "results": {
    "gain_dbi": 6.0,
    "impedance_ohm": 50.0,
    "efficiency_pct": 95.0,
    "radiation_pattern": "omnidirecional colinear"
  }
}
```

Nota: `commercial_omni_6dbi` não exige campos em `geometry`. `schema_version` promovido para `"2.0"` automaticamente pela presença dos campos físicos.

---

## Equivalência Python ↔ MATLAB externo

| Tipo Python | Equivalente MATLAB | Ganho nominal | Direcional? |
|---|---|---:|---|
| `dipolo` | `Dipole_HalfWave` | 2.15 dBi | não |
| `monopolo` | `Monopole_GroundPlane` | 5.15 dBi | não |
| `helicoidal` | `Helical_Axial` | ~11 dBi | sim (axial) |
| `parabolica` | `Parabolic_Dish` | ~20 dBi | sim |
| `pcb_compact` | `PCB_Compact` | 1–2 dBi | não |
| `commercial_omni_6dbi` | `Commercial_Omni_6dBi` | 6 dBi | não |

---

## Campos de antena vs. campos de nó/enlace

`AntennaSpec` guarda as propriedades físicas da antena: tipo, geometria, resultados calculados.

Os parâmetros que afetam o cálculo de enlace por nó ficam em `NodeSpec`:

| Campo `NodeSpec` | Efeito |
|---|---|
| `antenna_id` | Referencia uma `AntennaSpec` salva |
| `azimuth_deg` | Quando preenchido, ativa ganho direcional via `pattern_g()` |
| `tilt_deg` | Elevação/tilt do boresight |
| `cable_loss_db` | Perda de cabo/conector |
| `extra_loss_db` | Perda adicional arbitrária |
| `fading_margin_db` | Margem de fading tratada como perda |
| `polarization_loss_db` | Perda de polarização |

O sistema usa coordenadas ENU 3D para cálculo de geometria de enlace (azimute e elevação reais). Quando `azimuth_deg` é definido em `NodeSpec`, o solver aplica o padrão angular da antena via `pattern_g()` para antenas direcionais.

O campo `geometry` de `AntennaSpec` continua livre (dict sem schema fixo). Versões futuras do schema adicionarão campos físicos opcionais no topo de `AntennaSpec` (`gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional`, `pattern_model`, `practicality_score`, `multi_direction_score`) sem quebrar specs antigas.

---

## Notas

- `results: null` — antena não simulada ainda; apenas spec geométrica salva.
- `solver: "rapido"` — analítico, sem PyNEC. Preciso para referência; não validado em campo.
- `geometry` e `material` são dicts livres — estrutura varia por tipo de antena.
