# Public development roadmap

## Phase 1 — Foundation
- [x] Separate project structure and installable Python package
- [x] Source ledger and scientific scope
- [x] Synthetic inputs, reproducible figures and automated tests
- [x] Disclosure checklist and restrictive `.gitignore`
- [ ] Publish the repository once an empty GitHub repository is created
- [ ] Point the portfolio's one project link to the published repository

## Phase 2 — Push
- [x] Review constant- and expanding-gas boundary assumptions
- [x] Implement the restricted uniform-pipe moving-column balance and document its terms against the published model
- [x] Extend tests for pressure and numerical-step convergence
- [x] Distinguish the simplified public solver from the original engineering system
- [x] Prepare a code-generated Push plot for the website (publication if appropriate)

## Phase 3 — Pipe resistance
- [x] Literature-based pipe segments, Darcy–Weisbach friction and local losses
- [x] Synthetic pressure-loss scenarios and edge-case tests
- [x] Explicit distinction between equivalent diameter and pressure-loss equivalence
- [ ] Later integration: transient segmented Push momentum solver (not claimed as part of this phase)

## Phase 4 — Blow
- [x] Implement a limited uniform-pipe liquid-column transition and test volumetric conservation
- [x] Add a separate hypothetical first-order film-inventory demonstration
- [x] Document Cioncolini–Thome applicability warnings; full correlations are intentionally NOT implemented

## Phase 5 — Uncertainty
- [x] Sensitivity and quasi-Monte Carlo on independent hypothetical parameter ranges
- [x] Explicit sample quantile bands, numerical checks and assumption register
- [ ] Future: independently replicated scrambles for QMC error estimates, model discrepancy and experimental validation

## Phase 6 — Rinse and Dry
- [x] Add limited, labelled Rinse water/product compartment model and Dry first-order water removal illustration
- [x] Explicitly transfer water, product inventories and metadata from Rinse to Dry
- [x] Test two independent component balances, handoff and stopping conditions
- [x] Preserve explicit distinctions between illustration, verification and validation
- [ ] Future: calibrate physical closures against permitted independent experiments and connect a genuine four-stage solver


## Phase 7 — Consolidation and release review
- [x] Curated five plot types and retained all reproducible source generators
- [x] Updated short README and release-scoped technical notes
- [x] Added release preflight and complete figure reproduction to CI
- [x] Reinstalled in a separate local project copy and reran 177 tests
- [ ] Publish to a newly created, dedicated GitHub repository (owner action required)
- [ ] Verify remote contents and update the website link to that dedicated repository
