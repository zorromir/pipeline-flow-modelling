# Checklist before publishing changes

I use this list whenever I add new code, data, figures or documentation to the public repository. The examples were reconstructed with AI assistance, and the original company code and test data are confidential.

## Information and permissions

- [ ] No original employer source files, reports, internal screenshots or diagrams.
- [ ] No measurements, sensor traces, internal validation graphs or real equipment specifications.
- [ ] No calibrated coefficients, actual operating settings, customer details or internal URLs.
- [ ] No hidden private data in image metadata, archives, notebooks or Git history.
- [ ] Any new material is permitted to be shared; obtain authorization when ownership is unclear.
- [ ] The AI-assisted reconstruction disclosure still accurately describes how the public code was produced.

## Scientific descriptions

- [ ] Inputs are hypothetical or traceable to published sources.
- [ ] Figures clearly say what is simulated and which axes or quantities are shown.
- [ ] The documentation distinguishes verified numerical behaviour from experimental validation.
- [ ] Unimplemented physics, such as a fully coupled four-stage model or validated annular-film transport, is not claimed.
- [ ] Links to scientific papers and reproducible code point to the right files.

## Before pushing

```bash
python -m pip install -e ".[dev]"
python -m pytest
python tools/reproduce_all.py
python tools/audit_release.py
git status
git diff --cached
```

These commands are checks, not proof that publication is legally or technically safe. I still need to inspect the staged files myself. `.gitignore` cannot protect data already tracked by Git, and removing a file in a new commit does not erase it from earlier history.

## Current release

The repository was published in November 2026 with synthetic examples and a small selected figure gallery. A local release audit previously reported **177 passing tests**, but that result should not be presented as measured model accuracy. The original industrial work remains confidential.

There is no software licence in the repository. Publishing source files on GitHub does not automatically grant a general reuse licence.
