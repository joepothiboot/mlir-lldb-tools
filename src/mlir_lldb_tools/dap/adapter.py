import os
from .._bootstrap import ensure_lldb
from ..state import SESSION
from ..metadata import MetadataError

lldb = ensure_lldb()

class LldbAdapter:
    def __init__(self):
        self.dbg = lldb.SBDebugger.Create()
        self.dbg.SetAsync(False)
        self.dbg.HandleCommand("command script import src.mlir_lldb_tools")
        self.target = None; self.process = None
        self._refs = {}; self._next = 1000

    def launch(self, program, args=None, cwd=None, metadata=None):
        self.target = self.dbg.CreateTarget(program)
        if metadata:
            from ..metadata import Metadata
            SESSION.metadata = Metadata.load(metadata)
        self._pending_launch = (args or [], cwd or os.path.dirname(program))
        return {}

    def configuration_done(self):
        args, cwd = self._pending_launch
        self.process = self.target.LaunchSimple(args or None, None, cwd)
        return self._stop_reason()

    def set_breakpoints(self, path, lines):
        name = os.path.basename(path)
        out = []
        for ln in lines:
            bp = self.target.BreakpointCreateByLocation(name, ln)
            out.append({"id": bp.GetID(), "verified": bp.GetNumLocations() > 0, "line": ln})
        return out

    def resume(self, how):
        t = self.process.GetSelectedThread()
        {"continue": self.process.Continue, "next": lambda: t.StepOver(), "stepIn": lambda: t.StepInto()}[how]()
        return self._stop_reason()

    def _stop_reason(self):
        if not self.process.IsValid(): return "exited"
        r = self.process.GetSelectedThread().GetStopReason()
        return {lldb.eStopReasonBreakpoint: "breakpoint", lldb.eStopReasonPlanComplete: "step"}.get(r, "pause")

    def stack_trace(self):
        t = self.process.GetSelectedThread()
        return [{"id": i, "name": t.GetFrameAtIndex(i).GetFunctionName() or "??",
                 "line": t.GetFrameAtIndex(i).GetLineEntry().GetLine()} for i in range(t.GetNumFrames())]

    def scopes(self, frame_id):
        f = self.process.GetSelectedThread().GetFrameAtIndex(frame_id)
        locals_ = f.GetVariables(True, True, False, True)
        self._next += 1; self._refs[self._next] = locals_
        return [{"name": "Locals", "variablesReference": self._next, "expensive": False}]

    def variables(self, ref):
        container = self._refs.get(ref)
        if not container: return []
        out = []
        for i in range(container.GetNumChildren()):
            v = container.GetChildAtIndex(i)
            out.append({"name": v.GetName(), "value": v.GetSummary() or v.GetValue(), "type": v.GetTypeName()})
        return out

    def evaluate(self, expr, frame_id=0):
        v = self.process.GetSelectedThread().GetFrameAtIndex(frame_id).EvaluateExpression(expr)
        return {"result": v.GetSummary() or v.GetValue(), "type": v.GetTypeName(), "variablesReference": 0}

    def mlir_ir(self, value_id=None, local=None, frame_id=0):
        md = SESSION.require()
        if not value_id: value_id = md.value_id_for_local(local)
        op = md.op_for_value(value_id)
        return {"valueId": value_id, "opName": op.op_name,
                "mlir": (op.layer("mlir") or {}).get("op_text"),
                "provenance": op.provenance("mlir"), "fixture": md.fixture}