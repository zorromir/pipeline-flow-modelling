# Phase 4 — Blow: moving-column transition and film inventory

## Status

Two **independent public teaching examples** are implemented:

1. A constant-pressure, uniform-diameter, one-dimensional moving-column transition, with explicitly tracked outflow and tail leakage.
2. A generic first-order residual-film inventory demonstration using independently chosen hypothetical rates.

These examples **do not** form an integrated industrial Blow simulator. They do not implement the Cioncolini–Thome annular-flow correlations or infer film-removal rates from gas flow. There is no measured boundary pressure, compressor curve, private product property, calibration, or field-data validation.

## Transition: balance laws and scope

Let \(U\) be the discharge velocity of liquid, \(L\) the remaining full liquid-column length, \(A\) pipe cross-sectional area, and \(\alpha\in(0,1]\) a *hypothetical* partition parameter. The control-volume relationships are

$$
\frac{dL}{dt}=-\frac{U}{\alpha},\qquad
Q_{\mathrm{out}}=AU,\qquad
Q_{\mathrm{tail}}=AU\left(\frac{1}{\alpha}-1\right).
$$

For \(\alpha=1\), no liquid is retained at the tail within this bookkeeping. For \(0<\alpha<1\), a fraction is left behind; it is not yet assumed to be a validated uniform wall film.

The **restricted demonstration** uses a constant upstream absolute pressure and an externally specified outflow pressure. Its momentum equation is

$$
\frac{dU}{dt}
=\frac{\Delta p / \rho - \tfrac12(f_D L/D+K)U|U|}{L}
+\left[\beta\left(\frac1\alpha-1\right)-1\right]\frac{U|U|}{L}.
$$

Here \(f_D\) is a fixed Darcy factor, \(K\) a single local-loss coefficient, and \(\beta\) a *separate* dimensionless residual-momentum parameter. Neither coefficient is estimated or calibrated. **The transition does not include a hydrostatic elevation term**, a predictive compressor curve or segmented multiphase flow.

The integrated state is \([U,L,V_{\mathrm{out}},V_{\mathrm{tail}}]\). Because

$$
- A\frac{dL}{dt}
= \frac{dV_{\mathrm{out}}}{dt}
+\frac{dV_{\mathrm{tail}}}{dt},
$$

mass conservation requires

$$
V_0= AL(t)+V_{\mathrm{out}}(t)+V_{\mathrm{tail}}(t).
$$

The numerical solver stops when a prescribed positive column-length threshold is reached, *before* the \(1/L\) singularity. It reports a time-limit status if the threshold cannot be reached. The stopping threshold is a **modelling boundary**, not experimental evidence that all liquid has disappeared.

## Film: separated illustrative surrogate

The additional plot uses only

$$
\frac{dV_f}{dt}=-kV_f,\qquad V_f(t)=V_{f,0}e^{-kt}.
$$

The parameter \(k\) is a directly assumed, hypothetical constant. **It is not inferred from wall shear or the Cioncolini–Thome correlations**, and no physical cleaning-rate claim follows from this exercise. The film model is intentionally *not* auto-initialized from the transition's tail-leakage inventory: the transition may stop while a nonzero full column remains.

## Why annular correlations are not yet in the public implementation

The underlying technical report distinguishes the transition from an annular gas–liquid model. Its annular stage uses literature correlations by Cioncolini and Thome (2012, 2013 and 2017) for void fraction, film asymmetry and pressure drop/wall stress. Their domains of applicability must be assessed before use for a new diameter, fluid, or flow regime. Merely labelling the gas–liquid mixture 'annular' does not establish the regime. The current repository deliberately does **not** copy company software or reproduce unverified internal empirical film-stripping constants.

Future work would require a **public-source-only** implementation of the full correlations, published benchmark verification, explicit flow-pattern checks and independent experimental validation where disclosure is permitted. Do not label the current demonstration a validated annular-pressure or product-removal model.

## Reproduce

```bash
python -m pip install -e ".[dev]"
python -m pytest
python examples/blow_phase4_figures.py
```

Figures in `figures/`:

- `phase4-blow-transition-volumes` — volume partition over time (best public overview).
- `phase4-blow-transition-dynamics` — outlet speed during the shortened-column transition.
- `phase4-illustrative-film-inventory` — generic exponential decay under 3 invented rates.

## Numerical verification

- Exact physical quantity/units and sign choices.
- Closed volume balance with separately integrated outflow and tail leakage.
- Positive remaining length; root-located stopping event.
- Parameter-domain rejection, time-limit status, and step-refinement comparison.
- Film-inventory nonnegativity and conservation.

All tests use hypothetical inputs; no accuracy-versus-measurement result is claimed.

## Attribution

Public scientific context: Laanearu et al. (2012; 2014), Tijsseling et al. (2016), and Cioncolini–Thome (2012; 2013; 2017). Full citations are in [sources.md](../references/sources.md). The research basis is drawn from the user's private technical report (Section 6 and Appendix E), which **must not be committed or included in a public archive**. This repository contains an independently written subset for education and demonstration only.
