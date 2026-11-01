# Model scope and limitations

**Current calculation:** public Phase 2 implements a straight, horizontal rigid-column example using state variables $[Q,x_T]$. It supports either constant tail pressure or coupled expansion of an isolated initial gas volume. Uniform area, constant density, fixed wall and outlet-loss coefficients and constant stationary holdup are assumed.

**Independent examples:** the Phase 1 stand-alone polytropic pressure and volume-balance helpers remain, while Phase 2 has an additional solver which couples isolated-gas pressure to liquid motion.

**Phase 4 separate teaching examples:** `blow_transition.py` uses a constant-pressure, full-column control-volume transition with two independent leak/impulse parameters. `film_demo.py` is only a first-order hypothetical inventory decay, not an annular or cleaning model. The two are not coupled.

**Phase 6 separate Rinse/Dry demonstration:** Three notional well-mixed pipe compartments exchange water and product; an independently chosen first-order wall detachment is illustrative, and a typed Rinse→Dry transfer starts a separate first-order water-removal demonstration. They do not simulate two-phase hydrodynamics or real cleaning/drying efficiency. The models are not coupled to Push or Blow; gas mass flow is only carried as metadata.

**Not modelled here:** industrial tank replenishment, a compressor operating curve, pipe elevations or segmentation, non-Newtonian fluids, waterhammer, 3D interface shapes, annular-flow film correlations, true two-phase flow-regime selection, experimentally validated cleaning kinetics, physically calibrated rinse dilution, industrial drying performance, and uncertainty calibration. The four-stage engineering application is outside the current repository.

**Numerics:** `scipy.integrate.solve_ivp` with root-located events for volume target, positive column length, flow stall and end-of-window. Tests check independent time-derivative and integrated-flow consistency, conservation, and numerical convergence. These are verification checks, not experimental validation.

**Data provenance:** all numerical values are illustrative and deliberately unrelated to any commissioned installation. No original research report, measurement record, factory dimensions, sample identities, calibration tables or confidential code belongs here.

## Phase 5 scope

Scrambled Sobol sampling of four **invented independent uniform** Push inputs yields model-conditional percentiles and exploratory rank correlations. No company measurements, parameter estimation, statistical coverage guarantee, variance-based Sobol indices or coupled four-stage uncertainty analysis.
