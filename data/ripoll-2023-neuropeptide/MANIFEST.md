# Ripoll-Sánchez et al. 2023 — neuropeptidergic connectome

## Source
Ripoll-Sánchez L, Watteyne J, Sun H, Fernandez R, Taylor SR, Weinreb A, Bentley BL, Hammarlund M,
Miller DM 3rd, Hobert O, Beets I, Vértes PE, Schafer WR (2023). **The neuropeptidergic connectome
of *C. elegans*.** *Neuron* 111(22):3570–3589.e5. PMID 37935195 · doi:10.1016/j.neuron.2023.09.043

A genome-scale **predicted extrasynaptic ("wireless") signaling network**: a directed edge
source→target where the source expresses a neuropeptide precursor (NPP) and the target expresses a
cognate GPCR, for a biochemically-validated NPP–GPCR pair. **Not observed synapses.**

Vendored from the authors' repository (github.com/LidiaRipollSanchez/Neuropeptide-Connectome),
`Adjacency matrices for networks/01022024_neuropeptide_connectome_{short,mid,long}_range_model.csv`
(the 02/02/2024 update, with corrected scRNA-seq for dmsr-5 and npr-34).

## Vendored data
`short_range_network.csv`, `mid_range_network.csv`, `long_range_network.csv` — each a labeled
**302×302 directed weighted adjacency matrix** (`Row` = source neuron; columns = target neurons;
weight = number of NPP–GPCR pathways linking the pair). Edge counts: short 31,417 · mid 40,425 ·
long 53,558 (weights 1–20).

## Method / provenance (important)
- Expression is **CeNGEN single-cell RNA-seq at threshold 4 (most stringent)** — chosen because it
  best matched reporter-gene expression; a deliberately conservative choice that minimizes spurious
  edges (see the paper's Methods and reporter-vs-scRNAseq comparison, mmc4). The NPP–GPCR pairs are
  from biochemical deorphanization at **EC50 ≤ 500 nM**.
- The three **range models** reflect how far a peptide is assumed to diffuse: **short-range**
  (most anatomically constrained, most conservative) → **mid-range** → **long-range**
  (expression-only, unconstrained upper bound). All three are ingested as sibling datasets.

## Build
Ingested as three hermaphrodite, adult datasets — `ripoll_2023_neuropeptide_sr` / `_mr` / `_lr` —
with a new `neuropeptidergic` connection type, over cells already in the KG. Matrix motor-neuron
names are zero-padded (`DA01`); normalized to CIRCE names (`DA1`). Directed (row→column); weight =
NPP–GPCR pathway count.

## Not ingested / notes
- The **mechanistic layer** — the 92 NPP–GPCR pairs and per-neuron NPP/GPCR expression — is not
  ingested here (network-only). Available in the repo / paper supplements for a later pass.
- **Sensitivity variants** (CeNGEN thresholds 3–4 × EC50 10 nM–1 µM) are not ingested; only the
  reference threshold-4 / 500 nM networks.
- Being a predicted network on a different weight scale (pathway counts), it is KG/SPARQL-only and
  excluded from the viz's observed-connectivity projections/panel.
