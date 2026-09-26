import shlex, lldb
from ..printers import tensor, dsp, schema as schema_pp

class _Inspect:
    TYPE = None
    RENDER = None
    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if len(argv) != 1:
            result.SetError(f"usage: {self.NAME} <expr>"); return
        frame = exe_ctx.GetFrame()
        if not frame.IsValid():
            result.SetError("No stopped frame."); return
        val = frame.EvaluateExpression(argv[0])
        if not val.IsValid() or val.GetError().Fail():
            result.SetError(f"Could not evaluate {argv[0]!r}"); return
        if val.GetType().IsPointerType(): val = val.Dereference()
        result.AppendMessage(self.RENDER(val, {}))

class SchemaInspect(_Inspect):
    NAME, TYPE = "schema-inspect", "SchemaObject"
    RENDER = staticmethod(schema_pp.summary)

class DspInspect(_Inspect):
    NAME, TYPE = "dsp-inspect", "DspBuffer"
    RENDER = staticmethod(dsp.summary)