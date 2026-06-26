"""Phase 4 load + verify: load the RDF into an in-process triplestore and query it.

Uses Oxigraph (embedded, no server) so the serialized graph can be loaded and queried with
real SPARQL — both for the sample queries in ``queries/*.rq`` and for sanity-checking that
the RDF round-trips the counts the build produced.
"""

from __future__ import annotations

from pathlib import Path

from pyoxigraph import RdfFormat, Store

QUERIES_DIR = Path(__file__).parent / "queries"

_PREFIXES = """
PREFIX cckg: <https://wormbase.org/resources/connectome/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX WBbt: <http://purl.obolibrary.org/obo/WBbt_>
"""


def load_turtle(path: Path) -> Store:
    """Load a Turtle file into a fresh in-memory Oxigraph store."""
    store = Store()
    store.load(Path(path).read_bytes(), format=RdfFormat.TURTLE)
    return store


def load_turtle_data(turtle: str) -> Store:
    """Load Turtle text into a fresh in-memory Oxigraph store."""
    store = Store()
    store.load(turtle.encode(), format=RdfFormat.TURTLE)
    return store


def rows(store: Store, sparql: str) -> list[dict[str, str]]:
    """Run a SELECT and return rows as plain dicts of {var: value-as-string}."""
    result = store.query(_PREFIXES + sparql)
    names = [var.value for var in result.variables]
    out = []
    for solution in result:
        row = {}
        for name in names:
            term = solution[name]
            row[name] = term.value if term is not None else None
        out.append(row)
    return out


def scalar(store: Store, sparql: str) -> int:
    """Run a SELECT whose first row/column is a count and return it as int."""
    result = rows(store, sparql)
    return int(next(iter(result[0].values()))) if result else 0


def sample_queries() -> dict[str, str]:
    """Load the bundled sample SPARQL queries, keyed by file stem."""
    return {p.stem: p.read_text() for p in sorted(QUERIES_DIR.glob("*.rq"))}


def count_summary(store: Store) -> dict[str, int]:
    """Standard counts used for the round-trip sanity check."""
    return {
        "cells": scalar(store, "SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Cell }"),
        "cells_with_anatomy": scalar(
            store, "SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Cell ; cckg:anatomy ?a }"
        ),
        "datasets": scalar(store, "SELECT (COUNT(?d) AS ?n) WHERE { ?d a cckg:Dataset }"),
        "connections": scalar(store, "SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Connection }"),
        "chemical": scalar(
            store,
            'SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Connection ; cckg:connection_type "chemical" }',
        ),
        "gap_junction": scalar(
            store,
            'SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Connection ; cckg:connection_type "gap_junction" }',
        ),
        "functional": scalar(
            store,
            'SELECT (COUNT(?c) AS ?n) WHERE { ?c a cckg:Connection ; cckg:connection_type "functional" }',
        ),
    }
