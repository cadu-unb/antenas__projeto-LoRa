"""Core physical and regulatory constants."""

C_M_PER_S = 299_792_458.0

# Electromagnetic base constants (SI)
Z0_OHM = 50.0
EPSILON_0_F_PER_M = 8.854_187_817e-12
MU_0_H_PER_M = 1.256_637_061_435_917e-6

# ANATEL regulatory — Brazil LoRa 915–928 MHz (immutable)
LORA_BR_MIN_HZ = 915_000_000.0
LORA_BR_MAX_HZ = 928_000_000.0
LORA_DEFAULT_HZ = 915_000_000.0

DEFAULT_TX_POWER_DBM = 14.0
# SX1276 SF12/BW125kHz datasheet sensitivity
DEFAULT_RX_SENSITIVITY_DBM = -137.0
