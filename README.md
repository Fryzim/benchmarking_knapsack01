# Knapsack 0/1 — Comparative Benchmark of 16 Algorithms

**Team:** Chaabane, Arman, Bartosz, Ahmed · **Course:** Advanced Algorithms · December 2025

Comparative study of 16 algorithms for the 0/1 Knapsack problem, built to answer a practical question rather than just implement solvers: **when and why should you pick one algorithm over another**, given problem size, time budget, and optimality requirements.

## What's in it

- 16 algorithms implemented from scratch (no solver libraries): exact (brute force, DP, DP top-down, branch & bound), approximation (FPTAS, 2 variants), greedy heuristics (4 sorting criteria), and metaheuristics (genetic algorithm, simulated annealing, adaptive variants, randomized greedy)
- 1029 benchmark runs across 100+ instances, 13 sizes (n = 4 to 10,000), 4 correlation structures (uncorrelated, strongly/weakly correlated, similar weights) to stress different algorithm weaknesses
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
pip install numpy pandas scipy matplotlib seaborn scikit-learn jupyter
jupyter notebook knapsack_project.ipynb
```

Run cells in order. Benchmark instances are already provided in `benchmarks/`, so the full ~30-60 min benchmark run is optional — everything can be reproduced from existing data.

## Project structure

```
knapsack_project.ipynb     notebook: implementations, benchmarking, analysis
benchmarks/
  generated/                instances generated for this study
  large_scale/, low_dimension/   standard reference instances
  *_optimum/                     known optimal solutions for the above
benchmark_results.csv       raw results of all 1029 runs
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
