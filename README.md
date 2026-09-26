# Knapsack 0/1 Project - Comparative Algorithm

**Team:** Chaabane, Arman, Bartosz, Ahmed  
**Date:** December 2025
**Course:** Advanced Algorithms

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Table of Contents

- [About](#about)
- [Reproducing Results](#reproducing-results)
- [Detailed Installation](#detailed-installation)
- [Complete Usage Guide](#complete-usage-guide)
- [Project Structure](#project-structure)
- [Implemented Algorithms](#implemented-algorithms)
- [Data and Benchmarks](#data-and-benchmarks)
- [Results and Analysis](#results-and-analysis)
- [Known Issues and Limitations](#known-issues-and-limitations)

---

## About

This project presents a **comprehensive comparative analysis** of 16 algorithms to solve the Knapsack 0/1 problem. Our goal is to understand **when and why** to use each algorithm depending on the context (problem size, time constraints, optimality requirements).

### Main Features

- **16 algorithms** implemented from scratch (no external libraries for algorithms)
- **4 correlation types** tested to cover different use cases
- **1029 benchmark results** on 100+ instances
- **13 different sizes** (n = 4 to 10,000 items)
- **Statistical analyses**
- **Practical decision guide** to choose the optimal algorithm
- **100% reproducible code** with fixed seeds

### Our Contribution

Beyond the technical implementation, we created a **practical guide** showing **when and why** to use each algorithm. Each analysis answers a concrete question, avoiding complex statistics without utility.

---

## Reproducing Results

### Complete Reproduction

**Estimated duration:** ~30-60 minutes (depending on your machine)

```bash
# 1. Launch Jupyter Notebook
jupyter notebook knapsack_project.ipynb

# 2. Execute cells in order:
#    - Cells 1-4: Imports and data structures
#    - Cells 5-30: Implementation of 16 algorithms
#    - Cell 42: Benchmark generation (OPTIONAL - already provided)
#    - Cell 48: Benchmark execution (~30 min)
#    - Cells 50-65: Analysis and visualizations
```

**Important Note:** Complete benchmark execution takes time.

---

## Detailed Installation

### Prerequisites

- **Python 3.8 or higher** (tested on 3.8, 3.9, 3.10, 3.11)
- **pip** (Python package manager)
- **Jupyter Notebook** or **JupyterLab**
- **8 GB RAM minimum** (16 GB recommended for generating new benchmarks)

### Check Your Python Installation

```bash
python --version  # Should display Python 3.8 or higher
pip --version     # Should display pip 20.0 or higher
```

### Installation

```bash
# Basic scientific libraries
pip install numpy
pip install pandas
pip install scipy

# Visualization
pip install matplotlib
pip install seaborn

# Machine Learning
pip install scikit-learn

# Jupyter
pip install jupyter
pip install notebook
```

#### 3. Verify Installation

```python
# Open Python and test imports
python -c "
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon
from sklearn.model_selection import ParameterGrid
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
print('All dependencies are correctly installed!')
"
```

---

## Complete Usage Guide

### Step 1: Understanding the Notebook Structure

The `knapsack_project.ipynb` notebook is organized in 8 sections:

```
Section 1: Configuration and Imports
Section 2: Data Structures (Item, Problem, Solution)
Section 3: Benchmark Parsing
Section 4: Implementation of 16 Algorithms
Section 5: Benchmarking System
Section 6: Test Instance Generation
Section 7: Visualizations and Analysis
Section 8: Hyperparameter Optimization (not working)
```

### Step 2: Execute Algorithms

#### A. Test an Algorithm on a Simple Instance

```python
# Create a manual instance
items = [
    Item(0, weight=10, value=60),
    Item(1, weight=20, value=100),
    Item(2, weight=30, value=120)
]
problem = Problem(items, capacity=50)

# Test different algorithms
solution_dp = dynamic_programming(problem)
solution_greedy = greedy_ratio(problem)
solution_genetic = genetic_algorithm(problem, seed=42)

# Compare results
print(f"DP:      value={solution_dp.total_value}, time={solution_dp.time*1000:.2f}ms")
print(f"Greedy:  value={solution_greedy.total_value}, time={solution_greedy.time*1000:.2f}ms")
print(f"Genetic: value={solution_genetic.total_value}, time={solution_genetic.time*1000:.2f}ms")
```

#### B. Load and Test a Benchmark Instance

```python
# Load an instance from a file
problem = parse_benchmark_file('benchmarks/generated/uncorrelated_n100_c5000.txt')

print(f"Instance loaded: n={problem.n}, capacity={problem.capacity}")

# Test an algorithm
solution = genetic_algorithm(
    problem,
    population_size=100,
    generations=50,
    mutation_rate=0.02,
    crossover_rate=0.8,
    seed=42
)

print(f"Value: {solution.total_value}")
print(f"Weight: {solution.total_weight}/{problem.capacity}")
print(f"Time: {solution.time * 1000:.2f} ms")
print(f"Selected items: {len(solution.selected_items)}")
```

### Step 3: Generate New Benchmarks (OPTIONAL)

### Step 4: Execute Complete Benchmarks

```python
# WARNING: This takes ~30-60 minutes
results_df = run_all_benchmarks()

# Results are automatically saved in:
# - benchmarks/generated
# Benchmarks with known results are also present in benchmarks/
```

### Step 5: Analyze Results

#### Instance Batch

Our benchmark generator created **66 instances** strategically distributed by size and correlation type:

```python
# =============================================================================
# BENCHMARK GENERATOR
# =============================================================================
# Types: 'uncorrelated', 'weakly_correlated', 'strongly_correlated'
# =============================================================================

# MEDIUM size instances (n = 100-500)
generate_benchmarks(n=100,  capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=6)
generate_benchmarks(n=200,  capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=2)
generate_benchmarks(n=500,  capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=5)

# LARGE size instances (n = 1000-5000)
generate_benchmarks(n=1000, capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=3)
generate_benchmarks(n=2000, capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=3)
generate_benchmarks(n=5000, capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=2)

# VERY LARGE size instance (n = 10000)
generate_benchmarks(n=10000, capacity=1000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'])

# Commented examples for other possible configurations:
# generate_benchmarks(n=100, capacity=5000, correlation='uncorrelated')
# generate_benchmarks(n=100, capacity=5000, correlation='strongly_correlated', count=5)
# generate_benchmarks(n=100, capacity=5000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'])
# generate_benchmarks(n=100, capacity=5000, correlation=['uncorrelated', 'strongly_correlated', 'weakly_correlated'], count=5)
```

#### C. Generate Notebook Visualizations

Simply execute cells 50-65 of the notebook. They generate:

- Execution times
- Test coverage heatmap
- Performance by size
- Time-quality trade-off
- Predictive regression
- Statistical comparisons
- Hyperparameter optimization (not working correctly, see report)

---

## Project Structure

```
knapsack_project/
│
├── knapsack_project.ipynb          # MAIN NOTEBOOK
│
└── benchmarks/           
    ├── generated/                   # Generated instances
    │   ├── *.txt
    │   ├── *.txt
    │   ├── *.txt
    │   └── *.txt
    │
    ├── large_scale/                 # Large size instances
    ├── large_scale_optimum/         # Optimal solutions for large_scale
    ├── low_dimension/               # Small size instances
    └── low_dimension_optimum/       # Optimal solutions for low_dimension      
```

---

## Implemented Algorithms

### 1. Exact Algorithms (Guaranteed Optimality)

| Algorithm | Time Complexity | Space Complexity | Practical Limit | Implementation |
|-----------|----------------|------------------|-----------------|----------------|
| **Brute Force** | O(2^n) | O(n) | n ≤ 23 | Cell 6 |
| **Dynamic Programming** | O(n×C) | O(n×C) | n ≤ 5000, small C | Cell 7 |
| **DP Top-Down** | O(n×C) | O(n×C) | n ≤ 5000 | Cell 8 |
| **Branch and Bound** | O(2^n) ~ O(n log n) | O(n) | n ≤ 500 (variable) | Cell 9 |

**When to Use:**
- Brute Force: Small instances (n ≤ 20), verification
- DP: Medium instances (n ≤ 1000) with moderate capacity
- B&B: Problems with good upper bound

---

### 2. Approximation Algorithms (Theoretical Guarantee)

| Algorithm | Complexity | Guarantee | Implementation |
|-----------|------------|-----------|----------------|
| **FPTAS (ε=0.1)** | O(n²/ε) | ≥ (1-ε)×OPT | Cell 18 |
| **FPTAS (ε=0.05)** | O(n²/ε) | ≥ (1-ε)×OPT | Cell 18 |
| **FPTAS Adaptive** | O(n²/ε) | ≥ (1-ε)×OPT | Cell 19 |

**Known Limitation:** Our FPTAS implementation has a scaling bug limiting n ≤ 100. See [Known Issues](#known-issues-and-limitations) section.

**When to Use:**
- Need for theoretical guarantee
- Medium instances (n ≤ 500 after correction)
- Adjustable quality/time trade-off via ε

---

### 3. Greedy Heuristics (Ultra-Fast)

| Algorithm | Sort By | Complexity | Performance | Implementation |
|-----------|---------|------------|-------------|----------------|
| **Greedy Ratio** | value/weight ↓ | O(n log n) | 70-100% by type | Cell 10 |
| **Greedy Value** | value ↓ | O(n log n) | 60-95% | Cell 11 |
| **Greedy Weight** | weight ↑ | O(n log n) | 50-90% | Cell 12 |
| **Fractional** | ratio ↓ | O(n log n) | Upper bound | Cell 13 |

**When to Use:**
- Strict time constraint (< 1 ms)
- Greedy Ratio: strongly_correlated (quasi-optimal)
- Greedy Value: uncorrelated, inverse_strongly
- Greedy Weight: Avoid on inverse_strongly (very poor)

---

### 4. Metaheuristics (Large Instances)

| Algorithm | Key Parameters | Time | Performance | Implementation |
|-----------|----------------|------|-------------|----------------|
| **Genetic Algorithm** | pop=100, gen=50 | 100-500 ms | 85-98% | Cell 14 |
| **Genetic Adaptive** | Adaptive | 100-500 ms | 87-99% (+ stable) | Cell 15 |
| **Simulated Annealing** | T=1000, α=0.995 | 50-200 ms | 85-97% | Cell 16 |
| **SA Adaptive** | Adaptive | 50-200 ms | 88-98% (+ stable) | Cell 17 |
| **Randomized** | Greedy + random | 5-20 ms | 70-90% | Cell 20 |

**When to Use:**
- Large instances (n > 1000)
- Flexible time (a few seconds OK)
- Need for stability → Adaptive versions

---

## Data and Benchmarks

### Benchmark File Format

Our `.txt` files follow this standard format:

```
100 5000
# n capacity
# Then n lines with: value weight
60 10
100 20
120 30
...
```

### Generated Correlation Types

We generated **4 different types** to test algorithms in various contexts:

#### 1. **Uncorrelated**
```python
weights = random(1, 100)
values = random(1, 100)  # Independent
```
**Usage:** General case, no particular structure

---

#### 2. **Strongly Correlated**
```python
weights = random(1, 100)
values = weights  # Exactly equal
```
**Usage:** Tests if Greedy Ratio finds optimal (it should!)

---

#### 3. **Weakly Correlated**
```python
weights = random(1, 100)
values = weights + noise(-15, 15)  # Close but with noise
```
**Usage:** Tests robustness to noise

---

#### 4. **Similar Weights**
```python
weights = random(47, 53)  # All close to 50
values = random(1, 100)   # Varied values
```
**Usage:** Forces Greedy Weight to be mediocre

---

## Results and Analysis

### Analysis 1: Optimal Solution Rate

**Question:** Which algorithm finds the optimum most often?

| Algorithm | % Optimal | Avg Gap | Verdict |
|-----------|-----------|---------|---------|
| Dynamic Programming | 100.0% | 0.00% | ✓ OPTIMAL |
| DP Top-Down | 100.0% | 0.00% | ✓ OPTIMAL |
| Branch and Bound | 100.0% | 0.00% | ✓ OPTIMAL |
| FPTAS (ε=0.05) | 99.2% | 0.15% | ~ QUASI-OPTIMAL |
| FPTAS (ε=0.1) | 95.8% | 0.31% | ~ QUASI-OPTIMAL |
| Greedy Ratio | 78.5% | 2.34% | ○ GOOD |
| Genetic Adaptive | 12.3% | 4.21% | ○ APPROX |
| Simulated Annealing | 8.7% | 5.12% | ○ APPROX |

---

### Analysis 2: Practicability Limits (< 5 seconds)

**Question:** Up to what size can I use each algorithm?

| Algorithm | Max Size (n) | Time at Max | Confirmed Complexity |
|-----------|--------------|-------------|---------------------|
| Brute Force | 23 | 4.8s | ✓ O(2^n) |
| Branch and Bound | 500 | Variable | ✓ Pruning dependent |
| Dynamic Programming | 5000 | Depends on C | ✓ O(n×C) |
| FPTAS | 100 | 2.2s (BUG) | ✗ Should be more |
| Greedy | 10000+ | < 1s | ✓ O(n log n) |
| Metaheuristics | 10000+ | Adjustable | ✓ Scalable |

---

### Analysis 3: Greedy Performance by Type

**Question:** Which greedy to choose according to problem type?

**Results:**

| Correlation Type | Best Greedy | Gap | Worst Greedy | Gap |
|------------------|-------------|-----|--------------|-----|
| **Strongly Correlated** | Greedy Ratio | 0.12% ✓ | Greedy Weight | 8.45% |
| **Uncorrelated** | Greedy Value | 3.78% | Greedy Weight | 9.21% |
| **Weakly Correlated** | Greedy Ratio | 1.89% | Greedy Weight | 7.56% |
| **Similar Weights** | Greedy Value/Ratio | 4.12% | Greedy Weight | 12.34% |

**Remarks:**
- Greedy Ratio **quasi-optimal** on strongly_correlated (0.12% gap)
- **Sorting criterion** is crucial depending on data structure

---

### Analysis 4: Practical Decision Tree

**Question:** Which algorithm to choose in my context?

```
┌─ Need GUARANTEED OPTIMALITY?
│
├─ YES → Do I have n×C < 10 million?
│        │
│        ├─ YES → DYNAMIC PROGRAMMING
│        │        ✓ Guaranteed optimal
│        │        ✓ Predictable O(n×C)
│        │        ✗ Memory limited
│        │
│        └─ NO → BRANCH AND BOUND
│                 ✓ Guaranteed optimal
│                 ~ Variable time (pruning)
│                 ✗ Can be slow
│
└─ NO → What is my MAIN CONSTRAINT?
         │
         ├─ STRICT TIME (<1ms)
         │  │
         │  └─ What TYPE of problem?
         │     ├─ strongly_correlated → GREEDY RATIO ✓ Quasi-optimal
         │     ├─ uncorrelated → GREEDY VALUE
         │     └─ other → GREEDY RATIO (default)
         │
         ├─ QUALITY IMPORTANT (few seconds OK)
         │  │
         │  ├─ n < 200 → FPTAS (ε=0.05)
         │  │            ✓ Guarantee (1-ε)×OPT
         │  │            ✓ Polynomial time
         │  │
         │  └─ n ≥ 200 → METAHEURISTIC
         │               ├─ Need STABILITY → Genetic/SA Adaptive
         │               └─ Max performance → Genetic Algorithm
         │
         └─ LARGE INSTANCE (n > 1000)
            │
            └─ SIMULATED ANNEALING or GENETIC ALGORITHM
               ✓ Only ones that scale
               ~ Adjustable time
               ~ Quality not guaranteed but good (85-98%)
```

**Summary Table:**

| Criterion | DP | B&B | Greedy | FPTAS | Genetic | SA |
|-----------|----|----|--------|-------|---------|-----|
| Optimal | ✓ | ✓ | ✗ | ~ | ✗ | ✗ |
| Fast (<1ms) | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Scalable (n>1000) | ✗ | ✗ | ✓ | ~ | ✓ | ✓ |
| Stable | ✓ | ✓ | ✓ | ✓ | ~ | ~ |
| Memory OK | ✗ | ✓ | ✓ | ~ | ✓ | ✓ |

---

## Known Issues and Limitations

### FPTAS - Malfunction Beyond n=100

**Observed Symptoms:**
- FPTAS does not work for n > 100
- Abnormally high execution times:
  - n=100, ε=0.05: 2222 ms (vs 21 ms for DP)
  - n=100, ε=0.1: 1087 ms (vs 21 ms for DP)
- Ratio: FPTAS is 100× slower than DP while it should be comparable!

**Identified Cause:**

The error comes from the scaling formula in cell 18:

```python
# OUR CODE (INCORRECT):
K = (epsilon * v_max) / n

# Example: n=200, v_max=1000, ε=0.1
# K = (0.1 × 1000) / 200 = 0.5  ← K too small!

# Result:
# scaled_value = floor(500 / 0.5) = 1000  ← 2x larger!
# V_scaled = Σ scaled_values ≈ 200,000   ← Explosion!
# DP table: n × V_scaled = 200 × 200,000 = 40M cells
```

**Proposed Solution:**

```python
# CORRECT FORMULA:
K = max(1, (epsilon * v_max) / (2 * n))

# Or adjust epsilon for large instances:
if n > 100:
    epsilon_adjusted = epsilon * (n / 100)
    K = max(1, (epsilon_adjusted * v_max) / n)
```

**Impact on Results:**
- Coverage heatmap: FPTAS cells empty for n > 100
- Performance graphs: FPTAS absent from large sizes

**Status:** **Identified and documented** in the report (section 5.5). Not corrected in the code to preserve authenticity of presented results.

---
