"""Generate the Push uncertainty plots from hypothetical input ranges.

Run after installing the development dependencies:
    python examples/phase5_uncertainty_figures.py

The plots show numerical sample summaries, not measured predictions.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow.uncertainty import QMCSettings, LABELS, run_qmc

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(exist_ok=True)
TEAL, BLUE, WARM = "#24766e", "#467f9b", "#b98666"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.labelcolor": "#53666a", "axes.edgecolor": "#dbe4e0",
    "xtick.color": "#53666a", "ytick.color": "#53666a",
    "svg.fonttype": "none", "savefig.facecolor": "#f8faf8",
})


def basic(title: str, x: str, y: str):
    fig, ax = plt.subplots(figsize=(9.7, 4.7), layout="constrained")
    ax.set_title(title, fontsize=19, color="#20343a", loc="left", pad=18)
    ax.set(xlabel=x, ylabel=y)
    ax.grid(color="#dbe4e0", alpha=.85)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def save(fig, name: str):
    fig.savefig(OUT / (name + ".png"), dpi=200, bbox_inches="tight")
    fig.savefig(OUT / (name + ".svg"), bbox_inches="tight")
    plt.close(fig)


def main():
    cfg = QMCSettings(power=8, seed=20261101)
    result = run_qmc(cfg)
    n = len(result.completion_times_s)
    low, med, high = result.quantiles(result.aligned_flows_lps)
    progress = 100 * result.progress_fraction

    # All curves compared at the same fraction of the 50% discharge target,
    # not at the same time, because the simulated end times differ.
    fig, ax = basic("Modelled discharge under uncertain inputs",
                    "Progress towards the discharge target (%)", "Outlet product flow (L/s)")
    ax.fill_between(progress, low, high, color=TEAL, alpha=.18,
                    label="10th–90th sample percentiles")
    ax.plot(progress, med, color=TEAL, linewidth=2.7, label="Sample median")
    ax.set(xlim=(0, 100), ylim=(0, max(high) * 1.1))
    ax.legend(frameon=False, loc="upper left")
    save(fig, "phase5-push-qmc-flow-band")

    times = np.sort(result.completion_times_s)
    ecdf = np.arange(1, n + 1) / n
    p10, p50, p90 = result.quantiles(result.completion_times_s)
    fig, ax = basic("Distribution of simulated completion times",
                    "Time to 50% discharged product (s)", "Fraction of sampled runs completed")
    ax.step(times, ecdf, color=BLUE, lw=2.5, where="post", label="Empirical sample CDF")
    ax.axvspan(p10, p90, alpha=.1, color=TEAL, label="Central 80% of sample")
    ax.axvline(p50, color=TEAL, lw=2, linestyle="--", label=f"Median {p50:.2f} s")
    ax.set(ylim=(0, 1.02))
    ax.legend(frameon=False, loc="lower right")
    save(fig, "phase5-push-qmc-completion-times")

    correlations = result.rank_correlations
    labels = [LABELS[name] for name in result.names]
    fig, ax = plt.subplots(figsize=(9.7, 4.7), layout="constrained")
    ax.barh(labels[::-1], correlations[::-1], color=[BLUE if x < 0 else TEAL for x in correlations[::-1]])
    ax.set(xlim=(-1, 1), xlabel="Spearman correlation with completion time")
    ax.axvline(0, color="#20343a", lw=.8)
    ax.grid(axis="x", color="#dbe4e0")
    ax.set_axisbelow(True)
    ax.set_title("Exploratory parameter associations", fontsize=19,
                 loc="left", color="#20343a", pad=18)
    save(fig, "phase5-push-qmc-rank-associations")

    sizes = [16, 32, 64, 128, 256]
    estimates = [np.median(result.completion_times_s[:size]) for size in sizes]
    fig, ax = basic("Sample-design stability check", "Scrambled Sobol samples",
                    "Median simulated completion time (s)")
    ax.plot(sizes, estimates, color=WARM, lw=2.4, marker="o")
    ax.set_xscale("log", base=2)
    ax.set_xticks(sizes, [str(x) for x in sizes])
    save(fig, "phase5-push-qmc-sample-stability")

    print(f"N={n}, seed={cfg.seed}, all targets reached={result.success_fraction == 1.0}")
    print(f"Completion time p10/median/p90: {p10:.3f}, {p50:.3f}, {p90:.3f} s")
    print(f"Outlet-flow at 50% of target p10/median/p90: "
          f"{low[len(low)//2]:.2f}, {med[len(med)//2]:.2f}, {high[len(high)//2]:.2f} L/s")
    print("Spearman rho with completion time:", dict(zip(labels, map(float, correlations))))


if __name__ == "__main__":
    main()
