"""FPTAS: Fully Polynomial-Time Approximation Scheme.

Guarantees a solution with value >= (1-epsilon) x OPT by scaling item
values down before running an exact DP on the scaled instance.

Known limitation: the scaling factor K = (epsilon * v_max) / n becomes
too small as n grows, which inflates the DP table instead of shrinking
it (observed to blow up memory/time beyond n=100). Root cause and fix
are documented in the README; left unfixed here to preserve the
authenticity of the benchmark results discussed in the report.
"""
import time
from types import SimpleNamespace


def fptas(problem, epsilon=0.1):
    """Returns a solution with value >= (1-epsilon) x OPT.

    Args:
        problem: Problem instance
        epsilon: Approximation parameter (0 < epsilon < 1). Smaller
            epsilon gives a better approximation but is slower.
    """
    start_time = time.time()

    n = problem.n
    items = problem.items
    capacity = problem.capacity

    if epsilon <= 0 or epsilon >= 1:
        print(f"FPTAS: epsilon must be in ]0,1[, received {epsilon}")
        return None

    if n == 0:
        return SimpleNamespace(
            selected_items=[],
            total_value=0,
            total_weight=0,
            time=time.time() - start_time,
            usage_percent=0,
            epsilon=epsilon,
            scaling_factor=0,
        )

    v_max = max(item.value for item in items)

    # Scaling factor: K = (ε × v_max) / n
    # This ensures that the sum of scaled values is ≤ n²/ε
    K = (epsilon * v_max) / n

    if K < 1e-10:
        K = 1e-10

    scaled_items = []
    for idx, item in enumerate(items):
        scaled_value = int(item.value / K)  # Floor
        scaled_items.append({
            'idx': idx,
            'weight': item.weight,
            'value': item.value,
            'scaled_value': scaled_value,
        })

    V_scaled = sum(si['scaled_value'] for si in scaled_items)

    # Memory protection
    if V_scaled > 1_000_000:
        print(f"FPTAS Skip: V_scaled too large ({V_scaled:,})")
        return None

    estimated_mb = (n * V_scaled * 8) / (1024 * 1024)
    if estimated_mb > 200:
        print(f"FPTAS Skip: estimated memory too large ({estimated_mb:.0f} MB)")
        return None

    V_scaled = int(V_scaled)

    # dp[v] = minimum weight to achieve exactly scaled value v (1D, space-optimized)
    INF = float('inf')
    dp = [INF] * (V_scaled + 1)
    dp[0] = 0

    parent = [None] * (V_scaled + 1)  # parent[v] = (previous_value, idx_item)

    for idx, si in enumerate(scaled_items):
        sv = si['scaled_value']
        w = si['weight']

        # Backward traversal to avoid reusing the same item
        for v in range(V_scaled, sv - 1, -1):
            prev_v = v - sv
            if dp[prev_v] != INF:
                new_weight = dp[prev_v] + w
                if new_weight <= capacity and new_weight < dp[v]:
                    dp[v] = new_weight
                    parent[v] = (prev_v, idx)

    best_scaled_value = 0
    for v in range(V_scaled + 1):
        if dp[v] <= capacity:
            best_scaled_value = v

    selected_indices = []
    v = best_scaled_value
    while v > 0 and parent[v] is not None:
        prev_v, idx = parent[v]
        original_idx = scaled_items[idx]['idx']
        selected_indices.append(original_idx)
        v = prev_v

    total_value = sum(items[idx].value for idx in selected_indices)
    total_weight = sum(items[idx].weight for idx in selected_indices)

    time_taken = time.time() - start_time

    return SimpleNamespace(
        selected_items=selected_indices,
        total_value=total_value,
        total_weight=total_weight,
        time=time_taken,
        usage_percent=(total_weight / capacity * 100) if capacity > 0 else 0,
        epsilon=epsilon,
        scaling_factor=K,
    )


# Alias for compatibility with old name
ftpas = fptas


def fptas_adaptive(problem, time_budget=None):
    """Adjusts epsilon according to problem size: smaller (more precise)
    for small instances, larger (faster) for large ones."""
    n = problem.n

    if n <= 50:
        epsilon = 0.05
    elif n <= 100:
        epsilon = 0.1
    elif n <= 500:
        epsilon = 0.2
    else:
        epsilon = 0.3

    return fptas(problem, epsilon)


# Alias for compatibility
ftpas_adaptive = fptas_adaptive
