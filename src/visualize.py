"""All plotting functions used in the analysis notebook, extracted so the
notebook itself only has to call them on a loaded `results_df`."""
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

ALGO_COLORS = {
    'Brute Force': '#e41a1c',
    'Dynamic Programming': '#377eb8',
    'DP Top-Down': '#4daf4a',
    'Branch and Bound': '#984ea3',
    'Greedy Ratio': '#ff7f00',
    'Greedy Value': '#ffff33',
    'Greedy Weight': '#a65628',
    'Fractional Knapsack': '#f781bf',
    'Randomized': '#999999',
    'Genetic Algorithm': '#17becf',
    'Genetic Adaptive': '#1f77b4',
    'Simulated Annealing': '#d62728',
    'SA Adaptive': '#ff9896',
    'FTPAS (ε=0.1)': '#9467bd',
    'FTPAS (ε=0.05)': '#8c564b',
    'FTPAS Adaptive': '#e377c2',
}


def plot_time_by_size(results_df):
    """Average execution time by problem size, one line per algorithm (log scale)."""
    df = results_df.copy()
    agg_time = df.groupby(['algorithm', 'n'])['time_ms'].mean().reset_index().sort_values('n')

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=agg_time, x='n', y='time_ms', hue='algorithm', marker='o',
                 palette='husl', linewidth=2, markersize=8)

    plt.xlabel('Problem size (n)')
    plt.ylabel('Average time (ms)')
    plt.title('Execution time by problem size')
    plt.yscale('log')

    max_n = int(agg_time['n'].max())
    plt.xticks(range(0, max_n + 1000, 1000))
    plt.xlim(0, max_n + 500)

    plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def plot_coverage_heatmap(results_df):
    """Heatmap of how many benchmark files were actually tested per
    algorithm x size (useful to spot algorithms silently skipped)."""
    df = results_df.copy()
    file_counts = df.groupby(['algorithm', 'n']).size().reset_index(name='nb_files')
    pivot_counts = file_counts.pivot(index='algorithm', columns='n', values='nb_files').fillna(0).astype(int)
    pivot_counts = pivot_counts[sorted(pivot_counts.columns)]

    total_files_per_n = pivot_counts.max(axis=0)

    status_matrix = np.zeros_like(pivot_counts.values, dtype=float)
    for i in range(len(pivot_counts.index)):
        for j in range(len(pivot_counts.columns)):
            n_col = pivot_counts.columns[j]
            val = pivot_counts.values[i, j]
            total = total_files_per_n[n_col]
            if val >= total and total > 0:
                status_matrix[i, j] = 2  # all files
            elif val > 0:
                status_matrix[i, j] = 1  # partial
            else:
                status_matrix[i, j] = 0  # none

    fig, ax = plt.subplots(figsize=(14, 8))
    cmap_3colors = ListedColormap(['#e74c3c', '#f39c12', '#2ecc71'])
    ax.pcolormesh(status_matrix, cmap=cmap_3colors, edgecolors='white', linewidth=2, vmin=0, vmax=2)

    ax.set_xticks(np.arange(len(pivot_counts.columns)) + 0.5)
    ax.set_yticks(np.arange(len(pivot_counts.index)) + 0.5)
    ax.set_xticklabels([f'n={n}' for n in pivot_counts.columns], fontsize=10)
    ax.set_yticklabels(pivot_counts.index, fontsize=10)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    for i in range(len(pivot_counts.index)):
        for j in range(len(pivot_counts.columns)):
            val = int(pivot_counts.values[i, j])
            n_col = pivot_counts.columns[j]
            total = int(total_files_per_n[n_col])
            ax.text(j + 0.5, i + 0.5, f'{val}/{total}', ha='center', va='center',
                    color='white', fontsize=10, fontweight='bold')

    ax.set_xlabel('Size n', fontsize=12)
    ax.set_ylabel('Algorithm', fontsize=12)
    ax.set_title('Heatmap: Number of files tested by algorithm and size n', fontsize=13, fontweight='bold')

    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', label='All files tested'),
        Patch(facecolor='#f39c12', edgecolor='white', label='Partially tested'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='No files tested'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=10)

    plt.tight_layout()
    plt.show()


