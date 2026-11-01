"""Conservative preflight for accidental disclosure in a public source tree.

This static check cannot detect encoded secrets, copied code or all data leakage.
It is not a substitute for manual review or employer permission.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("src", "examples", "tests", "docs", "references", "figures", ".github")
SKIP_GENERATED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
ROOT_FILES = ("README.md", "pyproject.toml", ".gitignore")
BANNED_SUFFIXES = {".csv", ".tsv", ".xlsx", ".xls", ".xpt", ".pdf", ".zip", ".7z", ".db", ".sqlite", ".parquet", ".ipynb"}
BANNED_DIRS = {"private", "measurements", "experimental", "reports", "data", "testfabriek", "__pycache__", ".pytest_cache"}
BANNED_TERMS = re.compile(r"\bFluidor\b|\bTestfabriek\b|-----BEGIN(?: RSA| OPENSSH)? PRIVATE KEY-----", re.I)
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yml", ".yaml", ".svg", ".txt"}
EXPECTED_GALLERY = (
    "push-discharge-comparison", "phase3-segmented-vs-equivalent",
    "phase4-blow-transition-volumes", "phase5-push-qmc-flow-band",
    "phase6-rinse-dry-water-inventory",
)


def candidate_files():
    for file in ROOT_FILES:
        yield ROOT / file
    for folder in SOURCE_DIRS:
        yield from (p for p in (ROOT / folder).rglob("*") if p.is_file()
                    and not any(x.lower() in SKIP_GENERATED_DIRS for x in p.relative_to(ROOT).parts))
    yield from (p for p in (ROOT / "tools").glob("*.py") if p.name != "audit_release.py")


def main():
    findings = []
    n = 0
    for path in candidate_files():
        rel = path.relative_to(ROOT)
        if not path.exists():
            findings.append(f"Missing: {rel}")
            continue
        if path.suffix.lower() in BANNED_SUFFIXES:
            findings.append(f"Forbidden extension: {rel}")
        if any(part.lower() in BANNED_DIRS for part in rel.parts[:-1]):
            findings.append(f"Forbidden directory: {rel}")
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in ROOT_FILES:
            try:
                contents = path.read_text(encoding="utf-8")
            except UnicodeError:
                findings.append(f"Could not read text: {rel}")
                continue
            if BANNED_TERMS.search(contents):
                findings.append(f"Possible company identifier/secret in: {rel}")
        n += 1
    for stem in EXPECTED_GALLERY:
        for ext in ("svg", "png"):
            if not (ROOT / "figures" / f"{stem}.{ext}").is_file():
                findings.append(f"Missing selected figure: {stem}.{ext}")
    print(f"Publication preflight inspected {n} files.")
    if findings:
        print("Potential concerns:\n" + "\n".join(findings))
        return 1
    print("Basic filename/identifier scan passed. Manual release review remains mandatory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
