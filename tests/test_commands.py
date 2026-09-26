import json, os
from lldb_harness import session, needs_lldb, BUILD

METADATA = os.path.join(BUILD, "metadata.json")

def _op(name):
    ops = json.load(open(METADATA))["modules"][0]["ops"]
    return next(o for o in ops if o["op_name"] == name)

@needs_lldb
def test_break_op_stops_on_generated_line(session):
    assert "Loaded metadata" in session.cmd(f"mlir-lldb-tools load-metadata {METADATA}")
    assert "Breakpoint" in session.cmd("mlir-break-op toy_schema.validate_string")
    session.launch()
    line = session.frame().GetLineEntry()
    assert line.GetFileSpec().GetFilename() == "audioframe_validate.cpp"
    assert line.GetLine() == _op("toy_schema.validate_string")["layers"]["native"]["generated_line"]

@needs_lldb
def test_show_loc_maps_value_back_to_source(session):
    session.cmd(f"mlir-lldb-tools load-metadata {METADATA}")
    session.cmd("mlir-break-op toy_schema.validate_string")
    session.launch()
    out = session.cmd("mlir-show-loc %2")
    assert "toy_schema.validate_string" in out
    assert "examples/audioframe.schema:2:3" in out
    assert "__mlir_v2" in out
