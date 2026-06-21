from fastapi import APIRouter, HTTPException, Query, status

from ..domain.energy import estimate_energy
from ..schemas.antenna_spec import AntennaSpec
from ..schemas.lora_module import LoRaModule
from ..storage import antenna_storage
from ..storage import lora_module_storage

router = APIRouter(prefix="/api/v1/antennas", tags=["library"])


# ── Antenna CRUD ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[AntennaSpec])
def list_antennas():
    return antenna_storage.list_all()


@router.post("", response_model=AntennaSpec, status_code=status.HTTP_201_CREATED)
def create_antenna(spec: AntennaSpec):
    antenna_storage.save(spec)
    return spec


# ── LoRa module catalog (before /{id} to avoid routing conflict) ─────────────

@router.get("/lora-modules", response_model=list[LoRaModule])
def list_lora_modules():
    return lora_module_storage.list_modules()


@router.get("/lora-modules/{module_id}", response_model=LoRaModule)
def get_lora_module(module_id: str):
    m = lora_module_storage.get_module(module_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    return m


@router.post("/lora-modules/{module_id}/energy", response_model=dict)
def estimate_module_energy(
    module_id: str,
    sf: int = Query(12, ge=7, le=12),
    bw_khz: int = Query(125),
    tx_power_dbm: float = Query(20.0),
    payload_bytes: int = Query(20, ge=1, le=255),
    transmissions_per_day: int = Query(96),
) -> dict:
    """Estima consumo energético e vida útil de bateria para um módulo LoRa."""
    module = lora_module_storage.get_module(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")

    est = estimate_energy(module, tx_power_dbm, sf, bw_khz, payload_bytes, transmissions_per_day)
    return {
        "module": module_id,
        "tx_duration_ms": round(est.tx_duration_ms, 2),
        "energy_per_tx_mj": round(est.energy_per_tx_mj, 4),
        "daily_tx_count": est.daily_tx_count,
        "daily_energy_mwh": round(est.daily_energy_mwh, 4),
        "battery_life_days": round(est.battery_life_days, 1) if est.battery_life_days != float("inf") else None,
    }


# ── Antenna CRUD (continued) ──────────────────────────────────────────────────

@router.get("/{id}", response_model=AntennaSpec)
def get_antenna(id: str):
    spec = antenna_storage.load(id)
    if spec is None:
        raise HTTPException(status_code=404, detail="Antena não encontrada")
    return spec


@router.put("/{id}", response_model=AntennaSpec)
def update_antenna(id: str, spec: AntennaSpec):
    if antenna_storage.load(id) is None:
        raise HTTPException(status_code=404, detail="Antena não encontrada")
    updated = spec.model_copy(update={"id": id})
    antenna_storage.save(updated)
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_antenna(id: str):
    if not antenna_storage.delete(id):
        raise HTTPException(status_code=404, detail="Antena não encontrada")
