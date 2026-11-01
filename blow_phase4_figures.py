# Phase 6 — Rinse, Dry and explicit state transfer

## Status

This is a **standalone, independently written, synthetic process demonstration**.
It illustrates material inventories and process-stage interfaces. It is neither a
full four-stage engineering calculation nor an experimental cleaning/drying model.

The internal technical report motivating the broader project distinguishes four
operational stages and documents a Rinse state containing water, mobile product,
and wall product per segment, followed by a simpler Dry state containing remaining
water. It explicitly notes empirical Rinse cleaning and a provisional first-order
Dry approximation. The report itself and industrial source code are **not** included.

## Rinse — compartment inventories and product conservation

A pipe is replaced by $N$ effective well-mixed inventories, with *invented*
reference mixing volumes $V_i$ and imposed water feed $q>0$.

Let $W_i$ denote mobile water, $P_i$ mobile product, and $B_i$ an immobile
product inventory in segment $i$, all in litres. Define an **effective exchange
rate**, $a_i=q/V_i$ (per second), and the hypothetical wall-detachment rate $k$.

For $i=1,\dots,N$ (with $a_0W_0=a_0P_0=0$):

$$
\begin{aligned}
\dot W_i &= \mathbf 1_{i=1}q+a_{i-1}W_{i-1}-a_iW_i,\\
\dot P_i &= a_{i-1}P_{i-1}-a_iP_i+kB_i,\\
\dot B_i &= -kB_i.
\end{aligned}
$$

Cumulative quantities are

$$
\dot I_W=q,\qquad \dot O_W=a_NW_N,\qquad \dot O_P=a_NP_N.
$$

Two exact *global* conservation identities are asserted in software:

$$
I_W=\sum_i W_i+O_W, \qquad
\sum_i(B_i+P_i)+O_P=\sum_i[B_i(0)+P_i(0)].
$$

The inflow $q$, mixing volumes and $k$ are **illustrative model choices**, not
measured operating parameters or calibrated cleaning kinetics. In particular,
$V_i$ controls the exchange time; it must **not** be interpreted as an exact
physical liquid-filled volume constraint. There are no pressure, airflow,
compressor, hydration, real dilution-concentration or hygienic submodels.

### Stop condition

This demonstration terminates when the **cumulative supplied water** first
reaches an illustrative goal $I_W^*=48\,\mathrm L$, not at an experimentally
verified cleanliness target. The industrial report's current Rinse software is
also described as predominantly time driven; this demonstration is not presented
as a reproduction of its real control logic.

## Typed Rinse → Dry transfer

A frozen `RinseToDryTransfer` records $t_{\mathrm end}$, remaining water, product
inventories by segment, and gas mass flow as **metadata**. Dry begins at precisely
the transferred water inventory. Both water and product handoff residuals are
checked to numerical precision. The model **does not** automatically couple the
Blow solver into Rinse, nor use gas mass flow to calculate the Rinse or Dry rates.

## Dry — illustrative first-order water removal

Starting from the water inventory $W_0$ delivered by the Rinse stage,

$$
W(t)=W_0\exp(-k_Dt),\qquad O_D(t)=W_0-W(t).
$$

Dry stops at a chosen fraction of initial Dry-stage water removed,
$1-W/W_0\geq f_{\rm target}$, *if* it can reach that fraction before a maximum
duration. Otherwise its stop reason is `time_limit`. A zero-rate case is
supported. This is a **surrogate stopping definition**: the report does not yet
fix a definitive mathematical industrial dryness criterion. Product stays
unchanged in this simple Dry model; gas flow is only passed through as metadata.

## Example and results

The defaults use 3 invented compartments, $q=0.8\,\mathrm{L/s}$,
$V_i=12\,\mathrm L$, $k=0.025\,\mathrm{s^{-1}}$, a 48 L Rinse water goal,
and $k_D=0.026\,\mathrm{s^{-1}}$ with a **hypothetical** target of 90% water
removed during Dry.

- Rinse ends after 60.00 s, with 48.00 L cumulative water supplied.
- Rinse leaves approximately 31.82 L in the effective compartments.
- Dry reaches its illustrative water-removal target after about 88.56 s.
- Remaining water is approximately 3.18 L at the illustrative Dry stop.

These are synthetic numerical outputs, **not** experimentally validated
water use, cleaning effectiveness or drying times. Comparing them to a real
installation or using them for machine operation would be inappropriate.

## Verification and boundaries

The test suite checks finite/nonnegative inputs, mismatched segment vectors,
nonnegative inventories, monotonic cumulative export, exactly conserved water
and product separately, wall transfer into mobile product, zero detachment,
zero initial product, zero removal rate, unattainable targets, and Rinse/Dry
state continuity. These are **mathematical/software tests**, not external
physical validation.

Full Cioncolini–Thome annular pressure drop, real water/product reology,
compressor coupling, empirically calibrated cleaning kinetics, actual dryer
performance, branched pipelines and a full Push→Blow→Rinse→Dry solver are
**not** implemented in the public package.

## Reproduce

```bash
python -m pip install -e '.[dev]'
python -m pytest
python examples/phase6_rinse_dry_figures.py
```

Plots are under `figures/` and contain **only hypothetical simulations**.
