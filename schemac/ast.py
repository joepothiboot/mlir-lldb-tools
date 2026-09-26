from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .provenance import Provenance

_counter = {"n": 0}
def _next_id(): _counter["n"] += 1; return f"ast_{_counter['n']}"

@dataclass
class Node:
    prov: Provenance; node_id: str = field(default_factory=_next_id)

@dataclass
class TypeRef(Node):
    name: str = ""; dtype: Optional[str] = None; shape: Optional[List[int]] = None; params: Dict[str, int] = field(default_factory=dict)

@dataclass
class FieldDecl(Node):
    name: str = ""; type_ref: Optional[TypeRef] = None; constraints: Dict[str, int] = field(default_factory=dict)

@dataclass
class SchemaDecl(Node):
    name: str = ""; fields: List[FieldDecl] = field(default_factory=list)

@dataclass
class Module(Node):
    source_file: str = ""; schemas: List[SchemaDecl] = field(default_factory=list)