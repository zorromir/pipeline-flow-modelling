# Phase 5 — Input uncertainty with scrambled Sobol sampling

**Status:** Public numerical demonstration and implementation verification; **not experimental validation**, calibration, or a statement of accuracy for the industrial process.

## Research basis

The project report distinguishes sensitivity and uncertainty propagation from parameter fitting. Its Push section identifies the Darcy friction factor, holdup fraction and outlet-loss coefficient as uncertain modelling inputs; the wider research method uses quasi-Monte Carlo (QMC) methods. This open implementation uses an independently written, simplified moving-column model previously introduced in Phase 2. It does not reproduce a confidential uncertainty study or its input distributions.

## Question

How sensitive are simulated product discharge and the time to a target removal fraction to plausible *illustrative* variation in model inputs?

## Mathematical setup

For a deterministic numerical solver $g(\boldsymbol\theta)$, let the uncertain parameters be $\boldsymbol\theta=(p_{T,0},f_D,K_{\mathrm{out}},\beta)$. An independently scrambled four-dimensional Sobol design produces $\mathbf u_j\in(0,1)^4$. Each $\theta_i$ is mapped linearly under the deliberately invented uniform assumption $\theta_i\sim U(a_i,b_i)$, independently across dimensions. This is a **scenario design**, not a fitted probability distribution.

The model is run with identical fixed geometry and gas settings. We examine

- $T_{50}$, time to discharge 50% of initial liquid volume (the solver's physical stopping event);
- $Q_{\max}$, the peak calculated outlet product flow;
- $Q(r)$, outlet flow at fixed *progress* $r\in[0,1]$ toward the 50% discharge target. This progress alignment prevents averaging completed runs with still-running runs at the same clock time.

We report sample quantiles $q_{0.1},q_{0.5},q_{0.9}$ and descriptive Spearman rank correlations between each input and $T_{50}$. The rank correlations **are not variance-based Sobol indices**, even though the *sample design* uses Sobol points. The quantiles are **not calibrated prediction or confidence intervals**.

## Hypothetical input intervals

| Input | Interval | Units | Interpretation |
|---|---|---|---|
| Absolute initial air pressure | 370,000–620,000 | Pa | Synthetic upstream pressure |
| Darcy factor $f_D$ | 0.015–0.035 | dimensionless | Input friction coefficient |
| Outlet loss $K_{\mathrm{out}}$ | 2–6 | dimensionless | Concentrated exit resistance |
| Holdup fraction $\beta$ | 0.10–0.30 | dimensionless | Liquid fraction left behind the tail |

All other inputs use the invented defaults in `PushStageSettings`: 100 m uniform horizontal pipe, 0.2 m diameter, density 1000 kg/m³, initial air volume 2 m³, polytropic exponent 1.2, atmospheric outlet pressure, target 50% discharged liquid. These values **are not representative of or drawn from a company's installation**.

## Method and reproducibility

`src/pipeline_flow/uncertainty.py` uses `scipy.stats.qmc.Sobol(scramble=True, seed=20261101)` with $N=2^8=256$ scenarios. The existing `simulate_push_stage` ODE solver is called for each parameter vector. Stalls, time limits or invalid states are **errors rather than silently dropped samples**. Sample envelopes are calculated at 51 common fractions of discharged-product target; the seed, bounds and numerical tolerances are recorded in code.

```bash
python -m pip install -e '.[dev]'
python -m pytest
python examples/phase5_uncertainty_figures.py
```

The example saves four PNG and SVG figures to `figures/`. Additional tests check reproducibility, boundary mapping, physical stopping, uncertainty interval ordering, and missing-target handling.

## Limitations

- Invented independent uniform distributions encode **assumptions**, not measured industrial uncertainty.
- This applies only to the limited uniform-pipe **Push** ODE, not to a coupled four-stage process or to the Blow film illustration.
- Parameters may be correlated in a real application and some may be state dependent.
- Sample quantiles are design-conditional summaries, not statistical coverage claims or model-error bounds.
- A stable median across nested sample counts does **not** certify QMC convergence. Multiple independently scrambled designs and a larger numerical error study would be needed to quantify integration error.
- Input uncertainty excludes structural/model-form discrepancy, manufacturing tolerances, missing physics, and measurement uncertainty; this cannot determine industrial cleaning reliability or guarantee a removal target.

This work builds on the public pipe-emptying model of Tijsseling et al. (2016) and on general numerical QMC methodology; see the sources directory.
