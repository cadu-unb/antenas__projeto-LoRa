import pytest

from lora_antenna.gis.reference_tables import (
    delta_reference_m,
    reference_distance_m,
    reference_table,
)


def test_table_has_28_entries():
    table = reference_table()
    assert len(table) == 28


def test_delta_p1_p2():
    # Haversine = 399.0, MATLAB flat-earth = 399.4 → delta = -0.4
    result = delta_reference_m("P1", "P2", 399.0)
    assert abs(result - (-0.4)) < 0.05


def test_reference_distance_symmetry():
    d1 = reference_distance_m("P1", "P2")
    d2 = reference_distance_m("P2", "P1")
    assert d1 == d2


def test_all_pairs_positive():
    for (origin, dest), dist in reference_table().items():
        assert dist > 0.0, f"Non-positive distance for {origin}-{dest}: {dist}"


def test_unknown_pair_raises():
    with pytest.raises(KeyError):
        reference_distance_m("P1", "P99")


def test_all_labels_p1_to_p8():
    table = reference_table()
    labels = set()
    for origin, dest in table:
        labels.add(origin)
        labels.add(dest)
    assert labels == {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"}
