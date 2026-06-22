"""Tests for scripts/backfill_antenna_fields.py using a temporary directory."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas.antenna_spec import AntennaSpec

# Import the module under test by path manipulation
SCRIPT = ROOT / "scripts" / "backfill_antenna_fields.py"
import importlib.util

spec_loader = importlib.util.spec_from_file_location("backfill", SCRIPT)
backfill_mod = importlib.util.module_from_spec(spec_loader)
spec_loader.loader.exec_module(backfill_mod)


def _write_spec(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _read_spec(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ── fixtures ─────────────────────────────────────────────────────────────────

OLD_SPEC_DIPOLO = {
    "schema_version": "1.0",
    "id": "aaaa-0001",
    "name": "Old Dipolo",
    "type": "dipolo",
    "frequency_hz": 915_000_000,
    "solver": "rapido",
}

OLD_SPEC_OMNI = {
    "schema_version": "1.0",
    "id": "bbbb-0002",
    "name": "Old Omni",
    "type": "commercial_omni_6dbi",
    "frequency_hz": 915_000_000,
    "solver": "rapido",
    "geometry": {"length_m": 0.25},
}

FULL_SPEC_MONOPOLO = {
    "schema_version": "2.0",
    "id": "cccc-0003",
    "name": "Full Monopolo",
    "type": "monopolo",
    "frequency_hz": 915_000_000,
    "solver": "rapido",
    "hpbw_deg": 55.0,
    "polarization": "linear vertical",
    "is_directional": False,
    "gmax_dbi": 5.15,
    "pattern_model": "monopole",
    "practicality_score": 7.0,
    "multi_direction_score": 8.0,
}

SPEC_UNKNOWN_TYPE = {
    "schema_version": "1.0",
    "id": "dddd-0004",
    "name": "Unknown",
    "type": "patch_array",
    "frequency_hz": 2_400_000_000,
    "solver": "rapido",
}


# ── tests ─────────────────────────────────────────────────────────────────────

class TestDryRun:
    def test_reports_would_write_for_old_spec(self, tmp_path: Path):
        _write_spec(tmp_path / "aaaa-0001.json", OLD_SPEC_DIPOLO)
        r = backfill_mod._process(tmp_path / "aaaa-0001.json", write=False)
        assert r["status"] == "would_write"
        assert "hpbw_deg" in r["changes"]
        assert "polarization" in r["changes"]
        assert "gmax_dbi" in r["changes"]

    def test_dry_run_does_not_modify_file(self, tmp_path: Path):
        p = tmp_path / "aaaa-0001.json"
        _write_spec(p, OLD_SPEC_DIPOLO)
        original_text = p.read_text()
        backfill_mod._process(p, write=False)
        assert p.read_text() == original_text

    def test_skips_already_complete_spec(self, tmp_path: Path):
        p = tmp_path / "cccc-0003.json"
        _write_spec(p, FULL_SPEC_MONOPOLO)
        r = backfill_mod._process(p, write=False)
        assert r["status"] == "skip"

    def test_skips_unknown_type(self, tmp_path: Path):
        p = tmp_path / "dddd-0004.json"
        _write_spec(p, SPEC_UNKNOWN_TYPE)
        r = backfill_mod._process(p, write=False)
        assert r["status"] == "skip"
        assert "patch_array" in r["reason"]


class TestWrite:
    def test_writes_physical_fields_for_old_spec(self, tmp_path: Path):
        p = tmp_path / "aaaa-0001.json"
        _write_spec(p, OLD_SPEC_DIPOLO)
        r = backfill_mod._process(p, write=True)
        assert r["status"] == "written"
        data = _read_spec(p)
        assert data["hpbw_deg"] == pytest.approx(78.0)
        assert data["polarization"] == "linear vertical"
        assert data["gmax_dbi"] == pytest.approx(2.15)
        assert data["schema_version"] == "2.0"

    def test_preserves_geometry_on_write(self, tmp_path: Path):
        p = tmp_path / "bbbb-0002.json"
        _write_spec(p, OLD_SPEC_OMNI)
        backfill_mod._process(p, write=True)
        data = _read_spec(p)
        assert data["geometry"] == {"length_m": 0.25}

    def test_preserves_existing_physical_fields(self, tmp_path: Path):
        partial = {**OLD_SPEC_DIPOLO, "hpbw_deg": 90.0}
        p = tmp_path / "partial.json"
        _write_spec(p, partial)
        backfill_mod._process(p, write=True)
        data = _read_spec(p)
        assert data["hpbw_deg"] == pytest.approx(90.0)

    def test_no_write_when_nothing_to_fill(self, tmp_path: Path):
        p = tmp_path / "cccc-0003.json"
        _write_spec(p, FULL_SPEC_MONOPOLO)
        original_text = p.read_text()
        backfill_mod._process(p, write=True)
        assert p.read_text() == original_text


class TestMainCLI:
    def test_main_dry_run_returns_0(self, tmp_path: Path):
        _write_spec(tmp_path / "aaaa-0001.json", OLD_SPEC_DIPOLO)
        rc = backfill_mod.main(["--data-dir", str(tmp_path)])
        assert rc == 0

    def test_main_write_modifies_files(self, tmp_path: Path):
        _write_spec(tmp_path / "aaaa-0001.json", OLD_SPEC_DIPOLO)
        rc = backfill_mod.main(["--data-dir", str(tmp_path), "--write"])
        assert rc == 0
        data = _read_spec(tmp_path / "aaaa-0001.json")
        assert data["hpbw_deg"] is not None

    def test_main_missing_dir_returns_1(self):
        rc = backfill_mod.main(["--data-dir", "/nonexistent/path/xyz"])
        assert rc == 1

    def test_main_empty_dir_returns_0(self, tmp_path: Path):
        rc = backfill_mod.main(["--data-dir", str(tmp_path)])
        assert rc == 0

    def test_main_invalid_json_reports_error(self, tmp_path: Path):
        (tmp_path / "bad.json").write_text("{invalid}", encoding="utf-8")
        rc = backfill_mod.main(["--data-dir", str(tmp_path)])
        assert rc == 0