def plot_time_vs_quality(results_df):
    """Scatter of average time vs. average value, one point per algorithm."""
    df = results_df.copy()
    summary = df.groupby('algorithm').agg({'time_ms': 'mean', 'value': 'mean'}).reset_index()

    plt.figure(figsize=(10, 6))
    plt.scatter(summary['time_ms'], summary['value'], s=120, alpha=0.8)
    for _, row in summary.iterrows():
        plt.text(row['time_ms'], row['value'], row['algorithm'], fontsize=9,
                  verticalalignment='bottom', horizontalalignment='right')
    plt.xscale('log')
    plt.xlabel('Average time (ms)')
    plt.ylabel('Average value')
    plt.title('Time vs Quality tradeoff (one point = one algorithm)')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_performance_per_algorithm(results_df):
    """For each algorithm: value and time by size, split by category/correlation."""
    df = results_df.copy()
    colors_cat = {'large_scale': '#1f77b4', 'low_dimension': '#ff7f0e'}

    for algo in df['algorithm'].unique():
        algo_data = df[df['algorithm'] == algo].copy()

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f'Performance: {algo}', fontsize=14, fontweight='bold')

        group_col = 'category' if 'category' in algo_data.columns else 'correlation'
        agg_value = algo_data.groupby([group_col, 'n'])['value'].mean().reset_index()
        agg_value = agg_value.rename(columns={group_col: 'category'})

        for cat in agg_value['category'].unique():
            cat_data = agg_value[agg_value['category'] == cat]
            axes[0].plot(cat_data['n'], cat_data['value'], marker='o', label=cat, linewidth=2,
                         color=colors_cat.get(cat, None))

        axes[0].set_xlabel('Size n', fontsize=11)
        axes[0].set_ylabel('Average value', fontsize=11)
        axes[0].set_title('Value by size and category')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        axes[0].set_xscale('log')

        agg_time = algo_data.groupby([group_col, 'n'])['time_ms'].mean().reset_index()
        agg_time = agg_time.rename(columns={group_col: 'category'})

        for cat in agg_time['category'].unique():
            cat_data = agg_time[agg_time['category'] == cat]
            axes[1].plot(cat_data['n'], cat_data['time_ms'], marker='s', label=cat, linewidth=2,
                         color=colors_cat.get(cat, None))

        axes[1].set_xlabel('Size n', fontsize=11)
        axes[1].set_ylabel('Average time (ms)', fontsize=11)
        axes[1].set_title('Execution time by size')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        axes[1].set_xscale('log')
        axes[1].set_yscale('log')

        plt.tight_layout()
        plt.show()
        print(f"\n{'=' * 60}\n")


