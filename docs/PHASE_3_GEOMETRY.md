# Phase 3 — Pipe geometry and resistance

This phase adds an independent, public **steady single-phase** pipeline layer.
Its content uses only elementary geometric identities and the published Darcy–Weisbach relation, not private installation layouts, industrial records or employer implementation code.

## 1. Geometry as consecutive physical segments

For each section $i$, specify a length $L_i$, inner diameter $D_i$, endpoint elevations $z_{i,-},z_{i,+}$ and a dimensionless local loss $K_i$. Its cross-sectional area and volume are

$$
A_i=\frac{\pi D_i^2}{4},\qquad V_i=A_iL_i.
$$

For a coordinate interval $[a,b]$, the length intersecting section $i=[x_{i,-},x_{i,+}]$ is

$$
\ell_i(a,b)=\max\bigl(0,\min(b,x_{i,+})-\max(a,x_{i,-})\bigr),
$$

and the corresponding liquid volume is $V(a,b)=\sum_i A_i\ell_i(a,b)$. The inverse mapping `position_from_volume` recovers the position from a prescribed volume. This is groundwork for tracking a moving interface across different diameters.

**Convention:** a section's local $K_i$ is applied at its **downstream physical end**, not redistributed when a section is divided into numerical subintervals. Endpoint heights must agree between adjacent sections. At a diameter junction `area_at(x)` selects the downstream area.

## 2. Pressure loss for a given liquid flow

For the *same* forward volume flow $Q\ge 0$ through a series of incompressible, constant-density Newtonian liquid sections,

$$
v_i=\frac{Q}{A_i},\qquad
\Delta p_i=\underbrace{f_{D,i}\frac{L_i}{D_i}\frac{\rho v_i^2}{2}}_{\text{friction}} +
\underbrace{\rho g(z_{i,+}-z_{i,-})}_{\text{elevation}} +
\underbrace{K_i\frac{\rho v_i^2}{2}}_{\text{local losses}}.
$$

The model sums physical losses across consecutive sections. Elevation contribution can be negative in a descending section; friction and $K$ contributions are nonnegative. Given an outlet pressure, the demonstration reconstructs upstream junction pressures using the same section balance.

**Not included:** kinetic-head changes across diameter transitions, additional area-change/entrance losses unless assigned to a separate $K_i$, compressibility, gas–liquid slip, spatially variable fluid density, waterhammer, Reynolds-based automatic friction factors, reversed flow, branching networks and full CFD. Those are separate physics, not silently handled by the code. The wall roughness field is stored for traceability but **not used** to derive $f_D$; Darcy factors are specified inputs. Fanning and Darcy friction factors are not interchangeable ($f_D=4 f_F$).

## 3. Why volume equivalence is not pressure equivalence

The volume-equivalent diameter is

$$
D_{\mathrm{eq}}=\sqrt{\frac{4\sum_i A_iL_i}{\pi\sum_i L_i}}.
$$

It preserves *total pipe volume*. It **does not** preserve $\sum_i f_{D,i}L_i v_i^2/D_i$ because velocity depends on $D_i^{-2}$ and friction strongly on diameter. Our demonstration compares identical pipe volume, total height change and the same sum of local $K$ values (aggregated at the equivalent outlet). The discrepancy therefore reflects differences in how local cross-sections and losses are represented; it should not be used as a corrected prediction for an actual plant.

## 4. Code files and checks

- `src/pipeline_flow/geometry.py`: immutable `PipeSegment` and `PipeNetwork`, cumulative volume, active portions, height interpolation, inverse volume map.
- `src/pipeline_flow/resistance.py`: sectionwise friction/elevation/K terms and upstream junction pressures.
- `tests/test_geometry.py`, `tests/test_resistance.py`: formula checks, inversion/interval tests, monotonic $Q^2$ losses, hydrostatic balance, loss accounting at section ends, geometry validations, uniform-section split invariance.
- `examples/phase3_pipe_figures.py`: generates `phase3-pressure-breakdown` and `phase3-segmented-vs-equivalent` in PNG and SVG.

Install and run:

```bash
python -m pip install -e '.[dev]'
python -m pytest
python examples/phase3_pipe_figures.py
```

All dimensions and coefficients in the example are **invented**. They are not measurements or fitted industrial parameters.

## 5. Model integration boundary

The Phase 2 Push solver still assumes one uniform horizontal pipe. Phase 3 implements and verifies the **common geometry/steady-hydraulics layer separately**; it does **not** claim to have coupled that layer to the moving-column ODE. Doing so requires a consistent transient segmented momentum equation, special care at diameter junctions and new numerical-convergence tests. Similarly, the Phase 4 Blow solver will need regime-specific two-phase pressure losses rather than directly applying these one-phase relations.

### Literature basis

- Darcy–Weisbach relation for pipe friction and standard hydrostatic balance.
- Tijsseling, Hou, Bozkuş & Laanearu (2016), *Improved One-Dimensional Models for Rapid Emptying and Filling of Pipelines*, [DOI: 10.1115/1.4031508](https://doi.org/10.1115/1.4031508). Its moving-column formulation motivates subsequent integration; no complete reproduction of that research code is claimed.
