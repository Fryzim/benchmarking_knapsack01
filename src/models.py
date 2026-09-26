"""Core data structures shared by every algorithm and by the benchmarking system."""


class Item:
    """Represents an item with its weight and value."""

    def __init__(self, item_id, weight, value):
        self.id = item_id
        self.weight = weight
        self.value = value

    def ratio(self):
        return self.value / self.weight if self.weight > 0 else 0

    def __repr__(self):
        return f"Item({self.id}, w={self.weight}, v={self.value})"


class Problem:
    """Represents a knapsack problem instance."""

    def __init__(self, items, capacity):
        self.items = items
        self.capacity = capacity
        self.n = len(items)


class Solution:
    """Represents a solution to the problem."""

    def __init__(self, selected_items, total_value, total_weight, time_taken):
        self.selected_items = selected_items
        self.total_value = total_value
        self.total_weight = total_weight
        self.time = time_taken
        self.usage_percent = (total_weight / 1.0) * 100  # Overwritten by callers with real capacity
