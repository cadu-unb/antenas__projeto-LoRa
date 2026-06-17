from pathlib import Path

from ..schemas.antenna_spec import AntennaSpec

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "antenna_specs"


def save(spec: AntennaSpec) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / f"{spec.id}.json").write_text(spec.model_dump_json(indent=2))


def load(id: str) -> AntennaSpec | None:
    path = DATA_DIR / f"{id}.json"
    if not path.exists():
        return None
    return AntennaSpec.model_validate_json(path.read_text())


def list_all() -> list[AntennaSpec]:
    if not DATA_DIR.exists():
        return []
    specs = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            specs.append(AntennaSpec.model_validate_json(f.read_text()))
        except Exception:
            pass
    return specs


def delete(id: str) -> bool:
    path = DATA_DIR / f"{id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
