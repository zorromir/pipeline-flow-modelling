name: Python verification and synthetic figure reproduction

on:
  push:
  pull_request:

jobs:
  numerical-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install package and test dependencies
        run: python -m pip install -e ".[dev]"
      - name: Run model verification tests
        run: python -m pytest
      - name: Regenerate all figures from synthetic inputs
        run: python tools/reproduce_all.py
      - name: Check public file types and obvious identifiers
        run: python tools/audit_release.py
