import io, json
from mlir_lldb_tools.dap.protocol import Wire
from mlir_lldb_tools.dap.server import Server

class FakeAdapter:
    def launch(self, *a, **k): return {}
    def configuration_done(self): return "breakpoint"
    def set_breakpoints(self, p, l): return [{"id": 1, "verified": True, "line": l[0]}]

def test_initialize():
    buf = io.BytesIO()
    r = json.dumps({"command": "initialize", "type": "request", "seq": 1}).encode()
    buf.write(b"Content-Length: %d\r\n\r\n" % len(r) + r); buf.seek(0)
    out = io.BytesIO()
    Server(Wire(buf, out), FakeAdapter()).serve()
    out.seek(0)
    msg = Wire(out, io.BytesIO()).read()
    assert msg["success"] is True