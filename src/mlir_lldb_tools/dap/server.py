import sys, traceback
from .protocol import Wire, Disconnect

CAPABILITIES = {
    "supportsConfigurationDoneRequest": True,
    "supportsEvaluateForHovers": True,
    "supportsConditionalBreakpoints": False,
    "supportsSetVariable": False,
}


class Server:
    def __init__(self, wire, adapter):
        self.wire, self.a, self.running = wire, adapter, True

    def serve(self):
        while self.running:
            try:
                msg = self.wire.read()
            except Disconnect:
                break
            if msg.get("type") != "request":
                continue
            cmd, args = msg["command"], msg.get("arguments") or {}
            fn = getattr(self, f"do_{cmd.replace('-', '_')}", None)
            if not fn:
                self.wire.respond(
                    msg, success=False, message=f"Unsupported (see dap-scope.md)"
                )
                continue
            try:
                self.wire.respond(msg, fn(args) or {})
            except Exception as e:
                self.wire.respond(msg, success=False, message=str(e))
                continue
            if cmd == "initialize":
                self.wire.event("initialized")

    def do_initialize(self, a):
        return CAPABILITIES

    def do_launch(self, a):
        self.a.launch(a["program"], a.get("args"), a.get("cwd"), a.get("metadata"))
        return {}

    def do_configurationDone(self, a):
        reason = self.a.configuration_done()
        self.wire.event("stopped", {"reason": reason, "threadId": 1})
        return {}

    def do_setBreakpoints(self, a):
        return {
            "breakpoints": self.a.set_breakpoints(
                a.get("source", {}).get("path", ""),
                [b["line"] for b in a.get("breakpoints", [])],
            )
        }

    def do_threads(self, a):
        return {"threads": [{"id": 1, "name": "main"}]}

    def do_continue(self, a):
        self.a.resume("continue")
        return {"allThreadsContinued": True}

    def do_next(self, a):
        self.a.resume("next")
        return {"allThreadsContinued": True}

    def do_stepIn(self, a):
        self.a.resume("stepIn")
        return {"allThreadsContinued": True}

    def do_stackTrace(self, a):
        fr = self.a.stack_trace()
        return {"stackFrames": fr, "totalFrames": len(fr)}

    def do_scopes(self, a):
        return {"scopes": self.a.scopes(a.get("frameId", 0))}

    def do_variables(self, a):
        return {"variables": self.a.variables(a["variablesReference"])}

    def do_evaluate(self, a):
        return self.a.evaluate(a["expression"], a.get("frameId", 0))

    def do_mlirIr(self, a):
        return self.a.mlir_ir(a.get("valueId"), a.get("local"), a.get("frameId", 0))

    def do_disconnect(self, a):
        self.running = False
        return {}

    do_terminate = do_disconnect


def main():
    from .adapter import LldbAdapter

    Server(Wire(sys.stdin.buffer, sys.stdout.buffer), LldbAdapter()).serve()


if __name__ == "__main__":
    main()
