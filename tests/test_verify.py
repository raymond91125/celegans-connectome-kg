"""Phase 4 tests: load a small RDF graph into Oxigraph and run the count + sample queries."""

import pytest

from celegans_connectome_kg.build.datamodel import datamodel
from celegans_connectome_kg.export.rdf import to_turtle
from celegans_connectome_kg.verify.sparql import (
    count_summary,
    load_turtle_data,
    rows,
    sample_queries,
)


@pytest.fixture(scope="module")
def store():
    dm = datamodel()
    connectome = dm.Connectome(
        cells=[
            dm.Cell(id="cckg:cell/AVAL", name="AVAL", cell_type="neuron", anatomy="WBbt:0000001"),
            dm.Cell(id="cckg:cell/DA6", name="DA6", cell_type="neuron"),
            dm.Cell(id="cckg:cell/BWM-DL01", name="BWM-DL01", cell_type="muscle"),
        ],
        datasets=[dm.Dataset(id="cckg:dataset/d1", name="D1")],
        connections=[
            _conn(dm, "c1", "AVAL", "DA6", "chemical", 11.0),
            _conn(dm, "c2", "AVAL", "DA6", "gap_junction", 2.0),
            _conn(dm, "c3", "DA6", "AVAL", "gap_junction", 1.0),
            _conn(dm, "c4", "AVAL", "DA6", "functional", 3.0),
        ],
    )
    return load_turtle_data(to_turtle(connectome))


def _conn(dm, cid, pre, post, ctype, weight):
    return dm.Connection(
        id=f"cckg:conn/{cid}",
        pre=f"cckg:cell/{pre}",
        post=f"cckg:cell/{post}",
        connection_type=ctype,
        weight=weight,
        dataset="cckg:dataset/d1",
    )


def test_count_summary(store) -> None:
    assert count_summary(store) == {
        "cells": 3,
        "cells_with_anatomy": 1,
        "datasets": 1,
        "connections": 4,
        "chemical": 1,
        "gap_junction": 2,  # both directions stored faithfully in RDF (merge is viz-only)
        "functional": 1,
    }


def test_sample_queries_present() -> None:
    queries = sample_queries()
    assert {
        "cells_by_type",
        "connections_by_type",
        "ungrounded_cells",
        "strongest_chemical_outputs",
    } <= set(queries)


def test_cells_by_type_query(store) -> None:
    result = {
        r["cell_type"]: int(r["count"]) for r in rows(store, sample_queries()["cells_by_type"])
    }
    assert result == {"neuron": 2, "muscle": 1}


def test_ungrounded_cells_query(store) -> None:
    names = {r["name"] for r in rows(store, sample_queries()["ungrounded_cells"])}
    assert names == {"DA6", "BWM-DL01"}  # AVAL has anatomy, so excluded


def test_strongest_chemical_outputs_query(store) -> None:
    result = rows(store, sample_queries()["strongest_chemical_outputs"])
    assert result == [{"post_name": "DA6", "total_weight": "11"}]
