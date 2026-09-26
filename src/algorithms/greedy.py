"""Greedy heuristics: no optimality guarantee, but sub-millisecond even at n=10,000+."""
import time

from ..models import Solution


def greedy_by_value(problem):
    """Greedy by decreasing value. Favors high-value items, may ignore
    more profitable combinations of cheaper items."""
    start_time = time.time()

    sorted_items = sorted(enumerate(problem.items), key=lambda x: x[1].value, reverse=True)

    selected = []
    total_weight = 0
    total_value = 0

    for idx, item in sorted_items:
        if total_weight + item.weight <= problem.capacity:
            selected.append(idx)
            total_weight += item.weight
            total_value += item.value

    time_taken = time.time() - start_time
    sol = Solution(selected, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def greedy_by_weight(problem):
    """Greedy by increasing weight. Maximizes number of items; may ignore
    heavy but very valuable items."""
    start_time = time.time()

    sorted_items = sorted(enumerate(problem.items), key=lambda x: x[1].weight)

    selected = []
    total_weight = 0
    total_value = 0

    for idx, item in sorted_items:
        if total_weight + item.weight <= problem.capacity:
            selected.append(idx)
            total_weight += item.weight
            total_value += item.value

    time_taken = time.time() - start_time
    sol = Solution(selected, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def greedy_by_ratio(problem):
    """Greedy by decreasing value/weight ratio. The best greedy heuristic
    for 0-1: optimal strategy for fractional knapsack, good heuristic here."""
    start_time = time.time()

    sorted_items = sorted(enumerate(problem.items), key=lambda x: x[1].ratio(), reverse=True)

    selected = []
    total_weight = 0
    total_value = 0

    for idx, item in sorted_items:
        if total_weight + item.weight <= problem.capacity:
            selected.append(idx)
            total_weight += item.weight
            total_value += item.value

    time_taken = time.time() - start_time
    sol = Solution(selected, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / problem.capacity) * 100 if problem.capacity > 0 else 0
    return sol


def fractional_knapsack(problem):
    """Optimal greedy algorithm for the *fractional* relaxation of the problem
    (fractions of items are allowed). Serves as an upper bound for 0-1 Knapsack.
    """
    start_time = time.time()

    capacity = problem.capacity
    items = problem.items

    sorted_items = sorted(enumerate(items), key=lambda x: x[1].ratio(), reverse=True)

    total_value = 0.0
    total_weight = 0.0
    selected = []
    fractions = {}

    remaining_capacity = capacity

    for idx, item in sorted_items:
        if remaining_capacity <= 0:
            break

        if item.weight <= remaining_capacity:
            selected.append(idx)
            fractions[idx] = 1.0
            total_value += item.value
            total_weight += item.weight
            remaining_capacity -= item.weight
        else:
            fraction = remaining_capacity / item.weight
            fractions[idx] = fraction
            total_value += item.value * fraction
            total_weight += item.weight * fraction
            selected.append(idx)
            remaining_capacity = 0

    time_taken = time.time() - start_time

    sol = Solution(selected, total_value, total_weight, time_taken)
    sol.usage_percent = (total_weight / capacity) * 100 if capacity > 0 else 0
    sol.fractions = fractions
    sol.is_fractional = True

    return sol


def fractional_knapsack_bound(problem):
    """Upper bound of the 0-1 problem via fractional relaxation.

    Always ≥ the true optimum of the 0-1 problem; usable as a bounding
    function for Branch and Bound.
    """
    sorted_items = sorted(problem.items, key=lambda x: x.ratio(), reverse=True)

    total_value = 0.0
    remaining_capacity = problem.capacity

    for item in sorted_items:
        if remaining_capacity <= 0:
            break
        if item.weight <= remaining_capacity:
            total_value += item.value
            remaining_capacity -= item.weight
        else:
            total_value += item.value * (remaining_capacity / item.weight)
            break

    return total_value
