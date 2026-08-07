# Private peptidergic lines, not wiring, connect the extra-pharyngeal "feeding" neurons AIN, ASI, and AVK to the *C. elegans* pharynx: a knowledge-graph analysis

**Authors:** _(add author list)_
**Affiliation:** WormBase / CIRCE project
**Preprint / working analysis.** Reproducible source: `analysis/feeding_pathways/` in the CIRCE repository.

---

## Abstract

Whole-brain calcium imaging in *Caenorhabditis elegans* has shown that neurons far outside the
pharynx carry activity correlated with feeding, but such correlations do not, by themselves, reveal
a circuit. We asked whether the *C. elegans* connectome offers a structural explanation for three
extra-pharyngeal neurons — AIN, ASI, and AVK — reported to encode feeding by Atanas et al. (2023),
and if so, by what route. Using CIRCE, a LinkML-modelled, RDF/OWL knowledge graph that integrates
anatomical wiring, a functional signal-propagation atlas, and a biochemically grounded predicted
neuropeptide connectome, we answered the question entirely in SPARQL. We find no shared connectome
signature for the three neurons: projecting to the pharynx via neuropeptides is common (98 of the
extra-pharyngeal classes do it), and the three do not cluster. None of them is wired to the
pharyngeal pump-motor module (MC/M3/M4) — that module is a genuinely coupled cluster (chemical, gap,
and reciprocal functional edges), whereas AIN has no synaptic, electrical, or functional edge to it.
The only routes available to AIN and AVK are specific, high-affinity, and in AVK's case fully private
peptidergic channels: AVK→NSM (FLP-1→FRPR-7, 7 nM) and AVK→MC (FLP-1→DMSR-6, 14 nM) run on a peptide
expressed by AVK alone, and AIN→MC (NLP-42→SPRR-1, 8 nM) is near-private, while the AIN/ASI→NSM route
(NLP-47→GNRR-1) is a bus shared by 28 classes. We conclude that, for these neurons, coupling to
feeding is most parsimoniously neuromodulatory rather than wired, and we state four falsifiable,
molecule-specific predictions for experimental test. The analysis illustrates how a queryable
connectome converts a correlational imaging result into concrete bench hypotheses.

## 1. Introduction

The *C. elegans* connectome — a synapse-level wiring diagram of a compact, stereotyped nervous
system — is a foundational resource for linking circuits to behaviour (White et al., 1986; Cook et
al., 2019; Witvliet et al., 2021). Yet the wiring diagram is not the whole nervous system. Much of
the animal's signalling is **extrasynaptic**: neuropeptides and monoamines released into the
neighbourhood act on receptors on cells that are not synaptic partners. A biochemically deorphanized
peptide–receptor interaction map (Beets et al., 2023) combined with single-cell expression (Taylor
et al., 2021; the CeNGEN atlas) has enabled a genome-scale **predicted neuropeptidergic connectome**
(Ripoll-Sánchez et al., 2023), and a separate optogenetic **functional atlas** measures fast signal
propagation between neurons irrespective of the route (Randi et al., 2023). Interpreting a modern
functional-imaging experiment therefore requires reasoning across anatomy, physiology, and
extrasynaptic signalling at once.

Atanas et al. (2023) recorded brain-wide activity during free behaviour and reported that several
extra-pharyngeal neurons — among them AIN, ASI, and AVK — carry activity that correlates with
feeding, alongside the pharyngeal neurons MC, M3, and M4 (the last of which received a causal test in
that study). A correlation with a behaviour, however, does not identify a pathway: it leaves open
whether these neurons act on the feeding apparatus, and if so how. This is a structural question, and
it is exactly the kind of question a connectome should answer — provided the connectome is queryable
across its anatomical, functional, and extrasynaptic layers together.

Here we use **CIRCE** (Connectome Integration & Reasoning for *C. elegans*), a knowledge graph that
unifies those layers under a single LinkML schema and exports to RDF/OWL, to ask: **is there anything
in the connectome that distinguishes AIN, ASI, and AVK, and by what route could they reach the
feeding (pharyngeal) circuit?** The entire analysis is expressed as SPARQL queries over the graph, so
the method is transparent and re-runnable.

## 2. Methods

### 2.1 The knowledge graph