def plot_performance_by_correlation(results_df):
    """Value obtained by size, one small multiple per algorithm, colored by correlation type."""
    df = results_df.copy()

    corr_colors = {
        'uncorrelated': '#2ecc71',
        'weakly_correlated': '#f39c12',
        'strongly_correlated': '#e74c3c',
        'low_dimension': '#3498db',
        'large_scale': '#9b59b6',
    }

    algos_to_show = ['Dynamic Programming', 'Greedy Ratio', 'Genetic Algorithm', 'Simulated Annealing']
    algos_present = [a for a in algos_to_show if a in df['algorithm'].unique()]

    if not algos_present:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, algo in enumerate(algos_present[:4]):
        ax = axes[idx]
        algo_data = df[df['algorithm'] == algo]

        for corr in algo_data['correlation'].unique():
            corr_data = algo_data[algo_data['correlation'] == corr]
            agg = corr_data.groupby('n').agg({'value': 'mean', 'time_ms': 'mean'}).reset_index().sort_values('n')
            color = corr_colors.get(corr, '#333')
            ax.plot(agg['n'], agg['value'], 'o-', label=corr, color=color, linewidth=2, markersize=6)

        ax.set_xlabel('Size n', fontsize=10)
        ax.set_ylabel('Average value', fontsize=10)
        ax.set_title(f'{algo}', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        ax.set_xscale('log')

    plt.suptitle('Value obtained by size and correlation type', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_regression_modeling(results_df):
    """Fits a degree-2 polynomial to relative quality and a log-log line to
    time, per algorithm, to estimate its empirical time complexity.

    Returns:
        DataFrame summarizing R² and estimated complexity per algorithm.
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    from sklearn.preprocessing import PolynomialFeatures

    warnings.filterwarnings('ignore')

    df = results_df.copy()
    df['max_value_per_instance'] = df.groupby(['n', 'correlation'])['value'].transform('max')
    df['relative_quality'] = (df['value'] / df['max_value_per_instance']) * 100

    regression_results = []

    for algo in df['algorithm'].unique():
        algo_data = df[df['algorithm'] == algo].copy()
        if len(algo_data) == 0:
            continue

        grouped = algo_data.groupby('n').agg({
            'relative_quality': 'mean',
            'time_ms': 'mean',
        }).reset_index().sort_values('n')

        if len(grouped) < 2:
            continue

        X = grouped['n'].values.reshape(-1, 1)
        y_quality = grouped['relative_quality'].values
        y_time = grouped['time_ms'].values

        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)

        reg_quality = LinearRegression()
        reg_quality.fit(X_poly, y_quality)
        y_pred_quality = reg_quality.predict(X_poly)
        r2_quality = r2_score(y_quality, y_pred_quality)

        X_log = np.log1p(X)
        y_log = np.log1p(y_time)
        reg_time = LinearRegression()
        reg_time.fit(X_log, y_log)
        y_pred_time = np.expm1(reg_time.predict(X_log))
        r2_time = r2_score(y_time, y_pred_time)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax2 = ax.twinx()

        ax.scatter(grouped['n'], grouped['relative_quality'], color='blue',
                   alpha=0.6, s=60, label='Observed quality', zorder=3)
        ax.plot(grouped['n'], y_pred_quality, 'b--', linewidth=2,
                label=f'Quality Regression (R²={r2_quality:.3f})', zorder=2)
        ax.set_xlabel('Problem size (n)', fontsize=11)
        ax.set_ylabel('Relative Quality (%)', fontsize=11, color='blue')
        ax.tick_params(axis='y', labelcolor='blue')
        ax.set_xscale('log')

        ax2.scatter(grouped['n'], grouped['time_ms'], color='red',
                    alpha=0.6, s=60, marker='s', label='Observed time', zorder=3)
        ax2.plot(grouped['n'], y_pred_time, 'r--', linewidth=2,
                 label=f'Time Regression (R²={r2_time:.3f})', zorder=2)
        ax2.set_ylabel('Time (ms)', fontsize=11, color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_yscale('log')

        ax.set_title(f'{algo} - Performance Modeling', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9)

        plt.tight_layout()
        plt.show()

        quality_trend_coef = reg_quality.coef_[1] if len(reg_quality.coef_) > 1 else reg_quality.coef_[0]
        time_coef = float(reg_time.coef_[0])

        regression_results.append({
            'algorithm': algo,
            'quality_r2': r2_quality,
            'time_r2': r2_time,
            'quality_trend': 'decreasing' if quality_trend_coef < 0 else 'increasing',
            'time_complexity': f"O(n^{time_coef:.2f})" if time_coef > 0 else 'O(1)',
        })

    reg_df = pd.DataFrame(regression_results)

    print("\n" + "=" * 80)
    print("REGRESSION ANALYSIS - PERFORMANCE MODELING")
    print("=" * 80)
    for _, row in reg_df.iterrows():
        print(f"\n{row['algorithm']}:")
        print(f"  Quality: R² = {row['quality_r2']:.3f} (trend: {row['quality_trend']})")
        print(f"  Time: R² = {row['time_r2']:.3f} (estimated complexity: {row['time_complexity']})")

    return reg_df
