# Phase 2 — Air-driven liquid-column displacement

The idea here is simple: compressed air pushes a liquid column towards the outlet, and I want to calculate how the motion changes over time. This public example is an **AI-assisted reconstruction** of selected mathematical ideas from my industrial project. It uses the one-dimensional equations discussed by Tijsseling et al. (2016), simplified to a uniform horizontal pipe with invented parameters. It does not include the original company code or measurements.

## What the model follows

The solver integrates two time-dependent quantities:

- $Q(t)$: **product discharged at the outlet**, in $\mathrm{m^3/s}$.
- $x(t)$: **position of the moving tail** relative to the start, in metres.

With constant cross-sectional area $A=\pi D^2/4$, initial full-liquid length $L_0$ and stationary holdup fraction $\beta$, the moving full liquid column is $L(t)=L_0-x(t)$. The interface velocity is

$$
v_T(t)=\frac{Q(t)}{(1-\beta)A},\qquad \frac{dx}{dt}=v_T.
$$

The holdup fraction describes the idealized share of passed volume that stays behind. It is not a prediction of actual cleaning performance.

## Momentum balance

To represent the pressure force, liquid inertia and flow resistance, I use the following uniform-area, horizontal-pipe balance:

$$
\left(1-\frac{\beta}{2}\right)L\frac{dv_T}{dt}
=\beta(1-\beta)v_T^2+\frac{p_T-p_{\rm out}}{\rho}
-\frac{f_D}{2D}\left(1-\beta+\frac{\beta^2}{3}\right)Lv_T|v_T|
-\frac{K_{\rm out}}{2}v_{\rm out}|v_{\rm out}|.
$$

Here $v_{\rm out}=(1-\beta)v_T$. The program implements $dQ/dt=(1-\beta)A\,dv_T/dt$ and $dx/dt=v_T$. The signed quadratic-loss form reduces to the published $v^2$ expression for forward motion. Elevation is omitted by deliberately setting $z_T=z_{\rm out}$. This demonstration is not intended to represent the full geometry of a real installation.

## Pressure boundaries

Choose `pressure_mode="constant"` to hold $p_T=p_{T,0}$ fixed, or `pressure_mode="isolated_expansion"` for the **coupled** polytropic source

$$
V_g(t)=V_{g,0}+Ax(t), \qquad
p_T(t)=p_{T,0}\left(\frac{V_{g,0}}{V_g(t)}\right)^n.
$$

In the expanding-air case, the solver updates pressure as the gas volume changes. Both $p_T$ and $p_{\rm out}$ are **absolute pressures** (Pa). No compressor operating curve, active air replenishment, or full tank dynamics is modelled.

## Product-volume balance

For the synthetic uniform-area pipe:

$$
V_{\rm passed}=Ax,\qquad
V_{\rm out}=(1-\beta)Ax,\qquad
V_{\rm holdup}=\beta Ax,\qquad
V_{\rm full}=A(L_0-x).
$$

The solver exposes the residual $R_V=A L_0 - V_{\rm out}-V_{\rm holdup}-V_{\rm full}$. It also computes a diagnostic momentum residual, and the tests independently compare numerical derivatives and time-integrated outflow against the equations.

## Stopping and numerical safeguards

`scipy.integrate.solve_ivp` (DOP853) solves $[Q,x]$ with root-located terminal events. The simulation ends at the first of the **discharged-product target**, **minimum remaining full column**, **zero forward flow** (stall), or the **time limit**. An unreachable target is rejected before integration. Neither continuing past zero liquid-column length nor presenting a guessed end phase is allowed. Decreasing numerical time steps and tolerances is part of automated verification.

## How to reproduce

```bash
pip install -e '.[dev]'
pytest
python examples/push_stage_figures.py
```

The figure script writes plots into `figures/` as SVG and PNG. Only invented input parameters are used. The example can be explored from an installed Python interpreter:

```python
from pipeline_flow import PushStageSettings, simulate_push_stage

result = simulate_push_stage(PushStageSettings())
print(result.stop_reason, result.stop_time_s)
```

## Interpretation and limitations

- **Verified by tests:** internally consistent mass/volume bookkeeping, physical bounds, stopping events, the two pressure laws and numerical convergence for selected synthetic cases.
- **Not established:** predictive accuracy against experimental data, calibration transferability, or suitability for any industrial installation.
- **Not implemented:** segmented pipe diameter/elevation, actual air-tank replenishment, viscosity-dependent friction factor, waterhammer, and downstream Blow/Rinse/Dry models.
- **Research attribution:** Tijsseling, Hou, Bozkuş & Laanearu (2016), *Improved One-Dimensional Models for Rapid Emptying and Filling of Pipelines*, [DOI 10.1115/1.4031508](https://doi.org/10.1115/1.4031508). The public code was reconstructed with AI assistance from published equations. It is not the authors' original software or my confidential industrial implementation.
