"""Two original, data-free plots illustrating geometry and Darcy pressure losses.

Run: python examples/phase3_pipe_figures.py
All inputs are hypothetical and intentionally unrelated to test equipment.
"""
from pathlib import Path
import sys

# Run without editable installation as well as after `pip install -e .`.
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow.geometry import PipeNetwork, PipeSegment
from pipeline_flow.resistance import pressure_losses

OUT = BASE / "figures"
OUT.mkdir(parents=True, exist_ok=True)

TEAL, BLUE, SAND = "#24766e", "#467f9b", "#b98666"
INK, SUBTLE = "#20343a", "#53666a"

# Hypothetical geometry. The route stays continuous at each segment boundary.
ROUTE = PipeNetwork((
    PipeSegment(20., .16, 0., 3., local_loss_k=1.2),
    PipeSegment(35., .11, 3., 5., local_loss_k=2.0),
    PipeSegment(25., .14, 5., 1., local_loss_k=.8),
))
RHO = 998.0
DARCY = 0.024
OUTLET_ABS = 101325.0


def plot_style(ax, title, y_label):
    ax.set_title(title, loc="left", pad=18, fontsize=16, color=INK)
    ax.set_ylabel(y_label, color=SUBTLE)
    ax.set_facecolor("#ffffff")
    ax.grid(axis="y", color="#dbe4e0", linewidth=.9)
    ax.set_axisbelow(True)
    ax.spines[["right", "top"]].set_visible(False)
    ax.tick_params(colors=SUBTLE)


def save(fig, stem):
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def pressure_breakdown():
    q = .007
    result = pressure_losses(ROUTE, q, RHO, DARCY)
    fig, ax = plt.subplots(figsize=(9.6, 4.5), layout="constrained")
    plot_style(ax, "Pressure contributions by pipe segment", "Pressure contribution (kPa)")
    xs = np.arange(len(ROUTE.segments))
    width=.23
    ax.bar(xs-width, [s.friction_pa/1000 for s in result.sections], width,
           label="Wall friction", color=TEAL)
    ax.bar(xs, [s.elevation_pa/1000 for s in result.sections], width,
           label="Elevation (+ up / − down)", color=BLUE)
    ax.bar(xs+width, [s.local_pa/1000 for s in result.sections], width,
           label="Local K losses", color=SAND)
    ax.axhline(0, lw=1, color=INK)
    ax.set_xticks(xs, [f"Section {i+1}" for i in xs])
    ax.legend(frameon=False, ncol=3, fontsize=9, loc="upper right")
    save(fig,"phase3-pressure-breakdown")


def equivalent_comparison():
    """Same total volume and height change; not the same hydraulic losses."""
    s=ROUTE.segments
    eq=PipeNetwork((PipeSegment(ROUTE.length_m, ROUTE.equivalent_diameter_m,
                                s[0].start_height_m,s[-1].end_height_m,
                                local_loss_k=sum(x.local_loss_k for x in s)),))
    flows=np.linspace(0,.011,120)
    detailed=np.array([(r.friction_pa + r.local_pa) for r in (pressure_losses(ROUTE,float(q),RHO,DARCY) for q in flows)])/1000
    equivalent=np.array([(r.friction_pa + r.local_pa) for r in (pressure_losses(eq,float(q),RHO,DARCY) for q in flows)])/1000
    fig,ax=plt.subplots(figsize=(10,4.5),layout="constrained")
    plot_style(ax,"Equal pipe volume does not imply equal resistance","Friction + local losses (kPa)")
    ax.plot(1000*flows,detailed,lw=2.7,label="Three physical segments",color=TEAL)
    ax.plot(1000*flows,equivalent,lw=2.7,label="Volume-equivalent single pipe",color=BLUE,linestyle="--")
    ax.set_xlabel("Forward liquid flow (L/s)",color=SUBTLE)
    ax.legend(frameon=False,loc="upper left")
    save(fig,"phase3-segmented-vs-equivalent")
    r1=pressure_losses(ROUTE,.007,RHO,DARCY)
    r2=pressure_losses(eq,.007,RHO,DARCY)
    print("Hypothetical network:",f"L={ROUTE.length_m:.0f} m, V={ROUTE.volume_m3:.3f} m3, D_eq={ROUTE.equivalent_diameter_m:.4f} m")
    print("At Q=7 L/s:",f"segments {r1.total_pa/1000:.2f} kPa; equivalent {r2.total_pa/1000:.2f} kPa")


if __name__=="__main__":
    pressure_breakdown()
    equivalent_comparison()
