# AGENTS.md

Instructions for AI coding agents working in this repository.

## Layout

| Path | Contents |
|---|---|
| `include/aci_opt.hpp`, `src/aci_opt.cpp` | The engine. No dependencies. |
| `include/problems.hpp` | Built-in benchmark problems (must match `compare/problems.py`). |
| `python/` | pybind11 bindings (`eternal_bindings.cpp`) and the `eternal` package. |
| `tools/` | Benchmarks, MCP server, matmul showcase workload. |
| `app/main.cpp` | Desktop app (Dear ImGui / ImPlot). |
| `compare/` | Head-to-head harness against Optuna and Ax. |

## Verify every change

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DETERNAL_GUI=OFF && cmake --build build -j 8
ctest --test-dir build --output-on-failure
pip install ".[test]" && pytest -q
```

If the engine's search behaviour changes, also run `./build/eternal_bench 20 200` and report the
before/after table, including regressions.

## Rules

- The engine stays dependency-free and C++20.
- Keep `include/problems.hpp` and `compare/problems.py` numerically identical.
- Benchmark claims in the READMEs must be reproducible with the commands they cite. Report losses.
- User-facing strings in the app go through the language table so Japanese and English stay in sync.
- Update both `README.md` (Japanese) and `README.en.md` when behaviour or numbers change.
