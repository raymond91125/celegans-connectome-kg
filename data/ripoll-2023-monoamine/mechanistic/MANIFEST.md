# Ripoll-Sánchez et al. 2023 — monoamine connectome *mechanistic layer*

The base [../MANIFEST.md](../MANIFEST.md) ingests the monoamine connectome as a network: a directed
edge source→target weighted by the **number** of monoamine–receptor pathways linking the pair. This
folder adds the mechanistic decomposition — **which** monoamine→receptor pairs mediate each edge,
the analogue of the neuropeptide [../../ripoll-2023-neuropeptide/mechanistic/](../../ripoll-2023-neuropeptide/mechanistic/) layer.

## Why this is reconstructed, not read off

Unlike the neuropeptide network — where the paper ships 92 **individual per-pair adjacency
matrices** that decompose the aggregate exactly — the monoamine network is published **only as the
aggregate matrix** (`Adjacency matrices for networks/08062023_monoamine_connectome.csv`). There is
no per-pair monoamine matrix to read the attribution from, and the paper's monoamine-**production**
table (Pereira et al. 2015, the input its build script reads to know which neuron releases which
monoamine) is **not** in the repository.

So the attribution here is **reconstructed from first principles and validated**, by
[`reconstruct.py`](reconstruct.py) (committed, deterministic, no network access):

- An edge source→target for pair (monoamine *m*, receptor *r*) exists iff the source **produces**
  *m* and the target **expresses** *r*; the published weight is the count of such pairs. This is
  exactly the paper's `Network_building` construction.
- The **receptor** side is the binarized CeNGEN threshold-4 expression — the `MR` (monoamine
  receptor) genes of `Scripts & data/30072020_CENGEN_threshold4_expression_NPP_NPR_MR_LGC_allneurons.csv`,
  which we *do* have. The 14 receptor symbols were resolved to WormBase gene ids (see below) to pull
  their expression rows.
- The **producer** side (the missing Pereira table) is **recovered, not assumed**: each source's
  observed out-edge weight profile matches, for exactly one monoamine *m*, the per-target count of
  *m*'s receptors the target expresses. That uniquely identifies the source's monoamine.

## Validation — exact, 0 mismatches

Running the reconstruction over CeNGEN receptor expression + the published aggregate network:

- **2,881 / 2,881** published edges reproduced, and **every edge's weight is exact — 0 mismatches**.
- All **19** source neurons recovered **uniquely** (no source matched two monoamines, none matched
  none).
- The recovered source→monoamine map has **0 conflicts** with the canonical aminergic identities
  (Ser = ADF, HSN, I5, NSM; DA = ADE, CEP, PDE; Oct = RIC; Tyr = RIM). This is an *independent*
  cross-check: the map was recovered from expression + network, and it reproduces textbook identity.

Exact weight reproduction plus independent identity recovery is strong evidence the attribution is
**faithful, not fitted** — the same standard the neuropeptide mechanistic layer meets. (A wrong
WBGene for any receptor would perturb its expression row and break the exact reproduction, so the
0-mismatch result also validates the gene resolution.)

## Vendored files (all cell names normalized to CIRCE, `DA01`→`DA1`)

### `edge_pairs.csv` — per-edge pair attribution
Columns: `source`, `target`, `pair_index` (1–14, matching [../monoamine_pairs.csv](../monoamine_pairs.csv)).
One row per (edge, mediating pair). **4,127 rows** = the sum of all edge weights (2,881 edges,
weights 1–3). Grouping by `source,target` gives each edge's pair count, which equals that edge's
`weight` in [../monoamine_network.csv](../monoamine_network.csv).

### `monoamine_receptor_genes.csv` — the 14 receptor genes, resolved to WormBase
Columns: `symbol`, `wbgene` (`WB:WBGene…` curie), `category` (always `monoamine_receptor`),
`wbgene_source`. Resolution provenance (`wbgene_source`): 5 already present in CIRCE data
(`circe-existing`); 9 resolved via mygene.info → WormBase (`mygene-wormbase`). All 14 validated
transitively by the 0-mismatch reconstruction. The `ser-1..ser-4,ser-7` ids are consecutive
(`WBGene00004776`–`00004780`), a further consistency check.

### `monoamine_receptor_expression.csv` — per-neuron receptor expression
Columns: `cell`, `gene_symbol`. **787** (cell, receptor) records over the 302 neurons — the
binarized CeNGEN threshold-4 expression of the 14 receptors, i.e. the GPCR substrate that (with the
recovered producer identities) derives the network. The monoamine **ligand** side has no gene
expression rows: a monoamine is a small molecule, not a transcript, so production is carried
implicitly by which pairs mediate a source's edges.

## Notes / not included
- **Sensitivity variants** (other CeNGEN thresholds) are not ingested — only the reference
  threshold-4 expression, matching the base network.
- Receptor `systematic_name` is not carried (the base pairs table keys on symbol; the WBGene link is
  the stable join key).
