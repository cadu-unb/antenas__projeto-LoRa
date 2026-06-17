from pathlib import Path

from ..schemas.link_scenario import LinkScenario

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "scenarios"


def save(scenario: LinkScenario) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / f"{scenario.id}.json").write_text(scenario.model_dump_json(indent=2))


def load(id: str) -> LinkScenario | None:
    path = DATA_DIR / f"{id}.json"
    if not path.exists():
        return None
    return LinkScenario.model_validate_json(path.read_text())


def list_all() -> list[LinkScenario]:
    if not DATA_DIR.exists():
        return []
    result = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            result.append(LinkScenario.model_validate_json(f.read_text()))
        except Exception:
            pass
    return result
