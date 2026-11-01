# Pipeline flow modelling

This repository shows some of the mathematical models and numerical methods I worked with during a six-month industrial research project on removing liquid from pipelines.

I studied published models, adapted them to an industrial problem, wrote simulations, compared calculated quantities with available measurements and investigated the effect of uncertain inputs. A key challenge was that the flow changes during the process: moving a full liquid column is different from removing residual liquid, rinsing or drying.

![Push uncertainty study](figures/phase5-push-qmc-flow-band.png)

*Example: simulated outlet flow from 256 hypothetical input combinations. The line is the sample median and the shaded region shows the 10th–90th sample percentiles at the same progress towards a discharge target. These are not experimentally validated prediction intervals.*

## About this public reconstruction

**The code in this repository is an AI-assisted reconstruction of selected parts of my original project.** I used AI to help recreate, organise and document simplified Python examples of the mathematical models and numerical methods I worked with.

The original industrial research was my work, but **the original company code, experimental data, equipment details and calibrated results are confidential** and are not published here. The public examples use published equations and invented parameters. They are not exact copies of my original implementation or a complete model of the industrial system.

My aim is to show how I approached the mathematics and numerical modelling while making examples that other people can run without access to the company's data.

## What I modelled

| Part | What the public example does |
| --- | --- |
| **Push** | Simulates a moving liquid column driven by fixed pressure or expanding compressed air. |
| **Pipe geometry** | Calculates volume, friction, elevation and local pressure losses for connected pipe sections. |
| **Blow** | Tracks the remaining liquid column, discharged liquid and liquid left behind. A separate example explores an assumed film-removal rate. |
| **Uncertainty** | Runs 256 scrambled Sobol input scenarios to see how uncertain pressure, friction and other parameters affect Push results. |
| **Rinse and Dry** | Tracks water and product inventories during a simplified rinse, then transfers the remaining water to a separate drying example. |

The examples are **not connected into one complete Push–Blow–Rinse–Dry solver**. In particular, the Blow film calculation and Rinse/Dry models use simplified assumptions that have not been validated for an industrial installation.

For equations, assumptions and tests, see the [model scope](docs/MODEL_SCOPE.md) and the notes on [Push](docs/PHASE_2_PUSH.md), [pipe resistance](docs/PHASE_3_GEOMETRY.md), [Blow](docs/PHASE_4_BLOW.md), [uncertainty](docs/PHASE_5_UNCERTAINTY.md) and [Rinse/Dry](docs/PHASE_6_RINSE_DRY.md).

## Selected figures

These five plots are produced by Python scripts, not by image generation. All the inputs are hypothetical.

| Plot | What I wanted to investigate |
| --- | --- |
| [Push discharge](figures/push-discharge-comparison.png) | How does air expansion change the calculated liquid outflow? |
| [Pipe resistance](figures/phase3-segmented-vs-equivalent.png) | Why can pipes with equal volume have different pressure losses? |
| [Blow volume balance](figures/phase4-blow-transition-volumes.png) | How much liquid has left the pipe and how much is still inside? |
| [Push uncertainty](figures/phase5-push-qmc-flow-band.png) | How do different assumed input values change the simulated outflow? |
| [Rinse to Dry](figures/phase6-rinse-dry-water-inventory.png) | How can the remaining water be passed consistently into the next stage? |

See the [figure guide](docs/FIGURES.md) for more detail. The scripts can also produce additional diagnostic figures.

## Running the examples

Use Python 3.10 or newer. From the repository root:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python examples/push_stage_figures.py
python examples/phase5_uncertainty_figures.py
```

To regenerate all figures:

```bash
python tools/reproduce_all.py
```

The code is organised into:

```text
src/pipeline_flow/    Mathematical models and calculations
examples/             Scripts for hypothetical scenarios and figures
tests/                Numerical and conservation checks
figures/              Five selected plots in PNG and SVG
docs/                 Mathematical explanations and limitations
references/           Published sources
tools/                Figure reproduction and release checks
.github/workflows/    Automated checks
```

I also included a basic file-disclosure check:

```bash
python tools/audit_release.py
```

This is only an automated check. It cannot establish whether publication is legally permitted or detect every possible confidential detail.

## References

The main starting point for the moving-column equations is Tijsseling, Hou, Bozkuş and Laanearu (2016), [*Improved One-Dimensional Models for Rapid Emptying and Filling of Pipelines*](https://doi.org/10.1115/1.4031508). Chen et al. (2024), [*Experimental data on filling and emptying of a large-scale pipeline*](https://doi.org/10.1038/s41597-024-03441-7), provide useful public experimental context; their data are not included in these examples.

Three additional papers I used for the literature review were [Hart et al. (1989)](https://doi.org/10.1016/0301-9322(89)90023-2) on low liquid holdup and pressure losses, [Cioncolini and Thome (2012)](https://doi.org/10.1016/j.ijmultiphaseflow.2012.03.003) on annular void fraction, and [Cioncolini and Thome (2013)](https://doi.org/10.1016/j.ijmultiphaseflow.2012.12.003) on uneven liquid films in horizontal pipes. Their correlations are **not implemented** in the public code.

See [references/sources.md](references/sources.md) for bibliographic details, project relevance and limits.

## What the results do and do not show

The tests check whether the code follows the stated equations, respects stopping conditions and conserves the quantities it should. Passing them does not show that the models predict industrial measurements accurately. None of the public parameters is an estimate of the company's real operating conditions.

The original code and data remain confidential. Please do not assume the public examples can be used to operate or design an industrial system.

**Code reuse:** No software licence has been added, so reuse rights should not be assumed. See the [publication checklist](docs/PUBLICATION_CHECKLIST.md).
