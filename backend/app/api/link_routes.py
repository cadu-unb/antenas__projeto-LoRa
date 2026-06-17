from fastapi import APIRouter, HTTPException, status

from ..domain import link_budget as lb
from ..schemas.link_scenario import LinkResult, LinkScenario
from ..storage import antenna_storage, scenario_storage

router = APIRouter(prefix="/api/v1/scenarios", tags=["link"])


def _antenna_gain(antenna_id: str | None) -> float:
    if not antenna_id:
        return 0.0
    ant = antenna_storage.load(antenna_id)
    if ant is None or ant.results is None:
        return 0.0
    return float(ant.results.get("gain_dbi", 0.0))


@router.post("", response_model=LinkScenario, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: LinkScenario) -> LinkScenario:
    scenario_storage.save(scenario)
    return scenario


@router.get("", response_model=list[LinkScenario])
def list_scenarios() -> list[LinkScenario]:
    return scenario_storage.list_all()


@router.get("/{id}", response_model=LinkScenario)
def get_scenario(id: str) -> LinkScenario:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    return s


@router.post("/{id}/calculate", response_model=LinkResult)
def calculate(id: str) -> LinkResult:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    d = lb.haversine(s.node_a.lat, s.node_a.lon, s.node_b.lat, s.node_b.lon)
    az = lb.bearing(s.node_a.lat, s.node_a.lon, s.node_b.lat, s.node_b.lon)
    el = lb.elevation_angle(d, s.node_a.height_m, s.node_b.height_m)
    loss = lb.fspl_db(d, s.frequency_hz)

    tx_gain = _antenna_gain(s.node_a.antenna_id)
    rx_gain = _antenna_gain(s.node_b.antenna_id)

    rx_power, margin = lb.compute_link(
        tx_power_dbm=s.node_a.tx_power_dbm,
        tx_gain_dbi=tx_gain,
        tx_cable_db=s.node_a.cable_loss_db,
        path_loss_db=loss,
        rx_gain_dbi=rx_gain,
        rx_cable_db=s.node_b.cable_loss_db,
        rx_sensitivity_dbm=s.node_b.rx_sensitivity_dbm,
    )

    result = LinkResult(
        distance_m=round(d, 1),
        azimuth_deg=round(az, 2),
        elevation_deg=round(el, 4),
        fspl_db=round(loss, 2),
        rx_power_dbm=round(rx_power, 2),
        link_margin_db=round(margin, 2),
        feasibility=lb.feasibility(margin),
    )

    scenario_storage.save(s.model_copy(update={"results": result}))
    return result
