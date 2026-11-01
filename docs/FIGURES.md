# Figure guide

Five code-generated examples are selected for the public repository. All inputs are hypothetical; none of these figures are measurements, validated forecasts or industrial operating guidance.

| Phase | Preview | What is and is not shown |
| --- | --- | --- |
| Push | [PNG](../figures/push-discharge-comparison.png) · [SVG](../figures/push-discharge-comparison.svg) | Liquid discharge under two idealized pressure assumptions; not experimental outflow |
| Pipeline resistance | [PNG](../figures/phase3-segmented-vs-equivalent.png) · [SVG](../figures/phase3-segmented-vs-equivalent.svg) | Pressure-loss comparison using invented pipe segments; steady single-phase flow only |
| Blow | [PNG](../figures/phase4-blow-transition-volumes.png) · [SVG](../figures/phase4-blow-transition-volumes.svg) | Full-column, exported and retained liquid volume; not validated annular film removal |
| Uncertainty | [PNG](../figures/phase5-push-qmc-flow-band.png) · [SVG](../figures/phase5-push-qmc-flow-band.svg) | Pointwise sample percentiles across 256 invented parameter scenarios; not confidence bands |
| Rinse / Dry | [PNG](../figures/phase6-rinse-dry-water-inventory.png) · [SVG](../figures/phase6-rinse-dry-water-inventory.svg) | Explicit water-inventory handoff; drying rate and removal target are uncalibrated |

All 21 original figure types are reproducible using `python tools/reproduce_all.py`. To prevent excessive gallery clutter, only five pairs (SVG and PNG) are versioned. New generated files are ignored by Git unless explicitly reviewed and added.
