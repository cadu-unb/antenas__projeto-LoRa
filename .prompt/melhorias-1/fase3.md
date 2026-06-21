# Fase 3 — Motor Físico

**Objetivo:** implementar a física que está ausente ou incorreta no cálculo de link budget — ganho direcional real G(θ,φ), conversão ENU, orientação de antena, perdas adicionais e integração dos modelos de propagação ao link planner.

**Dependências:** Fase 2 concluída (NodeSpec com campos de perdas e orientação; solvers com `pattern_g()`).
**Arquivos afetados:** `backend/app/domain/link_budget.py`, `backend/app/domain/geometry.py` (novo), `backend/app/solvers/` (todos), `backend/app/api/link_routes.py`

---

## Etapa 1 — Conversão Geodésica para ENU (Gap 13)

**Objetivo:** criar módulo de geometria 3D que converte lat/lon/alt para coordenadas locais East-North-Up em metros. Pré-requisito para calcular azimute e elevação reais entre dois pontos com altitude.

### 1.1 — Criar `backend/app/domain/geometry.py`

```python
import math
from dataclasses import dataclass

# Parâmetros WGS-84
_a = 6378137.0          # semi-eixo maior (m)
_f = 1 / 298.257223563  # achatamento
_b = _a * (1 - _f)      # semi-eixo menor (m)
_e2 = 1 - (_b / _a) ** 2  # excentricidade ao quadrado

@dataclass
class ENUVector:
    east_m: float
    north_m: float
    up_m: float

    @property
    def distance_2d(self) -> float:
        return math.sqrt(self.east_m**2 + self.north_m**2)

    @property
    def distance_3d(self) -> float:
        return math.sqrt(self.east_m**2 + self.north_m**2 + self.up_m**2)

    @property
    def azimuth_deg(self) -> float:
        """Azimute (0=Norte, sentido horário), graus."""
        return math.degrees(math.atan2(self.east_m, self.north_m)) % 360

    @property
    def elevation_deg(self) -> float:
        """Ângulo de elevação acima do horizonte, graus."""
        return math.degrees(math.atan2(self.up_m, self.distance_2d))


def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> tuple[float, float, float]:
    """Converte lat/lon/alt (graus/metros) para ECEF (X, Y, Z em metros)."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    N = _a / math.sqrt(1 - _e2 * math.sin(lat) ** 2)
    x = (N + alt_m) * math.cos(lat) * math.cos(lon)
    y = (N + alt_m) * math.cos(lat) * math.sin(lon)
    z = (N * (1 - _e2) + alt_m) * math.sin(lat)
    return x, y, z


def geodetic_to_enu(
    lat_ref: float, lon_ref: float, alt_ref: float,
    lat_tgt: float, lon_tgt: float, alt_tgt: float,
) -> ENUVector:
    """
    Calcula o vetor ENU do ponto de referência até o ponto alvo.
    Todas as altitudes em metros acima do elipsoide (ou MSL aproximado).
    """
    x_r, y_r, z_r = geodetic_to_ecef(lat_ref, lon_ref, alt_ref)
    x_t, y_t, z_t = geodetic_to_ecef(lat_tgt, lon_tgt, alt_tgt)

    dx, dy, dz = x_t - x_r, y_t - y_r, z_t - z_r

    lat = math.radians(lat_ref)
    lon = math.radians(lon_ref)

    east  = -math.sin(lon) * dx + math.cos(lon) * dy
    north = (-math.sin(lat) * math.cos(lon) * dx
             - math.sin(lat) * math.sin(lon) * dy
             + math.cos(lat) * dz)
    up    = (math.cos(lat) * math.cos(lon) * dx
             + math.cos(lat) * math.sin(lon) * dy
             + math.sin(lat) * dz)

    return ENUVector(east, north, up)
```

### 1.2 — Atualizar `link_budget.py` para usar distância 3D (Gap 7)

Em `backend/app/domain/link_budget.py`, importar e usar `geodetic_to_enu`:

