from . import tensor, dsp, schema, error, mlirvalue  # noqa: F401  (LLDB resolves -F by module path)

_SUMMARIES = [
    ("tensor", "TensorView"),
    ("dsp", "DspBuffer"),
    ("schema", "SchemaObject"),
    ("error", "RuntimeError"),
    ("mlirvalue", "MlirValue"),
]

def register_all(debugger):
    for mod, type_name in _SUMMARIES:
        debugger.HandleCommand(
            f"type summary add -w mlir-lldb-tools "
            f"-F mlir_lldb_tools.printers.{mod}.summary -x '^{type_name}$'")
    debugger.HandleCommand("type category enable mlir-lldb-tools")
