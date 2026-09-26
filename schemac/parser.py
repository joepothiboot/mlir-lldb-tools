from .lexer import tokenize, Token
from .ast import Module, SchemaDecl, FieldDecl, TypeRef
from .provenance import Provenance, SourceLoc

class Parser:
    def __init__(self, text, filename):
        self.toks = tokenize(text, filename); self.i = 0; self.file = filename; self.lines = text.splitlines()

    @property
    def cur(self): return self.toks[self.i]

    def at(self, kind, text=None): return self.cur.kind == kind and (text is None or self.cur.text == text)

    def eat(self, kind, text=None):
        if not self.at(kind, text):
            c = self.cur
            raise SyntaxError(f"{self.file}:{c.line}:{c.col}: expected {text or kind}, got {c.text!r}")
        t = self.cur; self.i += 1; return t

    def prov(self, tok):
        snippet = self.lines[tok.line - 1].strip() if 0 < tok.line <= len(self.lines) else ""
        return Provenance(SourceLoc(self.file, tok.line, tok.col, snippet))

    def parse_module(self):
        t = self.cur; mod = Module(prov=self.prov(t), source_file=self.file)
        mod.prov = mod.prov.with_ast("Module", mod.node_id)
        while not self.at("eof"): mod.schemas.append(self.parse_schema())
        return mod

    def parse_schema(self):
        kw = self.eat("kw", "schema")
        name = self.eat("ident").text
        s = SchemaDecl(prov=self.prov(kw), name=name)
        s.prov = s.prov.with_ast("SchemaDecl", s.node_id)
        self.eat("punct", "{")
        while not self.at("punct", "}"): s.fields.append(self.parse_field())
        self.eat("punct", "}")
        return s

    def parse_field(self):
        nt = self.eat("ident"); self.eat("punct", ":"); tref = self.parse_type()
        f = FieldDecl(prov=self.prov(nt), name=nt.text, type_ref=tref, constraints=dict(tref.params))
        f.prov = f.prov.with_ast("FieldDecl", f.node_id)
        return f

    def parse_type(self):
        t = self.cur; prov = self.prov(t)
        if self.at("kw", "tensor"):
            self.eat("kw", "tensor"); self.eat("punct", "<")
            dtype = self.eat("kw").text; self.eat("punct", ","); self.eat("punct", "[")
            shape = [int(self.eat("int").text)]
            while self.at("punct", ","): self.eat("punct", ","); shape.append(int(self.eat("int").text))
            self.eat("punct", "]"); self.eat("punct", ">")
            tr = TypeRef(prov=prov, name="tensor", dtype=dtype, shape=shape)
        elif self.at("kw", "dsp_buffer"):
            self.eat("kw", "dsp_buffer"); self.eat("punct", "<")
            dtype = self.eat("kw").text; params = {}
            while self.at("punct", ","):
                self.eat("punct", ","); k = self.eat("ident").text
                self.eat("punct", "="); params[k] = int(self.eat("int").text)
            self.eat("punct", ">")
            tr = TypeRef(prov=prov, name="dsp_buffer", dtype=dtype, params=params)
        else:
            base = self.eat("kw").text; params = {}
            if self.at("punct", "("):
                self.eat("punct", "(")
                while not self.at("punct", ")"):
                    k = self.eat("ident").text; self.eat("punct", "="); params[k] = int(self.eat("int").text)
                    if self.at("punct", ","): self.eat("punct", ",")
                self.eat("punct", ")")
            tr = TypeRef(prov=prov, name=base, params=params)
        tr.prov = tr.prov.with_ast("TypeRef", tr.node_id)
        return tr

def parse_file(path):
    with open(path) as fh: return Parser(fh.read(), path).parse_module()