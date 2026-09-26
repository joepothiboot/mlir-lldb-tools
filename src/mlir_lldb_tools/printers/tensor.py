import lldb
from .common import check_magic, child, u, guard
from ..state import SESSION

DTYPE = {0: "f32", 1: "f64", 2: "i32", 3: "i64", 4: "i8"}
LAYOUT = {0: "row-major", 1: "col-major", 2: "strided"}

def _dims(v, field, rank):
    arr = child(v, field)
    out = []
    for i in range(rank):
        e = arr.GetChildAtIndex(i)
        out.append(e.GetValueAsSigned() if e.IsValid() else "?")
    return out

def _summary(valobj, _d):
    check_magic(valobj, "TensorView")
    rank = u(valobj, "rank")
    if rank > 4:                       # struct caps rank at 4
        from .common import Malformed
        raise Malformed(f"rank={rank} exceeds array capacity 4")
    dt   = DTYPE.get(u(valobj, "dtype"), f"?({u(valobj,'dtype')})")
    lay  = LAYOUT.get(u(valobj, "layout"), "?")
    shape, strides = _dims(valobj, "shape", rank), _dims(valobj, "strides", rank)
    data = u(valobj, "data")
    if data == 0:
        return f"TensorView<{dt}> shape: {shape} <data: NULL — not allocated>"
    head = (f"TensorView<{dt}> shape: {shape} strides: {strides} "
            f"layout: {lay} data: 0x{data:x}")
    if not SESSION.verbose:
        return head
    elems = 1
    for s in shape: elems *= (s if isinstance(s, int) else 0)
    contiguous = strides == [int(1)] if rank == 1 else None
    lines = [head,
             f"  elements : {elems}",
             f"  bytes    : {elems * (8 if dt in ('f64','i64') else 4)}",
             f"  contiguous: {_is_contiguous(shape, strides)}"]
    return "\n".join(lines)

def _is_contiguous(shape, strides):
    try:
        exp, ok = 1, True
        for s, st in zip(reversed(shape), reversed(strides)):
            ok &= (st == exp); exp *= s
        return ok
    except Exception:
        return "unknown"

summary = guard("TensorView", _summary)

class TensorSynthetic:
    """Synthetic children: expose shape/strides flat plus first data elements."""
    def __init__(self, valobj, _d): self.v = valobj; self.n = 0
    def update(self):
        try:
            self.rank = min(self.v.GetChildMemberWithName("rank")
                              .GetValueAsUnsigned(0), 4)
        except Exception: self.rank = 0
        self.n = self.rank + 1
        return False
    def num_children(self): return self.n
    def get_child_index(self, name):
        return int(name[4:]) if name.startswith("dim_") else -1
    def get_child_at_index(self, i):
        if i < self.rank:
            return self.v.GetChildMemberWithName("shape").GetChildAtIndex(i)
        return self.v.GetChildMemberWithName("data")