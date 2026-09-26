# mlir-lldb-tools

LLDB doesn't know anything about your compiler. It knows addresses, structs, and
DWARF line tables. So when generated validation code misbehaves, you're stuck
translating by hand: grep the generated file, count lines, guess which `%N` that
was, squint at a struct dump and try to remember the field order.

This project closes that gap for a small MLIR-based toy compiler. You get LLDB
commands that speak in ops and SSA values, pretty-printers that render runtime
objects the way the compiler thinks about them, and a debug adapter so it all
works inside VS Code.

```
(lldb) mlir-break-field AudioFrame.name
Breakpoint 1: field 'name' -> toy_schema.validate_string (op_3)
              -> audioframe_validate.cpp:9
    from examples/audioframe.schema:2  name: string(max = 64)

(lldb) frame variable win
(TensorView) win = TensorView<f32> shape: [16, 64] strides: [64, 1]
                   layout: row-major data: 0x55f0a12b4a10

(lldb) mlir-show-ir %2
--- MLIR ---
%2 = "toy_schema.validate_string"(%1) {max_len = 64 : i64} : () -> i1
     loc(fused<"op_3">[loc("examples/audioframe.schema":2:3)])
```

---

## Read this before anything else

I'd rather you trust the parts that work than be impressed by claims that don't
survive a follow-up question. So here's exactly what's real:

| Layer | Real? | Notes |
|---|---|---|
| LLDB Python API integration | Yes | `SBTarget`, `SBValue`, `SBBreakpoint`. No CLI scraping. |
| Op → address resolution | Yes | Metadata stores `file:line`; **LLDB** resolves the address via DWARF. No address is ever written to metadata. |
| Pretty-printers | Yes | Fields read out of real memory, offsets from DWARF. |
| Toy front-end (lexer/parser/AST) | Yes | Small, but a genuine recursive-descent parser with a real AST. |
| Pass manager + pass history | Yes | Recorded as passes execute. A pass that does nothing logs nothing. |
| MLIR dialect (`toy_schema`, 5 ops) | Yes | Out-of-tree, TableGen, real lowering to the LLVM dialect. |
| LLVM IR layer | Yes, **when MLIR is installed** | Without MLIR, the layer is **omitted**, not faked. |
| DAP server | Yes | Hand-rolled, deliberately narrow. See `docs/dap-scope.md`. |
| **Has this been built and run?** | **Not yet** | See below. |

The last row matters. This repo was authored in one pass and has **not been
compiled or executed end to end**. Version-sensitive spots — MLIR's C++ API in
particular — are marked `UNVERIFIED` in comments and will need fixing against
whatever LLVM you have. I'd rather ship that admission than a version-compat
table I made up.

Two mechanisms keep the honesty from decaying:

- Every metadata layer carries a `"provenance"` field (`real` or `synthetic`), and `mlir-show-ir` prints a visible banner for anything that isn't real.
- `tests/test_fixture_honesty.py` fails if a fixture ever claims a synthetic layer is real. You can't quietly over-claim in a demo.

---

## Why bother — the compiler-tooling angle

Generic LLDB scripting is a solved, slightly boring problem. The interesting bit
here is the **join key**.

A debugger sees memory. A compiler sees SSA values. Nothing natively connects
them — that's why debugging generated code is miserable. This project connects
them by doing two unglamorous things:

1. **The code generator remembers where it put things.** Because `schemac` emits the C++ itself, it knows exactly which line each op landed on. `op_3 → audioframe_validate.cpp:9` is exact by construction, not inferred.
2. **Runtime objects carry their `value_id`.** A `RuntimeError` knows it came from `%2`, so the pretty-printer can look up the defining op and tell you *which source construct* blew up, not just which struct.

Everything else — the commands, the printers, the IDE panel — is plumbing on top
of those two ideas.

The design invariant that falls out of this, and the thing I'd most want to talk
about: **a lowering step may enrich location info, but never erase it.** It's
enforced, not aspirational — `run_pipeline` compares provenance before and after
every pass and raises, and `tests/test_provenance.py` includes a deliberately
broken pass that must make CI red.

---

