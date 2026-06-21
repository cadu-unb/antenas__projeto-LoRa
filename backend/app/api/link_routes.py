from typing import Any, Literal

from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..domain import link_budget as lb
from ..domain.comparison import run_comparison
from ..domain.kml.parser import parse_kml
from ..schemas.link_scenario import (
    CandidateCoverageResult,
    CandidateSite,
    HopResult,
    KmlImportResult,
    LinkEdge,
    LinkResult,
    LinkScenario,
    NodeCoverageResult,
    SiteSelectionResult,
    TopologyResult,
)
from ..schemas.node_spec import NodeSpec
from ..storage import antenna_storage, lora_module_storage, scenario_storage

router = APIRouter(prefix="/api/v1/scenarios", tags=["link"])

_TOWER_KEYWORDS = {"torre", "tower"}


def _antenna_gain(antenna_id: str | None) -> float:
    if not antenna_id:
        return 0.0
    ant = antenna_storage.load(antenna_id)
    if ant is None or ant.results is None:
        return 0.0
    return float(ant.results.get("gain_dbi", 0.0))


def _is_tower_name(name: str) -> bool:
    low = name.lower()
    return any(kw in low for kw in _TOWER_KEYWORDS)


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


@router.get("/{id}/export")
def export_scenario(
    id: str,
    include_results: bool = Query(False),
) -> JSONResponse:
    """
    Exporta cenário como JSON para download.
    - include_results=false (padrão): apenas configuração (nós, antenas, links, candidatos)
    - include_results=true: configuração + todos os resultados de simulação
    """
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    if include_results:
        data = s.export_full()
        filename = f"scenario_{id}_completo.json"
    else:
        data = s.export_setup()
        filename = f"scenario_{id}_setup.json"

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return JSONResponse(content=data, headers=headers)


