from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from .node_spec import NodeSpec


class LinkResult(BaseModel):
    distance_m: float
    azimuth_deg: float
    elevation_deg: float
    fspl_db: float
    rx_power_dbm: float
    link_margin_db: float
    feasibility: str  # "verde" | "amarelo" | "vermelho"


class LinkEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_a_id: str
    node_b_id: str


class HopResult(BaseModel):
    edge_id: str
    node_a_id: str
    node_b_id: str
    node_a_name: str
    node_b_name: str
    distance_m: float
    fspl_db: float
    rx_power_dbm: float
    link_margin_db: float
    feasibility: str


class TopologyResult(BaseModel):
    hops: list[HopResult]
    islands: list[str]  # node IDs with no links
    bottleneck_margin_db: float  # min margin across all hops
    feasibility: str


class LinkScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    node_a: NodeSpec
    node_b: NodeSpec
    frequency_hz: float
    topology_type: str = "P2P"  # P2P | CHAIN | STAR | MESH | MULTI_STAR | HIERARCHICAL
    extra_nodes: list[NodeSpec] = Field(default_factory=list)
    links: list[LinkEdge] = Field(default_factory=list)
    polygons: list[dict] = Field(default_factory=list)
    results: Optional[LinkResult] = None
    topology_result: Optional[TopologyResult] = None
    metadata: dict = Field(default_factory=dict)


class KmlImportResult(BaseModel):
    scenario_id: str
    nodes_imported: int
    polygons_imported: int
    nodes: list[NodeSpec]
    polygons: list[dict]
