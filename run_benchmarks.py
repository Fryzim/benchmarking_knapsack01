"""CLI entry point: (optionally) generate benchmark instances, then run
every enabled algorithm against every discovered instance and save the
results to benchmark_results.csv.

Usage:
    python run_benchmarks.py              # run against existing benchmarks/
    python run_benchmarks.py --generate    # regenerate benchmarks/generated/ first
"""
import argparse

from src.benchmark import run_all_benchmarks
from src.generator import generate_benchmarks


def generate_all_instances():
    """Regenerates the same 66-instance suite used for this study."""
    correlations = ['uncorrelated', 'strongly_correlated', 'weakly_correlated']
    generate_benchmarks(n=100, capacity=1000, correlation=correlations, count=6)
    generate_benchmarks(n=200, capacity=1000, correlation=correlations, count=2)
    generate_benchmarks(n=500, capacity=1000, correlation=correlations, count=5)
    generate_benchmarks(n=1000, capacity=1000, correlation=correlations, count=3)
    generate_benchmarks(n=2000, capacity=1000, correlation=correlations, count=3)
    generate_benchmarks(n=5000, capacity=1000, correlation=correlations, count=2)
    generate_benchmarks(n=10000, capacity=1000, correlation=correlations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true",
                        help="Regenerate benchmarks/generated/ before running")
    args = parser.parse_args()

    if args.generate:
        print("Generating benchmark instances...")
        generate_all_instances()

    run_all_benchmarks()
