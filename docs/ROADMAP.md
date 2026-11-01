# Development notes and possible next steps

This repository grew in stages as I reconstructed selected mathematical examples from my industrial project with AI assistance. The original code and data remain confidential; this is a separate set of public examples.

## Already included

- **Push:** a one-dimensional moving-liquid-column solver with two air-pressure assumptions.
- **Geometry:** segmented pipe volumes and steady single-phase pressure losses.
- **Blow:** a liquid-column transition with conservation checks and a separate illustrative film-decay example.
- **Uncertainty:** scrambled Sobol sampling of hypothetical Push input ranges.
- **Rinse and Dry:** compartment inventories and an explicit Rinse-to-Dry water handoff.
- **Reproducibility:** an installable Python package, tests, figure generators, selected plots, a release audit and GitHub Actions.

The public [repository](https://github.com/zorromir/pipeline-flow-modelling) is published, and the [portfolio Projects page](https://zorromir.github.io/#projects) links to it.

## Ideas for further work

These are not implemented or validated yet:

1. Couple the segmented geometry layer to a consistent transient Push equation.
2. Study published annular-flow correlations and check their applicability before implementing any film model.
3. Use public benchmark measurements, where licences allow, for an independent validation exercise.
4. Run multiple independently scrambled Sobol designs to examine numerical QMC uncertainty.
5. Explore a genuinely coupled stage model only after the physical assumptions and state transfers are justified.

I will keep future work separate from the confidential industrial implementation. Any new numerical results or figures should be clearly identified as synthetic, public-data-based or experimental, depending on their actual source.

See [model scope](MODEL_SCOPE.md) and the [publication checklist](PUBLICATION_CHECKLIST.md).
