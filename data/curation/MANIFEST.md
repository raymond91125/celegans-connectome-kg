# Anatomy curation

`anatomy_curation.csv` — human-resolved cell → WBbt mappings for the cells the lexical
matcher leaves in the work-list (ambiguous + unmatched). Curator-authored, not an upstream
artifact.

- Curated: 2026-06-25, against the pinned WBBT (`data/wbbt/`).
- Method: each term confirmed against the pinned `wbbt.json` (label/synonym), per the
  `external-term-lookup` skill — no guessed IDs.
- 114 rows = the full Phase 2 work-list (95 BWM muscles + 19 others).

## Columns

`cell_name, wbbt_id, wbbt_label, confidence, note`

## Notes on resolutions

- **BWM-\*** (95) — grounded by quadrant: `DL→WBbt:0005816`, `DR→WBbt:0005817`,
  `VL→WBbt:0005818`, `VR→WBbt:0005819` (the per-quadrant body wall muscle classes; WBBT has
  no per-cell term for each of the 95).
- **M1 / M4 / M5** — pharyngeal **neurons** (`WBbt:0004488 / 0004467 / 0004465`), correcting
  the lexical false-match to the pm1/pm4/pm5 **muscle** terms (synonyms "m1"/"m4"/"m5").
- **pm2D / pm3D / pm5D** — the dorsal pharyngeal-muscle pair terms (`pm?DL-pm?DR`).
- Lower-confidence rows are flagged in the `confidence` column: `LegacyBodyWallMuscles`
  (legacy aggregate → generic body wall muscle cell), `excgl`, `hyp`.
