import pytest

from lora_antenna.antenna.base import Antenna
from lora_antenna.propagation.batch.contracts import (
    LinkBatchRequest,
    ScalarLinkInput,
)


def _default_scalar(**overrides) -> ScalarLinkInput:
    defaults = {
        "origin_label": "P1",
        "dest_label": "P2",
        "distance_m": 300.0,
        "distance_3d_m": 300.0,
        "total_extra_loss_db": 0.0,
    }
    defaults.update(overrides)
    return ScalarLinkInput(**defaults)


def test_scalar_same_label_raises():
    with pytest.raises(ValueError):
        _default_scalar(origin_label="A", dest_label="A")


def test_scalar_negative_distance_raises():
    with pytest.raises(ValueError):
        _default_scalar(distance_m=-1.0)


def test_scalar_negative_3d_distance_raises():
    with pytest.raises(ValueError):
        _default_scalar(distance_3d_m=-1.0)


def test_scalar_negative_loss_raises():
    with pytest.raises(ValueError):
        _default_scalar(total_extra_loss_db=-1.0)


def test_scalar_negative_buildings_raises():
    with pytest.raises(ValueError):
        _default_scalar(n_buildings_crossed=-1)


def test_batch_request_out_of_band_frequency_raises():
    scalar = _default_scalar()
    with pytest.raises(ValueError):
        LinkBatchRequest(
            pairs=[scalar],
            antenna=Antenna(gain_dbi=2.15),
            frequency_hz=433_000_000.0,
        )


def test_batch_request_invalid_sf_raises():
    scalar = _default_scalar()
    with pytest.raises(ValueError):
        LinkBatchRequest(
            pairs=[scalar],
            antenna=Antenna(gain_dbi=2.15),
            frequency_hz=915_200_000.0,
            sf=13,
        )


def test_batch_request_empty_pairs_raises():
    with pytest.raises(ValueError):
        LinkBatchRequest(
            pairs=[],
            antenna=Antenna(gain_dbi=2.15),
            frequency_hz=915_200_000.0,
        )


def test_batch_request_valid():
    scalar = _default_scalar()
    req = LinkBatchRequest(
        pairs=[scalar],
        antenna=Antenna(gain_dbi=2.15),
        frequency_hz=915_200_000.0,
    )
    assert req.sf == 12
    assert req.frequency_hz == 915_200_000.0
