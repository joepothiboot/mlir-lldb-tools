import pytest
from lldb_harness import session, needs_lldb

@needs_lldb
def test_tensor_valid(session):
    session.break_at_name("mlir_debug_checkpoint")
    out = session.cmd("frame variable win")
    assert "TensorView<f32>" in out
    assert "shape: [16, 64]" in out
