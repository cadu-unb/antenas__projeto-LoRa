import math

import pytest

from lora_antenna.core.constants import DEFAULT_RX_SENSITIVITY_DBM
from lora_antenna.propagation.friis import (
    LinkRisk,
    classify_link_risk,
    friis_received_power_dbm,
    fspl_db,
    link_margin_db,
)


def test_fspl_positive():
    loss = fspl_db(399.0, 915_200_000.0)
    assert loss > 0.0


def test_fspl_increases_with_distance():
    loss_near = fspl_db(100.0, 915_200_000.0)
    loss_far = fspl_db(1000.0, 915_200_000.0)
    assert loss_far > loss_near


def test_fspl_out_of_band_raises():
    with pytest.raises(ValueError):
        fspl_db(100.0, 433_000_000.0)


def test_friis_received_power_decreases_with_distance():
    pr_near = friis_received_power_dbm(14.0, 2.15, 2.15, fspl_db=fspl_db(100.0, 915_200_000.0))
    pr_far = friis_received_power_dbm(14.0, 2.15, 2.15, fspl_db=fspl_db(1000.0, 915_200_000.0))
    assert pr_near > pr_far


def test_link_margin_db():
    margin = link_margin_db(-65.0, DEFAULT_RX_SENSITIVITY_DBM)
    assert margin == pytest.approx(-65.0 - DEFAULT_RX_SENSITIVITY_DBM, abs=0.01)


def test_classify_low_risk():
    # margin > 20 dB → LOW
    risk = classify_link_risk(DEFAULT_RX_SENSITIVITY_DBM + 25.0)
    assert risk == LinkRisk.LOW


def test_classify_medium_risk():
    # 0 < margin <= 20 → MEDIUM
    risk = classify_link_risk(DEFAULT_RX_SENSITIVITY_DBM + 10.0)
    assert risk == LinkRisk.MEDIUM


def test_classify_high_risk():
    # margin <= 0 → HIGH
    risk = classify_link_risk(DEFAULT_RX_SENSITIVITY_DBM - 1.0)
    assert risk == LinkRisk.HIGH


def test_classify_uses_default_sensitivity():
    # With default sensitivity = -137.0, power = -110 → margin = 27 → LOW
    risk = classify_link_risk(-110.0)
    assert risk == LinkRisk.LOW
