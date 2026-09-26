import json
from mlir_lldb_tools.metadata import Metadata

def test_fixture_file_is_self_declaring():
    raw = json.load(open("fixtures/metadata.fixture.json"))
    assert raw["fixture"] is True