@router.post("/{id}/calculate", response_model=LinkResult)
def calculate(id: str) -> LinkResult:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    antenna_a = antenna_storage.load(s.node_a.antenna_id) if s.node_a.antenna_id else None
    antenna_b = antenna_storage.load(s.node_b.antenna_id) if s.node_b.antenna_id else None

    result = lb.compute_link_full(
        s.node_a, s.node_b, s.frequency_hz,
        propagation_model=s.propagation_model,
        antenna_a=antenna_a,
        antenna_b=antenna_b,
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


@router.post("/{id}/compare", response_model=list[dict])
def compare_scenarios(
    id: str,
    module_ids: list[str] = Query(default=[]),
    tx_antenna_ids: list[str] = Query(default=[]),
    gw_antenna_ids: list[str] = Query(default=[]),
) -> list[dict]:
    """Compara combinações módulo × antena_TX × antena_GW. Retorna tabela ordenada por margem mínima."""
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    modules = (
        [m for mid in module_ids if (m := lora_module_storage.get_module(mid)) is not None]
        if module_ids
        else lora_module_storage.list_modules()
    )

    all_antennas = antenna_storage.list_all()
    tx_ants = [a for a in all_antennas if a.id in tx_antenna_ids] if tx_antenna_ids else all_antennas[:3]
    gw_ants = [a for a in all_antennas if a.id in gw_antenna_ids] if gw_antenna_ids else all_antennas[:3]

    sensor_nodes = [s.node_b] + s.extra_nodes
    gateway_node = s.node_a

    rows = run_comparison(
        sensor_nodes=sensor_nodes,
        gateway_node=gateway_node,
        freq_hz=s.frequency_hz,
        modules=modules,
        tx_antenna_specs=tx_ants,
        gw_antenna_specs=gw_ants,
    )

    return [
        {
            "label": r.scenario_label,
            "module": r.module_id,
            "tx_antenna": r.tx_antenna_type,
            "gw_antenna": r.gw_antenna_type,
            "min_margin_db": round(r.min_margin_db, 2),
            "mean_margin_db": round(r.mean_margin_db, 2),
            "max_margin_db": round(r.max_margin_db, 2),
            "failure_count": r.failure_count,
            "critical_count": r.critical_count,
            "comfortable_count": r.comfortable_count,
            "robustness_score": round(r.robustness_score, 3),
        }
        for r in rows
    ]


# ── Site Selection ─────────────────────────────────────────────────────────────

class CandidateSiteIn(BaseModel):
    id: str | None = None
    name: str
    lat: float
    lon: float
    height_m: float = 20.0
    is_existing_tower: bool = False
    notes: str = ""


class SiteSelectionIn(BaseModel):
    height_overrides: dict[str, float] = Field(default_factory=dict)


@router.post("/{id}/candidates", response_model=LinkScenario)
def add_candidate(id: str, body: CandidateSiteIn) -> LinkScenario:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    candidate = CandidateSite(
        **({"id": body.id} if body.id else {}),
        name=body.name,
        lat=body.lat,
        lon=body.lon,
        height_m=body.height_m,
        is_existing_tower=body.is_existing_tower,
        notes=body.notes,
    )
    updated = s.model_copy(update={"candidates": s.candidates + [candidate]})
    scenario_storage.save(updated)
    return updated


@router.get("/{id}/candidates", response_model=list[CandidateSite])
def list_candidates(id: str) -> list[CandidateSite]:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    return s.candidates


@router.post("/{id}/site-selection")
def site_selection(
    id: str,
    selection_mode: Literal["coverage", "minimax"] = Query("coverage"),
    body: SiteSelectionIn = Body(default=SiteSelectionIn()),
) -> Any:
    s = scenario_storage.load(id)
    if s is None:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    if selection_mode == "minimax":
        sensor_nodes = [s.node_a, s.node_b] + s.extra_nodes
        return lb.minimax_gateway_rank(s.candidates, sensor_nodes)

    field_nodes = [s.node_a, s.node_b] + s.extra_nodes
    candidate_results: list[CandidateCoverageResult] = []

    for candidate in s.candidates:
        effective_height = body.height_overrides.get(candidate.id, candidate.height_m)
        node_results: list[NodeCoverageResult] = []

        for node in field_nodes:
            d = lb.haversine(candidate.lat, candidate.lon, node.lat, node.lon)
            loss = lb.fspl_db(d, s.frequency_hz)
            gain_node = _antenna_gain(node.antenna_id)
            rx_p, margin = lb.compute_link(
                tx_power_dbm=20.0,
                tx_gain_dbi=0.0,
                tx_cable_db=0.0,
                path_loss_db=loss,
                rx_gain_dbi=gain_node,
                rx_cable_db=node.cable_loss_db,
                rx_sensitivity_dbm=node.rx_sensitivity_dbm,
            )
            node_results.append(NodeCoverageResult(
                node_id=node.id,
                node_name=node.name,
                distance_m=round(d, 1),
                link_margin_db=round(margin, 2),
                feasibility=lb.feasibility(margin),
            ))

        total = len(field_nodes)
        covered = sum(1 for nr in node_results if nr.link_margin_db > 0)
        coverage_pct = round((covered / total * 100) if total else 0.0, 1)

        if coverage_pct >= 80:
            overall = "verde"
        elif coverage_pct >= 50:
            overall = "amarelo"
        else:
            overall = "vermelho"

        candidate_results.append(CandidateCoverageResult(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            height_m=effective_height,
            coverage_pct=coverage_pct,
            node_results=node_results,
            feasibility=overall,
        ))

    candidate_results.sort(key=lambda c: c.coverage_pct, reverse=True)
    result = SiteSelectionResult(candidates=candidate_results)
    scenario_storage.save(s.model_copy(update={"site_selection_result": result}))
    return result


# ── KML import ─────────────────────────────────────────────────────────────────

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

    new_nodes: list[NodeSpec] = []
    new_candidates: list[CandidateSite] = []

    for p in parsed.points:
        if _is_tower_name(p.name):
            new_candidates.append(CandidateSite(
                name=p.name,
                lat=p.lat,
                lon=p.lon,
                height_m=p.altitude or 20.0,
                is_existing_tower=True,
            ))
        else:
            new_nodes.append(NodeSpec(
                name=p.name,
                lat=p.lat,
                lon=p.lon,
                height_m=p.altitude or 0.0,
            ))

    poly_dicts = [p.model_dump() for p in parsed.polygons]

    updated = s.model_copy(update={
        "extra_nodes": s.extra_nodes + new_nodes,
        "polygons": s.polygons + poly_dicts,
        "candidates": s.candidates + new_candidates,
    })
    scenario_storage.save(updated)

    return KmlImportResult(
        scenario_id=id,
        nodes_imported=len(new_nodes),
        polygons_imported=len(parsed.polygons),
        candidates_imported=len(new_candidates),
        nodes=new_nodes,
        polygons=poly_dicts,
        candidates=new_candidates,
    )
