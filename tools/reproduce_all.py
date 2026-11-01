"""Regenerate all synthetic figures from the public Python examples.

Run from the repository root: python tools/reproduce_all.py
Extra diagnostic plots are not all committed to Git.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "generate_figures.py",
    "push_stage_figures.py",
    "phase3_pipe_figures.py",
    "blow_phase4_figures.py",
    "phase5_uncertainty_figures.py",
    "phase6_rinse_dry_figures.py",
)


def main():
    for script in SCRIPTS:
        print(f"Generating with {script}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "examples" / script)], check=True, cwd=ROOT)
    gallery = (
        "push-discharge-comparison",
        "phase3-segmented-vs-equivalent",
        "phase4-blow-transition-volumes",
        "phase5-push-qmc-flow-band",
        "phase6-rinse-dry-water-inventory",
    )
    missing = [f"{name}.{ext}" for name in gallery for ext in ("png", "svg")
               if not (ROOT / "figures" / f"{name}.{ext}").is_file()]
    if missing:
        raise RuntimeError(f"Missing selected figures: {missing}")
    print("All six generators completed, five selected figures verified.")


if __name__ == "__main__":
    main()
