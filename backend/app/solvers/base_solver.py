from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


class SolverResult(BaseModel):
    """Resultado unificado de qualquer solver EM ou de propagação."""

    gain_dbi: float
    impedance_ohm: float
    swr: float
    efficiency_pct: float
    radiation_pattern: str
    solver_used: str = "analítico"
    warning: Optional[str] = None
    extra: dict = Field(default_factory=dict)


class BaseSolver(ABC):
    """Contrato base para solvers EM e de propagação.

    Implementações:
    - MoMSolver   — Method of Moments via PyNEC (dipolo/monopolo/helicoidal)
    - ApertureSolver — Abertura para parabólica
    - OkumuraHata — Perda empírica de percurso
    - LongleyRice — Perda em terreno irregular

    Regra: se dependência externa ausente, solver deve retornar
    fallback analítico + warning, nunca propagar ImportError.
    """

    @abstractmethod
    def solve(self, spec: Any) -> SolverResult:
        """Computa resultado EM ou de propagação a partir de spec.

        Args:
            spec: Objeto com atributos type, frequency_hz, geometry (dict).
                  Aceita qualquer objeto com getattr; usa valores padrão se ausente.

        Returns:
            SolverResult com ganho, impedância, SWR, eficiência e padrão.
        """
        ...
