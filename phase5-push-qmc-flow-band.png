"""Reproducible Phase 2 Push figures with completely hypothetical inputs.

Generate by running `python examples/push_stage_figures.py` after installing
`pip install -e '.[plots]'`. No data files are read.
"""
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow import PushStageSettings, simulate_push_stage

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(exist_ok=True)
BG, INK, GRID = "#f8faf8", "#20343a", "#dbe4e0"
TEAL, BLUE, CLAY = "#24766e", "#467f9b", "#b98666"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "figure.facecolor": BG, "axes.facecolor": "#ffffff",
    "axes.edgecolor": GRID, "axes.labelcolor": "#53666a",
    "xtick.color": "#53666a", "ytick.color": "#53666a",
    "svg.fonttype": "none",
})


def chart(title, ylabel, xlabel="Simulation time (s)"):
    fig, ax = plt.subplots(figsize=(9.6, 4.4), layout="constrained")
    ax.set_title(title, loc="left", fontsize=19, color=INK, pad=15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["right", "top"]].set_visible(False)
    ax.grid(color=GRID, linewidth=.8)
    ax.set_axisbelow(True)
    return fig, ax


def save(fig, name):
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    settings = PushStageSettings()
    expansion = simulate_push_stage(settings)
    constant = simulate_push_stage(replace(settings, pressure_mode="constant"))

    fig, ax = chart("Push | Product discharge", "Discharged product (L/s)")
    ax.plot(expansion.time_s, 1000*expansion.outlet_flow_m3_s, color=TEAL,
            linewidth=2.7, label="Isolated gas expansion")
    ax.plot(constant.time_s, 1000*constant.outlet_flow_m3_s, color=BLUE,
            linewidth=2.7, label="Constant upstream pressure")
    ax.legend(frameon=False)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    save(fig, "push-discharge-comparison")

    fig, ax = chart("Push | Air pressure", "Absolute air pressure (bar)",
                    "Interface advance (m)")
    ax.plot(expansion.interface_position_m, expansion.air_pressure_pa_abs/1e5,
            color=TEAL, lw=2.7, label="Isolated gas expansion")
    ax.plot(constant.interface_position_m, constant.air_pressure_pa_abs/1e5,
            color=BLUE, lw=2.7, label="Constant upstream pressure")
    ax.legend(frameon=False)
    ax.set_ylim(bottom=0)
    save(fig, "push-pressure-sources")

    fig, ax = chart("Push | Product-volume conservation", "Liquid volume (m³)")
    ax.plot(expansion.time_s, expansion.full_column_volume_m3, color=BLUE,
            lw=2.7, label="Full product column")
    ax.plot(expansion.time_s, expansion.discharged_volume_m3, color=TEAL,
            lw=2.7, label="Discharged product")
    ax.plot(expansion.time_s, expansion.holdup_volume_m3, color=CLAY,
            lw=2.7, label="Liquid holdup")
    ax.legend(frameon=False)
    ax.set_ylim(bottom=0)
    save(fig, "push-product-volume")

    fig, ax = chart("Push | Moving interface", "Interface advance (m)")
    ax.plot(expansion.time_s, expansion.interface_position_m, color=TEAL,
            lw=2.7, label="Isolated gas expansion")
    ax.plot(constant.time_s, constant.interface_position_m, color=BLUE,
            lw=2.7, label="Constant upstream pressure")
    ax.legend(frameon=False)
    ax.set_ylim(bottom=0)
    save(fig, "push-interface-position")

    print("Created 4 data-free Push figures (SVG and PNG)")
    for label, result in (("expansion", expansion), ("constant", constant)):
        print(f"{label:>10}: end={result.stop_reason}, time={result.stop_time_s:.3f}s, "
              f"max |volume residual|={result.max_absolute_volume_residual_m3:.3e} m³")


if __name__ == "__main__":
    main()