CIRCE integrates, under one schema, the anatomical connectomes of White et al. (1986), Cook et al.
(2019, both sexes), Cook et al. (2020, pharynx), and the Witvliet et al. (2021) developmental series;
the Randi et al. (2023) functional signal-propagation atlas (wild-type and *unc-31* backgrounds); and
the Ripoll-Sánchez et al. (2023) predicted neuropeptidergic and aminergic connectomes, together with
the per-neuron CeNGEN expression (Taylor et al., 2021) and the deorphanized peptide–GPCR pairs (Beets
et al., 2023; multilayer framework of Bentley et al., 2016) that underlie them. Cells are grounded to
WBBT anatomy ontology terms and genes to persistent WormBase identifiers. Connections carry a
`connection_type` (`chemical`, `gap_junction`, `functional`, `neuropeptidergic`, `monoaminergic`), a
weight, and a source dataset. The graph is serialised to Turtle and queried with SPARQL (embedded
Oxigraph; the same store used by the project's verification suite, and identical to the deployed
`circe-sparql` endpoint).

### 2.2 Design decisions

*"Pharynx"* is defined as the 14 canonical pharyngeal **neuron** classes (I1–I6, M1–M5, MC, MI, NSM);
pharyngeal muscle and marginal cells are excluded, so "projects to the pharynx" means "projects to a
pharyngeal neuron."

*First-principles reconstruction.* Rather than reading precomputed peptidergic edges, we reconstruct
them from their premises: a source reaches a target through a peptide channel iff the source expresses
a deorphanized ligand gene, the target expresses the cognate GPCR gene (both in the Ripoll-Sánchez
CeNGEN expression dataset), and the ligand→GPCR pair is one of the biochemically validated pairs.
Expression is joined on WBGene identifiers, not symbols, because some source symbols are WormBase
synonyms of a different canonical gene. This is the same derivation the graph's own reference query
`neuropeptide_derived_targets.rq` performs.

*Baseline.* To judge whether a connection is notable we compare against all extra-pharyngeal classes,
not a hand-picked few. We rank every extra-pharyngeal class by the number of distinct pharyngeal
neuron classes it reaches via the predicted peptide network.

*Specificity.* The "privacy" of a peptide channel is the number of neuron classes that express its
ligand at all: a peptide expressed by one class is a private line; one expressed by many is a shared
broadcast bus. This controls for the fact that having *some* peptidergic edge to the pharynx is common.

### 2.3 Reproducibility

The five queries are in `analysis/feeding_pathways/queries/*.rq`; `run_queries.py` loads
`outputs/connectome.ttl` and executes them, writing `results.json`. Results are deterministic (each
query carries an `ORDER BY`; output is independent of `PYTHONHASHSEED`). Every quantity reported below
is produced by a named query.

```
uv run cckg build && uv run cckg export
uv run python analysis/feeding_pathways/run_queries.py
```

## 3. Results

### 3.1 There is no shared connectome signature (Q1)

Ranking every extra-pharyngeal class by its number of pharyngeal neuron targets in the predicted
peptide network shows that projecting to the pharynx is **ordinary**: 98 extra-pharyngeal classes do
so. The three "feeding" neurons do not cluster. AVK ranks **1st** (12 pharyngeal targets), but ASI is
**37th** (7) and AIN is **89th** (5); the top of the list (PQR, URX, AUA, HSN) has no special
relationship to feeding. No structural feature groups AIN, ASI, and AVK together.

### 3.2 AIN and ASI are not wired to AVK (Q2)

If AVK were a feeding hub that AIN and ASI feed into, wiring would be expected. There is none: across
all datasets and both directions, the only connections between AVK and AIN/ASI are neuropeptidergic
(36 edges); there is no chemical synapse, gap junction, or functional edge. Any relationship is
through the predicted peptide layer alone.

### 3.3 AIN is an outsider to the pump-motor module (Q5)

Among the paper's correlated set {MC, M3, M4, AIN}, the pharyngeal neurons MC/M3/M4 form a genuinely
coupled pump-motor cluster — interconnected by chemical synapses, the MC–M3 gap junction, and a
reciprocal MC↔M3 **functional** edge. AIN, by contrast, appears only on neuropeptidergic rows: it has
no chemical, gap, or functional edge to MC, M3, or M4 (nor, tested separately, to any pharyngeal
neuron). Connectomically the group is three coupled pump neurons plus an outsider.

