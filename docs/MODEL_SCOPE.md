# What the public models cover

This repository presents selected mathematical models and numerical examples rather than the complete industrial simulator. The original company code and measurements remain confidential. The public examples use published equations and hypothetical inputs.

## Which parts are implemented?

**Push.** The numerical example follows the outlet flow $Q$ and the position of a moving liquid interface $x_T$ in a straight, horizontal pipe. It assumes a uniform area, fixed density and friction parameters, and a constant holdup fraction. The upstream pressure can remain constant or decrease as a trapped gas volume expands.

**Pipe geometry and resistance.** A separate calculation handles several pipe segments, their volumes, elevations, wall friction and local pressure losses. This is a steady, single-phase model. It has **not** been coupled to the moving-column Push equations.

**Blow.** The transition example tracks a shortening full liquid column, discharged liquid and liquid left behind. A separate first-order film-inventory example shows what changing an assumed removal rate does. It is **not** a validated annular-flow model, and the two examples are not automatically linked.

**Rinse and Dry.** Rinse uses three illustrative mixing compartments with water, mobile product and product on the wall. A state transfer passes the remaining water to a separate first-order Dry model. The transfer is checked, but Push and Blow are not connected to these stages. Gas mass flow is recorded only as metadata, not used to determine the drying rate.

**Uncertainty.** Scrambled Sobol sampling varies four independently assumed uniform input ranges for the Push example. I use the resulting sample percentiles and exploratory rank correlations to illustrate uncertainty propagation. These are not fitted distributions, variance-based Sobol sensitivity indices or validated prediction intervals.

## What has not been modelled?

The examples do not include an industrial compressor curve, active tank replenishment, full transient pipe segmentation, non-Newtonian fluids, waterhammer, three-dimensional interfaces, annular-flow correlations, complete flow-regime selection, calibrated cleaning kinetics or experimentally validated drying. The full four-stage engineering application is outside this repository.

## How I check the calculations

The ODE examples use `scipy.integrate.solve_ivp`. The tests cover physical stopping conditions, volume balances, numerical consistency and selected convergence cases. This is useful for checking the **implementation**, but it is not the same as showing the model matches real measurements.

All parameter values in the public examples are hypothetical and unrelated to any installation I worked on. The [README](../README.md) explains the public implementation's provenance and confidentiality boundary.
