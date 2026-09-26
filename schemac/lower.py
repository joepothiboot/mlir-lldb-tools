from dataclasses import dataclass, field
from typing import List, Dict, Any
from .provenance import Provenance

@dataclass
class IrOp:
    op_id: str; op_name: str; results: List[str]; operands: List[str]; attrs: Dict[str, Any]; prov: Provenance
    pass_history: List[dict] = field(default_factory=list); dead: bool = False

@dataclass
class IrModule:
    source_file: str; ops: List[IrOp] = field(default_factory=list)
    @property
    def live(self): return [o for o in self.ops if not o.dead]

class Builder:
    def __init__(self, source_file): self.mod = IrModule(source_file); self._v = 0; self._o = 0
    def value(self): v = f"%{self._v}"; self._v += 1; return v
    def create(self, name, operands, attrs, prov, n_results=1):
        prov.validate(name); self._o += 1
        res = [self.value() for _ in range(n_results)]
        op = IrOp(f"op_{self._o}", name, res, list(operands), dict(attrs), prov)
        self.mod.ops.append(op)
        return op

def lower_module(ast_mod):
    b = Builder(ast_mod.source_file)
    for schema in ast_mod.schemas:
        obj = b.create("toy_schema.schema_ref", [], {"name": schema.name}, schema.prov)
        for f in schema.fields:
            ref = b.create("toy_schema.field_ref", obj.results, {"field_name": f.name}, f.prov)
            t = f.type_ref
            if t.name == "tensor":
                b.create("toy_schema.tensor_alloc", [], {"shape": t.shape, "dtype": t.dtype}, t.prov)
            elif t.name == "string":
                b.create("toy_schema.validate_string", ref.results, {"max_len": f.constraints["max"]}, f.prov)
            elif t.name in ("i32", "i64"):
                b.create("toy_schema.validate_range", ref.results, {"min": f.constraints.get("min", -2**31), "max": f.constraints.get("max", 2**31)}, f.prov)
    return b.mod