"""Unit tests for the Ripoll-Sánchez 2023 neuropeptide-network ingest."""

from pathlib import Path

from celegans_connectome_kg.ingest.neuropeptide import _norm, read_neuropeptide_network

CSV = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "ripoll-2023-neuropeptide"
    / "short_range_network.csv"
)


def test_name_normalization() -> None:
    assert _norm("DA01") == "DA1" and _norm("VD09") == "VD9" and _norm("VC06") == "VC6"
    assert _norm("VD10") == "VD10" and _norm("AVAL") == "AVAL"  # unpadded / non-serial unchanged


def test_read_neuropeptide_network() -> None:
    net = read_neuropeptide_network(CSV, "ripoll_2023_neuropeptide_sr", "SR", "desc")
    assert net.dataset_id == "ripoll_2023_neuropeptide_sr" and net.sex == "hermaphrodite"
    conns = net.connections
    assert len(conns) == 31417  # nonzero directed edges in the short-range matrix
    assert all(c.connection_type == "neuropeptidergic" and c.weight >= 1 for c in conns)
    # directed + weighted by pathway count; padded names normalized
    assert max(c.weight for c in conns) == 19
    names = {c.pre for c in conns} | {c.post for c in conns}
    assert "DA1" in names and "DA01" not in names
