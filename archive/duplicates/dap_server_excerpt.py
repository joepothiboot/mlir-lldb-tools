# src/mlir_lldb_tools/dap/server.py  (core loop, abridged)
class DapServer:
    def __init__(self, rfile, wfile):
        self.r, self.w, self.seq = rfile, wfile, 1
        self.dbg = lldb.SBDebugger.Create(); self.dbg.SetAsync(True)
        self.var_refs, self.next_ref = {}, 1000

    def _read(self):
        line = self.r.readline()
        if not line: return None
        n = int(line.decode().split(":")[1]); self.r.readline()
        return json.loads(self.r.read(n))

    def _send(self, obj):
        b = json.dumps(obj).encode()
        self.w.write(f"Content-Length: {len(b)}\r\n\r\n".encode() + b); self.w.flush()

    HANDLERS = ("initialize launch setBreakpoints configurationDone continue "
                "next stepIn stackTrace scopes variables evaluate "
                "mlirIr disconnect").split()

    def on_variables(self, args):
        val = self.var_refs[args["variablesReference"]]
        out = []
        for i in range(val.GetNumChildren()):
            c = val.GetChildAtIndex(i)
            out.append({"name": c.GetName(),
                        # Stage 2 printers drive the UI text:
                        "value": c.GetSummary() or c.GetValue() or "<n/a>",
                        "type": c.GetTypeName(),
                        "variablesReference": self._ref(c) if c.MightHaveChildren() else 0})
        return {"variables": out}

    def on_mlirIr(self, args):          # custom request, consumed by the VS Code ext
        frame = self._frame()
        vid = args.get("valueId") or SESSION.metadata.value_id_for_local(
                  args.get("local", ""))
        op = SESSION.require().op_for_value(vid)
        return {"valueId": vid, "opName": op.op_name,
                "mlir": (op.layer("mlir") or {}).get("op_text"),
                "llvmIr": (op.layer("llvm_ir") or {}).get("snippet"),
                "provenance": op.provenance("mlir"),
                "source": op.layer("source")}