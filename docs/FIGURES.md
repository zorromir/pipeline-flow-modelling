# Figures

I selected five plots that give a quick view of the different models. The Python scripts generate these figures from hypothetical inputs. They are not measured industrial results.

| Example | Figures | What to look for |
| --- | --- | --- |
| Push | [PNG](../figures/push-discharge-comparison.png) · [SVG](../figures/push-discharge-comparison.svg) | Two air-pressure assumptions give different liquid-discharge curves over time. |
| Pipe resistance | [PNG](../figures/phase3-segmented-vs-equivalent.png) · [SVG](../figures/phase3-segmented-vs-equivalent.svg) | A pipe with several diameters can have different pressure losses from a single pipe with the same total volume. |
| Blow | [PNG](../figures/phase4-blow-transition-volumes.png) · [SVG](../figures/phase4-blow-transition-volumes.svg) | The initial liquid is divided between the remaining column, discharged volume and liquid left behind. |
| Uncertainty | [PNG](../figures/phase5-push-qmc-flow-band.png) · [SVG](../figures/phase5-push-qmc-flow-band.svg) | The median and 10th–90th sample percentiles across 256 assumed input combinations, aligned by discharge progress rather than time. |
| Rinse / Dry | [PNG](../figures/phase6-rinse-dry-water-inventory.png) · [SVG](../figures/phase6-rinse-dry-water-inventory.svg) | The water remaining after Rinse becomes the starting inventory for Dry. |

These plots illustrate the calculations and help me check their behaviour. They do not establish industrial predictive accuracy. The Blow film model and the Rinse/Dry removal rates are especially simplified.

To generate the full set of examples locally, run:

```bash
python -m pip install -e ".[dev]"
python tools/reproduce_all.py
```

Only the five selected plot pairs (PNG and SVG) are committed. Other diagnostic figures can be regenerated from the code.

The plotting code uses hypothetical inputs; no confidential datasets or original industrial figures were used. See the [README](../README.md) for provenance and limitations.