```python
from backend.app.domain.geometry import geodetic_to_enu

def fspl_db(dist_m: float, freq_hz: float) -> float:
    """Free Space Path Loss em dB."""
    c = 3e8
    return 20 * math.log10(4 * math.pi * dist_m * freq_hz / c)

def compute_link(node_a, node_b, freq_hz, antenna_a=None, antenna_b=None):
    # Altitude acima do solo = height_m; altitude absoluta não disponível sem DEM.
    # Usar height_m como aproximação de diferença de altura entre nós.
    enu = geodetic_to_enu(
        node_a.lat, node_a.lon, node_a.height_m,
        node_b.lat, node_b.lon, node_b.height_m,
    )
    dist_m = enu.distance_3d   # antes: haversine 2D
    azimuth_a_to_b = enu.azimuth_deg
    elevation_a_to_b = enu.elevation_deg
    # ... rest do cálculo (ver Etapa 3)
```

> **Nota:** `height_m` é altura acima do solo, não altitude ASL. Para o campus UnB (altitude ASL ~1020–1047 m), o erro de usar `height_m` como altitude relativa é pequeno para distâncias >1 km. A altitude absoluta só seria necessária com DEM integrado (fora do escopo desta fase).

### 1.3 — Testes de geometria

Criar `tests/test_geometry.py`:

```python
from backend.app.domain.geometry import geodetic_to_enu

def test_enu_distance_matches_haversine_approximately():
    """Para distâncias curtas, ENU 2D ≈ Haversine."""
    enu = geodetic_to_enu(-15.78, -47.93, 0, -15.83, -48.05, 0)
    dist_2d_km = enu.distance_2d / 1000
    assert 12 < dist_2d_km < 15  # ~13 km

def test_enu_azimuth_roughly_west():
    """Ponto a oeste deve ter azimute ~270°."""
    enu = geodetic_to_enu(-15.78, -47.93, 0, -15.78, -48.20, 0)
    assert 250 < enu.azimuth_deg < 290

def test_enu_elevation_positive_for_higher_target():
    enu = geodetic_to_enu(-15.78, -47.93, 10, -15.79, -47.94, 100)
    assert enu.elevation_deg > 0
```

---

## Etapa 2 — Ganho Direcional G(θ,φ) por Tipo de Antena (Gap 1)

**Objetivo:** cada solver deve expor `pattern_g(theta_deg, phi_deg, freq_hz)` retornando ganho em dBi para aquele ângulo. O link budget usará esse valor em vez de `gain_dbi()` (G_max) quando a orientação do nó estiver definida.

### 2.1 — Padronizar `pattern_g` na classe base

Em `backend/app/solvers/base_solver.py`, adicionar método abstrato:

```python
class BaseSolver:
    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        raise NotImplementedError

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """
        Ganho em dBi para ângulos theta (elevação) e phi (azimute) em graus.
        Implementação padrão: retorna gain_dbi() (isotrope angular — G_max sempre).
        Sobrescrever em solvers de antenas diretivas.
        """
        return self.gain_dbi(freq_hz, **kwargs)
```

### 2.2 — Implementar `pattern_g` no solver helicoidal

Em `backend/app/solvers/mom_solver.py` ou arquivo dedicado do solver helicoidal:

```python
import math

def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
    """
    Padrão helicoidal modo axial (endfire).
    theta=0: boresight (eixo da hélice), ganho máximo.
    theta=90: broadside, ganho mínimo.
    Modelo: G(θ) ≈ G_max + 10·log10(cos²(θ)) para |θ| < 90°.
    """
    g_max = self.gain_dbi(freq_hz, **kwargs)
    theta_rad = math.radians(abs(theta_deg))
    if theta_rad >= math.pi / 2:
        return g_max - 20  # fora do feixe principal: -20 dB aprox.
    g_linear = (10 ** (g_max / 10)) * (math.cos(theta_rad) ** 2)
    return 10 * math.log10(max(g_linear, 1e-10))
```

