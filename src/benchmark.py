"""Running every enabled algorithm against every discovered benchmark instance."""
import time

import pandas as pd

from .algorithms import ALL_ALGORITHMS
from .parser import discover_benchmarks, parse_benchmark_file


def should_run_algorithm(algo_name, n, max_n, correlation=None):
    """Determines if an algorithm should be executed based on size and correlation."""
    if algo_name == 'Brute Force' and correlation != 'low_dimension':
        return False
    return n <= max_n


def run_benchmark(benchmark_info, algorithms=None, timeout=300):
    """Runs every algorithm on a single benchmark file.

    Returns:
        dict: per-algorithm results (value, weight, time, usage, ...) or
        a skip reason (too large, timeout, memory error, exception).
    """
    if algorithms is None:
        algorithms = ALL_ALGORITHMS

    problem = parse_benchmark_file(benchmark_info['path'])
    if problem is None:
        return None

    results = {
        'info': benchmark_info,
        'n': problem.n,
        'capacity': problem.capacity,
        'algorithms': {},
    }

    for algo_name, algo_func, max_n in algorithms:
        if not should_run_algorithm(algo_name, problem.n, max_n):
            results['algorithms'][algo_name] = {'skipped': True, 'reason': f'n={problem.n} > max_n={max_n}'}
            continue

        try:
            start = time.time()
            sol = algo_func(problem)
            elapsed = time.time() - start

            if elapsed > timeout:
                results['algorithms'][algo_name] = {'skipped': True, 'reason': f'timeout (>{timeout}s)'}
                print(f"{algo_name}: timeout ({elapsed:.1f}s)")
                continue

            if sol is None:
                results['algorithms'][algo_name] = {'skipped': True, 'reason': 'protection_triggered'}
                continue

            results['algorithms'][algo_name] = {
                'value': sol.total_value,
                'weight': sol.total_weight,
                'time': sol.time,
                'usage': sol.usage_percent,
                'items_count': len(sol.selected_items),
                'skipped': False,
            }

        except KeyboardInterrupt:
            print(f"\nManual interruption on {algo_name}")
            results['algorithms'][algo_name] = {'skipped': True, 'reason': 'interrupted'}
            continue

        except MemoryError:
            results['algorithms'][algo_name] = {'skipped': True, 'reason': 'memory_error'}
            print(f"{algo_name}: Insufficient memory")

        except Exception as e:
            results['algorithms'][algo_name] = {'skipped': True, 'reason': str(e)}
            print(f"{algo_name}: {str(e)}")

    return results


def run_all_benchmarks(base_path='benchmarks', output_csv='benchmark_results.csv'):
    """Runs all discovered benchmarks against all enabled algorithms.

    Saves ONLY at the end (no partial saves), and keeps going even if a
    single algorithm or benchmark fails.

    Returns:
        DataFrame with all results.
    """
    structure = discover_benchmarks(base_path)
    if structure is None:
        print("No benchmarks available")
        return None

    all_results = []
    total = len(structure['benchmarks'])

    print(f"Running {total} benchmarks...")
    for i, (key, bench_info) in enumerate(structure['benchmarks'].items(), 1):
        print(f"\n[{i}/{total}] {bench_info['correlation']} | {bench_info['size']} | {bench_info['capacity']}")

        try:
            problem = parse_benchmark_file(bench_info['path'])
            if problem is None:
                print("  ERROR: Cannot parse this benchmark, skipping")
                continue

            print(f"  n={problem.n}, capacity={problem.capacity}")

            for algo_name, algo_func, max_n in ALL_ALGORITHMS:
                if not should_run_algorithm(algo_name, problem.n, max_n, bench_info['correlation']):
                    if algo_name == 'Brute Force' and bench_info['correlation'] != 'low_dimension':
                        print(f"  SKIP {algo_name}: only on low_dimension")
                    else:
                        print(f"  SKIP {algo_name}: n={problem.n} > max_n={max_n}")
                    continue

                try:
                    start_algo = time.time()
                    sol = algo_func(problem)
                    elapsed = time.time() - start_algo

                    if elapsed > 300:
                        print(f"  WARNING {algo_name}: very long time ({elapsed:.1f}s)")

                    if sol is None:
                        print(f"  SKIP {algo_name}: protection triggered")
                        continue

                    all_results.append({
                        'correlation': bench_info['correlation'],
                        'n': problem.n,
                        'capacity_type': bench_info['capacity'],
                        'capacity_value': problem.capacity,
                        'algorithm': algo_name,
                        'value': sol.total_value,
                        'time_ms': sol.time * 1000,
                        'usage_percent': sol.usage_percent,
                        'items_selected': len(sol.selected_items),
                    })

                except MemoryError:
                    print(f"  ERROR {algo_name}: Memory error")
                    continue

                except KeyboardInterrupt:
                    if len(all_results) > 0:
                        df = pd.DataFrame(all_results)
                        df.to_csv('benchmark_results_interrupted.csv', index=False)
                        print("Emergency save: 'benchmark_results_interrupted.csv'")
                        return df
                    print("No results to save")
                    return None

                except Exception as e:
                    print(f"  ERROR {algo_name}: {str(e)}")
                    continue

        except Exception as e:
            print(f"  ERROR on this benchmark: {str(e)}")
            continue

    if len(all_results) == 0:
        print("WARNING: No results collected")
        return None

    df = pd.DataFrame(all_results)

    try:
        df.to_csv(output_csv, index=False)
        print(f"Results saved: '{output_csv}'")
    except Exception as e:
        print(f"ERROR during save: {e}")
        print("DataFrame is returned anyway")

    return df
