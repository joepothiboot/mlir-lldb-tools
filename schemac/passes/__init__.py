class Pass:
    name = "Pass"
    def run(self, mod, record): raise NotImplementedError

def run_pipeline(mod, passes):
    for seq, p in enumerate(passes, start=1):
        def record(op, action, _p=p, _s=seq):
            op.pass_history.append({"pass": _p.name, "action": action, "seq": _s})
        before = [(o.op_id, o.prov) for o in mod.ops]
        p.run(mod, record)
        for op_id, prov in before:
            op = next((o for o in mod.ops if o.op_id == op_id), None)
            if op and op.prov.source != prov.source:
                raise AssertionError(f"pass {p.name} altered provenance")
    return mod