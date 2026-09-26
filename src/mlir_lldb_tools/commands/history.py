import shlex
from ..state import SESSION
from ..metadata import MetadataError

class MlirPassHistory:
    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if len(argv) != 1:
            result.SetError("usage: mlir-pass-history <value-id>"); return
        try:
            op = SESSION.require().op_for_value(argv[0])
        except MetadataError as e:
            result.SetError(str(e)); return
        if not op.pass_history:
            result.AppendMessage(f"{argv[0]}: no recorded passes.")
            return
        lines = [f"{argv[0]} {op.op_name}", f"  {'seq':<4} {'pass':<20} action"]
        for h in op.pass_history:
            lines.append(f"  {h['seq']:<4} {h['pass']:<20} {h['action']}")
        result.AppendMessage("\n".join(lines))