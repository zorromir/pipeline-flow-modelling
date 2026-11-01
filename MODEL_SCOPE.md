# Local and confidential material
/data/
/private/
/measurements/
/experimental/
/reports/
*.csv
*.tsv
*.xlsx
*.xls
*.xpt
*.7z
*.zip
*.pdf
*.ipynb
.env
.env.*
*.pem
*.key

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/
*.egg-info/
build/
dist/

# OS / editors
.DS_Store
Thumbs.db
.vscode/
.idea/

# Keep a selected gallery; other output figures are reproducible but untracked
/figures/*
!/figures/push-discharge-comparison.png
!/figures/push-discharge-comparison.svg
!/figures/phase3-segmented-vs-equivalent.png
!/figures/phase3-segmented-vs-equivalent.svg
!/figures/phase4-blow-transition-volumes.png
!/figures/phase4-blow-transition-volumes.svg
!/figures/phase5-push-qmc-flow-band.png
!/figures/phase5-push-qmc-flow-band.svg
!/figures/phase6-rinse-dry-water-inventory.png
!/figures/phase6-rinse-dry-water-inventory.svg
