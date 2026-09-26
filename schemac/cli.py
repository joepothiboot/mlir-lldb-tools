import argparse, json, os
from .parser import parse_file
from .lower import lower_module
from .passes import run_pipeline
from .passes.folding import ConstraintFolding
from .passes.dce import RedundantCheckElim
from . import emit_cpp, emit_mlir, metadata_out

def _write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh: fh.write(text)

def main(argv=None):
    ap = argparse.ArgumentParser(prog="schemac")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("emit-mlir", "emit-cpp", "build"):
        p = sub.add_parser(name); p.add_argument("source"); p.add_argument("-o", "--out", required=True)
    b = sub.choices["build"]
    b.add_argument("--metadata", required=True)
    b.add_argument("--verify-provenance", action="store_true")
    a = ap.parse_args(argv)

    ast = parse_file(a.source)
    ir = run_pipeline(lower_module(ast), [ConstraintFolding(), RedundantCheckElim()])

    if a.cmd == "emit-mlir": _write(a.out, emit_mlir.print_module(ir))
    elif a.cmd == "emit-cpp": _write(a.out, "\n".join(emit_cpp.emit(ir).lines) + "\n")
    else:
        e = emit_cpp.emit(ir)
        _write(a.out, "\n".join(e.lines) + "\n")
        md = metadata_out.build(ir, e, source_file=a.source, generated_file=a.out,
                                verify=a.verify_provenance)
        _write(a.metadata, json.dumps(md, indent=2) + "\n")

if __name__ == "__main__":
    main()
