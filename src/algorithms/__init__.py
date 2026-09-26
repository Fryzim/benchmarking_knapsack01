"""Registry of all 16 implemented algorithms, with their size limits.

`ALL_ALGORITHMS` is what the benchmarking system iterates over; edit
`ALGORITHMS_CONFIG` to enable/disable an algorithm or change its max_n.
"""
from .approximation import fptas, fptas_adaptive, ftpas, ftpas_adaptive
from .exact import branch_and_bound, dynamic_programming, dynamic_programming_topdown, brute_force
from .greedy import fractional_knapsack, fractional_knapsack_bound, greedy_by_ratio, greedy_by_value, greedy_by_weight
from .metaheuristics import (
    genetic_algorithm,
    genetic_algorithm_adaptive,
    randomized_approach,
    simulated_annealing,
    simulated_annealing_adaptive,
)

ALGORITHMS_CONFIG = {
    # Exact algorithms
    'Brute Force':          {'enabled': True, 'max_n': 25},
    'Dynamic Programming':  {'enabled': True, 'max_n': 5000},
    'DP Top-Down':          {'enabled': True, 'max_n': 5000},
    'Branch and Bound':     {'enabled': True, 'max_n': 500},

    # Greedy algorithms
    'Greedy Ratio':         {'enabled': True, 'max_n': float('inf')},
    'Greedy Value':         {'enabled': True, 'max_n': float('inf')},
    'Greedy Weight':        {'enabled': True, 'max_n': float('inf')},
    'Fractional Knapsack':  {'enabled': True, 'max_n': float('inf')},

    # Stochastic/metaheuristic algorithms
    'Randomized':           {'enabled': True, 'max_n': float('inf')},
    'Genetic Algorithm':    {'enabled': True, 'max_n': float('inf')},
    'Genetic Adaptive':     {'enabled': True, 'max_n': float('inf')},
    'Simulated Annealing':  {'enabled': True, 'max_n': float('inf')},
    'SA Adaptive':          {'enabled': True, 'max_n': float('inf')},

    # FPTAS (approximation)
    'FPTAS (ε=0.1)':        {'enabled': True, 'max_n': float('inf')},
    'FPTAS (ε=0.05)':       {'enabled': True, 'max_n': float('inf')},
    'FPTAS Adaptive':       {'enabled': True, 'max_n': float('inf')},
}

ALGORITHMS_FUNCS = {
    'Brute Force':          brute_force,
    'Dynamic Programming':  dynamic_programming,
    'DP Top-Down':          dynamic_programming_topdown,
    'Branch and Bound':     branch_and_bound,
    'Greedy Ratio':         greedy_by_ratio,
    'Greedy Value':         greedy_by_value,
    'Greedy Weight':        greedy_by_weight,
    'Fractional Knapsack':  fractional_knapsack,
    'Randomized':           lambda p: randomized_approach(p, iterations=100),
    'Genetic Algorithm':    lambda p: genetic_algorithm(p, population_size=100, generations=50),
    'Genetic Adaptive':     genetic_algorithm_adaptive,
    'Simulated Annealing':  lambda p: simulated_annealing(p, initial_temp=1000, cooling_rate=0.995),
    'SA Adaptive':          simulated_annealing_adaptive,
    'FPTAS (ε=0.1)':        lambda p: ftpas(p, epsilon=0.1),
    'FPTAS (ε=0.05)':       lambda p: ftpas(p, epsilon=0.05),
    'FPTAS Adaptive':       ftpas_adaptive,
}

ALL_ALGORITHMS = [
    (name, ALGORITHMS_FUNCS[name], config['max_n'])
    for name, config in ALGORITHMS_CONFIG.items()
    if config['enabled']
]