### 2.3 — Implementar `pattern_g` no solver parabólico

Em `backend/app/solvers/aperture_solver.py`:

```python
import math

def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
    """
    Padrão parabólico — feixe estreito (pencil beam).
    HPBW ≈ 70λ/D graus.
    Modelo gaussiano: G(θ) ≈ G_max - 12·(θ/HPBW)².
    """
    g_max = self.gain_dbi(freq_hz, **kwargs)
    diameter_m = kwargs.get("diameter_m", 0.3)
    wavelength = 3e8 / freq_hz
    hpbw_deg = 70 * wavelength / diameter_m
    attenuation_db = 12 * (theta_deg / hpbw_deg) ** 2
    return g_max - attenuation_db
```

### 2.4 — Dipolo e Monopolo

Para dipolo e monopolo, `pattern_g` é o padrão toroidal (donuts shape):
- phi não afeta (omni em azimute)
- theta=90° (horizontal) = G_max; theta=0° ou 180° (eixo) = ganho mínimo

```python
# Em dipole_solver.py / monopole_solver.py
def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
    g_max = self.gain_dbi(freq_hz, **kwargs)
    theta_rad = math.radians(theta_deg)
    sin_theta = math.sin(theta_rad)
    if sin_theta <= 0:
        return g_max - 40
    g_linear = (10 ** (g_max / 10)) * (sin_theta ** 2)
    return 10 * math.log10(max(g_linear, 1e-10))
```

---

## Etapa 3 — Integrar G(θ,φ) e Perdas Adicionais no Link Budget (Gaps 1, 4, 11)

**Objetivo:** `compute_link()` agora usa ganho direcional real (se orientação definida) e soma as perdas extras do `NodeSpec`.

### 3.1 — Refatorar `compute_link` em `link_budget.py`

```python
from backend.app.domain.geometry import geodetic_to_enu
from backend.app.solvers import get_solver  # função que retorna solver pelo antenna_type

def _effective_gain(node, antenna, enu_to_peer: ENUVector) -> float:
    """
    Retorna ganho efetivo em dBi.
    Se node.azimuth_deg definido: calcula ângulo off-boresight e chama pattern_g().
    Caso contrário: retorna G_max.
    """
    if antenna is None:
        return 0.0

    solver = get_solver(antenna.antenna_type)
    g_max = solver.gain_dbi(antenna.frequency_hz or 915e6)

    if node.azimuth_deg is None:
        # Sem orientação definida: usar G_max (comportamento atual)
        return g_max

    # Calcular ângulo entre boresight da antena e direção do enlace
    boresight_az = node.azimuth_deg   # azimute do boresight
    boresight_el = node.tilt_deg      # elevação do boresight

    link_az = enu_to_peer.azimuth_deg
    link_el = enu_to_peer.elevation_deg

    # Ângulo off-boresight em azimute e elevação
    delta_az = abs(link_az - boresight_az) % 360
    if delta_az > 180:
        delta_az = 360 - delta_az
    delta_el = abs(link_el - boresight_el)

    # theta = ângulo total off-boresight (simplificado: soma quadrática)
    theta_off = math.sqrt(delta_az**2 + delta_el**2)

    return solver.pattern_g(theta_off, 0.0, antenna.frequency_hz or 915e6)


def compute_link(node_a, node_b, freq_hz, antenna_a=None, antenna_b=None):
    enu = geodetic_to_enu(
        node_a.lat, node_a.lon, node_a.height_m,
        node_b.lat, node_b.lon, node_b.height_m,
    )
    dist_m = enu.distance_3d
    azimuth_a_to_b = enu.azimuth_deg
    elevation_a_to_b = enu.elevation_deg

    # Vetor inverso para ganho de RX
    enu_b_to_a = ENUVector(-enu.east_m, -enu.north_m, -enu.up_m)

    # Ganhos diretivos
    g_tx = _effective_gain(node_a, antenna_a, enu)
    g_rx = _effective_gain(node_b, antenna_b, enu_b_to_a)

    # Perdas
    path_loss = fspl_db(dist_m, freq_hz)
    l_tx = node_a.cable_loss_db
    l_rx = node_b.cable_loss_db

    # Novas perdas adicionais (Fase 2, Gap 4 e 11)
    extra = (
        getattr(node_a, "extra_loss_db", 0.0)
        + getattr(node_b, "extra_loss_db", 0.0)
        + getattr(node_a, "polarization_loss_db", 0.0)
        + getattr(node_a, "fading_margin_db", 0.0)
    )

    rx_power_dbm = node_a.tx_power_dbm + g_tx - l_tx - path_loss - l_rx + g_rx - extra
    margin = rx_power_dbm - node_b.rx_sensitivity_dbm

    warnings = []
    if dist_m > 200_000:
        warnings.append(f"Distância {dist_m/1000:.0f} km excede escopo prático de LoRa (200 km).")

    return LinkResult(
        tx_power_dbm=node_a.tx_power_dbm,
        tx_gain_dbi=g_tx,
        tx_cable_db=l_tx,
        path_loss_db=path_loss,
        rx_cable_db=l_rx,
        rx_gain_dbi=g_rx,
        extra_loss_db=extra,
        rx_power_dbm=rx_power_dbm,
        rx_sensitivity_dbm=node_b.rx_sensitivity_dbm,
        link_margin_db=margin,
        distance_m=dist_m,
        azimuth_deg=azimuth_a_to_b,
        elevation_deg=elevation_a_to_b,
        warnings=warnings,
    )
```

