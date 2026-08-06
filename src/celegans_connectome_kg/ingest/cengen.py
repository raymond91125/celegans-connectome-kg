"""Ingest CeNGEN single-cell expression projected as plain Gene + GeneExpression records.

A minimal source-agnostic reader pair for the ``symbol,wbgene,category`` gene table and the
``cell,gene_symbol`` per-neuron expression list emitted by a CeNGEN threshold-4 projection (e.g.
``data/cengen-monoamine-ionotropic/``). Unlike the monoamine/neuropeptide mechanistic layers, there
is no network or receptor pairing here — just expression. The build turns these into ``Gene`` nodes
(keyed by WBGene, so they de-dupe against shared gene nodes) and per-cell ``GeneExpression`` records
via the shared expression builder.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExpressionGene:
    """A gene of a CeNGEN expression projection, resolved to WormBase."""

    symbol: str
    wbgene: str
    category: str


def read_gene_table(csv_path: Path) -> dict[str, ExpressionGene]:
    """Read a ``symbol,wbgene,category[,...]`` gene table into {symbol: ExpressionGene}."""
    out: dict[str, ExpressionGene] = {}
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            out[r["symbol"].strip()] = ExpressionGene(
                symbol=r["symbol"].strip(),
                wbgene=r["wbgene"].strip(),
                category=r["category"].strip(),
            )
    return out


def read_expression(csv_path: Path) -> list[tuple[str, str]]:
    """Read a ``cell,gene_symbol`` expression list into (cell, gene_symbol) records."""
    with open(csv_path, newline="") as f:
        return [(r["cell"].strip(), r["gene_symbol"].strip()) for r in csv.DictReader(f)]
