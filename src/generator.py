"""Generation of synthetic 0/1 Knapsack benchmark instances.

Supports three correlation structures between weights and values
(uncorrelated, weakly correlated, strongly correlated), which stress
different weaknesses in greedy heuristics.
"""
import os
from dataclasses import dataclass
from typing import List, Literal, Optional

import numpy as np

GENERATED_DIR = "benchmarks/generated"


@dataclass
class KnapsackInstance:
    n: int
    capacity: int
    weights: List[int]
    values: List[int]
    correlation_type: str

    def __str__(self):
        return f"KnapsackInstance(n={self.n}, capacity={self.capacity}, type={self.correlation_type})"


class KnapsackBenchmarkGenerator:
    CORRELATION_TYPES = [
        'uncorrelated',
        'weakly_correlated',
        'strongly_correlated',
    ]

    def __init__(self):
        self.rng = np.random.default_rng()

    def generate(self, n: int, R: int = 1000, capacity: Optional[int] = None,
                 capacity_ratio: float = 0.5, correlation_type: str = 'uncorrelated',
                 correlation_param: float = 100.0) -> KnapsackInstance:
        if correlation_type not in self.CORRELATION_TYPES:
            raise ValueError(f"Unknown type: {correlation_type}. Options: {self.CORRELATION_TYPES}")

        weights = self._generate_weights(n, R, correlation_type, correlation_param)
        values = self._generate_values(weights, R, correlation_type, correlation_param)

        if capacity is None:
            capacity = int(capacity_ratio * sum(weights))
        capacity = max(1, capacity)

        return KnapsackInstance(n=n, capacity=capacity, weights=weights.tolist(),
                                 values=values.tolist(), correlation_type=correlation_type)

    def _generate_weights(self, n: int, R: int, correlation_type: str, correlation_param: float) -> np.ndarray:
        weights = self.rng.integers(1, R + 1, n)
        return weights.astype(int)

    def _generate_values(self, weights: np.ndarray, R: int, correlation_type: str, correlation_param: float) -> np.ndarray:
        n = len(weights)
        if correlation_type == 'uncorrelated':
            values = self.rng.integers(1, R + 1, n)
        elif correlation_type == 'weakly_correlated':
            noise = self.rng.integers(-int(correlation_param), int(correlation_param) + 1, n)
            values = np.maximum(weights + noise, 1)
        elif correlation_type == 'strongly_correlated':
            values = weights + int(correlation_param)
        return values.astype(int)

    def _build_filename(self, instance: KnapsackInstance, index: int = None, format: str = 'standard') -> str:
        ext = '.kp' if format == 'kp' else '.txt'
        base = f"{instance.correlation_type}_n{instance.n}_c{instance.capacity}"
        if index is not None:
            return f"{base}_{index:03d}{ext}"
        return f"{base}{ext}"

    def save_to_file(self, instance: KnapsackInstance, filepath: str = None,
                      index: int = None, format: Literal['standard', 'kp'] = 'standard') -> str:
        if filepath is None:
            filepath = os.path.join(GENERATED_DIR, self._build_filename(instance, index, format))

        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        with open(filepath, 'w') as f:
            if format == 'standard':
                f.write(f"{instance.n} {instance.capacity}\n")
                for v, w in zip(instance.values, instance.weights):
                    f.write(f"{v} {w}\n")
            elif format == 'kp':
                f.write(f"\n{instance.n}\n{instance.capacity}\n\n")
                for v, w in zip(instance.values, instance.weights):
                    f.write(f"{v} {w}\n")
        return filepath


def generate_benchmarks(n: int, capacity: int = None, correlation='uncorrelated',
                         R: int = 1000, count: int = 1, format: str = 'standard') -> List[KnapsackInstance]:
    """Generates one or more benchmark files.

    Args:
        n: Number of items
        capacity: Knapsack capacity (None = 50% of sum of weights)
        correlation: Type or list of types ('uncorrelated', 'weakly_correlated', 'strongly_correlated')
        R: Max weight [1, R]
        count: Number of files to generate per type
        format: 'standard' (.txt) or 'kp'
    """
    generator = KnapsackBenchmarkGenerator()
    instances = []

    correlations = [correlation] if isinstance(correlation, str) else correlation

    for corr_type in correlations:
        for i in range(count):
            instance = generator.generate(n=n, R=R, capacity=capacity, correlation_type=corr_type)
            index = i + 1 if count > 1 else None
            generator.save_to_file(instance, index=index, format=format)
            instances.append(instance)

    return instances