### 3.2 — Atualizar `LinkResult` para incluir novos campos

Em `backend/app/schemas/link_scenario.py`:

```python
class LinkResult(BaseModel):
    # existentes:
    tx_power_dbm: float
    tx_gain_dbi: float
    tx_cable_db: float
    path_loss_db: float
    rx_cable_db: float
    rx_gain_dbi: float
    rx_power_dbm: float
    rx_sensitivity_dbm: float
    link_margin_db: float
    distance_m: float
    azimuth_deg: float
    elevation_deg: float
    # novos:
    extra_loss_db: float = 0.0
    warnings: list[str] = []
```

### 3.3 — Testes do link budget atualizado

Adicionar ao `tests/test_link_budget.py` (ou criar novo arquivo):

```python
def test_directional_gain_penalizes_misalignment():
    """Helicoidal apontada para W perde ganho em enlace para N."""
    node_a = NodeSpec(lat=-15.78, lon=-47.93, height_m=5,
                      azimuth_deg=270, tilt_deg=0,  # boresight para Oeste
                      tx_power_dbm=20, rx_sensitivity_dbm=-137)
    node_b = NodeSpec(lat=-15.68, lon=-47.93, height_m=5,  # Norte de A
                      tx_power_dbm=20, rx_sensitivity_dbm=-137)
    antenna_a = AntennaSpec(antenna_type="helicoidal", ...)
    result_misaligned = compute_link(node_a, node_b, 915e6, antenna_a=antenna_a)

    node_a_aligned = node_a.model_copy(update={"azimuth_deg": 0})  # boresight para Norte
    result_aligned = compute_link(node_a_aligned, node_b, 915e6, antenna_a=antenna_a)

    assert result_aligned.link_margin_db > result_misaligned.link_margin_db

def test_extra_loss_reduces_margin():
    node_a = NodeSpec(lat=-15.78, lon=-47.93, height_m=5,
                      tx_power_dbm=20, rx_sensitivity_dbm=-137, extra_loss_db=0)
    node_b = NodeSpec(lat=-15.83, lon=-48.05, height_m=5,
                      tx_power_dbm=20, rx_sensitivity_dbm=-137)
    result_no_loss = compute_link(node_a, node_b, 915e6)

    node_a_loss = node_a.model_copy(update={"extra_loss_db": 10.0})
    result_with_loss = compute_link(node_a_loss, node_b, 915e6)

    assert result_no_loss.link_margin_db - result_with_loss.link_margin_db == pytest.approx(10.0)

def test_3d_distance_gt_2d_when_altitude_differs():
    """Distância 3D > 2D quando há diferença de altitude."""
    node_a = NodeSpec(lat=-15.78, lon=-47.93, height_m=5)
    node_b = NodeSpec(lat=-15.83, lon=-48.05, height_m=1000)
    result = compute_link(node_a, node_b, 915e6)
    from backend.app.domain.link_budget import haversine
    dist_2d = haversine(node_a.lat, node_a.lon, node_b.lat, node_b.lon)
    assert result.distance_m > dist_2d
```

