[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pipeline-flow-modelling"
version = "0.7.0"
description = "Data-free numerical demonstrations of published pipe-flow equations"
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["numpy>=1.24", "scipy>=1.10"]

[project.optional-dependencies]
plots = ["matplotlib>=3.7"]
dev = ["pytest>=7.4", "matplotlib>=3.7"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
