#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p docs/transcripts
lldb -b -o "command script import src/mlir_lldb_tools" \
     -o "mlir-lldb-tools load-metadata build/metadata.json" \
     -o "mlir-break-op toy_schema.validate_string" \
     -o "run" -o "mlir-show-loc %2" -o "mlir-pass-history %2" \
     build/schema_demo 2>&1 | tee docs/transcripts/stage1.txt
