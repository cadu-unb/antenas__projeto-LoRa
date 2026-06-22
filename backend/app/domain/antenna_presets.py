from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..schemas.antenna_spec import AntennaSpec

# Physical presets aligned with MATLAB external reference.
# Keys match optional fields added in AntennaSpec v2.0.
ANTENNA_PRESETS: dict[str, dict] = {
    "dipolo": {
        "gmax_dbi": 2.15,
        "hpbw_deg": 78.0,
        "polarization": "linear vertical",
        "is_directional": False,
        "pattern_model": "dipole",
        "practicality_score": 8.0,
        "multi_direction_score": 9.0,
    },
    "monopolo": {
        "gmax_dbi": 5.15,
        "hpbw_deg": 55.0,
        "polarization": "linear vertical",
        "is_directional": False,
        "pattern_model": "monopole",
        "practicality_score": 7.0,
        "multi_direction_score": 8.0,
    },
    "helicoidal": {
        "gmax_dbi": 11.0,
        "hpbw_deg": 55.0,
        "polarization": "circular/elliptical",
        "is_directional": True,
        "pattern_model": "helical",
        "practicality_score": 5.0,
        "multi_direction_score": 3.0,
    },
    "parabolica": {
        "gmax_dbi": 20.0,
        "hpbw_deg": 18.0,
        "polarization": "feed-dependent",
        "is_directional": True,
        "pattern_model": "parabolic",
        "practicality_score": 2.0,
        "multi_direction_score": 1.0,
    },
    "pcb_compact": {
        # gmax_dbi=1 is the MATLAB nominal; the solver uses frequency-dependent
        # gain (1.5 dBi at 915 MHz). _effective_gain() must check from_preset
        # and skip this override for pcb_compact unless the user set it explicitly.
        "gmax_dbi": 1.0,
        "hpbw_deg": 120.0,
        "polarization": "linear",
        "is_directional": False,
        "pattern_model": "pcb",
        "practicality_score": 10.0,
        "multi_direction_score": 7.0,
    },
    "commercial_omni_6dbi": {
        "gmax_dbi": 6.0,
        "hpbw_deg": 35.0,
        "polarization": "linear vertical",
        "is_directional": False,
        "pattern_model": "omni_colinear",
        "practicality_score": 9.0,
        "multi_direction_score": 8.0,
    },
}

_PRESET_KEYS = frozenset(ANTENNA_PRESETS["dipolo"].keys())


@dataclass(frozen=True)
class SpecWithDefaults:
    """AntennaSpec with preset-filled fields + metadata about which fields came from the preset."""
    spec: "AntennaSpec"
    from_preset: frozenset[str]  # names of fields filled by preset, not set by user


def apply_antenna_defaults(spec: "AntennaSpec") -> SpecWithDefaults:
    """
    Return a new AntennaSpec with preset physical fields applied for unset slots.

    Rules:
    - Only fills None fields (and empty-string `notes`).
    - Never mutates the input spec or writes to disk.
    - `from_preset` records which fields came from the preset so callers
      (e.g. _effective_gain) can decide whether to trust them.
    - If the type has no preset, returns the spec unchanged with empty from_preset.
    """
    from ..schemas.antenna_spec import AntennaSpec  # local to avoid circular import

    preset = ANTENNA_PRESETS.get(spec.type.lower())
    if preset is None:
        return SpecWithDefaults(spec=spec, from_preset=frozenset())

    updates: dict = {}
    applied: set[str] = set()

    for key, preset_value in preset.items():
        current = getattr(spec, key, None)
        is_empty = current is None or (key == "notes" and current == "")
        if is_empty:
            updates[key] = preset_value
            applied.add(key)

    if not updates:
        return SpecWithDefaults(spec=spec, from_preset=frozenset())

    # Full reconstruction (not model_copy) so that model_validator runs and
    # schema_version is bumped to "2.0" when physical fields are present.
    data = spec.model_dump()
    data.update(updates)
    filled = AntennaSpec(**data)
    return SpecWithDefaults(spec=filled, from_preset=frozenset(applied))
