# MSIPS reproducibility supplement

All generated benchmark instances are synthetic. They validate selection implementation behavior under the stated constraints, not real attack resistance or performance of a smart-home deployment.

## Reproduce

Use Python 3.12 with NumPy 2.3.5 and SciPy 1.17.0. Run `python benchmark.py` from this directory. It regenerates instances, per-instance results and the summary. The seed is 20261016. The script runs 180 instances: 10, 20 or 30 candidates; separate, clustered or overlapping domains; 20 repetitions per cell. The saved script is the authoritative generator, including random draw order. Runtime measurements will vary with the host and solver environment.

Run `python verify_results.py` after generating the results. This independent exhaustive oracle checks all 60 ten-item cases. It passed on the supplied results. The benchmark script also checks returned-set feasibility and heuristic inclusion-minimality.

## Results and interpretation

The exact solver proved 167 cases optimal and 13 infeasible, with no time-limit outcomes. Nominal-only selection failed the residual score requirement in 134 of 180 cases, including all 13 robustly infeasible cases. Among the 167 robust-feasible cases, 121 nominal selections failed that requirement. The nominal-only rule is a controlled ablation, not an implementation of a published competing scheme. Heuristic gaps are conditional on feasible instances with exact optima. The largest observed gap was 900%; reverse deletion is not a near-optimal algorithm by default. Its time includes feasibility initialization.

The tests fix placement and common true gates, omit linkage and lockout cost, and use three randomly generated contribution vectors. They require two abstract functions nominally, but do not require both functions to survive compromise. Thus residual score feasibility is not continued authorization security. Contributions are not calibrated probabilities. No Fabric, status-list or registry deployment timing is reported.

## Search update

`search_log.json` gives five literal queries run through public-web search on 16 October 2026, in two batches. `screening.json` lists 93 returned URL records, 12 duplicates, eight retained records and 73 excluded records, with decisions and reasons. These counts are returned records, not estimated search-engine hit totals. Titles are normalized metadata, including one normalized remote-attestation title. This bounded update is separate from the earlier 60-source family map and is not an exhaustive database review. Five selected technical texts were accessible; Matter core and the two already-cited publisher articles were checked through indexed excerpts. Publisher links, technical specifications and supplementary direct follow-ups are cited in the manuscript.

## Figures

`figure3.svg`, `figure6.svg` and `figure7.svg` are editable vector originals; high-resolution PNG fallbacks are embedded alongside SVG alternatives in the DOCX. Run `python redraw_figures.py` with Matplotlib to regenerate them. The diagrams encode the revised manuscript's relationships directly.

## Files

- `benchmark.py`: deterministic generator, exact optimization, reverse deletion and nominal-only ablation.
- `benchmark_instances.json`: generated inputs.
- `benchmark_results.csv`: results and solver statuses for each instance.
- `benchmark_summary.json`: environment and nine-cell descriptive summary.
- `verify_results.py`: exhaustive oracle for ten-item cases.
- `search_log.json` and `screening.json`: bounded update records.
- `redraw_figures.py`, SVGs and PNGs: precise figure source and exports.
