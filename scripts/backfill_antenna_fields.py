#!/usr/bin/env python3
"""
Backfill physical fields in saved AntennaSpec JSON files.

Usage:
    python scripts/backfill_antenna_fields.py [--data-dir PATH] [--write]

Default: dry-run — shows what would change, writes nothing.
Add --write to apply changes. Reversible via git.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas.antenna_spec import AntennaSpec  # noqa: E402
from app.domain.antenna_presets import ANTENNA_PRESETS, apply_antenna_defaults  # noqa: E402

PHYSICAL_FIELDS = [
    "gmax_dbi", "hpbw_deg", "polarization", "is_directional",
    "pattern_model", "practicality_score", "multi_direction_score",
]


def _process(path: Path, write: bool) -> dict:
    raw = path.read_text(encoding="utf-8")
    try:
        spec = AntennaSpec.model_validate_json(raw)
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}

    missing = [f for f in PHYSICAL_FIELDS if getattr(spec, f) is None]
    if not missing:
        return {"status": "skip", "reason": "all physical fields already set"}

    if spec.type not in ANTENNA_PRESETS:
        return {"status": "skip", "reason": f"no preset for type '{spec.type}'"}

    result = apply_antenna_defaults(spec)
    changes = {f: getattr(result.spec, f) for f in result.from_preset}
    if not changes:
        return {"status": "skip", "reason": "no applicable preset values"}

    if write:
        path.write_text(result.spec.model_dump_json(indent=2), encoding="utf-8")
        return {"status": "written", "changes": changes}

    return {"status": "would_write", "changes": changes}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Backfill physical field presets into saved AntennaSpec JSON files.",
    )
    parser.add_argument(
        "--data-dir", type=Path,
        default=ROOT / "backend" / "data" / "antenna_specs",
        help="Directory with {id}.json files (default: backend/data/antenna_specs)",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write changes to disk (default: dry-run only)",
    )
    args = parser.parse_args(argv)

    data_dir: Path = args.data_dir
    if not data_dir.exists():
        print(f"ERROR: directory not found: {data_dir}", file=sys.stderr)
        return 1

    files = sorted(data_dir.glob("*.json"))
    if not files:
        print(f"No JSON files found in {data_dir}")
        return 0

    mode = "WRITE" if args.write else "DRY-RUN"
    print(f"\n[{mode}] Backfill — {len(files)} file(s) in {data_dir}\n")

    counts: dict[str, int] = {"written": 0, "would_write": 0, "skip": 0, "error": 0}

    for path in files:
        r = _process(path, write=args.write)
        status = r["status"]
        counts[status] = counts.get(status, 0) + 1

        if status in ("written", "would_write"):
            verb = "Written" if status == "written" else "Would write"
            print(f"  {verb}: {path.name}")
            for field, value in r["changes"].items():
                print(f"    + {field} = {value!r}")
        elif status == "skip":
            print(f"  Skip:   {path.name}  ({r['reason']})")
        else:
            print(f"  ERROR:  {path.name}  — {r['detail']}")

    print()
    if args.write:
        print(
            f"Done. {counts['written']} written, "
            f"{counts['skip']} skipped, {counts['error']} errors."
        )
    else:
        print(
            f"Dry-run complete. {counts['would_write']} would be written, "
            f"{counts['skip']} skipped, {counts['error']} errors."
        )
        if counts["would_write"]:
            print("Re-run with --write to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
