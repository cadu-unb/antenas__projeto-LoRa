"""
Testes de topologias avançadas — Fase 9.

Topologias cobertas: MESH, MULTI_STAR.
Funcionalidades testadas:
  - Adicionar/remover enlaces individuais
  - Detecção de ilhas (nós sem nenhum enlace)
  - Link budget multi-hop (acumulação por hop, gargalo = menor margem)
  - Redundância: nó com dois caminhos upstream → melhor margem exibida
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.domain.link_budget import find_islands, best_path_margin, feasibility
from backend.app.schemas.link_scenario import HopResult, LinkEdge

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────

BASE_SCENARIO = {
    "name": "Malha teste",
    "topology_type": "MESH",
    "frequency_hz": 915e6,
    "node_a": {
        "id": "node-a",
        "name": "Hub 1",
        "lat": -23.55,
        "lon": -46.63,
        "height_m": 30,
        "tx_power_dbm": 20,
        "rx_sensitivity_dbm": -137,
        "cable_loss_db": 0,
        "is_hub": True,
    },
    "node_b": {
        "id": "node-b",
        "name": "Hub 2",
        "lat": -23.60,
        "lon": -46.70,
        "height_m": 30,
        "tx_power_dbm": 20,
        "rx_sensitivity_dbm": -137,
        "cable_loss_db": 0,
        "is_hub": True,
    },
    "extra_nodes": [
        {
            "id": "node-c",
            "name": "Folha C",
            "lat": -23.57,
            "lon": -46.65,
            "height_m": 5,
            "tx_power_dbm": 14,
            "rx_sensitivity_dbm": -137,
            "cable_loss_db": 0,
            "is_hub": False,
        },
        {
            "id": "node-d",
            "name": "Folha D",
            "lat": -23.53,
            "lon": -46.68,
            "height_m": 5,
            "tx_power_dbm": 14,
            "rx_sensitivity_dbm": -137,
            "cable_loss_db": 0,
            "is_hub": False,
        },
    ],
    "links": [],
    "polygons": [],
}


def _create_scenario(overrides=None):
    payload = {**BASE_SCENARIO, **(overrides or {})}
    r = client.post("/api/v1/scenarios", json=payload)
    assert r.status_code == 201
    return r.json()


# ── find_islands (pura) ───────────────────────────────────────────────────────

def test_find_islands_all_isolated():
    """Sem enlaces → todos são ilhas."""
    islands = find_islands(["A", "B", "C"], [])
    assert set(islands) == {"A", "B", "C"}


def test_find_islands_none():
    """Todos conectados → sem ilhas."""
    edges = [
        LinkEdge(node_a_id="A", node_b_id="B"),
        LinkEdge(node_a_id="B", node_b_id="C"),
    ]
    islands = find_islands(["A", "B", "C"], edges)
    assert islands == []


def test_find_islands_partial():
    """Nó D não conectado → apenas D é ilha."""
    edges = [LinkEdge(node_a_id="A", node_b_id="B")]
    islands = find_islands(["A", "B", "D"], edges)
    assert islands == ["D"]


# ── best_path_margin (pura) ───────────────────────────────────────────────────

def _make_hop(edge_id, a_id, b_id, margin):
    return HopResult(
        edge_id=edge_id, node_a_id=a_id, node_b_id=b_id,
        node_a_name="X", node_b_name="Y",
        distance_m=1000, fspl_db=91.7,
        rx_power_dbm=-45.0, link_margin_db=margin,
        feasibility=feasibility(margin),
    )


def test_best_path_margin_redundant():
    """Nó com dois caminhos upstream → melhor margem retornada."""
    hops = [
        _make_hop("e1", "hub1", "leaf", 5.0),
        _make_hop("e2", "hub2", "leaf", 25.0),
    ]
    best = best_path_margin("leaf", hops)
    assert best == 25.0


def test_best_path_margin_single():
    hops = [_make_hop("e1", "hub1", "leaf", 12.0)]
    assert best_path_margin("leaf", hops) == 12.0


def test_best_path_margin_no_match():
    hops = [_make_hop("e1", "A", "B", 10.0)]
    assert best_path_margin("Z", hops) is None


# ── API — adicionar enlace ────────────────────────────────────────────────────

def test_add_link_returns_updated_scenario():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a",
        "node_b_id": "node-b",
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data["links"]) == 1
    assert data["links"][0]["node_a_id"] == "node-a"
    assert data["links"][0]["node_b_id"] == "node-b"


def test_add_link_with_explicit_id():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "id": "edge-xyz",
        "node_a_id": "node-a",
        "node_b_id": "node-c",
    })
    assert r.status_code == 200
    assert r.json()["links"][0]["id"] == "edge-xyz"


def test_add_link_scenario_not_found():
    r = client.post("/api/v1/scenarios/nonexistent/links", json={
        "node_a_id": "A", "node_b_id": "B",
    })
    assert r.status_code == 404


# ── API — remover enlace ──────────────────────────────────────────────────────

def test_remove_link_success():
    s = _create_scenario()
    # add link
    r = client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "id": "edge-to-remove",
        "node_a_id": "node-a",
        "node_b_id": "node-b",
    })
    assert len(r.json()["links"]) == 1

    # remove link
    r2 = client.delete(f"/api/v1/scenarios/{s['id']}/links/edge-to-remove")
    assert r2.status_code == 204

    # verify removed
    r3 = client.get(f"/api/v1/scenarios/{s['id']}")
    assert len(r3.json()["links"]) == 0


def test_remove_link_not_found():
    s = _create_scenario()
    r = client.delete(f"/api/v1/scenarios/{s['id']}/links/nonexistent-edge")
    assert r.status_code == 404


def test_remove_link_does_not_delete_scenario():
    s = _create_scenario()
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "id": "e1", "node_a_id": "node-a", "node_b_id": "node-b",
    })
    client.delete(f"/api/v1/scenarios/{s['id']}/links/e1")
    r = client.get(f"/api/v1/scenarios/{s['id']}")
    assert r.status_code == 200  # cenário ainda existe


# ── API — calculate_links ─────────────────────────────────────────────────────

def test_calculate_links_no_links_all_islands():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/calculate_links")
    assert r.status_code == 200
    data = r.json()
    assert data["hops"] == []
    assert len(data["islands"]) == 4  # A, B, C, D todos ilhas
    assert data["feasibility"] == "vermelho"


def test_calculate_links_single_hop_margin():
    """Enlace de ~5 km em espaço livre com Tx=20 dBm → margem positiva."""
    s = _create_scenario()
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-b",
    })
    r = client.post(f"/api/v1/scenarios/{s['id']}/calculate_links")
    assert r.status_code == 200
    data = r.json()
    assert len(data["hops"]) == 1
    hop = data["hops"][0]
    assert hop["distance_m"] > 0
    assert hop["fspl_db"] > 0
    assert hop["link_margin_db"] > 0  # LoRa 20 dBm → margem ampla em ~5 km


def test_calculate_links_bottleneck_is_minimum_margin():
    """Bottleneck margin = mínimo entre todos os hops."""
    # scenario with 3 nodes in a chain-mesh
    s = _create_scenario()
    # Link A→B (longa distância, menor margem)
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-b",
    })
    # Link A→C (distância curta, maior margem)
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-c",
    })
    r = client.post(f"/api/v1/scenarios/{s['id']}/calculate_links")
    data = r.json()
    hops = data["hops"]
    assert len(hops) == 2
    min_margin = min(h["link_margin_db"] for h in hops)
    assert abs(data["bottleneck_margin_db"] - min_margin) < 0.01


def test_calculate_links_island_detection():
    """Nó D sem enlace aparece em islands."""
    s = _create_scenario()
    # conectar apenas A, B, C
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-b",
    })
    client.post(f"/api/v1/scenarios/{s['id']}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-c",
    })
    r = client.post(f"/api/v1/scenarios/{s['id']}/calculate_links")
    data = r.json()
    assert "node-d" in data["islands"]
    assert "node-a" not in data["islands"]
    assert "node-b" not in data["islands"]


# ── Multi-estrela: dois hubs ──────────────────────────────────────────────────

def test_multi_star_two_hubs_connected():
    """Hub1 e Hub2 conectados entre si + cada hub com folha própria."""
    s = _create_scenario({"topology_type": "MULTI_STAR"})
    sid = s["id"]
    # Hub1 ↔ Hub2
    client.post(f"/api/v1/scenarios/{sid}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-b",
    })
    # Hub1 → Folha C
    client.post(f"/api/v1/scenarios/{sid}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-c",
    })
    # Hub2 → Folha D
    client.post(f"/api/v1/scenarios/{sid}/links", json={
        "node_a_id": "node-b", "node_b_id": "node-d",
    })
    r = client.post(f"/api/v1/scenarios/{sid}/calculate_links")
    data = r.json()
    assert len(data["hops"]) == 3
    assert data["islands"] == []  # todos conectados


def test_multi_star_node_with_two_upstream_hubs():
    """Folha C com dois hubs upstream → duas entradas em hops para node-c."""
    s = _create_scenario({"topology_type": "MULTI_STAR"})
    sid = s["id"]
    # Hub1 → Folha C
    client.post(f"/api/v1/scenarios/{sid}/links", json={
        "node_a_id": "node-a", "node_b_id": "node-c",
    })
    # Hub2 → Folha C (redundância)
    client.post(f"/api/v1/scenarios/{sid}/links", json={
        "node_a_id": "node-b", "node_b_id": "node-c",
    })
    r = client.post(f"/api/v1/scenarios/{sid}/calculate_links")
    data = r.json()
    hops_to_c = [h for h in data["hops"] if h["node_b_id"] == "node-c"]
    assert len(hops_to_c) == 2
    # melhor margem
    best = max(h["link_margin_db"] for h in hops_to_c)
    assert best > 0


# ── Topologia — campo topology_type armazenado ────────────────────────────────

def test_topology_type_mesh_persisted():
    s = _create_scenario({"topology_type": "MESH"})
    r = client.get(f"/api/v1/scenarios/{s['id']}")
    assert r.json()["topology_type"] == "MESH"


def test_topology_type_hierarchical():
    s = _create_scenario({"topology_type": "HIERARCHICAL"})
    assert s["topology_type"] == "HIERARCHICAL"


def test_is_hub_field_persisted():
    s = _create_scenario()
    assert s["node_a"]["is_hub"] is True
    assert s["node_b"]["is_hub"] is True
    assert s["extra_nodes"][0]["is_hub"] is False
