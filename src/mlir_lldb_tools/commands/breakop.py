import argparse, shlex, lldb
from ..state import SESSION
from ..metadata import MetadataError

class MlirBreakOp:
    """Set a breakpoint at the native code generated for a named MLIR op."""
    @staticmethod
    def parser():
        p = argparse.ArgumentParser(prog="mlir-break-op", add_help=False,
              description="Break at the generated code for a named op")
        p.add_argument("op_name")
        p.add_argument("-a", "--all", action="store_true")
        p.add_argument("-c", "--condition", help="breakpoint condition expression")
        p.add_argument("-h", "--help", action="store_true")
        return p

    def get_short_help(self): return "Break at generated code for an MLIR op."
    def get_long_help(self): return self.parser().format_help()

    def __call__(self, debugger, command, exe_ctx, result):
        p = self.parser()
        try:
            args = p.parse_args(shlex.split(command))
        except SystemExit:
            result.SetError(p.format_usage()); return
        if args.help:
            result.AppendMessage(p.format_help()); return
        try:
            md = SESSION.require()
            ops = md.ops_for_name(args.op_name)
        except MetadataError as e:
            result.SetError(str(e)); return

        target = exe_ctx.GetTarget() or debugger.GetSelectedTarget()
        if not target.IsValid():
            result.SetError("No target selected."); return

        chosen = ops if args.all else ops[:1]
        made = 0
        for op in chosen:
            nat = op.layer("native") or {}
            line = nat.get("generated_line")
            gen  = op.module.generated_file
            if not line: continue
            bp = target.BreakpointCreateByLocation(gen.split("/")[-1], int(line))
            if bp.GetNumLocations() == 0:
                result.AppendWarning(f"{op.op_id}: LLDB resolved 0 locations.")
                continue
            if args.condition: bp.SetCondition(args.condition)
            src = op.layer("source") or {}
            result.AppendMessage(
                f"Breakpoint {bp.GetID()}: {op.op_name} ({op.op_id}) -> {gen}:{line}")
            made += 1
        if made == 0:
            result.SetError(f"No breakpoints created for '{args.op_name}'.")