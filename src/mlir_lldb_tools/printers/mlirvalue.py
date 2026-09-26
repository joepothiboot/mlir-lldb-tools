from .common import child, u, guard
from ..state import SESSION

TAG = {0: "i1", 1: "i64", 2: "f64", 3: "ptr"}

def _summary(valobj, _d):
    vid  = u(valobj, "value_id")
    tag  = u(valobj, "type_tag")
    tname = TAG.get(tag, "unknown")
    un = child(valobj, "v")
    conc = un.GetChildMemberWithName("i").GetValue()
    s = f"%{vid} : {tname} = {conc}"
    md = SESSION.metadata
    if md:
        try:
            op = md.op_for_value(f"%{vid}")
            s += f"   defined by {op.op_name} ({op.op_id})"
        except Exception: pass
    return s

summary = guard("MlirValue", _summary)