### 3.4 The available routes are specific, high-affinity peptide channels (Q3, Q4)

The peptide channels from each neuron onto the two pharyngeal hubs NSM and MC, with binding affinity
(EC50) and specificity:

| Source → target | Channel | EC50 | Ligand broadcast by | Read |
|---|---|---:|---:|---|
| AVK → NSM | FLP-1 → FRPR-7 | 7.3 nM | **1 class** | private, high-affinity |
| AVK → MC  | FLP-1 → DMSR-6 | 14.3 nM | **1 class** | private, high-affinity |
| AIN → MC  | NLP-42 → SPRR-1 | 8.1 nM | 3 classes | near-private, high-affinity |
| AIN → NSM | NLP-47 → GNRR-1 | 62 nM | 28 classes | public bus |
| ASI → NSM | NLP-47 → GNRR-1 | 62 nM | 28 classes | public bus |

AVK's two channels both run on FLP-1, a peptide expressed by AVK alone in this dataset — fully private
lines onto the serotonergic pharyngeal neuron NSM and the pacemaker MC. AIN's channel onto MC
(NLP-42→SPRR-1) is near-private and high-affinity. The AIN/ASI→NSM route, in contrast, is carried by
NLP-47, broadcast by 28 classes: a shared bus, not a feeding-specific line. Specificity, not mere
presence, is what distinguishes the candidate routes.

## 4. Discussion

The connectome returns a largely **negative** answer to the surface question — AIN, ASI, and AVK
share no structural signature, are not wired to the pharyngeal pump module, and are not even wired to
one another — and a **positive** answer to the mechanistic one: the only routes these neurons have
into the feeding circuit are extrasynaptic peptide channels, and the most notable of them are private
and high-affinity. This dissociation is itself informative. It explains how neurons can "encode
feeding" in a whole-brain recording while being outsiders to the feeding wiring diagram: the coupling
is plausibly **wireless**. It also aligns with the broader picture from Atanas et al. (2023), in which
feeding-related coupling is flexible and state-dependent — a signature of neuromodulation rather than
hard wiring.

We frame the results as four falsifiable, molecule-specific hypotheses.

**H1. AVK reaches the pharynx through a private FLP-1 line.** AVK's only structural route is FLP-1 on
two private, high-affinity GPCRs — FRPR-7 on NSM (7 nM) and DMSR-6 on MC (14 nM) — used by no other
sender. *Prediction:* loss of `flp-1`, `frpr-7`, or `dmsr-6` decouples AVK activity from NSM/MC
feeding dynamics without altering the pump's intrinsic rhythm.

**H2. AIN acts on MC peptidergically, not by wiring.** AIN has no synaptic, electrical, or functional
edge to MC, yet carries a near-private, high-affinity NLP-42→SPRR-1 channel onto it. *Prediction:*
perturbing `nlp-42` or `sprr-1` reduces the AIN–MC activity correlation while MC's pump activity
persists. Because the channel is peptidergic, it is invisible to fast functional-imaging connectivity
— which is precisely why AIN reads as an outsider in the functional atlas.

**H3. The AIN/ASI→NSM route is a shared bus, not a feeding-specific channel.** NLP-47→GNRR-1 is
broadcast by 28 classes. *Prediction:* perturbing it has broad, non-feeding-specific effects, and the
AIN/ASI feeding correlation largely survives — a caution against over-interpreting this edge.

**H4 (unifying). For the extra-pharyngeal neurons, feeding coupling is neuromodulatory, not wired.**
MC/M3/M4 are a wired and functionally coupled module; AIN/ASI/AVK are connectome outsiders whose only
candidate links are private high-affinity peptide channels (AVK, AIN) or a public bus (AIN/ASI).
*Prediction:* the AIN/ASI/AVK feeding correlations survive fast synaptic silencing but break under
peptidergic disruption, whereas the MC/M3/M4 correlation behaves oppositely.

### 4.1 Limitations and confidence

