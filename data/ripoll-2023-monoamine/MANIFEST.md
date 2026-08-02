# Ripoll-Sánchez et al. 2023 — monoamine (aminergic) connectome

The companion **monoamine** signaling network to the neuropeptide connectome
([../ripoll-2023-neuropeptide/](../ripoll-2023-neuropeptide/)), from the same publication and
repository (Ripoll-Sánchez et al. 2023, *Neuron* 111:3570–3589; PMID 37935195;
github.com/LidiaRipollSanchez/Neuropeptide-Connectome). A **predicted** extrasynaptic network built
the same way as the neuropeptide one — a directed edge source→target where the source produces a
monoamine and the target expresses a cognate receptor — but for the four classical monoamines
instead of neuropeptides. **Not observed synapses.**

The monoamine ligand–receptor pairs are from Bentley et al. 2016 (*PLoS Comput Biol* 12:e1005283,
the multilayer *C. elegans* connectome); the network was recomputed by Ripoll-Sánchez et al. 2023
over CeNGEN single-cell receptor expression, so it is directly comparable to their neuropeptide
networks (same 302 neurons, same construction).

## Vendored files

### `monoamine_pairs.csv` — the 14 monoamine → receptor pairs
Columns: `pair_index` (1–14), `monoamine` (source abbreviation: `Ser`, `DA`, `Oct`, `Tyr`),
`monoamine_name` (serotonin / dopamine / octopamine / tyramine), `receptor` (GPCR gene symbol,
lowercase). From `Scripts & data/05062023_Ligand-receptor-interactions_Mon_from_Barry_Bentley.csv`.
The four monoamines and their receptors:
- **serotonin** → ser-1, ser-4, ser-5, ser-7
- **dopamine** → dop-1, dop-2, dop-3, dop-4
- **octopamine** → octr-1, ser-3, ser-6
- **tyramine** → ser-2, tyra-2, tyra-3

### `monoamine_network.csv` — the predicted aminergic connectome
Columns: `source`, `target`, `weight`. 2,881 directed edges; weight = number of monoamine–receptor
pathways linking source→target (1–3). Cell names normalized to CIRCE (`DA01`→`DA1`). From the
aggregate `Adjacency matrices for networks/08062023_monoamine_connectome.csv`. A single network —
unlike the neuropeptide layer there are **no** short/mid/long range models.

The 19 source neurons are the canonical aminergic set: dopaminergic (ADE, CEP, PDE), serotonergic
(ADF, NSM, HSN, I5), tyraminergic (RIM) and octopaminergic (RIC); each produces a single monoamine.

## Mechanistic layer

**Per-edge receptor attribution** — which specific monoamine→receptor pairs mediate each edge, the
analogue of the neuropeptide edge-pairs — lives in [mechanistic/](mechanistic/). The paper ships no
per-pair matrices for the monoamine network (only the aggregate), and its monoamine-**production**
table (Pereira et al. 2015) is not in the source repo, so the attribution is **reconstructed from
CeNGEN receptor expression + the published network and validated by reproducing all 2,881 weights
exactly** (0 mismatches; the source→monoamine map is recovered, not assumed, and matches canonical
identity). See [mechanistic/MANIFEST.md](mechanistic/MANIFEST.md). The 14 receptors are there
resolved to WBGene (`receptor_gene` on each pair) and their expression ingested.
