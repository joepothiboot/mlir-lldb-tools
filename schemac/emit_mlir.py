# schemac/emit_mlir.py
def loc(op):
    s = op.prov.source
    return f'loc(fused<"{op.op_id}">[loc("{s.file}":{s.line}:{s.col})])'
