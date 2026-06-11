"""Scalar propagation and interference calculations."""

from lora_antenna.propagation.batch import (
    LinkBatchRequest,
    LinkBatchResult,
    LinkPair,
    ScalarLinkInput,
)
from lora_antenna.propagation.friis import LinkRisk

__all__ = [
    "LinkBatchRequest",
    "LinkBatchResult",
    "LinkPair",
    "LinkRisk",
    "ScalarLinkInput",
]
