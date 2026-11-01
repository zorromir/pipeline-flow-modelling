"""Generate original, hypothetical Blow transition and film-surrogate plots."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pipeline_flow.blow_transition import BlowTransitionSettings, simulate_blow_transition
from pipeline_flow.film_demo import FilmScenario, simulate_film_demo

OUTPUT = Path(__file__).resolve().parents[1] / "figures"
OUTPUT.mkdir(exist_ok=True)
INK = "#20343a"
DIM = "#53666a"
TEAL = "#24766e"
BLUE = "#467f9b"
WARM = "#b98666"


def axes(title: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(10.8, 4.9), layout="constrained")
    ax.set_title(title, loc="left", color=INK, fontsize=19, pad=20)
    ax.set_xlabel("Simulation time (s)", color=DIM)
    ax.set_ylabel(ylabel, color=DIM)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#dbe4e0", linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def save(fig, filename: str):
    for fmt in ("png", "svg"):
        fig.savefig(OUTPUT / f"{filename}.{fmt}", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    cfg = BlowTransitionSettings()
    r = simulate_blow_transition(cfg)
    initial = cfg.length_m * cfg.area_m2

    fig, ax = axes("Blow transition: where the liquid goes", "Volume / initial liquid volume")
    ax.plot(r.time_s, r.liquid_column_length_m*cfg.area_m2 / initial, color=BLUE, lw=2.7, label="Remaining full column")
    ax.plot(r.time_s, r.discharged_volume_m3 / initial, color=TEAL, lw=2.7, label="Discharged liquid")
    ax.plot(r.time_s, r.tail_holdup_volume_m3 / initial, color=WARM, lw=2.7, label="Liquid left behind")
    ax.set_ylim(0, 1.03)
    ax.legend(frameon=False, ncol=2, fontsize=10)
    save(fig, "phase4-blow-transition-volumes")

    fig, ax = axes("Blow transition: predicted outlet speed", "Speed (m/s)")
    ax.plot(r.time_s, r.outlet_velocity_m_s, color=TEAL, lw=2.7, label="Outlet speed")
    ax.legend(frameon=False)
    save(fig, "phase4-blow-transition-dynamics")

    fig, ax = axes("Illustrative film inventory: assumed removal rates", "Remaining film (L)")
    for rate, color in ((.006, BLUE), (.015, TEAL), (.030, WARM)):
        film = simulate_film_demo(FilmScenario(removal_rate_per_s=rate))
        ax.plot(film.time_s, film.remaining_volume_l, lw=2.7, color=color,
                label=f"Assumed rate {rate:g} s⁻¹")
    ax.legend(frameon=False)
    save(fig, "phase4-illustrative-film-inventory")

    print("Transition event:", r.stop_reason)
    print("Elapsed seconds:", round(r.final_time_s, 4))
    print("Volume conservation max residual [m3]:", np.max(np.abs(r.volume_residual_m3)))
    print("3 plots each in SVG and PNG:", OUTPUT)


if __name__ == "__main__":
    main()
