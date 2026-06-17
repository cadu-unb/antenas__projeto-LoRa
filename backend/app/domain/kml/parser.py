"""
KML parser — nível 0 (pontos + altitude) e nível 1 (polígonos, apenas visual).

Suporta namespaces OGC 2.2 e Google Earth 2.1/2.2.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Optional

from pydantic import BaseModel

_NAMESPACES = [
    "http://www.opengis.net/kml/2.2",
    "http://earth.google.com/kml/2.2",
    "http://earth.google.com/kml/2.1",
    "",
]


class KmlPoint(BaseModel):
    name: str
    lat: float
    lon: float
    altitude: Optional[float] = None


class KmlPolygon(BaseModel):
    name: str
    outer_ring: list[list[float]]  # [[lon, lat, alt], ...]


class KmlParseResult(BaseModel):
    points: list[KmlPoint]
    polygons: list[KmlPolygon]


def _detect_ns(root: ET.Element) -> str:
    tag = root.tag
    if tag.startswith("{"):
        return tag[1 : tag.index("}")]
    return ""


def _tag(ns: str, local: str) -> str:
    return f"{{{ns}}}{local}" if ns else local


def _parse_coords_single(text: str) -> tuple[float, float, float] | None:
    """Parse 'lon,lat[,alt]' string."""
    parts = text.strip().split(",")
    if len(parts) < 2:
        return None
    try:
        lon = float(parts[0])
        lat = float(parts[1])
        alt = float(parts[2]) if len(parts) >= 3 else 0.0
        return lon, lat, alt
    except ValueError:
        return None


def _parse_coords_ring(text: str) -> list[list[float]]:
    """Parse whitespace-separated 'lon,lat[,alt]' tuples."""
    ring: list[list[float]] = []
    for token in text.strip().split():
        parts = token.split(",")
        if len(parts) < 2:
            continue
        try:
            lon = float(parts[0])
            lat = float(parts[1])
            alt = float(parts[2]) if len(parts) >= 3 else 0.0
            ring.append([lon, lat, alt])
        except ValueError:
            continue
    return ring


def parse_kml(content: str) -> KmlParseResult:
    """Parse KML string.  Raises ValueError for malformed XML."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError(f"KML malformado: {exc}") from exc

    ns = _detect_ns(root)
    t = lambda local: _tag(ns, local)  # noqa: E731

    points: list[KmlPoint] = []
    polygons: list[KmlPolygon] = []

    for pm in root.iter(t("Placemark")):
        name_el = pm.find(t("name"))
        name = (name_el.text or "").strip() if name_el is not None else "Sem nome"
        if not name:
            name = "Sem nome"

        # ── Point ────────────────────────────────────────────────────────────
        point_el = pm.find(f".//{t('Point')}")
        if point_el is not None:
            coords_el = point_el.find(t("coordinates"))
            if coords_el is not None and coords_el.text:
                parsed = _parse_coords_single(coords_el.text)
                if parsed:
                    lon, lat, alt = parsed
                    points.append(KmlPoint(
                        name=name,
                        lat=lat,
                        lon=lon,
                        altitude=alt if alt != 0.0 else None,
                    ))

        # ── Polygon ──────────────────────────────────────────────────────────
        poly_el = pm.find(f".//{t('Polygon')}")
        if poly_el is not None:
            outer_el = poly_el.find(
                f".//{t('outerBoundaryIs')}/{t('LinearRing')}/{t('coordinates')}"
            )
            if outer_el is None:
                # try without intermediate elements
                outer_el = poly_el.find(f".//{t('coordinates')}")
            if outer_el is not None and outer_el.text:
                ring = _parse_coords_ring(outer_el.text)
                if ring:
                    polygons.append(KmlPolygon(name=name, outer_ring=ring))

    return KmlParseResult(points=points, polygons=polygons)
