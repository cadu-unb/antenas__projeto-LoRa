from fastapi import APIRouter, HTTPException, Response

from ..workers.job_queue import job_queue

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("")
def list_jobs() -> list[dict]:
    return [j.to_dict() for j in job_queue.list_all()]


@router.get("/{job_id}")
def get_job(job_id: str) -> dict:
    job = job_queue.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job.to_dict()


@router.delete("/{job_id}", status_code=204)
def cancel_job(job_id: str) -> Response:
    ok = job_queue.cancel(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job não encontrado ou já finalizado.")
    return Response(status_code=204)
