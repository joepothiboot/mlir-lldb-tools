def __call__(self, debugger, command, exe_ctx, result):
    op = SESSION.require().op_for_value(args.value_id)
    m, ir = op.layer("mlir") or {}, op.layer("llvm_ir") or {}
    for layer, label in ((m, "MLIR"), (ir, "LLVM IR")):
        if not layer: continue
        if layer.get("provenance") != "real":
            result.AppendMessage(
                f"  [{layer.get('provenance','unknown')}] "
                f"{label} below is NOT produced by a real toolchain")
        result.AppendMessage(f"--- {label} ---\n{layer.get('op_text') or layer.get('snippet')}")