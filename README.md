# mlir-lldb-tools

LLDB tooling for a small MLIR-based toy compiler: commands that speak in ops and
SSA values, pretty-printers for the runtime's objects, and a minimal debug
adapter (DAP) for VS Code.

> **Status: early skeleton.** Most files are partial stubs. Nothing has been
> built or run end to end yet, and version-sensitive spots (especially MLIR's
> C++ API) are marked `UNVERIFIED`.

## The idea

A debugger sees memory; a compiler sees SSA values. This project joins them:

1. **The code generator records where it put things.** `schemac` emits the C++
   itself, so it knows which generated line each op landed on. That goes into a
   side-car `metadata.json`, and LLDB resolves the address via DWARF.
2. **Runtime objects carry their `value_id`**, so a printer can look up the
   defining op and point back at the source construct.

Each metadata layer carries a `provenance` field (`real` or `synthetic`), and
`mlir-show-ir` prints a banner for anything that isn't real.

## Layout

```
src/mlir_lldb_tools/   LLDB commands, pretty-printers, DAP server
schemac/               toy compiler: lexer, parser, AST, lowering, passes, emitters
mlir/                  out-of-tree toy_schema dialect + schemac-opt
runtime/               C++ object model and sample program
examples/              sample .schema input
fixtures/              checked-in generated C++ for the no-MLIR path
scripts/               toolchain probe, build, stage-1 demo
tests/                 pytest; markers split by required toolchain
vscode-ext/            tiny extension showing the current value's MLIR op
```

## LLDB commands

Registered by `command script import src/mlir_lldb_tools`:

| Command | Purpose |
|---|---|
| `mlir-break-op <op-name>` | Break at code generated for a named op |
| `mlir-break-field <Schema>.<field>` | Break on validation of a source-level field |
| `mlir-show-loc <%id>` | Defining op, source location, live value |
| `mlir-pass-history <%id>` | Passes that touched a value |
| `mlir-show-ir <%id>` | MLIR / LLVM IR for a value's op |
| `mlir-source <%id>` | Show the originating `.schema` lines |
| `schema-inspect` / `dsp-inspect <expr>` | Pretty-print on demand |
| `mlir-lldb-tools load-metadata\|verbose-print\|status` | Session admin |

Printers are registered for `TensorView`, `DspBuffer`, `SchemaObject`,
`RuntimeError` and `MlirValue`. Fields are read from memory via DWARF, and
malformed objects (bad `magic`) degrade to a readable message instead of throwing.

## Getting started

```bash
./scripts/probe-toolchain.sh      # records your lldb/clang/MLIR versions in docs/environment.md
pip install -e .[dev]
pytest -m "not needs_lldb and not needs_mlir"
```

With an MLIR dev install, `scripts/build.sh` sketches the full pipeline
(`.schema` → MLIR → `schemac-opt` → LLVM IR → C++ + metadata).

**Common snag:** LLDB's Python module is built against one CPython minor
version. `_bootstrap.py` reports both versions if they don't match. Use the
matching interpreter or `python -m venv --system-site-packages`.

## Known limitations

- Side-car metadata goes stale on rebuild. DWARF would be the proper home.
- Optimised builds: locals get optimised out; no location-list handling.
- One op is assumed to map to one native site (no inlining model).
- DAP server is deliberately narrow: no attach, `setVariable`, conditional
  breakpoints or watch expressions.

## License

MIT. See `LICENSE`.
