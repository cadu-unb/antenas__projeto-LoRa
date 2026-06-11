import math

import pytest

from lora_antenna.antenna.base import Antenna
from lora_antenna.propagation.batch import (
    LinkBatchRequest,
    ScalarLinkInput,
    execute_link_batch,
)


def _scalar(origin: str, dest: str, distance_m: float = 399.0) -> ScalarLinkInput:
    return ScalarLinkInput(
        origin_label=origin,
        dest_label=dest,
        distance_m=distance_m,
        distance_3d_m=distance_m,
        total_extra_loss_db=0.0,
    )


def _antenna() -> Antenna:
    return Antenna(gain_dbi=2.15)


def test_feasible_invariant_single_link():
    req = LinkBatchRequest(
        pairs=[_scalar("P1", "P2")],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    results = execute_link_batch(req)
    r = results[0]
    assert r.feasible == (r.link_margin_db > 0.0)


def test_sir_infinity_single_link():
    req = LinkBatchRequest(
        pairs=[_scalar("P1", "P2")],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    results = execute_link_batch(req)
    r = results[0]
    assert r.sir_db == math.inf
    assert r.sir_decodable is True


def test_sir_finite_with_two_origins():
    req = LinkBatchRequest(
        pairs=[_scalar("P1", "P3"), _scalar("P2", "P3")],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    results = execute_link_batch(req)
    for r in results:
        assert r.sir_db != math.inf


def test_result_count_matches_pairs():
    pairs = [_scalar("P1", "P2"), _scalar("P1", "P3"), _scalar("P2", "P3")]
    req = LinkBatchRequest(
        pairs=pairs,
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    results = execute_link_batch(req)
    assert len(results) == 3


def test_extra_loss_reduces_received_power():
    req_no_loss = LinkBatchRequest(
        pairs=[_scalar("P1", "P2")],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    req_with_loss = LinkBatchRequest(
        pairs=[
            ScalarLinkInput(
                origin_label="P1",
                dest_label="P2",
                distance_m=399.0,
                distance_3d_m=399.0,
                total_extra_loss_db=10.0,
            )
        ],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    r_no_loss = execute_link_batch(req_no_loss)[0]
    r_with_loss = execute_link_batch(req_with_loss)[0]
    assert r_no_loss.received_power_dbm > r_with_loss.received_power_dbm


def test_results_sorted_decodable_first():
    req = LinkBatchRequest(
        pairs=[_scalar("P1", "P3"), _scalar("P2", "P3")],
        antenna=_antenna(),
        frequency_hz=915_200_000.0,
    )
    results = execute_link_batch(req)
    decodable_flags = [r.sir_decodable for r in results]
    true_count = sum(1 for f in decodable_flags if f)
    false_count = sum(1 for f in decodable_flags if not f)
    # decodable entries come before non-decodable ones
    assert decodable_flags == [True] * true_count + [False] * false_count
