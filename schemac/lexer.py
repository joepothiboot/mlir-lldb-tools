import re
from dataclasses import dataclass

KEYWORDS = {"schema", "string", "i32", "i64", "f32", "f64", "tensor", "dsp_buffer", "bool"}

@dataclass
class Token:
    kind: str; text: str; line: int; col: int

_SPEC = [("ws", r"[ \t]+"), ("comment", r"//[^\n]*"), ("newline", r"\n"),
         ("int", r"-?\d+"), ("ident", r"[A-Za-z_][A-Za-z_0-9]*"), ("punct", r"[{}\[\]<>(),:=]")]
_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _SPEC))

def tokenize(text, filename="<stdin>"):
    line, line_start, pos, out = 1, 0, 0, []
    while pos < len(text):
        m = _RE.match(text, pos)
        if not m: raise SyntaxError(f"Unexpected character {text[pos]!r}")
        kind = m.lastgroup; col = pos - line_start + 1
        if kind == "newline": line += 1; line_start = m.end()
        elif kind not in ("ws", "comment"):
            txt = m.group()
            if kind == "ident" and txt in KEYWORDS: kind = "kw"
            out.append(Token(kind, txt, line, col))
        pos = m.end()
    out.append(Token("eof", "", line, pos - line_start + 1))
    return out