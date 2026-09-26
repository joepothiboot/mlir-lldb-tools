import lldb
from ..state import SESSION

MAGIC = {"TensorView": 0x544E5352, "DspBuffer": 0x44535042,
         "SchemaObject": 0x53434D41, "RuntimeError": 0x45525221}

class Malformed(Exception): pass

def child(v: lldb.SBValue, *path):
    """Walk named children, raising Malformed instead of returning junk."""
    cur = v
    for name in path:
        cur = cur.GetChildMemberWithName(name)
        if not cur.IsValid():
            raise Malformed(f"missing field '{name}'")
    return cur

def u(v, *path):
    c = child(v, *path)
    e = lldb.SBError(); val = c.GetValueAsUnsigned(e, 0)
    if e.Fail(): raise Malformed(f"unreadable {'.'.join(path)}")
    return val

def check_magic(v, kind):
    try:
        got = u(v, "magic")
    except Malformed:
        raise Malformed("no magic field — wrong type?")
    if got != MAGIC[kind]:
        raise Malformed(
            f"bad magic 0x{got:08X} (expected 0x{MAGIC[kind]:08X}) — object is "
            "uninitialised, mid-construction, or memory is corrupt")

def guard(kind, fn):
    """Wrap a summary fn so a malformed object degrades instead of throwing."""
    def wrapper(valobj, internal_dict, options=None):
        try:
            return fn(valobj, internal_dict)
        except Malformed as m:
            return f"<{kind} MALFORMED: {m} @ 0x{valobj.GetLoadAddress():x}>"
        except Exception as e:                       # never break the debugger
            return f"<{kind} printer error: {type(e).__name__}: {e}>"
    return wrapper