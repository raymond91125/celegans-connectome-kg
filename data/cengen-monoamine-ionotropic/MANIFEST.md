# Ionotropic monoamine receptors — CeNGEN threshold-4 expression

The **ionotropic** (ligand-gated) monoamine receptors: the amine-gated Cys-loop ion channels
directly opened by serotonin, dopamine, tyramine, or octopamine. Added to the KG as `Gene` +
per-neuron `GeneExpression` records so CIRCE represents the *full* aminergic **receptor** repertoire
— both the metabotropic (GPCR) side and the ionotropic side.

## Why these live outside the monoamine mechanistic layer

CIRCE's monoamine mechanistic layer (`../ripoll-2023-monoamine/`) covers the **GPCR** monoamine
receptors, because those are the receptor side of the Bentley et al. 2016 monoamine→GPCR pairs that
reconstruct the predicted aminergic network. The channels here are **ligand-gated ion channels**,
not GPCRs, so they are not part of that network and carry **no predicted `monoaminergic` edges**
(there is no ionotropic aminergic network to reconstruct). They are expression-only, all with
`category = ionotropic_receptor` (the same category as the genuinely ionotropic entries of Cook's
SI6, e.g. `acc-4`/`glr-2`). Keeping them separate preserves the monoamine layer's validation
invariant (exactly 14 GPCR receptors reproducing 2,881 edges).

## The receptors (8 amine-gated Cys-loop channels)

| Gene | WBGene | Amine ligand(s) | Ion selectivity | Deorphanized by |
|------|--------|-----------------|-----------------|-----------------|
| `mod-1`  | WBGene00003386 | serotonin | anion (Cl⁻) | Ranganathan et al. 2000, *Nature* 408:470 |
| `lgc-40` | WBGene00020767 | serotonin (low-affinity); also choline / ACh | anion | Ringstad et al. 2009, *Science* 325:96 |
| `lgc-53` | WBGene00020657 | dopamine | anion | Ringstad et al. 2009 |
| `lgc-55` | WBGene00013746 | tyramine | anion | Ringstad et al. 2009; Pirri et al. 2009, *Neuron* 62:526 |
| `lgc-50` | WBGene00020605 | serotonin, tryptamine | **cation** | Morud et al. 2021, *Curr Biol* 31:4282 |
| `lgc-52` | WBGene00013517 | dopamine, tyramine | anion | Morud et al. 2021 |
| `lgc-54` | WBGene00020528 | dopamine, tyramine, serotonin (high conc.) | anion | Morud et al. 2021 |
| `lgc-56` | WBGene00001588 | tyramine, dopamine, octopamine (high conc.) | anion | Morud et al. 2021 |

`mod-1` and `lgc-50` are the two serotonin receptors; `lgc-40`/`lgc-54` add lower-affinity or
polyspecific serotonin responses; `lgc-53`/`lgc-52`/`lgc-56` cover dopamine/tyramine (and octopamine
for `lgc-56`). Most are anion channels (inhibitory); `lgc-50` is the lone **cation** (excitatory)
channel — note this corrects an earlier mislabeling of `lgc-50` as a chloride channel.

The KG stores only `category = ionotropic_receptor` per gene (ion selectivity and the specific amine
are not modeled as gene slots) — the `amine_ligand`, `ion`, and `source` columns of
`monoamine_ionotropic_genes.csv` carry that provenance in the vendored file and this table.

### Excluded: `lgc-51`

`lgc-51` (WBGene00017399; Morud et al. 2021) is **not** included: it showed no intrinsic amine
response in the deorphanization screen and functions only as an accessory subunit that heteromerizes
with `lgc-52`. It is a channel *subunit* of amine-gated complexes, not itself an amine *receptor*, so
it is left out of the receptor set. (It is present in the CeNGEN matrix, in 6 neurons, if ever
wanted.)

## Source

Expression is the **CeNGEN** single-cell RNA-seq binary matrix at **threshold 4** (Taylor et al.
2021, *Cell* 184:4329-4347, doi:10.1016/j.cell.2021.06.023) — the same matrix the monoamine
reconstruction uses. All eight genes are rows of its `LGC` (ligand-gated channel) section, so no new
expression source is introduced. The specific matrix file
(`30072020_CENGEN_threshold4_expression_NPP_NPR_MR_LGC_allneurons.csv`, keyed by WormBase gene id,
`;`-delimited) is vendored via the Ripoll-Sánchez *Neuropeptide-Connectome* repo (env `RIPOLL_REPO`);
`build_expression.py` reads it and emits the two CSVs below. WormBase gene ids resolved via
mygene.info (species 6239) and confirmed as matrix rows.

## Vendored data

`monoamine_ionotropic_genes.csv` — `symbol,wbgene,category,amine_ligand,ion,source,wbgene_source`
for the eight genes (`category = ionotropic_receptor`). Ingested as `Gene` nodes, keyed by WBGene so
they de-dupe against any shared gene node. Only `symbol,wbgene,category` are read by the ingest; the
rest are documentary provenance.

`monoamine_ionotropic_expression.csv` — `cell,gene_symbol`, one row per expressing neuron
(threshold 4). Ingested as `GeneExpression` records (`confidence = reported`) under dataset
`cengen_2021_monoamine_ionotropic_expression`. 298 rows (mod-1 28, lgc-40 29, lgc-53 68, lgc-55 41,
lgc-50 60, lgc-52 14, lgc-54 17, lgc-56 41). Cell names are CIRCE-normalized (`DA01`→`DA1`).

Regenerate (deterministic — byte-identical against the pinned matrix):

```
RIPOLL_REPO=/path/to/Neuropeptide-Connectome python build_expression.py
```
