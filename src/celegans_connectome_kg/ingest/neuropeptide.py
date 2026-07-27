"""Ingest the Ripoll-Sánchez et al. 2023 neuropeptidergic connectome (Neuron 111:3570).

A predicted extrasynaptic ("wireless") signaling network: a directed edge source->target where the
source expresses a neuropeptide precursor and the target a cognate GPCR, for a biochemically
validated NPP-GPCR pair (CeNGEN threshold-4 expression + EC50 <= 500 nM). Three range models
(short/mid/long) reflect assumed peptide diffusion distance.

Each vendored file is a labeled 302x302 directed weighted adjacency matrix (row = source, column =
target, weight = number of NPP-GPCR pathways). Zero-padded motor-neuron names (``DA01``) are
normalized to CIRCE names (``DA1``). This module only parses; the build mints Connection records
with connection_type ``neuropeptidergic``.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from celegans_connectome_kg.ingest.neuron_graph import ConnectionRecord

#: Zero-padded serial motor-neuron names in the matrix (DA01, VD09) -> CIRCE form (DA1, VD9).
_PAD = re.compile(r"^([A-Za-z]+)0(\d)$")


def _norm(name: str) -> str:
    n = name.strip()
    m = _PAD.match(n)
    return f"{m.group(1)}{m.group(2)}" if m else n


@dataclass(frozen=True)
class NeuropeptideNetwork:
    connections: list[ConnectionRecord]
    dataset_id: str
    dataset_name: str
    dataset_description: str
    sex: str


def read_neuropeptide_network(
    csv_path: Path, dataset_id: str, dataset_name: str, dataset_description: str
) -> NeuropeptideNetwork:
    """Read one range-model adjacency matrix into directed weighted ConnectionRecords."""
    rows = list(csv.reader(open(csv_path, newline="")))
    targets = [_norm(x) for x in rows[0][1:]]
    conns: list[ConnectionRecord] = []
    for r in rows[1:]:
        src = _norm(r[0])
        for j, val in enumerate(r[1:]):
            w = int(val) if val not in ("", None) else 0
            if w > 0:
                conns.append(
                    ConnectionRecord(
                        dataset_id=dataset_id,
                        pre=src,
                        post=targets[j],
                        connection_type="neuropeptidergic",
                        weight=float(w),
                        syn=(),
                        ids=None,
                        pre_tid=None,
                        post_tid=None,
                    )
                )
    return NeuropeptideNetwork(
        conns, dataset_id, dataset_name, dataset_description, "hermaphrodite"
    )
