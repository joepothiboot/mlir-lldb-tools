from . import Pass

class RedundantCheckElim(Pass):
    name = "RedundantCheckElim"
    def run(self, mod, record):
        seen = {}
        for op in mod.live:
            if not op.op_name.startswith("toy_schema.validate"): continue
            key = (op.op_name, tuple(op.operands))
            if key in seen:
                op.dead = True; record(op, "eliminated duplicate check")
            else:
                seen[key] = op.op_id; record(op, "kept check")