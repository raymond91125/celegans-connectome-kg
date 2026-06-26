"""WBBT index for lexical anatomy grounding.

Loads the pinned WBBT OBO-graph JSON (``data/wbbt/wbbt.json``) and builds a normalized
lookup from cell-name strings to WBBT terms. The file imports non-anatomy ontologies (GO,
etc.), so only ``WBbt_*`` classes are indexed; deprecated/obsolete classes are skipped.

Each lookup hit carries a *kind* recording how it was reached — ``label`` or ``exact``
(strong, used for confident matches) vs. ``related`` / ``broad`` / ``narrow`` (weak, only
ever yield an ambiguous result). See :mod:`celegans_connectome_kg.match.matcher`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

#: OBO synonym predicate → our match-kind label.
_SYNONYM_KIND = {
    "hasExactSynonym": "exact",
    "hasRelatedSynonym": "related",
    "hasBroadSynonym": "broad",
    "hasNarrowSynonym": "narrow",
}

#: Kinds that can yield a confident (matched) result; others are weak → ambiguous.
STRONG_KINDS = frozenset({"label", "exact"})

_WS = re.compile(r"\s+")


def normalize(name: str) -> str:
    """Normalize a name for lexical comparison: trim, collapse whitespace, casefold."""
    return _WS.sub(" ", name.strip()).casefold()


def _iri_to_curie(iri: str) -> str:
    """``…/WBbt_0004013`` → ``WBbt:0004013``."""
    return "WBbt:" + iri.split("WBbt_", 1)[1]


@dataclass(frozen=True)
class Hit:
    """A single index hit: a WBBT term reached via a given match kind."""

    curie: str
    kind: str


@dataclass(frozen=True)
class WBBTTerm:
    """A WBBT anatomy term."""

    curie: str
    label: str | None


class WBBTIndex:
    """Normalized name → WBBT term lookup built from an OBO-graph JSON file."""

    def __init__(self) -> None:
        self.terms: dict[str, WBBTTerm] = {}
        self._by_norm: dict[str, set[Hit]] = {}

    def _add(self, norm_key: str, hit: Hit) -> None:
        if norm_key:
            self._by_norm.setdefault(norm_key, set()).add(hit)

    @classmethod
    def from_obograph(cls, path: Path) -> WBBTIndex:
        """Build the index from a WBBT OBO-graph JSON file."""
        graph = json.loads(Path(path).read_text())["graphs"][0]
        index = cls()
        for node in graph["nodes"]:
            iri = node.get("id", "")
            if "WBbt_" not in iri or node.get("type") != "CLASS":
                continue
            meta = node.get("meta", {})
            if meta.get("deprecated"):
                continue
            curie = _iri_to_curie(iri)
            label = node.get("lbl")
            index.terms[curie] = WBBTTerm(curie=curie, label=label)
            if label:
                index._add(normalize(label), Hit(curie, "label"))
            for syn in meta.get("synonyms", []):
                kind = _SYNONYM_KIND.get(syn.get("pred"), "other")
                index._add(normalize(syn.get("val", "")), Hit(curie, kind))
        return index

    def lookup(self, name: str) -> list[Hit]:
        """Return all hits for ``name``, sorted by (curie, kind) for determinism."""
        return sorted(self._by_norm.get(normalize(name), set()), key=lambda h: (h.curie, h.kind))
