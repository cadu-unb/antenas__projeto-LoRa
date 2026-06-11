"""Greedy graph coloring for LoRa channel allocation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from lora_antenna.propagation.interference import sir_threshold_db

LORA_CHANNELS_MHZ: tuple[float, ...] = (
    915.2,
    916.8,
    918.4,
    920.0,
    921.6,
    923.2,
    924.8,
    926.4,
)


@dataclass(frozen=True)
class ChannelAssignment:
    """Assigned LoRa channel for one node."""

    node_label: str
    channel_index: int
    channel_mhz: float


def build_interference_graph(
    sir_matrix: Mapping[tuple[str, str], float],
    *,
    nodes: Sequence[str] | None = None,
    sir_threshold_db_value: float | None = None,
    sf: int = 12,
) -> dict[str, set[str]]:
    """Build an undirected graph where edges indicate co-channel conflict."""
    threshold = (
        sir_threshold_db(sf)
        if sir_threshold_db_value is None
        else sir_threshold_db_value
    )
    graph: dict[str, set[str]] = {}

    if nodes is not None:
        graph.update({node: set() for node in nodes})

    for (origin, destination), sir_value in sir_matrix.items():
        graph.setdefault(origin, set())
        graph.setdefault(destination, set())
        if sir_value < threshold:
            graph[origin].add(destination)
            graph[destination].add(origin)

    return graph


def greedy_channel_assignment(
    nodes: Sequence[str],
    interference_graph: Mapping[str, set[str] | list[str] | tuple[str, ...]],
    *,
    channels_mhz: Sequence[float] = LORA_CHANNELS_MHZ,
) -> dict[str, ChannelAssignment]:
    """Assign channels using degree-ordered greedy graph coloring."""
    if not channels_mhz:
        raise ValueError("At least one channel is required.")

    ordered_nodes = sorted(
        nodes,
        key=lambda node: len(interference_graph.get(node, ())),
        reverse=True,
    )
    channel_by_node: dict[str, int] = {}

    for node in ordered_nodes:
        neighbors = set(interference_graph.get(node, ()))
        used_channels = {
            channel_by_node[neighbor]
            for neighbor in neighbors
            if neighbor in channel_by_node
        }

        for channel_index in range(len(channels_mhz)):
            if channel_index not in used_channels:
                channel_by_node[node] = channel_index
                break
        else:
            channel_by_node[node] = _least_conflicting_channel(
                neighbors,
                channel_by_node,
                len(channels_mhz),
            )

    return {
        node: ChannelAssignment(
            node_label=node,
            channel_index=channel_index,
            channel_mhz=channels_mhz[channel_index],
        )
        for node, channel_index in channel_by_node.items()
    }


def count_channel_collisions(
    assignments: Mapping[str, ChannelAssignment],
    interference_graph: Mapping[str, set[str] | list[str] | tuple[str, ...]],
) -> int:
    """Count graph edges whose endpoints still share the same channel."""
    collisions = 0
    seen_edges: set[tuple[str, str]] = set()

    for node, neighbors in interference_graph.items():
        for neighbor in neighbors:
            edge = tuple(sorted((node, neighbor)))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)

            left = assignments.get(node)
            right = assignments.get(neighbor)
            if left is None or right is None:
                continue
            if left.channel_index == right.channel_index:
                collisions += 1

    return collisions


def _least_conflicting_channel(
    neighbors: set[str],
    channel_by_node: Mapping[str, int],
    n_channels: int,
) -> int:
    conflict_counts = [0 for _ in range(n_channels)]
    for neighbor in neighbors:
        channel = channel_by_node.get(neighbor)
        if channel is not None:
            conflict_counts[channel] += 1
    return min(range(n_channels), key=lambda index: conflict_counts[index])
