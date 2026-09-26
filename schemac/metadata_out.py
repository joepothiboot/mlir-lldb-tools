import json, os

def build(ir_mod, emitter, *, source_file, generated_file, mlir_path=None, llvm_ir_path=None, producer=None, verify=False):
    ops_json = []
    for op in ir_mod.live:
        if verify: op.prov.validate(op.op_id)
        layers = {"source": op.prov.source.to_json(), "ast": op.prov.ast.to_json()}
        line = emitter.op_lines.get(op.op_id)
        if line:
            layers["native"] = {"generated_line": line, "symbol": "AudioFrame_validate", "local_var": "__mlir_v" + op.results[0].lstrip("%") if op.results else None, "provenance": "real"}
        ops_json.append({"op_id": op.op_id, "op_name": op.op_name, "results": op.results, "operands": op.operands, "attrs": op.attrs, "layers": layers, "pass_history": op.pass_history})
    return {"schema_version": 1, "producer": producer or {"tool": "schemac"}, "modules": [{"source_file": source_file, "generated_file": generated_file, "ops": ops_json}]}