# Changelog

All notable changes to this project are listed here. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-02

### Added
- Python package `eternal-optimizer` (`import eternal`): `Optimizer` (ask/tell), `minimize`, `RandomSearch`,
  `Memory` for warm-starting related studies, and access to verdicts, trials and events.
- Type stubs (`py.typed`, `_core.pyi`); `tell()` rejects NaN and infinite values.
- English README (`README.en.md`), MIT license, contributing guide, `AGENTS.md`, ADR 0001, issue templates.
- CI on Linux, macOS and Windows; wheel builds and PyPI publishing on release.
- CMake options `ETERNAL_TOOLS` and `ETERNAL_PYTHON`.

### Fixed
- `Memory::save` truncated lines when values needed full precision with exponents, corrupting
  saved memory on reload (64-byte buffer for up to 77 bytes). Parameter names with tabs or newlines,
  which also broke the format, are now rejected by the Python API.
- `tools/matmul_bench.cpp` did not build on Linux (missing `<cmath>`).

### Existing at first release
- C++ causal optimization engine (intervene, necessity screening, rule learning, confidence gate,
  crystallization, recheck) with memory across studies.
- Desktop app (Dear ImGui / ImPlot, Japanese and English), MCP server, benchmarks, comparison with
  Optuna and Ax, matmul showcase.