The findings rest on two tiers of evidence. **Robust** claims derive from observed data: MC/M3/M4
form a wired, functionally coupled module, and AIN/ASI/AVK have no observed synaptic or functional
edge to the pharynx or to AVK. **Moderate-confidence** claims — the specific channels, their
affinities, and their specificity — derive from the *predicted* peptidergic layer, which is grounded
in single-cell expression and in vitro biochemistry but is not observed connectivity; expression
thresholding and the EC50 ≤ 500 nM inclusion cutoff of the underlying pair set both influence which
channels appear. Critically, **none of this tests whether any route drives feeding behaviour**: that
requires the perturbation experiments named in H1–H4. CIRCE's contribution is to nominate the
specific molecules and cells to target, narrowing an open-ended imaging correlation to a small set of
bench-ready hypotheses.

### 4.2 Methodological note

The analysis is expressed entirely as SPARQL over an integrated graph, and the two load-bearing
results (the baseline ranking and the channel table) are reconstructed from first principles —
expression plus biochemistry — rather than read from precomputed edges. This makes each claim
auditable: a reader can run the query, inspect the join, and change a threshold. It also demonstrates
a general pattern for connectome knowledge graphs: extrasynaptic "wiring" need not be stored as edges
but can be *derived on demand* from the molecular premises, so that querying the graph is a form of
reasoning about the circuit.

## 5. Conclusion

A queryable, multilayer connectome converts a whole-brain imaging correlation into structure. For
AIN, ASI, and AVK the structure says: not a shared circuit, not wiring, but a small number of
specific — and in AVK's case private — high-affinity peptidergic channels onto the pharyngeal hubs
NSM and MC. The resulting four hypotheses are directly testable, and the entire derivation is a
handful of SPARQL queries anyone can re-run.

## Data and code availability

All queries (`queries/*.rq`), the runner (`run_queries.py`), and the machine-readable outputs
(`results.json`) are in `analysis/feeding_pathways/`. The knowledge graph is built and exported with
`uv run cckg build && uv run cckg export`; the source LinkML schema and all ingest code are in the
CIRCE repository. Each `.rq` file also runs unchanged against any CIRCE SPARQL endpoint.

## References

1. Atanas AA, Kim J, Wang Z, et al. Brain-wide representations of behavior spanning multiple
   timescales and states in *C. elegans*. *Cell* 186(19):4134–4151 (2023).
   doi:10.1016/j.cell.2023.07.035. PMID:37607537.
2. Ripoll-Sánchez L, Watteyne J, Sun H, et al. The neuropeptidergic connectome of *C. elegans*.
   *Neuron* 111(22):3570–3589 (2023). doi:10.1016/j.neuron.2023.09.043.
3. Beets I, Zels S, Vandewyer E, et al. System-wide mapping of peptide–GPCR interactions in
   *C. elegans*. *Cell Reports* 42(9):113058 (2023). doi:10.1016/j.celrep.2023.113058.
4. Bentley B, Branicky R, Barnes CL, et al. The multilayer connectome of *Caenorhabditis elegans*.
   *PLoS Comput. Biol.* 12(12):e1005283 (2016). doi:10.1371/journal.pcbi.1005283.
5. Taylor SR, Santpere G, Weinreb A, et al. Molecular topography of an entire nervous system (CeNGEN).
   *Cell* 184(16):4329–4347 (2021). doi:10.1016/j.cell.2021.06.023.
6. Randi F, Sharma AK, Dvali S, Leifer AM. Neural signal propagation atlas of *Caenorhabditis
   elegans*. *Nature* 623(7986):406–414 (2023). doi:10.1038/s41586-023-06683-4.
7. Cook SJ, Jarrell TA, Brittin CA, et al. Whole-animal connectomes of both *C. elegans* sexes.
   *Nature* 571:63–71 (2019). doi:10.1038/s41586-019-1352-7.
8. Cook SJ, Crouse CM, Yakovlev MA, et al. The connectome of the *Caenorhabditis elegans* pharynx.
   *J. Comp. Neurol.* 528(15):2767–2784 (2020). doi:10.1002/cne.24932.
9. Witvliet D, Mulcahy B, Mitchell JK, et al. Connectomes across development reveal principles of
   brain maturation. *Nature* 596(7871):257–261 (2021). doi:10.1038/s41586-021-03778-8.
10. White JG, Southgate E, Thomson JN, Brenner S. The structure of the nervous system of the nematode
    *Caenorhabditis elegans*. *Phil. Trans. R. Soc. Lond. B* 314(1165):1–340 (1986).
    doi:10.1098/rstb.1986.0056.
