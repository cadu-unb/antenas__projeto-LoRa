"""
KML parser tests — nível 0 (pontos) e nível 1 (polígonos).
"""
import io
import pytest
from fastapi.testclient import TestClient

from backend.app.domain.kml.parser import KmlParseResult, parse_kml
from backend.app.main import app

client = TestClient(app)

# ── KML fixtures ──────────────────────────────────────────────────────────────

KML_POINTS = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Gateway DF</name>
      <Point><coordinates>-47.9292,-15.7801,30</coordinates></Point>
    </Placemark>
    <Placemark>
      <name>Sensor DF2</name>
      <Point><coordinates>-48.0500,-15.8300,5</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""

KML_POLYGON = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Área de interesse</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -48.00,-15.90,0 -47.90,-15.90,0
              -47.90,-15.80,0 -48.00,-15.80,0
              -48.00,-15.90,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""

KML_MIXED = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Nó Alpha</name>
      <Point><coordinates>-47.93,-15.78,10</coordinates></Point>
    </Placemark>
    <Placemark>
      <name>Zona</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>-48.0,-15.9,0 -47.8,-15.9,0 -47.8,-15.7,0 -48.0,-15.7,0 -48.0,-15.9,0</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""

KML_NO_ALTITUDE = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Sensor</name>
      <Point><coordinates>-47.93,-15.78</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""

KML_GOOGLE_NS = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>
    <Placemark>
      <name>Ponto Google</name>
      <Point><coordinates>-47.93,-15.78,0</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""

KML_MALFORMED = "<?xml version='1.0'?><kml><Document><Placemark><name>x</name"

KML_EMPTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document></Document>
</kml>
"""


# ── Pure parser tests ─────────────────────────────────────────────────────────

def test_parse_two_points():
    r = parse_kml(KML_POINTS)
    assert len(r.points) == 2
    assert len(r.polygons) == 0


def test_parse_point_coordinates():
    r = parse_kml(KML_POINTS)
    gw = next(p for p in r.points if "DF" in p.name)
    assert abs(gw.lat - (-15.7801)) < 1e-4
    assert abs(gw.lon - (-47.9292)) < 1e-4
    assert gw.altitude == pytest.approx(30.0)


def test_parse_polygon():
    r = parse_kml(KML_POLYGON)
    assert len(r.polygons) == 1
    assert len(r.points) == 0
    poly = r.polygons[0]
    assert poly.name == "Área de interesse"
    assert len(poly.outer_ring) >= 3


def test_parse_mixed_points_and_polygons():
    r = parse_kml(KML_MIXED)
    assert len(r.points) == 1
    assert len(r.polygons) == 1


def test_parse_no_altitude_returns_none():
    r = parse_kml(KML_NO_ALTITUDE)
    assert len(r.points) == 1
    assert r.points[0].altitude is None


def test_parse_google_namespace():
    r = parse_kml(KML_GOOGLE_NS)
    assert len(r.points) == 1
    assert r.points[0].name == "Ponto Google"


def test_parse_empty_document():
    r = parse_kml(KML_EMPTY)
    assert r.points == []
    assert r.polygons == []


def test_parse_malformed_raises_valueerror():
    with pytest.raises(ValueError, match="KML malformado"):
        parse_kml(KML_MALFORMED)


def test_parse_result_is_kml_parse_result():
    r = parse_kml(KML_POINTS)
    assert isinstance(r, KmlParseResult)


def test_polygon_ring_coords_order():
    r = parse_kml(KML_POLYGON)
    ring = r.polygons[0].outer_ring
    # each entry is [lon, lat, alt]
    for coord in ring:
        assert len(coord) == 3


# ── API tests ─────────────────────────────────────────────────────────────────

SCENARIO_BASE = {
    "name": "Cenário KML test",
    "node_a": {
        "name": "A", "lat": -15.7801, "lon": -47.9292,
        "height_m": 10.0, "tx_power_dbm": 14.0,
        "rx_sensitivity_dbm": -137.0, "cable_loss_db": 0.0,
    },
    "node_b": {
        "name": "B", "lat": -15.8300, "lon": -48.0500,
        "height_m": 10.0, "tx_power_dbm": 14.0,
        "rx_sensitivity_dbm": -137.0, "cable_loss_db": 0.0,
    },
    "frequency_hz": 915_000_000.0,
}


def _make_scenario() -> str:
    r = client.post("/api/v1/scenarios", json=SCENARIO_BASE)
    assert r.status_code == 201
    return r.json()["id"]


def _kml_upload(scenario_id: str, kml_content: str):
    return client.post(
        f"/api/v1/scenarios/{scenario_id}/kml",
        files={"file": ("test.kml", io.BytesIO(kml_content.encode()), "application/vnd.google-earth.kml+xml")},
    )


def test_kml_import_returns_200():
    sid = _make_scenario()
    r = _kml_upload(sid, KML_POINTS)
    assert r.status_code == 200


def test_kml_import_nodes_count():
    sid = _make_scenario()
    r = _kml_upload(sid, KML_POINTS)
    assert r.json()["nodes_imported"] == 2


def test_kml_import_polygon_count():
    sid = _make_scenario()
    r = _kml_upload(sid, KML_POLYGON)
    assert r.json()["polygons_imported"] == 1


def test_kml_import_nodes_have_coords():
    sid = _make_scenario()
    r = _kml_upload(sid, KML_POINTS)
    nodes = r.json()["nodes"]
    assert len(nodes) == 2
    gw = next(n for n in nodes if "DF" in n["name"])
    assert abs(gw["lat"] - (-15.7801)) < 1e-4
    assert abs(gw["lon"] - (-47.9292)) < 1e-4


def test_kml_import_persists_extra_nodes():
    sid = _make_scenario()
    _kml_upload(sid, KML_POINTS)
    r2 = client.get(f"/api/v1/scenarios/{sid}")
    assert r2.status_code == 200
    assert len(r2.json()["extra_nodes"]) == 2


def test_kml_import_persists_polygons():
    sid = _make_scenario()
    _kml_upload(sid, KML_POLYGON)
    r2 = client.get(f"/api/v1/scenarios/{sid}")
    assert len(r2.json()["polygons"]) == 1


def test_kml_import_unknown_scenario_404():
    r = _kml_upload("does-not-exist", KML_POINTS)
    assert r.status_code == 404


def test_kml_import_malformed_returns_422():
    sid = _make_scenario()
    r = _kml_upload(sid, KML_MALFORMED)
    assert r.status_code == 422


def test_kml_calculate_after_import_same_as_direct():
    """Link budget deve bater independente de KML importado (nós extras não afetam P2P)."""
    sid_direct = _make_scenario()
    r_direct = client.post(f"/api/v1/scenarios/{sid_direct}/calculate")
    fspl_direct = r_direct.json()["fspl_db"]

    sid_kml = _make_scenario()
    _kml_upload(sid_kml, KML_POINTS)
    r_kml = client.post(f"/api/v1/scenarios/{sid_kml}/calculate")
    fspl_kml = r_kml.json()["fspl_db"]

    assert abs(fspl_direct - fspl_kml) < 0.01
