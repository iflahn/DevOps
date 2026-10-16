# MSIPS reproducibility release 2

Research companion for **Decision Specific Identity Evidence Selection for Smart Homes with Ledger Aware Placement**. Prepared 16 October 2026. All numerical contributions and generated instances are synthetic; this is not a calibrated security evaluation or a deployed Matter/Fabric benchmark.

Download `MSIPS_Reproducibility_v2.zip` in this folder for all saved input matrices and figure exports, or regenerate them with the code below.

## Reproduce

Use Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. From `benchmark_v2`, run:

```bash
python large_benchmark.py
python verify_large.py
python scenario_cases.py
python refresh_cases.py
python matter_policy.py
```

The generator fixes seed 2026101602. It creates 36 cases with 100, 300 or 1000 candidates, clustered or correlated-overlap domains, budget factors 1.05 or 1.25 relative to the continuous minimum-privacy relaxation, and three repetitions per cell. Full generation order and constraints are specified in the code. Fixed-location gates have common true state and no variable cost. Three scenario contribution vectors share latent domain/item effects. Four nominal functions and residual authentication coverage are required. These are synthetic dependency models, not observed household traces.

## Algorithms and results

Exact MILP uses a 3 s per-call limit and zero target relative gap. Forward construction scores capped normalized constraint-deficit reduction per `burden + eta * privacy` for eta in `[0, 2, 10, 100, 100000]`, chooses the best feasible start, reverse-prunes it and attempts up to 600 first-improvement one-for-one cost-reducing swaps. It uses no MILP start. A construction failure is not a proof of infeasibility.

The paired start experiment uses greedy eta=10, greedy eta=100 and a zero-objective feasibility MILP with a 1 s limit, each followed by the same reverse-delete pass. All 36 exact problems were proved optimal. Forward/local search returned feasible sets in 32 cases; successful-cell median gaps were 5.7–18.1%. Four failures occurred under the tighter budget. All 31 cases with at least two successful starts had different post-deletion costs; median paired spread was 18.75%, maximum 117.04%, relative to the best successful start.

A cost-focused pilot failed to construct feasible sets under the tight budgets; its results are retained as `pilot_results.csv` and `pilot_summary.json`. Final privacy-aware construction used the same generated inputs. The nominal-only rule is a constraint sanity check, not a competitive published security system or empirical attack-rate estimate.

`large_results.csv` includes status, runtime, heuristic success and optimum/bound gaps. `large_instances.json` contains all input matrices and saved selections. `verify_large.py` reconstructs the constraints independently and checks every saved exact and forward/local selection. It passed. Timings vary with the host. The run used an x86-64 Intel Xeon Platinum 8573C container, Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0; `OMP_NUM_THREADS=1` does not guarantee control of all solver or host scheduling.

## Worked scenarios and Matter-derived instance

`scenario_cases.py` exhaustively enumerates the door, technician and camera cases with two contribution vectors: remote impersonation and stolen-phone/device misuse. `refresh_cases.py` computes the technician threshold and owner-approval sweeps. These are hypothetical numerical cases. A positive residual score does not establish that an authorization function, posture gate or status authority remains trustworthy after compromise.

`matter_policy.py` instantiates a small ACL derived from the Matter SDK Access Control Guide: commissioning administrator, CASE subject, fabric, privilege, cluster and endpoint. It checks one permit and three deny outcomes. It is not a conformance test, execution of the Matter SDK or a device trace. Source: https://project-chip.github.io/connectedhomeip-doc/guides/access-control-guide.html (accessed 16 October 2026).

## Earlier checks and literature records

The `preliminary` directory preserves the earlier 180 small generated instances, exhaustive oracle for all 60 ten-item cases, search query and screening metadata, and vector figure source. Those results are preliminary; the primary manuscript now uses scenario-indexed worked cases and the larger stress benchmark. The earlier five-query search has 93 returned URL records, 12 duplicates, eight retained and 73 excluded. It is a bounded public-source update, not an exhaustive database review.

Reference [21] was subsequently retrieved as full text from Science Tokyo's repository (https://t2r2.star.titech.ac.jp/rrws/file/CTT100940118/ATD100000413/). Its lifecycle coverage is primary in the current map. Reference [54] remains abstract-only and is not included in family coverage counts. The Matter core specification's version metadata was updated to 1.4.2; the executable ACL illustration is based on the accessible SDK guide. The 1227-page core PDF could not be retrieved in full. No inaccessible source is represented as fully audited.

## Archive and citation

The repository commit records this exact release. `CITATION.cff` gives software citation metadata. A public DOI has not yet been assigned; no DOI is fabricated. Files include only our code, generated data, figure sources and bibliographic search metadata. Third-party article/specification PDFs and the unpublished manuscript are not redistributed here.
