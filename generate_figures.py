# Phase 7 — Public repository consolidation

## Objective

Make the independent examples of published flow mathematics easier to review: a short README, five selected source-generated figures, one canonical `src/pipeline_flow/` package, reproducible sample scripts, a simple CI workflow and an explicit disclosure boundary.

## What changed

1. Replaced the historical phase-by-phase README with a concise research summary, a five-figure gallery and accurate model boundaries.
2. Kept the complete modular source and tests from Phases 1–6. Separate models are **not** falsely connected into a validated four-stage solver.
3. Retained five representative chart pairs (PNG + SVG); the other 16 chart types are regenerable from the scripts but not versioned.
4. Added `tools/reproduce_all.py` and `tools/audit_release.py` to make reproduction and basic privacy checks repeatable.
5. Expanded CI to run all figure-generation programs and publication preflight.

## Verification evidence

- Date: 2026-11-01.
- Environment: Python 3.13.5 with existing NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, and pytest 9.0.2.
- Install: fresh local copy of the package installed in editable mode using available dependencies in this runtime (not an independent clean-room dependency download).
- Tests: **177 passed** (no failed tests).
- Figure scripts: all six completed, including 256 scrambled-Sobol Push scenarios.
- Volume/transfer checks: as implemented in the tests and example scripts. They demonstrate numerical consistency, **not validation against measurements**.
- Privacy check: a conservative filename and keyword scan; a human disclosure review is still required.

## Limitations before final release

- Verify ownership and permission to publish independently written code referencing company experience.
- Confirm none of the published numerical values or descriptions inadvertently disclose sensitive operational information.
- Obtain or decide an explicit software licence separately; none is granted here.
- Dedicated GitHub repository `pipeline-flow-modelling` requires manual creation if it does not already exist; do not point the portfolio to it until upload is verified.

## Checklist for GitHub upload

1. Create an empty public repo named `pipeline-flow-modelling` without auto-generated README or licence.
2. Extract the Phase 7 ZIP, open a terminal **inside** `pipeline-flow-modelling`, and run `python -m pip install -e ".[dev]"` plus `python -m pytest`.
3. Run `python tools/audit_release.py`, review `git status` and `git diff --cached` and check the images.
4. Commit and push only the files in this release package.
5. Verify GitHub renders the README and all five curated plot links before changing the portfolio's repository link.
