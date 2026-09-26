"""Process-wide session state shared by all commands and printers."""
from .metadata import Metadata, MetadataError

class Session:
    def __init__(self):
        self.metadata: Metadata = None
        self.verbose = False
    def require(self) -> Metadata:
        if self.metadata is None:
            raise MetadataError(
                "No metadata loaded. Run:\n"
                "    (lldb) mlir-lldb-tools load-metadata build/metadata.json\n"
                "or put that line in .lldbinit next to your binary.")
        return self.metadata

SESSION = Session()