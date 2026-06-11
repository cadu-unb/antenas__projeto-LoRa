import pytest

from lora_antenna.gis.distance_matrix import DistanceMatrix, DistanceMatrixEntry


def _entry(origin: str, dest: str, dist: float) -> DistanceMatrixEntry:
    return DistanceMatrixEntry(origin_label=origin, dest_label=dest, distance_m=dist)


def test_get_distance_forward():
    matrix = DistanceMatrix(entries=[_entry("P1", "P2", 399.0)])
    assert matrix.get_distance("P1", "P2") == 399.0


def test_get_distance_reverse():
    matrix = DistanceMatrix(entries=[_entry("P1", "P2", 399.0)])
    assert matrix.get_distance("P2", "P1") == 399.0


def test_get_distance_missing_raises():
    matrix = DistanceMatrix(entries=[])
    with pytest.raises(KeyError):
        matrix.get_distance("P1", "P2")


def test_to_dict():
    entry = _entry("A", "B", 100.0)
    matrix = DistanceMatrix(entries=[entry])
    d = matrix.to_dict()
    assert d[("A", "B")] == 100.0


def test_with_reference_delta_fills():
    entry = _entry("P1", "P2", 399.0)
    matrix = DistanceMatrix(entries=[entry])
    ref_table = {("P1", "P2"): 399.4}
    updated = matrix.with_reference_delta(ref_table)
    e = updated.entries[0]
    assert e.delta_reference_m is not None
    assert abs(e.delta_reference_m - (-0.4)) < 0.05


def test_with_reference_delta_missing_pair_is_none():
    entry = _entry("P1", "P2", 399.0)
    matrix = DistanceMatrix(entries=[entry])
    updated = matrix.with_reference_delta({})
    assert updated.entries[0].delta_reference_m is None


def test_matrix_is_frozen():
    matrix = DistanceMatrix(entries=[])
    with pytest.raises(Exception):
        matrix.entries = []  # type: ignore[misc]
