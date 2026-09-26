import shlex
from ..state import SESSION
from ..metadata import MetadataError

class MlirBreakField:
    def get_short_help(self): return "Break on validation of a schema field."
    def get_long_help(self):
        return ("usage: mlir-break-field <Schema>.<field>\n\n"
                "Resolves the field to the op validating it via DWARF.")

    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if len(argv) != 1 or "." not in argv[0]:
            result.SetError(self.get_long_help()); return
        schema_name, field = argv[0].split(".", 1)
        try:
            md = SESSION.require()
        except MetadataError as e:
            result.SetError(str(e)); return

        ref = next((o for m in md.modules for o in m.ops
                    if o.op_name.endswith("field_ref")
                    and o.attrs.get("field_name") == field), None)
        if ref is None:
            result.SetError(f"No field {field!r} found in metadata.")
            return
        users = [o for m in md.modules for o in m.ops
                 if set(o.operands) & set(ref.results)
                 and "validate" in o.op_name]
        target = exe_ctx.GetTarget() or debugger.GetSelectedTarget()
        for op in users:
            nat = op.layer("native") or {}
            gen = op.module.generated_file.split("/")[-1]
            bp = target.BreakpointCreateByLocation(gen, int(nat["generated_line"]))
            result.AppendMessage(f"Breakpoint {bp.GetID()}: field '{field}' -> {op.op_name}")