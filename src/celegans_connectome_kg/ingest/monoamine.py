"""Ingest the Ripoll-Sánchez et al. 2023 monoamine (aminergic) connectome.

The companion predicted network to the neuropeptidergic connectome: a directed edge source->target
where the source produces a monoamine (serotonin / dopamine / octopamine / tyramine) and the target
expresses a cognate GPCR, for a monoamine-receptor pair (Bentley et al. 2016) over CeNGEN receptor
expression. A single aggregate network (no range models); weight = number of monoamine-receptor
pathways. This module only parses; the build mints Connection records with connection_type
``monoaminergic``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from celegans_connectome_kg.ingest.neuron_graph import ConnectionRecord


@dataclass(frozen=True)
class MonoaminePair:
    """One monoamine -> GPCR-receptor pair (Bentley et al. 2016)."""

    index: int
    monoamine: str
    monoamine_name: str
    receptor: str


def read_monoamine_pairs(csv_path: Path) -> list[MonoaminePair]:
    """Read the 14 monoamine-receptor pairs (monoamine_pairs.csv)."""
    out: list[MonoaminePair] = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            out.append(
                MonoaminePair(
                    index=int(r["pair_index"]),
                    monoamine=r["monoamine"].strip(),
                    monoamine_name=r["monoamine_name"].strip(),
                    receptor=r["receptor"].strip(),
                )
            )
    return out


def read_monoamine_network(csv_path: Path, dataset_id: str) -> list[ConnectionRecord]:
    """Read monoamine_network.csv (source, target, weight) into ConnectionRecords.

    Names are already CIRCE-normalized in the vendored file. Directed, weighted; predicted (no
    per-synapse ids).
    """
    conns: list[ConnectionRecord] = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            w = int(r["weight"])
            if w > 0:
                conns.append(
                    ConnectionRecord(
                        dataset_id=dataset_id,
                        pre=r["source"].strip(),
                        post=r["target"].strip(),
                        connection_type="monoaminergic",
                        weight=float(w),
                        syn=(),
                        ids=None,
                        pre_tid=None,
                        post_tid=None,
                    )
                )
    return conns
