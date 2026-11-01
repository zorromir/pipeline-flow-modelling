"""Generate the project's illustrative graphs from hypothetical model inputs.

Outputs are numerical visualizations, not experiments or fitted predictions.
Run from any working directory with `python examples/generate_figures.py`.
"""
from dataclasses import replace
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow import (
    PushParameters, simulate_push, product_volume_balance, polytropic_pressure,
)

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(exist_ok=True)
TEAL, BLUE, CLAY = "#24766e", "#467f9b", "#b98666"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "figure.facecolor": "#f8faf8", "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#dbe4e0", "axes.labelcolor": "#53666a",
    "xtick.color": "#53666a", "ytick.color": "#53666a",
    "svg.fonttype": "none",
})


def setup(title, y_label, x_label="Time (s)"):
    fig, ax = plt.subplots(figsize=(9.5, 4.6), layout="constrained")
    ax.set_title(title, fontsize=18, loc="left", color="#20343a", pad=17)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(color="#dbe4e0", linewidth=.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main():
    p = PushParameters()  # invented example inputs; not industrial specifications
    r = simulate_push(p)

    fig, ax = setup("Liquid-column velocities", "Velocity (m/s)")
    ax.plot(r.time_s, r.interface_velocity_m_s, color=BLUE, lw=2.5, label="Interface")
    ax.plot(r.time_s, r.outlet_velocity_m_s, color=TEAL, lw=2.5, label="Outlet")
    ax.legend(frameon=False)
    save(fig, "industrial-model-velocities")

    fig, ax = setup("Remaining liquid-column length", "Column length (m)")
    ax.plot(r.time_s, r.remaining_column_m, color=TEAL, lw=2.5)
    save(fig, "industrial-model-column")

    fig, ax = setup("Resistance sensitivity", "Outlet flow (L/s)")
    for coefficient, color in zip((2, 4, 8), (BLUE, TEAL, CLAY)):
        row = simulate_push(replace(p, exit_loss_coefficient=coefficient))
        ax.plot(row.time_s, row.discharged_flow_m3_s * 1000, color=color,
                lw=2.5, label=f"Loss coefficient K = {coefficient}")
    ax.legend(frameon=False)
    save(fig, "industrial-model-resistance")

    # This pressure boundary is deliberately a separate idealized scenario.
    swept_fraction = np.linspace(0, .75, 181)
    initial_gas_fraction = .5
    normalized_pressure = polytropic_pressure(
        1.0, initial_gas_fraction, swept_fraction, exponent=1.2,
    )
    fig, ax = setup("Pressure during isolated gas expansion", "Absolute p / initial p",
                    "Swept volume / initial pipe volume")
    ax.plot(swept_fraction, normalized_pressure, color=TEAL, lw=2.5,
            label="Polytropic expansion")
    ax.plot(swept_fraction, np.ones_like(swept_fraction), color=BLUE, lw=2.5,
            label="Constant-pressure boundary")
    ax.set_ylim(0, 1.2)
    ax.legend(frameon=False)
    save(fig, "industrial-pressure-expansion")

    swept = np.linspace(0, .9, 181)
    rows = [product_volume_balance(1.0, s, .2) for s in swept]
    fig, ax = setup("Where the displaced product goes", "Fraction of initial product",
                    "Swept volume / initial pipe volume")
    ax.plot(swept, [v.full_column_m3 for v in rows], color=BLUE, lw=2.5,
            label="Full column")
    ax.plot(swept, [v.discharged_m3 for v in rows], color=TEAL, lw=2.5,
            label="Discharged")
    ax.plot(swept, [v.holdup_m3 for v in rows], color=CLAY, lw=2.5,
            label="Holdup")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False)
    save(fig, "industrial-product-volume-balance")

    print(f"Generated 5 synthetic figures (SVG and PNG) in {OUT}")


if __name__ == "__main__":
    main()
