import shlex, os
from ..state import SESSION
from ..metadata import MetadataError

class MlirSource:
    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if not argv:
            result.SetError("usage: mlir-source <value-id>"); return
        try:
            op = SESSION.require().op_for_value(argv[0])
        except MetadataError as e:
            result.SetError(str(e)); return
        src = op.layer("source") or {}
        f, line = src.get("file"), src.get("line")
        if not f:
            result.SetError(f"{argv[0]} has no source layer."); return
        result.AppendMessage(f"{f}:{line} -> {src.get('snippet','')}")
        if os.path.exists(f):
            lines = open(f).read().splitlines()
            lo, hi = max(1, line - 3), min(len(lines), line + 3)
            for n in range(lo, hi + 1):
                mark = "->" if n == line else "  "
                result.AppendMessage(f" {mark} {n:>4} {lines[n-1]}")