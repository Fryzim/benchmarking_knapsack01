# Knapsack 0/1 — Comparative Benchmark of 16 Algorithms

**Team:** Chaabane, Arman, Bartosz, Ahmed · **Course:** Advanced Algorithms · December 2025

Comparative study of 16 algorithms for the 0/1 Knapsack problem, built to answer a practical question rather than just implement solvers: **when and why should you pick one algorithm over another**, given problem size, time budget, and optimality requirements.

## What's in it

- 16 algorithms implemented from scratch (no solver libraries): exact (brute force, DP, DP top-down, branch & bound), approximation (FPTAS, 2 variants), greedy heuristics (4 sorting criteria), and metaheuristics (genetic algorithm, simulated annealing, adaptive variants, randomized greedy)
- 1197 benchmark runs across 100+ instances, 13 sizes (n = 4 to 10,000), 4 correlation structures (uncorrelated, strongly/weakly correlated, similar weights) to stress different algorithm weaknesses
- Statistical analysis: optimality rate, practicability limits, per-correlation-type performance, and a decision tree summarizing which algorithm to use in which context
- Reproducible: fixed seeds throughout, benchmark instances included in `benchmarks/`

## Main findings

| Question | Answer |
|---|---|
| Which algorithm is optimal and fastest below n≈5000? | Dynamic Programming (100% optimal, O(n×C)) |
| Which algorithm scales to n > 10,000? | Greedy heuristics (<1ms) or metaheuristics (85-98% of optimum, adjustable time) |
| Which greedy criterion to use? | Depends on correlation type — Greedy Ratio is near-optimal on strongly correlated instances (0.12% gap) but among the worst on others |
| Is FPTAS usable at scale? | No — see [Known Issues](#known-issues) |

Full decision tree and per-algorithm tables are in the notebook and below.

## Reproducing results

```bash
pip install -r requirements.txt

# Full re-run (regenerates instances + all 1197 benchmarks, ~30-60 min):
python run_benchmarks.py --generate

# Or just re-run against the benchmark instances already committed in benchmarks/:
python run_benchmarks.py

# Then open the notebook to view the analysis charts:
jupyter notebook knapsack_project.ipynb
```

`benchmark_results.csv` is already committed, so the notebook works out of the box without re-running anything.

## Reporting

- **Live dashboard:** [fryzim.github.io/benchmarking_knapsack01](https://fryzim.github.io/benchmarking_knapsack01/) — interactive time/quality-vs-size charts and greedy gap-to-optimum by correlation type, built from `benchmark_results.csv` (source in `docs/index.html`).
- **Power Query:** `reporting/power_query.m` — loads and types `benchmark_results.csv` for Power BI/Excel, adds algorithm-family and relative-quality columns.

## Project structure

```
src/
  models.py               Item, Problem, Solution
  generator.py             synthetic instance generator (3 correlation types)
  parser.py                reading .txt instances, discovering the benchmark suite
  algorithms/
    exact.py                 brute force, DP (bottom-up + top-down), branch and bound
    greedy.py                4 greedy heuristics + fractional relaxation
    approximation.py         FPTAS + adaptive epsilon
    metaheuristics.py        genetic algorithm, simulated annealing (+ adaptive variants), randomized
    __init__.py               registry: which algorithms run, up to which n
  benchmark.py              runs every algorithm against every discovered instance
  visualize.py              all plotting functions used in the notebook
  hyperparameters.py        exploratory hyperparameter-sensitivity helpers (see Known Issues)
run_benchmarks.py          CLI: (optionally) regenerate instances, run all benchmarks, save CSV
knapsack_project.ipynb     demo + analysis notebook (imports from src/, no algorithm code)
docs/index.html            live reporting dashboard (GitHub Pages)
reporting/power_query.m    Power Query (M) script for Power BI / Excel
benchmarks/
  generated/                instances generated for this study
  large_scale/, low_dimension/   standard reference instances
  *_optimum/                     known optimal solutions for the above
benchmark_results.csv       raw results of all 1197 runs
```

## Algorithms

### Exact (guaranteed optimal)
| Algorithm | Complexity | Practical limit |
|---|---|---|
| Brute Force | O(2^n) | n ≤ 23 |
| Dynamic Programming | O(n×C) | n ≤ 5000, small C |
| Branch and Bound | O(2^n) worst case | n ≤ 500 (pruning-dependent) |

### Approximation
| Algorithm | Guarantee | Practical limit |
|---|---|---|
| FPTAS (ε=0.05 / 0.1) | ≥ (1-ε)×OPT | n ≤ 100 (scaling bug, see below) |

### Greedy heuristics (<1ms)
Ratio (value/weight), Value, Weight, Fractional — performance ranges from 50% to 100% of optimum depending on correlation type; sorting criterion matters more than the algorithm itself.

### Metaheuristics (large instances, n > 1000)
Genetic Algorithm, Simulated Annealing, and adaptive variants of both — 85-98% of optimum, scales to n = 10,000+.

## Known issues

**FPTAS scaling bug (n > 100):** the scaling factor `K = (epsilon * v_max) / n` is too small for larger n, inflating the DP table instead of shrinking it (e.g. n=200 → 40M cells). Root cause identified (should be `K = max(1, (epsilon * v_max) / (2*n))`), documented but intentionally left unfixed to preserve the authenticity of the benchmark results discussed in the report.

**Branch and Bound bound() off-by-one:** `bound()` returns `0` whenever `current_weight >= problem.capacity`, instead of only when it *exceeds* capacity. This incorrectly discards the exact-capacity-full case, which can prune away the true optimum (e.g. items of weight 20 and 30 with capacity 50 — the optimal 20+30 split is pruned, and B&B returns a lower-value solution instead). Found while restructuring the code into `src/algorithms/exact.py`; not fixed here since it would change previously reported results, but worth fixing (`>` instead of `>=`) before trusting Branch and Bound's optimality on new instances.
