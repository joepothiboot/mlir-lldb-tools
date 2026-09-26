from . import Pass

class ConstraintFolding(Pass):
    name = "ConstraintFolding"
    def run(self, mod, record):
        for op in mod.live:
            if op.op_name == "toy_schema.validate_string" and "max_len" in op.attrs:
                record(op, f"folded max_len={op.attrs['max_len']} into op")
