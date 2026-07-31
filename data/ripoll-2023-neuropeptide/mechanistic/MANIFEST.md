# Ripoll-Sánchez et al. 2023 — neuropeptide connectome *mechanistic layer*

The base [../MANIFEST.md](../MANIFEST.md) ingests the neuropeptide connectome as a network: a
directed edge source→target weighted by the **number** of NPP–GPCR pathways linking the pair. This
folder adds the mechanistic decomposition — **which** peptide→receptor pairs mediate each edge.

## Source
Same publication (Ripoll-Sánchez et al. 2023, *Neuron* 111:3570–3589; PMID 37935195) and repository
(github.com/LidiaRipollSanchez/Neuropeptide-Connectome). NPP–GPCR pairs are the biochemically
deorphanized interactions of Beets et al. 2023, filtered to **EC50 ≤ 500 nM**.

## Vendored files

### `npp_gpcr_pairs.csv` — the 92 validated NPP–GPCR pairs
Columns: `pair_index` (1–92, matching the paper's per-pair network order), `ligand` (NPP gene,
lowercase), `gpcr` (receptor gene, lowercase), `ec50_nm` (EC50 in nanomolar), `npp_family`,
`gpcr_class`. Built by joining the canonical pair order in
`Adjacency matrices for networks/neuropeptide_pairs (network identities for Individual_net folders).csv`
with EC50 / family / class from `Supplementary Tables/Table S5. NPP-GPCR pairs information.xlsx`.
All 92 pairs matched an EC50 row.

### `edge_pairs.csv` — per-edge pair attribution
Columns: `source`, `target`, `pair_index`. One row per (edge, mediating pair): edge source→target
is mediated by pair `pair_index` (i.e. source expresses that pair's ligand and target expresses its
GPCR). 145,834 rows. Cell names normalized to CIRCE (`DA01`→`DA1`).

Derived from the paper's 92 **individual** per-pair adjacency matrices
(`Adjacency matrices for networks/Individual NPP-GPCR networks LR/`), which decompose the aggregate
network: file *i* is pair *i*'s source×target binary matrix. This is the **long-range** superset;
the mid- and short-range models are edge subsets of it with **identical** per-edge pair sets (the
range models gate edge *existence* by anatomical reach, not the pathway composition of an edge), so
one attribution serves all three range databases.

## Validation
Summing the 92 individual matrices reproduces the published aggregate long-range network exactly:
**53,558 edges, and for every edge the pair count equals the published weight — 0 mismatches.**
So `edge_pairs.csv` is a faithful decomposition, not an estimate. (Cross-check: group by
`source,target` in `edge_pairs.csv` and the row count per edge equals that edge's `weight` in
`../long_range_network.csv`.)

## Notes / not included
- Genes are carried as **symbols** (e.g. `nlp-40`, `aex-2`), not WormBase ids: the repo's
  gene-id ↔ symbol map is absent, so WBGene resolution (and modelling the ligand/GPCR as `Gene`
  entities) is deferred.
- Per-neuron NPP / GPCR **expression** (the CeNGEN substrate that, with the pairs, *derives* the
  network) is not ingested here — the edge decomposition above already gives the per-edge pairs
  directly. Expression ingest (enabling first-principles SPARQL derivation) is a later pass.
