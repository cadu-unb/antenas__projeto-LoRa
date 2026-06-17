"""Testes da fila de jobs e rotas /api/v1/jobs."""
import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.workers.job_queue import JobQueue, JobStatus


# ── Unit tests: JobQueue ───────────────────────────────────────────────────────

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def make_queue():
    return JobQueue()


def test_enqueue_returns_job_id():
    q = make_queue()

    async def work(sp):
        return {"value": 42}

    job_id = q.enqueue(work)
    assert isinstance(job_id, str)
    assert len(job_id) == 36  # UUID4


def test_job_pending_after_enqueue():
    q = make_queue()
    job_id = q.enqueue(lambda sp: asyncio.sleep(0))
    job = q.get(job_id)
    assert job is not None
    assert job.status == JobStatus.PENDING


def test_worker_runs_job_to_done(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMULATIONS_DIR", str(tmp_path))
    q = make_queue()

    async def work(sp):
        sp(50)
        return {"answer": 99}

    job_id = q.enqueue(work)

    async def run():
        worker = asyncio.create_task(q.start_worker())
        await asyncio.sleep(0.5)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass

    _run(run())
    job = q.get(job_id)
    assert job.status == JobStatus.DONE
    assert job.result == {"answer": 99}
    assert job.progress == 100


def test_cancel_pending_job():
    q = make_queue()
    long_job_id = q.enqueue(lambda sp: asyncio.sleep(60))
    ok = q.cancel(long_job_id)
    assert ok is True
    assert q.get(long_job_id)._cancel_requested is True


def test_cancel_nonexistent_job():
    q = make_queue()
    ok = q.cancel("does-not-exist")
    assert ok is False


def test_cancel_done_job_returns_false(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMULATIONS_DIR", str(tmp_path))
    q = make_queue()

    async def work(sp):
        return {}

    job_id = q.enqueue(work)

    async def run():
        worker = asyncio.create_task(q.start_worker())
        await asyncio.sleep(0.3)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass

    _run(run())
    assert q.get(job_id).status == JobStatus.DONE
    assert q.cancel(job_id) is False


def test_worker_cancels_job_via_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMULATIONS_DIR", str(tmp_path))
    q = make_queue()

    async def slow_work(sp):
        sp(10)
        await asyncio.sleep(0.5)
        sp(50)  # should raise if cancelled
        await asyncio.sleep(0.5)
        return {}

    job_id = q.enqueue(slow_work)

    async def run():
        worker = asyncio.create_task(q.start_worker())
        await asyncio.sleep(0.05)  # let job start
        q.cancel(job_id)
        await asyncio.sleep(0.8)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass

    _run(run())
    job = q.get(job_id)
    assert job.status == JobStatus.CANCELLED


# ── Integration tests: API routes ─────────────────────────────────────────────

client = TestClient(app)


def test_list_jobs_empty():
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_job_not_found():
    res = client.get("/api/v1/jobs/nonexistent-id")
    assert res.status_code == 404


def test_cancel_job_not_found():
    res = client.delete("/api/v1/jobs/nonexistent-id")
    assert res.status_code == 404


def test_simulate_endpoint_returns_job_id():
    payload = {
        "type": "dipolo",
        "frequency_hz": 915e6,
        "solver": "padrao",
    }
    res = client.post("/api/v1/sandbox/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)


def test_simulate_rapido_rejected():
    payload = {
        "type": "dipolo",
        "frequency_hz": 915e6,
        "solver": "rapido",
    }
    res = client.post("/api/v1/sandbox/simulate", json=payload)
    assert res.status_code == 400


def test_simulate_job_appears_in_list():
    before = {j["id"] for j in client.get("/api/v1/jobs").json()}
    payload = {"type": "dipolo", "frequency_hz": 433e6, "solver": "preciso"}
    job_id = client.post("/api/v1/sandbox/simulate", json=payload).json()["job_id"]
    after = {j["id"] for j in client.get("/api/v1/jobs").json()}
    assert job_id in after - before


def test_get_job_valid_status():
    payload = {"type": "monopolo", "frequency_hz": 868e6, "solver": "padrao"}
    job_id = client.post("/api/v1/sandbox/simulate", json=payload).json()["job_id"]
    job = client.get(f"/api/v1/jobs/{job_id}").json()
    valid_statuses = {"PENDING", "RUNNING", "DONE", "FAILED_MEMORY_LIMIT", "FAILED_TIME_LIMIT", "CANCELLED"}
    assert job["status"] in valid_statuses


def test_cancel_job_via_api():
    payload = {"type": "dipolo", "frequency_hz": 915e6, "solver": "padrao"}
    job_id = client.post("/api/v1/sandbox/simulate", json=payload).json()["job_id"]
    res = client.delete(f"/api/v1/jobs/{job_id}")
    assert res.status_code == 204
