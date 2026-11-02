# ADR 0001: Python bindings via pybind11 and scikit-build-core

- Status: accepted
- Date: 2026-11-02

## Context

The engine is C++ only. Most black-box optimization users (Optuna, Ax, scikit-optimize) work in
Python, and being installable with `pip` is the precondition for downloads and dependent packages.
The comparison harness already calls the engine from Python, but through a subprocess.

## Options

| Option | Pros | Cons |
|---|---|---|
| Rewrite in Python | No compiler needed | Two engines to keep identical; ~10x slower per iteration |
| ctypes / C ABI | No build-time dependency | Hand-written C shim; no exceptions or STL types across the boundary |
| nanobind | Smaller, faster binaries | Requires Python >= 3.8 with stable ABI caveats; less familiar to contributors |
| **pybind11 + scikit-build-core** | Mature; STL and exceptions map directly; builds with the existing CMake | Larger binaries; one wheel per Python version |

## Decision

pybind11 for bindings, scikit-build-core as the build backend, cibuildwheel for wheels. The module
is `eternal._core`; the public API (`eternal.Optimizer`, `minimize`, ...) is a thin Python layer that
converts between named dicts and the engine's ordered vectors.

## Consequences

- One engine: Python and C++ always behave identically.
- The CMake build gains `ETERNAL_PYTHON` and `ETERNAL_TOOLS` options so wheel builds skip the
  app, tools and their fetched dependencies.
- Wheels must be rebuilt for each new CPython release.
