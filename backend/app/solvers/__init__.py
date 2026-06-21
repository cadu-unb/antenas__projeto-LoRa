from .aperture_solver import ApertureSolver
from .base_solver import BaseSolver, SolverResult
from .colinear_solver import ColinearSolver
from .mom_solver import MoMSolver
from .pcb_solver import PcbSolver

_mom = MoMSolver()
_aperture = ApertureSolver()
_pcb = PcbSolver()
_colinear = ColinearSolver()

_REGISTRY: dict[str, BaseSolver] = {
    "dipolo": _mom,
    "monopolo": _mom,
    "helicoidal": _mom,
    "parabolica": _aperture,
    "pcb_compact": _pcb,
    "commercial_omni_6dbi": _colinear,
}


def get_solver(antenna_type: str) -> BaseSolver | None:
    return _REGISTRY.get(antenna_type.lower())