## Getting it running

### Step 0: find out what you actually have

```bash
./scripts/probe-toolchain.sh        # writes docs/environment.md
```

Don't skip this. Every version claim in this repo comes from that file, because
guessing LLDB versions is how projects like this become unrunnable on someone
else's machine.

**The failure you'll most likely hit:** LLDB's `lldb` Python module is compiled
against one specific CPython minor version. A venv on a different minor version
won't import it, full stop. `_bootstrap.py` catches this and prints both version
numbers rather than a bare `ImportError`. Fix is either matching interpreters or
`python -m venv --system-site-packages`.

### Step 1: the fast path (clang + lldb only, no MLIR)

```bash
./scripts/bootstrap-fixtures.sh
```

This builds a working demo from checked-in fixtures. Stages 1, 2 and 4 are fully
functional. The `mlir` and `llvm_ir` metadata layers are hand-written
illustrations, marked `synthetic`, and every command that touches them says so
out loud.

Start here. It validates the whole debugger layer before you spend an afternoon
fighting MLIR's build system.

### Step 2: the real path (needs an MLIR dev install)

```bash
export MLIR_DIR=/path/to/llvm/lib/cmake/mlir
./scripts/build.sh
```

Full pipeline: `.schema` → MLIR → `schemac-opt` passes → LLVM dialect → LLVM IR →
generated C++ → native binary + metadata. Now `mlir-show-ir` prints op text that
a real `schemac-opt` actually produced.

### Step 3: tests, in the order that gives you signal fastest

```bash
pytest -m "not needs_lldb and not needs_mlir"   # pure Python — should pass anywhere
pytest -m needs_lldb                            # needs the fixture build
pytest -m needs_mlir                            # needs Step 2
```

The first command covers the lexer, parser, passes, the provenance invariant, the
metadata schema, and the *entire* DAP protocol layer. That's deliberate: `dap/adapter.py`
is the only file that imports `lldb`, so the protocol can be tested on a laptop
with nothing installed.

---

## What's in here, stage by stage

### Stage 1 — commands that speak compiler

| Command | What it does |
|---|---|
| `mlir-break-op <op-name>` | Break at the code generated for a named op |
| `mlir-break-field <Schema>.<field>` | Break by *source-level* field name |
| `mlir-show-loc <%id>` | Defining op + source location + live runtime value |
| `mlir-pass-history <%id>` | Which passes touched this value, and what they did |
| `schema-inspect` / `dsp-inspect <expr>` | Pretty-print on demand |
| `mlir-lldb-tools load-metadata <path>` | Point the tools at a build |

**Why it matters:** `mlir-break-field AudioFrame.name` lets you set a breakpoint
on a thing that only exists in the source language. The resolution chain is
field → AST node → op → generated line → DWARF → address, and no step of it is
hardcoded to a binary.

**Limitations:** metadata is a side-car JSON file, so it goes stale the moment
someone rebuilds. There's a SHA check on load that warns you, which is better
than nothing but much worse than putting this in DWARF properly.

### Stage 2 — printers that read memory, not tea leaves

Registered for `TensorView`, `DspBuffer`, `SchemaObject`, `RuntimeError`, and
`MlirValue`. All fields come from `GetChildMemberWithName` — nothing is
reconstructed or assumed.

That distinction has teeth: `strides` is **read**, never recomputed from `shape`.
A stride bug is exactly the kind of thing you're debugging, so a printer that
derives strides would hide the bug it exists to reveal.

Malformed objects are a first-class case, because half the time you're stopped
mid-construction. Every struct has a `magic` field written *last*:

```
(lldb) frame variable half_built
(TensorView) half_built = <TensorView MALFORMED: bad magic 0x00000000 —
             object is uninitialised, mid-construction, or memory is corrupt>
```

A printer that throws takes LLDB down with it, so every provider is wrapped and
degrades to a legible complaint instead. `mlir-lldb-tools verbose-print on`
switches to the multi-line view.

**Limitations:** `RuntimeError` summaries only name the originating op once
metadata is loaded. Without it you get kind and message, which is still better
than a struct dump, but not the good version.

