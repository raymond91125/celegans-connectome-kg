"""Phase 2 ingest tests.

Two layers: small in-test fixtures that pin the normalization rules exactly (typ decoding,
weight derivation, dataset-id-from-filename), and a smoke test over the real pinned snapshot
asserting the totals recorded in data/neuron-graph/MANIFEST.md.
"""

import json
from pathlib import Path

import pytest

from celegans_connectome_kg.ingest.neuron_graph import (
    CONNECTION_TYPE_BY_CODE,
    load_neuron_graph,
    read_cells,
    read_connections_file,
    read_datasets,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "neuron-graph"


def test_typ_decoding_table() -> None:
    assert CONNECTION_TYPE_BY_CODE == {0: "chemical", 2: "gap_junction", 4: "functional"}


def test_weight_em_is_contact_count_functional_is_summed(tmp_path: Path) -> None:
    f = tmp_path / "demo_dataset.json"
    f.write_text(
        json.dumps(
            [
                {"pre": "A", "post": "B", "typ": 0, "syn": [1, 1, 1]},  # chemical -> len = 3
                {"pre": "A", "post": "C", "typ": 2, "syn": [1, 1]},  # gap_junction -> len = 2
                {
                    "pre": "A",
                    "post": "D",
                    "typ": 4,
                    "syn": [0.4, 0.4, 0.5],
                },  # functional -> round(1.3)=1
            ]
        )
    )
    recs = read_connections_file(f)
    assert [r.dataset_id for r in recs] == ["demo_dataset"] * 3  # id from file stem
    assert [r.connection_type for r in recs] == ["chemical", "gap_junction", "functional"]
    assert [r.weight for r in recs] == [3.0, 2.0, 1.0]
    assert recs[0].syn == (1, 1, 1)  # raw syn preserved


def test_unknown_typ_raises(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text(json.dumps([{"pre": "A", "post": "B", "typ": 9, "syn": [1]}]))
    with pytest.raises(ValueError, match="unknown connection typ"):
        read_connections_file(f)


def test_cell_flags_normalized_to_bool() -> None:
    cells = read_cells(DATA_DIR / "neurons.json")
    assert len(cells) == 447
    adal = next(c for c in cells if c.name == "ADAL")
    assert adal.cell_class == "ADA"
    assert adal.in_head is True and adal.in_tail is False
    assert all(isinstance(c.in_head, bool) for c in cells)


def test_datasets_loaded() -> None:
    datasets = read_datasets(DATA_DIR / "datasets.json")
    assert len(datasets) == 15
    assert {"randi_funconn_wildty", "white_1986_whole", "witvliet_2020_8"} <= {
        d.id for d in datasets
    }


def test_full_snapshot_totals_match_manifest() -> None:
    data = load_neuron_graph(DATA_DIR)
    assert len(data.cells) == 447
    assert len(data.datasets) == 15
    from collections import Counter

    by_type = Counter(c.connection_type for c in data.connections)
    # Totals across all pinned connection files (see MANIFEST.md per-file table).
    assert by_type["chemical"] == 16955
    assert by_type["gap_junction"] == 5467
    assert by_type["functional"] == 2614
    assert sum(by_type.values()) == len(data.connections) == 25036
