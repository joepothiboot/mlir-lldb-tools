#!/usr/bin/env bash
set -e
lldb -b -o "command script import src/mlir_lldb_tools" \
     -o "mlir-lldb-tools load-metadata build/metadata.json" \
     -o "mlir-break-op schema.validate_string" \
     -o "run" -o "mlir-show-loc %3" -o "mlir-pass-history %3" \
     build/schema_demo 2>&1 | tee docs/transcripts/stage1.txt