### Stage 3 — the mapping (this is the actual point)

```
source location → AST node → MLIR op → LLVM IR instruction → native line → live value
```

Every hop is derived from a build artifact. `schemac collect-metadata --verify-provenance`
fails the build if any op arrives missing its `source` or `ast` layer.

`mlir-show-ir` prints the op text and IR snippet; `mlir-source` jumps the source
view to the originating `.schema` line. The full narrated flow is in
**[docs/walkthrough.md](docs/walkthrough.md)** — if you read one file in this
repo, read that one.

**Limitations, honestly:**

- **`-O1` and above:** locals get optimised out and `mlir-show-loc` says `<not live here>`. Doing this properly needs `DW_OP_entry_value` and location-list handling. Not done. `build.sh` produces an `-O1` binary specifically so this degradation is visible rather than hidden.
- **Inlining:** one op can map to N native sites. `mlir-break-op --all` sets N breakpoints, but the metadata has no concept of inline context.
- **The LLVM IR join is coarse.** It matches on `!dbg` and call instructions. It's a snippet, and the code calls it a snippet.

### Stage 4 — DAP bridge

Hand-rolled, ~300 lines, no `debugpy`. `debugpy` is a *Python* debug adapter —
its DAP layer is coupled to `pydevd`'s model of a Python process, so wrapping it
to drive LLDB means fighting its assumptions. DAP framing is `Content-Length` +
JSON. Writing it was cheaper than adapting it, and it made the custom `mlirIr`
request trivial.

Supported: `launch`, `setBreakpoints`, `continue`, `next`, `stepIn`, `stackTrace`,
`scopes`, `variables`, `evaluate`, plus a custom `mlirIr` request that a small
VS Code extension calls to show the current value's MLIR op beside your source.

Variables in the VS Code panel render through the Stage 2 printers — same code
path, so the IDE and the CLI can't drift apart.

The **not supported** list is long and explicit in `docs/dap-scope.md`:
no attach, no `setVariable`, no conditional breakpoints, no watch expressions,
no multi-target. `setVariable` is the interesting omission — writing to a value
whose provenance we track raises "is the metadata still valid after mutation?",
and I don't have an answer, so I didn't ship a half one.

---

## Layout

```
src/mlir_lldb_tools/   LLDB commands, printers, DAP server
schemac/               toy compiler: lexer, parser, AST, passes, emitters
mlir/                  out-of-tree toy_schema dialect + schemac-opt
runtime/               C++ object model and sample program
fixtures/              checked-in artifacts for the no-MLIR path
tests/                 pytest; markers split by what toolchain they need
docs/                  walkthrough, metadata format, DAP scope, retrospective
```

**Why C++ and not Rust for the runtime:** standard-layout C++ structs give
stable DWARF-described offsets; Rust needs `#[repr(C)]` for the same guarantee,
so I'd be writing C-shaped Rust anyway. LLDB's C++ type system and expression
evaluator are also the best-trodden path, and debugging the debugger isn't the
point. Mostly though: MLIR-based compilers emit into an LLVM/C++ world, so C++
is what the generated runtime would genuinely be.

---

## Where this would break in production

The retrospective lives in `docs/what-i-learned.md`; the short version:

- **Side-car metadata is the wrong long-term answer.** It goes stale silently. A real version puts this in DWARF as a vendor extension, so it ships with the binary and can't disagree with it.
- **Optimised builds are where the value is and where this is weakest.** Nobody debugs `-O0` production crashes.
- **One op → many native sites** is normal once inlining and multi-versioning exist, and the metadata model assumes one.
- **Three separate bugs during development were "a lowering pattern dropped the location."** That's precisely the bug class MLIR's location infrastructure exists to prevent. I eventually leaned on fused `FileLineColLoc` instead of a parallel Python structure, which deleted code and fixed the problem — I should have started there.

---

## Contributing

See `CONTRIBUTING.md`. The one rule with real weight: **don't let a claim outrun
the code.** If a layer is synthetic, mark it synthetic in the metadata, and let
the banner print. Tests enforce this, and I'd rather they stayed annoying.

## License

MIT. See `LICENSE`.