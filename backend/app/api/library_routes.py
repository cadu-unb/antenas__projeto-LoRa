from fastapi import APIRouter, HTTPException, status

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
