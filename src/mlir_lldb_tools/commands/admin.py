import argparse, hashlib, os, shlex
from ..state import SESSION
from ..metadata import Metadata, MetadataError

class MlirAdmin:
    def __call__(self, debugger, command, exe_ctx, result):
        argv = shlex.split(command)
        if not argv: return
        sub, rest = argv[0], argv[1:]
        if sub == "load-metadata":
            try:
                md = Metadata.load(rest[0])
            except MetadataError as e:
                result.SetError(str(e)); return
            SESSION.metadata = md
            result.AppendMessage(f"Loaded metadata from {md.path}")
            if md.banner():
                result.AppendWarning(md.banner())
        elif sub == "verbose-print":
            SESSION.verbose = rest[0] == "on"
            result.AppendMessage(f"verbose printing {rest[0]}")
        elif sub == "status":
            md = SESSION.metadata
            result.AppendMessage(f"metadata: {md.path if md else '<none>'}\nverbose: {SESSION.verbose}")