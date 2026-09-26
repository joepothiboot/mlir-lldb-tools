"""Metadata v1 loader. Additive-only; Stage 3 adds keys under `layers`."""
import json, os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SCHEMA_VERSION = 1

class MetadataError(RuntimeError): pass

@dataclass
class Op:
    op_id: str
    op_name: str
    results: List[str]
    operands: List[str]
    layers: Dict[str, dict]
    pass_history: List[dict]
    module: "Module" = None

    def layer(self, name) -> Optional[dict]:
        return self.layers.get(name)

    def provenance(self, layer) -> str:
        l = self.layers.get(layer) or {}
        return l.get("provenance", "unknown")

@dataclass
class Module:
    source_file: str
    generated_file: str
    ops: List[Op] = field(default_factory=list)

@dataclass
class Metadata:
    path: str
    producer: dict
    modules: List[Module]
    _by_value: Dict[str, Op] = field(default_factory=dict)
    _by_opname: Dict[str, List[Op]] = field(default_factory=dict)

    @classmethod
    def load(cls, path) -> "Metadata":
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            raise MetadataError(f"No metadata file at {path}. "
                                "Run `schemac build` or pass the right path.")
        try:
            raw = json.load(open(path))
        except json.JSONDecodeError as e:
            raise MetadataError(f"{path} is not valid JSON: {e}") from e
        v = raw.get("schema_version")
        if v != SCHEMA_VERSION:
            raise MetadataError(
                f"metadata schema_version={v!r}, this build understands "
                f"{SCHEMA_VERSION}. Regenerate with a matching schemac.")
        md = cls(path=path, producer=raw.get("producer", {}), modules=[])
        for m in raw.get("modules", []):
            mod = Module(m["source_file"], m["generated_file"])
            for o in m.get("ops", []):
                op = Op(o["op_id"], o["op_name"], o.get("results", []),
                        o.get("operands", []), o.get("layers", {}),
                        o.get("pass_history", []), mod)
                mod.ops.append(op)
                for r in op.results:
                    md._by_value[r] = op
                md._by_opname.setdefault(op.op_name, []).append(op)
            md.modules.append(mod)
        return md

    # --- lookups with *useful* failures: a debugger tool must fail legibly ---
    def op_for_value(self, vid: str) -> Op:
        vid = vid if vid.startswith("%") else "%" + vid
        if vid not in self._by_value:
            known = ", ".join(sorted(self._by_value)[:12])
            raise MetadataError(f"Unknown value id {vid}. Known: {known} ...")
        return self._by_value[vid]

    def ops_for_name(self, name: str) -> List[Op]:
        if name not in self._by_opname:
            import difflib
            near = difflib.get_close_matches(name, self._by_opname, n=3)
            hint = f" Did you mean: {', '.join(near)}?" if near else \
                   f" Known ops: {', '.join(sorted(self._by_opname))}"
            raise MetadataError(f"No op named '{name}'.{hint}")
        return self._by_opname[name]

    def value_id_for_local(self, local: str) -> Optional[str]:
        for m in self.modules:
            for op in m.ops:
                if (op.layer("native") or {}).get("local_var") == local:
                    return op.results[0] if op.results else None
        return None