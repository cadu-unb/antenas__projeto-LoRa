"""Fila de jobs assíncrona para simulações pesadas.

Usa asyncio.Queue — single-process, single-worker. Celery seria alternativa
para escala multi-processo, mas asyncio basta para o MVP (ver relatório).
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .resource_guard import ResourceGuard, ResourceLimitError

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED_MEMORY_LIMIT = "FAILED_MEMORY_LIMIT"
    FAILED_TIME_LIMIT = "FAILED_TIME_LIMIT"
    CANCELLED = "CANCELLED"


@dataclass
class Job:
    id: str
    _coro_fn: Callable  # (set_progress: Callable[[int], None]) -> Coroutine
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    _cancel_requested: bool = field(default=False, repr=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class JobQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[Job] = asyncio.Queue()
        self._jobs: dict[str, Job] = {}

    def enqueue(self, coro_fn: Callable) -> str:
        """Cria job, enfileira e retorna job_id imediatamente.

        coro_fn: async callable com assinatura (set_progress: Callable[[int], None]) -> Any.
        set_progress(pct) atualiza progresso de 0-99; levantar CancelledError cancela o job.
        """
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, _coro_fn=coro_fn)
        self._jobs[job_id] = job
        self._queue.put_nowait(job)
        logger.info("Job %s enqueued", job_id)
        return job_id

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def list_all(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    def cancel(self, job_id: str) -> bool:
        """Solicita cancelamento. False se job não existe ou já finalizou."""
        job = self._jobs.get(job_id)
        if job is None:
            return False
        if job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
            return False
        job._cancel_requested = True
        logger.info("Job %s cancel requested", job_id)
        return True

    async def _run_job(self, job: Job) -> None:
        guard = ResourceGuard(job.id)

        def set_progress(pct: int) -> None:
            if job._cancel_requested:
                raise asyncio.CancelledError("cancelado pelo usuário")
            job.progress = max(0, min(99, pct))

        try:
            guard.check_ram()
            result = await guard.run_guarded(job._coro_fn(set_progress))
            if job._cancel_requested:
                job.status = JobStatus.CANCELLED
                job.error = "Simulação cancelada pelo usuário."
            else:
                job.result = result
                job.status = JobStatus.DONE
                job.progress = 100
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.error = "Simulação cancelada pelo usuário."
        except ResourceLimitError as e:
            job.status = JobStatus(e.code)
            job.error = e.message
        except Exception as e:
            job.status = JobStatus.FAILED_TIME_LIMIT
            job.error = (
                f"Erro inesperado durante simulação: {e}. "
                "Verifique os parâmetros e tente novamente."
            )
            logger.exception("Job %s failed with unexpected error", job.id)
        finally:
            job.finished_at = time.time()

    async def start_worker(self) -> None:
        """Loop do worker. Iniciar via asyncio.create_task() no startup da app."""
        logger.info("Job worker started")
        while True:
            job = await self._queue.get()
            try:
                if job._cancel_requested:
                    job.status = JobStatus.CANCELLED
                    job.finished_at = time.time()
                    logger.info("Job %s skipped (cancelled before start)", job.id)
                    continue

                job.status = JobStatus.RUNNING
                job.started_at = time.time()
                logger.info("Job %s started", job.id)
                await self._run_job(job)
                logger.info("Job %s finished: %s", job.id, job.status.value)
            except Exception:
                logger.exception("Unexpected worker loop error for job %s", job.id)
            finally:
                self._queue.task_done()


job_queue = JobQueue()
