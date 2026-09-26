"""Hyperparameter sensitivity analysis for the stochastic algorithms.

Not wired into the main pipeline: these two functions expect a
`cv_results` DataFrame from a cross-validation step that was designed
but never actually run in this project (see README, "Known Issues").
Kept here, isolated, because the report references them.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def visualize_hyperparameter_impact(cv_results, param_grid):
    """Visualizes the impact of each hyperparameter on performance.

    Args:
        cv_results: DataFrame with one row per (params, fold), expected to
            have `mean_score`, `std_score` and `ci_95` columns plus one
            column per hyperparameter in `param_grid`.
        param_grid: Dict of parameter name -> list of tested values.
    """
    if cv_results is None or len(cv_results) == 0:
        print("No results to visualize")
        return

    print("\n" + "=" * 80)
    print("HYPERPARAMETERS IMPACT VISUALIZATION")
    print("=" * 80)

    param_names = list(param_grid.keys())
    n_params = len(param_names)

    fig, axes = plt.subplots(1, n_params, figsize=(6 * n_params, 5))
    if n_params == 1:
        axes = [axes]

    for idx, param_name in enumerate(param_names):
        ax = axes[idx]

        grouped = cv_results.groupby(param_name).agg({
            'mean_score': 'mean',
            'std_score': 'mean',
            'ci_95': 'mean',
        }).reset_index().sort_values(param_name)

        x = grouped[param_name]
        y = grouped['mean_score']
        yerr = grouped['ci_95']

        bars = ax.bar(range(len(x)), y, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax.errorbar(range(len(x)), y, yerr=yerr, fmt='none',
                    ecolor='black', capsize=5, capthick=2)

        max_score = y.max()
        colors = []
        for score in y:
            if score >= max_score * 0.98:
                colors.append('darkgreen')
            elif score >= max_score * 0.95:
                colors.append('green')
            elif score >= max_score * 0.90:
                colors.append('orange')
            else:
                colors.append('red')
        for bar, color in zip(bars, colors):
            bar.set_facecolor(color)

        ax.set_xticks(range(len(x)))
        ax.set_xticklabels([f'{val}' for val in x], rotation=45 if len(x) > 5 else 0)
        ax.set_xlabel(param_name.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_ylabel('Score Moyen', fontsize=12, fontweight='bold')
        ax.set_title(f'Impact de {param_name}\n(Barres = IC 95%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        best_idx = y.idxmax()
        best_val = x.iloc[best_idx]
        ax.axvline(best_idx, color='red', linestyle='--', linewidth=2,
                   alpha=0.5, label=f'Meilleur: {best_val}')
        ax.legend()

    plt.suptitle('Hyperparameters Sensitivity Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()

    print("\nRELATIVE IMPACT OF HYPERPARAMETERS:")
    print("-" * 80)
    for param_name in param_names:
        grouped = cv_results.groupby(param_name)['mean_score']
        min_score = grouped.mean().min()
        max_score = grouped.mean().max()
        impact_pct = ((max_score - min_score) / min_score) * 100

        importance = "TRÈS IMPORTANT" if impact_pct > 5 else \
            "IMPORTANT" if impact_pct > 2 else \
            "MODÉRÉ" if impact_pct > 0.5 else \
            "FAIBLE"

        print(f"{param_name:25s}: Impact = {impact_pct:5.2f}% | {importance}")
        print(f"Meilleure valeur: {grouped.mean().idxmax()}")
        print(f"Score range: [{min_score:.1f}, {max_score:.1f}]")
        print()


def compare_default_vs_optimized(algorithm_func, problems, default_params,
                                  optimized_params, n_runs=10, random_state=42):
    """Compares an algorithm's default vs. tuned hyperparameters over
    several problems, using a paired Wilcoxon test for significance.

    Args:
        algorithm_func: Algorithm function, must accept a `seed` kwarg.
        problems: List of Problem instances.
        default_params / optimized_params: Dicts of kwargs to pass through.
        n_runs: Repetitions per configuration (paired by seed).
        random_state: Base seed.

    Returns:
        DataFrame with per-problem comparison stats.
    """
    import time as time_module

    from scipy.stats import wilcoxon

    print("\n" + "=" * 80)
    print("COMPARAISON: PARAMÈTRES FIXES vs OPTIMISÉS")
    print("=" * 80)
    print(f"Algorithme: {algorithm_func.__name__}")
    print(f"Number of problems: {len(problems)}")
    print(f"Répétitions par config: {n_runs}")
    print()

    results = []

    for prob_idx, problem in enumerate(problems):
        print(f"\n[Problème {prob_idx + 1}/{len(problems)}] n={problem.n}, capacity={problem.capacity}")

        default_scores, default_times = [], []
        for run in range(n_runs):
            seed = random_state + run
            try:
                start = time_module.time()
                sol = algorithm_func(problem, **default_params, seed=seed)
                elapsed = time_module.time() - start
                if sol is not None:
                    default_scores.append(sol.total_value)
                    default_times.append(elapsed * 1000)
            except Exception:
                pass

        optimized_scores, optimized_times = [], []
        for run in range(n_runs):
            seed = random_state + run
            try:
                start = time_module.time()
                sol = algorithm_func(problem, **optimized_params, seed=seed)
                elapsed = time_module.time() - start
                if sol is not None:
                    optimized_scores.append(sol.total_value)
                    optimized_times.append(elapsed * 1000)
            except Exception:
                pass

        if len(default_scores) > 0 and len(optimized_scores) > 0:
            default_mean = np.mean(default_scores)
            optimized_mean = np.mean(optimized_scores)
            improvement_pct = ((optimized_mean - default_mean) / default_mean) * 100

            if len(default_scores) == len(optimized_scores) and len(default_scores) >= 5:
                stat, p_value = wilcoxon(default_scores, optimized_scores)
                is_significant = p_value < 0.05
            else:
                p_value = None
                is_significant = None

            print(f"  Default:   {default_mean:.2f} ± {np.std(default_scores):.2f}")
            print(f"  Optimized: {optimized_mean:.2f} ± {np.std(optimized_scores):.2f}")
            print(f"  → Amélioration: {improvement_pct:+.2f}%", end='')
            if is_significant is not None:
                print(f" (p={p_value:.4f}) {'✓ SIGNIFICATIF' if is_significant else '✗ Non significatif'}")
            else:
                print()

            results.append({
                'n': problem.n,
                'capacity': problem.capacity,
                'default_mean': default_mean,
                'default_std': np.std(default_scores),
                'optimized_mean': optimized_mean,
                'optimized_std': np.std(optimized_scores),
                'improvement_pct': improvement_pct,
                'default_time_ms': np.mean(default_times),
                'optimized_time_ms': np.mean(optimized_times),
                'p_value': p_value,
                'is_significant': is_significant,
            })

    results_df = pd.DataFrame(results)

    print("\n" + "=" * 80)
    print("RÉSUMÉ GLOBAL")
    print("=" * 80)
    overall_improvement = results_df['improvement_pct'].mean()
    n_significant = results_df['is_significant'].sum() if 'is_significant' in results_df else 0
    n_total = len(results_df)
    print(f"\nAmélioration moyenne: {overall_improvement:+.2f}%")
    print(f"Améliorations significatives: {n_significant}/{n_total} problèmes")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    x = np.arange(len(results_df))
    width = 0.35
    ax.bar(x - width / 2, results_df['default_mean'], width,
           label='Paramètres par défaut', alpha=0.7, color='orange',
           yerr=results_df['default_std'], capsize=5)
    ax.bar(x + width / 2, results_df['optimized_mean'], width,
           label='Paramètres optimisés', alpha=0.7, color='green',
           yerr=results_df['optimized_std'], capsize=5)
    ax.set_xlabel('Problème', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score Moyen', fontsize=12, fontweight='bold')
    ax.set_title("Comparaison des Scores\n(Barres d'erreur = std)", fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'n={n}' for n in results_df['n']], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    ax = axes[1]
    colors = ['green' if imp > 0 else 'red' for imp in results_df['improvement_pct']]
    ax.barh(range(len(results_df)), results_df['improvement_pct'],
            color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_yticks(range(len(results_df)))
    ax.set_yticklabels([f'n={n}' for n in results_df['n']])
    ax.set_xlabel('Amélioration (%)', fontsize=12, fontweight='bold')
    ax.set_title('Amélioration par Problème\n(Vert=Amélioration, Rouge=Dégradation)', fontsize=13, fontweight='bold')
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.show()

    return results_df
