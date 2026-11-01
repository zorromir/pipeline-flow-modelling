# Public repository release notes

The public repository is now available at [github.com/zorromir/pipeline-flow-modelling](https://github.com/zorromir/pipeline-flow-modelling). I use it to show selected modelling methods from my six-month industrial research project.

**Disclosure:** The original industrial work was mine. The public code is an **AI-assisted reconstruction** of selected mathematical examples, not the original company implementation. It contains hypothetical inputs rather than confidential measurements or specifications.

## What I included

- One installable Python package under `src/pipeline_flow/`.
- Separate Push, pipe-resistance, Blow, uncertainty and Rinse/Dry examples.
- Five selected plots generated from Python; the scripts can regenerate additional figures.
- Unit tests, numerical stopping conditions and conservation checks.
- A GitHub Actions workflow for running tests, reproducing figures and checking for obvious disclosure mistakes.

The modules are related, but they do **not** form one validated four-stage industrial model.

## Numerical checks at the time of consolidation

On 1 November 2026 I tested a separate local copy of the release:

- Python 3.13.5 with installed NumPy, SciPy, Matplotlib and pytest dependencies.
- **177 tests passed** in that local environment.
- All six figure-generation scripts completed, including the 256-scenario scrambled Sobol example.
- A conservative file and keyword scan found no obvious prohibited input files.

This was a local verification run, not an independent reproduction of the original industrial experiments. The repository's GitHub Actions workflow should also be checked after later commits.

## Publication boundary

I do not publish the employer's code, data, geometry, calibration or original report. Numerical examples use published mathematics and invented parameters.

The automated release check does not establish legal permission to publish or guarantee that sensitive material could never appear. Further code or industrial results should only be added after a manual disclosure and rights review. No software licence has yet been granted.

For the current project overview and installation instructions, see the [README](../README.md). For future changes, use the [publication checklist](PUBLICATION_CHECKLIST.md).
