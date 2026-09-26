#!/usr/bin/env bash
# Build the demo binary and its debugger metadata.
#   schemac: .schema -> generated C++ + metadata.json (+ schemac's MLIR text)
#   clang++: runtime + generated C++ -> build/schema_demo (with -g)
# The MLIR stages (schemac-opt, mlir-translate) are not wired in yet, so the
# metadata has no `mlir`/`llvm_ir` layers: omitted, not faked.
set -euo pipefail
cd "$(dirname "$0")/.."

BUILD=${BUILD:-build}
PYTHON=${PYTHON:-python3}
CXX=${CXX:-clang++}
SCHEMA=${SCHEMA:-examples/audioframe.schema}

"$PYTHON" -m schemac emit-mlir "$SCHEMA" -o "$BUILD/audioframe.mlir"
"$PYTHON" -m schemac build "$SCHEMA" -o "$BUILD/generated/audioframe_validate.cpp" \
    --metadata "$BUILD/metadata.json" --verify-provenance

"$CXX" -g -O0 -std=c++17 -Iruntime/include \
    runtime/src/main.cpp runtime/src/mlir_rt.cpp "$BUILD/generated/audioframe_validate.cpp" \
    -o "$BUILD/schema_demo"

echo "built $BUILD/schema_demo and $BUILD/metadata.json"
if [ -n "${MLIR_DIR:-}" ]; then
  echo "note: MLIR_DIR is set, but the schemac-opt stages are not wired into this script yet"
fi
