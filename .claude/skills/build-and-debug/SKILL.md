---
name: build-and-debug
description: Build the schema demo and exercise the LLDB commands against it. Use when running, testing, or debugging the end-to-end schemac → clang → LLDB path.
---

# Build and debug the demo

1. `./scripts/probe-toolchain.sh`: check lldb/clang versions (writes `docs/environment.md`).
2. `./scripts/build.sh`: produces `build/schema_demo` and `build/metadata.json`.
3. `pytest -m needs_lldb`: integration tests on a live process.
4. `./scripts/demo_stage1.sh`: scripted LLDB session, good for a quick eyeball.

If `import lldb` fails, it's almost always a Python version mismatch; `_bootstrap.py`
prints both versions. Use the matching interpreter.

The MLIR stages aren't wired in, so `mlir-show-ir` reporting "no layer" is expected.
