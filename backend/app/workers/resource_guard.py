"""Guardião de recursos para simulações pesadas.

Aplica limites de RAM (MAX_RAM_GB) e tempo (MAX_RUNTIME_MIN) configurados
em backend/app/config.py. Log parcial gravado em JSONL mesmo em jobs abortados.
"""
import asyncio
import json
import logging
import os
import time
from typing import Any, Coroutine, Optional

import psutil

from ..config import MAX_RAM_GB, MAX_RUNTIME_MIN

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "simulations")
)


class ResourceLimitError(Exception):
    """Levantada quando simulação ultrapassa RAM ou tempo permitidos."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code  # "FAILED_MEMORY_LIMIT" | "FAILED_TIME_LIMIT"
        self.message = message
        super().__init__(message)


class ResourceGuard:
    """Monitor de RAM e timeout para simulações pesadas.

    Uso:
        guard = ResourceGuard("sim-uuid")
        result = await guard.run_guarded(minha_coroutine())

    Log persistido em backend/data/simulations/{sim_id}/log.jsonl.
    Limite de RAM verificado antes de iniciar e periodicamente via callback.
    Limite de tempo via asyncio.wait_for.
    """

    def __init__(
        self,
        sim_id: str,
        _timeout_override_s: Optional[float] = None,
        _ram_override_gb: Optional[float] = None,
    ) -> None:
        self.sim_id = sim_id
        self._timeout_s = _timeout_override_s if _timeout_override_s is not None else MAX_RUNTIME_MIN * 60
        self._ram_override_gb = _ram_override_gb
        self._start: Optional[float] = None

        log_dir = os.path.join(_DATA_DIR, sim_id)
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, "log.jsonl")

    def _log(self, event: str, data: Optional[dict] = None) -> None:
        entry = {"ts": round(time.time(), 3), "event": event, **(data or {})}
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("Falha ao gravar log de simulação: %s", exc)

    def _used_ram_gb(self) -> float:
        if self._ram_override_gb is not None:
            return self._ram_override_gb
        return psutil.virtual_memory().used / 1024**3

    def check_ram(self) -> None:
        """Verifica RAM. Levanta ResourceLimitError se acima do limite."""
        used = self._used_ram_gb()
        if used >= MAX_RAM_GB:
            self._log("FAILED_MEMORY_LIMIT", {"used_gb": round(used, 2), "limit_gb": MAX_RAM_GB})
            raise ResourceLimitError(
                "FAILED_MEMORY_LIMIT",
                f"Limite de memória atingido: {used:.1f} GB usados "
                f"de {MAX_RAM_GB} GB permitidos. "
                "Reduza o tamanho da simulação ou libere memória.",
            )

    def elapsed_min(self) -> float:
        if self._start is None:
            return 0.0
        return (time.time() - self._start) / 60.0

    async def run_guarded(self, coro: Coroutine) -> Any:
        """Executa coroutine com verificação de RAM e timeout.

        Args:
            coro: Coroutine a executar.

        Returns:
            Resultado da coroutine.

        Raises:
            ResourceLimitError com código FAILED_MEMORY_LIMIT ou FAILED_TIME_LIMIT.
        """
        self.check_ram()
        self._start = time.time()
        self._log(
            "START",
            {
                "max_ram_gb": MAX_RAM_GB,
                "max_runtime_min": MAX_RUNTIME_MIN,
                "timeout_s": self._timeout_s,
            },
        )

        try:
            result = await asyncio.wait_for(coro, timeout=self._timeout_s)
            self._log("DONE", {"elapsed_min": round(self.elapsed_min(), 3)})
            return result

        except asyncio.TimeoutError:
            elapsed = self.elapsed_min()
            self._log("FAILED_TIME_LIMIT", {"elapsed_min": round(elapsed, 3), "limit_min": MAX_RUNTIME_MIN})
            raise ResourceLimitError(
                "FAILED_TIME_LIMIT",
                f"Simulação abortada após {elapsed:.1f} min "
                f"(limite: {MAX_RUNTIME_MIN} min). "
                "Tente modo Padrão em vez de Preciso, ou reduza o número de segmentos.",
            )
        except ResourceLimitError:
            raise
        except Exception as exc:
            self._log("ERROR", {"error": str(exc)})
            raise
