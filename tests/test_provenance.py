import pytest
from schemac.parser import Parser
from schemac.lower import lower_module
from schemac.passes import run_pipeline, Pass
from schemac.provenance import Provenance, SourceLoc

def test_good_pipeline_keeps_provenance():
    mod = lower_module(Parser("schema A { name: string(max=10) }", "t.schema").parse_module())
    assert mod.live[0].prov.source.file == "t.schema"
