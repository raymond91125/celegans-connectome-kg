"""Run the feeding-pathway SPARQL queries against the CIRCE knowledge graph.

The entire analysis is SPARQL: each `queries/*.rq` is a self-contained SELECT over the built graph
(`outputs/connectome.ttl`), runnable as-is against any CIRCE SPARQL endpoint (e.g. the local
`circe-sparql` service) or, as here, an embedded in-process store. This runner loads the Turtle into
Oxigraph -- the same engine `cckg verify` uses -- executes every query, and writes `results.json`.
No pandas, no post-hoc graph munging: the KG answers the questions.

Determinism: every query carries its own ORDER BY, so results are stable and independent of
PYTHONHASHSEED. The one derived quantity is the rank of AIN/ASI/AVK in query 01's ordered output,
computed here by position (plain interpretation of the query result).

Run:  uv run python analysis/feeding_pathways/run_queries.py
"""

from __future__ import annotations

import json
from pathlib import Path

from pyoxigraph import RdfFormat, Store

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TTL = REPO / "outputs" / "connectome.ttl"
QUERIES = HERE / "queries"

FOCAL = ("AVK", "ASI", "AIN")  # the extra-pharyngeal "feeding" neurons (Atanas et al. 2023)


def run(store: Store, sparql: str) -> list[dict[str, str]]:
    result = store.query(sparql)
    names = [v.value for v in result.variables]
    return [{n: (s[n].value if s[n] is not None else None) for n in names} for s in result]


def focal_ranks(baseline_rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    """Rank (1-based position) of each feeding neuron in the ordered baseline ranking."""
    order = [r["srcClass"] for r in baseline_rows]
    out = {}
    for c in FOCAL:
        if c in order:
            i = order.index(c)
            out[c] = {
                "rank": i + 1,
                "pharyngealTargets": int(baseline_rows[i]["pharyngealTargets"]),
            }
    return out


def main() -> None:
    if not TTL.exists():
        raise SystemExit(f"missing {TTL} -- run `uv run cckg export` first")
    store = Store()
    store.load(TTL.read_bytes(), format=RdfFormat.TURTLE)

    results: dict[str, object] = {}
    for rq in sorted(QUERIES.glob("*.rq")):
        results[rq.stem] = run(store, rq.read_text())

    # Derived: where the three feeding neurons fall in the baseline ranking.
    baseline = results["01_baseline_pharyngeal_projection"]
    results["_derived_baseline_focal_ranks"] = focal_ranks(baseline)
    results["_derived_baseline_total_classes"] = len(baseline)

    (HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    # Console summary.
    print(f"baseline: {len(baseline)} extra-pharyngeal classes project to the pharynx via NP")
    for c, v in results["_derived_baseline_focal_ranks"].items():
        print(f"  {c}: rank {v['rank']} ({v['pharyngealTargets']} pharyngeal targets)")
    print("AVK <-> AIN/ASI edges by type:")
    for r in results["02_avk_proximity"]:
        print(f"  {r['type']}: {r['edges']}")
    print("feeding NP channels (source -> target  ligand->receptor  EC50 nM):")
    for r in results["03_feeding_np_channels"]:
        print(
            f"  {r['srcClass']} -> {r['tgtClass']}  {r['ligand']}->{r['receptor']}  {r['ec50_nm']}"
        )
    print("channel specificity (ligand: broadcasting classes):")
    for r in results["04_channel_specificity"]:
        print(f"  {r['ligand']}: {r['senderClasses']}")
    ain_edges = {
        (r["preClass"], r["postClass"], r["type"])
        for r in results["05_motor_cluster_edges"]
        if "AIN" in (r["preClass"], r["postClass"])
    }
    ain_nonpeptide = {e for e in ain_edges if e[2] != "neuropeptidergic"}
    print(f"AIN non-peptidergic edges within MC/M3/M4/AIN: {ain_nonpeptide or 'NONE'}")


if __name__ == "__main__":
    main()
