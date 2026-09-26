import shlex
from ..state import SESSION
from ..metadata import MetadataError

class MlirShowIr:
    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if len(argv) != 1:
            result.SetError("usage: mlir-show-ir <value-id>"); return
        try:
            md = SESSION.require()
            op = md.op_for_value(argv[0])
        except MetadataError as e:
            result.SetError(str(e)); return
        if md.banner():
            result.AppendWarning(md.banner())
        for key, label in (("mlir", "MLIR"), ("llvm_ir", "LLVM IR")):
            layer = op.layer(key)
            if not layer:
                result.AppendMessage(f"--- {label} ---\n<not available>")
                continue
            result.AppendMessage(f"--- {label} ---\n{layer.get('op_text') or layer.get('snippet')}")