"""Phase 2 match tests.

Small synthetic-index tests pin the bucketing rules exactly; a smoke test over the real
pinned WBBT + cell list asserts the matched/ambiguous/unmatched totals from the dry-run.
"""

import csv
import json
from pathlib import Path

from celegans_connectome_kg.ingest.neuron_graph import read_cells
from celegans_connectome_kg.match.matcher import (
    match_cell,
    match_cells,
    summarize,
    write_report_csv,
    write_worklist_csv,
)
from celegans_connectome_kg.match.wbbt import WBBTIndex, normalize

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
WBBT_JSON = DATA_DIR / "wbbt" / "wbbt.json"
NEURONS = DATA_DIR / "neuron-graph" / "neurons.json"


def _obograph(nodes: list[dict]) -> dict:
    return {"graphs": [{"nodes": nodes}]}


def _node(
    local_id: str,
    label: str,
    synonyms: list[tuple[str, str]] | None = None,
    deprecated: bool = False,
) -> dict:
    meta: dict = {}
    if synonyms:
        meta["synonyms"] = [{"pred": pred, "val": val} for pred, val in synonyms]
    if deprecated:
        meta["deprecated"] = True
    return {
        "id": f"http://purl.obolibrary.org/obo/WBbt_{local_id}",
        "lbl": label,
        "type": "CLASS",
        "meta": meta,
    }


def _index(nodes: list[dict], tmp_path: Path) -> WBBTIndex:
    p = tmp_path / "wbbt.json"
    p.write_text(json.dumps(_obograph(nodes)))
    return WBBTIndex.from_obograph(p)


def test_normalize() -> None:
    assert normalize("  ADAL ") == "adal"
    assert normalize("Body  Wall\tMuscle") == "body wall muscle"


def test_label_match_is_confident(tmp_path: Path) -> None:
    idx = _index([_node("0000001", "ADAL")], tmp_path)
    m = match_cell("ADAL", idx)
    assert m.status == "matched" and m.wbbt_id == "WBbt:0000001" and m.match_kind == "label"


def test_exact_synonym_matches(tmp_path: Path) -> None:
    idx = _index([_node("0000002", "some label", synonyms=[("hasExactSynonym", "AVAL")])], tmp_path)
    assert match_cell("AVAL", idx).status == "matched"


def test_only_related_synonym_is_ambiguous(tmp_path: Path) -> None:
    idx = _index(
        [_node("0004742", "pharyngeal cell", synonyms=[("hasRelatedSynonym", "I3")])], tmp_path
    )
    m = match_cell("I3", idx)
    assert m.status == "ambiguous" and m.wbbt_id is None
    assert "weak synonym" in m.reason


def test_multiple_strong_matches_is_ambiguous(tmp_path: Path) -> None:
    idx = _index([_node("0000003", "DUP"), _node("0000004", "DUP")], tmp_path)
    m = match_cell("DUP", idx)
    assert m.status == "ambiguous" and "strong matches" in m.reason


def test_no_hit_is_unmatched(tmp_path: Path) -> None:
    idx = _index([_node("0000005", "ADAL")], tmp_path)
    assert match_cell("BWM-DL01", idx).status == "unmatched"


def test_deprecated_terms_are_skipped(tmp_path: Path) -> None:
    idx = _index([_node("0000006", "ZZZ", deprecated=True)], tmp_path)
    assert "WBbt:0000006" not in idx.terms
    assert match_cell("ZZZ", idx).status == "unmatched"


def test_real_snapshot_bucket_totals() -> None:
    index = WBBTIndex.from_obograph(WBBT_JSON)
    cells = read_cells(NEURONS)
    counts = summarize(match_cells(cells, index))
    assert counts["matched"] == 333
    assert counts["ambiguous"] == 8
    assert counts["unmatched"] == 106
    assert sum(counts.values()) == 447


def test_report_and_worklist_written(tmp_path: Path) -> None:
    index = WBBTIndex.from_obograph(WBBT_JSON)
    cells = read_cells(NEURONS)
    matches = match_cells(cells, index)

    report = tmp_path / "match_report.csv"
    worklist = tmp_path / "match_worklist.csv"
    write_report_csv(matches, report)
    write_worklist_csv(matches, cells, worklist)

    report_rows = list(csv.DictReader(report.open()))
    assert len(report_rows) == 447
    worklist_rows = list(csv.DictReader(worklist.open()))
    # Work-list holds only the ambiguous + unmatched tail.
    assert len(worklist_rows) == 8 + 106
    assert all(r["status"] != "matched" for r in worklist_rows)
    assert "resolved_wbbt_id" in worklist_rows[0]
