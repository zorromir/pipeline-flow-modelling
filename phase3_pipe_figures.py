# Public release checklist

Only new, independently written examples of public mathematics are intended for this repository. Before any future commit, confirm:

- [ ] No original employer source files, copied code, internal reports or nonpublic diagrams.
- [ ] No measurement series, experimental run identifiers, sensor exports or validation graphics.
- [ ] No real pipe geometries, component inventories, machine set-points or calibrated coefficients.
- [ ] No filenames, images, metadata, notebooks or notebook outputs that reveal private locations or equipment.
- [ ] No credentials, customer names, account details, business documents or internal URLs.
- [ ] Every figure clearly indicates whether it is simulated, measured, or conceptually illustrated.
- [ ] Any public numerical constants are hypothetical or cited from published sources.
- [ ] Model code, figures and descriptions do not claim validation that has not occurred.
- [ ] Permission is obtained before releasing any original company-owned material, even if the data are removed.

**Important:** `.gitignore` does not stop a file from being included if deliberately force-added, nor does deleting a file remove it from Git history. Review every staged file before committing, including images and archives.

## Phase 2 checkpoint (2026-11-01)

- Public demonstration uses independently implemented published equations and invented input values.
- No experimental observations, original reports, proprietary calibration, or company code are bundled.
- Tests demonstrate numerical consistency, *not* validation against physical experiments.
- Review in GitHub remains necessary before public release.


## Phase 3 checkpoint (2026-11-01)

- Synthetic geometries were newly specified for this public demo, not copied from the internal report.
- The new files contain standard segment-area/volume identities, steady Darcy–Weisbach and local K losses.
- No measurement-driven fitting, raw test records or operational configurations are required.
- The segmented steady solver is deliberately not described as a verified transient multiphase model.
- The new figures reproduce hypothetical inputs and have labels explaining their scope.
- Run the publication check against all pending files before releasing to GitHub.

## Phase 4 checkpoint (2026-11-01)

- Transition uses a separate independently implemented control-volume model with completely invented inputs.
- No company experimental curves, pressure traces, film-stripping parameters or Cioncolini–Thome proprietary implementations are included.
- Generic first-order film decay is only an inventory example, not a cleaning-effectiveness prediction.
- Transition stopping threshold and nonzero residual column are disclosed; the transition's output is not automatically treated as annular film.
- Full correlation validation and permissions remain unresolved future work.

## Phase 6 checkpoint (2026-11-01)

- Rinse and Dry are **new, independent mathematical demonstrations**, not copies of employer software.
- All physical inputs, cleaning rates, inventory goals and end-of-stage thresholds are invented; no factory test records are used.
- The code checks separate conservation of water and product as well as exact inventory transfer to Dry.
- The Dry exponent is not physically calibrated and is not tied to compressor mass flow.
- The example demonstrates only Rinse→Dry transfer, **not** a full four-stage industrial model.
- Inspect each release and its image metadata for any accidental proprietary input before publication.


## Phase 7 publication gate (2026-11-01)

- [x] Source and test files consolidated into one installable Python package.
- [x] Only five curated figures (PNG and SVG) included in the release ZIP.
- [x] All six synthesis scripts rerun; 177 unit tests passed using a separate local copy of the package.
- [x] Conservative automatic file/identifier preflight passed; this is not proof of confidentiality or legal clearance.
- [ ] Manually review generated figures, metadata and text against confidentiality obligations.
- [ ] Obtain any necessary authorization for publication of original research outcomes.
- [ ] Create dedicated public GitHub repository and upload the release.
- [ ] Confirm the repository URL and then link the portfolio to it.
