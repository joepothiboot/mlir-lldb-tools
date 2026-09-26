"""Print schemac's IR as generic-form MLIR text with fused source locations.

This is schemac's own textual output, the input to schemac-opt. It is not
evidence that MLIR ran; metadata only gets an `mlir` layer from schemac-opt.
"""
import json

RESULT_TYPES = {"validate_string": "i1", "validate_range": "i1"}

def loc(op):
    s = op.prov.source
    return f'loc(fused<"{op.op_id}">[loc("{s.file}":{s.line}:{s.col})])'

def _attr(v):
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, int): return f"{v} : i64"
    if isinstance(v, str): return json.dumps(v)
    if isinstance(v, list): return "[" + ", ".join(f"{x} : i64" for x in v) + "]"
    raise TypeError(f"unsupported attribute value {v!r}")

def print_op(op):
    kind = op.op_name.rsplit(".", 1)[-1]
    attrs = ", ".join(f"{k} = {_attr(v)}" for k, v in sorted(op.attrs.items()))
    rty = RESULT_TYPES.get(kind, "!llvm.ptr")
    ins = ", ".join("!llvm.ptr" for _ in op.operands)
    res = f"{', '.join(op.results)} = " if op.results else ""
    outs = ", ".join(rty for _ in op.results)
    return (f'{res}"{op.op_name}"({", ".join(op.operands)}) {{{attrs}}} '
            f": ({ins}) -> ({outs}) {loc(op)}")

def print_module(mod):
    body = "\n".join("  " + print_op(o) for o in mod.live)
    return f"module {{\n{body}\n}}\n"