---

## Etapa 4 — Integrar Okumura-Hata e Longley-Rice ao Link Planner (Gap 17)

**Objetivo:** permitir que o link budget use um modelo de propagação diferente de FSPL, selecionável via query param ou campo no cenário.

### 4.1 — Adicionar campo `propagation_model` ao `LinkScenario`

Em `backend/app/schemas/link_scenario.py`:

```python
from typing import Literal

class LinkScenario(BaseModel):
    # ...campos existentes...
    propagation_model: Literal["fspl", "okumura_hata", "longley_rice"] = "fspl"
```

### 4.2 — Criar função de dispatch em `link_budget.py`

```python
from backend.app.solvers.okumura_hata import okumura_hata_loss
from backend.app.solvers.longley_rice import longley_rice_loss

def path_loss_db(dist_m: float, freq_hz: float, model: str = "fspl",
                 tx_height_m: float = 5, rx_height_m: float = 5,
                 environment: str = "suburban") -> float:
    if model == "okumura_hata":
        return okumura_hata_loss(dist_m, freq_hz, tx_height_m, rx_height_m, environment)
    elif model == "longley_rice":
        return longley_rice_loss(dist_m, freq_hz, tx_height_m, rx_height_m)
    else:
        return fspl_db(dist_m, freq_hz)
```

### 4.3 — Usar `propagation_model` no endpoint de cálculo

Em `link_routes.py`, no handler de `POST /{id}/calculate`:

```python
@router.post("/{scenario_id}/calculate", response_model=LinkResult)
async def calculate_link(scenario_id: str):
    scenario = scenario_storage.get(scenario_id)
    result = compute_link(
        scenario.node_a, scenario.node_b,
        scenario.frequency_hz,
        propagation_model=scenario.propagation_model,  # novo parâmetro
        antenna_a=..., antenna_b=...
    )
    # salvar resultado no cenário
    scenario.results = result
    scenario_storage.save(scenario)
    return result
```

### 4.4 — Testes de integração de modelos de propagação

```python
def test_okumura_hata_gives_higher_loss_than_fspl():
    """Okumura-Hata inclui perdas urbanas — sempre > FSPL puro."""
    dist_m = 5000
    freq_hz = 915e6
    fspl = path_loss_db(dist_m, freq_hz, model="fspl")
    oh   = path_loss_db(dist_m, freq_hz, model="okumura_hata",
                        tx_height_m=30, rx_height_m=1.5)
    assert oh > fspl
```

---

## Critério de Conclusão da Fase 3

- [ ] `uv run pytest tests/ -v` — zero falhas
- [ ] `geodetic_to_enu(-15.78, -47.93, 0, -15.83, -48.05, 0).distance_2d` retorna ~13 km (verificar manualmente)
- [ ] Helicoidal com `azimuth_deg=270` em enlace Norte→Norte tem margem menor que com `azimuth_deg=0`
- [ ] `extra_loss_db=10` reduz margem em exatamente 10 dB
- [ ] `GET /api/v1/scenarios/{id}/calculate` com `propagation_model="okumura_hata"` retorna `path_loss_db` diferente de FSPL
- [ ] `LinkResult` contém campo `warnings` no JSON de resposta
