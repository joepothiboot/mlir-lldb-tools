from .common import check_magic, child, u, guard
from ..state import SESSION

KINDS = {0: "None", 1: "TypeMismatch", 2: "ConstraintViolation", 3: "ShapeError"}

def _summary(valobj, _d):
    check_magic(valobj, "RuntimeError")
    kind = KINDS.get(u(valobj, "kind"), "Unknown")
    msg  = child(valobj, "message").GetSummary() or "<null>"
    f, l = child(valobj, "source_file").GetSummary(), u(valobj, "source_line")
    vid  = u(valobj, "value_id")
    line = f"RuntimeError[{kind}] {msg} at {f}:{l}"
    md = SESSION.metadata
    if md and vid:
        try:
            op = md.op_for_value(f"%{vid}")
            line += f"  <- {op.op_name} ({op.op_id})"
        except Exception: pass
    return line

summary = guard("RuntimeError", _summary)