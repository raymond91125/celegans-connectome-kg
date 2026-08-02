#!/usr/bin/env python3
"""Reconstruct + validate per-edge monoamine->receptor attribution for the Ripoll-Sanchez 2023
monoamine connectome, and emit the vendored mechanistic files this directory holds.

Why this exists
---------------
The base monoamine layer ([../MANIFEST.md](../MANIFEST.md)) ingests the network as edges weighted
by the number of monoamine-receptor pathways. This mechanistic layer adds *which* pairs mediate
each edge -- the analogue of the neuropeptide ``mechanistic/edge_pairs.csv``. Unlike the
neuropeptide network, the paper ships no per-pair monoamine matrices to read the attribution from
(only the aggregate ``08062023_monoamine_connectome.csv``), so we reconstruct it from first
principles and prove it faithful.

Method (mirrors the paper's ``Network_building``)
-------------------------------------------------
An edge source->target for pair (monoamine m, receptor r) exists iff the source PRODUCES m and the
target EXPRESSES r; the published weight is the count of such pairs. The receptor side is the
binarized CeNGEN threshold-4 expression (the ``MR`` genes of that matrix), which we have. The
producer side -- the paper's monoamine-production table (Pereira et al. 2015) -- is NOT in the
Ripoll repo, so instead of assuming it we RECOVER each source's monoamine: a source's observed
out-edge weight profile equals, for exactly one monoamine m, the per-target count of m's receptors
the target expresses. Reproducing every published weight is the validation; the recovered
source->monoamine map is independently cross-checked against canonical aminergic identity.

Result (see MANIFEST): 2,881 / 2,881 edges reproduced, every weight exact, 0 mismatches; all 19
sources recovered uniquely with 0 conflicts vs. the canonical identities. So the emitted
``edge_pairs.csv`` is a faithful decomposition, not an estimate.

Reproducing
-----------
Requires a checkout of the source repo (github.com/LidiaRipollSanchez/Neuropeptide-Connectome);
point RIPOLL_REPO at it. Deterministic; no network access, no randomness.

    RIPOLL_REPO=/path/to/Neuropeptide-Connectome python3 reconstruct.py

Writes edge_pairs.csv, monoamine_receptor_genes.csv, monoamine_receptor_expression.csv next to it,
with cell names normalized to CIRCE (DA01->DA1). Exits non-zero if validation is not exact.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("RIPOLL_REPO", "/home/raymond/local/src/git/Neuropeptide-Connectome"))
CENGEN = REPO / "Scripts & data" / "30072020_CENGEN_threshold4_expression_NPP_NPR_MR_LGC_allneurons.csv"
AGG = REPO / "Adjacency matrices for networks" / "08062023_monoamine_connectome.csv"

# The 14 Bentley et al. 2016 monoamine->receptor pairs (order matches ../monoamine_pairs.csv),
# receptor gene symbol resolved to its WormBase gene id. The 0-mismatch validation below is what
# ultimately confirms each WBGene: a wrong id would not reproduce the published expression/weights.
#   (pair_index, monoamine, receptor, wbgene, wbgene_source)
PAIRS = [
    (1, "Ser", "ser-1", "WBGene00004776", "mygene-wormbase"),
    (2, "Ser", "ser-4", "WBGene00004779", "circe-existing"),
    (3, "Ser", "ser-5", "WBGene00008890", "mygene-wormbase"),
    (4, "Ser", "ser-7", "WBGene00004780", "circe-existing"),
    (5, "DA", "dop-1", "WBGene00001052", "mygene-wormbase"),
    (6, "DA", "dop-2", "WBGene00001053", "mygene-wormbase"),
    (7, "DA", "dop-3", "WBGene00020506", "mygene-wormbase"),
    (8, "DA", "dop-4", "WBGene00016872", "circe-existing"),
    (9, "Oct", "octr-1", "WBGene00006411", "mygene-wormbase"),
    (10, "Oct", "ser-3", "WBGene00004778", "mygene-wormbase"),
    (11, "Oct", "ser-6", "WBGene00021897", "mygene-wormbase"),
    (12, "Tyr", "ser-2", "WBGene00004777", "circe-existing"),
    (13, "Tyr", "tyra-2", "WBGene00017157", "circe-existing"),
    (14, "Tyr", "tyra-3", "WBGene00006475", "mygene-wormbase"),
]
MONOAMINES = ["Ser", "DA", "Oct", "Tyr"]
RECEPTORS_OF = {m: [p for p in PAIRS if p[1] == m] for m in MONOAMINES}

# Canonical aminergic identities (Loer & Rand, WormAtlas; also stated in ../MANIFEST.md), by class.
CANON = {c: "DA" for c in ("ADE", "CEP", "PDE")}
CANON.update({c: "Ser" for c in ("ADF", "NSM", "HSN", "I5")})
CANON["RIM"] = "Tyr"
CANON["RIC"] = "Oct"

_PAD = re.compile(r"^([A-Za-z]+)0(\d)$")


def norm(name: str) -> str:
    """CIRCE cell-name normalization, identical to the ingest layer (DA01->DA1)."""
    m = _PAD.match(name.strip())
    return f"{m.group(1)}{m.group(2)}" if m else name.strip()


def klass(name: str) -> str:
    return re.sub(r"[LR]?[DV]?[LR]?$", "", name) or name


def load_receptor_expression() -> dict[str, set[str]]:
    with open(CENGEN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter=";"))
    neurons = rows[0][1:]
    wb_row = {r[0]: r[1:] for r in rows[1:]}
    expr: dict[str, set[str]] = {}
    for _, _, rsym, g, _ in PAIRS:
        row = wb_row.get(g)
        if row is None:
            sys.exit(f"FATAL: receptor {rsym} {g} is not a row in the CeNGEN matrix")
        expr[rsym] = {neurons[i] for i, v in enumerate(row) if v not in ("0", "", "0.0")}
    return expr


def load_published_network() -> tuple[list[str], dict[str, dict[str, int]]]:
    with open(AGG, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter=","))
    targets = rows[0][1:]
    observed: dict[str, dict[str, int]] = {}
    for r in rows[1:]:
        d = {targets[i]: int(v) for i, v in enumerate(r[1:]) if v not in ("0", "")}
        if d:
            observed[r[0]] = d
    return targets, observed


def main() -> int:
    recept_expr = load_receptor_expression()
    targets, observed = load_published_network()

    def predict(amine: str) -> dict[str, int]:
        return {
            t: sum(1 for _, _, rsym, _, _ in RECEPTORS_OF[amine] if t in recept_expr[rsym])
            for t in targets
            if any(t in recept_expr[rsym] for _, _, rsym, _, _ in RECEPTORS_OF[amine])
        }

    predicted = {m: predict(m) for m in MONOAMINES}

    # recover each source's monoamine by exact match of its observed out-profile
    recovered: dict[str, str] = {}
    ambiguous, unmatched = [], []
    for src, obs in observed.items():
        matches = [m for m in MONOAMINES if predicted[m] == obs]
        if len(matches) == 1:
            recovered[src] = matches[0]
        elif not matches:
            unmatched.append(src)
        else:
            ambiguous.append((src, matches))

    # validate: exact weight reproduction + canonical cross-check
    n_edges = sum(len(v) for v in observed.values())
    mismatch = 0
    for src, obs in observed.items():
        m = recovered.get(src)
        if m is None:
            mismatch += len(obs)
            continue
        pred = predicted[m]
        mismatch += sum(1 for k in set(pred) | set(obs) if pred.get(k, 0) != obs.get(k, 0))
    conflicts = [
        (s, m, CANON[klass(s)])
        for s, m in recovered.items()
        if klass(s) in CANON and CANON[klass(s)] != m
    ]

    print(f"sources={len(observed)} edges={n_edges} recovered={len(recovered)} "
          f"ambiguous={len(ambiguous)} unmatched={len(unmatched)} "
          f"weight_mismatches={mismatch} canonical_conflicts={len(conflicts)}")
    if mismatch or ambiguous or unmatched or conflicts:
        print("VALIDATION FAILED:", {"ambiguous": ambiguous, "unmatched": unmatched,
                                      "conflicts": conflicts})
        return 1

    # emit vendored files (CIRCE-normalized), deterministically ordered
    edge_rows = []
    for src in sorted(observed, key=lambda s: norm(s)):
        m = recovered[src]
        for tgt in sorted(observed[src], key=lambda t: norm(t)):
            for pidx, _, rsym, _, _ in RECEPTORS_OF[m]:
                if tgt in recept_expr[rsym]:
                    edge_rows.append((norm(src), norm(tgt), pidx))
    with open(HERE / "edge_pairs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "pair_index"])
        w.writerows(edge_rows)

    with open(HERE / "monoamine_receptor_genes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "wbgene", "category", "wbgene_source"])
        seen = set()  # de-dup receptors shared across monoamines (none currently, but be safe)
        for _, _, rsym, g, gsrc in PAIRS:
            if rsym in seen:
                continue
            seen.add(rsym)
            w.writerow([rsym, f"WB:{g}", "monoamine_receptor", gsrc])

    expr_rows = sorted(
        {(norm(cell), rsym) for rsym, cells in recept_expr.items() for cell in cells
         if norm(cell) in {norm(t) for t in targets}},
        key=lambda x: (x[0], x[1]),
    )
    with open(HERE / "monoamine_receptor_expression.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "gene_symbol"])
        w.writerows(expr_rows)

    print(f"wrote edge_pairs.csv ({len(edge_rows)} rows), "
          f"monoamine_receptor_genes.csv (14), "
          f"monoamine_receptor_expression.csv ({len(expr_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
