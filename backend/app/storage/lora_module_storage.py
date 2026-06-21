import json
from pathlib import Path
from typing import Optional

from ..schemas.lora_module import LoRaModule

_DATA_FILE = Path(__file__).parent.parent / "data" / "lora_modules.json"


def list_modules() -> list[LoRaModule]:
    with open(_DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return [LoRaModule(**item) for item in raw]


def get_module(module_id: str) -> Optional[LoRaModule]:
    for m in list_modules():
        if m.id == module_id:
            return m
    return None
