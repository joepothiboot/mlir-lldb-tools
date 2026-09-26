def register_all(debugger):
    cmds = [
      "type summary add -F mlir_lldb_tools.printers.tensor.summary  -x '^TensorView$'",
      "type summary add -F mlir_lldb_tools.printers.dsp.summary     -x '^DspBuffer$'",
      "type summary add -F mlir_lldb_tools.printers.schema.summary  -x '^SchemaObject$'",
      "type summary add -F mlir_lldb_tools.printers.error.summary   -x '^RuntimeError$'",
      "type summary add -F mlir_lldb_tools.printers.mlirvalue.summary -x '^MlirValue$'",
    ]
    for c in cmds: debugger.HandleCommand(c + " -w mlir-lldb-tools")
    debugger.HandleCommand("type category enable mlir-lldb-tools")