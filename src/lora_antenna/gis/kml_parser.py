"""KML parser for points and polygons used by the GIS layer."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from lora_antenna.models.geo import GeographicPosition


class KMLPolygonRole(str, Enum):
    """Semantic role inferred or assigned to a KML polygon."""

    CAMPUS_BOUNDARY = "campus_boundary"
    BUILDING = "building"
    OBSTACLE = "obstacle"
    UNKNOWN = "unknown"


class KMLPoint(GeographicPosition):
    """Point of interest extracted from a KML Placemark."""

    description: Optional[str] = None
    source_index: int = 0


class KMLPolygon(BaseModel):
    """Polygon extracted from a KML Placemark."""

    model_config = ConfigDict(frozen=True)

    label: str
    role: KMLPolygonRole = KMLPolygonRole.UNKNOWN
    exterior_ring: list[tuple[float, float]] = Field(default_factory=list)
    altitude_m: float = 0.0
    description: Optional[str] = None
    source_index: int = 0

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("KMLPolygon label cannot be empty.")
        return value

    @model_validator(mode="after")
    def validate_ring(self) -> "KMLPolygon":
        if len(self.exterior_ring) < 3:
            raise ValueError("KMLPolygon exterior_ring must have at least 3 points.")
        return self


class KMLDocument(BaseModel):
    """Validated KML document with point and polygon features."""

    model_config = ConfigDict(frozen=True)

    name: str = "KML Import"
    points: list[KMLPoint] = Field(default_factory=list)
    polygons: list[KMLPolygon] = Field(default_factory=list)
    schema_version: str = "1.0"
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_document(self) -> "KMLDocument":
        if not self.points and not self.polygons:
            raise ValueError("KML sem pontos ou poligonos reconheciveis.")

        labels = [point.label for point in self.points]
        if len(labels) != len(set(labels)):
            raise ValueError("KML contem labels de pontos duplicados.")
        return self

    @property
    def labels(self) -> list[str]:
        """Return point labels in source order."""
        return [point.label for point in self.points]

    def get_point(self, label: str) -> Optional[KMLPoint]:
        """Return a point by label."""
        for point in self.points:
            if point.label == label:
                return point
        return None

    def positions(self) -> list[GeographicPosition]:
        """Return KML points as neutral geographic positions."""
        return [
            GeographicPosition(
                label=point.label,
                latitude=point.latitude,
                longitude=point.longitude,
                altitude_m=point.altitude_m,
                altitude_srtm_m=point.altitude_srtm_m,
                x_m=point.x_m,
                y_m=point.y_m,
                z_m=point.z_m,
            )
            for point in self.points
        ]

    def polygons_by_role(self, *roles: KMLPolygonRole) -> list[KMLPolygon]:
        """Return polygons matching any of the provided roles."""
        role_set = set(roles)
        return [polygon for polygon in self.polygons if polygon.role in role_set]


def parse_kml_file(path: str | Path) -> KMLDocument:
    """Parse a KML document from a filesystem path."""
    return parse_kml(Path(path).read_bytes())


def parse_kml(kml_bytes: bytes) -> KMLDocument:
    """Parse Point and Polygon placemarks from KML bytes."""
    root = ET.fromstring(kml_bytes)
    ns_prefix = _namespace_prefix(root)
    doc_name = _document_name(root, ns_prefix)
    points: list[KMLPoint] = []
    polygons: list[KMLPolygon] = []

    for index, placemark in enumerate(root.iter(f"{ns_prefix}Placemark"), start=1):
        label = _child_text(placemark, ns_prefix, "name") or f"Feature {index}"
        description = _child_text(placemark, ns_prefix, "description")

        point = _parse_point(placemark, ns_prefix, label, description, index)
        if point is not None:
            points.append(point)

        polygons.extend(
            _parse_polygons(placemark, ns_prefix, label, description, index)
        )

    return KMLDocument(name=doc_name, points=points, polygons=polygons)


def _namespace_prefix(root: ET.Element) -> str:
    if root.tag.startswith("{"):
        return root.tag.split("}")[0] + "}"
    return ""


def _child_text(
    element: ET.Element,
    ns_prefix: str,
    child_name: str,
) -> Optional[str]:
    child = element.find(f"{ns_prefix}{child_name}")
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _document_name(root: ET.Element, ns_prefix: str) -> str:
    document_name = root.find(f".//{ns_prefix}Document/{ns_prefix}name")
    if document_name is not None and document_name.text:
        return document_name.text.strip()
    return "KML Import"


def _parse_point(
    placemark: ET.Element,
    ns_prefix: str,
    label: str,
    description: Optional[str],
    source_index: int,
) -> Optional[KMLPoint]:
    point = placemark.find(f".//{ns_prefix}Point")
    if point is None:
        return None

    coordinates_el = point.find(f".//{ns_prefix}coordinates")
    if coordinates_el is None or coordinates_el.text is None:
        return None

    coordinates = _parse_coordinates(coordinates_el.text)
    if not coordinates:
        return None

    lon, lat, altitude = coordinates[0]
    return KMLPoint(
        label=label,
        latitude=lat,
        longitude=lon,
        altitude_m=altitude,
        description=description,
        source_index=source_index,
    )


def _parse_polygons(
    placemark: ET.Element,
    ns_prefix: str,
    label: str,
    description: Optional[str],
    source_index: int,
) -> list[KMLPolygon]:
    polygons: list[KMLPolygon] = []
    role = infer_polygon_role(label, description)

    for polygon_index, polygon in enumerate(
        placemark.iter(f"{ns_prefix}Polygon"),
        start=1,
    ):
        coordinates_el = polygon.find(
            f".//{ns_prefix}outerBoundaryIs/"
            f"{ns_prefix}LinearRing/{ns_prefix}coordinates"
        )
        if coordinates_el is None or coordinates_el.text is None:
            coordinates_el = polygon.find(f".//{ns_prefix}coordinates")
        if coordinates_el is None or coordinates_el.text is None:
            continue

        coordinates = _parse_coordinates(coordinates_el.text)
        if len(coordinates) < 3:
            continue

        ring = [(lon, lat) for lon, lat, _ in coordinates]
        altitudes = [alt for _, _, alt in coordinates]
        polygon_label = label
        if polygon_index > 1:
            polygon_label = f"{label} #{polygon_index}"

        polygons.append(
            KMLPolygon(
                label=polygon_label,
                role=role,
                exterior_ring=ring,
                altitude_m=altitudes[0] if altitudes else 0.0,
                description=description,
                source_index=source_index,
            )
        )

    return polygons


def _parse_coordinates(coordinates_text: str) -> list[tuple[float, float, float]]:
    coordinates: list[tuple[float, float, float]] = []
    for raw_point in coordinates_text.replace("\n", " ").split():
        values = [value for value in raw_point.split(",") if value != ""]
        if len(values) < 2:
            continue
        lon = float(values[0])
        lat = float(values[1])
        altitude = float(values[2]) if len(values) >= 3 else 0.0
        coordinates.append((lon, lat, altitude))
    return coordinates


def infer_polygon_role(
    label: str,
    description: Optional[str] = None,
) -> KMLPolygonRole:
    """Infer a polygon role from KML label/description text."""
    text = f"{label} {description or ''}".lower()
    if any(token in text for token in ("campus", "boundary", "fronteira", "limite")):
        return KMLPolygonRole.CAMPUS_BOUNDARY
    if any(token in text for token in ("building", "edificio", "edificacao", "predio")):
        return KMLPolygonRole.BUILDING
    if any(token in text for token in ("obstacle", "obstaculo", "barreira")):
        return KMLPolygonRole.OBSTACLE
    return KMLPolygonRole.UNKNOWN
