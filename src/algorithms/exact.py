"""Exact algorithms: always return the optimal solution, at the cost of scalability."""
import sys
import time
from itertools import combinations

from ..models import Solution


def brute_force(problem):
    """Brute force algorithm for the 0-1 Knapsack problem.

    Explores all possible combinations of items to find the optimal
    solution. Guarantees optimal solution but with exponential complexity.

    Note:
        Do not use for n > 20-25 items (prohibitive time).
    """
    start_time = time.time()

    best_value = 0
    best_weight = 0
    best_items = []

    for size in range(problem.n + 1):
        for combo in combinations(range(problem.n), size):
            total_weight = sum(problem.items[i].weight for i in combo)
            total_value = sum(problem.items[i].value for i in combo)

            if total_weight <= problem.capacity and total_value > best_value:
                best_value = total_value
                best_weight = total_weight
                best_items = list(combo)

    time_taken = time.time() - start_time
    sol = Solution(best_items, best_value, best_weight, time_taken)
    sol.usage_percent = (best_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def dynamic_programming(problem):
    """Bottom-Up Dynamic Programming for the 0-1 Knapsack problem.

    Builds a memoization table iteratively starting from the simplest
    sub-problems to the complete problem. Guarantees optimal solution
    in pseudo-polynomial time.

    Returns:
        Solution object with optimal solution, or None if the matrix
        would be too large (memory protection).
    """
    start_time = time.time()

    n = problem.n
    C = problem.capacity

    total_cells = n * C
    if total_cells > 10_000_000:
        print(f"DP Skip: matrix too large ({n}×{C:,} = {total_cells:,})")
        return None

    estimated_mb = (total_cells * 8) / (1024 * 1024)
    if estimated_mb > 500:
        print(f"DP Skip: memory > 500 MB ({estimated_mb:.0f} MB)")
        return None

    dp = [[0 for _ in range(C + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = problem.items[i - 1]
        for w in range(C + 1):
            dp[i][w] = dp[i - 1][w]
            if item.weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - item.weight] + item.value)

    # Reconstruction
    selected = []
    w = C
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= problem.items[i - 1].weight

    total_value = dp[n][C]
    total_weight = sum(problem.items[i].weight for i in selected)

    time_taken = time.time() - start_time
    sol = Solution(selected, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def dynamic_programming_topdown(problem):
    """Top-Down Dynamic Programming with memoization.

    Advantages over Bottom-Up:
    - Only computes necessary sub-problems
    - More intuitive (follows recursive definition)
    - Can be faster if not all sub-problems are needed
    """
    start_time = time.time()

    n = problem.n
    C = problem.capacity
    items = problem.items

    # Protection against large instances
    total_cells = n * C
    if total_cells > 10_000_000:
        print(f"DP Top-Down Skip: matrix too large ({n}×{C:,} = {total_cells:,})")
        return None

    # Increase recursion limit if necessary
    old_limit = sys.getrecursionlimit()
    if n > old_limit - 100:
        sys.setrecursionlimit(n + 1000)

    # Cache for memoization: memo[i][w] = max value with items 0..i-1 and capacity w
    memo = {}

    def knapsack(i, w):
        """Recursive function with memoization."""
        if i == 0 or w == 0:
            return 0

        if (i, w) in memo:
            return memo[(i, w)]

        item = items[i - 1]

        if item.weight > w:
            result = knapsack(i - 1, w)
        else:
            result = max(
                knapsack(i - 1, w),  # Don't take
                knapsack(i - 1, w - item.weight) + item.value,  # Take
            )

        memo[(i, w)] = result
        return result

    optimal_value = knapsack(n, C)

    if optimal_value == 0:
        time_taken = time.time() - start_time
        return Solution([], 0, 0, time_taken)

    # Solution reconstruction
    selected = []
    w = C
    for i in range(n, 0, -1):
        if knapsack(i, w) != knapsack(i - 1, w):
            selected.append(i - 1)
            w -= items[i - 1].weight

    total_weight = sum(items[i].weight for i in selected)
    time_taken = time.time() - start_time

    sys.setrecursionlimit(old_limit)

    sol = Solution(selected, optimal_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / C) * 100 if C > 0 else 0
    return sol


def branch_and_bound(problem):
    """Branch and Bound algorithm for the 0-1 Knapsack problem.

    Intelligently explores the solution tree using an upper bound
    (fractional relaxation) to prune unpromising branches. Guarantees
    optimal solution.

    Strategy:
    - Sort items by decreasing value/weight ratio
    - Calculate upper bound via fractional relaxation
    - Prune branches where bound < best known solution
    """
    start_time = time.time()

    sorted_indices = sorted(range(problem.n),
                             key=lambda i: problem.items[i].ratio(),
                             reverse=True)

    best_value = 0
    best_solution = []

    def bound(level, current_weight, current_value):
        if current_weight >= problem.capacity:
            return 0

        value_bound = current_value
        total_weight = current_weight

        for i in range(level, problem.n):
            idx = sorted_indices[i]
            item = problem.items[idx]

            if total_weight + item.weight <= problem.capacity:
                total_weight += item.weight
                value_bound += item.value
            else:
                remaining = problem.capacity - total_weight
                value_bound += item.value * (remaining / item.weight)
                break

        return value_bound

    def branch(level, current_weight, current_value, current_items):
        nonlocal best_value, best_solution

        if level == problem.n:
            if current_value > best_value:
                best_value = current_value
                best_solution = current_items[:]
            return

        idx = sorted_indices[level]
        item = problem.items[idx]

        if current_weight + item.weight <= problem.capacity:
            new_value = current_value + item.value
            if bound(level + 1, current_weight + item.weight, new_value) > best_value:
                current_items.append(idx)
                branch(level + 1, current_weight + item.weight, new_value, current_items)
                current_items.pop()

        if bound(level + 1, current_weight, current_value) > best_value:
            branch(level + 1, current_weight, current_value, current_items)

    branch(0, 0, 0, [])

    total_weight = sum(problem.items[i].weight for i in best_solution)
    time_taken = time.time() - start_time

    sol = Solution(best_solution, best_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol
