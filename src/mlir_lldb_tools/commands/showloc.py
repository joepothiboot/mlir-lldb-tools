import shlex
from types import SimpleNamespace
from . import Command
from ..state import SESSION
from ..metadata import MetadataError

class MlirShowLoc(Command):
    """Print defining op, source location and live runtime value for %id."""
    def _parse(self, command, result):
        argv = shlex.split(command)
        if len(argv) != 1:
            result.SetError("usage: mlir-show-loc <value-id>"); return None
        return SimpleNamespace(value_id=argv[0])

    def __call__(self, debugger, command, exe_ctx, result):
        args = self._parse(command, result)
        if args is None: return
        try:
            op = SESSION.require().op_for_value(args.value_id)
        except MetadataError as e:
            result.SetError(str(e)); return

        src = op.layer("source") or {}
        out = [f"{args.value_id}  defined by  {op.op_name}  ({op.op_id})",
               f"  source : {src.get('file')}:{src.get('line')}:{src.get('col')}",
               f"  code   : {src.get('snippet','<none>')}",
               f"  operands: {', '.join(op.operands) or '<none>'}"]

        frame = exe_ctx.GetFrame()
        local = (op.layer("native") or {}).get("local_var")
        if not frame.IsValid():
            out.append("  runtime: <no frame — process not stopped>")
        elif not local:
            out.append("  runtime: <op has no materialised local>")
        else:
            v = frame.FindVariable(local)
            if not v.IsValid():
                out.append(f"  runtime: <{local} not live here "
                           f"(not yet executed, or optimised out)>")
            else:
                out.append(f"  runtime: {local} = {v.GetValue()} "
                           f"({v.GetTypeName()})  summary={v.GetSummary()}")
        result.AppendMessage("\n".join(out))