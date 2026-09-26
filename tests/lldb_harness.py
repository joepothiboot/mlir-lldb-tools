import os, pytest
from mlir_lldb_tools._bootstrap import ensure_lldb, LldbUnavailable

BUILD = os.environ.get("MLIR_LLDB_BUILD", "build")
BINARY = os.path.join(BUILD, "schema_demo")

try:
    lldb = ensure_lldb(); HAVE_LLDB = True; REASON = ""
except LldbUnavailable as e:
    lldb, HAVE_LLDB, REASON = None, False, str(e)

def needs_lldb(fn):
    """Mark for `-m needs_lldb` selection, and skip when lldb can't be imported."""
    return pytest.mark.needs_lldb(pytest.mark.skipif(not HAVE_LLDB, reason=REASON)(fn))

class Session:
    def __init__(self, binary=BINARY):
        self.dbg = lldb.SBDebugger.Create(); self.dbg.SetAsync(False)
        self.dbg.HandleCommand("command script import mlir_lldb_tools")
        self.target = self.dbg.CreateTarget(binary); self.process = None

    def cmd(self, text):
        res = lldb.SBCommandReturnObject()
        self.dbg.GetCommandInterpreter().HandleCommand(text, res)
        return (res.GetOutput() or "") + (res.GetError() or "")

    def break_at_name(self, name):
        bp = self.target.BreakpointCreateByName(name)
        assert bp.GetNumLocations() > 0
        return self.launch()

    def launch(self):
        self.process = self.target.LaunchSimple(None, None, os.getcwd())
        assert self.process.GetState() == lldb.eStateStopped, self.cmd("process status")
        return self.process

    def frame(self):
        return self.process.GetSelectedThread().GetSelectedFrame()

    def close(self):
        if self.process: self.process.Kill()
        lldb.SBDebugger.Destroy(self.dbg)

@pytest.fixture
def session(): s = Session(); yield s; s.close()