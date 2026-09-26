from .common import check_magic, child, u, guard
from ..state import SESSION

KIND = {0: "string", 1: "int", 2: "tensor", 3: "dsp"}

def _summary(valobj, _d):
    check_magic(valobj, "SchemaObject")
    name = child(valobj, "schema_name").GetSummary() or "<null>"
    n, mask = u(valobj, "field_count"), u(valobj, "validated_mask")
    done = bin(mask).count("1")
    head = f"SchemaObject {name} fields: {n} validated: {done}/{n}"
    if not SESSION.verbose: return head
    out, fields = [head], child(valobj, "fields")
    md = SESSION.metadata
    for i in range(min(n, 32)):
        f = fields.GetChildAtIndex(i)
        fname = f.GetChildMemberWithName("name").GetSummary() or "?"
        k = KIND.get(f.GetChildMemberWithName("kind").GetValueAsUnsigned(), "?")
        vid = f.GetChildMemberWithName("value_id").GetValueAsUnsigned()
        ok = "ok " if mask & (1 << i) else "-- "
        line = f"  [{ok}] {fname} : {k}"
        if md and vid:
            try:
                op = md.op_for_value(f"%{vid}")
                line += f"   <- {op.op_name} ({op.op_id})"
            except Exception: pass
        out.append(line)
    return "\n".join(out)

summary = guard("SchemaObject", _summary)