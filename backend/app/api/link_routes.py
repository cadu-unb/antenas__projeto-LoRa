from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from ..domain import link_budget as lb
from ..domain.kml.parser import parse_kml
from ..schemas.link_scenario import (
    HopResult,
    KmlImportResult,
    LinkEdge,
    LinkResult,
    LinkScenario,
    TopologyResult,
)
from ..schemas.node_spec import NodeSpec
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


class LinkEdgeIn(BaseModel):
    id: str | None = None
    node_a_id: str
    node_b_id: str


@router.post("/{id}/links", response_model=LinkScenario)
def add_link(id: str, body: LinkEdgeIn) -> LinkScenario:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    edge = LinkEdge(
        **({"id": body.id} if body.id else {}),
        node_a_id=body.node_a_id,
        node_b_id=body.node_b_id,
    )
    updated = s.model_copy(update={"links": s.links + [edge]})
    scenario_storage.save(updated)
    return updated


@router.delete("/{id}/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_link(id: str, link_id: str) -> None:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    new_links = [e for e in s.links if e.id != link_id]
    if len(new_links) == len(s.links):
        raise HTTPException(status_code=404, detail="Enlace não encontrado")
    scenario_storage.save(s.model_copy(update={"links": new_links}))


@router.post("/{id}/calculate_links", response_model=TopologyResult)
def calculate_links(id: str) -> TopologyResult:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    all_nodes = [s.node_a, s.node_b] + s.extra_nodes
    nodes_by_id = {n.id: n for n in all_nodes}

    islands = lb.find_islands(list(nodes_by_id.keys()), s.links)

    hops: list[HopResult] = []
    for edge in s.links:
        na = nodes_by_id.get(edge.node_a_id)
        nb = nodes_by_id.get(edge.node_b_id)
        if na is None or nb is None:
            continue
        d = lb.haversine(na.lat, na.lon, nb.lat, nb.lon)
        loss = lb.fspl_db(d, s.frequency_hz)
        gain_a = _antenna_gain(na.antenna_id)
        gain_b = _antenna_gain(nb.antenna_id)
        rx_p, margin = lb.compute_link(
            tx_power_dbm=na.tx_power_dbm,
            tx_gain_dbi=gain_a,
            tx_cable_db=na.cable_loss_db,
            path_loss_db=loss,
            rx_gain_dbi=gain_b,
            rx_cable_db=nb.cable_loss_db,
            rx_sensitivity_dbm=nb.rx_sensitivity_dbm,
        )
        hops.append(HopResult(
            edge_id=edge.id,
            node_a_id=na.id,
            node_b_id=nb.id,
            node_a_name=na.name,
            node_b_name=nb.name,
            distance_m=round(d, 1),
            fspl_db=round(loss, 2),
            rx_power_dbm=round(rx_p, 2),
            link_margin_db=round(margin, 2),
            feasibility=lb.feasibility(margin),
        ))

    bottleneck = min((h.link_margin_db for h in hops), default=0.0)
    result = TopologyResult(
        hops=hops,
        islands=islands,
        bottleneck_margin_db=round(bottleneck, 2),
        feasibility=lb.feasibility(bottleneck) if hops else "vermelho",
    )
    scenario_storage.save(s.model_copy(update={"topology_result": result}))
    return result


@router.post("/{id}/kml", response_model=KmlImportResult)
async def import_kml(id: str, file: UploadFile = File(...)) -> KmlImportResult:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    raw = await file.read()
    try:
        content = raw.decode("utf-8", errors="replace")
        parsed = parse_kml(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    new_nodes = [
        NodeSpec(
            name=p.name,
            lat=p.lat,
            lon=p.lon,
            height_m=p.altitude or 0.0,
        )
        for p in parsed.points
    ]
    poly_dicts = [p.model_dump() for p in parsed.polygons]

    updated = s.model_copy(update={
        "extra_nodes": s.extra_nodes + new_nodes,
        "polygons": s.polygons + poly_dicts,
    })
    scenario_storage.save(updated)

    return KmlImportResult(
        scenario_id=id,
        nodes_imported=len(new_nodes),
        polygons_imported=len(parsed.polygons),
        nodes=new_nodes,
        polygons=poly_dicts,
    )
