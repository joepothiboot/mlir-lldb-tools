_COMMANDS = [
    ("mlir-break-op", "commands.breakop.MlirBreakOp"),
    ("mlir-show-loc", "commands.showloc.MlirShowLoc"),
    ("schema-inspect", "commands.inspect.SchemaInspect"),
    ("dsp-inspect", "commands.inspect.DspInspect"),
    ("mlir-pass-history", "commands.history.MlirPassHistory"),
    ("mlir-show-ir", "commands.showir.MlirShowIr"),  # stage 3
    ("mlir-source", "commands.source.MlirSource"),  # stage 3
    ("mlir-lldb-tools", "commands.admin.MlirAdmin"),  # load-metadata, verbose-print
]


def __lldb_init_module(debugger, internal_dict):
    from ._bootstrap import ensure_lldb

    ensure_lldb()
    for name, cls in _COMMANDS:
        debugger.HandleCommand(f"command script add -o -c mlir_lldb_tools.{cls} {name}")
    from .printers import register_all

    register_all(debugger)
    print(
        "mlir-lldb-tools loaded. Try: mlir-lldb-tools load-metadata "
        "build/metadata.json"
    )
