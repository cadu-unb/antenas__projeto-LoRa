import pytest

from lora_antenna.core.constants import (
    C_M_PER_S,
    DEFAULT_RX_SENSITIVITY_DBM,
    DEFAULT_TX_POWER_DBM,
    EPSILON_0_F_PER_M,
    LORA_BR_MAX_HZ,
    LORA_BR_MIN_HZ,
    LORA_DEFAULT_HZ,
    MU_0_H_PER_M,
    Z0_OHM,
)


def test_electromagnetic_constants():
    assert Z0_OHM == 50.0
    assert abs(EPSILON_0_F_PER_M - 8.854_187_817e-12) < 1e-24
    assert abs(MU_0_H_PER_M - 1.256_637_061_435_917e-6) < 1e-18


def test_anatel_range():
    assert LORA_BR_MIN_HZ == 915_000_000.0
    assert LORA_BR_MAX_HZ == 928_000_000.0
    assert LORA_BR_MIN_HZ <= LORA_DEFAULT_HZ <= LORA_BR_MAX_HZ


def test_rx_sensitivity():
    assert DEFAULT_RX_SENSITIVITY_DBM == -137.0


def test_default_tx_power():
    assert DEFAULT_TX_POWER_DBM == 14.0


def test_speed_of_light():
    assert C_M_PER_S == 299_792_458.0
