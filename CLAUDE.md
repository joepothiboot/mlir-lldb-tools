# CLAUDE.md

LLDB tooling for a toy MLIR-based compiler. See `README.md` for the full picture;
this is the short version.

## Map

- `schemac/`: toy compiler (`.schema` → generated C++ + `metadata.json`)
- `src/mlir_lldb_tools/`: LLDB commands, pretty-printers, DAP server
- `runtime/`: C++ object model the generated code links against
- `mlir/`: toy_schema dialect, **not compiled yet** (`UNVERIFIED` spots)
- `tests/`: pytest, split by markers `needs_lldb` / `needs_mlir`

## Commands

```bash
pip install -e .[dev]
pytest -m "not needs_lldb and not needs_mlir"   # always runnable
./scripts/build.sh && pytest -m needs_lldb      # needs clang++ + lldb
```

## Ground rules

- **Never fake data.** Metadata layers carry `provenance` (`real`/`synthetic`);
  missing layers are omitted, not invented. Fixtures must declare `"fixture": true`.
- Printers must degrade to a readable message on bad memory, never throw.
- LLDB's Python module is tied to one CPython version. Import it via
  `_bootstrap.ensure_lldb()`, not `import lldb` directly.
- Format with Prettier (`.prettierrc.json`); match the surrounding style.
