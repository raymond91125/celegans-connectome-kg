"""Emit per-neuron expression for the ionotropic (ligand-gated) monoamine receptors.

CIRCE's monoamine mechanistic layer covers the *metabotropic* (GPCR) monoamine receptors, because
those are the receptor side of the Bentley et al. 2016 monoamine-GPCR pairs that reconstruct the
predicted aminergic network. This companion layer covers the *ionotropic* side: the amine-gated
Cys-loop chloride/cation channels, a small family of ligand-gated ion channels directly opened by
serotonin, dopamine, tyramine, or octopamine. They are not GPCRs and carry no predicted
monoaminergic edges (there is no ionotropic aminergic network to reconstruct), so they enter the KG
as plain ``Gene`` + per-neuron ``GeneExpression`` records -- giving the graph the full aminergic
*receptor* repertoire, metabotropic and ionotropic alike.

The eight channels below are the deorphanized amine-gated Cys-loop receptors from three studies:
  - MOD-1     serotonin (anion)                         Ranganathan et al. 2000, Nature 408:470
  - LGC-40    serotonin (low-aff), choline/ACh (anion)  Ringstad et al. 2009, Science 325:96
  - LGC-53    dopamine (anion)                          Ringstad et al. 2009
  - LGC-55    tyramine (anion)                          Ringstad et al. 2009; Pirri et al. 2009
  - LGC-50    serotonin, tryptamine (cation)            Morud et al. 2021, Curr Biol 31:4282
  - LGC-52    dopamine, tyramine (anion)                Morud et al. 2021
  - LGC-54    dopamine, tyramine, 5-HT[high] (anion)    Morud et al. 2021
  - LGC-56    tyramine, dopamine, octopamine[high]      Morud et al. 2021
LGC-51 (Morud 2021) is deliberately excluded: it has no intrinsic amine response and is an accessory
subunit that only heteromerizes with LGC-52, so it is not itself an amine *receptor*.

The expression substrate is the CeNGEN single-cell RNA-seq binary matrix, threshold 4 (Taylor et al.
2021, Cell 184:4329-4347) -- the ``LGC`` (ligand-gated channel) rows of the vendored
``..._NPP_NPR_MR_LGC_allneurons.csv`` matrix; all eight genes are rows of it. Reads the matrix from
the Ripoll-Sanchez repo (env ``RIPOLL_REPO``), writes ``monoamine_ionotropic_genes.csv`` and
``monoamine_ionotropic_expression.csv`` next to this file. Deterministic against the pinned matrix.

    RIPOLL_REPO=/path/to/Neuropeptide-Connectome python build_expression.py
"""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("RIPOLL_REPO", "/home/raymond/local/src/git/Neuropeptide-Connectome"))
CENGEN = (
    REPO / "Scripts & data" / "30072020_CENGEN_threshold4_expression_NPP_NPR_MR_LGC_allneurons.csv"
)

# The amine-gated Cys-loop receptors, WormBase gene ids resolved via mygene.info (species 6239) and
# confirmed as rows of the CeNGEN matrix below. The ``WB:`` CURIE prefix is the graph's gene-id
# convention. amine_ligand / ion columns are documentary provenance (the KG category is the generic
# ionotropic_receptor for all -- ion selectivity and specific ligand are not modeled as gene slots).
#   (symbol, wbgene, amine_ligand, ion, source, wbgene_source)
GENES = [
    ("mod-1", "WB:WBGene00003386", "serotonin", "anion", "Ranganathan 2000", "mygene-wormbase"),
    (
        "lgc-40",
        "WB:WBGene00020767",
        "serotonin/choline",
        "anion",
        "Ringstad 2009",
        "mygene-wormbase",
    ),
    ("lgc-53", "WB:WBGene00020657", "dopamine", "anion", "Ringstad 2009", "mygene-wormbase"),
    ("lgc-55", "WB:WBGene00013746", "tyramine", "anion", "Ringstad 2009", "mygene-wormbase"),
    ("lgc-50", "WB:WBGene00020605", "serotonin", "cation", "Morud 2021", "mygene-wormbase"),
    ("lgc-52", "WB:WBGene00013517", "dopamine/tyramine", "anion", "Morud 2021", "mygene-wormbase"),
    (
        "lgc-54",
        "WB:WBGene00020528",
        "dopamine/tyramine/serotonin",
        "anion",
        "Morud 2021",
        "mygene-wormbase",
    ),
    (
        "lgc-56",
        "WB:WBGene00001588",
        "tyramine/dopamine/octopamine",
        "anion",
        "Morud 2021",
        "mygene-wormbase",
    ),
]
CATEGORY = "ionotropic_receptor"

_PAD = re.compile(r"^([A-Za-z]+)0(\d)$")


def norm(name: str) -> str:
    """CIRCE cell-name normalization, identical to the ingest layer (DA01->DA1)."""
    m = _PAD.match(name.strip())
    return f"{m.group(1)}{m.group(2)}" if m else name.strip()


def load_expression() -> dict[str, list[str]]:
    """{gene_symbol: sorted list of expressing neurons} from the CeNGEN threshold-4 matrix."""
    with open(CENGEN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter=";"))
    neurons = rows[0][1:]
    wb_row = {r[0]: r[1:] for r in rows[1:]}
    out: dict[str, list[str]] = {}
    for sym, wb, *_ in GENES:
        row = wb_row.get(wb.split(":")[-1])  # matrix is keyed by bare WBGene id
        if row is None:
            sys.exit(f"FATAL: {sym} {wb} is not a row in the CeNGEN matrix")
        cells = {norm(neurons[i]) for i, v in enumerate(row) if v not in ("0", "", "0.0")}
        out[sym] = sorted(cells)
    return out


def main() -> None:
    expr = load_expression()

    with open(HERE / "monoamine_ionotropic_genes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["symbol", "wbgene", "category", "amine_ligand", "ion", "source", "wbgene_source"]
        )
        for sym, wb, lig, ion, src, wsrc in GENES:
            w.writerow([sym, wb, CATEGORY, lig, ion, src, wsrc])

    rows = [(cell, sym) for sym, *_ in GENES for cell in expr[sym]]
    with open(HERE / "monoamine_ionotropic_expression.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "gene_symbol"])
        w.writerows(rows)

    counts = ", ".join(f"{sym}={len(expr[sym])}" for sym, *_ in GENES)
    print(
        f"wrote monoamine_ionotropic_genes.csv ({len(GENES)}), "
        f"monoamine_ionotropic_expression.csv ({len(rows)} rows; {counts})"
    )


if __name__ == "__main__":
    main()
