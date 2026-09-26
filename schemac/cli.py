import argparse, json, os
from .parser import parse_file
from .lower import lower_module
from .passes import run_pipeline
from .passes.folding import ConstraintFolding
from .passes.dce import RedundantCheckElim
from . import emit_cpp, emit_mlir, metadata_out

def main():
    ap = argparse.ArgumentParser(prog="schemac")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("emit-mlir", "emit-cpp", "build"):
        p = sub.add_parser(name); p.add_argument("source"); p.add_argument("-o", "--out", required=True)
    b = sub.choices["build"]
    b.add_argument("--metadata", required=True)
    a = ap.parse_args()

    ast = parse_file(a.source)
    ir = run_pipeline(lower_module(ast), [ConstraintFolding(), RedundantCheckElim()])

    if a.cmd == "emit-mlir": open(a.out, "w").write(emit_mlir.print_module(ir))
    elif a.cmd == "emit-cpp": open(a.out, "w").write("\n".join(emit_cpp.emit(ir).lines))
    else:
        e = emit_cpp.emit(ir)
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w").write("\n".join(e.lines))
        md = metadata_out.build(ir, e, source_file=a.source, generated_file=a.out)
        json.dump(md, open(a.metadata, "w"), indent=2)