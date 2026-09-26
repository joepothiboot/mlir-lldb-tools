from dataclasses import dataclass, replace
from typing import Optional

@dataclass(frozen=True)
class SourceLoc:
    file: str; line: int; col: int; snippet: str = ""
    def to_json(self): return {"file": self.file, "line": self.line, "col": self.col, "snippet": self.snippet, "provenance": "real"}

@dataclass(frozen=True)
class AstRef:
    node_kind: str; node_id: str
    def to_json(self): return {"node_kind": self.node_kind, "node_id": self.node_id, "provenance": "real"}

@dataclass(frozen=True)
class Provenance:
    source: SourceLoc; ast: Optional[AstRef] = None
    def with_ast(self, kind, node_id) -> "Provenance": return replace(self, ast=AstRef(kind, node_id))
    def validate(self, who: str):
        if not self.source or not self.ast: raise ValueError(f"{who}: provenance incomplete")