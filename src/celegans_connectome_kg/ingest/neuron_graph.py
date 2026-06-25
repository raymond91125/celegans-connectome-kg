"""Phase 2 ingest: read pinned neuron-graph files into normalized records.

This stage is deliberately faithful — it normalizes shapes and decodes the ``typ`` code
and weight, but makes no biological judgements (e.g. neuron vs. muscle) and applies no
graph-level rules (e.g. gap-junction reverse dedup). Those belong to match/build.

Source layout (pinned under ``data/neuron-graph/``; see that dir's MANIFEST.md):
  - ``neurons.json``         — cell list
  - ``datasets.json``        — dataset/specimen metadata
  - ``connections/*.json``   — connection records; the dataset id is the file stem

Connection ``typ`` encoding (from neuron-graph ``populate-connections.js``):
  0 = chemical, 2 = electrical / gap junction, 4 = functional.
Weight mirrors neuron-graph: functional → ``round(sum(syn))``; otherwise ``len(syn)``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

#: neuron-graph ``typ`` code → our connection-type label (matches the LinkML enum).
CONNECTION_TYPE_BY_CODE: dict[int, str] = {0: "chemical", 2: "gap_junction", 4: "functional"}


@dataclass(frozen=True)
class CellRecord:
    """A cell as carried by neuron-graph's ``neurons.json`` (raw fields preserved)."""

    name: str
    cell_class: str | None
    neurotransmitter: str | None
    nemanode_type: str | None
    embryonic: bool | None
    in_head: bool | None
    in_tail: bool | None


@dataclass(frozen=True)
class DatasetRecord:
    """A dataset/specimen from ``datasets.json``."""

    id: str
    name: str
    type: str | None
    time: float | None
    visual_time: float | None
    description: str | None
    datatypes: str | None


@dataclass(frozen=True)
class ConnectionRecord:
    """A single observed connection, with ``dataset_id`` attached from the file stem.

    ``syn`` is preserved verbatim (the per-contact array) so a later release can promote it
    to individual-synaptic-contact evidence without re-ingesting.
    """

    dataset_id: str
    pre: str
    post: str
    connection_type: str
    weight: float
    syn: tuple[float, ...]
    ids: tuple[int, ...] | None
    pre_tid: tuple[int, ...] | None
    post_tid: tuple[int, ...] | None


@dataclass(frozen=True)
class NeuronGraphData:
    """The full ingested bundle from one pinned neuron-graph snapshot."""

    cells: list[CellRecord]
    datasets: list[DatasetRecord]
    connections: list[ConnectionRecord]


def _as_bool(value: object) -> bool | None:
    """neuron-graph encodes flags as 0/1 ints; normalize to bool (None if absent)."""
    return None if value is None else bool(value)


def read_cells(path: Path) -> list[CellRecord]:
    """Read ``neurons.json`` into :class:`CellRecord` objects."""
    raw = json.loads(Path(path).read_text())
    return [
        CellRecord(
            name=c["name"],
            cell_class=c.get("classes"),
            neurotransmitter=c.get("nt"),
            nemanode_type=c.get("typ"),
            embryonic=_as_bool(c.get("emb")),
            in_head=_as_bool(c.get("inhead")),
            in_tail=_as_bool(c.get("intail")),
        )
        for c in raw
    ]


def read_datasets(path: Path) -> list[DatasetRecord]:
    """Read ``datasets.json`` into :class:`DatasetRecord` objects."""
    raw = json.loads(Path(path).read_text())
    return [
        DatasetRecord(
            id=d["id"],
            name=d["name"],
            type=d.get("type"),
            time=d.get("time"),
            visual_time=d.get("visualTime"),
            description=d.get("description"),
            datatypes=d.get("datatypes"),
        )
        for d in raw
    ]


def _connection_weight(connection_type: str, syn: list[float]) -> float:
    """Aggregate weight, mirroring neuron-graph's populate-connections logic."""
    if connection_type == "functional":
        return float(round(sum(syn)))
    return float(len(syn))


def read_connections_file(path: Path) -> list[ConnectionRecord]:
    """Read one ``connections/<dataset>.json`` file; dataset id is the file stem."""
    path = Path(path)
    dataset_id = path.stem
    raw = json.loads(path.read_text())
    records: list[ConnectionRecord] = []
    for conn in raw:
        code = conn["typ"]
        connection_type = CONNECTION_TYPE_BY_CODE.get(code)
        if connection_type is None:
            raise ValueError(
                f"{path.name}: unknown connection typ {code!r} for {conn.get('pre')}->{conn.get('post')}"
            )
        syn = conn.get("syn", [])
        ids = conn.get("ids")
        pre_tid = conn.get("pre_tid")
        post_tid = conn.get("post_tid")
        records.append(
            ConnectionRecord(
                dataset_id=dataset_id,
                pre=conn["pre"],
                post=conn["post"],
                connection_type=connection_type,
                weight=_connection_weight(connection_type, syn),
                syn=tuple(syn),
                ids=tuple(ids) if ids is not None else None,
                pre_tid=tuple(pre_tid) if pre_tid is not None else None,
                post_tid=tuple(post_tid) if post_tid is not None else None,
            )
        )
    return records


def read_connections(connections_dir: Path) -> list[ConnectionRecord]:
    """Read every ``*.json`` under ``connections/`` (sorted for determinism)."""
    connections_dir = Path(connections_dir)
    records: list[ConnectionRecord] = []
    for path in sorted(connections_dir.glob("*.json")):
        records.extend(read_connections_file(path))
    return records


def load_neuron_graph(data_dir: Path) -> NeuronGraphData:
    """Load the full pinned snapshot rooted at ``data_dir`` (``data/neuron-graph``)."""
    data_dir = Path(data_dir)
    return NeuronGraphData(
        cells=read_cells(data_dir / "neurons.json"),
        datasets=read_datasets(data_dir / "datasets.json"),
        connections=read_connections(data_dir / "connections"),
    )
